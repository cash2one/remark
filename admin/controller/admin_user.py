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
        gid = self.I('group_id')
        if gid:
            gid = gid.split(',')
        else:
            gid = ['0']
        args = {
            "id" : self.I('id'),
            "remark" : self.I('follow_remark'),
            "user_group_id" : gid,
            "uid" : self.current_user.get('id')
        }
        status, group = self.importService('admin_user').update_media_follow_remark(args, self.mediaConf)
        if status==200:
            self.out(status)
        else:
            if '0' in group:
                self.out(status, '', ['默认'])
                return

            tupData = self.importService('admin_user').get_media_group(args['uid'], 1, group)
            groupName = [ item['name'] for item in tupData]
            self.out(status, '', groupName)

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

    def check_export(self):
        uid = self.current_user.get('id')

        mediaDay = self.importService('admin_user').check_day_export(uid, 1, self.datetime_timestamp())
        if mediaDay and len(mediaDay) >= self.mediaConf['meida_down_day_max']:
            self.out(self.CODE['SERVICE_USER_EXPORT_DAY_MAX_ERROR'], 'user export day max 20 counts', len(mediaDay))

        self.out(self.CODE['DB_OK'])

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
        service.set_export(uid, gid, 1)

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
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        intPageDataNum = 10
        # 分页url
        text = self.I('text')
        lisSearchCondition = []
        lisSearchCondition.append("text=%s" % (text))

        strPageUrl = '/admin_user/user_manage?'
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))

        lisAdminUser, intRows = self.importService('admin_user').getAdminUser(intPage, intPageDataNum, text)
        userData = self.importService('admin_user').get_all_user()
        tmpUser = {item['id']:(item['nickname'] or item['name']) for item in userData}
        self.dicViewData['searchCondition'] = text
        self.dicViewData['leader'] = tmpUser
        self.dicViewData['admin_user'] = lisAdminUser
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('user_manage', 'admin_user')

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
        self.out(dicResp['statusCode'])

    def password(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_user').updatePass(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/admin_user/user_manage'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def get_user(self):
        dicResp = self.importService('admin_user').get_all_user()
        self.out(200, '', dicResp)

class role_manage(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):

        self.display('role_manage', 'admin_user')

    def getRole(self):
        searchCondition = self.I('search')
        userRole = self.importService('admin_user').getAdminRole(searchCondition)
        lisAdminRole = {}
        lisAdminRole['userRole'] = userRole
        lisAdminRole['searchCondition'] = searchCondition
        self.out(200, '', lisAdminRole)

    def detail(self):
        strId = self.I('id')
        lisAdminRole = self.importService('admin_user').getUserRole(strId)
        self.dicViewData['admin_role'] = lisAdminRole
        self.display('detail', 'admin_user')

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
        args = {
            'role_id':self.I('role_id'),
            'role_label':self.I('role_label'),
            'role_module_id':self.I('role_module_id'),
            'role_access_id':self.I('role_access_id')
        }
        if args['role_access_id']:
            args['role_access_id'] = args['role_access_id'].split(',')

        dicResp = self.importService('admin_user').updateRole(args)
        self.out(dicResp['statusCode'])

    def deleteRole(self):
        strId = self.I('id')
        dicResp = self.importService('admin_user').deleteRole(strId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/admin_user/role_manage'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class permission_manager(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
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
        strPageUrl = "/admin_user/permission_manager?"
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))

        lisAdminModule, intRows = self.importService('admin_permission_manager').getModule(intPage, intPageDataNum, listSearch)
        self.dicViewData['admin_module'] = lisAdminModule
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('permission_manager', 'admin_user')

    def get_permission(self):
        lisAdminModule = self.importService('admin_permission_manager').getPermission()
        self.out(200, '', lisAdminModule)

    def create(self):
        dicArgs = {
            'label' : self.I('module_label'),
            'validity' : self.I('validity') or 1,
            'is_exsit_child' : self.I('is_exsit_child'),
            'class_active' : self.I('module_class_active'),
            'menu_route' : self.I('module_menu_route')
        }
        status = self.importService('admin_permission_manager').create_module(dicArgs)
        self.out(status)

    def update(self):
        dicArgs = {
            'id' : self.I('id'),
            'label' : self.I('editer_label'),
            'validity' : self.I('validity') or 1,
            'is_exsit_child' : self.I('editer_child'),
            'class_active' : self.I('editer_class_active'),
            'menu_route' : self.I('editer_menu_route'),
            'access_id' : self.I('access_id'),
            'sort' : self.I('editer_sort')
        }
        status = self.importService('admin_permission_manager').update(dicArgs)
        self.out(status)

    def changePermission(self):
        '''
            权限等级调换 -- parent_id 目标权限 -- access_id 自身权限
        '''
        parent_id = self.I('parent_id') or 0
        access_id = self.I('access_id') or 0
        status = self.importService('admin_permission_manager').changePermission(int(access_id), int(parent_id))
        self.out(status)

    def childModule(self):
        dicArgs = {
            'label' : self.I('label'),
            'validity' : self.I('validity') or 1,
            'is_exsit_child' : self.I('editer_child'),
            'menu_route' : self.I('menu_route'),
            'access_id' : self.I('access_id'),
            'access_level': self.I('access_level')
        }
        status = self.importService('admin_permission_manager').childModule(dicArgs)
        if status == 200:
            strRedirectUrl = '/admin_user/permission_manager'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        id=self.I('id')
        ischild=self.I('child')
        validity=self.I('validity') or 0
        status = self.importService('admin_permission_manager').delete(id, ischild, validity)
        self.out(status)

    def addAction(self):
        id=self.I('id')
        action_name=self.I('action_name')
        access_level=self.I('access_level')
        label=self.I('label')
        status = self.importService('admin_permission_manager').addAction(id, action_name, access_level,label)
        self.out(status)

    def updateAction(self):
        id=self.I('id')
        action_name=self.I('action_name')
        label=self.I('label')
        validity=self.I('validity') or 1
        status = self.importService('admin_permission_manager').updateAction(id, action_name, label, validity)
        self.out(status)

    def getAllPermission(self):
        tupData = self.importService('admin_permission_manager').getAllPermission()
        if tupData:
            self.out(200, '', tupData)
        else:
            self.out(401)

