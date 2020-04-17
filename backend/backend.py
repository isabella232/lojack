import sys
import os
import argparse

import txaio
txaio.use_twisted()

from txaio import make_logger, time_ns

from twisted.internet import reactor
from twisted.internet.defer import Deferred, gatherResults
from twisted.internet.protocol import ProcessProtocol

from autobahn.wamp.types import RegisterOptions, CallDetails
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer


class Client(ApplicationSession):

    async def onJoin(self, details):
        pid = os.getpid()
        self.log.info('Backend PID {pid} joined:\n{details}', pid=pid, details=details)

        self._cnt_echo = 0
        self._last = time_ns()

        async def echo(msg: bytes, details: CallDetails):
            self.log.debug('Client.echo(msg=<{mlen} bytes>) on backend PID {pid} from {client}',
                           mlen=len(msg), pid=pid, client=details.caller_authid)
            self._cnt_echo += 1
            if self._cnt_echo % 1000 == 1:
                now = time_ns()
                rate = round(self._cnt_echo / (now - self._last) / 10**9, 1)
                self._last = now
                self.log.info('Client.echo(): {cnt} calls ({rate} calls/sec) returned successfully by backend PID {pid}',
                              cnt=self._cnt_echo, pid=pid, rate=rate)
            res = {
                'pid': pid,
                'msg': msg,
                'caller': details.caller,
                'caller_authid': details.caller_authid,
            }
            return res

        await self.register(echo, "com.example.echo", options=RegisterOptions(invoke='random', details=True))

        self.log.info('Backend ready!')


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
                        default=','.join(['dvl{}'.format(i + 1) for i in range(10)]),
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

    args = parser.parse_args()

    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

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
        }

        runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])
        runner.run(Client, auto_reconnect=True)
