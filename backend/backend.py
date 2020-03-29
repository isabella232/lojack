import os
import argparse

import txaio
txaio.use_twisted()

from autobahn.wamp.types import RegisterOptions, CallDetails
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.serializer import CBORSerializer


class Client(ApplicationSession):

    async def onJoin(self, details):
        print('Client joined', details)

        pid = os.getpid()

        async def echo(msg: bytes, details: CallDetails):
            print('Client.echo(msg=<{} bytes>) from {}'.format(len(msg), details.caller_authid))
            res = {
                'pid': pid,
                'msg': msg,
                'caller': details.caller,
                'caller_authid': details.caller_authid,
            }
            return res

        await self.register(echo, "com.example.echo", options=RegisterOptions(invoke='random', details=True))


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

    args = parser.parse_args()

    if args.debug:
        txaio.start_logging(level='debug')
    else:
        txaio.start_logging(level='info')

    extra = {
    }

    runner = ApplicationRunner(url=args.url, realm=args.realm, extra=extra, serializers=[CBORSerializer()])
    runner.run(Client, auto_reconnect=True)
