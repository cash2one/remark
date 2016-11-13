# -*- coding:utf8 -*-

import base as base
import api.sms as sms


# 需求Service
class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        self.demandFormModel = self.importModel('demand_form')
        self.demandModel = self.importModel('demand')
        self.extraModel = self.importModel('demand_extra')
        self.demandTakeOrderModel = self.importModel('demand_take_order')
        self.demandOrderModel = self.importModel('demand_order')
        self.demandCartModel = self.importModel('demand_cart')
        self.demandCategoryMediaModel = self.importModel('demand_category_media')
        self.demandMediaTagModel = self.importModel('demand_media_tag')
        self.mediaModel = self.importModel('media')
        self.media_service = self.importService('media')
        self.area_service = self.importService('area')
        self.user_service = self.importService('user')

    def demandNew(self):
        """ 最新的需求

        @return tuple(list, dict) 最新需求tuple, 第一组为list，最新的需求，
            第二组为dict，各需求接单数
        """

        demandModel = self.importModel('demand')
        tupDemand = demandModel.find_many({
            'condition': 'status in (1) and time_end >= %s' % self.time.time(),
            'limit': ['0', '8'],
            'order': 'create_time desc'
        })
        lisDemand = []
        lisDemandId = []
        dicDemandJiedan = {}
        lisDemandFormId = []
        dicDemandForm = {}
        dicDemandJiedanOfficial = {}
        if tupDemand:
            for item in tupDemand:
                lisDemandId.append(str(item['id']))
                lisDemandFormId.append('2')
                # 格式化时间
                item['time_begin'] = self.formatTime(item['time_begin'], '%Y-%m-%d')
                item['time_end'] = self.formatTime(item['time_end'], '%Y-%m-%d')

                # 处理钱的小数点
                item['money'] = int(item['money'])

                # 处理已接单自媒体
                # dicDemandJiedanOfficial = self.demandJiedan(item['id'])
                item['official'] = dicDemandJiedanOfficial
                item['demand_form'] = 2

                # 压入列表
                lisDemand.append(item)

            # 处理类型
            dicDemandForm = self.demand_form(','.join(lisDemandFormId))

        return lisDemand, dicDemandJiedan, dicDemandForm

    def demandTakeOrderCount(self, lisDemandId):
        """ 需求接单统计

        @params lisDemandId list 需求ID
        @return dict 接单统计数，以需求ID为KEY，统计数为值的dict
        """

        if not lisDemandId or not isinstance(lisDemandId, list):
            return None

        dicDemandTakeOrderCount = {}
        for item in lisDemandId:
            dicData = self.demandTakeOrderModel.findOne({
                'fields': ['count(id) as count', 'demand_id'],
                'condition': 'demand_id = "%s"' % item
            })

            if dicData['demand_id'] not in dicDemandTakeOrderCount.keys():
                dicDemandTakeOrderCount[dicData['demand_id']] = dicData['count']

        return dicDemandTakeOrderCount

    def demandCount(self):
        """ 需求数统计
        """

        # 读取数据
        # 发布成功的条数
        dicDemandCountPush = self.demandCountPush({
            'fields': ['count(*) as count'],
            'condition': ''
        })

        # 完成的条数
        dicDemandCountComplate = self.demandCountComplate({
            'fields': ['count(*) as count'],
            'condition': 'status = 3'
        })

        return dicDemandCountPush['count'], dicDemandCountComplate['count']

    def demandCountPush(self, dicData):
        """ 发布成功的条数
        """
        demandModel = self.importModel('demand')
        dicDemandCountPush = demandModel.find_one(dicData)

        return dicDemandCountPush

    def demandCountComplate(self, dicData):
        """ 完成的条数
        """
        demandModel = self.importModel('demand')
        dicDemandCountComplate = demandModel.find_one(dicData)

        return dicDemandCountComplate

    def demandList(self, dicData):
        """ 需求列表

        @params dicData dict 数据
            dicData['page']         分页页码
            dicData['demand_form']  需求形式
            dicData['category']     分类ID
            dicData['tag']          Tag ID
            dicData['status']       状态
            dicData['money']        价格区间
            dicData['time_begin']   开始时间
            dicData['time_end']     结束时间
        """

        listCondition = []
        listJoin = []

        # 需求形式
        if dicData['demand_form']:
            listCondition.append('d.form in (%s)' % dicData['demand_form'])

        # 分类
        if dicData['category']:
            listCondition.append('dcm.cate_media_id in (%s)' % dicData['category'])
            listJoin.append('demand_category_media as dcm ON (d.id = dcm.demand_id)')

        # Tag
        if dicData['tag']:
            listCondition.append('dmt.tag_id in (%s)' % dicData['tag'])
            listJoin.append('demand_media_tag dmt on (d.id = dmt.demand_id)')

        # 状态
        if dicData['status']:
            listCondition.append('d.status in (%s)' % (dicData['status']))
        else:
            listCondition.append('d.status in (2, 3, 4)')

        # 开始时间
        if dicData['time_begin']:
            listCondition.append('time_end >= %d' % self.timetostr(dicData['time_begin'] + ' 00:00:00'))

        # 结束时间
        if dicData['time_end']:
            listCondition.append('time_begin <= %d' % self.timetostr(dicData['time_end'] + ' 23:59:59'))

        # 预算
        if dicData['money']:
            list_money = dicData['money'].split(',')
            listCondition.append('money >= %s and money <= %s' % (list_money[0], list_money[1]))

        # 查询
        tupData = self.demandModel.findPaginateAs('demand as d', {
            'condition': ' and '.join(listCondition),
            'join': ' join '.join(listJoin),
            'page': [dicData['page'], 10],
            'order': 'd.create_time desc'
        })

        # 数据格式化
        if tupData:
            for k, item in enumerate(tupData[0]):
                item['category'] = self.demandCategory(str(item['id']))
                item['tag'] = self.demandTag(str(item['id']))
                # 营销形式
                form_name = self.demandFormModel.findOne({
                    'condition': 'id = "%s"' % item['form']
                })

                item['form_name'] = ""
                if form_name:
                    item['form_name'] = form_name['name']
                # 日期的处理
                item['time_begin'] = self.formatTime(item['time_begin'], '%Y-%m-%d')
                item['time_end'] = self.formatTime(item['time_end'], '%Y-%m-%d')
                item['money'] = int(item['money'])
        return {'list': tupData[0],
                'count': tupData[1],
                'category': self.importService('category_media').commonUse(),
                'tag': self.importService('tag').get_list(),
                'status': self.get_status_valid(),
                'demand_form': self.demand_form()}

    def detail(self, str_demand_id):
        """ 详情

        @params strDemandId string 营销需求Id
        """

        demandModel = self.importModel('demand')
        tupData = demandModel.findManyAs('demand as d', {
            'condition': 'd.id = %s' % str_demand_id,
            'join': 'demand_extra as de ON(d.id = de.demand_id)'
        })

        self.demand_view_count(str_demand_id)

        if tupData:
            area_service = self.importService('area')
            media_service = self.importService('media')
            check_Model = self.importModel('demand_check')
            for k, item in enumerate(tupData):
                # 时间
                item['time_begin'] = self.formatTime(item['time_begin'], '%Y-%m-%d')
                item['time_end'] = self.formatTime(item['time_end'], '%Y-%m-%d')
                item['cart_count'] = self.cart_count(item['id'])
                item['money'] = int(item['money'])

                # if item['artical_body']:
                #    item['artical_body'] = self.escapeString(item['artical_body'].encode('utf8'), True)

                # 类目
                item['category'] = self.demandCategory(str_demand_id)

                # Tag
                item['tag'] = self.demandTag(str_demand_id)

                # 处理类型
                item['demand_form_info'] = self.demand_form(item['form'])

                # 原文链接
                if item['origin_link']:
                    item['origin_link'] = 'http://' + item['origin_link'] if 'http://' not in item[
                        'origin_link'] else item['origin_link']
                # 如果状态为5读取未通过审核原因
                if item['status'] == 5:
                    dicCheckInfo = check_Model.findOne({
                        'condition': 'demand_id = "%s"' % str_demand_id
                    })
                    # print dicCheckInfo
                    if dicCheckInfo:
                        item['check_info'] = dicCheckInfo['info']
                        # print item
                # 如果状态为-1，读取禁止理由
                if item['status'] == -1:
                    demandModel = self.importModel('demand')
                    dicReason = demandModel.get_reason(str_demand_id)
                    if dicReason:
                        item['reason'] = dicReason['reason']

                item['area'] = area_service.get_area(item['audience_province_id'], item['audience_city_id'],
                                                     item['audience_county_id'])
                item['audience_gender'] = media_service.get_audience_gender(item['audience_gender'])
            return tupData[0]
        return ()

    def has_demand(self, str_user_id, str_demand_id):
        """ 详情

        @params strDemandId string 营销需求Id
        """
        demandModel = self.importModel('demand')
        tupData = demandModel.findOne({
            'condition': 'id = %s and user_id = %s' % (str_demand_id, str_user_id)
        })

        return tupData

    def custom_media(self, demandId, userId):
        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findManyAs('demand_take_order as dt', {
            'fields': ['dt.demand_id', 'm.user_id', 'm.id as media_id',
                       'dt.media_id', 'm.avatar as avatar', 'm.name', 'm.identify',
                       'm.audience_gender', 'm.value_level',
                       'm.audience_province_id', 'm.audience_city_id', 'm.audience_county_id',
                       'mw.original', 'mw.qrcode'],
            'join': 'media as m ON (dt.media_id = m.id) join media_wechat mw on (m.id = mw.media_id)',
            'condition': 'dt.demand_id = "%s" and m.user_id = "%s" and dt.status = 1' % (demandId, userId)
        })
        if tupData:
            media_service = self.importService('media')
            area_service = self.importService('area')
            for k, item in enumerate(tupData):
                item['value_level'] = media_service.get_value_level(item['value_level'])
                item['avatar'] = self.getAvatarUrl(item['avatar'], 'avatarx')
                item['qrcode'] = media_service.get_qrcode(item['qrcode'])
                item['category'] = media_service.media_category(item['media_id'])
                if not item['category']:
                    item['category'] = {'name': '不限'}
                    # 2015、10、27 能测下么？
                    # item['category']['name'] =  '未设行业'
                item['tag'] = media_service.get_tag(item['media_id'])
                item['audience_gender'] = media_service.get_audience_gender(item['audience_gender'])
                item['area'] = area_service.get_area(item['audience_province_id'], item['audience_city_id'],
                                                     item['audience_county_id'])
                item['cart_status'] = 0
                dicCart = self.demandCartModel.findOne({
                    'condition': 'demand_id = "%s" and media_id = %s' % (demandId, item['media_id'])
                })
                # item['price'] =int(item['price'])
                if dicCart:
                    dicPrice = self.media_service.media_attr_value_info(dicCart['media_price_id'])[0]
                    item['attr_value_info'] = ' + '.join(dicPrice['attr_value_info'].values())
                    item['cart_id'] = dicCart['id']
                    item['cart_status'] = dicCart['status']
                    item['price'] = int(dicPrice['price'])
        return tupData
    def overdue_msg(self,demand_id_lis):
        demandModel = self.importModel('demand')
        if not demand_id_lis:
            return 401
        for did in demand_id_lis:
            dicDemand = demandModel.findOne({
                'condition': 'id = "%s" and user_id = "%s"' % (did, strUserId)
            })

            if not dicDemand:
                return 601

            try:
                demandTakeOrderModel = self.importModel('demand_take_order')
                tup_take_order = demandTakeOrderModel.findMany({
                    'condition': 'demand_id = "%s"' % dicDemand['id']
                })
                if tup_take_order :
                    for item in tup_take_order :
                        self.importService('message').send_message(item['user_id'],'demand_expire_media',{
                            'demand_id': str(dicDemand['id']).encode('utf-8'),
                            'demand_title':dicDemand['title']
                        })
                return 200
            except Exception, e:
                print e
                # self.model.db.rollback()
                return 500

    def demand_view_count(self, str_demand_id):
        """ 需求流量数
        """

        self.demandModel.update({
            'fields': ['view_count = view_count + 1'],
            'condition': 'id = %s' % str_demand_id
        })

    def demand_form(self, demandFormId=None):
        """ 根据ID获取类型名称

        @params demandFormId string 需求ID，多个用,号分割
        """

        str_demand_form_id = ""
        if isinstance(demandFormId, list):
            str_demand_form_id = ','.join(demandFormId)
        elif demandFormId is not None:
            str_demand_form_id = demandFormId

        demand_form_model = self.importModel('demand_form')

        if str_demand_form_id != "":
            tupDemandForm = demand_form_model.findMany({
                'condition': 'id in (%s)' % str_demand_form_id
            })

            dicDemandForm = {}
            if tupDemandForm:
                for item in tupDemandForm:
                    dicDemandForm[item['id']] = item
            return dicDemandForm
        else:
            tupDemandForm = demand_form_model.findMany({
                'sort': 'sort desc'
            })
            return tupDemandForm

    def demandCreate(self, dicParams):
        """ 创建需求

        @params dicParams dict 需求数据
        """

        # 转义
        dicParams = self.escapeString(dicParams)

        if dicParams['audience_city_id'] == "":
            dicParams['audience_city_id'] = 0
        if dicParams['audience_county_id'] == "":
            dicParams['audience_county_id'] = 0

        # 替换回车为换行
        dicParams['marketing'] = dicParams['marketing'].replace('\n', '<br/>')

        # 转化时间
        dicParams['time_begin'] = self.timetostr(dicParams['time_begin'] + " 00:00:00")
        dicParams['time_end'] = self.timetostr(dicParams['time_end'] + " 23:59:59")

        # 生成时间
        dicParams['create_time'] = int(self.time.time())

        # 营销数据
        dic_demand = {
            'key': 'user_id, title, form, time_begin, time_end, marketing, money, phone, '
                   'media_platform_id, audience_province_id, audience_city_id, audience_county_id, create_time',
            'val': '"%s", "%s", "%s", "%s", "%s", "%s", \
                    %s, "%s", "%s", %s, %s, %s, "%s"' %
                   (dicParams['user_id'], dicParams['title'], dicParams['form'], dicParams['time_begin'],
                    dicParams['time_end'], dicParams['marketing'],
                    dicParams['money'], dicParams['phone'], dicParams['media_platform_id'],
                    dicParams['audience_province_id'],
                    dicParams['audience_city_id'], dicParams['audience_county_id'], dicParams['create_time'])
        }
        intDemandId = self.demandModel.insert(dic_demand)
        if self.model.db.status != 200:
            self.status = 601
            return 0

        # 分类数据
        self.demandCategoryMediaModel.insert(intDemandId, dicParams['category'])
        if self.model.db.status != 200:
            self.status = 601
            return 0

        # 标签数据
        self.demandMediaTagModel.insert(intDemandId, dicParams['tag'])
        if self.model.db.status != 200:
            self.status = 601
            return 0

        # 额外数据
        self.extraModel.insert(intDemandId, dicParams)
        if self.model.db.status != 200:
            self.status = 601
            return 0

        # # 内容数据
        # demandArticalModel = self.importModel('demand_artical')
        # demandArticalModel.insert(intDemandId, dicParams)
        return intDemandId

    def myDemand(self, dicData):
        """ 我的需求

        @params dicData dict 数据
            dicData['user_id'] 用户ID
            dicData['page'] 页码
        """

        # strPageCount = 20
        # strStartLimit = dicData['page'] * strPageCount if 'page' in dicData.keys() and dicData['page'] > 1 else 0

        lisCondition = []
        # 发布需求的用户id 筛选
        if dicData.get('user_id'):
            lisCondition.append('user_id = "%s"' % dicData['user_id'])
        # demand id 筛选
        if dicData.get('demand_id'):
            lisCondition.append('id in (%s)' % ', '.join(dicData['demand_id']))
        # 接单需求 状态标识 -1
        if dicData['status'] == -1:
            lisCondition.append('status in (2, 3, 4)')
        # 全部需求
        elif dicData['status'] == 0:
            lisCondition.append('status in (1, 2, 3, 4, 5, 6, 7)')
        else:
            lisCondition.append('status = %s' % dicData['status'])

        strCondition = ' and '.join(lisCondition)

        demandModel = self.importModel('demand')
        tupData = demandModel.findPaginate({
            'fields': ['*', 'id as demand_id', 'form as demand_form'],
            'condition': strCondition,
            'page': [dicData['page'], 10],
            'order': 'id desc'
        })
        if tupData:
            lisDemandId = []
            lisDemandFormId = []
            for k, item in enumerate(tupData[0]):
                lisDemandId.append(str(item['demand_id']))
                lisDemandFormId.append(str(item['demand_form']))
                # 日期的处理
                item['time_begin'] = self.formatTime(item['time_begin'], '%Y-%m-%d')
                item['time_end'] = self.formatTime(item['time_end'], '%Y-%m-%d')

                item['cart_count'] = self.cart_count(item['demand_id'])

            # 处理类别
            dicDemandForm = self.demand_form(lisDemandFormId)

            for k, item in enumerate(tupData[0]):
                item['demand_form'] = dicDemandForm[item['demand_form']]['name'] \
                    if item['demand_form'] in dicDemandForm.keys() else ''
                item['category'] = self.demandCategory(lisDemandId)

        return tupData

    def demand(self, dicData):
        # print dicData
        lisCondition = []
        # 发布需求的用户id 筛选
        if dicData.get('user_id'):
            lisCondition.append('user_id = "%s"' % dicData['user_id'])
        # demand id 筛选
        if dicData.get('demand_id'):
            lisCondition.append('id in (%s)' % ', '.join(dicData['demand_id']))
        # 接单需求 状态标识 -1
        if dicData['status'] == -1:
            lisCondition.append('status in (2, 3, 4)')
        # 全部需求
        elif dicData['status'] == 0:
            lisCondition.append('status in (1, 2, 3, 4, 5)')
        else:
            lisCondition.append('status = %s' % dicData['status'])

        strCondition = ' and '.join(lisCondition)

        demandModel = self.importModel('demand')
        tupData = demandModel.findMany({
            'fields': ['*', 'id as demand_id', 'form as demand_form'],
            'condition': strCondition,
        })
        if tupData:
            lisDemandId = []
            lisDemandFormId = []
            for k, item in enumerate(tupData):
                lisDemandId.append(str(item['demand_id']))
                lisDemandFormId.append(str(item['demand_form']))
                # 日期的处理
                tupData[k]['time_begin'] = self.formatTime(item['time_begin'], '%Y/%m/%d')
                tupData[k]['time_end'] = self.formatTime(item['time_end'], '%Y/%m/%d')

            # 处理类别
            dicDemandForm = self.demand_form(lisDemandFormId)

            for k, item in enumerate(tupData):
                tupData[k]['demand_form'] = dicDemandForm[item['demand_form']]['name'] \
                    if item['demand_form'] in dicDemandForm.keys() else ''
                tupData[k]['category'] = self.demandCategory(lisDemandId)

        return tupData

    def demand_order(self, dicArgs):
        # strPageCount = 20
        # strStartLimit = dicArgs['page'] * strPageCount if 'page' in dicArgs and dicArgs['page'] > 1 else 0
        lisCondition = []
        # 用户id 筛选
        if dicArgs.get('user_id'):
            # 必须用括号限制条件
            lisCondition.append('(ad_user_id = %s or m_user_id = %s)' % (dicArgs['user_id'], dicArgs['user_id']))
        # 全部状态
        if dicArgs['status'] == 0:
            pass
        else:
            lisCondition.append('status = %s' % dicArgs['status'])
        strCondition = ' and '.join(lisCondition)
        # print strCondition
        tupData, rows = self.importModel('demand_order').findPaginate({
            'condition': strCondition,
            'page': [dicArgs['page'], 10],
            'order': 'id desc'
        })
        lisData = []
        for i in tupData:
            i['create_time'] = self.formatTime(i['create_time'], '%Y.%m.%d')
            # i['appeal'] = self.order_appeal_detail(i['id'])
            lisData.append(i)
        return lisData, rows

    def demand_order_detail(self, strDemandOrderId):
        dicData = self.importModel('demand_order').findOneAs(
            'demand_order as do',
            {
                'fields': ['do.*', 'u.nickname as ad_username', 'u1.nickname as media_username',
                           'dt.phone as media_phone'],
                'join': 'user as u ON (u.id = do.ad_user_id) '
                        'LEFT JOIN user as u1 ON (u1.id = do.m_user_id) '
                        'LEFT JOIN demand_take_order as dt ON (dt.demand_id = do.demand_id and dt.media_id = do.media_id)',
                'condition': 'do.id = %s' % strDemandOrderId
            }
        )
        if dicData:
            dicData['create_time'] = self.formatTime(dicData['create_time'], '%Y.%m.%d')
        return dicData

    def cancel_order(self, str_user_type, str_user_id, str_order_id):
        list_condition = ['id = %s' % str_order_id, 'status = 1']

        # 广告主
        if str_user_type == '5':
            list_condition.append('ad_user_id = %s' % str_user_id)
        elif str_user_type == '6':
            list_condition.append('m_user_id = %s' % str_user_id)
        else:
            return 401
        return self.importModel('demand_order').update({
            'fields': ['status = %s' % str_user_type if str_user_type else '1'],
            'condition': ' and '.join(list_condition)
        })

    def order_appeal(self, str_user_id, str_order_id, str_description):
        demand_appeal_model = self.importModel('demand_appeal')
        demand_appeal_model.insert({
            'key': 'ad_user_id, order_id, description, status, create_time',
            'val': '"%s", "%s", "%s", "1", "%s"' % (str_user_id, str_order_id,
                                                    str_description, int(self.time.time()))
        })
        dicSms = self.importModel('demand_order').findOneAs('demand_order as do',{
            'fields':['m.name','do.m_user_id'],
            'join':'media as m ON(do.media_id = m.id)',
            'condition' : 'do.id = {oid}'.format(oid = str_order_id)
        })
        #print dicSms
        if dicSms:
            self.importService('message').send_message(dicSms['m_user_id'],'complain',{
                'order_id': str(str_order_id).encode('utf-8'),
                'media_title':dicSms['name']
            })
        if self.model.db.status != 200:
            self.status = 601

    def order_appeal_detail(self, str_order_id):
        dicData = self.importModel('demand_appeal').findOne({
            'condition': 'order_id = %s' % str_order_id
        }
        )
        return dicData

    def order_feedback(self, str_user_id, str_order_id, str_description):
        dicData = self.importModel('demand_appeal').insert({
            'key': 'ad_user_id, order_id, description, status, create_time',
            'val': '"%s", "%s", "%s", "1", "%s"' % (
                str_user_id, str_order_id, str_description, int(self.time.time()))
        })

        return dicData


    def demand_feedback_detail(self, str_order_id):
        dicData = self.importModel('demand_wechat_feedback').findOneAs(
            'demand_wechat_feedback as dwf',
            {
                'fields': ['dwf.*', 'u.nickname', 'm.name as media_name', 'd.title as demand_title'],
                'join': 'user as u ON (u.id = dwf.user_id) '
                        'LEFT JOIN media as m ON (m.id = dwf.media_id) '
                        'LEFT JOIN demand as d ON (d.id = dwf.demand_id)',
                'condition': 'dwf.order_id = %s' % str_order_id
            }
        )
        if dicData:
            link = dicData['url']
            dicData['publish_time'] = self.formatTime(dicData['publish_time'], '%Y.%m.%d')
            try:
                dicData['idx'] = link[link.index('&idx=') + len('&idx='): link.index('&sn')]
            except IndexError:
                dicData['idx'] = ''
            dicData['picturex_1'] = self.getAvatarUrl(dicData['picture_1'], 'feedbackx') if dicData['picture_1'] else ''
            dicData['picturex_2'] = self.getAvatarUrl(dicData['picture_2'], 'feedbackx') if dicData['picture_2'] else ''
            dicData['picturex_3'] = self.getAvatarUrl(dicData['picture_3'], 'feedbackx') if dicData['picture_3'] else ''
            dicData['picture_1'] = self.getAvatarUrl(dicData['picture_1'], 'feedback') if dicData['picture_1'] else ''
            dicData['picture_2'] = self.getAvatarUrl(dicData['picture_2'], 'feedback') if dicData['picture_2'] else ''
            dicData['picture_3'] = self.getAvatarUrl(dicData['picture_3'], 'feedback') if dicData['picture_3'] else ''
        return dicData

    def demandCategory(self, demandId):
        """ 根据需求ID获取对应分类信息

        @params demandId list/str 广告需求ID，多个用,号分割
        """

        strDemandId = ""
        if isinstance(demandId, list):
            strDemandId = ','.join(demandId)
        elif isinstance(demandId, str)  :
            strDemandId = demandId
        # print strDemandId
        demandModel = self.importModel('demand')
        tupData = demandModel.findManyAs('demand_category_media as dcm', {
            'fields': ['cm.id as cate_id', 'cm.name as name'],
            'condition': 'dcm.demand_id in (%s)' % strDemandId,
            'join': 'category_media as cm ON (dcm.cate_media_id = cm.id)',
        })

        return list(tupData)

    def demandTag(self, demandId):
        """ 处理Tag

        @params strDemandId string 广告需求ID，多个用,号分割
        """

        # strDemandId = ""
        # if isinstance(demandId, list):
        #    strDemandId = ','.join(demandId)
        # elif isinstance(demandId, str):
        #    strDemandId = demandId

        demandModel = self.importModel('demand')
        tupTag = demandModel.findManyAs('demand_media_tag as dmt', {
            'fields': ['t.id as tag_id', 't.name as name'],
            'condition': 'dmt.demand_id="%s"' % demandId,
            'join': 'tag as t ON (dmt.tag_id = t.id)'
        })

        return tupTag

    @staticmethod
    def demand_category_key(tupData):
        """ 将需求分类转为以需求ID为KEY的字典

        @params tupData tuple 需求分类元组
        """

        dicCategory = {}
        if tupData:
            for item in tupData:
                if item['demand_id'] not in dicCategory.keys():
                    dicCategory[item['demand_id']] = []

                dicCategory[item['demand_id']].append(item)

        return dicCategory

    def demand_take_order_demand_id(self, str_demand_id, str_status='0'):
        lisCondition = ['demand_id = %s' % str_demand_id]
        if str_status == '0':
            lisCondition.append('status in (1, 2, 3, 4)')
        else:
            lisCondition.append('status = %s' % str_status)

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findMany({
            'condition': ' and '.join(lisCondition)
        })
        return tupData

    def demand_take_order_user_id(self, str_user_id, str_status='0'):
        lisCondition = ['user_id = %s' % str_user_id]
        if str_status == '0':
            lisCondition.append('status in (1, 2, 3, 4)')
        else:
            lisCondition.append('status = %s' % str_status)

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findMany({
            'condition': ' and '.join(lisCondition)
        })
        return tupData

    def get_take_order(self, str_user_id, str_demand_id, str_media_id):
        lis_condition = ['user_id = %s' % str_user_id,
                         'demand_id = %s' % str_demand_id,
                         'media_id = %s' % str_media_id]

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findMany({
            'condition': ' and '.join(lis_condition)
        })
        return tupData

    def get_take_order_1(self, str_demand_id, str_media_id):
        lis_condition = ['demand_id = %s' % str_demand_id, 'media_id = %s' % str_media_id]

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findMany({
            'condition': ' and '.join(lis_condition)
        })
        return tupData

    def demand_take_order(self, demand_id, limit=None):
        """ 接单列表

        @params demandId string/list 需求ID
        """
        if isinstance(demand_id, list):
            str_demand_id = ','.join(demand_id)
        else:
            str_demand_id = demand_id

        # 总接单数
        dicTakeOrder = {
            'fields': ['dto.demand_id as demand_id', 'dto.phone as phone',
                       'm.id as media_id', 'm.name as name', 'm.avatar as avatar', 'm.value_level as value_level',
                       'm.identify as identify', 'm.user_id as user_id',
                       'm.audience_gender as audience_gender',
                       'm.audience_province_id as audience_province_id', 'm.audience_city_id as audience_city_id',
                       'm.audience_county_id as audience_county_id',
                       'mw.original as original', 'mw.qrcode as qrcode'],
            'condition': 'dto.demand_id in (%s)' % str_demand_id,
            'join': 'media as m ON (dto.media_id = m.id) join media_wechat as mw on (mw.media_id = m.id)',
            'order': 'm.id desc'
        }
        if limit is not None:
            dicTakeOrder['limit'] = ['0', limit]

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.findManyAs('demand_take_order as dto', dicTakeOrder)

        if tupData:
            for k, item in enumerate(tupData):
                # 处理头像
                item['avatar'] = self.getAvatarUrl(item['avatar'])
                item['media_category'] = self.media_service.media_category(item['media_id'])
                if not item['media_category']:
                    item['media_category'] = {'cate_id': 0, 'name': '不限'}
                item['media_tag'] = self.media_service.media_tag(item['media_id'])
                item['media_price'] = self.media_service.media_price(item['media_id'])
                item['original'] = self.media_service.get_original(item['original'])
                item['value_level'] = self.media_service.get_value_level(item['value_level'])
                item['qrcode'] = self.media_service.get_qrcode(item['qrcode'])
                item['audience_gender'] = self.media_service.get_audience_gender(item['audience_gender'])
                item['area'] = self.area_service.get_area(item['audience_province_id'], item['audience_city_id'],
                                                          item['audience_county_id'])
                item['user'] = self.user_service.get_user(item['user_id'])
                if item['user']:
                    item['user']['avatar'] = self.getAvatarUrl(item['user']['avatar'])
                # 判断自媒体是否存在于对应需求单id的预选单中
                item['exist_in_cart'] = self.cart_exist(demand_id, item['media_id'])

        return tupData

    def cart_exist(self, demand_id, media_id):
        exist = self.demandCartModel.findOne({
            'condition': 'demand_id in (%s) and media_id in (%s)' % (demand_id, media_id),
        })
        if exist:
            return 1
        else:
            return 0

    def take_order_media(self, str_uid, str_demand_id):
        """ 我的接单自媒体列表

        @params strUid string 用户ID
        """

        media_model = self.importModel('media')
        tupData = media_model.findManyAs('media as m', {
            'fields': ['m.*', 'mw.wechat_id', 'mw.original', 'mw.qrcode', 'cm.id as cate_id', 'cm.name as cate_name'],
            'join': 'media_wechat as mw ON (m.id = mw.media_id) ' +
                    'left join category_media as cm on (m.category_media_id = cm.id) ',
            'condition': 'm.user_id = "%s" and m.status = 0' % str_uid
        })

        untake_count = 0
        if tupData:
            media_service = self.importService('media')
            for k, item in enumerate(tupData):
                str_media_id = str(item['id'])

                # avatar
                item['avatar'] = media_service.getAvatarUrl(item['avatar'], 'avatarx')

                # 自媒体已经接过此需求单
                if self.get_take_order(str_uid, str_demand_id, str_media_id):
                    item['status'] = -1
                    continue

                # 报价
                item['price'] = media_service.media_price(str_media_id)
                if len(item['price']) == 0:
                    item['status'] = -2
                    untake_count += 1
                    continue

                # tag
                item['category'] = media_service.media_category(str_media_id)
                if not item['category']:
                    item['status'] = -2
                    untake_count += 1
                    continue

                # tag
                item['tag'] = media_service.get_tag(str_media_id)
                if len(item['tag']) == 0:
                    item['status'] = -2
                    untake_count += 1

        return tupData, untake_count

    # def demandJiedanMy(self, strDemandId, strUserId):
    #    """ 我的接单信息
    #
    #    @params strDemandId string 需求ID
    #    @params strUserId string 用户ID
    #    """
    #
    #    demandTakeOrderModel = self.importModel('demand_take_order')
    #    tupData = demandTakeOrderModel.findMany({
    #        'fields': ['dj.*', 'oa.id as official_id', 'oa.avatar', 'oa.name', 'oa.wechat_id', 'oa.features'],
    #        'condition': 'dj.demand_id = "%s" and dj.user_id = "%s"' % (strDemandId, strUserId),
    #        'join': 'pt_official_accounts as oa ON (dj.oa_id = oa.id)'
    #    })
    #
    #    lisData = self.demandJiedanData(tupData)
    #
    #    lisOfficialId = []
    #    dicCategory = {}
    #    if lisData:
    #        for item in lisData:
    #            lisOfficialId.append(str(item['official_id']))
    #
    #        # 处理分类
    #        if lisOfficialId:
    #            officialService = self.importService('official')
    #            tupCategory = officialService.official_categorys(lisOfficialId)
    #            dicCategory = officialService.official_category_key(tupCategory)
    #
    #        # 重组数据
    #        for k, item in enumerate(lisData):
    #            if item['official_id'] in dicCategory.keys():
    #                lisData[k]['category'] = dicCategory[item['official_id']]
    #            else:
    #                lisData[k]['category'] = {}
    #
    #    return lisData

    def take_order(self, str_user_id, str_demand_id, str_media_id, str_phone):
        """ 提交接单
        """
        try:
            lis_media_id = str_media_id.split(',')
            #print lis_media_id
            for media_id in lis_media_id:
                #print media_id
                exist = self.demandTakeOrderModel.getRows({
                    'condition': 'demand_id = {did} and media_id = {mid}'.format(did=str_demand_id, mid=media_id)
                })
                print exist
                if exist == 0:
                    #print 1111
                    self.demandTakeOrderModel.insert({
                        'key': "user_id, demand_id, media_id, phone, status, create_time",
                        'val': '%s, %s, %s, %s, 1, %d' % (
                            str_user_id, str_demand_id, media_id, str_phone, int(self.time.time()))
                    })
            dicOrder = self.demandTakeOrderModel.findMany({
                'fields': ['count(*) as count'],
                'condition': 'demand_id ={did}'.format(did=str_demand_id)
            })
            # self.model.db.commit()
            # print dicOrder
            if dicOrder[0]['count'] == len(lis_media_id):
                dicData = self.demandModel.findOneAs(
                    'demand as d',
                    {
                        'fields': ['d.*', 'u.nickname'],
                        'join': 'user as u ON (u.id = d.user_id) ',
                        'condition': 'd.id = {did}'.format(did=str_demand_id),
                        'order': 'd.create_time desc'
                    }
                )
                # print dicData
                sms.sendsms(dicData['phone'], 'take_order', {
                    'nickname': dicData['nickname'].encode('utf-8'),
                    'demand_title': dicData['title'].encode('utf-8'),
                })
                self.importService('message').send_message(dicData['user_id'],'take_order',{
                    'demand_title': dicData['title'].encode('utf-8'),
                    'demand_id':str(str_demand_id).encode('utf-8')
                })
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def take_order_cancel(self, str_m_user_id, str_demand_id, str_media_id):
        """ 需求修改
        """
        lis_condition = ['user_id = %s' % str_m_user_id,
                         'demand_id = %s' % str_demand_id,
                         'media_id = %s' % str_media_id]

        self.demandTakeOrderModel.delete({
            'condition': ' and '.join(lis_condition)
        })
        if self.model.db.status != 200:
            return 601

    def feedback_submit(self, dicData):
        try:
            link = dicData['url']
            biz = link[link.index('__biz=') + len('__biz='): link.index('&')]
            dicDataWechat = self.importModel('media_wechat').findOne({
                'condition': 'media_id = %s' % dicData['media_id']
            })
            if biz != dicDataWechat.get('biz'):
                return 401
            self.importModel('demand_wechat_feedback').insert({
                'key': 'user_id, order_id, demand_id, media_id, url, title, read_num, publish_time, '
                       'picture_1, picture_2, picture_3, status, last_update_time, create_time',
                'val': '%s, %s, %s, %s, "%s", "%s", %s, %s, "%s", "%s", "%s", %s, %s, %s' % (
                    dicData['user_id'], dicData['order_id'], dicData['demand_id'], dicData['media_id'],
                    dicData['url'], dicData['title'], dicData['read_num'],
                    self.time.mktime(self.time.strptime(dicData['publish_time'], '%Y-%m-%d')),
                    dicData['picture_1'], dicData['picture_2'], dicData['picture_3'], 1,
                    int(self.time.time()),int(self.time.time())
                )
            })
            self.importModel('demand_order').update({
                'fields': ['status = 3'],
                'condition': 'id = %s and status = 2' % dicData['order_id']
            })
            # self.model.db.commit()
            dicSms = self.demandOrderModel.findOneAs(
                'demand_order as o',
                {
                    'fields': ['u.nickname', 'm.name', 'd.title', 'd.phone','d.user_id'],
                    'join': 'user as u ON (u.id = o.ad_user_id) '
                            'LEFT JOIN media as m ON(m.id = o.media_id) '
                            'LEFT JOIN demand as d ON(d.id = o.demand_id) ',
                    'condition': 'o.id = {oid}'.format(oid=dicData['order_id']),
                    'order': 'd.create_time desc'
                }
            )
            # print dicData
            sms.sendsms(dicSms['phone'], 'feedback', {
                'nickname': dicSms['nickname'].encode('utf-8'),
                'demand_title': dicSms['title'].encode('utf-8'),
                'media_title': dicSms['name'].encode('utf-8'),
            })
            self.importService('message').send_message(dicSms['user_id'],'feedback',{
                    'media_title': dicSms['name'].encode('utf-8'),
                    'order_id': str(dicData['order_id']).encode('utf-8')
                })
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def feedback_pass(self, strDemandId, strOrderId):
        try:
            feedbackModel = self.importModel('demand_wechat_feedback')
            feedback = feedbackModel.findOne({
                'condition': 'order_id = %s and demand_id = %s' % (strOrderId, strDemandId)
            })
            import api.crawler as crawler
            cw = crawler.crawler()
            readNum = cw.get_num_real_time(feedback.get('url')).get('readnum', 0)
            feedbackModel.update({
                'fields': ['status = 0',
                           'read_num = %s' % readNum,
                           'last_update_time = %s' % int(self.time.time())],
                'condition': 'order_id = %s and status = 1' % strOrderId
            })
            demandOrderModel = self.importModel('demand_order')
            demandOrderModel.update({
                'fields': ['status = 4'],
                'condition': 'id = %s and status = 3' % strOrderId
            })
            tupData = demandOrderModel.findMany({
                'condition': 'demand_id = %s' % strDemandId
            })
            status = set([i['status'] for i in tupData])
            # 需求单所有的订单全为结束状态
            if 4 in status and len(status) == 1:
                self.importModel('demand').update({
                    'fields': ['status = 4'],
                    'condition': 'id = %s' % strDemandId
                })
            dicSms = self.demandOrderModel.findOneAs(
                'demand_order as o',
                {
                    'fields': ['u.nickname', 'm.name', 'd.title', 'dt.phone','dt.user_id'],
                    'join': 'user as u ON (u.id = o.m_user_id) '
                            'LEFT JOIN media as m ON(m.id = o.media_id) '
                            'LEFT JOIN demand as d ON(d.id = o.demand_id) '
                            'LEFT JOIN demand_take_order as dt '
                            'ON(dt.demand_id = o.demand_id and dt.media_id = o.media_id )',
                    'condition': 'o.id = {oid}'.format(oid=strOrderId),
                    'order': 'd.create_time desc'
                }
            )
            # print dicData
            sms.sendsms(dicSms['phone'], 'feedback_check', {
                'nickname': dicSms['nickname'].encode('utf-8'),
                'demand_title': dicSms['title'].encode('utf-8'),
                'media_title': dicSms['name'].encode('utf-8'),
            })
            self.importService('message').send_message(dicSms['user_id'],'feedback_check',{
                    'media_title': dicSms['name'].encode('utf-8'),
                    'order_id':str(strOrderId).encode('utf-8')
                })
            # self.model.db.commit()
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def cart(self, strDemandId, strUserId):
        dicDemand = self.demandModel.findOneAs(
            'demand as d',
            {
                'fields': ['d.*', 'df.name as demand_form'],
                'join': 'demand_form as df ON (df.id = d.form)',
                'condition': 'd.id = %s' % strDemandId
            }
        )
        tupData = self.demandCartModel.findManyAs(
            'demand_cart as dc',
            {
                'fields': ['dc.*', 'm.name as media_name', 'm.avatar'],
                'join': 'media as m ON (m.id = dc.media_id) ',
                'condition': 'dc.demand_id = %s and dc.ad_user_id = %s' % (strDemandId, strUserId)
            }
        )
        if dicDemand['money']:
            dicDemand['money'] = int(dicDemand['money'])

        if tupData:
            for k, item in enumerate(tupData):
                media_phone = self.get_take_order_1(strDemandId, item['media_id'])
                if media_phone:
                    item['media_phone'] = media_phone[0]['phone']
                else:
                    item['media_phone'] = ()
                # tupData[0]['price'] = int(tupData[0]['price'])
                # 只取整第一项？ 2015-11-10 fix
                item['price'] = int(item['price'])

        return dicDemand, tupData

    def cart_count(self, strDemandId):
        dicDemand = self.demandCartModel.findOne(
            {
                'fields': ['count(1) as count'],
                'condition': 'demand_id = %s' % strDemandId
            }
        )
        return dicDemand['count']

    def cart_create(self, str_ad_user_id, str_demand_id, str_m_user_id, str_media_id, str_media_price_id, str_price):
        exist = self.demandCartModel.findOne({
            'condition': 'demand_id = "%s" and media_id = "%s"' % (str_demand_id, str_media_id)
        })

        if exist:
            self.status = 700  # 重复刊例报价
        else:
            self.demandCartModel.insert({
                'key': 'ad_user_id, demand_id, m_user_id, media_id, media_price_id, price, status, create_time',
                'val': '%s, %s, %s, %s, %s, %s, 0, %d' % (
                    str_ad_user_id, str_demand_id, str_m_user_id, str_media_id, str_media_price_id, str_price,
                    int(self.time.time()))
            })
            self.importModel('media_price').update({
                'fields': ['status = 1'],
                'condition': 'id = {media_price_id}'.format(media_price_id=str_media_price_id)
            })
            if self.model.db.status != 200:
                self.status = 601

    def cart_update(self, dicData):
        cartService = self.importModel('demand_cart')
        try:
            strPrice = dicData.get('price')
            media_price_id = dicData.get('media_price_id')
            if media_price_id:
                self.importModel('media_price').update({
                    'fields': ['status = 0'],
                    'condition': 'id = {media_price}'.format(media_price=media_price_id)
                })
            if strPrice:
                strPrice = int(strPrice)
                cartService.update({
                    'fields': ['price = %s' % strPrice, 'status = 2'],
                    'condition': 'id = %s and status = 1' % dicData['cart_id']
                })
                dicSms = self.demandCartModel.findOneAs(
                    'demand_cart as c',
                    {
                        'fields': ['d.phone', 'u.nickname', 'd.title', 'm.name as media_title', 'c.media_price_id',
                                   'c.price','d.user_id','d.id as demand_id'],
                        'join': 'user as u ON (u.id = c.ad_user_id) '
                                'LEFT JOIN demand as d ON(d.id = c.demand_id) '
                                'LEFT JOIN media as m ON( m.id=c.media_id) ',
                        'condition': 'c.id = {cid}'.format(cid=dicData['cart_id']),
                        'order': 'd.create_time desc'
                    }
                )
                dicPrice = self.media_service.media_attr_value_info(dicSms['media_price_id'])[0]
                # print dicPrice['attr_value_info']
                price_name = ""
                for (k, v) in dicPrice['attr_value_info'].items():
                    # print '%s :%s' %(k,v)
                    price_name = price_name + v
                    # print price_name
                # print price_name
                sms.sendsms(dicSms['phone'], 'already_change_price', {
                    'nickname': dicSms['nickname'].encode('utf-8'),
                    'price': str(dicSms['price']).encode('utf-8'),
                    'media_title': dicSms['media_title'].encode('utf-8'),
                    'price_name': price_name.encode('utf-8'),
                })
                #print dicData['cart_id']
                self.importService('message').send_message(dicSms['user_id'],'already_change_price',{
                    'nickname':dicSms['nickname'].encode('utf-8'),
                    'cart_id':str(dicSms['demand_id']).encode('utf-8'),
                    'price': str(dicSms['price']).encode('utf-8'),
                    'media_title': dicSms['media_title'].encode('utf-8'),
                    'price_name': price_name.encode('utf-8'),
                    # TODO 价格变化信息
                    #'change_info':''
                })
            else:
                cartService.update({
                    'fields': ['status = 1'],
                    'condition': 'id = %s and status = 0' % dicData['cart_id']
                })
                # 改价发送短信
                # print 1111
                dicSms = self.demandCartModel.findOneAs(
                    'demand_cart as c',
                    {
                        'fields': ['u.nickname', 'd.title', 'm.name as media_title', 'c.media_price_id', 't.phone','t.user_id','c.demand_id'],
                        'join': 'user as u ON (u.id = c.m_user_id) '
                                'LEFT JOIN demand as d ON(d.id = c.demand_id) '
                                'LEFT JOIN media as m ON( m.id=c.media_id) '
                                'LEFT JOIN demand_take_order as t ON(t.demand_id = c.demand_id and t.media_id = c.media_id)',
                        'condition': 'c.id = {cid}'.format(cid=dicData['cart_id']),
                        'order': 'd.create_time desc'
                    }
                )
                dicPrice = self.media_service.media_attr_value_info(dicSms['media_price_id'])[0]
                # print dicPrice['attr_value_info']
                price_name = ""
                for (k, v) in dicPrice['attr_value_info'].items():
                    # print '%s :%s' %(k,v)
                    price_name = price_name + v
                    # print price_name
                # print price_name
                sms.sendsms(dicSms['phone'], 'apply_change_price', {
                    'nickname': dicSms['nickname'].encode('utf-8'),
                    'demand_title': dicSms['title'].encode('utf-8'),
                    'media_title': dicSms['media_title'].encode('utf-8'),
                    'price_name': price_name.encode('utf-8'),
                })
                self.importService('message').send_message(dicSms['user_id'],'apply_change_price',{
                    'demand_id':str(dicSms['demand_id']).encode('utf-8'),
                    'demand_title': dicSms['title'].encode('utf-8'),
                    'media_title': dicSms['media_title'].encode('utf-8'),
                    'price_name': price_name.encode('utf-8'),
                })
            # self.model.db.commit()

            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def cart_delete(self, strCartId):
        try:
            # 更改刊例报价状态，删除后不在为使用状态中
            # media_price_id = self.importModel('demand_cart').findOne({
            #     'fields': ['media_price_id'],
            #     'condition': 'id = %s' % strCartId
            # })[0]['media_price_id']
            # self.importModel('media_price').update({
            #     'fields': ['status = 0'],
            #     'condition': 'id = {media_price}'.format(media_price=media_price_id)
            # })
            self.importModel('demand_cart').delete({
                'condition': 'id = %s' % strCartId
            })

            # self.model.db.commit()
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    # def pay_create(self, strData, strUserId):
    #     """ 创建支付信息
    #
    #     @params strData string 支付信息，JSON格式
    #     @params strUserId string 用户ID
    #     """
    #
    #     if not strData or not strUserId:
    #         return {'status': 401, 'id': None}
    #
    #     dicData = self.json.loads(strData.replace('&#39;', '\\\"'))
    #     strDemandId = dicData.get('demand_id')
    #     strMoney = dicData.get('total_price')
    #     lisCartDetail = eval(dicData.get('cart_detail'))
    #     strTradeCode = self.salt(22)
    #     intCreateTime = int(self.time.time())
    #
    #     if not strDemandId or not strMoney or not lisCartDetail:
    #         return {'status': 401, 'id': None}
    #
    #     try:
    #         demandOrderModel = self.importModel('demand_order')
    #         demandPayModel = self.importModel('pay')
    #         for item in lisCartDetail:
    #             strMediaId = item.get('media_id')
    #             strMediaPriceId = item.get('media_price_id')
    #             strPrice = item['price']
    #             # 检查订单信息是否存在（需求单id，自媒体id，刊例id）
    #             dicOrder = demandOrderModel.findOne({
    #                 'condition': 'demand_id = %s and media_id = %s and media_price_id = %s' % (
    #                     strDemandId, strMediaId, strMediaPriceId)
    #             })
    #             if dicOrder:
    #                 strOrderId = dicOrder.get('id')
    #                 demandOrderModel.update({
    #                     'fields': ['price = %s' % strPrice],
    #                     'condition': 'id = %s' % strOrderId
    #                 })
    #             else:
    #                 strOrderId = demandOrderModel.insert({
    #                     'key': 'ad_user_id, demand_id, m_user_id, media_id, '
    #                            'media_price_id, price, status, create_time',
    #                     'val': '%s, %s, %s, %s, %s, %s, %s, %s' % (
    #                         item['ad_user_id'], strDemandId, item['m_user_id'],
    #                         strMediaId, strMediaPriceId, strPrice, 1, intCreateTime)
    #                 })
    #             # 检查支付信息是否存在（订单id）
    #             dicPay = demandPayModel.findOne({
    #                 'condition': 'order_id = %s' % strOrderId
    #             })
    #
    #             if dicPay:
    #                 demandPayModel.update({
    #                     'fields': ['money = %s' % strMoney, 'trade_code = "%s"' % strTradeCode],
    #                     'condition': 'order_id = %s' % strOrderId
    #                 })
    #             else:
    #                 demandPayModel.insert({
    #                     'key': 'order_id, demand_id, pay_type, money, trade_code, status, create_time',
    #                     'val': '%s, %s, %s, %s, "%s", %s, %s' % (
    #                         strOrderId, strDemandId, 1, strMoney, strTradeCode, 1, intCreateTime)
    #                 })
    #         self.model.db.commit()
    #         return {'status': 200, 'demand_id': strDemandId}
    #     except Exception, e:
    #         print e
    #         self.model.db.rollback()
    #         return {'status': 500, 'demand_id': None}

    def pay(self, strData, strUserId):
        if not strData or not strUserId:
            return {'status': 401}

        dicData = self.json.loads(strData.replace('&#39;', '\\\"'))
        lisCartDetail = eval(dicData.get('cart_detail'))
        dicData['cart_detail'] = lisCartDetail
        dicData['user_id'] = strUserId

        return {'status': 200, 'data': dicData}

    def get_pay_info(self, strDemandId, strAdUserId):
        # 付款码
        strTradeCode = self.salt(22)
        # print 'gen code: {code}'.format(code=strTradeCode)
        # 标题
        dicData = self.importModel('demand').findOne({
            'fields': ['title'],
            'condition': 'id = %s' % strDemandId
        })

        # 广告主应付款
        tupPrice = self.importModel('demand_cart').findMany({
            'fields': ['price'],
            'condition': 'ad_user_id = %s and demand_id = %s' % (strAdUserId, strDemandId)
        })
        money = sum([i['price'] for i in tupPrice])
        orderPayModel = self.importModel('pay')
        dicPay = orderPayModel.findOne({
            'condition': 'user_id = %s and demand_id = "%s"' % (strAdUserId, strDemandId)
        })
        if not dicPay:
            # 生成广告主的流水

            import uuid
            import re
            uuids = str(uuid.uuid1())
            uuidt = ('').join(re.findall(r"[0-9]",uuids))[:-14]
            strOrderId = self.formatTime(int(self.time.time()), '%Y%m%d')+uuidt
            orderPayModel.insert({
                'key': 'user_id, order_id, demand_id, pay_type, money, trade_code, status, create_time',
                'val': '%s, %s, %s, %s, %s, "%s", %s, %s' % (
                    strAdUserId, strOrderId, strDemandId, 1, money, strTradeCode, 1, int(self.time.time()))
            })
            dicData['trade_code'] = strTradeCode
            dicData['order_id'] = strOrderId
        else:
            orderPayModel.update({
                'fields': ['money = %s' % money],
                'condition': 'user_id = %s and demand_id = "%s"' % (strAdUserId, strDemandId)
            })

            dicData['trade_code'] = dicPay['trade_code']
            dicData['order_id'] = dicPay['order_id']
        # print 'send code: {code}'.format(code=dicData['trade_code'])
        dicData['money'] = money
        return dicData

    # def pay(self, strId, strUserId):
    #     """ 确认支付
    #     通过支付记录ID和用户ID获取需求信息与支付信息
    #
    #     @params strId string 支付记录ID
    #     @params strUserId string 用户ID
    #     """
    #
    #     if not strId or not strUserId:
    #         return 401
    #
    #     demandPayModel = self.importModel('pay')
    #     dicData = demandPayModel.find_one_demand({
    #         'condition': 'dp.id = "%s" and dp.user_id = "%s"' % (strId, strUserId),
    #         'join': 'demand as d ON (d.demand_id = dp.demand_id)',
    #     })
    #
    #     return dicData

    def payed(self, strDemandId):
        """ 已支付信息

        @params strDemandId string 需求ID
        """

        if not strDemandId:
            return 401

        demandPayModel = self.importModel('pay')
        dicData = demandPayModel.find_one_demand({
            'condition': 'dp.demand_id = "%s"' % strDemandId,
        })

        return dicData

    def pay_check(self, dicData):
        """ 验证异步通知信息，更改需求单状态，生成订单记录, 清空预选单

        @params dicData dict 数据
        """
        # print 'step0'
        # print dicData
        if not dicData['out_trade_no']:
            return 401

        demandPayModel = self.importModel('pay')

        dicDemandPay = demandPayModel.findOne({
            'condition': 'trade_code = "%s"' % dicData['out_trade_no'],
        })

        if not dicDemandPay:
            return 601

        try:
            strUserId = dicDemandPay['user_id']
            strDemandId = dicDemandPay['demand_id']
            # 需求单变为营销中
            demandModel = self.importModel('demand')
            demandModel.update({
                'fields': ['status = 3'],
                'condition': 'id = "%s"' % strDemandId
            })
            # print 'step1'
            # 修改广告主的流水支付状态
            demandPayModel = self.importModel('pay')
            demandPayModel.update({
                'fields': ['status = 0'],
                'condition': 'id = "%s"' % dicDemandPay['id']
            })
            # print 'step2'
            # 读取预选单信息并生成订单
            demandCartModel = self.importModel('demand_cart')
            tupCart = demandCartModel.findMany({
                'condition': 'ad_user_id = %s and demand_id = %s' % (strUserId, strDemandId)
            })
            # print 111
            for item in tupCart:
                demandOrderModel = self.importModel('demand_order')
                demandOrderModel.insert({
                    'key': 'ad_user_id, demand_id, m_user_id, media_id, media_price_id, price, status, create_time',
                    'val': '%s, %s, %s, %s, %s, %s, %s, %s' % (
                        item['ad_user_id'], strDemandId, item['m_user_id'],
                        item['media_id'], item['media_price_id'],
                        item['price'], 2, int(self.time.time())
                    )
                })
                self.importModel('media_price').update({
                    'fields': ['status = 0'],
                    'condition': 'id = {media_price}'.format(media_price=item['media_price_id'])
                })
            # print 222
            # 删除预选单
            self.importModel('demand_cart').delete({
                'condition': 'ad_user_id = %s and demand_id = %s' % (strUserId, strDemandId)
            })

            # 记录支付流水，判断是否已有记录，如果没有，新增
            # demandPayLogModel = self.importModel('order_pay_log')
            # dicPayLog = demandPayLogModel.find_one({
            #     'condition': 'yidao_trade_no = "%s"' % dicData['out_trade_no']
            # })
            # if not dicPayLog:
            #     strBody = dicData['body'] if 'body' in dicData.keys() else ''
            #     demandPayLogModel.insert({
            #         'key': 'pay_id, user_id, demand_id, yidao_trade_no, money, body, price, buyer_email, '
            #                'sign, discount, trade_status, gmt_payment, subject, trade_no, '
            #                'seller_id, is_total_fee_adjust, use_coupon, gmt_create, '
            #                'out_trade_no, payment_type, total_fee, sign_type, notify_time, '
            #                'buyer_id, notify_id, notify_type, quantity, log_create',
            #         'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", '
            #                '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", '
            #                '"%s", "%s", "%s", "%s", "%s", "%s"' % (
            #             dicDemandPay['id'],
            #             dicDemandPay['user_id'],
            #             dicDemandPay['demand_id'],
            #             dicData['out_trade_no'],
            #             dicData['price'],
            #             strBody,
            #             dicData['price'],
            #             dicData['buyer_email'],
            #             dicData['sign'],
            #             dicData['discount'],
            #             dicData['trade_status'],
            #             dicData['gmt_payment'],
            #             dicData['subject'],
            #             dicData['trade_no'],
            #             dicData['seller_id'],
            #             dicData['is_total_fee_adjust'],
            #             dicData['use_coupon'],
            #             dicData['gmt_create'],
            #             dicData['out_trade_no'],
            #             dicData['payment_type'],
            #             dicData['total_fee'],
            #             dicData['sign_type'],
            #             dicData['notify_time'],
            #             dicData['buyer_id'],
            #             dicData['notify_id'],
            #             dicData['notify_type'],
            #             dicData['quantity'],
            #             int(self.time.time())
            #         )
            #     })

            # self.model.db.commit()
            # 发送短信通知
            # print 333
            # print dicDemandPay
            # 读取该需求所有接单信息
            tupDemandTakeOrder = self.demand_take_order_demand_id(strDemandId)
            # print tupDemandTakeOrder
            if tupDemandTakeOrder:
                # print 666
                import api.sms as sms
                # 用户ID
                lisUserId = []
                for item in tupDemandTakeOrder:
                    lisUserId.append(str(item['user_id']))

                # 发送短信
                for k, item in enumerate(tupDemandTakeOrder):
                    Mediainfo = self.demandTakeOrderModel.findOneAs('demand_take_order as t', {
                        'fields': ['m.name', 'u.nickname', 't.phone','m.user_id','o.id as order_id'],
                        'condition': 'm.id = {mid} and t.demand_id = {did}'.format(mid=item['media_id'],did = strDemandId),
                        'join': 'media as m ON(m.id = t.media_id) LEFT JOIN user as u ON(u.id = m.user_id) LEFT JOIN demand_order as o ON(t.media_id = o.media_id and t.demand_id = o.demand_id)'
                    })

                    strUserPhone = Mediainfo['phone']
                    strNickname = Mediainfo['nickname']  # 用户昵称
                    strMediatitle = Mediainfo['name']
                    strOrderId = Mediainfo['order_id']
                    Demandinfo = self.demandModel.findOne({
                        'fields': ['title'],
                        'condition': 'id = {did}'.format(did=strDemandId),
                    })
                    strDemandTitle = Demandinfo['title']
                    # print strDemandTitle
                    # print strUserPhone
                    # print  strMediatitle
                    flag = self.demandOrderModel.findOne({
                        'condition': 'demand_id = {did} and media_id ={mid}'.format(did=strDemandId,
                                                                                    mid=item['media_id'])
                    })
                    if flag:
                        strKey = 'pay'
                        sms.sendsms(strUserPhone, strKey, {
                        'nickname': strNickname.encode('utf8'),
                        'demand_title': strDemandTitle.encode('utf8'),
                        'media_title': strMediatitle.encode('utf8'),
                        })
                        self.importService('message').send_message(Mediainfo['user_id'],strKey,{
                            'demand_id': str(strDemandId).encode('utf-8'),
                            'order_id': str(strOrderId).encode('utf-8'),
                            'demand_title': strDemandTitle.encode('utf8'),
                            'media_title': strMediatitle.encode('utf8'),
                        })

                    else:
                        strKey = 'nopay'
                        self.importService('message').send_message(Mediainfo['user_id'],strKey,{
                            'demand_id': str(strDemandId).encode('utf-8'),
                            'demand_title': strDemandTitle.encode('utf8'),

                        })


            return 200
        except Exception, e:
            print e
            # print 444
            # self.model.db.rollback()
            return 500

    def feedback_create(self, strJiedanId, dicData, strUserId):
        """ 提交反馈

        @params strJiedanId string 接单ID
        @params dicData dict 反馈信息
        @params strUserId string 用户ID
        """

        # 发送短信变量
        # strDemandId = ''  # 需求ID
        strNickname = ''  # 用户昵称
        strDemandTitle = ''  # 需求标题
        strUserPhone = ''  # 用户手机
        strKey = 'feedback'  # 消息类型

        if not strJiedanId or not dicData or not strUserId:
            return {'status': 401}

        # 获取接单信息
        dicJiedan = self.demand_jiedan_one(strJiedanId)
        if not dicJiedan:
            return {'status': 601}

        strDemandId = str(dicJiedan['demand_id'])

        strType = ''
        # 获取支付信息
        demandPayModel = self.importModel('pay')
        dicPay = demandPayModel.find_one_demand({
            'condition': 'dp.demand_id = "%s"' % dicJiedan['demand_id'],
            'join': 'demand as d ON (dp.demand_id = d.demand_id)'
        })
        if dicPay:
            strUserPhone = dicPay['phone']
            strDemandTitle = dicPay['title']
            strDetail = dicPay['detail']
            try:
                lisDetail = self.json.loads(strDetail)
            except Exception, e:
                print e
                lisDetail = []

            if lisDetail:
                for item in lisDetail:
                    if item['jid'] == strJiedanId:
                        strType = item['ptype']

        # 转换图文类型
        dicData['crawl_type'] = self.dicConfig['TU_TYPE'][dicData['crawl_type']]

        # 写数据
        try:
            # 读取反馈信息，判断是否已经提交
            demandFeedbackModel = self.importModel('demand_wechat_feedback')
            dicFeedback = demandFeedbackModel.findOne({
                'condition': 'demand_id = "%s" and oa_id = "%s"' % (dicJiedan['demand_id'], dicJiedan['oa_id'])
            })
            if dicFeedback:
                # 更新
                intId = dicFeedback['id']
                demandFeedbackModel.update({
                    'fields': ['url = "%s"' % dicData['url'], 'title = "%s"' % dicData['title'],
                               'crawl_type = "%s"' % dicData['crawl_type'], 'picture = "%s"' % dicData['picture']],
                    'condition': 'demand_id = "%s" and oa_id = "%s"' % (dicJiedan['demand_id'], dicJiedan['oa_id'])
                })
            else:
                intId = demandFeedbackModel.insert({
                    'key': 'demand_id, jiedan_id, oa_id, title, type, crawl_type, url, picture, time',
                    'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
                        dicJiedan['demand_id'],
                        strJiedanId,
                        dicJiedan['oa_id'],
                        dicData['title'],
                        strType,
                        dicData['crawl_type'],
                        dicData['url'],
                        dicData['picture'],
                        int(self.time.time())
                    )
                })

            # 更新订单状态
            self.demand_update_status(dicJiedan['demand_id'], 3)
            # self.model.db.commit()

            # 发送通知短信
            import api.sms as sms

            # 读取用户信息
            accountService = self.importService('account')
            dicUser = accountService.getOne(dicPay['user_id'])
            if dicUser:
                strNickname = dicUser['nickname']

            sms.sendsms(strUserPhone, strKey, {
                'nickname': strNickname.encode('utf8'),
                'demand_title': strDemandTitle.encode('utf8'),
                'demand_id': strDemandId,
            })
            return {'status': 200, 'id': intId}
        except Exception, e:
            print e
            # self.model.db.rollback()
            return {'status': 500, 'id': ''}

    def demand_feedback_list(self, strDemandId):
        """ 反馈列表, 指定需求ID，关联自媒体信息

        @params strDemandId string 需求ID
        """

        dicData = {}

        # 处理支付
        dicDemandJiedanDetail = {}
        demandPayModel = self.importModel('pay')
        dicPayed = demandPayModel.findOne({
            'condition': 'demand_id = "%s"' % strDemandId
        })
        if dicPayed:
            strDemandPayDetail = dicPayed['detail']
            lisDemandPayDetail = self.json.loads(strDemandPayDetail)
            if lisDemandPayDetail:
                for item in lisDemandPayDetail:
                    item['ptype'] = self.dicConfig['PRICE_TYPE'][item['ptype']]
                    dicDemandJiedanDetail[item['jid']] = item['ptype']

        demandTakeOrderModel = self.importModel('demand_take_order')
        tupData = demandTakeOrderModel.find_list({
            'fields': ['dj.*', 'oa.user_id', 'oa.name', 'oa.avatar', 'oa.wechat_id'],
            'condition': 'dj.demand_id = "%s" and dj.status = 1' % strDemandId,
            'join': 'pt_official_accounts as oa ON (dj.oa_id = oa.id)'
        })
        if tupData:
            lisUserId = []
            # lis_jiedan_id = []
            dicJiedan = {}
            demandFeedbackModel = self.importModel('demand_wechat_feedback')
            for k, item in enumerate(tupData):
                # 读取反馈信息
                dicFeedback = demandFeedbackModel.findOne({
                    'condition': 'jiedan_id = "%s" and oa_id = "%s"' % (item['id'], item['oa_id'])
                })
                if dicFeedback:
                    dicFeedback['picture'] = self.getAvatarUrl(dicFeedback['picture'])
                    dicFeedback['type'] = self.dicConfig['PRICE_TYPE'][dicFeedback['type']]
                    dicFeedback['time'] = self.formatTime(dicFeedback['time'], '%Y-%m-%d')

                tupData[k]['feedback'] = dicFeedback

                tupData[k]['avatar'] = self.getAvatarUrl(item['avatar'], 'avatar')
                tupData[k]['type'] = dicDemandJiedanDetail[str(item['id'])]

                if item['user_id'] not in dicJiedan.keys():
                    dicJiedan[item['user_id']] = []

                dicJiedan[item['user_id']].append(item)

                if item['user_id']:
                    lisUserId.append(str(item['user_id']))

            # 处理用户
            if lisUserId:
                accountService = self.importService('account')
                tupUser = accountService.get_list(','.join(lisUserId))
                if tupUser:
                    for item in tupUser:
                        item['avatar'] = self.getAvatarUrl(item['avatar'])

                        dicData[item['user_id']] = {}
                        item['phone'] = dicJiedan[item['user_id']][0]['phone']
                        dicData[item['user_id']]['user'] = item
                        dicData[item['user_id']]['jiedan'] = dicJiedan[item['user_id']]

        return dicData

    def demand_feedback_one_id(self, strId):
        """ 获取一条反馈信息，指定ID，关联需求表

        @params strId string 反馈ID
        """
        demandFeedbackModel = self.importModel('demand_wechat_feedback')
        dicData = demandFeedbackModel.find_one_demand({
            'join': 'demand as d ON (d.demand_id = df.demand_id)',
            'condition': 'df.id = "%s"' % strId
        })

        return dicData

    def demand_feedback_update_status(self, strId, strDemandId):
        """ 修改反馈状态，同时修改订单状态为已结束

        @params strId string 反馈ID
        @params strDemandId string 订单ID
        """

        strNickname = ''
        # strDemandTitle = ''
        # strDemandId = ''
        strUserPhone = ''

        try:
            # 读取反馈信息
            demandFeedbackModel = self.importModel('demand_wechat_feedback')
            dicFeedback = demandFeedbackModel.find_one_demand({
                'condition': 'df.id = "%s"' % strId
            })
            if not dicFeedback:
                return 601

            strDemandId = dicFeedback['demand_id']
            strDemandTitle = dicFeedback['title']

            demandFeedbackModel.update({
                'fields': ['status = 1'],
                'condition': 'id = "%s"' % strId
            })

            self.demand_update_status(strDemandId, 5)

            # self.model.db.commit()

            # 发送通知短信
            import api.sms as sms

            # 读取用户信息
            officialService = self.importService('official')
            dicOfficial = officialService.official_one_user({
                'oa_id': dicFeedback['oa_id']
            })
            if dicOfficial:
                strNickname = dicOfficial['nickname']

            # 电话
            demandTakeOrderModel = self.importModel('demand_take_order')
            dicJiedan = demandTakeOrderModel.find_one({
                'condition': 'id = "%s"' % dicFeedback['jiedan_id']
            })
            if dicJiedan:
                strUserPhone = dicJiedan['phone']

            strKey = 'feedback_check'
            sms.sendsms(strUserPhone, strKey, {
                'nickname': strNickname.encode('utf8'),
                'demand_title': strDemandTitle.encode('utf8'),
                'demand_id': strDemandId,
            })
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def demand_update_status(self, strDemandId, intStatus):
        """ 更新订单状态

        @params strDemandId string 订单ID
        @params intStatus int 状态
        """

        if not strDemandId or not intStatus:
            return 401

        # 读取订单信息，判断状态
        demandModel = self.importModel('demand')
        dicDemand = demandModel.getOne(strDemandId)
        if not dicDemand:
            return 601

        if intStatus == 3:
            if dicDemand['status'] != 2:
                return 603

        if intStatus == 5:
            if dicDemand['status'] != 3 and dicDemand['status'] != 4:
                return 603

        # 执行更新
        demandModel.update({
            'fields': ['status = "%s"' % intStatus],
            'condition': 'demand_id = "%s"' % strDemandId
        })

        # demandModel.commit()

    def cancel(self, strDemandId, strUserId):
        """ 取消需求

        @params strDemandId string 需求ID
        @params strUserId string 用户ID
        """

        if not strDemandId or not strUserId:
            return 401

        # 读取需求
        demandModel = self.importModel('demand')
        dicDemand = demandModel.findOne({
            'condition': 'id = "%s" and user_id = "%s"' % (strDemandId, strUserId)
        })

        if not dicDemand:
            return 601

        if dicDemand['status'] == 3 or dicDemand['status'] == 4:
            return 604

        # 执行取消（修改状态为7）
        try:
            demandModel.update({
                'fields': ['status = 7'],
                'condition': 'id = "%s"' % dicDemand['id']
            })

            demandTakeOrderModel = self.importModel('demand_take_order')
            demandTakeOrderModel.update({
                'fields': ['status = 3'],
                'condition': 'demand_id = "%s"' % dicDemand['id']
            })
            tup_take_order = demandTakeOrderModel.findMany({
                'condition': 'demand_id = "%s"' % dicDemand['id']
            })
            if tup_take_order :
                for item in tup_take_order :
                    self.importService('message').send_message(item['user_id'],'demand_cancel',{
                        'demand_id': str(dicDemand['id']).encode('utf-8'),
                        'demand_title':dicDemand['title']
                    })
            # self.model.db.commit()

            # 如果有人接单，发送撤销短消息
            # tupJiedan = self.demandTakeOrderModel.findMany({
            #     'fields': ['u.nickname', 'dj.phone'],
            #     'condition': 'dj.demand_id = "%s"' % dicDemand['demand_id'],
            #     'join': 'pt_users as u ON (dj.user_id = u.user_id)'
            # })
            # if tupJiedan:
            #     for item in tupJiedan:
            #         strNickname = item['nickname']
            #         strDemandTitle = dicDemand['title']
            #         import api.sms as sms
            #         sms.sendsms(item['phone'], 'cancel', {
            #             'nickname': strNickname,
            #             'demand_title': strDemandTitle.encode('utf8'),
            #         })

            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def get_status_valid(self):
        return [
            {'id': '2', 'name': '接单中'},
            {'id': '3', 'name': '营销中'},
            {'id': '4', 'name': '需求结束'},
        ]

    # 综合指数
    def get_stauts(self, int_status):
        for status in self.get_all_status():
            if status['id'] == str(int_status):
                return status['name']

        return 'E'

    @staticmethod
    def get_all_status():
        return [
            {'id': '1', 'name': '审核中'},
            {'id': '2', 'name': '接单中'},
            {'id': '3', 'name': '营销中'},
            {'id': '4', 'name': '需求结束'},
            {'id': '5', 'name': '审核不通过'},
            {'id': '6', 'name': '营销过期'},
        ]
