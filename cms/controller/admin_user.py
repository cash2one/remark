# -*- coding:utf-8 -*-

import base


class center(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'center'
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').index(uid)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = dicData
        self.display('index', 'admin_user')

    def changPass(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').changePass(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/admin_user/center'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def checkOldPass(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            dicResp = self.importService('admin_user').checkOldPass(args)
            statusCode = dicResp['statusCode']
            self.out(statusCode, '', {})

    def update(self):
        if self._POST:
            uid = self.current_user.get('id')
            args = self.request.arguments
            args['user_id'] = uid
            dicResp = self.importService('admin_user').updateAccout(args)
            self.out(dicResp['statusCode'])
        else:
            self.out(500)

class media_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_follow'
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_follow_media(uid)
        tupGroup = self.importService('admin_user').get_group(uid, 1)
        mediaFow = self.importService('admin_user').get_media_follow(uid)
        group_name = {i['id']: i['name'] for i in tupGroup}
        group_name.update({0: '默认'})
        column = self.importService('admin_user').get_media_column()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['media'] = dicData
        self.dicViewData['group'] = tupGroup
        self.dicViewData['mediaFow'] = mediaFow
        self.dicViewData['group_name'] = group_name
        self.dicViewData['column'] = column
        self.display('follow', 'admin_user')

    def update_remark(self):
        args = {
            "id" : self.I('id'),
            "remark" : self.I('follow_remark'),
            "user_group_id" : self.II('user_group_id') or ['0'],
            "uid" : self.current_user.get('id')
        }
        status = self.importService('admin_user').update_media_follow_remark(args)
        if status == 200:
            strRedirectUrl = '/admin_user/media_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update_group(self):
        gid = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(gid, name, 1)
        if status == 200:
            strRedirectUrl = '/admin_user/media_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete_group(self):
        gid = self.I('id')
        status = self.importService('admin_user').delete_group(gid, 1)
        if status == 200:
            strRedirectUrl = '/admin_user/media_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def create_group(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 1)
        self.out(status)

    def export(self):
        gid = self.I('group')
        col = self.I('column')
        if not gid or not col:
            return
        uid = self.current_user.get('id')
        service = self.importService('admin_user')
        file_name = 'follow_media_' + str(int(self.time.time())) + '.xlsx'
        path = self.dicConfig['UPLOAD_PATH'] + "/static/data/" + file_name
        data = service.get_follow_media_detail(uid, gid, col)
        service.write_to_excel(path, data)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        buf_size = 1024
        # print "path = ", path
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

class demand_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'demand_follow'
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_follow_demand(uid)
        tupGroup = self.importService('admin_user').get_group(uid, 2)
        demandData = self.importService('admin_user').get_demand_follow(uid)
        group_name = {i['id']: i['name'] for i in tupGroup}
        group_name.update({0: '默认'})
        self.dicViewData['menu'] = strMenu
        self.dicViewData['demand'] = dicData
        self.dicViewData['group'] = tupGroup
        self.dicViewData['group_name'] = group_name
        self.dicViewData['demandData'] = demandData
        self.display('follow', 'admin_user')

    def update_remark(self):
        args = {
            "demand_id" : self.I('id'),
            "remark" : self.I('follow_remark'),
            "gid" : self.II('group_id'),
            "uid" : self.current_user.get('id')
        }
        if not args['gid']:
            args['gid']=['0']
        status = self.importService('admin_user').update_demand_follow_remark(args)
        if status == 200:
            strRedirectUrl = '/admin_user/demand_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update_group(self):
        gid = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(gid, name, 2)
        if status == 200:
            strRedirectUrl = '/admin_user/demand_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete_group(self):
        gid = self.I('id')
        status = self.importService('admin_user').delete_group(gid, 2)
        if status == 200:
            strRedirectUrl = '/admin_user/demand_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def create_group(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 2)
        self.out(status)

class user_manage(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'manager_user'
        lisAdminUser = self.importService('admin_user').getAdminUser()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['admin_user'] = lisAdminUser
        self.display('user_manage', 'admin_user')

    def getRole(self):
        strId = self.I('id')
        if strId:
            tupData = self.importService('admin_user').getRoleOption(strId)
        else:
            tupData = self.importService('admin_user').getRoleOption()
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def create(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.out(500)
            dicResp = self.importService('admin_user').createUser(args)
            self.out(dicResp['statusCode'])
        else:
            self.out(500)

    def update(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.out(500)
            dicResp = self.importService('admin_user').updateUser(args)
            self.out(dicResp['statusCode'])
        else:
            self.out(500)


    def delete(self):
        strId = self.I('id')
        dicResp = self.importService('admin_user').deleteUser(strId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/admin_user/user_manage'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class role_manage(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'manager_permissions'
        lisAdminRole = self.importService('admin_user').getAdminRole()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['admin_role'] = lisAdminRole
        self.display('role_manage', 'admin_user')

    def getModule(self):
        strId = self.I('id')
        if strId:
            tupData = self.importService('admin_user').getAdminModule(strId)
        else:
            tupData = self.importService('admin_user').getAdminModule()
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def create(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').createRole(args)
            self.out(dicResp['statusCode'])
        else:
            self.out(500)

    def update(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').updateRole(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/admin_user/role_manage'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def deleteRole(self):
        strId = self.I('id')
        dicResp = self.importService('admin_user').deleteRole(strId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/admin_user/role_manage'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class module_manager(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'manager_module'
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1

        listSearch = {
            "searchType":self.I('searchType'),
            "search_txt":self.I('search_txt'),
            "search_level":self.I('search_level')
        }
        lisSearchCondition = []
        for key in listSearch:
            value = listSearch[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))

        # 单页数据条数
        intPageDataNum = 10
        strPageUrl = "/admin_user/module_manager?"
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))

        lisAdminModule, intRows = self.importService('admin_module_manager').getModule(intPage, intPageDataNum, listSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['admin_module'] = lisAdminModule
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('module_manager', 'admin_user')

    def create(self):
        dicArgs = {
            'label' : self.I('module_label'),
            'name' : self.I('module_name'),
            'is_exsit_child' : self.I('is_exsit_child'),
            'class_active' : self.I('module_class_active'),
            'menu_route' : self.I('module_menu_route')
        }
        status = self.importService('admin_module_manager').create_module(dicArgs)
        if status == 200:
            strRedirectUrl = '/admin_user/module_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        dicArgs = {
            'id' : self.I('id'),
            'label' : self.I('editer_label'),
            'name' : self.I('editer_name'),
            'is_exsit_child' : self.I('editer_child'),
            'class_active' : self.I('editer_class_active'),
            'menu_route' : self.I('editer_menu_route'),
            'access_id' : self.I('access_id'),
            'sort' : self.I('editer_sort')
        }
        status = self.importService('admin_module_manager').update(dicArgs)
        if status == 200:
            strRedirectUrl = '/admin_user/module_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def childModule(self):
        dicArgs = {
            'label' : self.I('label'),
            'name' : self.I('name'),
            'is_exsit_child' : self.I('editer_child'),
            'class_active' : self.I('class_active'),
            'menu_route' : self.I('menu_route'),
            'access_id' : self.I('access_id'),
            'access_level': self.I('access_level')
        }
        # print "dicArgs = ",dicArgs
        status = self.importService('admin_module_manager').childModule(dicArgs)
        if status == 200:
            strRedirectUrl = '/admin_user/module_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        id=self.I('id')
        ischild=self.I('child')
        status = self.importService('admin_module_manager').delete(id, ischild)
        if status == 200:
            strRedirectUrl = '/admin_user/module_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def module(self):
        userModule = self.I('userModule')
        self.set_secure_cookie("userModule",userModule, expires=self.time.time() + 1800)

    def getModule(self):
        userModule = self.get_secure_cookie('userModule')
        self.out(200, '', {"userModule":userModule})


class passwd_manage(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'passwd_manage'
        lisAdminUser = self.importService('admin_user').getAdminUser()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['admin_user'] = lisAdminUser
        self.display('passwd_manage', 'admin_user')

    def password(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').updatePass(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/admin_user/passwd_manager'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        strId = self.I('id')
        dicResp = self.importService('admin_user').deleteUser(strId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/admin_user/passwd_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

class advertiser_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.profileService = self.importService('pf_advertiser')

    def index(self):
        strMenu = 'advertiser_follow'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 搜索内容
        listSearch = {
            "searchType":self.I('searchType'),
            "search_txt":self.I('search_txt'),
            "search_level":self.I('search_level')
        }
        uid = self.current_user.get('id')
        lisSearchCondition = []
        for key in listSearch:
            value = listSearch[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))

        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/admin_user/advertiser_follow?'
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))

        tupData, intRows = self.profileService.get_advertiser(intPage, intPageDataNum, listSearch, uid)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['advertiser'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('advertiser_follow', 'admin_user')

    def delete(self):
        adId = self.I('id')
        status = self.profileService.delete_advertiser(adId)
        if status == 200:
            strRedirectUrl = '/admin_user/advertiser_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class document_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'document_follow'
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_document_follow(uid)
        tupGroup = self.importService('admin_user').get_group(uid, 3)
        demandData = self.importService('admin_user').get_follow_follow(uid)
        group_name = {i['id']: i['name'] for i in tupGroup}
        group_name.update({0: '默认'})
        self.dicViewData['menu'] = strMenu
        self.dicViewData['document'] = dicData
        self.dicViewData['group'] = tupGroup
        self.dicViewData['group_name'] = group_name
        self.dicViewData['documentData'] = demandData

        self.display('document_follow', 'admin_user')

    def create(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 3)
        self.out(status)

    def delete(self):
        group = self.I('id')
        status = self.importService('admin_user').delete_group(group, 3)
        if status == 200:
            strRedirectUrl = '/admin_user/document_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def remark(self):
        documentID = self.I('id')
        group_id = self.I('group_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        if group_id:
            group_id = group_id.split(',')
        else:
            group_id = ['0']

        status = self.importService('admin_user').update_document_remark(documentID, group_id, remark, uid)
        self.out(status)

    def update(self):
        gid = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(gid, name, 3)
        if status == 200:
            strRedirectUrl = '/admin_user/document_follow'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

class plan_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_plan_follow(uid)
        group = self.importService('admin_user').get_group(uid, 4)
        planData = self.importService('admin_user').get_plan(uid)
        group_name = {i['id']: i['name'] for i in group}
        group_name.update({0: '默认'})
        self.dicViewData['plan'] = dicData
        self.dicViewData['group'] = group
        self.dicViewData['group_name'] = group_name
        self.dicViewData['planData'] = planData
        self.display('plan_follow', 'admin_user')

    def create(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 4)
        self.out(status)

    def delete(self):
        id = self.I('id')
        status = self.importService('admin_user').delete_group(id, 4)
        self.display('plan_follow', 'admin_user')

    def update(self):
        id = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(id, name, 4)
        self.out(status)

    def remark(self):
        planID = self.I('id')
        group_id = self.I('group_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        if group_id:
            group_id = group_id.split(',')
        else:
            group_id = ['0']

        status = self.importService('admin_user').update_plan_remark(planID, group_id, remark, uid)
        self.out(status)

class planning_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_planning_follow(uid)
        group = self.importService('admin_user').get_group(uid, 5)
        planningData = self.importService('admin_user').get_planning(uid)
        group_name = {i['id']: i['name'] for i in group}
        group_name.update({0: '默认'})
        self.dicViewData['planning'] = dicData
        self.dicViewData['group'] = group
        self.dicViewData['group_name'] = group_name
        self.dicViewData['planningData'] = planningData
        self.display('planning_follow', 'admin_user')

    def create(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 5)
        self.out(status)

    def delete(self):
        id = self.I('id')
        status = self.importService('admin_user').delete_group(id, 5)
        self.display('planning_follow', 'admin_user')

    def update(self):
        id = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(id, name, 5)
        self.out(status)

    def remark(self):
        planningID = self.I('id')
        group_id = self.I('group_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        if group_id:
            group_id = group_id.split(',')
        else:
            group_id = ['0']
        status = self.importService('admin_user').update_planning_remark(planningID, group_id, remark, uid)
        self.out(status)



