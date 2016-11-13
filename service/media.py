# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):

        base.baseService.__init__(self, _model, param)

        self.mediaModel = self.importModel('media')
        self.mediawechatModel = self.importModel('media_wechat')
        self.mediatagModel = self.importModel('media_tag')
        self.mediapriceModel = self.importModel('media_price')
        self.advalueModel = self.importModel('ad_value')
        self.tagModel = self.importModel('tag')
        self.user_model = self.importModel('user')

        self.area_service = self.importService('area')

    def list(self, dicData):
        """ 列表

        @params dicData dict
            dicData['page']                 分页页码
            dicData['category']             类目媒体
            dicData['tag']                  媒体Tag
            dicData['value_level']          媒体价值等级
            dicData['audience_gender']      受众性别
            dicData['identify']             账号认证
            dicData['original']             是否原创
            dicData['query']                查询词
            dicData['audience_province']    受众省份
            dicData['audience_city']        受众城市
            dicData['audience_county']      受众县
        """

        listCondition = []
        listJoin = []

        # 分类
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])

        # Tag
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append('media_tag mt on (m.id = mt.demand_id)')

        # 媒体价值等级
        if dicData['value_level']:
            listCondition.append('m.value_level in (%s)' % dicData['value_level'])

        # 受众性别
        if dicData['audience_gender']:
            listCondition.append('m.audience_gender in (%s)' % dicData['audience_gender'])

        # 账号认证
        if dicData['identify']:
            # 原认证判断
            # listCondition.append('m.identify in (%s)' % dicData['identify'])
            # 新认证判断
            idf = dicData['identify']
            if idf == '1':
                listCondition.append('m.identify is not NULL and m.identify != "" ')
            else:
                listCondition.append('(m.identify is NULL or m.identify = "")')

        # 是否原创
        if dicData['original']:
            listCondition.append('mw.original in (%s)' % dicData['original'])
        listJoin.append('media_wechat mw on (m.id = mw.media_id)')

        # 受众省份
        if dicData['audience_province']:
            listCondition.append('m.audience_province = %s' % dicData['audience_province'])

        # 受众城市
        if dicData['audience_city']:
            listCondition.append('m.audience_city = %s' % dicData['audience_city'])

        # 受众县
        if dicData['audience_county']:
            listCondition.append('m.audience_county = %s' % dicData['audience_county'])

        # 查询词
        if dicData['query']:
            listCondition.append('m.name like "%' + dicData['query'] + '%"')

        # 状态
        listCondition.append('m.status = 0')

        # 查询
        tupData = self.mediaModel.findPaginateAs('media as m', {
            'condition': ' and '.join(listCondition),
            'join': ' join '.join(listJoin),
            'page': [dicData['page'], 10],
            'order': 'm.create_time desc'
        })

        # 数据格式化
        if tupData:
            area_service = self.importService('area')
            for k, item in enumerate(tupData[0]):
                item['category'] = self.media_category_name(str(item['id']))
                if not item['category']:
                    item['category'] = '不限'
                item['tag'] = self.media_tag(str(item['id']))

                item['area'] = area_service.get_area(item['audience_province_id'], item['audience_city_id'],
                                                     item['audience_county_id'])
                item['value_level'] = self.get_value_level(item['value_level'])
                item['audience_gender'] = self.get_audience_gender(item['audience_gender'])

        return {'list': tupData[0],
                'count': tupData[1],
                'category': self.importService('category_media').commonUse(),
                'tag': self.importService('tag').get_list()}

    def detail(self, strMediaId):
        """ get one media by media's id

        @params strMediaId string media's id
        """

        if not strMediaId:
            return 401

        dicMedia = self.mediaModel.findOneAs('media as m', {
            'fields': ['m.*', 'u.nickname', 'u.avatar as user_avatar'],
            'condition': 'm.id = "%s"' % strMediaId,
            'join': 'user as u ON (m.user_id = u.id)'
        })

        if dicMedia:
            # get media wechat
            mediaWechatModel = self.importModel('media_wechat')
            dicMediaWechat = mediaWechatModel.findOne({
                'condition': 'media_id = "%s"' % strMediaId
            })
            if dicMediaWechat:
                dicMedia['original'] = dicMediaWechat['original']
                dicMedia['wechat_id'] = dicMediaWechat['wechat_id']
                # 二维码
                dicMedia['qrcode'] = self.getAvatarUrl(dicMediaWechat['qrcode'], 'avatar')
            else:
                dicMedia['original'] = ''
                dicMedia['wechat_id'] = ''
                dicMedia['qrcode'] = ''

            # 自媒体头像
            dicMedia['avatar'] = self.getAvatarUrl(dicMedia['avatar'], 'avatarx')
            # 用户头像
            dicMedia['user_avatar'] = self.getAvatarUrl(dicMedia['user_avatar'], 'avatar')

            # audience_area
            dicMedia['area'] = self.area_service.get_area(dicMedia['audience_province_id'],
                                                          dicMedia['audience_city_id'], dicMedia['audience_county_id'])

            # 阅读数据
            # dicMedia['week_read_data'] = self.week_read_data(dicMedia['data_info'])
            dicMedia['week_read_data'] = ''
            # 刊例报价

            dicMedia['price'] = self.media_price(strMediaId)

            # 标签
            tagService = self.importService('tag')
            tupMediaTag = tagService.get_tag(strMediaId)
            dicMedia['tags'] = tupMediaTag

            # 行业
            if dicMedia['category_media_id']:
                categoryMediaService = self.importService('category_media')
                dicCategory = categoryMediaService.get_one_category(str(dicMedia['category_media_id']))
                dicMedia['category'] = dicCategory['name']
            else:
                dicMedia['category'] = '不限'

            # 性别
            dicMedia['audience_gender'] = self.get_audience_gender(dicMedia['audience_gender'])
            # 级别
            dicMedia['value_level'] = self.get_value_level(dicMedia['value_level'])

        return dicMedia

    def media_basic(self, str_media_id):
        """ get one media by media's id

        @params strMediaId string media's id
        """

        dicMedia = self.mediaModel.findOneAs('media as m', {
            'fields': ['m.*', 'u.nickname', 'u.avatar as user_avatar'],
            'condition': 'm.id = %s' % str_media_id,
            'join': 'user as u ON (m.user_id = u.id)'
        })
        if dicMedia:
            # get media wechat
            mediaWechatModel = self.importModel('media_wechat')
            dicMediaWechat = mediaWechatModel.findOne({
                'condition': 'media_id = "%s"' % str_media_id
            })
            if dicMediaWechat:
                dicMedia['original'] = dicMediaWechat['original']
                dicMedia['wechat_id'] = dicMediaWechat['wechat_id']
                # 二维码
                dicMedia['qrcode'] = self.getAvatarUrl(dicMediaWechat['qrcode'], 'avatar')
            else:
                dicMedia['original'] = ''
                dicMedia['wechat_id'] = ''
                dicMedia['qrcode'] = ''

            # 自媒体头像
            dicMedia['avatar'] = self.getAvatarUrl(dicMedia['avatar'], 'avatarx')
            # 用户头像
            dicMedia['user_avatar'] = self.getAvatarUrl(dicMedia['user_avatar'], 'avatar')
            # audience_area
            dicMedia['area'] = self.area_service.get_area(dicMedia['audience_province_id'],
                                                          dicMedia['audience_city_id'], dicMedia['audience_county_id'])

            # 阅读数据
            # dicMedia['week_read_data'] = self.week_read_data(dicMedia['data_info'])
            dicMedia['week_read_data'] = ''
            # 刊例报价

            dicMedia['price'] = self.media_price(str_media_id)

            # 标签
            tagService = self.importService('tag')
            tupMediaTag = tagService.get_tag(str_media_id)
            dicMedia['tags'] = tupMediaTag

            # 行业
            if dicMedia['category_media_id']:
                categoryMediaService = self.importService('category_media')
                dicCategory = categoryMediaService.get_one_category(str(dicMedia['category_media_id']))
                dicMedia['category'] = dicCategory['name']
            else:
                dicMedia['category'] = '不限'

            # 性别
            dicMedia['audience_gender'] = self.get_audience_gender(dicMedia['audience_gender'])
            # 级别
            dicMedia['value_level'] = self.get_value_level(dicMedia['value_level'])

        return dicMedia

    def user_media_num(self, strUserId):
        """ 用户的自媒体数
        """

        dicData = self.mediaModel.findOne({
            'fields': ['count(id) as count'],
            'condition': 'user_id = "%s"' % strUserId
        })

        return dicData['count']

    def my_media(self, strUid):
        """ 我的自媒体

        @params strUid string 用户ID
        """
        lis_media_id = []
        # dic_media_price = {}
        # dic_media_tag = {}

        tupData = self.mediaModel.findManyAs('media as m', {
            'fields': ['m.*', 'mw.wechat_id', 'mw.original', 'mw.qrcode'],
            'join': 'media_wechat as mw ON (m.id = mw.media_id)',
            'condition': 'm.user_id = "%s"' % strUid
        })
        if tupData:
            category_media_service = self.importService('category_media')
            for k, item in enumerate(tupData):
                lis_media_id.append(str(item['id']))

                # avatar
                item['avatar'] = self.getAvatarUrl(item['avatar'], 'avatarx')

                # 地区
                item['area'] = self.area_service.get_area(item['audience_province_id'], item['audience_province_id'],
                                                          item['audience_county_id'])

                # 级别
                item['value_level'] = self.get_value_level(item['value_level'])

                # 受众性别
                item['audience_gender'] = self.get_audience_gender(item['audience_gender'])

                # tag
                item['tag'] = self.get_tag(item['id'])

                # category
                item['category'] = category_media_service.get_one_category(item['category_media_id'])
        return tupData

    def find_user(self, media_id):
        """ 通过media id 使用user 信息
        @ params media_id  用户id
        """
        tup_user_id = self.mediaModel.findMany({
            'fields': ['user_id'],
            'condition': 'id = "%s"' % media_id
        })
        if tup_user_id:
            user_id = tup_user_id[0].get('user_id')

            user_info = self.user_model.findMany({
                'fields': ['id', 'nickname', 'avatar', 'phone'],
                'condition': 'id = "%s"' % user_id
            })
            if user_info:
                user_info[0]['avatar'] = self.getAvatarUrl(user_info[0]['avatar'], 'avatarx')
                return user_info
            return 404
        else:
            return 404

    def media_category(self, str_media_id):
        """ 处理类目

        @params strDemandId string 广告需求ID，多个用,号分割
        """

        # str_media_id = ""
        # if isinstance(media_id, list):
        #    str_media_id = ','.join(media_id)
        # elif isinstance(media_id, str):
        #    str_media_id = media_id

        tupCategory = self.mediaModel.findManyAs('media as m', {
            'fields': ['cm.id as cate_id', 'cm.name as name'],
            'join': 'category_media as cm ON (m.category_media_id = cm.id)',
            'condition': 'm.id=%s and m.category_media_id is not NULL' % str_media_id
        })
        if tupCategory:
            return tupCategory[0]
        else:
            return {}

    def media_category_name(self, str_media_id):
        """ 处理Tag

        @params strDemandId string 广告需求ID，多个用,号分割
        """

        dicTag = self.mediaModel.findOneAs('media as m', {
            'fields': ['cm.name as name'],
            'condition': 'm.id="%s"' % str_media_id,
            'join': 'category_media as cm ON (m.category_media_id = cm.id)'
        })
        if dicTag:
            return dicTag['name']
        else:
            return ""

    def media_tag(self, str_media_id):
        """ 处理Tag
        """

        tupTag = self.mediaModel.findManyAs('media_tag as mt', {
            'fields': ['t.id as tag_id', 't.name as name'],
            'condition': 'mt.media_id="%s"' % str_media_id,
            'join': 'tag as t ON (mt.tag_id = t.id)'
        })

        return tupTag

    # 综合指数
    def get_value_level(self, int_val_level):
        for value_level in self.get_all_value_level():
            if value_level['id'] == str(int_val_level):
                return value_level['name']

        return '?'

    @staticmethod
    def get_all_value_level():
        return [
            {'id': '1', 'name': 'A'},
            {'id': '2', 'name': 'B'},
            {'id': '3', 'name': 'C'},
            {'id': '4', 'name': 'D'},
            {'id': '5', 'name': 'E'},
        ]

    # 受众性别
    def get_audience_gender(self, int_audience_gender):
        for audience_gender in self.get_all_audience_gender():
            if audience_gender['id'] == str(int_audience_gender):
                return audience_gender['name']

        return '不限'

    @staticmethod
    def get_all_audience_gender():
        return [
            {'id': '1', 'name': '偏女性'},
            {'id': '2', 'name': '偏男性'},
        ]

    # 认证
    def get_identify(self, int_identify):
        for identify in self.get_all_identify():
            if identify['id'] == str(int_identify):
                return identify['name']

        return '不限'

    @staticmethod
    def get_all_identify():
        return [
            {'id': '1', 'name': '已认证'},
            {'id': '0', 'name': '未认证'},
        ]

    # 原创
    def get_original(self, int_original):
        for original in self.get_all_original():
            if original['id'] == str(int_original):
                return original['name']

        return '不限'

    @staticmethod
    def get_all_original():
        return [
            {'id': '0', 'name': '非原创'},
            {'id': '1', 'name': '原创'},
        ]

    def media_simple(self, media_id):
        if isinstance(media_id, list):
            strCondition = 'id in (%s)' % ', '.join(media_id)
        else:
            strCondition = 'id = %s' % media_id
        tupData = self.mediaModel.findMany({
            'fields': ['id as media_id', 'name', 'avatar'],
            'condition': strCondition
        })
        lisData = []
        for i in tupData:
            i['avatar'] = self.getAvatarUrl(i['avatar'], 'avatar')
            lisData.append(i)
        return lisData

    def similry_media(self, str_media_id):
        dic_media = self.get_media(str_media_id)
        # print dic_media
        if not dic_media:
            return {}

        # 相同类目
        tup_same_category = ()
        if dic_media['category_media_id'] != 0 and dic_media['category_media_id'] is not None:
            tup_same_category = self.mediaModel.findMany({
                'fields': ['id'],
                'condition': 'category_media_id = %s' % dic_media['category_media_id']
            })

        return tup_same_category

    def media_reco(self, tup_demand_category):
        list_demand_cate = []
        for demand_cate in tup_demand_category:
            list_demand_cate.append(str(demand_cate['cate_id']))

        if len(list_demand_cate) == 0:
            return ()

        # 相同类目
        # tup_same_category = ()
        tup_same_category = self.mediaModel.findMany({
            'fields': ['id'],
            'condition': 'category_media_id in (%s)' % ', '.join(list_demand_cate)
        })

        return tup_same_category

    # 可以用 get_tag 代替
    # def media_tag_list(self, mediaId):
    #    # print "loadsuccess"
    #    tags = self.mediatagModel.findMany({
    #        'fields': ['tag_id'],
    #        'condition': 'media_id ="%s"' % mediaId
    #    })
    #
    #    tag_list = []
    #    for term in tags:
    #        tag_list.append(term.get('tag_id'))
    #
    #    return tag_list

    def check_wechat(self, strBiz):
        dicData = self.importModel('media_wechat').findOne({
            'condition': 'biz = "%s"' % strBiz
        })
        if dicData:
            return True
        else:
            return False

    def media_wechat_create(self, dicData):
        try:
            res = self.importModel('media_wechat').findOne({
                'condition': 'wechat_id="%s"' % dicData['wechat_id']
            })
            if res:
                return {'status': 601}
            mediaId = self.importModel('media').insert({
                'key': 'user_id, name, breif, avatar, create_time',
                'val': '%s, "%s", "%s", "%s", %s' % (dicData['user_id'], dicData['name'],
                                                     dicData['features'], dicData['avatar'], int(self.time.time()))
            })
            self.importModel('media_wechat').insert({
                'key': 'media_id, wechat_id, qrcode, biz, gh_id',
                'val': '%s, "%s", "%s", "%s", "%s"' % (mediaId, dicData['wechat_id'], dicData['qrcode'],
                                                       dicData['biz'], dicData['user_name'])
            })
            # 同步到媒体库
            self.sync_to_project(mediaId, dicData)
            # self.model.db.commit()
            return {'status': 200, 'data': {'media_id': mediaId}}
        except Exception, e:
            print e
            # self.model.db.rollback()
            return {'status': 500}

    def sync_to_project(self, media_id, dicData):
        try:
            res = self.importModel('project_media').findOne({
                'condition': 'id=%s' % media_id
            })
            if res:
                return
            self.importModel('project_media').insert({
                'key': 'id, user_id, name, breif, avatar, create_time',
                'val': '%s, %s, "%s", "%s", "%s", %s' % (
                    media_id, dicData['user_id'], dicData['name'],
                    dicData['features'], dicData['avatar'], int(self.time.time()))
            })
            self.importModel('project_media_wechat').insert({
                'key': 'media_id, wechat_id, qrcode, biz, gh_id',
                'val': '%s, "%s", "%s", "%s", "%s"' % (media_id, dicData['wechat_id'], dicData['qrcode'],
                                                       dicData['biz'], dicData['user_name'])
            })
        except Exception, e:
            print e

    def get_media(self, media_id):
        """ 获取一个自媒体信息

        @params media_id string 自媒体ID
        """

        dicMedia = self.mediaModel.findOne({
            'condition': 'id = "%s"' % media_id
        })
        if dicMedia:
            category_media_service = self.importService('category_media')

            dicMedia['avatar'] = self.getAvatarUrl(dicMedia['avatar'])
            dicMedia['original'] = self.importModel('media_wechat').findOne({
                'fields':['original'],
                'condition': 'media_id = "%s"' % media_id
            })['original']
            dicMedia['category'] = category_media_service.get_one_category(dicMedia['category_media_id'])
            dicMedia['tag'] = self.media_tag(dicMedia['id'])
            dicMedia['audience_gender_name'] = self.get_audience_gender(dicMedia['audience_gender'])
            dicMedia['area'] = ''
            if dicMedia['audience_province_id'] >=0:
                dicMedia['area'] = self.area_service.get_area(dicMedia['audience_province_id'], dicMedia['audience_city_id'],
                                                     dicMedia['audience_county_id'])
                #print dicMedia['area']
        return dicMedia

    def get_biz(self, media_id):
        dicData = self.mediawechatModel.findOne({
            'fields': ['biz'],
            'condition': 'media_id = %s' % media_id
        })
        # print dicData
        return dicData.get('biz')

    def media_edit(self, dicData):
        """ 修改自媒体信息
        """
        #print dicData
        if not dicData['id'] :
            return 401

        # 检查数据是否存在
        dicMedia = self.get_media(dicData['id'])
        if not dicMedia:
            return 601
        lisFields = []
        if dicData['audience_gender']:
            lisFields = ['audience_gender = %s' % dicData['audience_gender'],]
            self.mediaModel.update({
            'fields': lisFields,
            'condition': 'id = %s' % dicData['id']
            })
        if dicData['category_media_id']:
            lisFields.append('category_media_id = %s' % dicData['category_media_id'])
            self.mediaModel.update({
                'fields': lisFields,
                'condition': 'id = %s' % dicData['id']
            })

        if dicData['tag']:
            #print 111
            self.mediatagModel.delete({
                'condition': 'media_id = "%s"' % dicData['id']
            })
            #print 222
            self.mediatagModel.insert(dicData['id'], dicData['tag'])

        # 修改
        if dicData.get('audience_province_id'):
            #print 1
            lisFields = ['audience_province_id = %s' % dicData['audience_province_id'],]
            strCityId = 'NULL' if dicData['audience_city_id'] is '' else dicData['audience_city_id']
            strCountyId = 'NULL' if dicData['audience_county_id'] is '' else dicData['audience_county_id']
            lisFields.append('audience_city_id = %s' % strCityId)
            lisFields.append('audience_county_id = %s' % strCountyId)
            self.mediaModel.update({
                'fields': lisFields,
                'condition': 'id = %s' % dicData['id']
            })
        return 500
        #
        #
        # # tag
        # # 删除tag
        # self.mediatagModel.delete({
        #     'condition': 'media_id = "%s"' % dicData['id']
        # })
        # self.mediatagModel.insert(dicData['id'], dicData['tag'])

    def media_price_create(self, dic_data):
        """ 添加刊例价格
        """

        if not dic_data['id'] or not dic_data['attribute'] or not dic_data['price'] or not dic_data['user_id']:
            return 401

        try:
            dic_data['attribute'] = dic_data['attribute'].replace('"', '\\"')
            res = self.mediapriceModel.findOne({
                # 'condition': 'media_id = %s and price = %s and attr_value_info = \'%s\'' % (
                'condition': 'media_id = %s and attr_value_info = \'%s\' and status != 2' % (
                    dic_data['id'], dic_data['attribute'])
            })
            if res:
                return 601
            self.mediapriceModel.insert({
                'key': 'media_id, price, attr_value_info,status',
                'val': '"%s", "%s", "%s","%s"' % (dic_data['id'], dic_data['price'], dic_data['attribute'], 0)
            })
            # self.model.db.commit()
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def media_price_edit(self,dic_data):
        try:
            if not dic_data['id'] or not dic_data['media_price_id'] or not dic_data['price'] or not dic_data['user_id']:
                return 401
            res = self.mediapriceModel.findOne({
                    'condition': 'id = {mpid}'.format(mpid = dic_data['media_price_id'])
            })
            dic_data['attribute'] = res['attr_value_info']
            self.media_price_del(dic_data['media_price_id'])
            self.media_price_create(dic_data)
            return 200
        except Exception, e:
            print e
            return 500


    def media_attr_value_info(self, media_price_id):
        if isinstance(media_price_id, list):
            strCondition = 'id in (%s)' % ', '.join(media_price_id)
        else:
            strCondition = 'id = %s' % media_price_id
        tupData = self.mediapriceModel.findMany({
            'fields': ['id as media_price_id', 'price', 'attr_value_info'],
            'condition': strCondition
        })
        # 属性字典
        tupDataAttr = self.importModel('ad_attribute').findMany({})
        dicAttr = {str(int(i['id'])): i['name'] for i in tupDataAttr}
        # 属性值字典
        tupDataValue = self.importModel('ad_value').findMany({})
        dicValue = {str(int(i['id'])): i['name'] for i in tupDataValue}
        # 报价组合
        lisData = []
        for i in tupData:
            # 构建{attr_id: value_id, ...}
            # dicAttrValue = dict([j.split(':') for j in i['attr_value_info'].split(',')])
            lisAttrValue = self.json.loads(i['attr_value_info'])
            dicAttrValue = dict([(j['attr_id'], j['value']) for j in lisAttrValue])
            # 构建{attr_name: value_name, ...}
            dicAttrValueName = {dicAttr.get(k, ''): dicValue.get(dicAttrValue[k], '') for k in dicAttrValue}
            lisData.append(
                {'attr_value_info': dicAttrValueName, 'price': i['price'], 'media_price_id': i['media_price_id']})
        return lisData

    def media_price(self, str_media_id):
        """ 刊例列表

        @params str_media_id string 自媒体ID
        @params str_user_id string 用户ID
        """

        lis_attr_value_id = []
        dic_attr_value = {}

        tupData = self.mediapriceModel.findMany({
            'condition': 'media_id = "%s" and status != 2' % str_media_id,
            'order': 'id desc'
        })
        if tupData:
            for k, item in enumerate(tupData):
                lis_attr_value = self.json.loads(item['attr_value_info'])
                if lis_attr_value:
                    for v in lis_attr_value:
                        lis_attr_value_id.append(v['value'])
                tupData[k]['attr_value_info'] = lis_attr_value

        if lis_attr_value_id:
            str_attr_value_id = ','.join(lis_attr_value_id)
            tup_attr_value = self.advalueModel.findMany({
                'condition': 'id in (%s)' % str_attr_value_id
            })
            if tup_attr_value:
                for item in tup_attr_value:
                    dic_attr_value[item['id']] = item['name']

            for k, item in enumerate(tupData):
                lis_attr_value = []
                if item['attr_value_info']:
                    for v in item['attr_value_info']:
                        lis_attr_value.append(dic_attr_value[int(v['value'])])

                str_attr_value = '/'.join(lis_attr_value)
                tupData[k]['attr_value_info'] = str_attr_value

        return tupData

    def media_price_del(self, str_media_id):
        """ 删除刊例价格
        """

        if not str_media_id:
            return 401

        try:
            self.mediapriceModel.update({
                'fields': ['status =2'],
                'condition': 'id = "%s"' % str_media_id
            })
            # print 111
            # self.model.db.commit()
            return 200
        except Exception, e:
            print e
            # self.model.db.rollback()
            return 500

    def get_tag(self, str_media_id):
        """ 获取自媒体标签
        """

        tupTag = self.mediatagModel.findManyAs(
            'media_tag as mt',
            {
                'condition': 'mt.media_id = "%s"' % str_media_id,
                'join': 'tag as t ON (mt.tag_id = t.id)'
            }
        )

        return tupTag

    def get_attribute_value(self):
        """ 获取刊例属性
        """

        dic_attribute = {}

        attributeValueModel = self.importModel('ad_attribute_value')
        tup_attribute_value = attributeValueModel.findManyAs('ad_attribute_value as aav', {
            'fields': ['aa.id as attr_id', 'aa.name as attr_name', 'av.id as value_id', 'av.name as value_name'],
            'join': 'ad_attribute as aa ON (aav.attr_id = aa.id) LEFT JOIN ad_value as av ON (aav.value_id = av.id)'
        })
        if tup_attribute_value:
            for item in tup_attribute_value:
                if item['attr_id'] not in dic_attribute.keys():
                    dic_attribute[item['attr_id']] = {
                        'name': item['attr_name'],
                        'value': []
                    }

                dic_attribute[item['attr_id']]['value'].append(item)

        return dic_attribute
    def check_origin(self,str_media_id,strUrl):
        #print str_media_id
        #print strUrl

        from api.sogou import Crawler

        res = Crawler().crawl_with_url(strUrl)
        biz = res.get('biz')
        original = res.get('original')
        if not biz:
            return 402
        biz_ex = self.importService('media').get_biz(str_media_id)
        if biz == biz_ex and original == '1':
            self.importModel('media_wechat').update({
                'fields':['original = 1'],
                'condition':'media_id = {mid}'.format(mid = str_media_id)
            })
            return 200
        return 403

        # import api.origin as origin
        # biz_lis = origin.Eric_crawler().biz(strUrl)
        # if biz_lis is None:
        #     #print 222
        #     return 402
        # else:
        #     Biz = biz_lis[0]
        # #print Biz
        # Biz_data = self.importService('media').get_biz(str_media_id)
        # #print Biz_data
        # if Biz==Biz_data:
        #     origin_status = origin.Eric_crawler().origin(strUrl)
        #     if origin_status == 200:
        #         self.importModel('media_wechat').update({
        #             'fields':['original = 1'],
        #             'condition':'media_id = {mid}'.format(mid = str_media_id)
        #         })
        #         return 200
        # return 403

    @staticmethod
    def get_qrcode(qrcode):
        return 'http://7sbnkf.com2.z0.glb.qiniucdn.com/' + qrcode + '-avatar'
