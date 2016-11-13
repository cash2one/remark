# -*- coding:utf-8 -*-

import base as base


# 帐号Service
class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        # 数据对象
        self.account_model = self.importModel('account')
        self.user_model = self.importModel('user')
        self.area_model = self.importModel('area')
        self.user_wechat_model = self.importModel('user_wechat')
        self.wallet_model = self.importModel('wallet')
        self.pay_model = self.importModel('pay')

    def login(self, str_account, str_password):
        """ 登录
        @params 
            str_account     帐号
            str_password    密码
        """

        # 检测帐号
        dic_account = self.get_account(str_account)
        if not dic_account:
            self.status = 601
            return

        # 检测密码
        if dic_account['password'] != self.get_password(str_password, dic_account['salt']):
            self.status = self.model.dicConfig['SERVICE_ACCOUNT_PASSWORD_ERROR']
            return

        # 得到用户信息
        user_service = self.importService('user')
        dic_user = user_service.get_user(dic_account['user_id'])

        if dic_user['status'] != 0:  # 非正常用户
            self.status = 704
            return
        self.status = user_service.status

        return dic_user

    # def register(self, str_account, str_password, str_nickname):
    #    """ 注册
    #
    #    @params
    #        str_account     帐号
    #        str_password    密码
    #        str_nickname    昵称
    #    """
    #
    #    # 检测帐号
    #    dic_account = self.get_account(str_account)
    #    if dic_account:
    #        return
    #
    #    # 生成salt
    #    strPassword = self.get_password(str_password, self.salt())
    #    
    #    # 生成user信息
    #    int_user_id = self.user_model.insert({
    #        'key': 'nickname',
    #        'val': '"%s"' % dicData['nickname']
    #    })
    #    if self.model.db.status != self.model.dicConfig['DB_OK']:
    #        self.status = self.model.dicConfig['SERICE_DB_ERROR']
    #        return
    #
    #    # 生成帐号信息
    #    self.account_model.insert({
    #        'key': 'user_id, account, password, salt, create_time',
    #        'val': '"%s", "%s", "%s", "%s", "%s"' % (int_user_id,
    #                                                dicData['account'], 
    #                                                strPassword, 
    #                                                strSalt, 
    #                                                int(self.time.time()))
    #    })
    #    if self.model.db.status != self.model.dicConfig['DB_OK']:
    #        self.status = self.model.dicConfig['SERICE_DB_ERROR']
    #        return
    #
    #    return int_user_id

    # def register_open(self, dicData):
    #     """ 第三方登录注册
    #
    #     @params dicData dict
    #     """
    #
    #     dicReturn = {
    #         'status': 0,
    #         'user_id': None
    #     }
    #
    #     # 判断帐号是否存在
    #     dicUser = self.get_user_by_account(dicData['account'])
    #     # 如果存在，判断密码是否正确
    #     if dicUser:
    #         strPassword = self.hashlib.sha256('%s -- %s' % (dicData['password'], dicUser['salt'])).hexdigest()
    #         if strPassword != dicUser['password']:
    #             return {'status': 602}
    #         else:
    #             intInsertId = dicUser['user_id']
    #             dicData['nickname'] = dicUser['nickname']
    #     else:
    #         # 生成salt
    #         strSalt = self.salt()
    #         strPassword = self.hashlib.sha256('%s -- %s' % (dicData['password'], strSalt)).hexdigest()
    #
    #         # 生成验证字符串
    #         strVerificationCode = self.salt(65)
    #
    #         intInsertId = self.account_model.insert({
    #             'key': 'account, password, salt, nickname, verification_code, create_time',
    #             'val': '"%s", "%s", "%s", "%s", "%s", "%s"' % (
    #                 dicData['account'],
    #                 strPassword,
    #                 strSalt,
    #                 dicData['nickname'],
    #                 strVerificationCode,
    #                 int(self.time.time())
    #             )
    #         })
    #         if self.model.db.status != 200:
    #             return {}
    #
    #     # 三方帐号信息
    #     self.user_wechat_model.insert({
    #         'key': 'user_id, \
    #             province, \
    #             openid, \
    #             headimgurl, \
    #             language, \
    #             city, \
    #             country, \
    #             sex, \
    #             unionid, \
    #             privilege, \
    #             nickname, \
    #             status, \
    #             created_at',
    #         'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
    #             intInsertId,
    #             dicData['province'],
    #             dicData['openid'],
    #             dicData['headimgurl'],
    #             dicData['language'],
    #             dicData['city'],
    #             dicData['country'],
    #             dicData['sex'],
    #             dicData['unionid'],
    #             dicData['privilege'],
    #             dicData['nickname'],
    #             0,
    #             self.formatTime(int(self.time.time())),
    #         )
    #     })
    #     if self.model.db.status != 200:
    #         return {}
    #
    #     # 处理头像
    #     dicReturn = {
    #         'status': 200,
    #         'user_id': intInsertId,
    #         'nickname': dicData['nickname']
    #     }
    #     return dicReturn

    def get_list(self, strUserId):
        """ 根据user_id获取多条数据，多个用,事情分割
        """

        if not strUserId:
            return 401

        tupUser = self.account_model.findMany({
            'condition': 'user_id in (%s)' % strUserId
        })

        return tupUser

    ##################################################################################################
    def get_account(self, str_account):
        """ 获得账号信息

        @params str_account string 帐号
        """

        dic_account = self.account_model.findOne({'condition': 'account = "%s"' % str_account})

        return dic_account

    def get_account_by_user_id(self, str_user_id):
        """ 获取账户信息

        @params str_user_id string 用户ID
        """

        tup_account = self.account_model.findMany({'condition': 'user_id = %s' % str_user_id})
        return tup_account

    #####################################################################
    # def bind_wechat(self, dicData):
    #     """ 绑定微信
    #     """
    #     import sys
    #     sys.stderr.write(str(dicData))
    #     user_wechat_model = self.importModel('user_wechat')
    #     user_wechat_model.insert({
    #         'key': 'user_id, openid, nickname, sex, province, city, county, '
    #                'headimgurl, privilege, unionid, status, created_time',
    #         'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", 0, "%s"' % (
    #             dicData['user_id'],
    #             dicData['openid'],
    #             dicData['nickname'],
    #             dicData['sex'],
    #             dicData['province'],
    #             dicData['city'],
    #             dicData['country'],
    #             dicData['headimgurl'],
    #             dicData['privilege'],
    #             dicData['unionid'],
    #             int(self.time.time()),
    #         )
    #     })
    #     if self.model.db.status != 200:
    #         self.status = 601

    def check_phone(self, str_user_id):
        dicData = self.account_model.findOne({
            'condition': 'user_id = %s and account_type = 2' % str_user_id
        })
        if dicData:
            return 200
        else:
            return 404

    def bind_phone(self, str_uid, str_phone, str_password):
        dicAccount = self.account_model.findOne({
            'condition': 'user_id = %s' % str_uid
        })
        # 微信跳转，无帐号
        if not dicAccount:
            str_salt = self.salt()
            str_password = self.get_password(str_password, str_salt)
        # 邮箱跳转，有帐号
        else:
            str_salt = dicAccount['salt']
            if self.get_password(str_password, str_salt) != dicAccount['password']:
                self.status = 603
                return
            str_password = dicAccount['password']
        dicUser = self.importModel('user').findOne({
            'fields': ['nickname, avatar'],
            'condition': 'id = %s' % str_uid
        })
        self.account_model.insert({
            'key': 'user_id, account, password, salt, account_type, create_time',
            'val': '%s, "%s", "%s", "%s", %s, %s' % (
                str_uid, str_phone, str_password, str_salt, 2, int(self.time.time()))
        })
        self.user_model.update({
            'fields': ['phone = "%s"' % str_phone],
            'condition': 'id = %s' % str_uid
        })
        return {'user_id': str_uid, 'avatar': dicUser['avatar'], 'nickname': dicUser['nickname']}

    ######################################################################
    def bind_email(self, strUserId, strEmail, strPassword):
        """ 绑定邮箱

        @params strUserId string 用户 ID
        @params strEmail string 旧邮箱，第一次绑定为空
        @params strPassword string 登录密码
        """
        dicAccount = self.account_model.findOne({
            'condition': 'user_id = %s' % strUserId
        })
        if dicAccount['password'] != self.hashlib.sha256('%s -- %s' % (strPassword, dicAccount['salt'])).hexdigest():
            return 603
        # 发邮件
        # 变更邮箱链接
        strDeadLine = str(int(self.time.time()) + 60 * 60 * 24)
        strCode = self.hashlib.md5(strUserId + strEmail + strDeadLine).hexdigest()
        strChangeLink = 'http://%s/user?a=change_email&uid=%s&deadline=%s&email=%s&code=%s' % \
                        (self.param['host'], strUserId, strDeadLine, strEmail, strCode)

        # 发送邮件
        import api.sendcloud as sendcloud
        boolStatus = sendcloud.send_template_mail('【一道】修改邮箱', **{
            'template_invoke_name': '32187_invoke_25',
            'substitution_vars': '{"sub": {"{{ u.nickname }}": ["尊敬的用户"], '
                                 '"{{ new_email }}": ["%s"], '
                                 '"{{ change_link }}": ["%s"]}, '
                                 '"to": ["%s"]}' % (strEmail, strChangeLink, strEmail)
        })
        if not boolStatus:
            return 500
        #
        return 200

    def change_email(self, strUserId, strDeadLine, strEmail, strCode):
        # 检测链接是否篡改
        if strCode != self.hashlib.md5(strUserId + strEmail + strDeadLine).hexdigest():
            return 401
        # 检测链接是否在有效期内
        if int(self.time.time()) > int(strDeadLine):
            return 601
        intStatus = self.update_account_by_email(strUserId, strEmail)
        return intStatus

    def set_password(self, str_user_id, str_password):
        # 新salt
        strSalt = self.salt()
        # 新密码
        strPasswordSalt = self.get_password(str_password, strSalt)

        # 根据user_id修改所有的account密码
        self.account_model.update({
            'fields': ['password = "%s"' % strPasswordSalt, 'salt = "%s"' % strSalt],
            'condition': 'user_id = "%s"' % str_user_id
        })
        if self.model.db.status != 200:
            self.status = 601

    #####################################################################################
    # def forget_pwd(self, strEmail, strForgetPwdVcode):
    #     """ 找回密码
    #
    #     @params strEmail string 邮箱
    #     @params strForgetPwdVcode string 验证字串
    #     """
    #
    #     if not strEmail or not strForgetPwdVcode:
    #         return 401
    #
    #     dicData = self.account_model.findOne({
    #         'condition': 'account = "%s"' % strEmail
    #     })
    #     if not dicData:
    #         return 601
    #
    #     # 修改密码地址
    #     strChangePwdUrl = 'http://%s/user?a=change_email&v=%s' % (self.param['host'], change)
    #
    #     # 发送邮件
    #     import api.sendcloud as sendcloud
    #     booStatus = sendcloud.send_template_mail('一道找回密码', **{
    #         'template_invoke_name': '32187_invoke_9',
    #         'substitution_vars': '{"sub": {"{{ current_user.display_name }}": ["onlyfu"], '
    #                              '"{{ current_user.findpassword_url }}": ["%s"]}, '
    #                              '"to": ["%s"]}' % (strChangePwdUrl, strEmail)
    #     })
    #     if not booStatus:
    #         return 500
    #
    #     return 200

    def reset_password(self, strEmail, strPassword, strRePassword):
        """ 重置密码

        @params strEmail string 用户邮箱
        @params strPassword string 密码
        @params strRePassword string 确认密码
        """

        if not strEmail or not strPassword or not strRePassword:
            return 401

        if strPassword != strRePassword:
            return 604

        # 读取帐户信息
        dicUser = self.account_model.find_one({
            'condition': 'account = "%s"' % strEmail
        })
        if not dicUser:
            return 601

        # 新salt
        strSalt = self.salt()
        # 新密码
        strPassword = self.hashlib.sha256('%s -- %s' % (strPassword, strSalt)).hexdigest()
        # 执行修改
        self.account_model.update({
            'fields': ['password = "%s"' % strPassword, 'salt = "%s"' % strSalt],
            'condition': 'account = "%s"' % strEmail
        })
        if self.model.db.status != 200:
            return 601

    def change_password(self, strUserId, strOldPassword, strNewPassword, strReNewPassword):
        """ 修改密码
        
        @params strUserId string 用户ID
        @params strOldPassword string 原密码
        @params strNewPassword string 新密码
        @params strReNewPassword string 新密码的确认密码
        """

        # 读取用户信息
        tupAccount = self.get_account_by_user_id(strUserId)
        if not tupAccount:
            self.status = 601

        if tupAccount[0]['password'] != self.get_password(strOldPassword, tupAccount[0]['salt']):
            self.status = 603

        # 修改密码
        self.set_password(strUserId, strNewPassword)

    def updateAccount(self, str_user_id, str_account_old, str_account):
        """ 更新登录信息
        """

        self.account_model.update({
            'fields': ['account = "%s"' % str_account],
            'condition': 'user_id = %s and account = %s' % (str_user_id, str_account_old)
        })

    def signup(self, str_nickname, str_phone, str_password):
        """ 注册

        @params
            str_account     帐号
            str_password    密码
            str_nickname    昵称
        """

        # 检测帐号
        dic_account = self.get_account(str_phone)
        if dic_account:
            return

        intTime = int(self.time.time())

        # 生成salt
        strSalt = self.salt()
        strPasswordSalt = self.get_password(str_password, strSalt)

        # 生成user信息
        int_user_id = self.user_model.insert({
            'key': 'nickname, phone, create_time',
            'val': '"%s", "%s", %d' % (str_nickname, str_phone, intTime)
        })
        if self.model.db.status != 200:
            self.status = self.model.dicConfig['SERVICE_DB_ERROR']
            return

        # 生成帐号信息
        self.account_model.insert({
            'key': 'user_id, account, password, salt, account_type, create_time',
            'val': '%s, "%s", "%s", "%s", 2, %d' % (int_user_id,
                                                    str_phone,
                                                    strPasswordSalt,
                                                    strSalt,
                                                    intTime)
        })
        self.importService('message').send_message(int_user_id,'reg',{
            'nickname' : str_nickname
        })
        # print "注册成功"
        if self.model.db.status != 200:
            self.status = self.model.dicConfig['SERVICE_DB_ERROR']
            return

        return int_user_id

    def get_password(self, str_password, str_salt):
        return self.hashlib.sha256('%s -- %s' % (str_password, str_salt)).hexdigest()

    def update_account_by_phone(self, strUserId, strPhone):
        dicAccount = self.account_model.findOne({
            'condition': 'account = "%s"' % strPhone
        })
        if dicAccount:
            return 602

        # 更新用户信息
        self.user_model.update({
            'fields': ['phone = "%s"' % strPhone],
            'condition': 'id = "%s"' % strUserId
        })
        if self.model.db.status != 200:
            return 601

        # 更新帐号信息
        # 查询已有帐号
        tupAccount = self.account_model.findMany({
            'condition': 'user_id="%s"' % strUserId
        })
        dicAccount = {str(i['account_type']): i for i in tupAccount}

        # 已绑定手机帐号
        if dicAccount.get('2'):
            self.account_model.update({
                'fields': ['account="%s"' % strPhone],
                'condition': 'user_id="%s" and account_type = 2' % strUserId
            })
        # 未绑定手机帐号
        else:
            # 获取邮箱帐号的信息
            dicAccountEmail = dicAccount.get('1')
            self.account_model.insert({
                'key': 'user_id, account, password, salt, account_type, create_time',
                'val': '%s, "%s", "%s", "%s", 2, %s' % (strUserId,
                                                        strPhone,
                                                        dicAccountEmail['password'],
                                                        dicAccountEmail['salt'],
                                                        int(self.time.time()))
            })
        if self.model.db.status != 200:
            return 601

        return 200

    def update_account_by_email(self, strUserId, strEmail):
        # 更新用户信息
        self.user_model.update({
            'fields': ['email = "%s"' % strEmail],
            'condition': 'id = "%s"' % strUserId
        })
        if self.model.db.status != 200:
            return 601

        # 更新帐号信息
        # 查询已有帐号
        tupAccount = self.account_model.findMany({
            'condition': 'user_id="%s"' % strUserId
        })
        dicAccount = {str(i['account_type']): i for i in tupAccount}

        # 已绑定邮箱帐号
        if dicAccount.get('1'):
            self.account_model.update({
                'fields': ['account="%s"' % strEmail],
                'condition': 'user_id="%s" and account_type = 1' % strUserId
            })
        # 未绑定邮箱帐号
        else:
            # 获取手机帐号的信息
            dicAccountEmail = dicAccount.get('2')
            self.account_model.insert({
                'key': 'user_id, account, password, salt, account_type, create_time',
                'val': '%s, "%s", "%s", "%s", 2, %s' % (strUserId,
                                                        strEmail,
                                                        dicAccountEmail['password'],
                                                        dicAccountEmail['salt'],
                                                        int(self.time.time()))
            })
        if self.model.db.status != 200:
            return 601
        return 200

    def get_wallet(self, user_id):
        data = self.wallet_model.findMany({
            'fields':['money, alipay_account, alipay_name, status'],
            'condition': 'user_id="%s"' % user_id
        })
        return data

    def get_pay_order(self, user_id):
        data = self.pay_model.findMany({
            'fields':['order_id, pay_type, money, create_time'],
            'condition': 'user_id="%s"' % user_id
        })
        return data