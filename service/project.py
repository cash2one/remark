# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    lis_status = ['已结束','准备中','进行中']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.wechatModel = self.importModel('wechat')
        self.mediaModel = self.importModel('project_media')
        self.mediaWechatModel = self.importModel('project_media_wechat')
        self.ad_feedbackModel = self.importModel('project_ad_feedback')
        self.advertiserModel = self.importModel('project_advertiser')
        self.planModel = self.importModel('project_plan')
        self.plan_demand_model = self.importModel('project_ad_plan_demand')
        self.mediaService = self.importService('media')
        self.plan_mediaModel = self.importModel('project_ad_plan_media')
        # self.mediaWechatModel = self.importModel('media_wechat')

    def get_wechat(self, dicData):
        listCondition = []
        listJoin = []

        # 分类
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])

        # Tag
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append('media_tag mt on (m.id = mt.media_id)')

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
        listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_wechat mw on (m.id = mw.media_id)')

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
            # listCondition.append('m.name like "%' + dicData['query'] + '%"')
            dicField = {'1': 'name', '2': 'wechat_id', '3': 'biz', '4': 'brief'}
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
            }
        )

        # 数据格式化
        if tupData:
            area_service = self.importService('area')
            for k, item in enumerate(tupData[0]):
                item['category'] = self.mediaService.media_category_name(str(item['id']))
                if not item['category']:
                    item['category'] = '不限'
                item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
                item['tag'] = self.mediaService.media_tag(str(item['id']))

                item['area'] = area_service.get_area(item['audience_province_id'], item['audience_city_id'],
                                                     item['audience_county_id'])
                item['value_level'] = self.mediaService.get_value_level(item['value_level'])
                # item['audience_gender'] = self.mediaService.get_audience_gender(item['audience_gender'])

        return {'wechat': tupData[0],
                'count': tupData[1],
                'category': self.importService('category_media').commonUse(),
                'tag': self.importService('tag').get_list()}

    def wechat_detail(self, intId):
        dicMedia = self.mediaModel.findOne({
            'condition': 'id={id}'.format(id=intId)
        })
        dicMediaWechat = self.mediaWechatModel.findOne({
            'condition': 'media_id={mid}'.format(mid=intId)
        })
        dicMediaWechat.pop('id')
        dicMedia.update(dicMediaWechat)
        dicMedia['create_time'] = self.formatTime(dicMedia['create_time'], '%Y-%m-%d')
        dicMedia['last_update_time'] = self.formatTime(dicMedia['last_update_time'], '%Y-%m-%d')
        dicMedia['category'] = self.category(dicMedia['category_media_id'])
        dicMedia['tag'] = self.tag(dicMedia['tag'])
        dicMedia['original_label'] = self.original(dicMedia['original'])
        dicMedia['audience_gender_label'] = self.audience_gender(dicMedia['audience_gender'])
        dicMedia['audience_area'] = self.audience_area(
            dicMedia['audience_province_id'], dicMedia['audience_city_id'], dicMedia['audience_county_id'])
        dicMedia['audience_age'] = self.audience_age(dicMedia['audience_age'])
        dicMedia['audience_career'] = self.audience_career(dicMedia['audience_career'])
        dicMedia['audience_degree'] = self.audience_degree(dicMedia['audience_degree'])
        dicMedia['audience_income'] = self.audience_income(dicMedia['audience_income'])
        dicMedia['ad_type'] = self.ad_type(dicMedia['ad_type'])
        dicMedia['role'] =  self.role(dicMedia['role'])
        dicMedia['can_original'] = self.radio_format(dicMedia['can_original'])
        dicMedia['comment'] = self.radio_format(dicMedia['comment'])
        dicMedia['award'] = self.radio_format(dicMedia['award'])
        dicMedia['kol'] = self.radio_format(dicMedia['kol'])
        dicMedia['ad'] = self.radio_format(dicMedia['ad'])
        dicMedia['station'] = self.radio_format(dicMedia['station'])
        dicMedia['worth'] = self.radio_format(dicMedia['worth'])
        return dicMedia

    def radio_format(self, num, option=2):
        if option == 3:
            return {0: '不限', 1:'是', 2:'否'}.get(num, '-')
        return {0: '-', 1:'是', 2:'否'}.get(num, '-')

    def role(self, num):
        return {0:'-', 1:'企业', 2:'个人'}.get(num, '-')

    def ad_type(self, ad_type):
        if ad_type == 'None' or ad_type is None:
            return
        all = {'1':'软广', '2':'硬广'}
        rtn = {i: all.get(i) for i in ad_type.split(',')}
        return rtn

    def update_wechat_detail(self, dicArg):
        dicWechat = {}
        if 'original' in dicArg:
            dicWechat['original'] = dicArg.pop('original')
        if 'top_avg_read_num' in dicArg:
            dicWechat['top_avg_read_num'] = dicArg.pop('top_avg_read_num')
        if 'top_three_avg_read_num' in dicArg:
            dicWechat['top_three_avg_read_num'] = dicArg.pop('top_three_avg_read_num')
        if 'like_num' in dicArg:
            dicWechat['like_num'] = dicArg.pop('like_num')
        mediaFields = []
        for k in dicArg:
            if k == 'id':
                continue
            mediaFields.append('{k}=\'{v}\''.format(k=k, v=dicArg[k]))
        self.mediaModel.update({
            'fields': mediaFields,
            'condition': 'id={id}'.format(id=dicArg['id'])
        })
        if self.model.db.status != 200:
            return 500
        mediaWechatFields = []
        if dicWechat:
            for k in dicWechat:
                mediaWechatFields.append('{k}={v}'.format(k=k,v=dicWechat[k]))
            self.mediaWechatModel.update({
                'fields': mediaWechatFields,
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
        if tag is None:
            return
        tupData = self.importModel('tag').findMany({
            'condition': 'id in ({tag})'.format(tag=tag)
        })
        rtn = {str(i['id']): i['name'] for i in tupData}
        return rtn

    def original(self, num):
        return '原创' if num == 1 else '-'

    def audience_gender(self, num):
        return {0:'不限', 1:'偏女性', 2:'偏男性'}.get(num, '-')

    def audience_area(self, province, city, county):
        if province == 0:
            return '全国性'
        else:
            # TODO
            area = self.importService('area').get_area(province, city, county)
            return area

    def audience_age(self, age):
        if age is None:
            return
        all = {'1':'70后', '2':'80后', '3':'85后', '4':'90后', '5':'95后', '6':'其他'}
        rtn = {i: all.get(i) for i in age.split(',')}
        return rtn

    def audience_career(self, career):
        if career is None:
            return
        all =  {'1':'工薪阶层', '2':'白领', '3':'高管', '4':'创业者',
                '5':'企事业单位', '6':'国企', '7':'公职人员', '8':'自由职业者'}
        rtn = {i: all.get(i) for i in career.split(',')}
        return rtn

    def audience_degree(self, degree):
        if degree is None:
            return
        all = {'1':'高中以下', '2':'高中', '3':'大专', '4':'本科', '5':'研究生', '6':'研究生以上'}
        rtn = {i: all.get(i) for i in degree.split(',')}
        return rtn

    def audience_income(self, income):
        if income is None:
            return
        all = {'1':'5万以下', '2':'5万-10万', '3':'10万-20万', '4':'20万以上'}
        rtn = {i: all.get(i) for i in income.split(',')}
        return rtn

    def create_wechat(self, dicData):
        res = self.mediaWechatModel.findOne({
            'condition': 'biz="%s"' % dicData['biz']
        })
        if res:
            return 601
        mediaId = self.mediaModel.insert({
            'key': 'user_id, name, brief, avatar, src_type, create_time',
            'val': '%s, "%s", "%s", "%s", %s, %s' % (0, dicData['name'], dicData['features'], dicData['avatar'],
                                                     2, int(self.time.time()))
        })
        self.mediaWechatModel.insert({
            'key': 'media_id, wechat_id, qrcode, biz, gh_id',
            'val': '%s, "%s", "%s", "%s", "%s"' % (mediaId, dicData['wechat_id'], dicData['qrcode'],
                                                   dicData['biz'], dicData['user_name'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_wechat(self, strId, strGender, strOriginal, strAd, strKol):
        self.mediaModel.update({
            'fields': ['audience_gender={ag}'.format(ag=strGender),
                       'ad={ad}'.format(ad=strAd),
                       'kol={kol}'.format(kol=strKol)],
            'condition': 'id={id}'.format(id=strId)
        })
        self.mediaWechatModel.update({
            'fields': ['original={og}'.format(og=strOriginal),],
            'condition': 'media_id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_category_media(self):
        return self.importModel('category_media').findMany({})

    def get_tag(self):
        return self.importModel('tag').findMany({})

    def get_wechat(self, intPage, intPageDataNum, strField, strQuery):
        dicField = {'1': 'name', '2': 'wechat_id', '3': 'biz', '4': 'brief'}
        strCol = dicField[strField]
        # 搜索条件
        if strField == '1' or strField == '4':
            if strField== '4' and len(strQuery.decode("u8")) >= 4:
                searchCondition = 'match ({col}) against (\'{key}\')'.format(col=strCol, key=strQuery)
            else:
                searchCondition = '{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
        else:
            searchCondition = '{col} = \'{key}\''.format(col=strCol, key=strQuery)

        tupData, intRows = self.wechatModel.findPaginate({
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum]
        })
        # media_ids = [str(i['media_id']) for i in tupData]
        # dicAvatar = {}
        # if media_ids:
        #     tupDataMedia = self.mediaModel.findMany({
        #         'fields': ['id, avatar'],
        #         'condition': 'id in ({ids})'.format(ids=','.join(media_ids))
        #     })
        #     dicAvatar = {i['id']:i['avatar'] for i in tupDataMedia}
        # for j in tupData:
        #     strKey = dicAvatar.get(j['media_id'], '')
        #     if strKey:
        #         j['avatar'] = '{host}{key}{tp}'.format(host=self.dicConfig['PIC']['HOST'], key=strKey, tp='-avatar')
        #     else:
        #         j['avatar'] = ''
        return tupData, intRows

    def update_wechat(self, strId, strOriginal, strAd, strKol):
        self.wechatModel.update({
            'fields': ['original={og}'.format(og=strOriginal),
                       'ad={ad}'.format(ad=strAd),
                       'kol={kol}'.format(kol=strKol)],
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_ad_feedback(self, intPage, intPageDataNum):
        tupData, intRows = self.ad_feedbackModel.findPaginate({
            'page': [intPage, intPageDataNum]
        })
        for idx, i in enumerate(tupData, 1):
            i['idx'] = (intPage - 1) * intPageDataNum + idx
        return tupData, intRows

    def create_ad_feedback(self, dicArgs):
        self.ad_feedbackModel.insert({
            'key': 'media_id, demand_id, ad_user_id, url, investment, signup_num, rol, last_update_time, create_time',
            'val': '{mid}, {did}, {auid}, {url}, {inv}, {num}, {rol}, {ut}, {ct}'.format(
                mid=dicArgs['media_id'], did=dicArgs['demand_id'], auid=dicArgs['ad_user_id'],
                url=dicArgs['url'] if dicArgs['url'] else 'NULL', inv=dicArgs['investment'], num=dicArgs['signup_num'], rol=dicArgs['rol'],
                ut=int(self.time.time()), ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_ad_feedback(self, dicArgs):
        self.ad_feedbackModel.update({
            'fields': ['media_id={mid}'.format(mid=dicArgs['media_id']),
                       'demand_id={did}'.format(did=dicArgs['demand_id']),
                       'ad_user_id={auid}'.format(auid=dicArgs['ad_user_id']),
                       'url="{url}"'.format(url=dicArgs['url'] if dicArgs['url'] else 'NULL'),
                       'investment={inv}'.format(inv=dicArgs['investment']),
                       'signup_num={num}'.format(num=dicArgs['signup_num']),
                       'rol={rol}'.format(rol=dicArgs['rol']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_ad_feedback(self, strId):
        self.ad_feedbackModel.delete({
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_advertiser(self, intPage, intPageDataNum):
        tupData, intRows = self.advertiserModel.findPaginate({
            'page': [intPage, intPageDataNum]
        })
        for idx, i in enumerate(tupData, 1):
            i['idx'] = (intPage - 1) * intPageDataNum + idx
        return tupData, intRows

    def create_advertiser(self, dicArgs):
        self.advertiserModel.insert({
            'key': 'company, contact_person, contact_phone, product_info, audience_info, last_update_time, create_time',
            'val': '\'{comp}\', \'{cps}\', \'{cpn}\', \'{pi}\', \'{ai}\', {ut}, {ct}'.format(
                comp=dicArgs['company'], cps=dicArgs['contact_person'], cpn=dicArgs['contact_phone'],
                pi=dicArgs['product_info'], ai=dicArgs['audience_info'],
                ut=int(self.time.time()), ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_advertiser(self, dicArgs):
        self.advertiserModel.update({
            'fields': ['company=\'{comp}\''.format(comp=dicArgs['company']),
                       'contact_person=\'{cps}\''.format(cps=dicArgs['contact_person']),
                       'contact_phone=\'{cpn}\''.format(cpn=dicArgs['contact_phone']),
                       'product_info=\'{pi}\''.format(pi=dicArgs['product_info']),
                       'audience_info=\'{ai}\''.format(ai=dicArgs['audience_info']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_advertiser(self, strId):
        self.advertiserModel.delete({
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def advertiser_detail(self, strId):
        dicAd = self.advertiserModel.findOne({
            'condition': 'id = {id}'.format(id=strId)
        })
        return dicAd

    def advertiser_plan(self, strAdId):
        tupPlan = self.planModel.findMany({
            'condition': 'advertiser_id={ad_id}'.format(ad_id=strAdId)
        })
        return tupPlan

    def get_plan(self, intPage, intPageDataNum):
        tupData, intRows = self.planModel.findPaginateAs(self.dicConfig['DB_PROJECT'] +'.plan as p',{
            'fields': ['p.*','a.company'],
            'page': [intPage, intPageDataNum],
            'join':self.dicConfig['DB_PROJECT'] +'.advertiser as a ON(a.id = p.advertiser_id)'
        })
        #print  tupData
        for idx, i in enumerate(tupData, 1):
            i['idx'] = (intPage - 1) * intPageDataNum + idx
        return tupData, intRows

    def create_plan(self, dicArgs):
        #print 111
        self.planModel.insert({
            'key': 'advertiser_id, title, time_begin, time_end, money, status, last_update_time, create_time',
            'val': '{ad_id}, \'{tt}\', {tbg}, {ted}, {money}, {status}, {ut}, {ct}'.format(
                ad_id=dicArgs['advertiser_id'], tt=dicArgs['title'], tbg=dicArgs['time_begin'], ted=dicArgs['time_end'],
                money=dicArgs['money'], status=1, ut=int(self.time.time()), ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_plan(self, dicArgs):
        self.planModel.update({
            'fields': ['advertiser_id={ad_id}'.format(ad_id=dicArgs['advertiser_id']),
                       'title=\'{tt}\''.format(tt=dicArgs['title']),
                       'time_begin={tbg}'.format(tbg=dicArgs['time_begin']),
                       'time_end={ted}'.format(ted=dicArgs['time_end']),
                       'money={money}'.format(money=dicArgs['money']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_plan(self, strId):
        self.planModel.delete({
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_one_plan(self,pid):
        dic_data = self.planModel.findOneAs(self.dicConfig['DB_PROJECT'] +'.ad_plan as p',{
                'fields':['p.*','a.company'],
                'condition':'p.id={id}'.format(id=pid),
                'join':self.dicConfig['DB_PROJECT'] +'.advertiser as a ON(a.id = p.advertiser_id)'
        })

        dic_data['time_begin'] = self.formatTime(dic_data['time_begin'], '%Y-%m-%d')
        dic_data['time_end'] = self.formatTime(dic_data['time_end'], '%Y-%m-%d')
        if dic_data['status'] not in [0,1,2]: dic_data['status'] =  0
        dic_data['status'] = self.lis_status[dic_data['status']]
        return dic_data
        
    #####################################################################################
    lis_demand_status = ['未下单', '已下单']
    def get_plan_demand(self, intPage, intPageDataNum):
        tupData, intRows = self.plan_demand_model.findPaginate({
            'page': [intPage, intPageDataNum]
        })

        return tupData, intRows

    def create_demand(self, dicArgs):
        create_time = int(self.time.time())
        self.plan_demand_model.insert({
            'key': 'plan_id, name, money, description, status, last_update_time, create_time',
            'val': "%s, '%s', %s, '%s', 0, %s, %s" % (dicArgs['plan_id'], dicArgs['name'], int(dicArgs['money']), dicArgs['description'], create_time, create_time)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_one_demand(self, pid):
        dic_data = self.plan_demand_model.findOne({
            'condition' : 'id=%s' % (pid)
        })
        #if dic_data:
        #    dic_data['status'] = self.lis_demand_status[dic_data['status']]
        return dic_data

    def update_demand(self, dicArgs):
        self.plan_demand_model.update({
            'fields': ['plan_id=%s' % (dicArgs['plan_id']),
                       'name=\'%s\'' % (dicArgs['name']),
                       'description=\'%s\'' % (dicArgs['description']),
                       'demand_id=%s' % (dicArgs['demand_id']),
                       'money=%s' % (dicArgs['money']),
                       'status=%s' % (dicArgs['status']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200
        
    def create_potential(self, demand_id, plan_id, media_id, description):
        create_time = int(self.time.time())
        self.plan_mediaModel.insert({
            'key': 'plan_id, plan_demand_id, media_id, description, status, last_update_time, create_time',
            'val': '%s, %s, %s, %s, 0, %s, %s' % (
                plan_id, demand_id, media_id, description, create_time, create_time
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_potential(self, id, plan_demand_id, description, status):
        self.plan_mediaModel.update({
            #'fields': ['status=%s' % (status), 'description=%s' % (description)],
            'fields': ['status=%s' % (status)],
            'condition':'plan_demand_id = %s and id=%s' %(plan_demand_id, id)
        })
        if self.model.db.status != 200:
            return 500
        return 200
        
    def get_plan_demand_media(self, demand_id):
        original_name =['-','原创']
        kol_name = ['-','是']
        gender_name = ['不限','偏女性','偏男性']
        tup_data = self.plan_mediaModel.findManyAs(self.dicConfig['DB_PROJECT'] +'.plan_media as pm',{
            'fields':['pm.id as id, pm.description','pm.status','pm.plan_demand_id as plan_demand_id','pm.last_update_time','m.identify','m.name','m.kol','mw.original','mw.top_avg_read_num','m.id','m.audience_gender'],
            'condition':'pm.plan_demand_id=%s' % (demand_id),
            'join':self.dicConfig['DB_PROJECT'] +'.media as m ON(m.id = pm.media_id) Left JOIN '+self.dicConfig['DB_PROJECT']+'.media_wechat as mw ON(pm.media_id = mw.media_id)'
        })

        for item in tup_data:
            item['original'] = original_name[item['original']]
            item['kol'] = kol_name[item['kol']]
            item['audience_gender'] = gender_name[item['audience_gender']]
            item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
            if not item['identify'] :
                item['identify'] = '否'
        return tup_data