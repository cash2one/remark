# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.mediaModel = self.importModel('project_media')
        self.mediaTagModel = self.importModel('project_media_tag')
        self.categoryModel = self.importModel('project_category_media')
        self.tagModel = self.importModel('project_tag')

    def get_category(self, intPage, intPageDataNum, strSearch):
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
        if strSearch:
            searchCondition = 'name like "%{search}%"'.format(search=strSearch)
        # 简要信息
        tupData, intRows = self.categoryModel.findPaginate({
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum],
            'order': 'sort asc'
        })
        # 数据格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def create_category(self, name):
        try:
            _sort = self.categoryModel.findOne({
                'fields': ['max(sort) as sort']
            }).get('sort') + 1
        except Exception, e:
            print e
            return 500
        self.categoryModel.insert({
            'key': 'name, sort',
            'val': '"{name}", {sort}'.format(name=name, sort=_sort)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_category(self, _id, name):
        self.categoryModel.update({
            'fields': ['name = "{name}"'.format(name=name)],
            'condition': 'id = {id}'.format(id=_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_category(self, _id):
        self.categoryModel.delete({
            'condition': 'id = {id}'.format(id=_id)
        })
        self.mediaModel.update({
            'fields': ['category_media_id = 0'],
            'condition': 'category_media_id = {cid}'.format(cid=_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_tag(self, intPage, intPageDataNum, strSearch):
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
        if strSearch:
            searchCondition = 'name like "%{search}%"'.format(search=strSearch)
        # 简要信息
        tupData, intRows = self.tagModel.findPaginate({
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum],
            'order': 'sort asc'
        })
        # 数据格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def create_tag(self, name):
        try:
            _sort = self.tagModel.findOne({
                'fields': ['max(sort) as sort']
            }).get('sort') + 1
        except Exception, e:
            print e
            return 500
        self.tagModel.insert({
            'key': 'name, sort',
            'val': '"{name}", {sort}'.format(name=name, sort=_sort)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_tag(self, _id, name):
        self.tagModel.update({
            'fields': ['name = "{name}"'.format(name=name)],
            'condition': 'id = {id}'.format(id=_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_tag(self, _id):
        self.tagModel.delete({
            'condition': 'id = {id}'.format(id=_id)
        })
        self.mediaTagModel.delete({
            'condition': 'tag_id = {id}'.format(id=_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200
