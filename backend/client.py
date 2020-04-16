import os
import argparse
from pprint import pformat

import txaio
txaio.use_twisted()

from txaio import sleep

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer


class Client(ApplicationSession):

    async def onJoin(self, details):
        self.log.info('Client.onJoin(details={details})', details=details)

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
            await sleep(1)
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

    args = parser.parse_args()

    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

    extra = {
        'iter': args.iter,
    }

    runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])
    runner.run(Client, auto_reconnect=True)
