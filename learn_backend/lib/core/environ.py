#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import imp
import sys

RUNTIME_OK = 0


class Environ(object):

    ENVIRON_PARAMS_NAME = 'Environ_name'
    ENVIRON_DOCUMENT_ROOT_NAME = 'Document_root'
    GLOBAL_ENVIRON = 'environ'
    BASE_SUB_ENVIRON = 'environs'
    DEFAULT_ENVIRON = 'defautls'
    CURRENT_ENVIRON = 'current'
    APP_FOLDER_NAME = 'apps'
    API_FOLDER_NAME = 'apis'
    FILTER_FOLDER_NAME = 'filters'

    _cache = {}

    # def __new__(cls, env_id, document_root):
    #
    #     super_new = super(Environ, cls).__new__
    #
    #     obj = cls._cache.get(env_id)
    #
    #     if not obj:
    #         obj = cls._cache[env_id] = super_new(cls, env_id, document_root)
    #         setattr(obj, '_modules', {})
    #         setattr(obj, '_paths', {})
    #
    #     return obj

    def __init__(self):
        pass
    #     self.identity = env_id
    #     self.document_root = document_root

    def app_path(self):
        object_list = self._paths.get('app_path', [])

        if not object_list:
            if not self.is_global():
                object_list = self.join_path(self.APP_FOLDER_NAME)

            object_list.append(os.path.join(self.document_root,
                                            self.APP_FOLDER_NAME))
        return object_list

    def api_path(self):

        object_list = self._paths.get('api_path', [])
        if not object_list:
            if not self.is_global():
                object_list = self.join_path(self.APP_FOLDER_NAME,
                                             self.API_FOLDER_NAME)

            object_list.append(os.path.join(self.document_root, self.APP_FOLDER_NAME,
                                            self.API_FOLDER_NAME))

        return object_list

    def filter_path(self):

        # return []
        object_list = self._paths.get('filter_path', [])

        if not object_list:
            if not self.is_global():
                object_list = self.join_path(self.APP_FOLDER_NAME,
                                             self.FILTER_FOLDER_NAME)

            object_list.append(os.path.join(self.document_root, self.APP_FOLDER_NAME),
                               self.FILTER_FOLDER_NAME)
        return object_list

    def join_path(self, *args):
        return
        # env, version = self.identity.split(':')

        # return [os.path.join(self.document_root, self.BASE_SUB_ENVIRON,
        #                    env, version, *args),
        #         os.path.join(self.document_root, self.BASE_SUB_ENVIRON,
        #                    self.DEFAULT_ENVIRON, version, *args),
        #         os.path.join(self.document_root, self.BASE_SUB_ENVIRON,
        #                       env, self.CURRENT_ENVIRON, *args)]

    def is_global(self):
        return True
        # return self.identity == self.GLOBAL_ENVIRON

    def multi(self):
        return False

    def import_module(self, module, path):

        for subpath in path:
            module_id = '%s:%s' % (subpath, module)
            obj = self._modules.get(module_id)

            try:
                if not obj:
                    obj = imp.load_module(module,
                                          *imp.find_module(module, [subpath]))
                    self._modules[module_id] = sys.modules.pop(module)
                return obj
            except ImportError, e:
                continue

        raise ImportError, "no module named %s" % module



class APIEnviron(object):

    METHOD_ARGUMENT_NAME = 'method'

    @classmethod
    def build_env(cls, req):

        # env_id = req.request.headers[Environ.ENVIRON_PARAMS_NAME]
        # document_root = req.request.headers[Environ.ENVIRON_DOCUMENT_ROOT_NAME]

        env = Environ()

        return cls(req, env)

    def __init__(self, req, env):
        self.req = req
        self.get_argument = req.get_argument
        self.get_arguments = req.get_arguments
        self.env = env
        self.errno = 0
        self.msg = {}
        self.headers = {}
        self.errno = RUNTIME_OK
        # self.storage = Storage(self)
        # self.cache = Cache(self)
        self.callbacks = []

        self.authenticate = True

        self.user = req.get_current_user(self)
        self.manager = Manager(self.user)
        self.game_config = None
        self.params = {}

    def finish(self):
        self.params = None
        self.game_config = None


class Manager(object):

    def __init__(self, user):
        self.user = user
        self._model = {}

    def get_model_key(self, uid, name):
        return "_%s_%s" % (uid, name)

    def get_user(self, uid):

        key = self.get_model_key(uid, 'user')
        if key in self._model:
            obj = self._model[key]
        else:
            obj = self.user.__class__.get(uid)

            self._model[key] = obj

        return obj