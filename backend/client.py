import os
import sys
import argparse

import txaio
txaio.use_twisted()

from txaio import sleep, make_logger

from twisted.internet.protocol import ProcessProtocol
from twisted.internet.defer import Deferred, gatherResults
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer


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
                print('ok, echo() successfully called the {}-th time, answered by callee with PID {}'.format(cnt, res['pid']))
                await sleep(.1)
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

    parser.add_argument('--realm',
                        dest='realm',
                        type=str,
                        default=os.environ.get('CBREALM', 'dvl1'),
                        help='The realm to join on the router.')

    parser.add_argument('--iterations',
                        dest='iter',
                        type=int,
                        default=10,
                        help='Number of iterations before exiting.')

    parser.add_argument('--realms',
                        dest='realms',
                        type=str,
                        default=','.join(['dvl{}'.format(i + 1) for i in range(10)]),
                        help='The realm to join on the router.')

    parser.add_argument('--parallel',
                        dest='parallel',
                        type=int,
                        default=1,
                        help='Parallel degree (process-based).')

    args = parser.parse_args()

    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

    extra = {
        'iter': args.iter,
    }

    if args.parallel > 1:
        dl = []
        for realm in args.realms.split(','):
            for i in range(args.parallel):
                cmd = [sys.executable, '-u', os.path.abspath(__file__), '--url', args.url, '--realm', realm]
                done = Deferred()
                worker = Worker(done)
                reactor.spawnProcess(worker, cmd[0], args=cmd, usePTY=True)
                dl.append(done)
        all = gatherResults(dl)
        reactor.run()
    else:
        runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])
        runner.run(Client, auto_reconnect=True)
