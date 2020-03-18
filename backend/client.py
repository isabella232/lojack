import os
import datetime
from autobahn.twisted.component import Component, run

CBURL = os.environ.get('CBURL', 'wss://lojack1.crossbario.com/ws')
CBREALM = os.environ.get('CBREALM', 'dvl1')

component = Component(transports=CBURL, realm=CBREALM)


@component.on_join
async def joined(session, details):
    print("session joined:", details)

    def now(details=None):
        now = datetime.datetime.utcnow()
        return now.strftime("%Y-%m-%dT%H:%M:%SZ")

    def echo(*args, **kwargs):
        details = kwargs.pop('details', None)
        return CallResult(*args, **kwargs)

    await session.register(now, 'com.lojack.now')
    await session.register(echo, 'com.lojack.echo')

    print("session ready!")


if __name__ == "__main__":
    print('connecting to {}@{} ..'.format(CBREALM, CBURL))
    run([component])
