import os
import sys
from jinja2 import Environment, FileSystemLoader

config_name = sys.argv[1]
params = {
    'parallel_proxy': 4,
    'realm_names': ['dvl{}'.format(i + 1) for i in range(10)]
}

env = Environment(loader=FileSystemLoader('.'))

with open(os.path.join('node1/.crossbar', config_name), 'wb') as f:
    page = env.get_template(config_name)
    contents = page.render(**params)
    f.write(contents.encode('utf8'))
