# -*- coding:utf-8 -*-

import base

class service(base.baseService):

    exsit_child = ["否","是"]
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.cur_time = int(self.time.time())
        self.adminPermissionModel = self.importModel('admin_permission')

    def getModule(self, intPage, intPageDataNum, listSearch):
        condition = 'access_rw!=4 '
        if listSearch['searchType']=="1" and listSearch['search_txt']:
           condition += 'and name like \'%{search}%\' or ' \
                        'label like \'%{search}%\' '.format(search=listSearch['search_txt'])
        elif listSearch['searchType']=="2":
            dic = self.adminPermissionModel.findOne({
                'fields': ['access_id'],
                'condition': 'id = \'{nm}\''.format(nm=listSearch['search_txt'])
            })
            if len(dic)>0:
                condition += 'and parent_id = {pid}'.format(pid=dic['access_id'])
            else:
                condition += 'and parent_id = {pid}'.format(pid=1)
        elif listSearch['searchType']=="3":
            condition += ' and access_level = {le}'.format(le=listSearch['search_level'])
        tupData, intRows = self.adminPermissionModel.findPaginate({
            'condition':condition ,
             'page': [intPage, intPageDataNum],
        })
        return tupData, intRows

    def getPermission(self):
        condition = 'access_rw!=4 '
        tupData = self.adminPermissionModel.findMany({
            'fields': ['id, label, is_exsit_child, access_level, access_id, menu_route, parent_id, validity, tag, name'],
            'condition':condition ,
        })
        return tupData

    def check_value(self,dicArgs, checkType):
        if dicArgs['label'] ==None or dicArgs['name']==None :
            return 500
        if dicArgs['is_exsit_child'] == '0':
            if dicArgs['menu_route']==None :
                return 500
        else:
           dicArgs['menu_route'] =  ""

        isExsit=[]
        if checkType ==1 :          #check 防止新添加的名称已经存在数据库
            isExsit = self.adminPermissionModel.findOne({
                'fields': ['id'],
                'condition': 'name = \'{nm}\''.format(nm=dicArgs['name'])
            })
        elif checkType ==2:         #check 防止更新后的名称已经存在数据库
            isExsit = self.adminPermissionModel.findOne({
                'fields': ['access_id'],
                'condition': 'name = \'{nm}\''.format(nm=dicArgs['name'])
            })
            if len(isExsit)>0 and int(isExsit['access_id']) != int(dicArgs['access_id']):
                isExsit=[1]
            else:
                isExsit=[]

        if len(isExsit)>0:
            return 500
        return 200

    def create_module(self, dicArgs):
        # status = self.check_value(dicArgs, 1)
        # if status!=200:
        #     return 500

        data = self.adminPermissionModel.findOne({
            'fields': ['max(access_id) as aid']
        })
        self.adminPermissionModel.insert({
            'key': 'name, label, is_exsit_child, access_level, access_id, parent_id, menu_route, validity, create_time',
            'val': '\'{nm}\', \'{lb}\', {iec}, {al}, {aid}, 0, \'{mr}\', {val}, {ct}'.format(
                nm='', lb=dicArgs['label'], iec=dicArgs['is_exsit_child'],al=1, aid=data['aid']+1, mr=dicArgs['menu_route'], val=dicArgs['validity'],ct=self.cur_time
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def set_child_permission(self, accessID, validity):
        self.adminPermissionModel.update({
            'fields': ['validity= {val}'.format(val=validity) ],
            'condition': 'parent_id = \'{pid}\''.format(pid=accessID)
        })
        if self.model.db.status != 200:
            return 500

        data = self.adminPermissionModel.findMany({
            'fields' :['access_id','is_exsit_child'],
            'condition': 'parent_id ={aid}'.format(aid=accessID)
        })
        if len(data)>0:
            for item in data:
                if int(item['is_exsit_child'])>0:
                    self.set_child_permission(item['access_id'], validity)
        return 200

    def update(self, dicArgs):

        # status = self.check_value(dicArgs, 2)
        # if status!=200:
        #     return 500
        data = self.adminPermissionModel.findOne({
            'fields' :['is_exsit_child'],
            'condition': 'access_id ={aid}'.format(aid=dicArgs['access_id'])
        })

        data_list = ['name = \'{name}\''.format(name=''),
                   'label = \'{label}\''.format(label=dicArgs['label']),
                   'sort = {sort}'.format(sort=dicArgs['sort']),
                   'validity = \'{validity}\''.format(validity=dicArgs['validity']),
                   'menu_route = \'{route}\''.format(route=dicArgs['menu_route'])]

        if int(dicArgs['is_exsit_child']) == int(data['is_exsit_child']):
            self.adminPermissionModel.update({
                'fields': data_list,
                'condition': 'access_id = \'{aid}\''.format(aid=dicArgs['access_id'])
            })
            status = self.set_child_permission(dicArgs['access_id'], dicArgs['validity'])
            if status!=200:
                return 500
        else:
            if int(data['is_exsit_child'])==1:            #之前有子权限，现在撤销子权限
                data_list.append('is_exsit_child = 0')
                self.adminPermissionModel.update({
                    'fields': data_list,
                    'condition': 'access_id = \'{aid}\''.format(aid=dicArgs['access_id'])
                })
                status = self.set_child_permission(dicArgs['access_id'], 0) #设置为无效
                if status!=200:
                    return 500
            else:                                       #之前无子权限，现在加入子权限
                data_list.append('is_exsit_child = 1')
                self.adminPermissionModel.update({
                    'fields': data_list,
                    'condition': 'access_id = \'{aid}\''.format(aid=dicArgs['access_id'])
                })
        if self.model.db.status != 200:
            return 500
        return 200

    def childModule(self, dicArgs):
        # status = self.check_value(dicArgs, 1)
        # if status!=200:
        #     return 500

        # print "dicArgs = ", dicArgs
        data = self.adminPermissionModel.findOne({
            'fields': ['max(access_id) as aid']
        })
        self.adminPermissionModel.insert({
            'key': 'name, label, is_exsit_child, access_level, access_id, menu_route, parent_id, validity',
            'val': '\'{nm}\', \'{lb}\', {iec}, {al}, {aid}, \'{mr}\', {pid}, {val}'.format(
                nm='', lb=dicArgs['label'], iec=dicArgs['is_exsit_child'],al=int(dicArgs['access_level'])+1,
                aid=data['aid']+1, mr=dicArgs['menu_route'],pid=dicArgs['access_id'], val=dicArgs['validity']
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete(self, permissionID, ischild, validity):
        # print "moduleID = ", moduleID
        self.adminPermissionModel.update({
            'fields': ['validity= {val}'.format(val=validity) ],
            'condition': 'access_id = \'{aid}\''.format(aid=permissionID)
        })
        if self.model.db.status != 200:
            return 500

        if int(ischild)==1 :
            status = self.set_child_permission(permissionID, validity)        #   设置为无效
            if status!=200:
                return 500
        return 200

    def checkAction(self, parent_id, action_name):
        #print "4444 parent_id = ",parent_id, action_name
        actionData = self.adminPermissionModel.findOne({
            'fields': ['id, access_level'],
            'condition': 'validity!=0 and tag=1 and parent_id = {aid} and name=\'{name}\' '.format(aid=parent_id, name=action_name)
        })
        if actionData:
            return True, actionData
        else:
            data = self.adminPermissionModel.findOne({
                'fields': ['access_id, access_level'],
                'condition': 'validity!=0 and access_id = {id} and tag=0'.format(id=parent_id)
            })
            return False, data

    def addAction(self, id, action_name, access_level, label):
        data = self.adminPermissionModel.findOne({
            'fields': ['max(access_id) as aid']
        })
        self.adminPermissionModel.insert({
            'key': 'name, access_level, access_id, parent_id, tag, label, create_time',
            'val': '\'{nm}\', \'{al}\', \'{aid}\', {pid}, {ty}, \'{label}\', {ct}'.format(
                nm=action_name, al=int(access_level)+1,
                aid=data['aid']+1, pid=id, ty=1, label=label, ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def updateAction(self, id, action_name, label, validity):
        self.adminPermissionModel.update({
            'fields': ['name = \'{name}\''.format(name=action_name),
                       'label = \'{label}\''.format(label=label),
                       'validity = {va}'.format(va=validity)],
            'condition': 'id = \'{id}\''.format(id=id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def changeChildPermission(self, access_id, level):
        self.adminPermissionModel.update({
            'fields':['access_level=\'{level}\''.format(level=level)],
            'condition': 'parent_id = {id}'.format(id=access_id)
        })
        if self.model.db.status != 200:
            return 500

        permissionData = self.adminPermissionModel.findMany({
            'fields':['access_id, is_exsit_child'],
            'condition':'parent_id = {id}'.format(id=access_id)
        })
        level+=1
        for item in permissionData:
            if item['is_exsit_child']==1:
                self.changeChildPermission(item['access_id'], level)
        return 200

    def setPermissionGrade(self, level, access_id, parent_id, accessData):
        level+=1
        self.adminPermissionModel.update({
            'fields': ['parent_id={pid}, access_level=\'{level}\''.format(pid=parent_id, level=level)],
            'condition': 'access_id = {id}'.format(id=access_id)
        })
        if self.model.db.status != 200:
            return 500

        if accessData and (accessData['is_exsit_child']==1):
            status = self.changeChildPermission(access_id, level+1)
            if status != 200:
                return status
        return 200

    def changePermission(self, access_id, parent_id):
        if access_id <= 0 or parent_id < 0 or (access_id==parent_id):
            return 401
        if parent_id == 0:

            accessData = self.adminPermissionModel.findOne({
                'fields': ['is_exsit_child, access_level, access_id, menu_route, parent_id, validity, tag'],
                'condition':'access_id = {id}'.format(id=access_id)
            })
            if not accessData or (accessData and (accessData['validity']==0 or accessData['tag']==1)):
                return 401

            level = 0
            status = self.setPermissionGrade(level, access_id, 0, accessData)
            if status != 200:
                return status
        else:
            parentData = self.adminPermissionModel.findOne({
                'fields': ['is_exsit_child, access_level, access_id, menu_route, parent_id, validity, tag'],
                'condition':'access_id = {id}'.format(id=parent_id)
            })
            if not parentData or (parentData and (parentData['validity']==0 or parentData['tag']==1)):
                return 401

            accessData = self.adminPermissionModel.findOne({
                'fields': ['is_exsit_child, access_level, access_id, menu_route, parent_id, validity, tag'],
                'condition':'access_id = {id}'.format(id=access_id)
            })
            if not accessData or (accessData and accessData['tag'] == 1):
                return 401

            level = int(parentData['access_level'])
            if parentData and parentData['is_exsit_child'] == 1:     # 父级存在子id
                status = self.setPermissionGrade(level, access_id, parent_id, accessData)
                if status != 200:
                    return status

            elif parentData and parentData['is_exsit_child'] == 0:   # 父级不存在子id
                self.adminPermissionModel.update({
                    'fields': ['is_exsit_child=1'],
                    'condition': 'access_id = {id}'.format(id=parent_id)
                })
                if self.model.db.status != 200:
                    return 500

                status = self.setPermissionGrade(level, access_id, parent_id, accessData)
                if status != 200:
                    return status
        return 200

    def getAllPermission(self):
        permissionData = self.adminPermissionModel.findMany({
            'fields': ['is_exsit_child, access_level, access_id, parent_id, label'],
            'condition':'tag = 0 and validity!=0'
        })
        return permissionData