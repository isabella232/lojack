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
        print('Client joined', details)

        n = 0
        while True:
            msg = os.urandom(256)
            res = await self.call("com.example.echo", msg)
            assert type(res) == dict and 'msg' in res and type(res['msg']) == bytes
            assert res['msg'] == msg
            # FIXME
            # assert details.session == res['caller']
            # assert details.authid == res['caller_authid']
            n += 1
            print('ok, echo() successfully called {}th time, answered by PID {}'.format(n, res['pid']))
            await sleep(1)


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
