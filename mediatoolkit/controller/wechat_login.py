# -*- coding:utf-8 -*-

import time
import base


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
