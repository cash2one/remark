# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.userRoleModel = self.importModel('admin_user_role')
        self.rolePermissionModel = self.importModel('admin_role_permission')
        self.adminPermissionModel = self.importModel('admin_permission')

    def getUserRole(self, userId):
        tupData = self.userRoleModel.findManyAs(
            self.dicConfig['DB_ADMIN'] + '.user_role as ur',
            {
                'fields': ['ur.role_id', 'r.name', 'r.label'],
                'join': self.dicConfig['DB_ADMIN'] + '.role as r ON (r.id = ur.role_id)',
                'condition': 'ur.user_id = {uid}'.format(uid=userId)
            }
        )
        return tupData

    def getRoleModule(self, roleId):
        tupData = self.rolePermissionModel.findManyAs(
            self.dicConfig['DB_ADMIN'] + '.role_permission as rm',
            {
                'fields': ['m.id'],
                'join': self.dicConfig['DB_ADMIN'] + '.permission as m ON (m.id = rm.permission_id)',
                'condition': 'rm.role_id = {rid}'.format(rid=roleId)
            }
        )
        return tupData

    def getUserModuleName(self, userId):
        tupData = self.getUserRole(userId)
        lisRoleIds = [i['role_id'] for i in tupData]
        length = len(lisRoleIds)

        lisModuleData = []
        if length == 0:
            return [], False
        elif length == 1:
            tupDataRoleModule = self.getRoleModule(lisRoleIds[0])
            lisModuleData = [str(i['id']) for i in tupDataRoleModule]
        else:
            strToint=[]
            for item in lisRoleIds:
                strToint.append(int(item))
            tupDataRoleModule = self.rolePermissionModel.findManyAs(
                self.dicConfig['DB_ADMIN'] + '.role_permission as rm',
                {
                    'fields': ['m.id as id'],
                    'join': self.dicConfig['DB_ADMIN'] + '.permission as m ON (m.id = rm.permission_id)',
                    'condition': 'm.validity!=0 and rm.role_id in {rid}'.format(rid=str(tuple(strToint)))
                }
            )
            lisModuleData = [str(i['id']) for i in tupDataRoleModule]

        if 1 in lisRoleIds:
            return lisModuleData, True
        else:
            return lisModuleData, False

    def getUserAccess(self):
        tupData = self.adminPermissionModel.findMany({
                'fields': ['id','name','label','access_id','access_level','parent_id','is_exsit_child','menu_route', 'validity'],
                'condition': 'tag=0 and validity!=0',
                'order': 'access_level,sort asc',
            })
        return tupData