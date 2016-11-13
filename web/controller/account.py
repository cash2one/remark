# -*- coding:utf-8 -*-

import base
import requests
import time

class Login(base.base):
    """ 登录
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.accountService = self.importService('account')

    def index(self):
        """
        """

        # 获取参数
        strAccount  = self.I('account')
        strPassword = self.I('password')

        # 判断参数
        if not strAccount :
            #print  1111
            self.out(401)
            return
        elif not strPassword:
            self.out(402)
            return 
        # 调用Service
        dic_user = self.accountService.login(strAccount, strPassword)
        if self.accountService.status != 200:
            self.out(self.accountService.status)
            return

        ## 是否绑定手机
        intStatus = self.accountService.check_phone(dic_user['id'])
        if intStatus != 200:
            self.set_secure_cookie('uid', str(dic_user['id']))
            self.out(201)
            return
        
        # 记录登录状态
        if self.accountService.status == 200:
            self.set_secure_cookie("user_id", str(dic_user['id']))
            self.set_secure_cookie("user_avatar", str(dic_user['avatar']))
            self.set_secure_cookie("user_nickname", str(dic_user['nickname'].encode('utf8')))
            self.set_secure_cookie('media_vcode', '')
        self.out(self.accountService.status)


    def logout(self):
        """ 登出
        """

        try:
            self.set_secure_cookie('user_id', '')
            self.set_secure_cookie('user_avatar', '')
            self.set_secure_cookie('user_nickname', '')

            self.redirect('/')
        except Exception, e:
            self.out(500)

    def forget_pwd(self):
        """ 忘记密码
        """

        if self._POST:
            # 提交
            strEmail = self.I('email')
            if not strEmail:
                return 401

            # 验证字串
            strVcode = self.salt(32)
            strForgetPwdVcode = strVcode + '|' + str(int(self.time.time())) + '|' + strEmail
            # 记录cookie
            self.set_secure_cookie('forget_pwd_vcode', strForgetPwdVcode, strVcode, expires=time.time()+900)
            # 验证邮箱是否存在
            accountService = self.importService('account')
            intStatus = accountService.forget_pwd(strEmail, self.md5(strForgetPwdVcode))
            self.out(intStatus)
            return

        self.display('forget_pwd');

    def change_pwd(self):
        """ 修改密码
        """

        # 获取参数
        strVcode = self.I('v')

        # 读取cookie值
        strForgetPwdVcode = self.get_secure_cookie('forget_pwd_vcode', strVcode, expires=time.time()+900)
        
        # 验证是否匹配
        if strVcode != self.md5(strForgetPwdVcode):
            self.redirect('/602')
            return

        # 提取邮箱
        lisVcode = strForgetPwdVcode.split('|')
        if len(lisVcode) < 3:
            self.redirect('/603')
            return
            
        if self._POST:
            strEmail = self.I('email')
            strPassword = self.I('password')
            strRePassword = self.I('re_password')

            accountService = self.importService('account')
            intStatus = accountService.reset_password(strEmail, strPassword, strRePassword)
            self.out(intStatus)
            return

        strEmail = lisVcode[2]

        self.dicViewData['email'] = strEmail
        self.dicViewData['token'] = strVcode

        self.display('change_pwd')



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


class WechatLogin(base.base):
    """ 微信登录
    """

    def initialize(self):

        base.base.initialize(self)

        self.accountService = self.importService('account')
        self.userService = self.importService('user')

    def get_wechat_info(self, code):
        # 通过code获取access_token
        try:
            r = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=wxb3f7618fff2272e5&secret=3e56a584d7412fe5791c83b87bfb8ac8&code={}&grant_type=authorization_code'.format(code))
            data = r.json()

            # 通过access_token和openid获取用户的基础信息，包括头像、昵称、性别、地区
            r = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s' % (data["access_token"], data['openid'] ))
            return self.json.loads(r.text.encode('ISO-8859-1'))
        except Exception, e:
            print e
            self.redirect('/')

    def index(self):
        """
        """
        # 生成二维码登陆的链接，嵌入到JS上 
        # https://open.weixin.qq.com/connect/qrconnect?appid=wxb3f7618fff2272e5&redirect_uri=http://www.yidao.info/weixin_login&response_type=code&scope=snsapi_login&state=2014#wechat_redirect
        # 获取参数
        strState = self.I('state')
        strCode = self.I('code')
        if strState:
            dicRequestData = {}
            wx = self.get_wechat_info(strCode)
            if wx:
                dicRequestData = {
                    'openid'    : wx['openid'],
                    'nickname'  : wx['nickname'],
                    'province'  : wx['province'],
                    'headimgurl': wx['headimgurl'],
                    'language'  : wx['language'],
                    'city'      : wx['city'],
                    'country'   : wx['country'],
                    'sex'       : wx['sex'],
                    'unionid'   : wx['unionid'],
                    'privilege' : wx['privilege']
                }

                # 验证是否已经注册
                dicUserWechat = self.userService.get_wechat_by_openid(dicRequestData['openid'])
                if not dicUserWechat:
                    # 注册
                    intStatus = self.register(dicRequestData)
                else:
                    dicUser = self.userService.get_user(dicUserWechat['user_id'])

                    ## 是否绑定手机
                    intStatus = self.accountService.check_phone(dicUserWechat['user_id'])
                    if intStatus != 200:
                        self.set_secure_cookie('uid', str(dicUserWechat['user_id']))
                        self.display('bind_phone', 'Account')
                        return

                    # 登录
                    self.set_secure_cookie("user_id", str(dicUser['id']))
                    self.set_secure_cookie("user_avatar", str(dicUser['avatar']))
                    self.set_secure_cookie("user_nickname", str(dicUser['nickname'].encode('utf8')))

                    self.redirect('/');

    def register(self, dicData):
        """ 微信注册 
        """
        
        #print dicData
        self.set_secure_cookie('wechat_data', self.json.dumps(dicData))
        self.display('bind_phone', 'Account')
                         
        ## 检查是否有openid相同的帐号
        ## 如果有，直接绑定，如果没有，显示绑定界面
        #user_service = self.importService('user')
        #dicUser = user_service.get_wechat_by_openid(dicData['openid'])
        #if not dicUser:
        #    # 记录数据到cookie
        #    self.set_secure_cookie('wechat_data', self.json.dumps(dicData))
        #    self.display('bind_phone')
        #else:
        #    dicData['user_id'] = dicUser['user_id']
        #    dicResult = self.accountService.register_bind(dicData)
        #    if dicResult['status'] == 200:
        #        self.set_secure_cookie("user_id", str(dicUser['user_id']))
        #        self.set_secure_cookie("user_avatar", dicUser['avatar'])
        #        self.set_secure_cookie("user_nickname", dicUser['nickname'])
        #
        #        self.redirect('/');
        #    else:
        #        self.out(dicResult['status'], 'Reg failed!')

    def bind_account(self):
        """ 绑定帐号
        """

        if not self._POST:
            self.out(501);
            return
            
        # 检测cookie是否有值
        strData = self.get_secure_cookie('weixin_data')
        if not strData:
            self.out(602)
            return

        dicData = self.json.loads(strData)
        
        # 获以参数
        dicData['account'] = self.I('email')
        dicData['password'] = self.I('password')

        if not dicData['account'] or not dicData['password']:
            self.out(401)
            return

        # 生成帐号信息
        dicResult = self.accountService.register_open(dicData)
        if dicResult['status'] == 200:
            self.set_secure_cookie("user_id", str(dicResult['user_id']))
            self.set_secure_cookie("user_avatar", 'none')
            self.set_secure_cookie("user_nickname", dicResult['nickname'])
            self.set_secure_cookie('weixin_data', '')

        self.out(dicResult['status'])

    def reg_test(self):
        self.display('bind_email')

class BindWechat(base.base):
    """ 绑定微信
    """
    
    def initialize(self):
        
        base.base.initialize(self)

        self.accountService = self.importService('account')
        self.userService = self.importService('user')
        
    def get_wechat_info(self, code):
        # 通过code获取access_token
        r = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=wxb3f7618fff2272e5&secret=3e56a584d7412fe5791c83b87bfb8ac8&code={}&grant_type=authorization_code'.format(code))
        data = r.json()

        # 通过access_token和openid获取用户的基础信息，包括头像、昵称、性别、地区
        r = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s' % (data["access_token"], data['openid'] ))
        return self.json.loads(r.text.encode('ISO-8859-1'))

    def index(self):
        """ 绑定微信
        """

        if not self.current_user['user_id']:
            self.redirect('/401')
            return
        
        strState = self.I('state')
        strCode = self.I('code')

        wx = self.get_wechat_info(strCode)
        if wx:
            dicRequestData = {
                'openid'    : wx['openid'],
                'nickname'  : wx['nickname'],
                'province'  : wx['province'],
                'headimgurl': wx['headimgurl'],
                'city'      : wx['city'],
                'country'   : wx['country'],
                'sex'       : wx['sex'],
                'unionid'   : wx['unionid'],
                'privilege' : wx['privilege'],
                'user_id'   : self.current_user['user_id']
            }

            # 判断微信是否已经绑定
            dicWechat = self.userService.get_wechat_by_openid(dicRequestData['openid'])
            user_service = self.importService('user')
            if not dicWechat:
                # 绑定
                user_service.create_wechat_data(dicRequestData)
                if user_service.status != 200:
                    self.redirect('/user')
                    return
            else:
                user_service.update_wechat_data(dicRequestData)
                if user_service.status != 200:
                    self.redirect('/user')
                    return
            self.redirect('/user?a=bind')
