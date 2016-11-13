# -*- coding:utf-8 -*-

import base

class plan(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.projectService = self.importService('project_plan')
        self.project_demandService = self.importService('project_demand')

    def index(self):
        strMenu = 'project_plan'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 搜索内容
        strSearch = self.I('search')
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/plan?'
        tupData, intRows = self.projectService.get_plan(intPage, intPageDataNum, strSearch)
        self.dicViewData['plan'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['menu'] = strMenu
        self.display('plan', 'project')

    def detail(self):
        pid = self.I('id')
        uid = self.current_user.get('id')
        #dic_media = ['description','status','last_update_time',' identify','name','kol','original','top_avg_read_num','id','audience_gender','pot_id']
        self.dicViewData['demand'] = self.projectService.get_plan_demand(pid)
        self.dicViewData['fd_info'] = self.projectService.get_fd_info(pid)
        self.dicViewData['detail'] = self.projectService.get_one_plan(pid)
        self.dicViewData['group'] = self.projectService.check_group(pid, uid)
        self.dicViewData['groupData'] = self.importService('admin_user').get_group(uid, 4)
        self.display('detail', 'project')

    def create(self):
        dicArgs = {
            'advertiser_id': self.I('plan_advertiser_id'),
            'title': self.I('plan_title'),
            'brief': self.I('plan_brief'),
            'time_begin': self.I('plan_time_begin'),
            'time_end': self.I('plan_time_end'),
            'money': self.I('plan_money')
        }
        status = self.projectService.create_plan(dicArgs)
        self.out(status)

    def update(self):
        dicArgs = {
            'id': self.I('plan_id'),
            'advertiser_id': self.I('plan_advertiser_id'),
            'title': self.I('plan_title'),
            'brief': self.I('plan_brief'),
            'strategy': self.I('plan_strategy'),
            'target': self.I('plan_target'),
            'time_begin': self.I('plan_time_begin'),
            'time_end': self.I('plan_time_end'),
            'money': self.I('plan_money'),
            'progress': self.I('plan_progress'),
            'follower': self.I('plan_follower'),
            'summary': self.I('plan_summary'),
        }
        self.projectService.update_plan(dicArgs)
        self.redirect('/project/plan?a=detail&id={pid}'.format(pid = dicArgs['id']))

    def delete(self):
        strId = self.I('id')
        self.projectService.delete_plan(strId)
        self.redirect('/project/plan')

    def plan_finish(self):
        strid = self.I('id')
        self.projectService.plan_finish(strid)
        self.redirect('/project/plan?a=detail&id=%s' % (strid))

    def follow(self):
        strid = self.I('id')
        remark = self.I('remark')
        group = self.I('group')
        uid = self.current_user.get('id')
        if group:
            group = group.split(',')
        status = self.projectService.follow_group(strid, group, uid, remark)
        self.out(status)
