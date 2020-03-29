import os
import sys
import math
import json
from jinja2 import Environment, FileSystemLoader

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

config_name = sys.argv[1]
config_out_name = sys.argv[2]

# is_production = len(sys.argv) > 3 and sys.argv[3] is not None
is_production = 'CBPRODUCTION' in os.environ

if is_production:
    print('configuring for PRODUCTION ..')
    ENDPOINT = {
        'type': 'tcp',
        'port': 443,
        'shared': True,
        'backlog': 1024,
        'tls': {
            'certificate': 'lojack1.crossbario.com.crt',
            'key': 'lojack1.crossbario.com.key',
            'dhparam': 'dhparam.pem',
            'chain_certificates': [
                'lojack1.crossbario.com.issuer.crt'
            ],
            'ciphers': 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256'
        }
    }
else:
    print('configuring for DEVELOPMENT ..')
    ENDPOINT = {
        'type': 'tcp',
        'port': 8080,
        'shared': True,
        'backlog': 1024
    }

params = {
    'parallel_router': 2,
    'parallel_proxy': 4,
    'realm_names': ['dvl{}'.format(i + 1) for i in range(10)]
}
assert len(params['realm_names']) >= params['parallel_router']

chunk_len = int(math.ceil(len(params['realm_names']) / params['parallel_router']))

params['realm_names_per_router'] = list(enumerate(chunks(params['realm_names'], chunk_len)))

res = {}
for router_no, router_realms in params['realm_names_per_router']:
    for realm_name in router_realms:
        res[realm_name] = router_no
params['realm_name_to_router'] = list(res.items())

params['endpoint'] = json.dumps(ENDPOINT, ensure_ascii=False)

from pprint import pprint
pprint(params)

env = Environment(loader=FileSystemLoader('.'))

with open(config_out_name, 'wb') as f:
    page = env.get_template(config_name)
    contents = page.render(**params)
    f.write(contents.encode('utf8'))
