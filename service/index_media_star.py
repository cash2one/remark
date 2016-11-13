# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 自媒体(明星榜)
        self.mediaStarModel = self.importModel('index_media_star')
        # 微信自媒体
        self.mediaWechatModel = self.importModel('media_wechat')

    def query(self, limit=None):
        """
        :func: 自媒体(明星榜)数据
        """
        dicArg = {
            'fields': ['ims.*',
                       'm.name as name', 'm.avatar as avatar', 'm.value_level as value_level',
                       'mw.original as original', 'mw.top_avg_read_num', 'mw.top_three_avg_read_num'],
            'join': 'media as m ON (m.id = ims.media_id) left join media_wechat as mw on (ims.media_id = mw.media_id)',
            'order': 'ims.sort asc'
        }
        if limit is not None:
            dicArg['limit'] = ['0', str(limit)]
        tupData = self.mediaStarModel.findManyAs('index_media_star as ims', dicArg)

        # 数据格式化
        media_service = self.importService('media')
        if tupData:
            for k, item in enumerate(tupData):
                item['value_level'] = media_service.get_value_level(item['value_level'])
                item['avatar'] = self.getAvatarUrl(item['avatar'])
                item['idx'] = k + 1
                item['last_update_time'] = self.formatTime(item.get('last_update_time'), '%Y-%m-%d')
            return tupData[0]
        return {}

    def create(self, dicArgs):
        """
        :func: 新增自媒体(明星榜)
        :param dicArgs: 自媒体(明星榜)参数
        """

        if 'media_id' in dicArgs:
            dicSort = self.mediaStarModel.findOne({'fields': ['max(sort) as sort']})
            intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
            strKey = 'sort, last_update_time'
            strVal = '{sort}, {time}'.format(sort=intSort, time=int(self.time.time()))
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if strArgKey and arg_key != 'a':
                    strKey += ', {col}'.format(col=arg_key)
                    strVal += ', \'{val}\''.format(val=strArgKey)
            media_info = self.importModel('media').findOne({
                'condition': 'id = "%s"' % dicArgs['media_id'][0]
            })
            # print media_info
            if 'id' not in media_info:
                intStatusCode = 404
                return {'statusCode': intStatusCode}
            self.mediaStarModel.insert({'key': strKey, 'val': strVal})
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def update(self, dicArgs):
        """
        :func: 编辑自媒体(明星榜)
        :param dicArgs: 自媒体(明星榜)参数
        """
        if 'media_id' in dicArgs:
            strId = dicArgs.pop('idx_media_id')[0]
            fields = ['last_update_time = {time}'.format(time=int(self.time.time()))]
            # 广告主及链接(与表字段同名)
            for arg_key in dicArgs:
                strArgKey = dicArgs[arg_key][0]
                if arg_key != 'a':
                    fields.append('{col} = \'{val}\''.format(col=arg_key, val=strArgKey))
            self.mediaStarModel.update({
                'fields': fields,
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def delete(self, intId):
        """
        :func: 删除自媒体(明星榜)
        :param intId: 自媒体(明星榜)ID
        """
        self.mediaStarModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
