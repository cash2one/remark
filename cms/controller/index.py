# -*- coding:utf-8 -*-

import base


class index(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        self.dicViewData['menu'] = ''
        self.display('index')
