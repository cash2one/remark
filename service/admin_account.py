# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.accountModel = self.importModel('admin_account')
        self.userModel = self.importModel('admin_user')

    def login(self, dicArgs):
        """
        :func: 登录
        :param dicArgs: 登录参数含帐号、密码
        """
        if 'account' in dicArgs and 'password' in dicArgs:
            dicAccount = self.accountModel.findOne({
                'condition': 'account="%s"' % dicArgs['account'][0]
            })
            if not dicAccount:
                return {'status': 601}
            # 检测密码
            if dicAccount['password'] != \
                    self.hashlib.sha256('%s -- %s' % (dicArgs['password'][0], dicAccount['salt'])).hexdigest():
                return {'status': 603}

            dicUser = self.userModel.findOne({
                'condition': 'id = "%s"' % dicAccount['user_id']
            })
            if dicUser['status'] == 1:
                return {'status': 403}

        else:
            return {'status': 400}
        return {'status': 200, 'user': dicUser}
