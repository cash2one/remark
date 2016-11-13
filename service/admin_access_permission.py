# -*- coding:utf-8 -*-

import base



class service(base.baseService):
    # PASSTIME = 1296000  # 60*60*24*15  15天,用户操作的模块记录的过期时间
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.adminUserModel = self.importModel('admin_user')
        self.adminPermissionModel = self.importModel('admin_permission')
        self.adminAccessPermission = self.importModel('admin_access_permission')
        self.adminUserRoleModel = self.importModel('admin_user_role')
        self.adminRolePermissionModel = self.importModel('admin_role_permission')

    def getUserStatus(self, user_id):
        userStatus = self.adminUserModel.findOne({
            'fields': ['id'],
            'condition': 'status=0 and id = %d' % int(user_id)
        })
        return userStatus

    def getUserModuleId(self, permission_id):
        searchModule = "id = \'{id}\'".format(id=permission_id)
        userStatus = self.adminPermissionModel.findMany({
            'fields': ['id'],
            'condition': '{condition}'.format(condition=searchModule)
        })
        return userStatus

    def adminModuleIndex(self, user_id, id, url):
        self.adminAccessPermission.insert({
            'key': 'user_id, permission_id, url, create_time',
            'val': '{uid}, {mid}, \'{url}\', {ct}'.format(uid=user_id, mid=id, url=url, ct=int(self.time.time()))
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def getUserIndex(self, user_id, ACCESSTIME):
        val_time = int(self.time.time()) - ACCESSTIME
        # print "startTime = {st} and endTime = {et} ".format(st=val_time,et=int(self.time.time()))
        data = self.adminAccessPermission.findOne({
            'fields': ['count(1) as counts'],
            'condition': 'user_id = {Uid} and create_time >= {ct}'.format(Uid=user_id, ct=val_time)
        })
        return  data['counts']

    def setUserInvalidity(self, user_id):
        self.adminUserModel.update({
            'fields': ['status = 1'],
            'condition': 'id = {uid}'.format(uid=user_id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def deleteUserIndex(self, PASSTIME):
        val_time = int(self.time.time()) - PASSTIME   #超过半个月的用户操作记录，清除
        self.adminAccessPermission.delete({
            'condition': 'user_id>0 and create_time < {ct}'.format(ct=val_time)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def getUserRole(self, uid):
        data = self.adminUserRoleModel.findOne({
            'fields': ['role_id'],
            'condition': 'user_id = {uid}'.format(uid=uid)
        })
        return data

    def getRoleOpera(self, role, permission):
        data = self.adminRolePermissionModel.findOne({
            'fields': ['access_operat'],
            'condition': 'role_id = {rid} and permission_id = {mid}'.format(rid=role, mid=permission)
        })
        return data

    def get_log(self, intPage, intPageDataNum, listSearch):
        searchCondition=''
        if 'search_txt' in listSearch.keys():
            searchCondition = ' (ac.url like \'%{url}%\'  or au.nickname like \'%{url}%\')'.format(url = listSearch['search_txt'])
        tupData, intRows = self.adminAccessPermission.findPaginateAs(
            self.dicConfig['DB_ADMIN'] +'.user_access_permission as ac' ,{
                'fields': ['ac.*, au.nickname,au.name'],
                'join':  self.dicConfig['DB_ADMIN'] +'.user as au ON(ac.user_id = au.id )' ,
                'condition': '{search}'.format(search=searchCondition),
                'page': [intPage, intPageDataNum],
                'order': 'create_time desc'
            })
        for idx, i in enumerate(tupData, 1):
            i['name'] = i['nickname'] or i['name']
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
        return tupData, intRows