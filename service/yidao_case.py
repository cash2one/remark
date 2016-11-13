# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # banner
        self.caseModel = self.importModel('yidao_case')

    def query(self, intPage=1, intPageDataNum=2):
        """
        :func: 公告数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        """
        # intDataNumStart = (intPage - 1) * intPageDataNum

        tupData, intRows = self.caseModel.findPaginate({
            'fields': ['id', 'media_name_1'],
            'page': [intPage, intPageDataNum],
            'order': 'create_time asc'
        })

        # 数据整合及格式化
        return tupData

    def create(self, dicArgs):
        """
        :func: 新增banner
        :param dicArgs: banner参数
        """
        if 'media_name' in dicArgs:
            self.caseModel.insert({
                'key': 'media_name',
                'val': '"%s"' % dicArgs['type']
            })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def update(self, dicArgs):
        """
        :func: 更新banner
        :param dicArgs: banner参数
        """
        if 'id' in dicArgs and 'media_name':
            self.caseModel.update({
                'fields': 'media_name = "%s"' % dicArgs['media_name'],
                'condition': 'id = {id}'.format(id=dicArgs['id'])
            })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def delete(self, intId):
        """
        :func: 删除Banner
        :param intId: Banner ID
        """
        self.caseModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
