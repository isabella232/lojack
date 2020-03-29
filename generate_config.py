import os
import sys
import math
from jinja2 import Environment, FileSystemLoader

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

config_name = sys.argv[1]
config_out_name = sys.argv[2]

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

from pprint import pprint
pprint(params)

env = Environment(loader=FileSystemLoader('.'))

with open(config_out_name, 'wb') as f:
    page = env.get_template(config_name)
    contents = page.render(**params)
    f.write(contents.encode('utf8'))
