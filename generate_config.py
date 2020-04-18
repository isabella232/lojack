import os
import sys
import math
import json
from jinja2 import Environment, FileSystemLoader

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

hostname = sys.argv[1]
config_name = sys.argv[2]
config_out_name = sys.argv[3]

if len(sys.argv) > 4:
    config_routers = int(sys.argv[4])
else:
    config_routers = 2

if len(sys.argv) > 5:
    config_proxies = int(sys.argv[5])
else:
    config_proxies = 4

# is_production = len(sys.argv) > 3 and sys.argv[3] is not None
is_production = 'CBPRODUCTION' in os.environ and int(os.environ['CBPRODUCTION'])

ENDPOINTS = []

if is_production:
    ENDPOINTS.append(json.dumps({
        'type': 'tcp',
        'port': 443,
        'shared': True,
        'backlog': 1024,
        'tls': {
            'certificate': '{}.crt'.format(hostname),
            'key': '{}.key'.format(hostname),
            'dhparam': 'dhparam.pem',
            'chain_certificates': [
                '{}.issuer.crt'.format(hostname)
            ],
            'ciphers': 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256'
        }
    }, ensure_ascii=False))
    ENDPOINTS.append(json.dumps({
        'type': 'tcp',
        'port': 80,
        'shared': True,
        'backlog': 1024
    }, ensure_ascii=False))
else:
    ENDPOINTS.append(json.dumps({
        'type': 'tcp',
        'port': 80,
        'shared': True,
        'backlog': 1024
    }, ensure_ascii=False))

params = {
    'parallel_router': config_routers,
    'parallel_proxy': config_proxies,
    'realm_names': ['dvl{}'.format(i + 1) for i in range(8)]
}
assert len(params['realm_names']) >= params['parallel_router']

chunk_len = int(math.ceil(len(params['realm_names']) / params['parallel_router']))

params['realm_names_per_router'] = list(enumerate(chunks(params['realm_names'], chunk_len)))

res = {}
for router_no, router_realms in params['realm_names_per_router']:
    for realm_name in router_realms:
        res[realm_name] = router_no
params['realm_name_to_router'] = list(res.items())

params['endpoints'] = ENDPOINTS

from pprint import pprint
pprint(params)

env = Environment(loader=FileSystemLoader('.'))

with open(config_out_name, 'wb') as f:
    page = env.get_template(config_name)
    contents = page.render(**params)
    f.write(contents.encode('utf8'))
