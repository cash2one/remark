# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.wechatFriendModel = self.importModel('project_media_wechat_friend')
        self.mediaModel = self.importModel('project_media')
        self.mediaTagModel = self.importModel('project_media_tag')
        self.ad_feedbackModel = self.importModel('project_feedback')
        self.advertiserModel = self.importModel('project_advertiser')
        self.planModel = self.importModel('project_plan')
        self.plan_demand_model = self.importModel('project_plan_demand')
        self.mediaService = self.importService('media')
        self.plan_mediaModel = self.importModel('project_demand_media')
        self.demand_service = self.importService('demand')
        self.mediaCommonService = self.importService('media_common')

    def get_wechat_friend_page(self, dicData):
        listCondition = ['m.platform_id = 5']
        listJoin = []
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_tag mt on (m.id = mt.media_id)')
        if dicData['black_pr'] and dicData['black_pr'] != '-1':
            listCondition.append('m.black_pr = %s' % dicData['black_pr'])
        if dicData['comment'] and dicData['comment'] != '-1':
            listCondition.append('m.comment = %s' % dicData['comment'])
        if dicData['kol'] and dicData['kol'] != '-1':
            listCondition.append('m.kol = %s' % dicData['kol'])
        if dicData['ad'] and dicData['ad'] != '-1':
            listCondition.append('m.ad = %s' % dicData['ad'])
        if dicData['ad_type'] and dicData['ad_type'] != '-1':
            listCondition.append('m.ad_type like \'%{atp}%\''.format(atp=dicData['ad_type']))
        if dicData['worth'] and dicData['worth'] != '-1':
            listCondition.append('m.worth = %s' % dicData['worth'])
        if dicData['fans_num'] and dicData['fans_num'] != ',':
            fn = self.build_interval_condition('m.fans_num', dicData['fans_num'])
            if fn: listCondition.append(fn)
        if dicData['forward_price'] and dicData['forward_price'] != ',':
            fp = self.build_interval_condition('mw.forward_price', dicData['forward_price'])
            if fp: listCondition.append(fp)
        if dicData['other_price'] and dicData['other_price'] != ',':
            op = self.build_interval_condition('m.other_price', dicData['other_price'])
            if op: listCondition.append(op)
        if dicData['audience_gender'] and dicData['audience_gender'] != '-1':
            listCondition.append('m.audience_gender = %s' % dicData['audience_gender'])
        if dicData['audience_age']:
            listCondition.append('m.audience_age like \'%{age}%\''.format(age=dicData['audience_age']))
        if dicData['audience_career']:
            listCondition.append('m.audience_career like \'%{career}%\''.format(career=dicData['audience_career']))
        # 查询词
        if dicData['query']:
            dicField = {'1': 'name', '2': 'wechat_id', '3': 'biz', '4': 'brief',
                        '5': 'contact_phone', '6': 'contact_qq', '7': 'contact_wechat', '8': 'remark'}
            strField = dicData['field']
            strQuery = dicData['query']
            strCol = dicField[strField]
            # 搜索条件
            if strField == '2' or strField == '3':
                searchCondition = 'mw.{col} = \'{key}\''.format(col=strCol, key=strQuery)
            else:
                searchCondition = 'm.{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
            listCondition.append(searchCondition)
        listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_wechat_friend mw on (m.id = mw.media_id)')
        # 查询
        tupData, count = self.mediaModel.findPaginateAs(
            self.dicConfig['DB_PROJECT'] + '.media as m',
            {
                'condition': ' and '.join(listCondition),
                'join': ' join '.join(listJoin),
                'page': [dicData['page'], 10],
                'order': 'm.last_update_time desc'
            },
            cacheRow=True
        )
        # 数据格式化
        liswechat_friend= []
        if tupData:
            dic_wechat_friend = {}
            for k, item in enumerate(tupData, 1):
                if 'tag_id' in item:
                    item.pop('tag_id')
                item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
                dic_wechat_friend[item['id']] = item
            # print dic_wechat_friend
            liswechat_friend =  dic_wechat_friend.values()
            liswechat_friend.sort(key=lambda i:i['last_update_time'], reverse=True)
        # print liswechat_friend
        return {'wechat_friend': liswechat_friend,
                'count': count,
                'category': self.mediaCommonService.get_category_media(),
                'tag': self.mediaCommonService.get_tag()}

    def build_interval_condition(self, col, value):
        strCondition = ''
        start, end = value.split(',')
        if start and end:
            strCondition = '%s between %s and %s' % (col, float(start), float(end))
        elif start:
            strCondition = '%s >= %s' % (col, float(start))
        elif end:
            strCondition = '%s <= %s' % (col, float(end))
        return strCondition

    def get_wechat_friend(self, dicData):
        listCondition = []
        listJoin = []
        # 分类
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])

        # Tag
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_tag mt on (m.id = mt.media_id)')

        # # 媒体价值等级
        # if dicData['value_level']:
        #     listCondition.append('m.value_level in (%s)' % dicData['value_level'])

        # 受众性别
        if dicData['audience_gender']:
            listCondition.append('m.audience_gender in (%s)' % dicData['audience_gender'])

        # # 账号认证
        # if dicData['identify']:
        #     # 原认证判断
        #     # listCondition.append('m.identify in (%s)' % dicData['identify'])
        #     # 新认证判断
        #     idf = dicData['identify']
        #     if idf == '1':
        #         listCondition.append('m.identify is not NULL and m.identify != "" ')
        #     else:
        #         listCondition.append('(m.identify is NULL or m.identify = "")')

        # 是否原创
        if dicData['original']:
            listCondition.append('mw.original in (%s)' % dicData['original'])
        listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_wechat_friend mw on (m.id = mw.media_id)')

        # # 受众省份
        # if dicData['audience_province']:
        #     listCondition.append('m.audience_province = %s' % dicData['audience_province'])
        #
        # # 受众城市
        # if dicData['audience_city']:
        #     listCondition.append('m.audience_city = %s' % dicData['audience_city'])
        #
        # # 受众县
        # if dicData['audience_county']:
        #     listCondition.append('m.audience_county = %s' % dicData['audience_county'])

        # 查询词
        if dicData['query']:
            # listCondition.append('m.name like "%' + dicData['query'] + '%"')
            dicField = {'1': 'name', '2': 'wechat_friend_id', '3': 'biz', '4': 'brief'}
            strField = dicData['field']
            strQuery = dicData['query']
            strCol = dicField[strField]
            # 搜索条件
            if strField == '1' or strField == '4':
                searchCondition = 'm.{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
            else:
                searchCondition = 'mw.{col} = \'{key}\''.format(col=strCol, key=strQuery)
            listCondition.append(searchCondition)

        # 状态
        listCondition.append('m.status = 0')

        # 查询
        tupData = self.mediaModel.findPaginateAs(
            self.dicConfig['DB_PROJECT'] + '.media as m',
            {
                'condition': ' and '.join(listCondition),
                'join': ' join '.join(listJoin),
                'page': [dicData['page'], 10],
                'order': 'm.last_update_time desc'
            },
            cacheRow=True
        )
        # 数据格式化
        liswechat_friend, count = [], 0
        if tupData:
            wechat_friend, count = tupData
            dic_wechat_friend = {}
            for k, item in enumerate(wechat_friend):
                if 'tag_id' in item:
                    item.pop('tag_id')
                item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
                dic_wechat_friend[item['id']] = item
            liswechat_friend =  dic_wechat_friend.values()
            liswechat_friend.sort(key=lambda i:i['last_update_time'], reverse=True)
        return {'wechat_friend': liswechat_friend,
                'count': count,
                'category': self.importService('category_media').commonUse(),
                'tag': self.importService('tag').get_list()}

    def wechat_friend_detail(self, intId):
        dicMedia = self.mediaModel.findOne({
            'condition': 'id={id}'.format(id=intId)
        })
        dicMediaWechatFriend = self.wechatFriendModel.findOne({
            'condition': 'media_id={mid}'.format(mid=intId)
        })
        tupMediaTag = self.mediaTagModel.findMany({
            'condition': 'media_id={mid}'.format(mid=intId)
        })
        strTag = ','.join([str(i['tag_id']) for i in tupMediaTag])
        dicMediaWechatFriend.pop('id')
        dicMedia.update(dicMediaWechatFriend)
        dicMedia['create_time'] = self.formatTime(dicMedia['create_time'], '%Y-%m-%d')
        dicMedia['last_update_time'] = self.formatTime(dicMedia['last_update_time'], '%Y-%m-%d')
        dicMedia['category'] = self.category(dicMedia['category_media_id'])
        dicMedia['tag'] = self.tag(strTag)
        dicMedia['audience_gender'] = self.audience_gender(dicMedia['audience_gender'])
        dicMedia['audience_area'] = self.audience_area(
            dicMedia['audience_province_id'], dicMedia['audience_city_id'], dicMedia['audience_county_id'])
        dicMedia['audience_age'] = self.audience_age(dicMedia['audience_age'])
        dicMedia['audience_career'] = self.audience_career(dicMedia['audience_career'])
        dicMedia['ad_type'] = self.ad_type(dicMedia['ad_type'])
        dicMedia['role'] =  self.role(dicMedia['role'])
        dicMedia['black_pr'] = self.radio_format(dicMedia['black_pr'])
        dicMedia['can_afford_article'] = self.radio_format(dicMedia['can_afford_article'])
        dicMedia['comment'] = self.radio_format(dicMedia['comment'])
        dicMedia['award'] = self.radio_format(dicMedia['award'])
        dicMedia['kol'] = self.radio_format(dicMedia['kol'])
        dicMedia['ad'] = self.radio_format(dicMedia['ad'])
        dicMedia['station'] = self.radio_format(dicMedia['station'])
        dicMedia['association'] = self.radio_format(dicMedia['association'])
        dicMedia['worth'] = self.radio_format(dicMedia['worth'])
        dicMedia['src_type'] = self.src_type(dicMedia['src_type'])
        dicMedia['farm_level'] = self.farm_level(dicMedia['farm_level'])
        return dicMedia

    def wechat_friend_sale_result(self, intId):
        tupData = self.importModel('project_feedback').findManyAs(
            self.dicConfig['DB_PROJECT'] +'.feedback as f',
            {
                'fields':['f.*', 'dm.link as link', 'dm.money as money','m.name as media_name','pd.name as plan_demand_name'],
                'join': self.dicConfig['DB_PROJECT'] + '.media as m ON(f.media_id = m.id) LEFT JOIN ' +
                        self.dicConfig['DB_PROJECT'] + '.demand_media as dm ON(f.plan_demand_id = dm.plan_demand_id and f.media_id = dm.media_id) LEFT JOIN '+
                        self.dicConfig['DB_PROJECT'] + '.plan_demand as pd ON(f.plan_demand_id = pd.id)',
                'condition': 'f.media_id = %s' % intId,
                'order': 'id desc'
            }
        )
        for i, item in enumerate(tupData, 1):
            item['web_demand_name'] = '-'
            if item['demand_id']:
                demand_info = self.demand_service.detail(str(item['demand_id']))
                if demand_info:
                    item['web_demand_name'] = demand_info['title']
                else:
                    item['demand_id'] = 0

        return tupData

    def src_type(self, num):
        all = {0:'一道入驻', 1:'抓取数据', 2:'人工筛选'}
        return all.get(num, '-')

    def farm_level(self, num):
        all = {0:'-', 1:'无', 2:'轻度', 3:'严重'}
        return num, all.get(num, '-')

    def radio_format(self, num, option=2):
        if option == 3:
            return num, {0: '不限', 1:'是', 2:'否'}.get(num, '-')
        return num, {1:'是', 2:'否'}.get(num, '-')

    def role(self, num):
        return num, {1:'企业', 2:'个人'}.get(num, '-')

    def ad_type(self, ad_type):
        # print ad_type, type(ad_type)
        if ad_type == 'None' or ad_type == '0' or not ad_type:
            return {}
        all = {'1':'软广', '2':'硬广'}
        rtn = {i: all.get(i) for i in ad_type.split(',')}
        return rtn

    def update_wechat_friend_detail(self, dicArg):
        dicwechat_friend = {}
        if 'tag' in dicArg:
            tags = dicArg.pop('tag')
            lst_tag = tags.split(',') if tags else []
            media_id = dicArg['id']
            self.mediaTagModel.delete({'condition': 'media_id={mid}'.format(mid=media_id)})
            for tag_id in lst_tag:
                self.mediaTagModel.insert({'key': 'media_id, tag_id', 'val': '%s, %s' % (media_id, tag_id)})
        if 'forward_price' in dicArg:
            dicwechat_friend['forward_price'] = dicArg.pop('forward_price')
        mediaFields = []
        for k in dicArg:
            if k == 'id':
                continue
            if dicArg[k] is None:
                mediaFields.append('{k}={v}'.format(k=k, v='null'))
            else:
                mediaFields.append('{k}=\'{v}\''.format(k=k, v=dicArg[k]))
        mediaFields.append('last_update_time={ut}'.format(ut=int(self.time.time())))
        self.mediaModel.update({
            'fields': mediaFields,
            'condition': 'id={id}'.format(id=dicArg['id'])
        })
        if self.model.db.status != 200:
            return 500
        mediawechat_friendFields = []
        if dicwechat_friend:
            for k in dicwechat_friend:
                mediawechat_friendFields.append('{k}={v}'.format(k=k,v=dicwechat_friend[k]))
            self.wechatFriendModel.update({
                'fields': mediawechat_friendFields,
                'condition': 'media_id={id}'.format(id=dicArg['id'])
            })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_all_category(self):
        rtn = self.importModel('category_media').findMany({})
        return rtn

    def get_all_tag(self):
        rtn = self.importModel('tag').findMany({})
        return rtn

    def get_all_area(self):
        rtn = self.importModel('area').findMany({})
        return rtn

    def category(self, num):
        if num is None:
            return
        dicData = self.importModel('category_media').findOne({
            'condition': 'id = {id}'.format(id=num)
        })
        return {dicData.get('id', ''): dicData.get('name', '')}

    def tag(self, tag):
        if tag == 'None' or tag is None or tag == '':
            return {}
        tupData = self.importModel('tag').findMany({
            'condition': 'id in ({tag})'.format(tag=tag)
        })
        rtn = {str(i['id']): i['name'] for i in tupData}
        return rtn

    def original(self, num):
        return '原创' if num == 1 else '-'

    def audience_gender(self, num):
        return num, {0:'不限', 1:'偏女性', 2:'偏男性'}.get(num, '-')

    def audience_area(self, province, city, county):
        if province == 0:
            return '全国性'
        else:
            area = self.importService('area').get_area(province, city, county)
            return area

    def audience_age(self, age):
        if age == '0' or age is None or age == '':
            return {}
        all = {'1':'70后', '2':'80后', '3':'85后', '4':'90后', '5':'95后', '6':'其它'}
        rtn = {i: all.get(i) for i in age.split(',')}
        # print rtn
        return rtn

    def audience_career(self, career):
        if career == '0' or career is None or career == '':
            return {}
        all =  {'1':'工薪阶层', '2':'白领', '3':'高管', '4':'创业者',
                '5':'企事业单位', '6':'国企', '7':'公职人员', '8':'自由职业者'}
        rtn = {i: all.get(i) for i in career.split(',')}
        return rtn

    def check_biz(self, biz):
        res = self.wechatFriendModel.findOne({
            'condition': 'biz="%s"' % biz
        })
        if res:
            return 601
        return 200

    def check_biz_with_id(self, mid, biz):
        res = self.wechatFriendModel.findOne({
            'condition': 'biz="%s" and media_id=%s' % (biz, mid)
        })
        if res:
            return 200
        return 601

    def follow(self, mid, uid, remark):
        follow_model = self.importModel('project_media_follow')
        res = self.check_follow(mid, uid)
        if res:
            follow_model.delete({
                'condition': 'user_id=%s and media_id=%s' % (uid, mid)
            })
            follow = 0
        else:
            follow_model.insert({
                'key': 'user_id, media_id, remark, create_time',
                'val': '%s, %s, "%s", %s' % (uid, mid, remark, int(self.time.time()))
            })
            follow = 1
        if self.model.db.status != 200:
            return 500, {}
        return 200, {'follow': follow}


    def check_follow(self, mid, uid):
        res = self.importModel('project_media_follow').findOne({
            'condition': 'user_id=%s and media_id=%s' % (uid, mid)
        })
        return res

    def create_wechat_friend(self, dicData):
        now = int(self.time.time())
        mediaId = self.mediaModel.insert({
            'key': 'user_id, name, brief, avatar, platform_id, src_type, create_time, last_update_time',
            'val': '%s, "%s", "%s", "%s", %s, %s, %s, %s' % (
                0, dicData['name'], dicData['brief'], dicData['avatar'], 5, 2, now, now)
        })
        self.wechatFriendModel.insert({
            'key': 'media_id, wechat_id, forward_price',
            'val': '%s, "%s", %s' % (mediaId, dicData['wechat_id'], dicData['forward_price'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_wechat_friend_base(self, dicData):
        now = int(self.time.time())
        self.mediaModel.update({
            'fields': ['name=\'{name}\''.format(name=dicData['name']),
                       'brief=\'{brief}\''.format(brief=dicData['brief']),
                       'avatar=\'{avatar}\''.format(avatar=dicData['avatar']),
                       'last_update_time={ut}'.format(ut=now),
                       ],
            'condition': 'id={id}'.format(id=dicData['id'])
        })
        self.wechatFriendModel.update({
            'fields': ['wechat_id=\'{wid}\''.format(wid=dicData['wechat_id'])],
            'condition': 'media_id={id}'.format(id=dicData['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_wechat_friend(self, strId, strGender, strOriginal, strAd, strKol):
        self.mediaModel.update({
            'fields': ['audience_gender={ag}'.format(ag=strGender),
                       'ad={ad}'.format(ad=strAd),
                       'kol={kol}'.format(kol=strKol)],
            'condition': 'id={id}'.format(id=strId)
        })
        self.wechatFriendModel.update({
            'fields': ['original={og}'.format(og=strOriginal),],
            'condition': 'media_id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_wechat_friend(self, intPage, intPageDataNum, strField, strQuery):
        dicField = {'1': 'name', '2': 'wechat_friend_id', '3': 'biz', '4': 'brief'}
        strCol = dicField[strField]
        # 搜索条件
        if strField == '1' or strField == '4':
            if strField== '4' and len(strQuery.decode("u8")) >= 4:
                searchCondition = 'match ({col}) against (\'{key}\')'.format(col=strCol, key=strQuery)
            else:
                searchCondition = '{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
        else:
            searchCondition = '{col} = \'{key}\''.format(col=strCol, key=strQuery)

        tupData, intRows = self.wechatFriendModel.findPaginate({
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum]
        })
        return tupData, intRows

    def update_wechat_friend(self, strId, strOriginal, strAd, strKol):
        self.wechatFriendModel.update({
            'fields': ['original={og}'.format(og=strOriginal),
                       'ad={ad}'.format(ad=strAd),
                       'kol={kol}'.format(kol=strKol)],
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

