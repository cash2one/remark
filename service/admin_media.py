# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 自媒体
        self.mediaModel = self.importModel('media')
        # 标签
        self.tagModel = self.importModel('tag')
        # 用户
        self.userModel = self.importModel('user')
        # 区域
        self.areaModel = self.importModel('area')
        # 平台
        self.platformModel = self.importModel('platform')
        # 分类(自媒体)
        self.categoryMediaModel = self.importModel('category_media')
        # 自媒体-分类
        self.mediaTagModel = self.importModel('media_tag')
        # 微信(自媒体)
        self.mediaWechatModel = self.importModel('media_wechat')
        # 自媒体-报价
        self.mediaPriceModel = self.importModel('media_price')
        # 自媒体刊例报价属性
        self.mediaAttrModel = self.importModel('ad_attribute')
        # 自媒体刊例报价属性值
        self.mediaValueModel = self.importModel('ad_value')
        # 自媒体状态名称
        self.mediaStatusLabel = {0: '正常', 1: '已注销', 2: '已禁用'}
        # 自媒体价值等级
        self.mediaValueLevelLabel = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}

    def index(self, intPage, intPageDataNum, intTimeStart, intTimeEnd, strSearch):
        '''
        :func: 获取自媒体简要信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param intTimeStart: 筛选的起始时间
        :param intTimeEnd: 筛选的结束时间
        :param strSearch: 搜索的内容
        '''
        # 当前页起始序号
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 筛选时间条件
        timeCondition = ''
        if intTimeStart != 0 and intTimeEnd != 0:
            timeCondition = 'm.create_time > {start} and m.create_time < {end}'.format(
                start=intTimeStart, end=intTimeEnd
            )
        elif intTimeEnd != 0:
            timeCondition = 'm.create_time < {end}'.format(end=intTimeEnd)
        elif intTimeStart != 0:
            timeCondition = 'm.create_time > {start}'.format(start=intTimeStart)
        # 搜索条件
        searchCondition = ''
        if strSearch and timeCondition:
            searchCondition = ' and m.name like \'%{search}%\''.format(search=strSearch)
        elif strSearch:
            searchCondition = 'm.name like \'%{search}%\''.format(search=strSearch)
        # 自媒体简要信息
        tupData, intRows = self.mediaModel.findPaginateAs(
            'media as m',
            {
                'fields': ['m.id', 'm.user_id', 'm.name', 'm.create_time', 'm.status', 'u.nickname','m.identify'],
                'join': 'user as u ON (m.user_id = u.id) LEFT JOIN media_wechat as mw ON (mw.media_id = m.id)',
                'condition': '{time}{search}'.format(time=timeCondition, search=searchCondition),
                'page': [intPage, intPageDataNum],
                'order': 'm.create_time desc'
            }
        )
        lis_data = list(tupData)
        # 数据格式化
        lisIndexInfo = []
        for idx, i in enumerate(lis_data):
            detail_data = self.detail(i['id']).get('dicData', {})
            price_info = detail_data.get('price', [])
            i['top_price'] = '-'
            #print price_info
            for item in price_info:
                if  u'\u591a\u56fe\u6587\u5934\u6761' in item['attr_value_info'].values():
                    i['top_price'] = item['price']
            #print detail_data
            i['idx'] = intDataNumStart + idx + 1
            i['status_label'] = self.mediaStatusLabel.get(i.get('status'), '-')
            i['create_time'] = self.formatTime(i.get('create_time', 0), '%Y-%m-%d')
            if i['identify'] == 1:
                i['identify'] = '已认证'
            else:
                i['identify'] = '-'
            i['category'] = detail_data.get('category')
            i['original'] = detail_data.get('original')
            i['top_avg_read_num'] = detail_data.get('top_avg_read_num')
            i['value_level_label'] = detail_data.get('value_level_label')
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def detail(self, intId):
        '''
        :func: 获取自媒体详细信息
        :param intId: 自媒体ID
        '''
        # print 111
        try:
            # 自媒体信息
            dicData = self.mediaModel.findOne({
                'condition': 'id = {id}'.format(id=intId)
            })
            # print  dicData
            if not dicData:
                return {'statusCode': 404}
            # 自媒体所属用户
            dicDataUser = self.userModel.findOne({
                'fields': ['nickname'],
                'condition': 'id = {uid}'.format(uid=dicData['user_id'])
            })
            # 自媒体平台
            dicDataPlatform = self.platformModel.findOne({
                'fields': ['name as platform'],
                'condition': 'id = {pid}'.format(pid=dicData['platform_id'])
            })
            # print 222
            # 自媒体分类
            dicDataCategory = {}
            if dicData['category_media_id']:
                dicDataCategory = self.categoryMediaModel.findOne({
                    'fields': ['name as category'],
                    'condition': 'id = {cid}'.format(cid=dicData['category_media_id'])
                })

            # 自媒体受众省
            if dicData['audience_province_id'] == 0:
                dicDataAudienceProvince = {'province': '全国性'}
            else:
                dicDataAudienceProvince = self.areaModel.findOne({
                    'fields': ['name as province'],
                    'condition': 'id = {aid}'.format(aid=dicData['audience_province_id'])
                })
            # 自媒体受众市
            # print 222
            if dicData['audience_city_id'] is None:
                dicDataAudienceCity = {'city': ''}
            else:
                dicDataAudienceCity = self.areaModel.findOne({
                    'fields': ['name as city'],
                    'condition': 'id = {aid}'.format(aid=dicData['audience_city_id'])
                })
            # 自媒体受众县
            if dicData['audience_county_id'] is None:
                dicDataAudienceCounty = {'county': ''}
            else:
                dicDataAudienceCounty = self.areaModel.findOne({
                    'fields': ['name as county'],
                    'condition': 'id = {aid}'.format(aid=dicData['audience_county_id'])
                })
            if dicData['identify'] == 1:
                dicData['identify'] = '已认证'
            else:
                dicData['identify'] = '-'
            # 微信(自媒体)
            dicDataWechat = self.mediaWechatModel.findOne({
                'fields': ['top_avg_read_num', 'top_three_avg_read_num','original','gh_id','wechat_id','qrcode'],
                'condition': 'media_id = {mid}'.format(mid=dicData['id'])
            })
            # print 333
            # 自媒体报价
            tupDataPrice = self.mediaPriceModel.findMany({
                'fields': ['attr_value_info', 'price'],
                'condition': 'media_id = {mid}'.format(mid=dicData['id'])
            })
            # 属性字典
            tupDataAttr = self.mediaAttrModel.findMany({})
            dicAttr = {str(int(i['id'])): i['name'] for i in tupDataAttr}
            # 属性值字典
            tupDataValue = self.mediaValueModel.findMany({})
            dicValue = {str(int(i['id'])): i['name'] for i in tupDataValue}
            # 报价组合
            lisDataPrice = []
            for i in tupDataPrice:
                # 构建{attr_id: value_id, ...}
                # dicAttrValue = dict([j.split(':') for j in i['attr_value_info'].split(',')])
                lisAttrValue = self.json.loads(i['attr_value_info'])
                dicAttrValue = dict([(j['attr_id'], j['value']) for j in lisAttrValue])
                # 构建{attr_name: value_name, ...}
                dicAttrValueName = {dicAttr.get(k, ''): dicValue.get(dicAttrValue[k], '') for k in dicAttrValue}
                lisDataPrice.append({'attr_value_info': dicAttrValueName, 'price': i['price']})
            # 自媒体标签
            tupDataTag = self.mediaTagModel.findManyAs(
                'media_tag as mt',
                {
                    'fields': ['t.id', 't.name'],
                    'join': 'tag as t ON (t.id = mt.tag_id)',
                    'condition': 'mt.media_id = {mid}'.format(mid=dicData['id'])
                }
            )
            if dicDataWechat['original'] ==1:
                dicData['original'] = '原创'
            else:
                dicData['original'] = '-'
            # 结果合并及格式化
            dicData['nickname'] = dicDataUser.get('nickname', '-')
            dicData['platform'] = dicDataPlatform.get('platform', '-')
            dicData['category'] = dicDataCategory.get('category', '-')
            #print dicData['category']
            dicData['province'] = dicDataAudienceProvince.get('province', '-')
            dicData['city'] = dicDataAudienceCity.get('city', '-')
            dicData['county'] = dicDataAudienceCounty.get('county', '-')
            dicData['top_avg_read_num'] = dicDataWechat.get('top_avg_read_num', '-')
            dicData['top_three_avg_read_num'] = dicDataWechat.get('top_three_avg_read_num', '-')
            if 'qrcode' in dicDataWechat:
                dicData['qrcode'] = '{host}{key}{suffix}'.format(
                    host=self.dicConfig['PIC']['HOST'], key=dicDataWechat['qrcode'], suffix='-avatar'
                )
            else:
                dicData['qrcode'] = ''
            if ('wechat_id' not in dicDataWechat) and ('gh_id' in dicDataWechat):
                dicData['wechat_id'] = dicDataWechat['gh_id']
            else:
                dicData['wechat_id'] = dicDataWechat['wechat_id']
            dicData['price'] = lisDataPrice
            dicData['tag'] = tupDataTag
            dicData['status_label'] = self.mediaStatusLabel.get(dicData.get('status'), '-')
            dicData['value_level_label'] = self.mediaValueLevelLabel.get(dicData['value_level'], '?')
            dicData['create_time'] = self.formatTime(dicData.get('create_time', 0), '%Y-%m-%d')
            dicData['avatar'] = '{host}{key}{suffix}'.format(
                host=self.dicConfig['PIC']['HOST'], key=dicData['avatar'], suffix='-avatar'
            )
            return {'statusCode': 200, 'dicData': dicData}
        except Exception, e:
            # print e
            return {'statusCode': 500}

    def ban(self, intId):
        '''
        :func: 禁用自媒体
        :param intId: 自媒体ID
        '''
        self.mediaModel.update({
            'fields': ['status = 2'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def unban(self, intId):
        '''
        :func: 取消禁用自媒体
        :param intId: 自媒体ID
        '''
        self.mediaModel.update({
            'fields': ['status = 0'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def updateName(self, intId, dicArgs):
        '''
        :func: 更新自媒体名称
        :param intId: 自媒体ID
        :param dicArgs: 参数字典
        '''
        if 'media_name' in dicArgs:
            strMediaName = dicArgs['media_name'][0]
            self.mediaModel.update({
                'fields': ['name = \'{name}\''.format(name=strMediaName)],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}
    def updateOriginal(self,intId,dicArgs):
        #print dicArgs
        if 'media_original' in dicArgs:
            strMediaOriginal = dicArgs['media_original'][0]
            #print strMediaOriginal
            self.mediaWechatModel.update({
                'fields': ['original = {ori}'.format(ori=strMediaOriginal)],
                'condition': 'media_id = {id}'.format(id=intId)
            })
            #print self.model.db.status
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}
    def updateValue(self,intId,dicArgs):
        #print dicArgs
        if 'media_value' in dicArgs:
            strMediaValue = dicArgs['media_value'][0]
            self.mediaModel.update({
                'fields': ['value_level = {val}'.format(val=strMediaValue)],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def updateCategory(self, intId, dicArgs):
        '''
        :func: 更新自媒体类别
        :param intId: 自媒体ID
        :param dicArgs: 参数字典
        '''
        if 'media_category' in dicArgs:
            strMediaCategory = dicArgs['media_category'][0]
            self.mediaModel.update({
                'fields': ['category_media_id = {mid}'.format(mid=strMediaCategory)],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def getCategory(self):
        '''
        :func: 获取行业分类列表
        '''
        tupData = self.categoryMediaModel.findMany({
            'fields': ['id', 'name']
        })
        return tupData

    def getTag(self, intId):
        '''
        :func: 获取标签列表
        '''
        tupData = self.tagModel.findMany({
            'fields': ['id', 'name']
        })
        # print tupData
        tupDataChecked = self.mediaTagModel.findManyAs(
            'media_tag as mt',
            {
                'fields': ['t.id', 't.name'],
                'join': 'tag as t ON (t.id = mt.tag_id)',
                'condition': 'mt.media_id = {mid}'.format(mid=intId)
            }
        )
        # print tupDataChecked
        checkedId = set([i['id'] for i in tupDataChecked])
        # print checkedId
        lisData = []
        for idx, i in enumerate(tupData):
            i['idx'] = idx + 1
            i['checked'] = 1 if i['id'] in checkedId else 0
            lisData.append(i)
        return lisData

    def updateTag(self, intId, dicArgs):
        '''
        :func: 更新自媒体标签
        :param intId: 自媒体ID
        :param dicArgs: 参数字典
        '''
        tagIdNew = set()
        if 'media_tag' in dicArgs:
            tagIdNew = set(dicArgs['media_tag'])
        tupData = self.mediaTagModel.findMany({
            'fields': ['tag_id'],
            'condition': 'media_id = {mid}'.format(mid=intId)
        })
        tagIdOld = set([str(i['tag_id']) for i in tupData])
        tagIdInsert = tagIdNew - tagIdOld
        tagIdDelete = tagIdOld - tagIdNew
        for did in tagIdDelete:
            self.mediaTagModel.delete({
                'condition': 'media_id = {mid} and tag_id = {tid}'.format(mid=intId, tid=did)
            })
        for iid in tagIdInsert:
            # self.mediaTagModel.insert({
            #     'key': 'media_id, tag_id',
            #     'val': '{mid}, {tid}'.format(mid=intId, tid=iid)
            # })
            self.mediaTagModel.insert(intId, iid)
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def updateAudienceGender(self, intId, dicArgs):
        '''
        :func: 更新自媒体受众性别
        :param intId: 自媒体ID
        :param dicArgs: 参数字典
        '''
        if 'media_audience_gender' in dicArgs:
            strMediaAudienceGender = dicArgs['media_audience_gender'][0]
            self.mediaModel.update({
                'fields': ['audience_gender = {ag}'.format(ag=strMediaAudienceGender)],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def getArea(self, parent_id):
        '''
        :func: 获取区域列表
        :param parent_id: 区域父ID
        '''
        tupData = self.areaModel.findMany({
            'fields': ['id', 'name'],
            'condition': 'parent = {pid}'.format(pid=parent_id)
        })
        return tupData

    def updateAudienceArea(self, intId, dicArgs):
        '''
        :func: 更新自媒体受众区域
        :param intId: 自媒体ID
        :param dicArgs: 参数字典
        '''
        if 'media_audience_province' in dicArgs and 'media_audience_city' in dicArgs and \
                'media_audience_county' in dicArgs:
            fields = []
            strProvince = dicArgs['media_audience_province'][0]
            strCity = dicArgs['media_audience_city'][0]
            strCounty = dicArgs['media_audience_county'][0]
            fields.append('audience_province_id = {aid}'.format(aid='0' if strProvince == '-1' else strProvince))
            fields.append('audience_city_id = {aid}'.format(aid='NULL' if strCity == '-1' else strCity))
            fields.append('audience_county_id = {aid}'.format(aid='NULL' if strCounty == '-1' else strCounty))
            self.mediaModel.update({
                'fields': fields,
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}
