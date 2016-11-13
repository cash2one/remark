# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 互推
        self.winwinModel = self.importModel('winwins')
        # 用户信息
        self.userModel = self.importModel('user')
        # 互推状态
        self.winwinStatus = {-2: '未发起(隐藏中)', -1: '已发起(隐藏中)', 0: '未发起', 1: '已发起'}

    def winwin(self, intPage, intPageDataNum, strSearch):
        """
        :func: 互推列表
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        :param strSearch: 搜索内容
        """
        intDataNumStart = (intPage - 1) * intPageDataNum
        # 搜索条件
        searchCondition = ''
        if strSearch:
            searchCondition = 'w.title like \'%{search}%\''.format(search=strSearch)
        tupData, intRows = self.winwinModel.findPaginate(
            'pt_winwins as w',
            {
                'fields': ['w.id', 'w.description', 'w.start_date', 'w.status',
                           'w.title', 'w.user_id', 'u.nickname'],
                'join': 'pt_users as u ON (w.user_id = u.user_id)',
                'condition': '{search}'.format(search=searchCondition),
                'page': intPage,
                'limit': [str(intDataNumStart), str(intPageDataNum)],
                'order': 'w.created_at desc'
            }
        )
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            uDesc = i['description'][:40]
            i['description'] = uDesc if len(uDesc) < 40 else uDesc + '...'
            lisIndexInfo.append(i)
        return lisIndexInfo, intRows

    def winwinDetail(self, intId):
        '''
        :func: 查看互推详细信息
        :param intId: 互推ID
        '''
        try:
            dicData = self.winwinModel.findOne({
                'condition': 'id = {id}'.format(id=intId)
            })
            dicDataUser = self.userModel.findOne({
                'fields': ['nickname'],
                'condition': 'user_id = {id}'.format(id=dicData.get('user_id'))
            })
            if dicDataUser is None:
                dicData['nickname'] = ''
            else:
                dicData.update(dicDataUser)
            dicData['status_tag'] = self.winwinStatus.get(dicData.get('status'), 'unknown')
            dicData['created_at'] = dicData.get('created_at').strftime('%Y-%m-%d')
            dicData['start_date'] = dicData.get('start_date').strftime('%Y-%m-%d')
            return {'statusCode': 200, 'dicData': dicData}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def winwinDelete(self, intId):
        '''
        :func: 删除互推条目
        :param intId: 互推ID
        '''
        self.winwinModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def winwinUpdateStatus(self, intId, intStatus):
        '''
        :func: 互推状态更新
        :param intId: 互推ID
        :param intStatus: 互推状态
        '''
        # 互推状态转移字典
        dicSwitch = {-2: 0, 0: -2, -1: 1, 1: -1}
        self.winwinModel.update({
            'fields': ['status = {new}'.format(new=dicSwitch[intStatus])],
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
