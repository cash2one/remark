# -*- coding:utf-8 -*-

import base

class center(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'center'
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').index(uid)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = dicData
        self.display('index', 'admin_user')

    def changPass(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').changePass(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/admin_user/center'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def checkOldPass(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            dicResp = self.importService('admin_user').checkOldPass(args)
            statusCode = dicResp['statusCode']
            self.out(statusCode, '', {})

    def update(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            dicResp = self.importService('admin_user').updateAccout(args)
            self.out(dicResp['statusCode'])
        else:
            self.out(500)