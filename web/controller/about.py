# -*- coding:utf-8 -*-

import base as base

class About(base.base):
    """ 关于我们及其它
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        base.base.initialize(self)

    def index(self):
        """
        """

        self.display('about');

    def contact(self):
        """
        """

        self.display('contact');

