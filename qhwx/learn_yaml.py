import yaml

file_path = 'local_ghh.yaml'

class PrettySafeLoader(yaml.SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))


PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/tuple', PrettySafeLoader.construct_python_tuple)

with open(file_path) as f:
    GAMECONFIGJSON = yaml.load(f, Loader=PrettySafeLoader)

# print GAMECONFIGJSON


cfg_file = 'model.conf'
def configure(cfg_file):
    cf = open(cfg_file)
    try:
        gs = {}
        exec (cf.read(), gs)
        for k in gs:
            if k != "__builtins__":
                print k, gs[k]
    finally:
        cf.close()

configure(cfg_file)

# config_name = 'redbag'
# class A():
#     config_value = {'ddd': 'ddd'}
# config = A()
# exec (config_name + '=config.config_value')
# print config.config_value


class A:

    def __init__(self):
        self._uid = None

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, val):
        self._uid = val


a = A()
print a.uid
a.uid = '3'
print a.uid


class B:

    def __init__(self):
        self.gov_value = 0
        self.wit_value = 0
        self.skill = {}

    @classmethod
    def _install(cls, gov_value=0, wit_value=0):
        b = cls()
        b.gov_value = gov_value
        b.wit_value = wit_value
        return b

class C:

    @property
    def bonus(self):
        z = B._install(3, 4)
        return reduce(lambda x, y: x + y, [z])

b = B()
c = C()
a = {}
f = dict.setdefault(a, B._install())