#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

from sqlalchemy.orm.instrumentation import instance_dict
from sqlalchemy.orm.loading import sessionlib
from sqlalchemy.orm.loading import load_scalar_attributes as load_scalar_attributesOld
from sqlalchemy.orm.attributes import InstrumentedAttribute as InstrumentedAttributeOld

from Source.DataBase.Common.DBEngine import DBEngine


class MyInstrumentedAttribute(InstrumentedAttributeOld):

    def __get__(self, instance, owner):
        if instance is None:
            return self
        dict_ = instance_dict(instance)
        if self.key in dict_:
            return dict_[self.key]
        else:
            return InstrumentedAttributeOld.__get__(self, instance, owner)
        # return InstrumentedAttributeOld.__get__(self, instance, owner)


def My_load_scalar_attributes(mapper, state, attribute_names):
    session = sessionlib._state_session(state)
    if not session:
        DBEngine.NewSession()._save_or_update_state(state)
    return load_scalar_attributesOld(mapper, state, attribute_names)


sqlalchemy = __import__("sqlalchemy")
# sqlalchemy.orm.attributes.InstrumentedAttribute = MyInstrumentedAttribute
sqlalchemy.orm.loading.load_scalar_attributes = My_load_scalar_attributes