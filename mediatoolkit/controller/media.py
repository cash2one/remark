# -*- coding:utf-8 -*-

import base as base

class Media(base.base):
    """ 自媒体
    """
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        self.display('index')

    def create(self):
        title = self.I('title')
        content = self.I('content')
        user_id = self.current_user.get('id')
        if not title or not content:
            self.out(401)

        status = self.importService('mediaTool_content').create_content(title, content, user_id)
        self.out(status)

    def get_content(self):
        data = self.importService('mediaTool_content').get_content()
        if data:
            self.out(200, '', data)
        else:
            self.out(404)