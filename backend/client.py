import os

from autobahn.twisted.util import sleep
from autobahn.twisted.component import Component, run
from autobahn.wamp.types import RegisterOptions, CallResult

CBURL = os.environ.get('CBURL', 'wss://lojack1.crossbario.com/ws')
CBREALM = os.environ.get('CBREALM', 'dvl1')

component = Component(transports=CBURL, realm=CBREALM)


@component.on_join
async def joined(session, details):
    print("session joined:", details)

    def echo(*args, **kwargs):
        _ = kwargs.pop('details', None)
        kwargs['pid'] = os.getpid()
        return CallResult(*args, **kwargs)

    await session.register(echo, 'com.lojack.echo',
                          options=RegisterOptions(invoke='random'))

    print("session ready!")

    counter = 100
    while counter:
        res = await session.call('com.lojack.echo', counter,
                                 msg='Hello from {}'.format(os.getpid()))
        print(res)
        await sleep(1)
        counter -= 1


if __name__ == "__main__":
    print('connecting to {}@{} ..'.format(CBREALM, CBURL))
    run([component])
