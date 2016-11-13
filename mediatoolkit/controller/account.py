# -*- coding:utf-8 -*-

import time
import base

class Account(base.base):
    def initialize(self):
        base.base.initialize(self)
        self.account_service = self.importService('account')

    def index(self):
        self.out(200)

    def signup(self):
        if self._POST:
            str_nickname = self.I('nickname')
            str_phone = self.I('phone')
            str_verify_code = self.I('verify_code')
            str_password = self.I('password')

            if '%s--%s' % (str_phone, str_verify_code) != self.get_secure_cookie('verify_code'):
                self.out(601)
                return

            user_id = self.account_service.signup(str_nickname, str_phone, str_password)
            if self.account_service.status == 200:
                self.set_secure_cookie("user_id",       str(user_id))
                self.set_secure_cookie("user_avatar",   'none')
                self.set_secure_cookie("user_nickname", str_nickname)
                self.set_secure_cookie('verify_code',   '')
            self.out(self.account_service.status)
            return
        self.display('signup')

    def bind_phone(self):
        str_status = self.I('status')
        if self._POST:
            str_phone       = self.I('phone')
            str_verify_code = self.I('verify_code')
            str_password    = self.I('password')

            if '%s--%s' % (str_phone, str_verify_code) != self.get_secure_cookie('verify_code'):
                self.out(601)
                return

            ## 已有用户手机绑定
            str_uid = self.get_secure_cookie('uid')
            if not str_uid and str_status == '1':
                str_uid = self.get_secure_cookie('user_id')
            if str_uid:
                dicResp = self.account_service.bind_phone(str_uid, str_phone, str_password)
                if not dicResp:
                    self.out(self.account_service.status)
                    return
                if self.account_service.status == 200:
                    self.set_secure_cookie("user_id", dicResp['user_id'])
                    self.set_secure_cookie("user_avatar", dicResp['avatar'])
                    self.set_secure_cookie("user_nickname", dicResp['nickname'])
                    self.set_secure_cookie('verify_code',   '')
                    self.set_secure_cookie('uid', '')
                self.out(self.account_service.status)
                return

            ## 微信注册手机绑定
            str_wechat_data = self.get_secure_cookie('wechat_data')
            if str_wechat_data:
                dic_wechat_data = self.json.loads(str_wechat_data)
                str_nickname = dic_wechat_data['nickname']
                int_user_id = self.account_service.signup(str_nickname, str_phone, str_password)
                if self.account_service.status != 200:
                    self.out(self.account_service.status)
                    return

                dic_wechat_data['user_id'] = int_user_id
                user_service = self.importService('user')
                user_service.create_wechat_data(dic_wechat_data)
                if user_service.status != 200:
                    self.out(user_service.status)
                    return

                self.set_secure_cookie("user_id",       str(int_user_id))
                self.set_secure_cookie("user_avatar",   'none')
                self.set_secure_cookie("user_nickname", str_nickname)
                self.set_secure_cookie('verify_code',   '')
                self.out(200)
                return

        self.display('bind_phone')

    ###
    def verify_phone(self):
        strPhone = self.I('phone')
        # print strPhone
        # fuck 谁加的代码， 没账号就不发短信，那一万年也注册不上了， 以屎为鉴
        # account = self.account_service.get_account(strPhone)
        # if len(account) == 0:
        #     self.out(300)
        #     return

        # 生成验证码
        strVerifyCode = self.salt(6, True)
        # print strVerifyCode
        # 记录cookie
        self.set_secure_cookie("verify_code", '%s--%s' % (strPhone, strVerifyCode), expires=time.time()+900)
        # print strPhone
        import api.sms as sms
        sms.sendsms(strPhone, 'verify_phone', {
            'verify_code': strVerifyCode
        })

        self.out(200)

    ## 检测手机是否用过
    def check_account(self):
        strPhone = self.I('phone')
        account = self.account_service.get_account(strPhone)
        if isinstance(account, dict):
            if len(account) > 0:
                self.out(300)
            else:
                self.out(200)
        return

    def verify_user(self):
        strPhone = self.I('phone')
        strCode = self.I('verify_code')
        strInput = '%s--%s' % (strPhone, strCode)
        strVerifyCode = self.get_secure_cookie('verify_code')
        if strInput != strVerifyCode:
            self.out(601)
            return
        self.out(200, dicData={'set_new_pass':
            """
            <div id="set_new_pass" class="signBox">
            <h2>设置密码</h2><h3>为了你的账号安全，请输入新的密码</h3>
                <label>
                    <span>新密码</span>
                    <input id="phone" type="text" value="%s" style="display:none;">
                    <input id="verify_code" type="text" value="%s" style="display:none;">
                    <input type="password" style="display:none;">
                    <input type="password" id="password" name="password" value="" placeholder="6-32个字符">
                    <em class="errorTips" id="tip4"></em>
                </label>
                <button class="submitBtn" onclick="set_new_pass()">保存</button>
                <div class="tips">如果你的账号是邮箱注册，请联系右侧客服找回。</div>
            </div>
            """ % (strPhone, strCode)
        })


    def set_password(self):
        strPhone = self.I('phone')
        strCode = self.I('verify_code')

        strPassword = self.I('password')
        strInput = '%s--%s' % (strPhone, strCode)
        strVerifyCode = self.get_secure_cookie('verify_code')
        if strInput != strVerifyCode:
            self.out(601)
            return

        account = self.account_service.get_account(strPhone)
        if len(account) == 0:
            self.out(300)
            return

        self.account_service.set_password(account['user_id'], strPassword)
        if self.account_service.status == 200:
            dic_user = self.importService('user').get_user(account['user_id'])
            self.set_secure_cookie("user_id", str(dic_user['id']))
            self.set_secure_cookie("user_avatar", str(dic_user['avatar']))
            self.set_secure_cookie("user_nickname", str(dic_user['nickname'].encode('utf8')))
            self.set_secure_cookie('verify_code', '')
        self.out(self.account_service.status)


    def change_password(self):
        """ 修改密码
        """
        strOldPassword = self.I('opwd')
        strNewpassword = self.I('npwd')
        strReNewPassword = self.I('npwd2')
        self.account_service.change_password(self.current_user['user_id'], strOldPassword, strNewpassword, strReNewPassword)
        self.out(self.account_service.status)

    def forget_pwd(self):
        """ 忘记密码
        """
        self.display('forget_pwd')


