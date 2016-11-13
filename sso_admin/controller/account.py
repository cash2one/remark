# -*- coding:utf-8 -*-

import base


class Account(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.isAuth = False
        self.isAccess = False

    def index(self):
        """
        :func: 登录
        """
        
        # 获取参数
        strAccount =self.I('account', '')
        strPassword = self.I('password', '')
        strRedirectUrl = self.I('redirect_url', 'http://www.baidu.com')
        
        # 判断参数
        if strAccount == "" or strPassword == "":
            self.display('login')
            return
        
        # 调用Service
        accountService = self.importService('admin_account')
        dicReturn = accountService.login({
            'account': strAccount,
            'password': strPassword
        })
                
        # 记录登录状态
        if dicReturn['status'] == 200:
            self.set_secure_cookie("user_id", str(dicReturn['user']['id']))
            self.set_secure_cookie("user_nickname", str(dicReturn['user']['nickname'].encode('utf8')))
            self.redirect(strRedirectUrl + "?user_id=%s&user_nickname=%s" 
                            % (str(dicReturn['user']['id']), str(dicReturn['user']['nickname'].encode('utf8'))))
            
        self.out(dicReturn['status'])

    def logout(self):
        """
        :func: 登出
        """
        try:
            self.set_secure_cookie('user_id', '')
            self.set_secure_cookie('user_nickname', '')
            self.redirect('/login')
        except Exception, e:
            self.out(500)
