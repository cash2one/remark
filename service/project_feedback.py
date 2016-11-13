# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    lis_status = ['已结束','准备中','进行中']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.feedback_model = self.importModel('project_feedback')
        self.demand_service = self.importService('demand')
        self.feedback_follow_model = self.importModel('feedback_follow')

    def get_feedback_page(self, intPage, intPageDataNum, strRoiLeft, strRoiRight, strEffectLevel):
        roiCond = self.importService('media_wechat').build_interval_condition(
            'f.roi', strRoiLeft + ',' + strRoiRight)
        if strEffectLevel == '-1':
            levelCond = ''
        else:
            levelCond = 'f.effect_level = %s' % strEffectLevel
        cond = ''
        if roiCond and levelCond:
            cond = roiCond + ' and ' + levelCond
        elif roiCond:
            cond = roiCond
        elif levelCond:
            cond = levelCond
        dicArgs = {
            'fields':['f.*','m.name as media_name','pd.name as plan_demand_name'],
            'page': [intPage, intPageDataNum],
            'join': self.dicConfig['DB_PROJECT'] +'.media as m ON(f.media_id = m.id) LEFT JOIN '+ self.dicConfig['DB_PROJECT']+
            '.plan_demand as pd ON(f.plan_demand_id = pd.id)',
            'order': 'f.id desc'
        }
        if cond:
            dicArgs['condition'] = cond
        tupData, intRows = self.feedback_model.findPaginateAs(self.dicConfig['DB_PROJECT'] +'.feedback as f', dicArgs)
        for idx, item in enumerate(tupData, 1):
            item['idx'] = (intPage - 1) * intPageDataNum + idx

            item['web_demand_name'] = '-'
            if item['demand_id']:
                demand_info = self.demand_service.detail(str(item['demand_id']))
                if demand_info:
                    item['web_demand_name'] = demand_info['title']
                else:
                    item['demand_id'] = 0
            item['effect_level'] = self.effect_level(item['effect_level'])
        return tupData, intRows

    def get_one_feedback(self, intId):
        dicData = self.feedback_model.findOneAs(
            self.dicConfig['DB_PROJECT'] +'.feedback as f',
            {
                'fields':['f.*','m.name as media_name','pd.name as plan_demand_name'],
                'join': self.dicConfig['DB_PROJECT'] +'.media as m ON(f.media_id = m.id) LEFT JOIN '+ self.dicConfig['DB_PROJECT']+
                '.plan_demand as pd ON(f.plan_demand_id = pd.id)',
                'condition': 'f.id = %s' % intId
            }
        )
        dicData['web_demand_name'] = '-'
        if dicData.get('demand_id'):
            demand_info = self.demand_service.detail(str(dicData['demand_id']))
            if demand_info:
                dicData['web_demand_name'] = demand_info['title']
            else:
                dicData['demand_id'] = 0
        dicData['effect_level'] = self.effect_level(dicData['effect_level'])
        dicData['last_update_time'] = self.formatTime(dicData['last_update_time'], '%Y-%m-%d')
        dicData['create_time'] = self.formatTime(dicData['create_time'], '%Y-%m-%d')
        return dicData

    def effect_level(self, num):
        all = {0: '', 1:'很差', 2:'差', 3:'一般', 4:'好', 5:'很好'}
        return num, all.get(num, '')

    def comment(self, num):
        all = {0: '', 1:'是', 2:'否'}
        return num, all.get(num, '')


    def get_feedback(self, plan_demand_id, media_id):
        if media_id == '-':
            return {}
        tupData = self.feedback_model.findOne({
            'condition': 'plan_demand_id=%s and media_id=%s' % (plan_demand_id, media_id)
        })
        return tupData

    def create(self, dicArgs):
        craete_time = int(self.time.time())
        self.feedback_model.insert({
            'key': 'media_id, demand_id, plan_demand_id, sale_money, description, roi, last_update_time, create_time',
            'val': '{mid}, {did}, {pdid}, {sale_money}, \'{desc}\', {roi}, {ut}, {ct}'.format(
                mid=dicArgs['media_id'], did=dicArgs['demand_id'] if dicArgs['demand_id'] else 0 ,
                pdid=dicArgs['plan_demand_id'], sale_money=dicArgs['sale_money'],
                desc=dicArgs['description'], roi=dicArgs['roi'],
                ut=craete_time, ct=craete_time
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update(self, dicArgs):
        self.feedback_model.update({
            'fields': ['media_id={mid}'.format(mid=dicArgs['media_id']),
                       'demand_id={did}'.format(did=dicArgs['demand_id'] if dicArgs['demand_id'] else 0),
                       'plan_demand_id={pdid}'.format(pdid=dicArgs['plan_demand_id']),
                       'read_num={read_num}'.format(read_num=dicArgs['read_num']),
                       'like_num={like_num}'.format(like_num=dicArgs['like_num']),
                       'fans_num={fans_num}'.format(fans_num=dicArgs['fans_num']),
                       'register_num={reg_num}'.format(reg_num=dicArgs['register_num']),
                       'ticket_num={ticket_num}'.format(ticket_num=dicArgs['ticket_num']),
                       'order_num={ord_num}'.format(ord_num=dicArgs['order_num']),
                       'trade_num={trade_num}'.format(trade_num=dicArgs['trade_num']),
                       'trade_money={trade_money}'.format(trade_money=dicArgs['trade_money']),
                       'sale_money={sale_money}'.format(sale_money=dicArgs['sale_money']),
                       'description=\'{desc}\''.format(desc=dicArgs['description']),
                       'roi={roi}'.format(roi=dicArgs['roi']),
                       'effect_level=\'{el}\''.format(el=dicArgs['effect_level']),
                       'comment_num={comment_num}'.format(comment_num=dicArgs['comment_num']),
                       'last_update_time={ut}'.format(ut=int(self.time.time()))
                       ],
            'condition': 'id={id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_feedback(self, strId):
        self.feedback_model.delete({
            'condition': 'id={id}'.format(id=strId)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def check_group(self, id, uid):
        tupData = self.feedback_follow_model.findMany({
            'fields': ['id'],
            'condition': 'feedback_id = %s and user_id = %s ' % (id, uid)
        })
        return tupData

    def follow_group(self, id, group, uid, remark):
        if self.check_group(id, uid):
            self.feedback_follow_model.delete({
                'condition': 'user_id=%s and feedback_id=%s' % (uid, id)
            })
            if self.model.db.status != 200:
                return 500
        else:
            if not group:
                group = ['0']
            for item in group:
                self.feedback_follow_model.insert({
                    'key':'feedback_id, group_id, remark, user_id, create_time',
                    'val':'{id}, {group}, \'{remark}\', {uid}, {ct}'.format(
                    id=id, group=item, remark=remark, uid=uid, ct=int(self.time.time()))
                })
                if self.model.db.status != 200:
                    return 500
        return 200