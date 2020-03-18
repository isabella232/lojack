import sys
from jinja2 import Environment, FileSystemLoader

params = {
    'parallel_proxy': 4,
    'realm_names': ['dvl{}'.format(i + 1) for i in range(10)]
}

env = Environment(loader=FileSystemLoader('.'))

with open('node1/.crossbar/config.json', 'wb') as f:
    page = env.get_template(sys.argv[1])
    contents = page.render(**params)
    f.write(contents.encode('utf8'))