class user_role(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/admin_user/user_role?'

        text = self.I('text')
        lisSearchCondition = []
        lisSearchCondition.append("text=%s" % (text))

        lisAdminUser, intRows = self.importService('admin_user').getAdminUser(intPage, intPageDataNum, text, condition='user_role')
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['admin_user'] = lisAdminUser
        self.display('user_role', 'admin_user')

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

    def update_role(self):
        if self._POST:
            dicArgs = self.request.arguments
            if not isinstance(dicArgs, dict):
                self.redirect('/admin_user/user_role')
                return
            dicResp = self.importService('admin_user').update_role(dicArgs)
            self.out(dicResp['statusCode'])
        else:
            self.out(self.CODE['SERVICE_DB_ERROR'], 'request method error','')

class advertiser_follow(base.base):
    advertiserStatus_init = ["","销售线索","接触中","意向客户","成交客户"]
    status4=["","稳定客户","短期客户"]

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.user_id = self.current_user.get('id')
        self.project_service = self.importService('project_advertiser')
        self.mediaCommonService = self.importService('media_common')

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 搜索内容
        listSearch = {
            "searchType":self.I('searchType'),
            "search_txt":self.I('search_txt'),
            "search_level":self.I('search_level'),
            "sub_status":self.I('sub_status')
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

        tupData, intRows = self.project_service.get_advertiser(intPage, intPageDataNum, listSearch, uid)
        self.dicViewData['advertiser'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('advertiser_follow', 'admin_user')

    def detail(self):
        '''
        :func: 查看详细信息
        '''
        intId = int(self.I('id'))
        strType = self.I('type') or 'look'
        tupPlan = self.project_service.advertiser_plan(intId)
        self.dicViewData['plan'] = tupPlan

        uid = self.current_user.get('id')

        self.dicViewData['id'] = intId
        if strType == 'look':
            self.display('detail', 'admin_user')
        else:
            self.display('update', 'admin_user')

    def get_basic(self):
        intId = int(self.I('id'))
        dicAdvertiser_value = self.project_service.advertiser_basic(intId)
        dataDic = {}
        dataDic['detail_info_value'] = dicAdvertiser_value
        self.out(200, '', dataDic)

    def get_contact(self):
        intId = int(self.I('id'))
        dicResp = self.mediaCommonService.get_contact(intId, relation_type=2)
        dataDic = {}
        if dicResp:
            dataDic['detail_info_value'] = dicResp
            self.out(200, '', dataDic)
            return
        self.out(404)

    def get_text(self):
        intId = int(self.I('id'))
        dicAdvertiser_value = self.project_service.advertiser_text(intId)
        dataDic = {}
        dataDic['detail_info_value'] = dicAdvertiser_value
        self.out(200, '', dataDic)

    def get_plan(self):

        intId = int(self.I('id'))
        tupPlan = self.project_service.advertiser_plan(intId)
        dataDic = {}
        dataDic['plan'] = tupPlan
        self.out(200, ' ', dataDic)

    def create(self):
        dicArgs = {
            'company': self.I('advertiser_company'),
            'link': self.I('advertiser_link'),
            'remark': self.I('advertiser_remark'),
            'product_info': self.I('advertiser_product_info'),
            'audience_info': self.I('advertiser_audience_info')
        }
        # print dicArgs
        status = self.project_service.create_advertiser(dicArgs)
        self.out(status)

    def update_basic(self):
        sub_status=0
        id = self.I('id')
        if self.I('advertiser_status')=="4" :
            sub_status= self.I('sub_status')
        dicArgs = {
            'company': self.I('advertiser_company'),
            'company_short': self.I('advertiser_company_short'),
            'brief': self.I('advertiser_brief'),
            'link': self.I('advertiser_link'),
            'category': self.I('advertiser_category'),
            'area': self.I('advertiser_area'),
            'advertiser_status': self.I('advertiser_status'),
            'sub_status': sub_status,
        }
        status = self.project_service.update_advertiser(dicArgs, id)
        self.out(status)

    def update_text(self):
        id = self.I('id')
        dicArgs = {
            'company': self.I('advertiser_company'),
            'requirement': self.I('advertiser_requirement'),
            'progress': self.I('advertiser_progress'),
            'remark': self.I('advertiser_remark'),
            'product_info': self.I('advertiser_product_info'),
            'audience_info': self.I('advertiser_audience_info'),
        }
        #print dicArgs
        status = self.project_service.update_advertiser(dicArgs, id)
        self.out(status)

    def delete(self):
        strId = self.I('id')
        self.project_service.delete_advertiser(strId, self.user_id)
        self.redirect('/admin_user/advertiser_follow')

    def get_user(self):
        strId = self.I('id')
        userId = self.user_id
        if strId:
            tupData = self.project_service.getUser(strId, userId)
        else:
            tupData = self.project_service.getUser('', userId)
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def add_contact(self):
        dicArg = {
            'relation_type': 2,
            'relation_id': self.I('id'),
            'contact_person': self.I('advertiser_contact_person'),
            'contact_position': self.I('advertiser_contact_position'),
            'contact_phone': self.I('advertiser_contact_phone'),
            'contact_qq': self.I('advertiser_contact_qq'),
            'contact_wechat': self.I('advertiser_contact_wechat'),
            'contact_email': self.I('advertiser_contact_email'),
            'contact_tel': self.I('advertiser_contact_tel'),
            'contact_other': self.I('advertiser_contact_other')
        }
        status = self.mediaCommonService.add_contact(dicArg)
        self.out(status)

    def delete_contact(self):
        dicArgs = {
            "contact_id" : self.I('id'),
            "relation_id" : self.I('relation_id'),
            "relation_type": 2
        }
        status = self.mediaCommonService.del_contact(dicArgs)
        self.out(status)

    def update_contact(self):
        dicArg = {
            'id': self.I('contact_id'),
            'contact_person': self.I('advertiser_contact_person'),
            'contact_position': self.I('advertiser_contact_position'),
            'contact_phone': self.I('advertiser_contact_phone'),
            'contact_qq': self.I('advertiser_contact_qq'),
            'contact_wechat': self.I('advertiser_contact_wechat'),
            'contact_email': self.I('advertiser_contact_email'),
            'contact_tel': self.I('advertiser_contact_tel'),
            'contact_other': self.I('advertiser_contact_other')
        }
        status = self.mediaCommonService.update_contact(dicArg)
        self.out(status)

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

class feedback_follow(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        uid = self.current_user.get('id')
        dicData = self.importService('admin_user').get_feedback_follow(uid)
        group = self.importService('admin_user').get_group(uid, 6)
        feedbackData = self.importService('admin_user').get_feedback(uid)
        group_name = {i['id']: i['name'] for i in group}
        group_name.update({0: '默认'})
        self.dicViewData['feedback'] = dicData
        self.dicViewData['group'] = group
        self.dicViewData['group_name'] = group_name
        self.dicViewData['feedbackData'] = feedbackData
        self.display('feedback_follow', 'admin_user')

    def create(self):
        group = self.I('group')
        uid = self.current_user.get('id')
        status = self.importService('admin_user').create_group(uid, group, 6)
        self.out(status)

    def update(self):
        id = self.I('id')
        name = self.I('group_name')
        status = self.importService('admin_user').update_group(id, name, 6)
        self.out(status)

    def delete(self):
        id = self.I('id')
        status = self.importService('admin_user').delete_group(id, 6)
        self.display('feedback_follow', 'admin_user')

    def remark(self):
        feedback_id = self.I('id')
        group_id = self.I('group_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        if group_id:
            group_id = group_id.split(',')
        else:
            group_id = ['0']
        status = self.importService('admin_user').update_feedback_remark(feedback_id, group_id, remark, uid)
        self.out(status)

class operation_log(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        lisSearchCondition = []
        listSearch = {
            "search_txt":self.I('search_txt')
        }
        for key in listSearch:
            value = listSearch[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/admin_user/operation_log?'
        tupData, intRows = self.importService('admin_access_permission').get_log(intPage, intPageDataNum, listSearch)
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))
        self.dicViewData['logData'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('operation_log', 'admin_user')
