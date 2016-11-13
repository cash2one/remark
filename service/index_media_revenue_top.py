# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 自媒体(收入榜)
        self.mediaRevenueTopModel = self.importModel('index_media_revenue_top')
        # 接单数
        self.demandTakeOrderModel = self.importModel('demand_take_order')
        # 微信自媒体
        self.mediaWechatModel = self.importModel('media_wechat')

    def query(self, limit=None):
        """
        :func: 自媒体(收入榜)数据
        """
        # level
        dicLevel = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        dicArg = {
            'fields': ['xm.*', 'm.name', 'm.avatar', 'm.value_level'],
            'join': 'media as m ON (m.id = xm.media_id)',
            'order': 'xm.sort asc'
        }
        if limit is not None:
            dicArg['limit'] = ['0', str(limit)]
        tupData = self.mediaRevenueTopModel.findManyAs('index_media_revenue_top as xm', dicArg)
        lisMediaIds = [int(i['media_id']) for i in tupData]
        length = len(lisMediaIds)
        if length == 0:
            return []
        elif length == 1:
            strCondition = 'media_id = {ids}'.format(ids=lisMediaIds[0])
        else:
            strCondition = 'media_id in {ids}'.format(ids=str(tuple(lisMediaIds)))
        # 获取微信公众号阅读数
        tupWechatData = self.mediaWechatModel.findManyAs(
            'media_wechat as mw',
            {
                'fields': ['mw.media_id', 'mw.top_avg_read_num', 'mw.top_three_avg_read_num'],
                'condition': strCondition
            }
        )
        # 获取接单数
        tupDataTakeOrder = self.demandTakeOrderModel.findMany({
            'fields': ['count(*) as count', 'media_id'],
            'condition': '{cond} and status in (1, 4) group by media_id'.format(cond=strCondition)
        })
        dicWechatData = {i['media_id']: (i['top_avg_read_num'], i['top_three_avg_read_num']) for i in tupWechatData}
        dicDataTakeOrder = {i['media_id']: i['count'] for i in tupDataTakeOrder}
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
            if strMediaId in dicDataTakeOrder:
                i['order_num'] = dicDataTakeOrder[strMediaId]
            else:
                i['order_num'] = 0
            i['idx'] = idx + 1
            i['value_level'] = dicLevel.get(i['value_level'], 'A')
            i['avatar'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], i['avatar'], '-avatar')
            i['last_update_time'] = self.formatTime(i.get('last_update_time'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        # print lisIndexInfo
        return lisIndexInfo

    def create(self, dicArgs):
        """
        :func: 新增自媒体(收入榜)
        :param dicArgs: 自媒体(收入榜)参数
        """
        # print 222
        if 'media_id' in dicArgs:
            media_info = self.importModel('media').findOne({
                'condition': 'id = "%s"' % dicArgs['media_id'][0]
            })
            strMediaId = dicArgs.pop('media_id')[0]
            dicSort = self.mediaRevenueTopModel.findOne({'fields': ['max(sort) as sort']})
            intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
            strKey = 'media_id, sort, last_update_time'
            strVal = '{media_id}, {sort}, {time}'.format(
                media_id=strMediaId, sort=intSort, time=int(self.time.time())
            )
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if strArgKey and arg_key != 'a':
                    strKey += ', {col}'.format(col=arg_key)
                    # print strKey
                    strVal += ', \'{val}\''.format(val=strArgKey)
            # print strKey
            # print media_info
            if 'id' not in media_info:
                intStatusCode = 404
                return {'statusCode': intStatusCode}

            self.mediaRevenueTopModel.insert({'key': strKey, 'val': strVal})
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def update(self, dicArgs):
        """
        :func: 编辑自媒体(收入榜)
        :param dicArgs: 自媒体(收入榜)参数
        """
        if 'media_id' in dicArgs:
            strId = dicArgs.pop('idx_media_id')[0]
            strMediaId = dicArgs.pop('media_id')[0]
            fields = ['media_id = {media_id}'.format(media_id=strMediaId),
                      'last_update_time = {time}'.format(time=int(self.time.time()))]
            # 广告主及链接(与表字段同名)
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if arg_key != 'a':
                    fields.append('{col} = \'{val}\''.format(col=arg_key, val=strArgKey))
            self.mediaRevenueTopModel.update({
                'fields': fields,
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def delete(self, intId):
        """
        :func: 删除自媒体(收入榜)
        :param intId: 自媒体(收入榜)ID
        """
        self.mediaRevenueTopModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
