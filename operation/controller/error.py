# -*- coding:utf-8 -*-

import base


class error(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        self.display('404')
