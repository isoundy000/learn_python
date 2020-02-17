#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings
from lib.utils.encoding import force_unicode

module_name = "return_msg_" + settings.LANG

module = __import__('lang_config.%s' % module_name, globals(), locals(), ["return_msg_config", "i18n"])
return_msg_config = getattr(module, "return_msg_config")
i18n = getattr(module, "i18n")


class I18nMsg(object):

    def __init__(self, i18n):
        self.i18n = i18n

    def __call__(self, flag, *args, **kwargs):
        msg = self.i18n.get(flag)
        if not msg:
            return u''

        return force_unicode(msg)

    def __getitem__(self, item):
        msg = self.i18n.get(item)
        if not msg:
            return u''

        return force_unicode(msg)


i18n_msg = I18nMsg(i18n)