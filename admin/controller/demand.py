# -*- coding:utf-8 -*-

import base


class demand(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'demand'
        # 订单状态
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '10'
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
        # 分页url
        strPageUrl = '/demand?status={status}&start={start}&end={end}'.format(
            status=strStatus, start=strTimeStart, end=strTimeEnd)
        try:
            intTimeStart = int(tFunc(strTimeStart))
        except ValueError:
            intTimeStart = 0
        try:
            intTimeEnd = int(tFunc(strTimeEnd))
        except ValueError:
            intTimeEnd = 0
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo=[]
        intRows=0


        lisIndexInfo, intRows = self.importService('admin_demand').index(
            intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd, strSearch
        )
        # elif(int(strStatus)==13):
        #     lisIndexInfo, intRows = self.importService('admin_demand').wait_order(
        #         intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd
        #     )
        # elif(int(strStatus)==14):
        #     lisIndexInfo, intRows = self.importService('admin_demand').ended_order(
        #         intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd
        #     )
        self.dicViewData['menu'] = strMenu
        self.dicViewData['status'] = strStatus
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index')

    def detail(self):
        '''
        :func: 查看订单详细信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_demand').detail(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['detail_info'] = dicResp['dicData']
            self.display('detail')
        else:
            self.redirect('/500')

    def order(self):
        '''
        :func: 广告主下单信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_demand').order(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['order_info'] = dicResp['lisData']
            self.display('detail_order')
        else:
            self.redirect('/500')

    def takeOrder(self):
        '''
        :func: 自媒体接单信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_demand').takeOrder(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['take_order_info'] = dicResp['lisData']
            self.display('detail_take_order')
        else:
            self.redirect('/500')

    def feedback(self):
        '''
        :func: 反馈信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_demand').feedback(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['feedback_info'] = dicResp['lisData']
            self.display('detail_feedback')
        else:
            self.redirect('/500')

    def appeal(self):
        '''
        :func: 申诉信息
        '''
        
        intId = int(self.I('id'))
        dicResp = self.importService('admin_demand').appeal(intId)
        # print dicResp
        if dicResp['statusCode'] == 200:
            self.dicViewData['appeal_info'] = dicResp['lisData']
            self.display('detail_appeal')
        else:
            self.redirect('/500')

    def cancel(self):
        '''
        :func: 广告需求单撤销
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '0'
        dicResp = self.importService('admin_demand').cancel(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/demand?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def allow(self):
        '''
        :func: 广告需求单审核通过
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '0'
        dicResp = self.importService('admin_demand').allow(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/demand?status={status}'.format(status=strStatus)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def disallow(self):
        '''
        :func: 不通过订单
        '''
        intId = int(self.I('id'))
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '0'
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_demand').disallow(intId, args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/demand?status={status}'.format(status=strStatus)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def updateAppealResult(self):
        """
        :func: 变更申诉结论
        """
        intId = int(self.I('id'))
        intDemandId = int(self.I('demand_id'))
        if self._POST:
            args = self.request.arguments
            args['id'] = [intId]
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_demand').updateAppealResult(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/demand?a=appeal&id={aid}'.format(aid=intDemandId)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

class order(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'demand_order'
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '10'
        
        try:
            intPage = int(self.I('page'))  # 页码
        except ValueError:
            intPage = 1
            
        # 单页数据条数
        intPageDataNum = 20
        # 字符串时间转换成浮点型时间
        tFunc = lambda s: self.time.mktime(self.time.strptime(s, '%Y-%m-%d'))
        # 筛选时间
        strTimeStart = self.I('start')
        strTimeEnd = self.I('end')
        # 搜索内容
        strSearch = self.I('search')
        # 分页url
        strPageUrl = '/demand/order?status={status}&start={start}&end={end}'.format(
            status=strStatus, start=strTimeStart, end=strTimeEnd)
        try:
            intTimeStart = int(tFunc(strTimeStart))
        except ValueError:
            intTimeStart = 0
        try:
            intTimeEnd = int(tFunc(strTimeEnd))
        except ValueError:
            intTimeEnd = 0

        # 获取首页数据和数目
        lisIndexInfo=[]
        intRows=0

        lisIndexInfo, intRows = self.importService('admin_demand').al_order(
            intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd,strSearch
        )
        self.dicViewData['menu'] = strMenu
        self.dicViewData['status'] = strStatus
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'demand')
        
class appeal(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
    
        
    def index(self):
        strMenu = 'demand_appeal'
        strStatus = self.I('status')
        if not strStatus:
            strStatus = '1'
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
        # 分页url
        strPageUrl = '/demand?status={status}&start={start}&end={end}'.format(
            status=strStatus, start=strTimeStart, end=strTimeEnd)
        try:
            intTimeStart = int(tFunc(strTimeStart))
        except ValueError:
            intTimeStart = 0
        try:
            intTimeEnd = int(tFunc(strTimeEnd))
        except ValueError:
            intTimeEnd = 0

        # 获取首页数据和数目
        lisIndexInfo=[]
        intRows=0

        lisIndexInfo, intRows = self.importService('admin_demand').appeal(
            intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd
        )

        self.dicViewData['menu'] = strMenu
        self.dicViewData['status'] = strStatus
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'demand')

    def detail(self):
        demand_id = self.I('id')
        appeal_info = self.importService('admin_demand').appeal_detail(demand_id)
        #print appeal_info
        self.dicViewData['info'] = appeal_info
        self.display('detail_appeal','demand')

    def updateAppealResult(self):
        #print 1111
        demand_id = self.I('id')
        if self._POST:
            args = self.request.arguments
            args['id'] = demand_id
            #print args
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_demand').updateAppealResult(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/demand/appeal?a=detail&id={aid}'.format(aid=demand_id)
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def allow(self):
        appeal_id = self.I('id')
        statuscode = self.importService('admin_demand').allowAppeal(appeal_id)
        if statuscode== 200:
            strRedirectUrl = '/demand/appeal?a=detail&id={aid}'.format(aid=appeal_id)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def denied(self):
        appeal_id = self.I('id')
        statuscode = self.importService('admin_demand').denyAppeal(appeal_id)
        if statuscode== 200:
            strRedirectUrl = '/demand/appeal?a=detail&id={aid}'.format(aid=appeal_id)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)