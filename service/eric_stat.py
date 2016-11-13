# -*- coding:utf-8 -*-
import base
import datetime
import time
import types


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.siteModel = self.importModel('stat_site')
        self.indexModel = self.importModel('stat_index')
        self.demandModel = self.importModel('demand')
        self.demand_take_orderModel = self.importModel('demand_take_order')
        self.demand_orderModel = self.importModel('demand_order')
        self.demand_logModel = self.importModel('demand_log')
        self.demand_appeal_model = self.importModel('demand_appeal')
        self.userModel = self.importModel('user')
        self.mediaModel = self.importModel('media')
        self.pay_model = self.importModel('pay')

    def findstat(self, date):
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[8:10])
        timeint = datetime.datetime(year, month, day)
        timestamp = time.mktime(timeint.timetuple())
        timestampnext = timestamp + 86400
        # print  timestamp

        stat_site = self.siteModel.findMany({
            'fields': ['SUM(pv) as stat_pv_day', 'SUM(uv) as stat_uv_day', 'SUM(ip) as stat_ip_day',
                       'SUM(user) as stat_user_day'],
            'condition': 'day >= {today}and day<{tomorrow}'.format(today=timestamp, tomorrow=timestampnext)
        })
        stat_index = self.indexModel.findMany({
            'fields': ['SUM(pv) as index_pv_day', 'SUM(uv) as index_uv_day', 'SUM(ip) as index_ip_day'],
            'condition': 'day >= {today}and day<{tomorrow}'.format(today=timestamp, tomorrow=timestampnext)
        })
        stat = list(stat_site)
        for k in stat[0].keys():
            if stat[0][k] is None:
                # print 1
                stat[0][k] = 0
            else:
                stat[0][k] = long(stat[0][k])
        stat_index_list = list(stat_index)
        for k in stat_index_list[0].keys():
            if stat_index_list[0][k] is None:
                # print 2
                stat_index_list[0][k] = 0
            else:
                stat_index_list[0][k] = long(stat_index_list[0][k])
        stat.extend(stat_index_list)
        # print stat
        return stat

    def find_demand_num(self, date):
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[8:10])
        timeint = datetime.datetime(year, month, day)
        timestamp = time.mktime(timeint.timetuple())
        timestampnext = timestamp + 86400
        # print timestamp
        # print timestampnext
        deidnum = self.demandModel.findMany({
            'fields': ['count(*) as demand_count'],  # 营销需求数
            'condition': 'create_time >= {today}and create_time<{tomorrow}'.format(today=timestamp,
                                                                                   tomorrow=timestampnext)
        })
        takeordernum = self.demand_take_orderModel.findMany({
            'fields': ['count(*) as take_order_count'],  # 接单数
            'condition': 'create_time >= {today}and create_time<{tomorrow}'.format(today=timestamp,
                                                                                   tomorrow=timestampnext)
        })
        ordernum = self.demand_orderModel.findMany({
            'fields': ['count(*) as order_count'],  # 下单数
            'condition': 'create_time >= {today}and create_time<{tomorrow}'.format(today=timestamp,
                                                                                   tomorrow=timestampnext)
        })
        de_comp = self.demand_logModel.findMany({
            'fields': ['count(*) as demand_comp_count'],  # 下单数
            'condition': 'create_time >= {today}and '
                         'create_time<{tomorrow}and new_status=0'.format(today=timestamp,
                                                                         tomorrow=timestampnext)
        })
        new_user = self.userModel.findMany({
            'fields': ['count(*) as new_user_count'],
            'condition': 'create_time >= {today}and create_time<{tomorrow}'.format(today=timestamp,
                                                                                   tomorrow=timestampnext)
        })
        new_media = self.mediaModel.findMany({
            'fields': ['count(*) as new_media_count'],
            'condition': 'create_time >= {today}and create_time<{tomorrow}'.format(today=timestamp,
                                                                                   tomorrow=timestampnext)
        })

        log = {'demand_count': deidnum[0].get('demand_count'),
               'take_order_count': takeordernum[0].get('take_order_count'),
               'order_count': ordernum[0].get('order_count'),
               'demand_comp_count': de_comp[0].get('demand_comp_count'),
               'new_user_count': new_user[0].get('new_user_count'),
               'new_media_count': new_media[0].get('new_media_count')}
        return log

    def find_wait_order(self):
        all_demand = list(self.demandModel.findMany({
            'fields': ['id'],
            'condition': 'status = 2'
        }))

        return len(all_demand)

    def find_in_appeal(self):
        all_in_appeal = list(self.demand_appeal_model.findMany({
            'fields': ['count(*) as count'],
            'condition': 'status != 2'
        }))
        # print all_in_appeal[0].get('count')
        return all_in_appeal[0].get('count')

    def find_complete(self):
        all_complete = self.demandModel.findMany({
            'fields': ['count(*) as count'],
            'condition': 'status = 4'
        })
        return all_complete[0].get('count')

    def find_in_demand(self):
        in_demand = self.demandModel.findMany({
            'fields': ['count(*) as count'],
            'condition': 'status = 3'
        })
        return in_demand[0].get('count')

    def find_wait_feedback(self):
        all_feedback = list(self.demand_orderModel.findMany({
            'fields': ['count(*) as count'],
            'condition': 'status = 2 '
        }))
        # print all_in_appeal[0].get('count')
        return all_feedback[0].get('count')
