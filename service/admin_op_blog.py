# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 博客
        self.blogModel = self.importModel('blog')

    def blog(self, intPage, intPageDataNum, strSearch):
        """
        :func: 博文数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        :param strSearch: 搜索内容
        """
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 搜索条件
        searchCondition = ''
        if strSearch:
            searchCondition = 'b.title like \'%{search}%\''.format(search=strSearch)
        tupData, intRows = self.blogModel.findPaginate(
            'pt_blogs as b',
            {
                'fields': ['b.id', 'b.title', 'b.summary', 'b.author', 'b.update_at'],
                # 'join': 'pt_users as u ON (w.user_id = u.user_id)',
                'condition': '{search}'.format(search=searchCondition),
                'page': intPage,
                'limit': [str(intDataNumStart), str(intPageDataNum)],
                'order': 'b.update_at desc'
            }
        )
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            uDesc = i['summary'][:40]
            i['summary'] = uDesc if len(uDesc) < 40 else uDesc + '...'
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def blogTop(self, intId):
        """
        :func: 置顶博文
        :param intId: 博文id
        """
        self.blogModel.update({
            'fields': ['update_at = \'{time}\''.format(
                time=self.time.strftime("%Y-%m-%d %H:%M:%S", self.time.localtime())
            )],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def blogDelete(self, intId):
        """
        :func: 删除博文
        """
        self.blogModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
