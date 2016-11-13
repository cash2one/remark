# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    lis_demand_status = ['未下单', '已下单']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.plan_demand_model = self.importModel('project_plan_demand')
        self.demand_media_model = self.importModel('project_demand_media')
        self.project_feedback_service = self.importService('project_feedback')

    def get_plan_demand(self, intPage, intPageDataNum, strSearch=''):
        searchCondition = ''
        if strSearch:
            searchCondition = 'name like \'%{search}%\''.format(search=strSearch)
        tupData, intRows = self.plan_demand_model.findPaginateAs(self.dicConfig['DB_PROJECT'] +'.plan_demand as pd',{
            'fields': ['pd.*','p.title as plan_title'],
            'condition': '{search}'.format(search=searchCondition),
            'join':  self.dicConfig['DB_PROJECT'] +'.plan as p ON(p.id = pd.plan_id)',
            'page': [intPage, intPageDataNum],
            'order': 'pd.last_update_time desc'
        })

        for dic_data in tupData:
            dic_data['start_time'] = self.formatTime(dic_data['start_time'], '%Y-%m-%d')
            dic_data['end_time'] = self.formatTime(dic_data['end_time'], '%Y-%m-%d')
            dic_data['last_update_time'] = self.formatTime(dic_data['last_update_time'], '%Y-%m-%d')
            for k in dic_data.keys():
                if not dic_data[k]:
                    dic_data[k] = "-"
        return tupData, intRows

    def create_demand(self, dicArgs):
        dicArgs['start_time'] = int(self.time.mktime(self.time.strptime(dicArgs['start_time'], "%Y-%m-%d")))
        dicArgs['end_time'] = int(self.time.mktime(self.time.strptime(dicArgs['end_time'], "%Y-%m-%d")))
        create_time = int(self.time.time())
        self.plan_demand_model.insert({
            'key': 'plan_id, name, start_time, end_time, money, description, status, last_update_time, create_time',
            'val': "%s, '%s', %s, %s, %s, '%s', 0, %s, %s" % (
                dicArgs['plan_id'], dicArgs['name'], dicArgs['start_time'], dicArgs['end_time'],
                int(dicArgs['money']), dicArgs['description'], create_time, create_time)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_fd_info(self, intId):
        tupData = self.importModel('project_feedback').findManyAs(
            self.dicConfig['DB_PROJECT'] +'.feedback as f',
            {
                'fields':['f.*', 'dm.money as money'],
                'join': self.dicConfig['DB_PROJECT'] + '.demand_media as dm ON(f.plan_demand_id = dm.plan_demand_id and f.media_id = dm.media_id)',
                'condition': 'f.plan_demand_id = %s' % intId,
            }
        )
        dicData = self.importModel('project_demand_media').findOne({
            'fields': ['sum(money) as total_money'],
            'condition': 'plan_demand_id = %s' % intId,
        })
        # print dicData
        # print tupData
        if not tupData:
            return {}
        total_money = dicData.get('total_money', 0)
        sale = sum([i['money'] if i['money'] else 0 for i in tupData])
        sale_money = sum([i['sale_money'] for i in tupData])
        read_num = sum([i['read_num'] for i in tupData])
        like_num = sum([i['like_num'] for i in tupData])
        reg_num = sum([i['register_num'] for i in tupData])
        ticket_num = sum([i['ticket_num'] for i in tupData])
        order_num = sum([i['order_num'] for i in tupData])
        trade_num = sum([i['trade_num'] for i in tupData])
        trade_money = sum([i['trade_money'] for i in tupData])
        roi = 0 if sale == 0 else round(sale_money * 1.0 / sale, 3)
        cpm = 0 if read_num == 0 else round(sale * 1000.0 / read_num , 3)
        ucp = 0 if reg_num == 0 else round(sale * 1.0 / reg_num, 3)
        bucp = 0 if trade_num == 0 else round(sale * 1.0 / trade_num, 3)
        return {'sale': sale, 'sale_money': sale_money, 'roi': roi, 'trade_money': trade_money,
                'read_num': read_num, 'like_num': like_num, 'reg_num':reg_num,
                'ticket_num': ticket_num, 'order_num': order_num, 'trade_num': trade_num,
                'cpm': cpm, 'ucp': ucp, 'bucp': bucp, 'total_money': total_money}

    def get_one_demand(self, pid):
        dic_data = self.plan_demand_model.findOneAs(self.dicConfig['DB_PROJECT'] +'.plan_demand as pd',{
            'fields': ['pd.*','p.title as plan_title'],
            'join':  self.dicConfig['DB_PROJECT'] +'.plan as p ON(p.id = pd.plan_id)',
            'condition' : 'pd.id=%s' % (pid)
        })
        # print dic_data
        if dic_data.get('last_update_time') :
            dic_data['start_time'] = self.formatTime(dic_data['start_time'], '%Y-%m-%d')
            dic_data['end_time'] = self.formatTime(dic_data['end_time'], '%Y-%m-%d')
            dic_data['last_update_time'] = self.formatTime(dic_data['last_update_time'], '%Y-%m-%d')
        return dic_data

    def follow(self, did, uid, gid, remark):
        follow_model = self.importModel('project_demand_follow')
        res = self.check_follow(did, uid)
        if res:
            follow_model.delete({
                'condition': 'user_id=%s and plan_demand_id=%s' % (uid, did)
            })
            follow = 0
        else:
            if gid:
                for i in gid:
                    follow_model.insert({
                        'key': 'user_id, plan_demand_id, group_id, remark, create_time',
                        'val': '%s, %s, %s, "%s", %s' % (uid, did, i, remark, int(self.time.time()))
                    })
            else:
                follow_model.insert({
                    'key': 'user_id, plan_demand_id, remark, create_time',
                    'val': '%s, %s, "%s", %s' % (uid, did, remark, int(self.time.time()))
                })
            follow = 1
        if self.model.db.status != 200:
            return 500, {}
        return 200, {'follow': follow}

    def check_follow(self, did, uid):
        res = self.importModel('project_demand_follow').findOne({
            'condition': 'user_id=%s and plan_demand_id=%s' % (uid, did)
        })
        return res


    def update_demand(self, dicArgs):
        dicArgs['start_time'] = int(self.time.mktime(self.time.strptime(dicArgs['start_time'], "%Y-%m-%d")))
        dicArgs['end_time'] = int(self.time.mktime(self.time.strptime(dicArgs['end_time'], "%Y-%m-%d")))
        #print dicArgs
        self.plan_demand_model.update({
            'fields': [
                'name=\'%s\'' % (dicArgs['name']),
                'target=\'%s\'' % (dicArgs['target']),
                'description=\'%s\'' % (dicArgs['description']),
                'follower=\'%s\'' % (dicArgs['follower']),
                'summary=\'%s\'' % (dicArgs['summary']),
                'money=%s' % (dicArgs['money']),
                'status=%s' % (dicArgs['status']),
                'start_time={st}'.format(st=dicArgs['start_time']),
                'end_time={et}'.format(et=dicArgs['end_time']),
                'last_update_time={ut}'.format(ut=int(self.time.time()))
            ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200
        
    def create_potential(self, plan_demand_id, plan_id, media_id):
        create_time = int(self.time.time())
        self.demand_media_model.insert({
            'key': "plan_id, plan_demand_id, media_id, status, last_update_time, create_time",
            'val': "%s, %s, %s, 1, %s, %s" % (
                plan_id, plan_demand_id, media_id, create_time, create_time
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_potential(self, dicArg):
        if not dicArg['start_time']:
            dicArg['start_time'] = 0
        else:
            dicArg['start_time'] = int(self.time.mktime(self.time.strptime(dicArg['start_time'], "%Y-%m-%d")))
        if not dicArg['money']:
            dicArg['money'] = 0
        self.demand_media_model.update({
            'fields': ['link=\'%s\'' % dicArg['link'],
                       'money=%s' % dicArg['money'],
                       'start_time=%s' % dicArg['start_time'],
                       'description=\'%s\'' % dicArg['description'],
                       'remark=\'%s\'' % dicArg['remark'],
                       'status=%s' % dicArg['status']],
            'condition':'id=%s' % dicArg['id']
        })
        if self.model.db.status != 200:
            return 500
        return 200
        
    def get_demand_media(self, plan_demand_id):
        kol_name = {1:'是', 2: '否'}
        comment_name = {1:'有', 2:'没有'}
        award_name = {1:'有', 2: '没有'}

        tup_data = self.demand_media_model.findManyAs(self.dicConfig['DB_PROJECT'] +'.demand_media as pm',{

            'fields':['pm.id as id, pm.description','pm.status','pm.plan_demand_id as plan_demand_id',
                      'pm.start_time, pm.link, pm.money, pm.remark',
                      'm.name', 'mw.top_avg_read_num', 'mw.top_three_avg_read_num', 'mw.like_num',
                      'm.comment', 'm.award', 'm.kol','mw.original','m.id as media_id','m.first_price'],
            'condition':'pm.plan_demand_id=%s' % (plan_demand_id),
            'join':self.dicConfig['DB_PROJECT'] +'.media as m ON(m.id = pm.media_id) Left JOIN '+self.dicConfig['DB_PROJECT']+'.media_wechat as mw ON(pm.media_id = mw.media_id)',
            'order':'pm.start_time desc'
        })
        # print tup_data
        for item in tup_data:
            for key in item.keys():
                if key != 'status' and not item[key]:
                    item[key] = '-'

            # item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
            if not item['top_avg_read_num'] :
                item['top_avg_read_num'] = '-'
            if not item['top_three_avg_read_num'] :
                item['top_three_avg_read_num'] = '-'
            if not item['like_num'] :
                    item['like_num'] = '-'

            item['kol'] = kol_name.get(item['kol'], '-')
            item['comment'] = comment_name.get(item['comment'], '-')
            item['award'] = award_name.get(item['award'], '-')

            if not item['first_price'] :
                item['first_price'] = '-'

            item['feedback'] = self.project_feedback_service.get_feedback(item['plan_demand_id'], item['media_id'])
            # print item['feedback']
            if item['start_time'] != '-':
                item['start_time'] = self.formatTime(item['start_time'], '%Y-%m-%d')
        return tup_data