# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 自媒体刊例报价属性
        self.mediaAttrModel = self.importModel('ad_attribute')
        # 自媒体刊例报价属性值
        self.mediaValueModel = self.importModel('ad_value')
        # 自媒体刊例报价属性-属性值
        self.mediaAttrValueModel = self.importModel('ad_attribute_value')

    def index(self, intPage, intPageDataNum, strSearch):
        '''
        :func: 获取简要信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param strSearch: 搜索的内容
        '''
        # 当前页起始序号
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 搜索条件
        searchCondition = ''
        if strSearch and searchCondition:
            searchCondition = ' and a.name like \'%{search}%\''.format(search=strSearch)
        elif strSearch:
            searchCondition = 'a.name like \'%{search}%\''.format(search=strSearch)
        # 简要信息
        tupData, intRows = self.mediaAttrValueModel.findPaginateAs(
            'ad_attribute_value as av',
            {
                'fields': ['av.id', 'av.attr_id', 'av.value_id',
                           'a.name as attr_name', 'v.name as value_name'],
                'join': 'ad_attribute as a ON (a.id = av.attr_id) '
                        'JOIN ad_value as v ON (v.id = av.value_id)',
                'condition': '{search}'.format(search=searchCondition),
                'page': [intPage, intPageDataNum],
                'order': 'av.id asc'
            }
        )
        # 数据格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def create(self, dicArgs):
        if 'attr_name' in dicArgs and 'value_name' in dicArgs:
            strAttrName = dicArgs['attr_name'][0]
            strValueName = dicArgs['value_name'][0]
            aid = self.mediaAttrModel.findOne({'condition': 'name = \'{an}\''.format(an=strAttrName)}).get('id')
            vid = self.mediaValueModel.findOne({'condition': 'name = \'{vn}\''.format(vn=strValueName)}).get('id')
            # 新属性
            if aid is None:
                aid = self.mediaAttrModel.insert({'key': 'name', 'val': '\'{an}\''.format(an=strAttrName)})
            # 新属性值
            if vid is None:
                vid = self.mediaValueModel.insert({'key': 'name', 'val': '\'{vn}\''.format(vn=strValueName)})
            self.mediaAttrValueModel.insert({
                'key': 'attr_id, value_id',
                'val': '{aid}, {vid}'.format(aid=aid, vid=vid)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def update(self, dicArgs):
        if 'attr_value_id' in dicArgs and 'attr_name' in dicArgs and 'value_name' in dicArgs:
            strId = dicArgs['attr_value_id'][0]
            strAttrName = dicArgs['attr_name'][0]
            strValueName = dicArgs['value_name'][0]
            strAttrId = dicArgs['attr_id'][0]
            strValueId = dicArgs['value_id'][0]
            self.mediaAttrModel.update({
                'fields': ['name = \'{an}\''.format(an=strAttrName)],
                'condition': 'id = {aid}'.format(aid=strAttrId)
            })
            self.mediaValueModel.update({
                'fields': ['name = \'{vn}\''.format(vn=strValueName)],
                'condition': 'id = {vid}'.format(vid=strValueId)
            })
            self.mediaAttrValueModel.update({
                'fields': ['attr_id = {aid}'.format(aid=strAttrId),
                           'value_id = {vid}'.format(vid=strValueId)],
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def delete(self, intId):
        self.mediaAttrValueModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
