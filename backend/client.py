import sys
import os
import argparse

import txaio
txaio.use_twisted()

from txaio import sleep, make_logger, time_ns

from twisted.internet import reactor
from twisted.internet.defer import Deferred, gatherResults
from twisted.internet.protocol import ProcessProtocol

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer


class PipelinedClient(ApplicationSession):

    async def onJoin(self, details):
        pid = os.getpid()
        self.log.info('Client PID {pid} joined:\n{details}', pid=pid, details=details)

        self._last = time_ns()
        self._cnt_success = 0
        self._cnt_error = 0

        def issue_batch():
            dl = []
            for i in range(200):
                msg = os.urandom(256)
                d = self.call("com.example.echo", msg)

                def success(res):
                    self._cnt_success += 1

                def error(err):
                    self._cnt_error += 1

                d.addCallbacks(success, error)
                dl.append(d)

            return gatherResults(dl)

        b2 = None
        while True:
            b1 = issue_batch()
            if b2:
                await b2
            b2 = issue_batch()
            await b1

            now = time_ns()
            duration = (now - self._last) / 10 ** 9
            if duration > 10.:
                now = time_ns()
                cnt = self._cnt_success + self._cnt_error
                rate = round(cnt / duration, 1)
                self._last = now
                self.log.info(
                    'Client.echo(): {cnt} calls ({rate} calls/sec) returned (cnt_success={cnt_success}, cnt_error={cnt_error}) for client PID {pid}',
                    cnt=cnt, pid=pid, rate=rate, cnt_success=self._cnt_success, cnt_error=self._cnt_error)
                self._cnt_success = 0
                self._cnt_error = 0

            await sleep(.1)

    def onLeave(self, details):
        self.log.info('Client.onLeave(details={details})', details=details)
        if details.reason == 'wamp.close.normal':
            self.log.info('Shutting down ..')
            # user initiated leave => end the program
            try:
                self._stop = True
                self.config.runner.stop()
                self.disconnect()
            except:
                self.log.failure()
        else:
            # continue running the program (let ApplicationRunner perform auto-reconnect attempts ..)
            self.log.info('Will continue to run (reconnect)!')

    def onDisconnect(self):
        ApplicationSession.onDisconnect(self)
        if self._stop:
            from twisted.internet import reactor
            if reactor.running:
                reactor.stop()


class Client(ApplicationSession):

    async def onJoin(self, details):
        self.log.info('Client.onJoin(details={details})', details=details)

        try:
            n = self.config.extra['iter']
            cnt = 0
            while n:
                msg = os.urandom(256)
                res = await self.call("com.example.echo", msg)
                assert type(res) == dict and 'msg' in res and type(res['msg']) == bytes
                assert res['msg'] == msg
                n -= 1
                cnt += 1
                if cnt % 100 == 1:
                    print('ok, echo() successfully called the {}-th time, answered by callee with PID {}'.format(cnt, res['pid']))
                await sleep(.01)
        except:
            self.log.failure()
        self.leave()

    def onLeave(self, details):
        self.log.info('Client.onLeave(details={details})', details=details)
        if details.reason == 'wamp.close.normal':
            self.log.info('Shutting down ..')
            # user initiated leave => end the program
            try:
                self._stop = True
                self.config.runner.stop()
                self.disconnect()
            except:
                self.log.failure()
        else:
            # continue running the program (let ApplicationRunner perform auto-reconnect attempts ..)
            self.log.info('Will continue to run (reconnect)!')

    def onDisconnect(self):
        ApplicationSession.onDisconnect(self)
        if self._stop:
            from twisted.internet import reactor
            if reactor.running:
                reactor.stop()


class Worker(ProcessProtocol):

    log = make_logger()

    def __init__(self, done):
        self.done = done

    def connectionMade(self):
        self.log.info('{klass}.connectionMade()', klass=self.__class__.__name__)
        ProcessProtocol.connectionMade(self)

    def outReceived(self, data):
        self.log.debug('{klass}.outReceived(data=<{data_len} bytes>)', klass=self.__class__.__name__, data_len=len(data))
        print(data.decode())

    def errReceived(self, data):
        self.log.debug('{klass}.errReceived(data=<{data_len} bytes>)', klass=self.__class__.__name__, data_len=len(data))
        print(data.decode())

    def processEnded(self, status):
        self.log.info('{klass}.processEnded(status={status})', klass=self.__class__.__name__, status=status)
        rc = status.value.exitCode
        if rc == 0:
            self.done.callback(self)
        else:
            self.done.errback(rc)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Enable debug output.')

    parser.add_argument('--url',
                        dest='url',
                        type=str,
                        default=os.environ.get('CBURL', 'rs://localhost:8080'),
                        help='The router URL to connect to.')

    parser.add_argument('--realms',
                        dest='realms',
                        type=str,
                        default=','.join(['dvl{}'.format(i + 1) for i in range(8)]),
                        help='The realm to join on the router.')

    parser.add_argument('--parallel',
                        dest='parallel',
                        type=int,
                        default=1,
                        help='Parallel degree (process-based).')

    parser.add_argument('--realm',
                        dest='realm',
                        type=str,
                        default=None,
                        help='The router realm to join the worker with.')

    parser.add_argument('--worker',
                        dest='worker',
                        type=str,
                        default=None,
                        help='The worker number when parallel degree > 1.')

    parser.add_argument('--iterations',
                        dest='iter',
                        type=int,
                        default=10,
                        help='Number of iterations before exiting.')

    args = parser.parse_args()

    if args.parallel > 1:
        dl = []
        for realm in args.realms.split(','):
            for i in range(args.parallel):
                cmd = [sys.executable, '-u', os.path.abspath(__file__), '--url', args.url, '--realm', realm, '--worker={}'.format(i)]
                done = Deferred()
                worker = Worker(done)
                reactor.spawnProcess(worker, cmd[0], args=cmd, usePTY=True)
                dl.append(done)
        all = gatherResults(dl)
        reactor.run()
    else:
        extra = {
            'worker': args.worker,
            'iter': args.iter,
        }

        runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])
        runner.run(PipelinedClient, auto_reconnect=True)
