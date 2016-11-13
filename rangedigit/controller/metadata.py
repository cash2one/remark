# -*- coding: utf-8 -*-

import base


class category(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'metadata_category'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/metadata/category?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('metadata').get_category(intPage, intPageDataNum, strSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'metadata')

    def create(self):
        name = self.I('name')
        status = self.importService('metadata').create_category(name)
        if status == 200:
            strRedirectUrl = '/metadata/category'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        _id = self.I('id')
        name = self.I('name')
        status = self.importService('metadata').update_category(_id, name)
        if status == 200:
            strRedirectUrl = '/metadata/category'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        _id = self.I('id')
        status = self.importService('metadata').delete_category(_id)
        if status == 200:
            strRedirectUrl = '/metadata/category'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class tag(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'metadata_tag'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/metadata/tag?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('metadata').get_tag(intPage, intPageDataNum, strSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'metadata')

    def create(self):
        name = self.I('name')
        status = self.importService('metadata').create_tag(name)
        if status == 200:
            strRedirectUrl = '/metadata/tag'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        _id = self.I('id')
        name = self.I('name')
        status = self.importService('metadata').update_tag(_id, name)
        if status == 200:
            strRedirectUrl = '/metadata/tag'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        _id = self.I('id')
        status = self.importService('metadata').delete_tag(_id)
        if status == 200:
            strRedirectUrl = '/metadata/tag'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)
