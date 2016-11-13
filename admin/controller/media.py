# -*- coding:utf-8 -*-

import base


class media(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media'
        # 页码
        try:
            intPage = int(self.I('page'))
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
        strPageUrl = '/yidao/media?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        admin_media_service = self.importService('admin_media')
        lisIndexInfo, intRows = admin_media_service.index(
            intPage, intPageDataNum, intTimeStart, intTimeEnd, strSearch
        )
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'yidao')

    def detail(self):
        '''
        :func: 查看自媒体详细信息
        '''
        strMenu = 'media'
        intId = int(self.I('id'))
        dicResp = self.importService('admin_media').detail(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['menu'] = strMenu
            self.dicViewData['detail_info'] = dicResp['dicData']
            self.display('detail', 'yidao')
        elif dicResp['statusCode'] == 500:
            self.redirect('/500')
        else:
            self.redirect('/404')

    def ban(self):
        '''
        :func: 禁用自媒体
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_media').ban(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/yidao/media'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def unban(self):
        '''
        :func: 取消禁用自媒体
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_media').unban(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/yidao/media'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def updateName(self):
        '''
        :func: 修改自媒体名称
        '''
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateName(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateAudienceGender(self):
        '''
        :func: 修改自媒体受众性别
        '''
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateAudienceGender(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateOriginal(self):
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateOriginal(intId, args)
            #print dicResp['statusCode']
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateValue(self):
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateValue(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateCategory(self):
        '''
        :func: 修改自媒体分类
        '''
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateCategory(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateTag(self):
        '''
        :func: 修改自媒体标签
        '''
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateTag(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def getCategory(self):
        '''
        :func: 获取分类列表
        '''
        tupData = self.importService('admin_media').getCategory()
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def getTag(self):
        '''
        :func: 获取标签列表
        '''
        intId = int(self.I('id'))
        lisData = self.importService('admin_media').getTag(intId)
        if lisData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', lisData)

    def getArea(self):
        '''
        :func: 获取区域列表
        '''
        strParentId = self.I('parent_id')
        try:
            intParentId = int(strParentId) if strParentId else 0
        except Exception:
            intParentId = -1
        tupData = self.importService('admin_media').getArea(intParentId)
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def updateAudienceArea(self):
        '''
        :func: 修改自媒体受众区域
        '''
        intId = int(self.I('id'))
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_media').updateAudienceArea(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/yidao/media?a=detail&id={id}'.format(id=intId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)