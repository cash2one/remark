# -*- coding:utf-8 -*-

import base
import time
import sys



class service(base.baseService):
    lis_status = ['已结束','准备中','进行中']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.planModel = self.importModel('project_plan')
        self.plan_demandModel = self.importModel('project_plan_demand')
        self.planFollowModel = self.importModel('plan_follow')

    def advertiser_plan(self, strAdId):
        tupPlan = self.planModel.findMany({
            'condition': 'advertiser_id={ad_id}'.format(ad_id=strAdId)
        })
        return tupPlan

    def get_plan(self, intPage, intPageDataNum, strSearch=''):
        searchCondition = ''
        if strSearch:
            searchCondition = 'p.title like \'%{search}%\' or p.brief like \'%{search}%\''.format(search=strSearch)
        tupData, intRows = self.planModel.findPaginateAs(self.dicConfig['DB_PROJECT'] +'.plan as p',{
            'fields': ['p.*','a.company'],
            'condition': '{search}'.format(search=searchCondition),
            'page': [intPage, intPageDataNum],
            'join':self.dicConfig['DB_PROJECT'] +'.advertiser as a ON(a.id = p.advertiser_id)',
            'order': 'p.last_update_time desc'
        })
        #print  tupData
        for idx, i in enumerate(tupData, 1):
            i['idx'] = (intPage - 1) * intPageDataNum + idx
            i['time_begin'] = time.strftime("%Y-%m-%d", time.localtime(i['time_begin']))
            i['time_end'] = time.strftime("%Y-%m-%d", time.localtime(i['time_end']))
            i['last_update_time'] = time.strftime("%Y-%m-%d", time.localtime(i['last_update_time']))
        return tupData, intRows

    def create_plan(self, dicArgs):
        dicArgs['time_begin'] = int(time.mktime(time.strptime(dicArgs['time_begin'], "%Y-%m-%d")))
        dicArgs['time_end'] = int(time.mktime(time.strptime(dicArgs['time_end'], "%Y-%m-%d")))
        # print dicArgs
        self.planModel.insert({
            'key': 'advertiser_id, title, brief, time_begin, time_end, money, status, last_update_time, create_time',
            'val': '{ad_id}, \'{tt}\', \'{bf}\', {tbg}, {ted}, {money}, {status}, {ut}, {ct}'.format(
                ad_id=dicArgs['advertiser_id'], tt=dicArgs['title'], bf=dicArgs['brief'],
                tbg=dicArgs['time_begin'], ted=dicArgs['time_end'],
                money=dicArgs['money'], status=1, ut=int(self.time.time()), ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_plan(self, dicArgs):
        # print dicArgs
        dicArgs['time_begin'] = int(time.mktime(time.strptime(dicArgs['time_begin'], "%Y-%m-%d")))
        dicArgs['time_end'] = int(time.mktime(time.strptime(dicArgs['time_end'], "%Y-%m-%d")))
        self.planModel.update({
            'fields': ['advertiser_id={ad_id}'.format(ad_id=dicArgs['advertiser_id']),
                       'title=\'{tt}\''.format(tt=dicArgs['title']),
                       'brief=\'{bf}\''.format(bf=dicArgs['brief']),
                       'target=\'{target}\''.format(target=dicArgs['target']),
                       'strategy=\'{stg}\''.format(stg=dicArgs['strategy']),
                       'time_begin={tbg}'.format(tbg=dicArgs['time_begin']),
                       'time_end={ted}'.format(ted=dicArgs['time_end']),
                       'money={money}'.format(money=dicArgs['money']),
                       'follower=\'{fw}\''.format(fw=dicArgs['follower']),
                       'summary=\'{sy}\''.format(sy=dicArgs['summary']),
                       'progress=\'{pg}\''.format(pg=dicArgs['progress']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_plan(self, strId):
        self.planModel.delete({
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_one_plan(self,pid):
        dic_data = self.planModel.findOneAs(self.dicConfig['DB_PROJECT'] +'.plan as p',{
                'fields':['p.*','a.company'],
                'condition':'p.id={id}'.format(id=pid),
                'join':self.dicConfig['DB_PROJECT'] +'.advertiser as  a ON(a.id = p.advertiser_id)'
        })
        dic_data['time_begin'] = self.formatTime(dic_data['time_begin'], '%Y-%m-%d')
        dic_data['time_end'] = self.formatTime(dic_data['time_end'], '%Y-%m-%d')
        dic_data['last_update_time'] = self.formatTime(dic_data['last_update_time'], '%Y-%m-%d')
        if dic_data['status'] not in [0,1,2]:
            dic_data['status'] =  0
        dic_data['status'] = self.lis_status[dic_data['status']]
        return dic_data

    def plan_finish(self,pid):
        self.planModel.update({
            'fields':['status = 0'],
            'condition': 'id = {pid}'.format(pid =pid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_fd_info(self, intId):
        tupPlanDemand = self.importModel('project_plan_demand').findMany({
            'condition': 'plan_id = %s' % intId
        })
        planDemandIds = [str(int(i['id'])) for i in tupPlanDemand]
        if not planDemandIds:
            return {}
        tupData = self.importModel('project_feedback').findManyAs(
            self.dicConfig['DB_PROJECT'] +'.feedback as f',
            {
                'fields':['f.*', 'dm.money as money'],
                'join': self.dicConfig['DB_PROJECT'] + '.demand_media as dm ON(f.plan_demand_id = dm.plan_demand_id and f.media_id = dm.media_id)',
                'condition': 'f.plan_demand_id in (%s)' % ','.join(planDemandIds),
            }
        )
        dicData = self.importModel('project_demand_media').findOne({
            'fields': ['sum(money) as total_money'],
            'condition': 'plan_demand_id in (%s)' % ','.join(planDemandIds),
        })
        total_money = dicData.get('total_money', 0)
        money = sum([i['money'] or 0 for i in tupData])
        sale_money = sum([i['sale_money'] for i in tupData])
        read_num = sum([i['read_num'] for i in tupData])
        like_num = sum([i['like_num'] for i in tupData])
        reg_num = sum([i['register_num'] for i in tupData])
        ticket_num = sum([i['ticket_num'] for i in tupData])
        order_num = sum([i['order_num'] for i in tupData])
        trade_num = sum([i['trade_num'] for i in tupData])
        trade_money = sum([i['trade_money'] for i in tupData])
        roi = 0 if money == 0 else round(sale_money * 1.0 / money, 3)
        cpm = 0 if read_num == 0 else round(money * 1000.0 / read_num, 3)
        ucp = 0 if reg_num == 0 else round(money * 1.0 / reg_num, 3)
        bucp = 0 if trade_num == 0 else round(money * 1.0 / trade_num, 3)
        return {'sale': money, 'sale_money': sale_money, 'roi': roi, 'trade_money': trade_money,
                'read_num': read_num, 'like_num': like_num, 'reg_num':reg_num,
                'ticket_num': ticket_num, 'order_num': order_num, 'trade_num': trade_num,
                'cpm': cpm, 'ucp': ucp, 'bucp': bucp, 'total_money': total_money}

    def get_plan_demand(self,pid):
        tup_data = self.plan_demandModel.findMany({
            'condition':'plan_id = {0}'.format(pid)
        })
        for item in tup_data:
            item['start_time'] = self.formatTime(item['start_time'],'%Y-%m-%d')
            item['end_time'] = self.formatTime(item['end_time'],'%Y-%m-%d')
            item['last_update_time'] = self.formatTime(item['last_update_time'],'%Y-%m-%d')
        return tup_data

    def check_group(self, id, uid):
        tupData = self.planFollowModel.findMany({
            'fields': ['id'],
            'condition': 'plan_id = %s and user_id = %s ' % (id, uid)
        })
        return tupData

    def follow_group(self, id, group, uid, remark):
        if self.check_group(id, uid):
            self.planFollowModel.delete({
                'condition': 'user_id=%s and plan_id=%s' % (uid, id)
            })
            if self.model.db.status != 200:
                return 500
        else:
            if not group:
                group = ['0']
            for item in group:
                self.planFollowModel.insert({
                    'key':'plan_id, group_id, remark, user_id, createTime',
                    'val':'{id}, {group}, \'{remark}\', {uid}, {ct}'.format(
                    id=id, group=item, remark=remark, uid=uid, ct=int(self.time.time()))
                })
                if self.model.db.status != 200:
                    return 500
        return 200
