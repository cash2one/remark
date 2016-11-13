# -*- coding:utf-8 -*-

import base


class user(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'user'
        # 页码
        try:
            intPage = int(self.I('page', 1))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 字符串时间转换成浮点型时间
        tFunc = lambda s: self.time.mktime(self.time.strptime(s, '%Y-%m-%d'))
        # 筛选时间
        strTimeStart = self.I('start')
        strTimeEnd = self.I('end')
        try:
            intTimeStart = int(tFunc(strTimeStart))
        except ValueError:
            intTimeStart = 0
        try:
            intTimeEnd = int(tFunc(strTimeEnd))
        except ValueError:
            intTimeEnd = 0
        # 分页url
        strPageUrl = '/user?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('user').index(
            intPage, intPageDataNum, intTimeStart, intTimeEnd, strSearch
        )

        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'yidao')

    def detail(self):
        '''
        :func: 查看用户详细信息
        '''
        intId = int(self.I('id'))
        #
        strMenu = 'user'
        if self._POST:
            args = self.request.arguments
            # print args
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            if 'contact_email' in args:
                dicResp = self.importService('user').updateContact(intId, args)
            elif 'status_update' in args:
                dicResp = self.importService('user').updateStatus(intId, args)
            elif 'vip_update' in args:
                dicResp = self.importService('user').updateVip(intId, args)
            else:
                return
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/user?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)
            return
        #
        dicUser = self.importService('user').detail(intId)
        if dicUser:
            self.dicViewData['detail_info'] = dicUser
            self.dicViewData['menu'] = strMenu
            self.display('detail', 'yidao')
        else:
            self.redirect('/500')

    # def media(self):
    #     '''
    #     :func: 查看用户拥有的自媒体
    #     '''
    #     intId = int(self.I('id'))
    #     dicResp = self.importService('admin_user').media(intId)
    #     self.out(**dicResp)
