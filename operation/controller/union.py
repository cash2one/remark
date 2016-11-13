# -*- coding:utf-8 -*-

import base


class union(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 状态
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '0'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 筛选时间
        strTimeStart = self.I('start')
        strTimeEnd = self.I('end')
        # 分页url
        strPageUrl = '/union?status={status}&start={start}&end={end}'.format(
            status=strStatus, start=strTimeStart, end=strTimeEnd)
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('admin_union').index(
            intPage, intPageDataNum, strStatus, strTimeStart, strTimeEnd, strSearch
        )
        self.dicViewData['status'] = strStatus
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index')

    def detail(self):
        '''
        :func: 查看详细信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_union').detail(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['detail_info'] = dicResp['dicData']
            self.display('detail')
        else:
            self.redirect('/500')

    def allow(self):
        '''
        :func: 通过
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        dicResp = self.importService('admin_union').allow(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/union?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def disallow(self):
        '''
        :func: 不通过
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        dicResp = self.importService('admin_union').disallow(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/union?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def ban(self):
        '''
        :func: 禁用
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        dicResp = self.importService('admin_union').ban(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/union?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def unban(self):
        '''
        :func: 取消禁用
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        dicResp = self.importService('admin_union').unban(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/union?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        '''
        :func: 删除
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        dicResp = self.importService('admin_union').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/union?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)
