# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 友链
        self.friendlinkModel = self.importModel('friendlink')

    def query(self, intPage=1, intPageDataNum=10):
        """
        :func: 友链数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        """
        intDataNumStart = (intPage - 1) * intPageDataNum
        tupData, intRows = self.friendlinkModel.findPaginate({
            'page': [intPage, intPageDataNum],
            'order': 'sort asc'
        })
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['create_time'] = self.formatTime(i.get('last_update_time'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def friendlinkCreate(self, dicArgs):
        """
        :func: 新增友链
        :param dicArgs: 友链参数
        """
        if 'friendlink_title' in dicArgs and 'logo' in dicArgs and \
                'friendlink_url' in dicArgs and 'friendlink_desc' in dicArgs:
            strTitle = dicArgs['friendlink_title'][0]
            strLogo = '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicArgs['logo'][0], '-link')
            strUrl = dicArgs['friendlink_url'][0]
            strDesc = dicArgs['friendlink_desc'][0]
            dicSort = self.friendlinkModel.findOne({'fields': ['max(sort) as sort']})
            intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
            # desc 为sql 关键字 作为字段名需要``标识
            self.friendlinkModel.insert({
                'key': 'title, logo, link, `desc`, sort, status, last_update_time',
                'val': '\'{title}\', \'{logo}\', \'{link}\', \'{desc}\', {sort}, {status}, {time}'.format(
                    title=strTitle, logo=strLogo, link=strUrl, desc=strDesc,
                    sort=intSort, status=0, time=int(self.time.time())
                )
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def friendlinkEdit(self, dicArgs):
        """
        :func: 编辑友链
        :param dicArgs: 友链参数
        """

        if 'friendlink_id' in dicArgs and 'friendlink_title' in dicArgs and 'logo' in dicArgs and \
                'friendlink_url' in dicArgs and 'friendlink_desc' in dicArgs:
            strId = dicArgs['friendlink_id'][0]
            strTitle = dicArgs['friendlink_title'][0]
            strLogo = dicArgs['logo'][0]
            strUrl = dicArgs['friendlink_url'][0]
            strDesc = dicArgs['friendlink_desc'][0]
            lisFields = ['title = \'{title}\''.format(title=strTitle),
                         'link = \'{link}\''.format(link=strUrl),
                         # desc 为sql 关键字 作为字段名需要``标识
                         '`desc` = \'{desc}\''.format(desc=strDesc),
                         'last_update_time = {time}'.format(time=int(self.time.time()))]
            if strLogo:
                lisFields.append('logo = \'{logo}\''.format(logo=strLogo))
            self.friendlinkModel.update({
                'fields': lisFields,
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def friendlinkDelete(self, intId):
        """
        :func: 删除友链
        :param intId: 友链ID
        """

        self.friendlinkModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
