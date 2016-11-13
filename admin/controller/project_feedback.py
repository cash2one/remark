# -*- coding:utf-8 -*-

import base

class feedback(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.projectService = self.importService('project_feedback')

    def index(self):
        strMenu = 'project_feedback'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 搜索内容
        strRoiLeft = self.I('roi_left')
        strRoiRight = self.I('roi_right')
        strEffectLevel = self.I('effect_level', '-1')
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/feedback?'
        tupData, intRows = self.projectService.get_feedback_page(
            intPage, intPageDataNum, strRoiLeft, strRoiRight, strEffectLevel)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['cond'] = {'roi_left': strRoiLeft, 'roi_right':strRoiRight, 'level':strEffectLevel}
        self.dicViewData['ad_feedback'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('feedback', 'project')

    def detail(self):
        strMenu = 'project_feedback'
        feedback_id = self.I('id')
        uid = self.current_user.get('id')
        self.dicViewData['detail'] = self.projectService.get_one_feedback(feedback_id)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['group'] = self.projectService.check_group(feedback_id, uid)
        self.dicViewData['groupData'] = self.importService('admin_user').get_group(uid, 6)
        self.display('detail', 'project')

    def create(self):
        dicArgs = {
            'media_id': self.I('media_id'),
            'demand_id': self.I('demand_id'),
            'plan_demand_id': self.I('plan_demand_id'),
            'sale_money': self.I('sale_money', '0'),
            'description': self.I('description', ''),
            'roi': self.I('roi', '0')
        }
        status = self.projectService.create(dicArgs)
        self.out(status)

    def update(self):
        dicArgs = {
            'id':self.I('id'),
            'media_id': self.I('media_id'),
            'demand_id': self.I('demand_id'),
            'plan_demand_id': self.I('plan_demand_id'),
            'read_num': self.I('read_num', '0'),
            'like_num': self.I('like_num', '0'),
            'fans_num': self.I('fans_num', '0'),
            'register_num': self.I('register_num', '0'),
            'ticket_num': self.I('ticket_num', '0'),
            'order_num': self.I('order_num', '0'),
            'trade_num': self.I('trade_num', '0'),
            'trade_money': self.I('trade_money', '0'),
            'sale_money': self.I('sale_money', '0'),
            'description': self.I('description'),
            'roi': self.I('roi'),
            'comment_num': self.I('comment_num', '0'),
            'effect_level': self.I('effect_level')
        }
        status = self.projectService.update(dicArgs)
        self.redirect('/project/feedback?a=detail&id={id}'.format(id = dicArgs['id']))

    def delete(self):
        strId = self.I('id')
        self.projectService.delete_feedback(strId)
        self.redirect('/project/feedback')

    def follow(self):
        strid = self.I('id')
        remark = self.I('remark')
        group = self.I('group')
        uid = self.current_user.get('id')
        if group:
            group = group.split(',')
        status = self.projectService.follow_group(strid, group, uid, remark)
        self.out(status)