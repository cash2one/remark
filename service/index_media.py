# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 首页自媒体
        self.mediaIndexModel = self.importModel('index_media')

        # 微信自媒体
        self.mediaWechatModel = self.importModel('media_wechat')

        # 自媒体-报价
        self.mediaPriceModel = self.importModel('media_price')
        self.mediaModel = self.importModel('media')
        self.mediaCategoryModel = self.importModel('media_category')
        self.mediaTagModel = self.importModel('media_tag')
        self.tagModel = self.importModel('tag')

    def query(self, limit=None):
        """
        :func: 首页自媒体数据
        """
        # level
        dicLevel = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        dicArg = {
            'fields': ['xm.*', 'm.name', 'm.avatar', 'm.value_level', 'mw.original'],
            'join': 'media as m ON (m.id = xm.media_id) left join media_wechat as mw on (xm.media_id = mw.media_id)',
            'order': 'xm.sort asc'
        }
        if limit is not None:
            dicArg['limit'] = ['0', str(limit)]
        tupData = self.mediaIndexModel.findManyAs('index_media as xm', dicArg)
        lisMediaIds = [int(i['media_id']) for i in tupData]
        length = len(lisMediaIds)
        if length == 0:
            return []
        elif length == 1:
            strCondition = 'media_id = {ids}'.format(ids=lisMediaIds[0])
        else:
            strCondition = 'media_id in {ids}'.format(ids=str(tuple(lisMediaIds)))
        # 获取微信公众号阅读数
        tupWechatData = self.mediaWechatModel.findMany({
            'fields': ['media_id', 'top_avg_read_num', 'top_three_avg_read_num'],
            'condition': strCondition
        })
        dicWechatData = {i['media_id']: (i['top_avg_read_num'], i['top_three_avg_read_num']) for i in tupWechatData}
        # 自媒体报价
        tupDataPrice = self.mediaPriceModel.findMany({
            'fields': ['attr_value_info', 'price', 'media_id'],
            'condition': strCondition
        })
        # 获取行业和标签 by eric

        # print tupData
        for item in tupData:
            strMediaId = item['media_id']
            tupCategoryId = self.mediaModel.findOne({
                'fields': ['category_media_id'],
                'condition': 'id = "%s"' % strMediaId
            })
            # print tupCategoryId
            if 'category_media_id' in tupCategoryId:
                categoryId = tupCategoryId['category_media_id']
                tupCategoryName = self.mediaCategoryModel.findMany({
                    'fields': ['name'],
                    'condition': 'id = "%s"' % categoryId
                })
                categoryName = ""
                if tupCategoryName:
                    categoryName = tupCategoryName[0]['name']
                item['category_name'] = categoryName
                tupTagId = self.mediaTagModel.findMany({
                    'fields': ['tag_id'],
                    'condition': 'media_id = "%s"' % strMediaId
                })
            # print tupTagId
            item['tag_name'] = []
            for n, item2 in enumerate(tupTagId):
                tagId = tupTagId[n]['tag_id']
                tupTagName = self.tagModel.findOne({
                    'fields': ['name'],
                    'condition': 'id = "%s"' % tagId
                })
                if tupTagName:
                    tagName = tupTagName['name']
                    if tagName:
                        item['tag_name'].append(tagName)
        # print tupData

        # # 属性字典
        # tupDataAttr = self.mediaAttrModel.findMany({})
        # dicAttr = {str(int(i['id'])): i['name'] for i in tupDataAttr}
        # # 属性值字典
        # tupDataValue = self.mediaValueModel.findMany({})
        # dicValue = {str(int(i['id'])): i['name'] for i in tupDataValue}
        # # 报价组合
        # lisDataPrice = []
        # for i in tupDataPrice:
        #     # 构建{attr_id: value_id, ...}
        #     dicAttrValue = dict([j.split(':') for j in i['attr_value_info'].split(',')])
        #     # 构建{attr_name: value_name, ...}
        #     dicAttrValueName = {dicAttr.get(k, ''): dicValue.get(dicAttrValue[k], '') for k in dicAttrValue}
        #     lisDataPrice.append({'attr_value_info': dicAttrValueName, 'price': i['price']})
        #
        # 以最高报价作为头条报价
        dicTopPrice = {}
        for k in tupDataPrice:
            strMediaId = k['media_id']
            intPrice = k['price']
            dicTopPrice.setdefault(strMediaId, 0)
            if intPrice > dicTopPrice[strMediaId]:
                dicTopPrice[strMediaId] = intPrice
        # 合并结果 数据格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            strMediaId = i['media_id']
            if strMediaId in dicWechatData:
                i['top_avg_read_num'] = dicWechatData[strMediaId][0]
                i['top_three_avg_read_num'] = dicWechatData[strMediaId][1]
            else:
                i['top_avg_read_num'] = 0
                i['top_three_avg_read_num'] = 0
            i['top_price'] = dicTopPrice.get(strMediaId, 0)
            i['idx'] = idx + 1
            i['value_level'] = dicLevel.get(i['value_level'], '?')
            i['avatar'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], i['avatar'], '-avatar')
            i['last_update_time'] = self.formatTime(i.get('last_update_time'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        return lisIndexInfo

    def mediaCreate(self, dicArgs):
        """
        :func: 新增首页自媒体
        :param dicArgs: 自媒体参数
        """

        if 'media_id' in dicArgs:
            dicSort = self.mediaIndexModel.findOne({'fields': ['max(sort) as sort']})
            intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
            strKey = 'sort, last_update_time'
            strVal = '{sort}, {time}'.format(sort=intSort, time=int(self.time.time()))
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if strArgKey and arg_key != 'a':
                    strKey += ', {col}'.format(col=arg_key)
                    strVal += ', \'{val}\''.format(val=strArgKey)
            # print dicArgs['media_id'][0]
            media_info = self.mediaModel.findOne({
                'condition': 'id = "%s"' % dicArgs['media_id'][0]
            })
            # print media_info
            if 'id' not in media_info.has_key:
                intStatusCode = 404
                return {'statusCode': intStatusCode}
            self.mediaIndexModel.insert({'key': strKey, 'val': strVal})
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def mediaUpdate(self, dicArgs):
        """
        :func: 编辑首页自媒体
        :param dicArgs: 自媒体参数
        """
        if 'media_id' in dicArgs:
            strId = dicArgs.pop('idx_media_id')[0]
            fields = ['last_update_time = {time}'.format(time=int(self.time.time()))]
            # 广告主及链接(与表字段同名)
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if arg_key != 'a':
                    fields.append('{col} = \'{val}\''.format(col=arg_key, val=strArgKey))
            self.mediaIndexModel.update({
                'fields': fields,
                'condition': 'id = {id}'.format(id=strId)
            })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def mediaDelete(self, intId):
        """
        :func: 删除首页自媒体
        :param intId: 自媒体ID
        """
        self.mediaIndexModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
