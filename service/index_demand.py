# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.idxDemandModel = self.importModel('index_demand')

    def index(self, limit=None):
        # TODO 接单数，人气值，前5自媒体头像
        dicArg = {
            'fields': ['xd.id', 'xd.demand_id', 'xd.sort', 'xd.last_update_time',
                       'd.title', 'd.form', 'd.money', 'd.time_begin', 'd.time_end', 'd.view_count'],
            'join': 'demand as d ON (d.id = xd.demand_id)',
            'order': 'xd.sort asc'
        }
        if limit is not None:
            dicArg['limit'] = ['0', str(limit)]

        idxDemandModel = self.importModel('index_demand')
        tupData = idxDemandModel.findManyAs('index_demand as xd', dicArg)
        # 数据整合及格式化
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = idx + 1
            i['last_update_time'] = self.formatTime(i.get('last_update_time'), '%Y-%m-%d')
            i['time_begin'] = self.formatTime(i.get('time_begin'), '%Y-%m-%d')
            i['time_end'] = self.formatTime(i.get('time_end'), '%Y-%m-%d')
            lisIndexInfo.append(i)
        return lisIndexInfo

    def query(self, limit=4):
        """
        :func: 首页广告需求数据
        """
        tupIdxDemand = self.idxDemandModel.findManyAs('index_demand as i_d', {
            'fields': ['d.id as demand_id', 'd.title', 'form', 'money', 'time_begin', 'time_end', 'view_count'],
            'join': 'demand as d on (i_d.demand_id = d.id)',
            'order': 'sort asc',
            'limit': ['0', str(limit)]
        })

        if tupIdxDemand:
            demandService = self.importService('demand')
            for k, item in enumerate(tupIdxDemand):
                item['time_begin'] = self.formatTime(item['time_begin'], '%Y-%m-%d')
                item['time_end'] = self.formatTime(item['time_end'], '%Y-%m-%d')

                item['money'] = int(item['money'])

                item['demand_form'] = demandService.demand_form(item['form'])[item['form']]['name']
                item['take_order'] = demandService.demand_take_order(item['demand_id'])

        return tupIdxDemand

    def create(self, dicArgs):
        """
        :func: 新增首页需求单
        :param dicArgs: 需求单参数
        """
        if 'demand_id' not in dicArgs:
            return 404

        strDemandId = dicArgs['demand_id'][0]
        demand_model = self.importModel('demand')
        demand_info = demand_model.findOne({
            'condition': 'id = "%s"' % strDemandId
        })
        if 'id' not in demand_info:
            return 404

        idxDemandModel = self.importModel('index_demand')
        dicSort = idxDemandModel.findOne({'fields': ['max(sort) as sort']})
        intSort = 1 if dicSort['sort'] is None else dicSort['sort'] + 1
        self.idxDemandModel.insert({
            'key': 'demand_id, sort, last_update_time',
            'val': '{demand_id}, {sort}, {time}'.format(
                demand_id=strDemandId, sort=intSort, time=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def update(self, dicArgs):
        """
        :func: 编辑首页需求单
        :param dicArgs: 需求单参数
        """
        if 'demand_id' not in dicArgs:
            return 404

        strId = dicArgs['idx_demand_id'][0]
        strDemandId = dicArgs['demand_id'][0]
        idxDemandModel = self.importModel('index_demand')
        idxDemandModel.update({
            'fields': ['demand_id = {demand_id}'.format(demand_id=strDemandId),
                       'last_update_time = {time}'.format(time=int(self.time.time()))],
            'condition': 'id = {id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def delete(self, intId):
        """
        :func: 删除首页需求单
        :param intId: 需求单ID
        """
        idxDemandModel = self.importModel('index_demand')
        idxDemandModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return 601
        return 200
