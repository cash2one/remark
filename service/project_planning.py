# -*- coding:utf-8 -*-

import base


class service(base.baseService):

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.planning_model = self.importModel('planning')
        self.planningFollow_model = self.importModel('planning_follow')

    def get_planningPage(self, intPage, intPageDataNum):
        tupData, intRows = self.planning_model.findPaginate({
            'page': [intPage, intPageDataNum],
            'order': 'updateTime desc'
        })
        return tupData, intRows

    def create(self, dicArgs):
        if not dicArgs or not dicArgs['title'] or dicArgs['title']=="":
            return 500
        curTime = int(self.time.time())
        self.planning_model.insert({
            'key': 'title, content, updateTime, createTime',
            'val': '\'{title}\', \'{content}\', {ut}, {ct}'.format(
                title=dicArgs['title'], content=dicArgs['content'], ut=curTime, ct=curTime)
        })
        if self.model.db.status != 200:
            return 500

        tupPlan = self.planning_model.findOne({
            'fields': ['max(planID) as planID'],
        })
        self.planning_model.update({
            'fields':['planID={id}'.format(id = int(tupPlan['planID'])+1)],
            'condition': 'title = \'{title}\''.format(title=dicArgs['title'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def details(self, planID):
        tupPlan = self.planning_model.findOne({
            'condition':'planID = \'{planID}\''.format(planID=planID)
        })
        return tupPlan

    def update(self, dicArgs):
        if not dicArgs or not dicArgs['title'] or dicArgs['title']=="":
            return 500
        curTime = int(self.time.time())
        self.planning_model.update({
            'fields':['title=\'{title}\''.format(title = dicArgs['title']),
                      'content=\'{content}\''.format(content = dicArgs['content']),
                        'updateTime={upt}'.format(upt = curTime)],
            'condition': 'planID = {id}'.format(id=dicArgs['id'])
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def check_group(self, id, uid):
        tupData = self.planningFollow_model.findMany({
            'fields': ['id'],
            'condition': 'planning_id = %s and user_id = %s ' % (id, uid)
        })
        return tupData

    def follow_group(self, id, group, uid, remark):
        data = self.check_group(id, uid)
        if data:
            self.planningFollow_model.delete({
                'condition': 'user_id=%s and planning_id=%s' % (uid, id)
            })
            if self.model.db.status != 200:
                return 500
        else:
            if not group:
                group = ['0']
            for item in group:
                self.planningFollow_model.insert({
                    'key':'planning_id, group_id, remark, user_id, createTime',
                    'val':'{id}, {group}, \'{remark}\', {uid}, {ct}'.format(
                    id=id, group=item, remark=remark, uid=uid, ct=int(self.time.time()))
                })
                if self.model.db.status != 200:
                    return 500
        return 200