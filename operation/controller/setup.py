# -*- coding:utf-8 -*-

import base


class setup(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        self.display('index', 'setup')

class properties(base.base):
    '''
    :func: 刊例属性管理
    '''

    def initialize(self):
        base.base.initialize(self)

    def index(self):
        strMenu = 'setting_advertising'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/ad?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('admin_su_properties').index(intPage, intPageDataNum, strSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'setup')

    def create(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_su_properties').create(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/setup/properties'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_su_properties').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/setup/properties'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        intId = int(self.I('id'))
        dicResp = self.importService('admin_su_properties').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/setup/properties'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)