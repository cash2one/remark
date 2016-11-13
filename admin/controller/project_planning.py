# -*- coding:utf-8 -*-

import base
from api.html import MYHTMLParser

class planning(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.projectService = self.importService('project_planning')

    def index(self):
        strMenu = 'planning_manager'
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1

        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/planning?'
        tupData, intRows = self.projectService.get_planningPage(intPage, intPageDataNum)
        for idx, item in enumerate(tupData, 1):
            item['idx'] = (intPage - 1) * intPageDataNum + idx
            item['updateTime'] = self.formatTime(item.get('updateTime'), '%Y-%m-%d')

        self.dicViewData['planning'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)

        self.dicViewData['menu'] = strMenu
        self.display('planning', 'project')

    def create(self):
        dicArgs = {
            "title":self.I('planning_title'),
            "content":self.I('planning_content'),
        }
        status = self.projectService.create(dicArgs)
        if status==200:
            strRedirectUrl = '/project/planning'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def details(self):
        planID = self.I('id')
        strMenu = 'planning_manager'
        uid = self.current_user.get('id')
        group = self.projectService.check_group(planID, uid)
        planInfo = self.projectService.details(planID)
        planInfo['updateTime'] = self.formatTime(planInfo.get('updateTime'), '%Y-%m-%d')
        planInfo['createTime'] = self.formatTime(planInfo.get('createTime'), '%Y-%m-%d')
        self.dicViewData['group'] = group
        self.dicViewData['groupData'] = self.importService('admin_user').get_group(uid, 5)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['planInfo'] = planInfo
        #print "group = ", group

        self.display('details', 'project')

    def update(self):
        dicArgs = {
            "id":self.I('id'),
            "title":self.I('planning_title'),
            "content":self.I('planning_content'),
        }
        strMenu = 'planning_manager'
        status = self.projectService.update(dicArgs)
        if status==200:
            planID = self.I('id')
            planInfo = self.projectService.details(planID)
            planInfo['updateTime'] = self.formatTime(planInfo.get('updateTime'), '%Y-%m-%d')
            planInfo['createTime'] = self.formatTime(planInfo.get('createTime'), '%Y-%m-%d')
            self.dicViewData['menu'] = strMenu
            self.dicViewData['planInfo'] = planInfo
            self.display('details', 'project')
        else:
            strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def load(self):
        sourceData = self.I('planInfo_content')
        file_name = self.I('planInfo_title')+".docx"
        path = self.dicConfig['UPLOAD_PATH'] + "/static/data/"+file_name
        documents_load= MYHTMLParser(path, self.I('planInfo_title'))
        documents_load.complete(sourceData)

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        buf_size = 1024
        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()
        try:
            import os
            os.remove(path)
        except Exception:
            pass
        return False

    def follow(self):
        strid = self.I('id')
        remark = self.I('remark')
        group = self.I('group')
        uid = self.current_user.get('id')
        if group:
            group = group.split(',')
        status = self.projectService.follow_group(strid, group, uid, remark)
        self.out(status)