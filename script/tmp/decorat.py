#!usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('../..')
import base
import tornado.web
import time
import urllib2

class test(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.isAuth = False
        self.isAccess = False

    def index(self):
        uid = self.current_user.get('id')
        return uid

def access_read(*arg):
    def _deco(func):
        def __deco(*args, **kwargs):
            print("before %s called [%s]." % (func.__name__, arg))
            print "user_id = ",test().index()
            func(*args, **kwargs)
            print("  after %s called [%s]." % (func.__name__, arg))
        return __deco
    return _deco
