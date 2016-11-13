# -*- coding:utf-8 -*-

import base

# 首页
class Debug(base.base):

    def initialize(self):
        base.base.initialize(self)

    def index(self):
        # print self.request.uri
        # print self.request.arguments
        self.out('error')
        pass

    def write_cookie(self):
        str_uid = self.I('uid')
        self.set_secure_cookie("user_id", str_uid)
        self.out('success')

    def clean_cookie(self):
        self.set_secure_cookie("user_id", '')
        self.out('success')
