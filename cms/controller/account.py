# -*- coding:utf-8 -*-

import time
import base

class login(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.isAuth = False
        self.isAccess = False

    def index(self):
        """
        :func: 登录
        """
        if self._POST:
            dicArgs = self.request.arguments
            if not isinstance(dicArgs, dict):
                self.redirect('/login')
                return
            dicResp = self.importService('admin_account').login(dicArgs)
            if dicResp['status'] == 200:
                self.set_secure_cookie("user_id",       str(dicResp['user']['id']),                      expires=time.time() + 1800)
                self.set_secure_cookie("user_name",     str(dicResp['user']['nickname'].encode('utf8')), expires=time.time() + 1800)
                # self.redirect('/')
                self.out(dicResp['status'])
            else:
                self.out(dicResp['status'])
            return
        self.display('login')

    def logout(self):
        """
        :func: 登出
        """
        try:
            self.set_secure_cookie('user_id', '')
            self.set_secure_cookie('user_name', '')
            self.set_secure_cookie('user_access', '')
            self.redirect('/login')
        except Exception, e:
            print e
            self.out(500)
