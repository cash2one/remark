# -*- coding:utf-8 -*-

import base
import api.sms as sms


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 需求单
        self.demandModel = self.importModel('demand')
        self.demandOrderModel = self.importModel('demand_order')
        self.demandTakeOrderModel = self.importModel('demand_take_order')
        self.demandFeedbackModel = self.importModel('demand_wechat_feedback')
        self.demandAppealModel = self.importModel('demand_appeal')
        # 需求单状态标签
        self.demandStatus = {0: '需求完成', 1: '审核中', 2: '接单中', 3: '营销中', 4: '结束',
                             5: '审核不通过', 6: '流单', 7: '已撤销'}
        self.orderStatus = {1: '广告主已下单', 2: '广告主取消', 3: '自媒体改价',
                            4: '自媒体取消', 5: '等待反馈', 6: '广告主确认'}
        self.takeOrderStatus = {1: '接单中', 2: '自媒体取消', 3: '广告主取消', 4: '完成接单'}
        self.feedbackStatus = {0: '广告主已验收', 1: '等待确认', 2: '已申诉'}
        self.appealStatus = {0: '申诉结束', 1: '未处理', 2: '处理中'}
        # 媒体平台标签
        self.platformStatus = {0: '不限', 2: '微信公众号'}

    def index(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd, strSearch):
        '''
        :func: 获取需求单首页信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param strStatus: 需求单状态
        :param intTimeStart: 筛选的起始时间
        :param intTimeEnd: 筛选的结束时间
        :param strSearch: 搜索的内容
        '''
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 订单状态条件
        if int(strStatus) == 10:
            statusCondition = ''
        else:
            statusCondition = 'd.status = {status}'.format(status=strStatus)
        # 筛选时间条件
        timeCondition = ''
        if statusCondition:
            if intTimeStart != 0 and intTimeEnd != 0:
                timeCondition = ' and d.create_time > {start} and d.create_time < {end}'.format(
                    start=intTimeStart, end=intTimeEnd
                )
            elif intTimeEnd != 0:
                timeCondition = ' and d.create_time < {end}'.format(end=intTimeEnd)
            elif intTimeStart != 0:
                timeCondition = ' and d.create_time > {start}'.format(start=intTimeStart)
        else:
            if intTimeStart != 0 and intTimeEnd != 0:
                timeCondition = 'd.create_time > {start} and d.create_time < {end}'.format(
                    start=intTimeStart, end=intTimeEnd
                )
            elif intTimeEnd != 0:
                timeCondition = 'd.create_time < {end}'.format(end=intTimeEnd)
            elif intTimeStart != 0:
                timeCondition = 'd.create_time > {start}'.format(start=intTimeStart)
        # 搜索条件
        searchCondition = ''
        # print timeCondition
        # print statusCondition
        if strSearch and (timeCondition or statusCondition):
            searchCondition = ' and d.title like \'%{search}%\''.format(search=strSearch)
        elif strSearch:
            searchCondition = ' d.title like \'%{search}%\''.format(search=strSearch)
        tupData, intRows = self.demandModel.findPaginateAs(
            'demand as d',
            {
                'fields': ['d.*', 'u.nickname', 'df.name as demand_form'],
                'join': 'user as u ON (u.id = d.user_id) LEFT JOIN demand_form as df ON (df.id = d.form)',
                'condition': '{status}{time}{search}'.format(
                    status=statusCondition, time=timeCondition, search=searchCondition
                ),
                'page': [intPage, intPageDataNum],
                'order': 'd.create_time desc'
            }
        )
        # print intRows
        # 需求单进行中细分进度
        dicProcess = {}
        # 需求单进行中
        # if strStatus == '3' or strStatus == '0':
        #     lisDemandId = [str(i['id']) for i in tupData]
        #     strInCondition  = 'demand_id in (' + ','.join(lisDemandId) + ')'
        #     tDemandIds = set([str(i['demand_id']) for i in self.demandTakeOrderModel.findMany(
        #         {'fields':['demand_id'], 'condition': strInCondition})])
        #     oDemandIds = set([str(i['demand_id']) for i in self.demandOrderModel.findMany(
        #         {'fields':['demand_id'], 'condition': strInCondition})])
        #     fDemandIds = set([str(i['demand_id']) for i in self.demandFeedbackModel.findMany(
        #         {'fields':['demand_id'], 'condition': strInCondition})])
        #     aDemandIds = set([str(i['demand_id']) for i in self.demandAppealModel.findMany(
        #         {'fields':['demand_id'], 'condition': strInCondition})])
        #     for strDemandId in lisDemandId:
        #         tmp = {}
        #         tmp['take_order'] = True if strDemandId in tDemandIds else False
        #         tmp['order'] = True if strDemandId in oDemandIds else False
        #         tmp['feedback'] = True if strDemandId in fDemandIds else False
        #         tmp['appeal'] = True if strDemandId in aDemandIds else False
        #         dicProcess[int(strDemandId)] = tmp
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['process'] = dicProcess.get(i['id'], {})
            i['status_tag'] = self.demandStatus.get(i.get('status'), 'unknown')
            i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
            i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        # print intRows
        return lisIndexInfo, intRows

    def wait_order(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd):
        # print "enter"
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 订单状态条件
        Condition = 'd.status = 2'
        # 筛选时间条件
        timeCondition = ''
        if intTimeStart != 0 and intTimeEnd != 0:
            timeCondition = ' and d.create_time > {start} and d.create_time < {end}'.format(
                start=intTimeStart, end=intTimeEnd
            )
        elif intTimeEnd != 0:
            timeCondition = ' and d.create_time < {end}'.format(end=intTimeEnd)
        elif intTimeStart != 0:
            timeCondition = ' and d.create_time > {start}'.format(start=intTimeStart)
        dicProcess = {}
        tupData, intRows = self.demandModel.findPaginateAs(
            'demand as d',
            {
                'fields': ['d.*', 'u.nickname', 'df.name as demand_form'],
                'join': 'user as u ON (u.id = d.user_id) LEFT JOIN demand_form as df ON (df.id = d.form)',
                'condition': '{status}{time}'.format(
                    status=Condition, time=timeCondition
                ),
                'page': [intPage, intPageDataNum],
                'order': 'd.create_time desc'
            }
        )
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['process'] = dicProcess.get(i['id'], {})
            i['status_tag'] = self.demandStatus.get(i.get('status'), 'unknown')
            i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
            i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        # print intRows
        return lisIndexInfo, intRows

    def ended_order(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd):
        # print "enter"
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 订单状态条件
        Condition = '(d.status=0)'
        # 筛选时间条件
        timeCondition = ''
        if intTimeStart != 0 and intTimeEnd != 0:
            timeCondition = ' and d.create_time > {start} and d.create_time < {end})'.format(
                start=intTimeStart, end=intTimeEnd
            )
        elif intTimeEnd != 0:
            timeCondition = ' and d.create_time < {end})'.format(end=intTimeEnd)
        elif intTimeStart != 0:
            timeCondition = ' and d.create_time > {start})'.format(start=intTimeStart)
        dicProcess = {}
        tupData, intRows = self.demandModel.findPaginateAs(
            'demand as d',
            {
                'fields': ['d.*', 'u.nickname', 'df.name as demand_form'],
                'join': 'user as u ON (u.id = d.user_id) LEFT JOIN demand_form as df ON (df.id = d.form)',
                'condition': '{condition}{time}'.format(
                    condition=Condition, time=timeCondition,
                ),
                'page': [intPage, intPageDataNum],
                'order': 'd.create_time desc'
            }
        )
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['process'] = dicProcess.get(i['id'], {})
            i['status_tag'] = self.demandStatus.get(i.get('status'), 'unknown')
            i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
            i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        # print intRows
        return lisIndexInfo, intRows

    def detail(self, intId):
        try:
            dicData = self.demandModel.findOneAs(
                'demand as d',
                {
                    'fields': ['d.*', 'u.nickname', 'df.name as demand_form'],
                    'join': 'user as u ON (u.id = d.user_id) LEFT JOIN demand_form as df ON (d.form = df.id)',
                    'condition': 'd.id = {did}'.format(did=intId),
                    'order': 'd.create_time desc'
                }
            )
            dicData['platform_tag'] = self.platformStatus.get(dicData.get('media_platform_id'), 'unknown')
            dicData['status_tag'] = self.orderStatus.get(dicData.get('status'), 'unknown')
            dicData['time_begin'] = self.formatTime(dicData.get('time_begin'), '%Y-%m-%d')
            dicData['time_end'] = self.formatTime(dicData.get('time_end'), '%Y-%m-%d')
            dicData['create_time'] = self.formatTime(dicData.get('create_time'), '%Y-%m-%d')
            return {'statusCode': 200, 'dicData': dicData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def order(self, intId):
        try:
            tupData = self.demandOrderModel.findManyAs(
                'demand_order as do',
                {
                    'fields': ['do.*', 'u.nickname'],
                    'join': 'user as u ON (u.id = do.user_id)',
                    'condition': 'do.demand_id = {did}'.format(did=intId),
                    'order': 'do.create_time desc'
                }
            )
            lisData = []
            for idx, i in enumerate(tupData):
                i['idx'] = idx + 1
                i['status_tag'] = self.orderStatus.get(i.get('status'), 'unknown')
                i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
                lisData.append(i)
            return {'statusCode': 200, 'lisData': lisData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def takeOrder(self, intId):
        try:
            tupData = self.demandTakeOrderModel.findManyAs(
                'demand_take_order as dto',
                {
                    'fields': ['dto.*', 'u.nickname', 'm.name'],
                    'join': 'user as u ON (u.id = dto.user_id) LEFT JOIN media as m ON (m.id = dto.media_id)',
                    'condition': 'dto.demand_id = {did}'.format(did=intId),
                    'order': 'dto.create_time desc'
                }
            )
            lisData = []
            for idx, i in enumerate(tupData):
                i['idx'] = idx + 1
                i['status_tag'] = self.takeOrderStatus.get(i.get('status'), 'unknown')
                i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
                lisData.append(i)
            return {'statusCode': 200, 'lisData': lisData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def feedback(self, intId):
        try:
            tupData = self.demandFeedbackModel.findManyAs(
                'demand_wechat_feedback as dwf',
                {
                    'fields': ['dwf.*', 'u.nickname', 'm.name'],
                    'join': 'user as u ON (u.id = dwf.user_id) LEFT JOIN media as m ON (m.id = dwf.media_id)',
                    'condition': 'dwf.demand_id = {did}'.format(did=intId),
                    'order': 'dwf.create_time desc'
                }
            )
            lisData = []
            for idx, i in enumerate(tupData):
                i['idx'] = idx + 1
                i['status_tag'] = self.feedbackStatus.get(i.get('status'), 'unknown')
                i['publish_time'] = self.formatTime(i.get('publish_time'), '%Y-%m-%d')
                i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
                i['picture_1'] = '{host}{key}'.format(host=self.dicConfig['PIC']['HOST'], key=i['picture_1'])
                i['picture_2'] = '{host}{key}'.format(host=self.dicConfig['PIC']['HOST'], key=i['picture_2'])
                i['picture_3'] = '{host}{key}'.format(host=self.dicConfig['PIC']['HOST'], key=i['picture_3'])
                lisData.append(i)
            return {'statusCode': 200, 'lisData': lisData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def appeal(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd):

        intDataNumStart = (intPage - 1) * intPageDataNum
        # 订单状态条件

        statusCondition = 'da.status = {status}'.format(status=strStatus)
        # 筛选时间条件
        timeCondition = ''
        if intTimeStart != 0 and intTimeEnd != 0:
            timeCondition = ' and da.create_time > {start} and da.create_time < {end}'.format(
                start=intTimeStart, end=intTimeEnd
            )
        elif intTimeEnd != 0:
            timeCondition = ' and da.create_time < {end}'.format(end=intTimeEnd)
        elif intTimeStart != 0:
            timeCondition = ' and da.create_time > {start}'.format(start=intTimeStart)
        # 搜索条件

        tupData, intRows = self.demandAppealModel.findPaginateAs(
            'demand_appeal as da',
            {
                'fields': ['da.*', 'u.nickname', ],
                'join': 'user as u ON (u.id = da.ad_user_id)',
                'condition': '{status}{time}'.format(
                    status=statusCondition, time=timeCondition
                ),
                'order': 'da.create_time desc'
            }
        )
        # print intRows
        # 需求单进行中细分进度
        dicProcess = {}
        # print 111
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['process'] = dicProcess.get(i['id'], {})
            i['status_tag'] = self.demandStatus.get(i.get('status'), 'unknown')
            i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        # print intRows
        return lisIndexInfo, intRows

    def allow(self, int_demand_id):
        """
        :func: 广告需求单审核通过
        :param int_demand_id: id
        """
        dicData = self.demandModel.findOneAs(
            'demand as d',
            {
                'fields': ['d.*', 'u.nickname'],
                'join': 'user as u ON (u.id = d.user_id)',
                'condition': 'd.id = {did}'.format(did=int_demand_id),
                'order': 'd.create_time desc'
            }
        )
        self.demandModel.update({
            'fields': ['status = 2'],
            'condition': 'id = %d' % int_demand_id
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        # print 111
        # print dicData['nickname'],dicData['title']
        self.importService('message').send_message(dicData['user_id'],'pass',{
            'demand_title': dicData['title'].encode('utf-8'),
            'demand_id': str(int_demand_id).encode('utf-8')
        })
        sms.sendsms(dicData['phone'], 'pass', {
            'nickname': dicData['nickname'].encode('utf-8'),
            'demand_title': dicData['title'].encode('utf-8')
        })
        return {'statusCode': 200}

    def disallow(self, intId, args):
        if 'reason' in args:
            strReason = args['reason'][0]
            self.demandModel.update({
                'fields': ['status = 5'],
                'condition': 'id = %s' % intId
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            self.importModel('demand_check').insert({
                'key': 'demand_id, info, create_time',
                'val': '%s, "%s", %s' % (intId, strReason, int(self.time.time()))
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
        dicData = self.demandModel.findOneAs(
            'demand as d',
            {
                'fields': ['d.*', 'u.nickname', 'dc.info'],
                'join': 'user as u ON (u.id = d.user_id) LEFT JOIN demand_check as dc ON(d.id = dc.demand_id)',
                'condition': 'd.id = {did}'.format(did=intId),
                'order': 'd.create_time desc'
            }
        )
        # print dicData
        sms.sendsms(dicData['phone'], 'denied', {
            'nickname': dicData['nickname'].encode('utf-8'),
            'demand_title': dicData['title'].encode('utf-8'),
            'check_info': dicData['info'].encode('utf-8')
        })
        self.importService('message').send_message(dicData['user_id'],'denied',{
            'demand_title': dicData['title'].encode('utf-8'),
            'check_info': dicData['info'].encode('utf-8'),
            'demand_id': str(intId).encode('utf-8')
        })
        return {'statusCode': 200}

    def updateAppealResult(self, dicArgs):
        """
        :func: 更新申诉结论
        :param dicArgs: 参数
        """

        if ('result' and 'refund_money') in dicArgs:
            # print 222
            strId = dicArgs['id']
            strResult = dicArgs['result'][0]
            strRefund = dicArgs['refund_money'][0]
            self.demandAppealModel.update({
                'fields': ['result = \'{res}\''.format(res=strResult), 'refund_money={ref}'.format(ref=strRefund),
                           'status = 3'],
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    # def al_order(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd):
    #     intDataNumStart = (intPage - 1) * intPageDataNum
    #     # 订单状态条件
    #     if int(strStatus) == 5 :
    #         statusCondition ='(o.status=5 or o.status=6)'
    #     else:
    #         statusCondition = 'o.status = {status}'.format(status=strStatus)
    #     # 筛选时间条件
    #     timeCondition = ''
    #     if intTimeStart != 0 and intTimeEnd != 0:
    #         timeCondition = ' and o.create_time > {start} and o.create_time < {end}'.format(
    #             start=intTimeStart, end=intTimeEnd
    #         )
    #     elif intTimeEnd != 0:
    #         timeCondition = ' and o.create_time < {end}'.format(end=intTimeEnd)
    #     elif intTimeStart != 0:
    #         timeCondition = ' and o.create_time > {start}'.format(start=intTimeStart)
    #     # 搜索条件
    #
    #     tupData, intRows = self.demandOrderModel.findPaginateAs(
    #         'demand_order as o',
    #         {
    #             'fields': ['o.*', 'u.nickname', 'm.name as media_name'],
    #             'join': 'user as u ON (u.id = o.user_id) LEFT JOIN media as m ON (m.id = o.media_id)',
    #             'condition': '{status}{time}'.format(
    #                 status=statusCondition, time=timeCondition
    #             ),
    #             'page': [intPage, intPageDataNum],
    #             'order': 'o.create_time desc'
    #         }
    #     )
    #     #print intRows
    #     # 需求单进行中细分进度
    #     dicProcess = {}
    #
    #     # 数据整合及格式化
    #     lisIndexInfo = []
    #     for idx, i in enumerate(tupData):
    #         i['idx'] = intDataNumStart + idx + 1
    #         i['process'] = dicProcess.get(i['id'], {})
    #         i['status_tag'] = self.demandStatus.get(i.get('status'), 'unknown')
    #         i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
    #         i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
    #         i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
    #         i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
    #         lisIndexInfo.append(i)
    #
    #     return lisIndexInfo, intRows

    def al_order(self, intPage, intPageDataNum, strStatus, intTimeStart, intTimeEnd, strSearch):
        status_name ={1:'等待付款',2:'等待反馈',3:'等待验收',4:'已完成',5:'已取消',6:'已取消',}
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 订单状态条件
        if int(strStatus) == 5:
            statusCondition = '(do.status=5 or do.status=6)'
        elif int(strStatus) == 10:
            # print 111
            statusCondition = ''
        else:
            statusCondition = 'do.status = {status}'.format(status=strStatus)
        # 筛选时间条件
        timeCondition = ''
        if statusCondition:
            if intTimeStart != 0 and intTimeEnd != 0:
                timeCondition = ' and do.create_time > {start} and do.create_time < {end}'.format(
                    start=intTimeStart, end=intTimeEnd
                )
            elif intTimeEnd != 0:
                timeCondition = ' and do.create_time < {end}'.format(end=intTimeEnd)
            elif intTimeStart != 0:
                timeCondition = ' and do.create_time > {start}'.format(start=intTimeStart)
        else:
            if intTimeStart != 0 and intTimeEnd != 0:
                timeCondition = 'do.create_time > {start} and do.create_time < {end}'.format(
                    start=intTimeStart, end=intTimeEnd
                )
            elif intTimeEnd != 0:
                timeCondition = 'do.create_time < {end}'.format(end=intTimeEnd)
            elif intTimeStart != 0:
                timeCondition = ' do.create_time > {start}'.format(start=intTimeStart)
                # 搜索条件
        searchCondition = ''
        if strSearch and (statusCondition or timeCondition):
            if strSearch.isdigit():
                # print 111
                searchCondition = ' and (m.name like \'%{search}%\' or do.demand_id = {doid}) '.format(search=strSearch,
                                                                                                       doid=int(
                                                                                                           strSearch))
                # print searchCondition
            else:
                # print 222
                searchCondition = ' and m.name like \'%{search}%\''.format(search=strSearch)
                # print  searchCondition
        elif strSearch:
            if strSearch.isdigit():
                # print 111
                searchCondition = 'm.name like \'%{search}%\' or do.demand_id = {doid} '.format(search=strSearch,
                                                                                                doid=int(strSearch))
                # print searchCondition
            else:
                # print 222
                searchCondition = 'm.name like \'%{search}%\''.format(search=strSearch)
                # print  searchCondition
        tupData, intRows = self.demandOrderModel.findPaginateAs(
            'demand_order as do',
            {
                'fields': ['do.*', 'u.nickname', 'm.name as media_name','d.title'],
                'join': 'user as u ON (u.id = do.ad_user_id) LEFT JOIN media as m ON (m.id = do.media_id) LEFT JOIN demand as d on(d.id = do.demand_id)',
                'condition': '{status}{time}{search}'.format(
                    status=statusCondition, time=timeCondition, search=searchCondition
                ),
                'page': [intPage, intPageDataNum],
                'order': 'do.create_time desc'
            }
        )
        # print intRows
        # 需求单进行中细分进度
        dicProcess = {}

        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['process'] = dicProcess.get(i['id'], {})
            i['status_tag'] = self.orderStatus.get(i.get('status'), 'unknown')
            i['platform_tag'] = self.platformStatus.get(i.get('media_platform_id'), 'unknown')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
            i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
            index = i['status']
            i['status_name'] = status_name[index]
            lisIndexInfo.append(i)
        # print lisIndexInfo
        # print intRows
        return lisIndexInfo, intRows

    def appeal_detail(self, appeal_id):
        tup_info = self.importModel('demand_appeal').findManyAs('demand_appeal as da', {
            'fields': ['da.*', 'do.demand_id', 'do.price', 'do.media_price_id', 'do.media_id', 'df.url', 'df.title',
                       'df.publish_time', 'df.picture_1 as p1', 'df.picture_2 as p2', 'df.picture_3 as p3',
                       'adu.nickname', 'm.name as media_name', 'd.title as dtitle'],
            'condition': 'da.id = {aid}'.format(aid=appeal_id),
            'join': 'demand_order as do ON(da.order_id = do.id) '
                    'LEFT JOIN demand_wechat_feedback as df ON(df.order_id = da.order_id) '
                    'LEFT JOIN user as adu ON(adu.id = do.ad_user_id) '
                    'LEFT JOIN media as m ON(do.media_id = m.id) '
                    'LEFT JOIN demand as d ON(d.id = do.demand_id) '
        })
        # print 22
        dic_info = tup_info[0]
        dic_info['p1'] = self.getAvatarUrl(dic_info['p1'], 'feedbackx')
        dic_info['p2'] = self.getAvatarUrl(dic_info['p2'], 'feedbackx')
        dic_info['p3'] = self.getAvatarUrl(dic_info['p3'], 'feedbackx')
        dic_info['create_time'] = self.formatTime((dic_info['create_time']), '%Y-%m-%d')
        dic_info['publish_time'] = self.formatTime((dic_info['publish_time']), '%Y-%m-%d')
        return dic_info

    def allowAppeal(self, appeal_id):
        self.demandAppealModel.update({
            'fields': ['status = 2'],
            'condition': 'id = {id}'.format(id=appeal_id)
        })
        dict_appeal = self.demandAppealModel.findOne({
            'fields': ['order_id'],
            'condition': 'id = {id}'.format(id=appeal_id)
        })
        order_id = dict_appeal['order_id']
        #print order_id
        self.demandOrderModel.update({
            'fields': ['status = 4'],
            'condition': 'id = {id}'.format(id=order_id)
        })
        dict_order = self.demandOrderModel.findOneAs('demand_order as do',{
            'fields': ['do.demand_id','do.ad_user_id','do.m_user_id','m.name as media_title'],
            'condition': 'do.id = {id}'.format(id=order_id),
            'join': 'media as m ON(m.id = do.media_id)'
        })
        demand_id = dict_order['demand_id']
        #print demand_id
        tupStatus = self.demandOrderModel.findMany({
            'fields': ['id','status'],
            'condition': 'demand_id = {id} and status != 4'.format(id= demand_id)
        })
        #print status_flag

        if not tupStatus:
            self.demandModel.update({
            'fields': ['status = 4'],
            'condition': 'id = {id}'.format(id=demand_id)
            })
        self.importService('message').send_message(dict_order["ad_user_id"],'appeal_done',{
            'media_title':dict_order['media_title'].encode('utf-8'),
            'order_id': str(order_id).encode('utf-8')
        })
        self.importService('message').send_message(dict_order["m_user_id"],'appeal_done_media',{
            'media_title':dict_order['media_title'].encode('utf-8'),
            'order_id': str(order_id).encode('utf-8')
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def denyAppeal(self, appeal_id):
        self.demandAppealModel.update({
            'fields': ['status = 1'],
            'condition': 'id = {id}'.format(id=appeal_id)
        })
        if self.model.db.status != 200:
            return 601
        return 200
