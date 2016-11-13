# -*- coding:utf-8 -*-

import base
import json

class service(base.baseService):

    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.adminAccountModel = self.importModel('admin_account')
        self.adminUserModel = self.importModel('admin_user')
        self.adminRoleModel = self.importModel('admin_role')
        self.adminPermissionModel = self.importModel('admin_permission')
        self.adminUserRoleModel = self.importModel('admin_user_role')
        self.adminRolePermissionModel = self.importModel('admin_role_permission')
        self.adminAccessPermissionModule = self.importModel('admin_access_permission')
        self.advertiserFollowModel = self.importModel('advertiser_follow')
        self.documentFollowModel = self.importModel('document_follow')
        self.planFollowModel = self.importModel('plan_follow')
        self.planningFollowModel = self.importModel('planning_follow')
        self.feedbackFollowModel = self.importModel('feedback_follow')
        self.yidaoExportModel = self.importModel('yidao_export')

    def index(self, uid):
        dicData = self.adminAccountModel.findOne({
            'fields': ['account'],
            'condition': 'user_id = {uid}'.format(uid=uid)
        })
        dicDataUser = self.adminUserModel.findOne({
            'fields': ['name', 'phone', 'email', 'nickname','position', 'create_time'],
            'condition': 'id = {uid}'.format(uid=uid)
        })

        dicData.update(dicDataUser)
        dicData['create_time'] = self.formatTime(dicData.get('create_time'), '%Y-%m-%d')
        return dicData


    def get_follow_media(self, uid):
        tupData = self.importModel('project_media_follow').findManyAs(
            self.dicConfig['DB_PROJECT'] + '.media_follow as mf',
            {
                'join': self.dicConfig['DB_PROJECT'] + '.media as m ON (m.id = mf.media_id)',
                'condition': 'mf.user_id = {uid} and mf.status=1'.format(uid=uid)
            }
        )
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['create_time'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def get_media_group(self, uid, tag, gid):
        tupData = self.importModel('project_follow_group').findMany({
            'fields': ['name'],
            'condition': 'user_id = {uid} and category = {cg} and id in ({gid})'.format(uid=uid, cg=tag, gid=','.join(gid))
        })
        return tupData

    def update_media_follow_remark(self, args, mediaConf):

        mid = args['id']
        uid = args['uid']
        gid = args['user_group_id']
        remark = args['remark']
        dataDic = self.importModel('project_media_follow').findMany({
            'fields': ['group_id'],
            'condition': 'media_id = {id} and user_id = {uid} and status=1'.format(id=mid, uid=uid)
        })

        groupData = self.importModel('project_media_follow').findMany({
            'fields': ['count(1) as counts, group_id'],
            'condition': 'status=1 group by group_id '
        })
        tupGroup = { item['group_id']: item['counts'] for item in groupData}

        errorGroup = []
        for item in gid:
            if int(item) in tupGroup and tupGroup[int(item)]>=mediaConf['media_group_max']:
                errorGroup.append(item)

        if errorGroup:
            return 401, errorGroup
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in gid:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.importModel('project_media_follow').insert({
                    'key': 'user_id, media_id, group_id, remark, create_time',
                    'val': '{uid}, {mid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, mid=mid, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500

        for index in userGroup:
            if str(index) not in gid :
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.importModel('project_media_follow').update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'media_id = {id} and user_id = {uid} and group_id in ({gid}) and status=1'.format(id=mid, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.importModel('project_media_follow').update({
                'fields':['status=0'],
                'condition': 'media_id = {id} and user_id = {uid} and group_id in ({gid})'.format(id=mid, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200, errorGroup

    def get_media_follow(self, uid):
        tupData = self.importModel('project_media_follow').findMany({
            'fields': ['media_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['media_id'])] = str(item['media_id'])
        return dicData

    def get_demand_follow(self, uid):
        tupData = self.importModel('project_demand_follow').findMany({
            'fields': ['plan_demand_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['plan_demand_id'])] = str(item['plan_demand_id'])
        return dicData

    def get_follow_demand(self, uid):
        tupData = self.importModel('project_demand_follow').findManyAs(
            self.dicConfig['DB_PROJECT'] + '.demand_follow as df',
            {
                'join': self.dicConfig['DB_PROJECT'] + '.plan_demand as pd ON (pd.id = df.plan_demand_id)',
                'condition': 'df.user_id = {uid} and df.status=1'.format(uid=uid)
            }
        )
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['create_time'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def update_demand_follow_remark(self, args):
        demand_id = args['demand_id']
        uid = args['uid']
        gid = args['gid']
        remark = args['remark']
        dataDic = self.importModel('project_demand_follow').findMany({
            'fields': ['group_id'],
            'condition': 'plan_demand_id = {id} and user_id = {uid} and status=1'.format(id=demand_id, uid=uid)
        })
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in gid:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.importModel('project_demand_follow').insert({
                    'key': 'user_id, plan_demand_id, group_id, remark, create_time',
                    'val': '{uid}, {pid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, pid=demand_id, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500
        for index in userGroup:
            if str(index) not in gid:
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.importModel('project_demand_follow').update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'plan_demand_id = {id} and user_id = {uid} and group_id in ({gid}) and status=1'.format(id=demand_id, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.importModel('project_demand_follow').update({
                'fields':['status=0'],
                'condition': 'plan_demand_id = {id} and user_id = {uid} and group_id in ({gid}) and status=1'.format(id=demand_id, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200


    def create_group(self, uid, group, category):
        self.importModel('project_follow_group').insert({
            'key': 'user_id, name, category, create_time',
            'val': '{uid}, \'{name}\', {category}, {ct}'.format(
                uid=uid, name=group, category=category, ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_group(self, uid, category):
        tupData = self.importModel('project_follow_group').findMany({
            'condition': 'user_id = {uid} and category = {cg} and status=1'.format(uid=uid, cg=category)
        })
        for item in tupData:
            item['create_time'] = self.formatTime(item['create_time'], '%Y-%m-%d')
        return tupData

    def update_group(self, gid, name, category):
        self.importModel('project_follow_group').update({
            'fields': ['name = \'{name}\''.format(name=name)],
            'condition': 'id = {id} and status=1'.format(id=gid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def delete_group(self, gid, category):
        cur_time = int(self.time.time())
        if category == 1:
            self.importModel('project_media_follow').update({
                'fields':['status=0 and create_time=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        elif category == 2:
            self.importModel('project_demand_follow').update({
                'fields':['status=0 and create_time=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        elif category == 3:
            self.importModel('document_follow').update({
                'fields':['status=0 and createTime=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        elif category == 4:
            self.importModel('plan_follow').update({
                'fields':['status=0 and createTime=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        elif category == 5:
            self.importModel('planning_follow').update({
                'fields':['status=0 and createTime=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        elif category == 6:
            self.importModel('feedback_follow').update({
                'fields':['status=0 and create_time=\'{tm}\''.format(tm=cur_time)],
                'condition': 'group_id = {gid} and status=1'.format(gid=gid)
            })
        self.importModel('project_follow_group').update({
            'fields':['status=0 and create_time=\'{tm}\''.format(tm=cur_time)],
            'condition': 'id = {id} and category = {cg} and status=1'.format(id=gid, cg=category)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_media_column(self):
        return [('name','名称'), ('wechat_id', '微信号'), ('identify', '认证'), ('brief','简介'),
                ('top_avg_read_num', '头条阅读数'), ('like_num', '点赞数'), ('fans_num', '粉丝数'),
                ('first_price', '头条报价'), ('second_price', '二条报价'), ('other_price', '其它报价'),
                ('contact_person', '联系人'), ('contact_phone', '电话'), ('contact_qq', 'QQ'),
                ('contact_wechat', '微信'), ('remark', '备注')]

    def write_to_excel(self, file_name, data, has_title=True):
        import xlsxwriter
        workbook = xlsxwriter.Workbook(file_name)
        format_title=workbook.add_format()    # 定义format_title格式对象
        format_title.set_align('center')    # 定义format_title对象单元格居中对齐的格式
        format_title.set_bold()    # 定义format_title对象单元格内容加粗的格式
        keys = sorted(data.keys())
        for key in keys:
            if not isinstance(key, basestring):
                key = str(key)
            worksheet = workbook.add_worksheet(key)
            row, col = 0, 0
            for item in data[key]:
                if has_title and row == 0:
                    worksheet.write_row(row, col, item, format_title)
                else:
                    worksheet.write_row(row, col, item)
                row += 1
        workbook.close()


    def get_follow_media_detail(self, uid, gid, col):
        if isinstance(gid, list):
            gid = ','.join(gid)
        tupData = self.importModel('project_media_follow').findManyAs(
            self.dicConfig['DB_PROJECT'] + '.media_follow as mf',
            {
                'fields': ['m.*', 'mw.*', 'mf.*'],
                'join': self.dicConfig['DB_PROJECT'] + '.media as m ON (m.id = mf.media_id) left join ' +
                        self.dicConfig['DB_PROJECT'] + '.media_wechat as mw ON (mw.media_id = mf.media_id)',
                'condition': 'mf.user_id = {uid} and mf.group_id in ({gid}) and mf.status=1'.format(uid=uid, gid=gid)
            }
        )
        group = self.importModel('project_follow_group').findMany({
            'condition': 'status = 1'
        })
        dicGroup = {i['id']: i['name'] for i in group}
        dicGroup.update({0: u'默认'})
        dicData = {}
        if isinstance(col, basestring):
            col = [col]
        dic_col = {i[0]:i[1] for i in self.get_media_column()}
        titles = [dic_col.get(i, '').decode('u8') for i in col]
        for item in tupData:
            group_id = item['group_id']
            group_name = dicGroup.get(group_id, group_id)
            dicData.setdefault(group_name, [titles])
            # dicData[group_name].append(titles)
            col_data = []
            for k in col:
                col_data.append(item.get(k, ''))
            dicData[group_name].append(col_data)
        return dicData


    def changePass(self, dicArgs):
        """
        :func: 更改密码
        :param dicArgs: uid 旧密码 新密码
        """
        if 'user_id' in dicArgs and 'old_password' in dicArgs and 'new_password' in dicArgs:
            # 根据user_id查询用户
            dicUser = self.adminAccountModel.findOne({
                'condition': 'user_id = {uid}'.format(uid=dicArgs['user_id'])
            })
            if not dicUser:
                return {'statusCode': 601}
            # 检测旧密码是否正确
            if dicUser['password'] != self.hashlib.sha256(
                    '{pw} -- {salt}'.format(pw=dicArgs['old_password'][0], salt=dicUser['salt'])
            ).hexdigest():
                return {'statusCode': 603}
            # 更新新密码
            strNewPass = self.hashlib.sha256(
                '{pw} -- {salt}'.format(pw=dicArgs['new_password'][0], salt=dicUser['salt'])
            ).hexdigest()
            self.adminAccountModel.update({
                'fields': ['password = \'{new_pass}\''.format(new_pass=strNewPass)],
                'condition': 'user_id = {uid}'.format(uid=dicArgs['user_id'])
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def updatePass(self, dicArgs):

        if 'user_id' in dicArgs and 'update_password' in dicArgs:
            dicUser = self.adminAccountModel.findOne({
                'condition': 'user_id = {uid}'.format(uid=dicArgs['user_id'][0])
            })
            strNewPass = self.hashlib.sha256(
                '{pw} -- {salt}'.format(pw=dicArgs['update_password'][0], salt=dicUser['salt'])
            ).hexdigest()
            self.adminAccountModel.update({
                'fields': ['password = \'{new_pass}\''.format(new_pass=strNewPass)],
                'condition': 'user_id = {uid}'.format(uid=dicArgs['user_id'][0])
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def checkOldPass(self, dicArgs):
        try:
            if 'user_id' in dicArgs and 'old_password' in dicArgs:
                # 根据user_id查询用户
                dicUser = self.adminAccountModel.findOne({
                    'condition': 'user_id = {uid}'.format(uid=dicArgs['user_id'])
                })
                if not dicUser:
                    return {'statusCode': 601}
                # 检测旧密码是否正确
                if dicUser['password'] != self.hashlib.sha256(
                        '{pw} -- {salt}'.format(pw=dicArgs['old_password'][0], salt=dicUser['salt'])
                ).hexdigest():
                    return {'statusCode': 603}
                return {'statusCode': 200}
            else:
                return {'statusCode': 400}
        except Exception, e:
            print e
            return {'statusCode': 500}

    def updateAccout(self, dicArgs):
        if 'user_id' in dicArgs and 'user_nickname' in dicArgs and 'user_name' in dicArgs and 'user_phone' in dicArgs and 'user_position' in dicArgs:
            listData = ['user_name','user_phone','user_email']
            userData = self.get_user_data(dicArgs['user_id'])
            for item in (dicArgs):
                if item in listData and dicArgs[item][0]:
                    status = self.check_user_create(dicArgs[item][0], 2, dicArgs['user_id'])
                    if status != 200:
                        return {'statusCode': 401}    #认证失败

                    if dicArgs[item][0]:
                        checkData = self.adminAccountModel.findOne({
                            'fields':['id'],
                            'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'], data = dicArgs[item][0])
                        })
                    if not userData[0][item] or (not checkData and userData[0][item]==dicArgs[item][0]):
                        tupData = self.adminAccountModel.findOne({
                            'fields':['password, salt'],
                            'condition': 'user_id = \'{id}\' '.format(id=dicArgs['user_id'])
                        })
                        self.adminAccountModel.insert({
                            'key': 'user_id, account, password, salt',
                            'val': '{uid}, \'{un}\', \'{up}\', \'{us}\''.format(
                                uid=dicArgs['user_id'], un=dicArgs[item][0], up=tupData['password'], us=tupData['salt']
                            )
                        })
                        if self.model.db.status != 200:
                            return {'statusCode': 601}
                    elif userData[0][item] and  userData[0][item]!=dicArgs[item][0]:
                        # 更新用户
                        self.adminAccountModel.update({
                            'fields': ['account = \'{un}\''.format(un=dicArgs[item][0])],
                            'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'], data = userData[0][item])
                        })
                        if self.model.db.status != 200:
                            return {'statusCode': 601}

                elif item in listData and not dicArgs[item][0]:
                    self.adminAccountModel.delete({
                        'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'], data = userData[0][item])
                    })

            self.adminUserModel.update({
                'fields': ['name = \'{nm}\''.format(nm=dicArgs['user_name'][0]),
                           'nickname = \'{nk}\''.format(nk=dicArgs['user_nickname'][0]),
                           'phone = \'{ph}\''.format(ph=dicArgs['user_phone'][0]),
                           'email = \'{em}\''.format(em=dicArgs['user_email'][0]),
                           'position = \'{ps}\''.format(ps=dicArgs['user_position'][0])],
                'condition': 'id = {uid}'.format(uid=dicArgs['user_id'])
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}

            return {'statusCode': 200}
        return {'statusCode': 200}


    def getAdminUser(self,intPage, intPageDataNum, text=None, condition=None):
        if not condition :
            searchCondition = ''
        elif condition and text:
            searchCondition = 'status=0 and '
        elif condition and not text:
            searchCondition = 'status=0 '

        if text:
            searchCondition += ' (name like \'%{search}%\' or ' \
            'nickname like \'%{search}%\')'.format(search=text)

        tupData, intRows = self.adminUserModel.findPaginate({
            'page': [intPage, intPageDataNum],
            'condition': '%s' % searchCondition
        })

        tupDataRole = self.adminRoleModel.findMany({})
        dicRole = {i['id']: i['label'] for i in tupDataRole}
        for item in tupData:
            rolelist = []
            data = self.adminUserRoleModel.findMany({
                'fields':['role_id'],
                'condition': 'user_id = {uid}'.format(uid=item['id'])
            })
            for index in data:
                rolelist.append(dicRole.get(index['role_id'],'unknown'))
            item['role_label']=rolelist
        lisAdminUser = []
        for idx, i in enumerate(tupData):
            i['idx'] = idx + 1
            lisAdminUser.append(i)
        return lisAdminUser, intRows

    def check_user_create(self, data, type=1, uid=0):
        if uid==0:
            searchTxt = ""
        else:
            searchTxt = " and id={uid}".format(uid=uid)
        userData = self.adminUserModel.findMany({
            'fields':['id'],
            'condition':' phone = \'{search}\' or ' \
                          'email = \'{search}\' or ' \
                          'name = \'{search}\' {text}'.format(search=data, text=searchTxt)
        })
        if type==1:
            if len(userData)==0:
                return 200
        elif type==2:
            if (len(userData)==0) or (len(userData)==1 and int(uid)==int(userData[0]['id'])):
                return 200
        else:
            return 401

    def get_user_data(self, uid):
        userData = self.adminUserModel.findMany({
            'fields':['id, phone as user_phone, email as user_email, name as user_name, nickname'],
            'condition':' id= {uid}'.format(uid=uid)
        })
        return userData

    def createUser(self, dicArgs):
        if 'user_name' in dicArgs and 'user_password' in dicArgs and 'remark' in dicArgs :
            strUserName = dicArgs['user_name'][0]
            position = dicArgs['user_position'][0]
            remark = dicArgs['remark'][0]
            status = self.check_user_create(strUserName)
            if status != 200:
                return {'statusCode': 401}    #认证失败

            strSalt = self.salt()
            strPassWord = self.hashlib.sha256(
                '{pw} -- {salt}'.format(pw=dicArgs['user_password'][0], salt=strSalt)
            ).hexdigest()
            # 添加用户
            userId = self.adminUserModel.insert({
                'key': 'phone, email, nickname, name, status, create_time, position, remark',
                'val': '\'{ph}\', \'{em}\',  \'{nkm}\', \'{nm}\', {status}, {time}, \'{ps}\', \'{rm}\''.format(
                    ph="", em="",  nkm="", nm=strUserName, status=0, time=int(self.time.time()), ps=position, rm=remark
                )
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            self.adminAccountModel.insert({
                'key': 'user_id, account, password, salt',
                'val': '{uid}, \'{un}\', \'{up}\', \'{us}\''.format(
                    uid=userId, un=strUserName, up=strPassWord, us=strSalt
                )
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}

            role = self.adminRoleModel.findOne({
                'fields':['id'],
                'condition':'name = "schoolmate"'
            })
            # 添加用户身份关联
            for item in role:
                self.adminUserRoleModel.insert({
                    'key': 'user_id, role_id',
                    'val': '{uid}, {rid}'.format(uid=userId, rid=role[item])
                })
                if self.model.db.status != 200:
                    return {'statusCode': 601}
            #广告跟踪人默认加入
            advsList = self.advertiserFollowModel.findMany({
                'fields':['distinct advertiser_id'],
            })
            userLis = self.adminUserModel.findOne({
                'fields':['max(id) as id'],
            })
            for item in advsList:
                self.advertiserFollowModel.insert({
                    'key': 'advertiser_id, user_id, validity',
                    'val': '{aid}, {uid}, {va}'.format(aid=item['advertiser_id'], uid=userLis['id'],va=0)
                })
                if self.model.db.status != 200:
                    return {'statusCode': 601}
            return {'statusCode': 200}

        if 'update_password' in dicArgs and 'user_id' in dicArgs:
            strUserId = dicArgs['user_id'][0]
            strSalt = self.salt()
            strPassWord = self.hashlib.sha256(
                '{pw} -- {salt}'.format(pw=dicArgs['update_password'][0], salt=strSalt)
            ).hexdigest()

            self.adminAccountModel.update({
                'fields': ['password = \'{up}\''.format(up=strPassWord),
                           'salt = \'{us}\''.format(us=strSalt)],
                'condition': 'user_id = {uid}'.format(uid=strUserId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}
        else:
            return {'statusCode': 500}


    def updateUser(self, dicArgs):
        if 'user_id' in dicArgs and 'user_name' in dicArgs and 'user_status' in dicArgs and 'remark' in  dicArgs and 'leader' in dicArgs:
            listData = ['user_name','user_phone','user_email']
            userData = self.get_user_data(dicArgs['user_id'][0])
            for item in (dicArgs):

                if item in listData and dicArgs[item][0]:

                    status = self.check_user_create(dicArgs[item][0], 2, dicArgs['user_id'][0])
                    if status != 200:
                        return {'statusCode': 401}    #认证失败

                    if dicArgs[item][0]:
                        checkData = self.adminAccountModel.findOne({
                            'fields':['id'],
                            'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'][0], data = dicArgs[item][0])
                        })
                    if not userData[0][item] or (not checkData and userData[0][item]==dicArgs[item][0]):
                        tupData = self.adminAccountModel.findOne({
                            'fields':['password, salt'],
                            'condition': 'user_id = \'{id}\' '.format(id=dicArgs['user_id'][0])
                        })
                        self.adminAccountModel.insert({
                            'key': 'user_id, account, password, salt',
                            'val': '{uid}, \'{un}\', \'{up}\', \'{us}\''.format(
                                uid=dicArgs['user_id'][0], un=dicArgs[item][0], up=tupData['password'], us=tupData['salt']
                            )
                        })
                        if self.model.db.status != 200:
                            return {'statusCode': 601}
                    elif userData[0][item] and  userData[0][item]!=dicArgs[item][0]:

                        # 更新用户
                        self.adminAccountModel.update({
                            'fields': ['account = \'{un}\''.format(un=dicArgs[item][0])],
                            'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'][0], data = userData[0][item])
                        })
                        if self.model.db.status != 200:
                            return {'statusCode': 601}

                elif item in listData and not dicArgs[item][0]:
                    self.adminAccountModel.delete({
                        'condition': 'user_id = {uid} and account = \'{data}\''.format(uid=dicArgs['user_id'][0], data = userData[0][item])
                    })
            strUserId = dicArgs['user_id'][0]
            strUserName = dicArgs['user_name'][0]
            strUserNickname = dicArgs['user_nickname'][0]
            strStatus = dicArgs['user_status'][0]
            self.adminUserModel.update({
                'fields': ['nickname = \'{nn}\''.format(nn=strUserNickname),
                        'name = \'{name}\''.format(name =strUserName ),
                        'phone = \'{ph}\''.format(ph =dicArgs['user_phone'][0] ),
                        'email = \'{em}\''.format(em =dicArgs['user_email'][0] ),
                        'status = {st}'.format(st =strStatus ),
                        'position = \'{ps}\''.format(ps =dicArgs['user_position'][0] ),
                        'leader = \'{ld}\''.format(ld =dicArgs['leader'][0] ),
                        'remark = \'{rm}\''.format(rm =dicArgs['remark'][0] ),
                ],
                'condition': 'id = {uid}'.format(uid=strUserId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}
        else:
            return {'statusCode': 401}


    def deleteUser(self, strId):
        self.adminUserModel.delete({
            'condition': 'id = {uid}'.format(uid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        self.adminAccountModel.delete({
            'condition': 'user_id = {uid}'.format(uid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        self.adminUserRoleModel.delete({
            'condition': 'user_id = {uid}'.format(uid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def getAdminRole(self, searchCondition=None):
        condition = ''
        if searchCondition:
            condition = 'm.tag=0 and m.validity=1 and r.label like \'%{label}%\''.format(label=searchCondition)
        else:
            condition = 'm.tag=0 and m.validity=1 '

        tupData = self.adminRoleModel.findManyAs(
            self.model.dicConfig['DB_ADMIN'] + '.role_permission as rm',
            {
                'fields': ['r.id', 'r.label as role_label', 'm.label as module_label',
                           'm.access_level as level', 'm.access_id as accessId', 'm.parent_id as parentId','m.tag as tag'],
                'join': self.model.dicConfig['DB_ADMIN'] + '.role as r ON (r.id = rm.role_id) '
                        'LEFT JOIN ' + self.model.dicConfig['DB_ADMIN'] + '.permission as m ON (m.id = rm.permission_id )',
                'condition':condition
            }
        )
        dicAdminRole = {}
        for i in tupData:
            permission = []
            permission.append(i['module_label'])
            permission.append(int(i['level']))
            permission.append(i['accessId'])
            permission.append(i['parentId'])
            dicAdminRole.setdefault(i['id'], {'role_label': i['role_label'], 'permission':[]})
            # dicAdminRole[i['id']]['module_label'].append(i['module_label'])
            dicAdminRole[i['id']]['permission'].append(permission)
        lisAdminRole = []
        idx = 1
        for key in dicAdminRole:
            dicAdminRole[key]['id'] = key
            dicAdminRole[key]['idx'] = idx
            lisAdminRole.append(dicAdminRole[key])
            idx += 1
        return lisAdminRole

    def getUserRole(self, roleId):
        tupData = self.adminRoleModel.findOne({
            'condition': 'id = \'{id}\' '.format(id=roleId)
        })
        return tupData

    def createRole(self, dicArgs):
        if 'role_label' in dicArgs and 'role_module_id' in dicArgs:
            strRoleName = dicArgs['role_name'][0]
            strRoleLabel = dicArgs['role_label'][0]
            lisRoleModuleIds = json.loads(dicArgs['role_module_id'][0])
            check = self.adminRoleModel.findOne({
                'fields': ['id'],
                'condition': 'name = \'{name}\' '.format(name=strRoleName)
            })
            if len(check)>0:
                return {'statusCode': 401}

            check = self.adminRoleModel.findOne({
                'fields': ['id'],
                'condition': 'label = \'{label}\' '.format(label=strRoleLabel)
            })
            if len(check)>0:
                return {'statusCode': 401}
            # 添加身份
            roleId = self.adminRoleModel.insert({
                'key': 'name, label',
                'val': '\'{name}\', \'{label}\''.format(name=strRoleName, label=strRoleLabel)
            })
            # 添加身份权限模块关联
            for mid in lisRoleModuleIds:
                data = self.adminPermissionModel.findOne({
                    'fields': ['access_id'],
                    'condition': 'id = \'{id}\' '.format(id=mid)
                })
                if len(data)>0:
                    operatData = self.adminPermissionModel.findMany({
                    'fields': ['id'],
                    'condition': 'parent_id = \'{id}\' and tag=1 '.format(id=data['access_id'])
                    })
                    for item in operatData:
                        self.adminRolePermissionModel.insert({
                            'key': 'role_id, permission_id',
                            'val': '{rid}, {mid}'.format(rid=roleId, mid=item['id'])
                        })
                self.adminRolePermissionModel.insert({
                    'key': 'role_id, permission_id',
                    'val': '{rid}, {mid}'.format(rid=roleId, mid=mid)
                })
                if self.model.db.status != 200:
                    return {'statusCode': 601}
            return {'statusCode': 200}
        else:
            return {'statusCode': 500}


    def updateRole(self, dicArgs):
        if 'role_id' in dicArgs and 'role_label' in dicArgs and 'role_module_id' in dicArgs:
            strRoleId = dicArgs['role_id']
            strRoleLabel = dicArgs['role_label']
            lisRoleModuleIds = dicArgs['role_module_id']
            accessRole = dicArgs['role_access_id']

            if lisRoleModuleIds:
                lisRoleModuleIds = lisRoleModuleIds.split(',')
            # 更新身份
            self.adminRoleModel.update({
                'fields': ['label = \'{label}\''.format(label=strRoleLabel)],
                'condition': 'id = {rid}'.format(rid=strRoleId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            # 更新身份权限模块关联
            self.adminRolePermissionModel.delete({
                'condition': 'role_id = {rid}'.format(rid=strRoleId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}

            roleApret = {}
            for aid in accessRole:
                access = aid.split('_')[-1]
                module = aid.split('_')[0]
                if module in roleApret.keys():
                    roleApret[module] = 1<<(4-int(access))|int(roleApret[module])
                else:
                    data = 1<<(4-int(access))
                    roleApret[module] = data

            for mid in lisRoleModuleIds:
                if str(mid) in roleApret.keys():
                    access_operat = bin(int(roleApret[str(mid)])).replace('0b','').zfill(4)
                else:
                    access_operat = '1111'
                self.adminRolePermissionModel.insert({
                    'key': 'role_id, permission_id, access_operat',
                    'val': '{rid}, {mid}, \'{ao}\''.format(rid=strRoleId, mid=mid, ao= access_operat )
                })
                if self.model.db.status != 200:
                    return {'statusCode': 601}

        return {'statusCode': 200}

    def deleteRole(self, strId):
        self.adminRoleModel.delete({
            'condition': 'id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.adminUserRoleModel.delete({
            'condition': 'role_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.adminRolePermissionModel.delete({
            'condition': 'role_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def getAdminModule(self, intId=None):
        tupData = self.adminPermissionModel.findMany({
            'fields': ['id', 'label','access_id','parent_id','access_level','is_exsit_child', 'tag'],
            'condition':'validity!=0 ',
            'order':'access_level, sort asc'
        })
        checkedId = set()
        access_operat = {}
        if intId is not None:
            tupDataChecked = self.adminRolePermissionModel.findMany({
                'fields': ['permission_id', 'access_operat'],
                'condition': 'role_id = {rid}'.format(rid=intId)
            })
            checkedId = set([i['permission_id'] for i in tupDataChecked])
            access_operat = {i['permission_id']: i['access_operat'] for i in tupDataChecked}

        lisData = []
        for idx, i in enumerate(tupData):
            i['idx'] = idx + 1
            i['checked'] = 1 if i['id'] in checkedId else 0
            i['operat'] = access_operat[i['id']] if i['id'] in access_operat.keys() else '0000'
            lisData.append(i)
        return lisData

    def getRoleOption(self, intId=None):
        tupData = self.adminRoleModel.findMany({
            'fields': ['id', 'label']
        })
        checkedId = set()
        if intId is not None:
            tupDataChecked = self.adminUserRoleModel.findMany({
                'fields': ['role_id'],
                'condition': 'user_id = {uid}'.format(uid=intId)
            })
            checkedId = set([i['role_id'] for i in tupDataChecked])
        lisData = []
        for idx, i in enumerate(tupData):
            i['idx'] = idx + 1
            i['checked'] = 1 if i['id'] in checkedId else 0
            lisData.append(i)
        return lisData

    def getUserModule(self, urlPath):
        listData = self.adminPermissionModel.findOne({
            'fields': ['id', 'name', 'access_id'],
            'condition':'menu_route = \'{mr}\'and validity=1 '.format(mr=urlPath)
        })
        if 'id' in listData:
            return listData['id'],listData['access_id']
        else:
            return '0', '0'

    def deleteUser(self, strId):
        self.adminUserModel.delete({
            'condition': 'id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.adminAccountModel.delete({
            'condition': 'user_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.adminUserRoleModel.delete({
            'condition': 'user_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.adminAccessPermissionModule.delete({
            'condition': 'user_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}

        self.advertiserFollowModel.delete({
            'condition': 'user_id = {rid}'.format(rid=strId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}

    def get_document_follow(self, uid):

        tupData = self.documentFollowModel.findManyAs(
            self.dicConfig['DB_PROJECT'] +'.document_follow as df' ,{
                'fields': ['pd.media_title, df.id, df.document_id, df.remark, df.user_id, df.group_id as group_id, df.createTime as createtime, df.id'],
                'join':  self.dicConfig['DB_PROJECT'] +'.demand_media_content as pd ON(pd.id = df.document_id )' ,
                'condition': 'df.user_id = %s and df.status=1 ' % uid

        })
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['createtime'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def get_follow_follow(self, uid):
        tupData = self.documentFollowModel.findMany({
            'fields': ['document_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['document_id'])] = str(item['document_id'])
        return dicData

    def update_document_remark(self, documentID, group_id, remark, uid):

        dataDic = self.documentFollowModel.findMany({
            'fields': ['group_id'],
            'condition': 'document_id = {id} and user_id = {uid} and status=1'.format(id=documentID, uid=uid)
        })
        # print "dataDic = ",dataDic
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in group_id:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.documentFollowModel.insert({
                    'key': 'user_id, document_id, group_id, remark, createTime',
                    'val': '{uid}, {pid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, pid=documentID, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500
        for index in userGroup:
            if str(index) not in group_id:
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.documentFollowModel.update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'document_id = {id} and user_id = {uid} and group_id in ({gid}) and status=1'.format(id=documentID, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.documentFollowModel.update({
                'fields': ['status = 0'],
                'condition': 'document_id = {id} and user_id = {uid} and group_id in ({gid}) and status=1'.format(id=documentID, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200


    def get_plan_follow(self, uid):

        tupData = self.planFollowModel.findManyAs(
            self.dicConfig['DB_PROJECT'] +'.plan_follow as df' ,{
                'fields': ['pd.title, df.id, df.plan_id, df.remark, df.user_id, df.group_id as group_id, df.createTime as createTime, df.id'],
                'join':  self.dicConfig['DB_PROJECT'] +'.plan as pd ON(pd.id = df.plan_id )' ,
                'condition': 'df.user_id = %s and df.status=1 ' % uid
        })
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['createTime'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def get_plan(self, uid):
        tupData = self.planFollowModel.findMany({
            'fields': ['plan_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['plan_id'])] = str(item['plan_id'])
        return dicData

    def update_plan_remark(self, planID, group_id, remark, uid):
        dataDic = self.planFollowModel.findMany({
            'fields': ['group_id'],
            'condition': 'plan_id = {id} and user_id = {uid} and status=1'.format(id=planID, uid=uid)
        })
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in group_id:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.planFollowModel.insert({
                    'key': 'user_id, plan_id, group_id, remark, createTime',
                    'val': '{uid}, {pid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, pid=planID, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500
        for index in userGroup:
            if str(index) not in group_id:
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.planFollowModel.update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'plan_id = {id} and user_id = {uid} and status=1 and group_id in ({gid}) '.format(id=planID, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.planFollowModel.update({
                'fields': ['status = 0'],
                'condition': 'plan_id = {id} and user_id = {uid} and status=1 and group_id in ({gid})'.format(id=planID, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200

    def get_planning_follow(self, uid):
        tupData = self.planningFollowModel.findManyAs(
            self.dicConfig['DB_PROJECT'] +'.planning_follow as pf' ,{
                'fields': ['pd.title, pf.id, pf.planning_id, pf.remark, pf.user_id, pf.group_id as group_id, pf.createTime as createTime, pf.id'],
                'join':  self.dicConfig['DB_PROJECT'] +'.planning_content as pd ON(pd.planid = pf.planning_id )' ,
                'condition': 'pf.user_id = %s and pf.status=1 ' % uid
        })
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['createTime'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def get_planning(self, uid):
        tupData = self.planningFollowModel.findMany({
            'fields': ['planning_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['planning_id'])] = str(item['planning_id'])
        return dicData

    def update_planning_remark(self, planningID, group_id, remark, uid):
        dataDic = self.planningFollowModel.findMany({
            'fields': ['group_id'],
            'condition': 'planning_id = {id} and user_id = {uid} and status=1'.format(id=planningID, uid=uid)
        })
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in group_id:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.planningFollowModel.insert({
                    'key': 'user_id, planning_id, group_id, remark, createTime',
                    'val': '{uid}, {pid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, pid=planningID, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500
        for index in userGroup:
            if str(index) not in group_id:
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.planningFollowModel.update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'planning_id = {id} and user_id = {uid} and status=1 and group_id in ({gid})'.format(id=planningID, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.planningFollowModel.update({
                'fields': ['status = 0'],
                'condition': 'planning_id = {id} and user_id = {uid} and status=1 and group_id in ({gid})'.format(id=planningID, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200

    def get_feedback_follow(self, uid):
        tupData = self.feedbackFollowModel.findManyAs(
            self.dicConfig['DB_PROJECT'] +'.feedback_follow as df' ,{
                'fields': ['m.name as media_name, df.id, df.feedback_id, df.remark, df.user_id, df.group_id as group_id, df.create_time as createTime, df.id'],
                'join':  self.dicConfig['DB_PROJECT'] +'.feedback as fd ON(fd.id = df.feedback_id ) LEFT JOIN '+ self.dicConfig['DB_PROJECT']+
                '.media as m ON( m.id = fd.media_id)',
                'condition': 'df.user_id = %s and df.status=1 ' % uid
        })
        dicData = {}
        for item in tupData:
            item['create_time'] = self.formatTime(item['createTime'], '%Y-%m-%d')
            group_id = item['group_id']
            dicData.setdefault(group_id, [])
            dicData[group_id].append(item)
        return dicData

    def get_feedback(self, uid):
        tupData = self.feedbackFollowModel.findMany({
            'fields': ['feedback_id, group_id'],
            'condition': 'user_id = {uid} and status=1'.format(uid=uid)
        })
        dicData = {}
        for item in tupData:
            if item['group_id'] !=0 :
                dicData[str(item['group_id'])+str(item['feedback_id'])] = str(item['feedback_id'])
        return dicData

    def update_feedback_remark(self, feedbackID, group_id, remark, uid):
        dataDic = self.feedbackFollowModel.findMany({
            'fields': ['group_id'],
            'condition': 'feedback_id = {id} and user_id = {uid} and status=1'.format(id=feedbackID, uid=uid)
        })
        userGroup, groupUp, groupDel = [],[],[]
        for data in dataDic:
            userGroup.append(data['group_id'])
        cur_time = int(self.time.time())

        for item in group_id:
            if int(item) in userGroup:
                groupUp.append(item)
            else:
                self.feedbackFollowModel.insert({
                    'key': 'user_id, feedback_id, group_id, remark, create_time',
                    'val': '{uid}, {pid}, {gid}, \'{ram}\', {ct}'.format(
                        uid=uid, pid=feedbackID, gid=item, ram=remark, ct=cur_time)
                })
                if self.model.db.status != 200:
                    return 500
        for index in userGroup:
            if str(index) not in group_id:
                groupDel.append(str(index))

        if len(groupUp)>0:
            self.feedbackFollowModel.update({
                'fields': ['remark = \'{remark}\''.format(remark=remark)],
                'condition': 'feedback_id = {id} and user_id = {uid} and group_id in ({gid})'.format(id=feedbackID, uid=uid, gid=','.join( groupUp)) })
            if self.model.db.status != 200:
                return 500

        if len(groupDel)>0:
            self.feedbackFollowModel.update({
                'fields': ['status = 0'],
                'condition': 'feedback_id = {id} and user_id = {uid} and status=1 and group_id in ({gid})'.format(id=feedbackID, uid=uid, gid=','.join( groupDel)) })
            if self.model.db.status != 200:
                return 500
        return 200

    def get_all_user(self):
        dicData = self.adminUserModel.findMany({
            'fields':['id, name, nickname'],
            'condition':'status = 0'
        })
        return dicData

    def update_role(self, dicArgs):
        if 'role' in dicArgs and 'id' in dicArgs:
            strUserId = dicArgs['id'][0]
            lisUserRoleIds = dicArgs['role'][0].split(",")

            # 更新用户身份关联
            self.adminUserRoleModel.delete({
                'condition': 'user_id = {uid}'.format(uid=strUserId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}

            for rid in lisUserRoleIds:
                self.adminUserRoleModel.insert({
                    'key': 'user_id, role_id',
                    'val': '{uid}, {rid}'.format(uid=strUserId, rid=rid),
                })
                if self.model.db.status != 200:
                    return {'statusCode': 601}
            return {'statusCode': 200}
        else:
            return {'statusCode': 601}


    def set_export(self, uid, gid, type):
        lisData = self.importModel('project_media_follow').findMany({
            'fields':['media_id'],
            'condition': 'user_id = {uid} and status=1 and group_id in ({gid})'.format(uid=uid, gid=','.join(gid))
        })

        if lisData:
            mediaData = [ str(item['media_id']) for item in lisData]
            self.yidaoExportModel.insert({
                'key': 'user_id, filed_id, export_type, create_time',
                'val': '{uid}, \'{mid}\', {dt}, {ct}'.format(uid=uid, mid=','.join(mediaData), dt=type, ct=int(self.time.time())),
            })
        if self.model.db.status != 200:
            return 601
        else:
            return 200

    def check_export(self, uid, type):
        tupData = self.yidaoExportModel.findMany({
            'fields':['COUNT(1) as count'],
            'condition': 'user_id = {uid} and export_type = {ty}'.format(uid=uid, ty=type)
        })
        return tupData

    def check_day_export(self, uid, type, time):
        tupData = self.yidaoExportModel.findMany({
            'fields':['COUNT(1) as count'],
            'condition': 'user_id = {uid} and export_type = {ty} and create_time > {ct}'.format(uid=uid, ty=type, ct=time)
        })
        return tupData