# -*- coding:utf-8 -*-

import base

class demand(base.base):

    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.project_demand_service = self.importService('project_demand')

    def index(self):
        strMenu = 'project_demand'
        # 页码
        intPage = int(self.I('page', 1))
        # 搜索内容
        strSearch = self.I('search')
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/demand?'
        tupData, intRows = self.project_demand_service.get_plan_demand(intPage, intPageDataNum, strSearch)
        self.dicViewData['demand'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['menu'] = strMenu
        self.display('demand', 'project')

    def detail(self):
        strMenu = 'project_demand'
        plan_demand_id = self.I('id')
        uid = self.current_user.get('id')
        follow = self.project_demand_service.check_follow(plan_demand_id, uid)
        tupGroup = self.importService('admin_user').get_group(uid, 2)
        self.dicViewData['follow'] = follow
        self.dicViewData['group'] = tupGroup
        self.dicViewData['detail'] = self.project_demand_service.get_one_demand(plan_demand_id)
        self.dicViewData['fd_info'] = self.project_demand_service.get_fd_info(plan_demand_id)
        self.dicViewData['media'] = self.project_demand_service.get_demand_media(plan_demand_id)

        self.dicViewData['menu'] = strMenu
        self.display('detail', 'project')

    def follow(self):
        did = self.I('plan_demand_id')
        uid = self.current_user.get('id')
        remark = self.I('remark')
        gid = self.I('group_id')
        if gid:
            gid = gid.split(',')
        else:
            gid = []
        resp = self.project_demand_service.follow(did, uid, gid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        dicArgs = {
            'plan_id': self.I('plan_id'),
            'name': self.I('name'),
            'start_time': self.I('start_time'),
            'end_time': self.I('end_time'),
            'description': self.I('description'),
            'money': self.I('money')
        }
        #print dicArgs
        self.project_demand_service.create_demand(dicArgs)
        self.redirect('/project/plan?a=detail&id={0}'.format(dicArgs['plan_id']))

    def update(self):
        dicArgs = {
            'id': self.I('id'),
            'name': self.I('name'),
            'money': self.I('money', '0'),
            'start_time': self.I('start_time'),
            'end_time': self.I('end_time'),
            'follower': self.I('follower'),
            'summary': self.I('summary'),
            'target': self.I('target'),
            'description': self.I('description'),
            'status': self.I('status'),
        }
        self.project_demand_service.update_demand(dicArgs)
        self.redirect('/project/demand?a=detail&id={pid}'.format(pid = dicArgs['id']))

    def delete(self):
        strId = self.I('id')
        self.project_demand_service.delete_plan_demand(strId)
        self.redirect('/project/demand')

    def create_potential(self):
        plan_id = self.I('plan_id')
        id = self.I('id')
        media_id = self.I('media_id')

        status = self.project_demand_service.create_potential(id, plan_id, media_id)
        self.out(status)

    def update_potential(self):
        dicArgs = {
            'id': self.I('id'),
            'link': self.I('link'),
            'money': self.I('money'),
            'start_time': self.I('start_time'),
            'remark': self.I('remark'),
            'description': self.I('description', ''),
            'status': self.I('status')
        }
        # id = self.I('id')
        # description = self.I('description')
        # status = self.I('status')
        status = self.project_demand_service.update_potential(dicArgs)
        self.out(status)

