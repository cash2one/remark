# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 联盟
        self.unionModel = self.importModel('union')
        # 用户
        self.userModel = self.importModel('user')
        # 联盟状态标签
        self.unionStatus = {-2: '已禁用', -1: '未通过', 0: '未审核', 1: '正常'}

    def index(self, intPage, intPageDataNum, strStatus, strTimeStart, strTimeEnd, strSearch):
        '''
        :func: 获取联盟首页信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param strStatus: 联盟状态
        :param strTimeStart: 筛选的起始时间
        :param strTimeEnd: 筛选的结束时间
        :param strSearch: 搜索的内容
        '''
        # 当前页起始序号
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 联盟状态条件
        if strStatus == '0':
            statusCondition = 'un.status = {status}'.format(status=strStatus)
        else:
            statusCondition = 'un.status in ({status})'.format(status=strStatus)
        # 筛选时间条件
        timeCondition = ''
        if strTimeStart != '' and strTimeEnd != '':
            timeCondition = ' and un.create_time > \'{start}\' and un.create_time < \'{end}\''.format(
                start=strTimeStart, end=strTimeEnd)
        elif strTimeEnd != '':
            timeCondition = ' and un.create_time < \'{end}\''.format(end=strTimeEnd)
        elif strTimeStart != '':
            timeCondition = ' and un.create_time > \'{start}\''.format(start=strTimeStart)
        # 搜索条件
        searchCondition = ''
        if strSearch:
            searchCondition = ' and un.name like \'%{search}%\''.format(search=strSearch)

        tupData, intRows = self.unionModel.getPaginate(
            'pt_unions as un',
            {
                'fields': ['un.id', 'un.name', 'un.user_id', 'un.create_time', 'un.status', 'u.nickname'],
                'join': 'pt_users as u ON (un.user_id = u.user_id)',
                'condition': '{status}{time}{search}'.format(
                    status=statusCondition, time=timeCondition, search=searchCondition),
                'page': intPage,
                'limit': [str(intDataNumStart), str(intPageDataNum)],
                'demand': 'un.create_time desc'
            }
        )
        # 数据整合
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['status_tag'] = self.unionStatus.get(i.get('status'), 'unknown')
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def detail(self, intId):
        '''
        :func: 查看联盟详细信息
        :param intId: 联盟ID
        '''
        try:
            dicData = self.unionModel.getOne({
                'condition': 'id = {id}'.format(id=intId)
            })
            dicDataUser = self.userModel.findOne({
                'fields': ['nickname'],
                'condition': 'user_id = {user_id}'.format(user_id=dicData.get('user_id'))
            })
            # 用户信息缺失
            if dicDataUser is None:
                dicDataUser = {'nickname': ''}
            # 合并结果
            dicData.update(dicDataUser)
            dicData['logo'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicData.get('logo'), '-union')
            dicData['status_tag'] = self.unionStatus.get(dicData.get('status'), 'unknown')
            return {'statusCode': 200, 'dicData': dicData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def allow(self, intId):
        '''
        :func: 联盟审核通过
        :param intId: 联盟ID
        '''
        self.unionModel.updateOne({
            'fields': ['status = 1'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def disallow(self, intId):
        '''
        :func: 联盟审核不通过
        :param intId: 联盟ID
        '''
        self.unionModel.updateOne({
            'fields': ['status = -1'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def ban(self, intId):
        '''
        :func: 禁用联盟
        :param intId: 联盟ID
        '''
        self.unionModel.updateOne({
            'fields': ['status = -2'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def unban(self, intId):
        '''
        :func: 取消禁用联盟
        :param intId: 联盟ID
        '''
        self.unionModel.updateOne({
            'fields': ['status = 1'],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def delete(self, intId):
        '''
        :func: 删除联盟
        :param intId: 联盟ID
        '''
        self.unionModel.deleteOne({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
