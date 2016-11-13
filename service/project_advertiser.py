# -*- coding:utf-8 -*-

import base

class service(base.baseService):
    lis_status = ['已结束','准备中','进行中']

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.wechatModel = self.importModel('wechat')
        self.mediaModel = self.importModel('project_media')
        self.mediaWechatModel = self.importModel('project_media_wechat')
        self.ad_feedbackModel = self.importModel('project_feedback')
        self.advertiserModel = self.importModel('project_advertiser')
        self.planModel = self.importModel('project_plan')
        self.plan_demand_model = self.importModel('project_plan_demand')
        self.mediaService = self.importService('media')
        self.advertiserFollowModel=self.importModel('advertiser_follow')
        self.adminUserModel = self.importModel('admin_user')
        self.adminUserRoleModel = self.importModel('admin_user_role')
        self.contactModel = self.importModel('project_contact')
        self.contactRelationModel = self.importModel('project_contact_relation')

    def get_advertiser(self, intPage, intPageDataNum, listSearch, userId=None):
        userAd = []
        searchCondition = ''
        sub_status = listSearch['sub_status']
        if userId:
            adData = self.advertiserModel.findManyAs(
                self.dicConfig['DB_PROJECT'] +'.advertiser as pd' ,{
                    'fields': ['pd.*'],
                    'join':  self.dicConfig['DB_PROJECT'] +'.advertiser_follow as af ON(af.advertiser_id = pd.id )' ,
                    'condition': 'af.user_id = %s and validity=1' % userId
                })
            for index in adData:
                userAd.append(str(index['id']))

        if listSearch["searchType"] == "1" or listSearch["searchType"] == "2" or not listSearch["searchType"]:
            if userId and (listSearch["searchType"] == "1" or listSearch["searchType"] == "2") :
                searchCondition = 'id in ({id}) and '.format( id = ','.join( userAd if userAd else '0'))
            elif userId :
                searchCondition = 'id in ({id}) '.format( id = ','.join(userAd if userAd else '0'))

            ## 1 文本搜索
            if listSearch["searchType"] == "1":
                if listSearch["search_txt"] is not None:
                    searchCondition += ' (company like \'%{search}%\' or ' \
                                      'company_short like \'%{search}%\' or ' \
                                      'brief like \'%{search}%\' or ' \
                                      'remark like \'%{search}%\')'.format(search=listSearch["search_txt"])
            ## 2 状态搜索
            elif listSearch["searchType"] == "2" :
                if listSearch["search_level"] in ["4"]:
                    # print "search_level = ", listSearch["search_level"]
                    searchCondition += ' advertiser_status = {status} and sub_status={sub}'.format(status=listSearch["search_level"], sub=sub_status)
                else:
                    searchCondition += ' advertiser_status = {status}'.format(status=listSearch["search_level"])

            tupData, intRows = self.advertiserModel.findPaginate({
                'condition': '{search}'.format(search=searchCondition),
                'page': [intPage, intPageDataNum],
                'order': 'last_update_time desc'
            })
        elif listSearch["searchType"] == "3" :
            ## 3 搜索老客户
            if userId :
                searchCondition = 'pd.id in ({id})'.format( id = ','.join(userAd if userAd else '0'))
            tupData, intRows = self.advertiserModel.findPaginateAs(self.dicConfig['DB_PROJECT'] +'.advertiser  as pd',{
                'fields': ['pd.*'],
                'join':  self.dicConfig['DB_PROJECT'] +'.plan as plan ON(pd.id = plan.advertiser_id )' ,
                'condition': '{search}'.format(search=searchCondition),
                'page': [intPage, intPageDataNum],
                'group': 'plan.advertiser_id',
                'order': 'pd.last_update_time desc',
            })
            intRows =  len(list(tupData))
        #######################################################################
        tupDataRole = self.adminUserModel.findMany({
            'condition':'status=0'
        })
        dicRole = {i['id']: i['nickname'] or i['name'] for i in tupDataRole}

        for item in tupData:
            followerlist = []
            data = self.advertiserFollowModel.findMany({
                'fields': ['user_id'],
                'condition': "advertiser_id = {id} and validity=1 ".format(id=item['id'] or 0)
            })
            for index in data:
                followerlist.append(dicRole.get(index['user_id'],'unknown'))
            item['follower']=followerlist

        for idx, i in enumerate(tupData, 1):
            i['idx'] = (intPage - 1) * intPageDataNum + idx
            i['last_update_time'] = self.formatTime(i.get('last_update_time'), '%Y-%m-%d')
        return tupData, intRows

    def getUser(self, strID=None, user_id=None):

        roleId= self.adminUserRoleModel.findManyAs(
            self.dicConfig['DB_ADMIN'] +'.role as role', {
            'fields': ['role.id as id'],
            'join':  self.dicConfig['DB_ADMIN'] +'.role_permission as rp ON(rp.role_id = role.id) LEFT JOIN ' +
                     self.dicConfig['DB_ADMIN'] +'.permission as pre ON(pre.id = rp.permission_id) ',
            'condition':'pre.validity=1 and (pre.menu_route="/project/advertiser" or pre.menu_route="/admin_user/advertiser_follow") and role.name!="god" '
        })
        roleUser = [str(item['id']) for item in roleId]

        listUser= self.adminUserModel.findManyAs(
            self.dicConfig['DB_ADMIN'] +'.user as user', {
            'fields': ['user.id', 'user.nickname', 'user.name'],
            'join':  self.dicConfig['DB_ADMIN'] +'.user_role as ur ON(ur.user_id = user.id) ',
            'condition':'user.status=0 and user.id !={user_id} and ur.role_id in ({role_id}) group by user.id'.format(user_id=user_id, role_id=','.join(roleUser))
        })

        checkedId = set()
        if strID:
            tupDataChecked = self.advertiserFollowModel.findMany({
                'fields': ['user_id'],
                'condition': 'advertiser_id = {aid} and validity=1'.format(aid=strID)
            })
            checkedId = set([i['user_id'] for i in tupDataChecked])
        lisData = []
        for idx, i in enumerate(listUser):
            i['idx'] = idx + 1          #序号
            i['id'] = i['id']           #用户ID--user_id
            i['checked'] = 1 if i['id'] in checkedId else 0
            lisData.append(i)
        return lisData

    def create_advertiser(self, dicArgs):
        self.advertiserModel.insert({
            'key': 'company, link, product_info, '
                   'audience_info, remark, last_update_time, create_time',
            'val': '\'{comp}\', \'{link}\', \'{pi}\', \'{ai}\', \'{remark}\', {ut}, {ct}'.format(
                comp=dicArgs['company'], link=dicArgs['link'],
                pi=dicArgs['product_info'], ai=dicArgs['audience_info'],
                remark=dicArgs['remark'], ut=int(self.time.time()), ct=int(self.time.time())
            )
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_advertiser(self, dicArgs, id):
        update_fields = []
        for (k,v) in dicArgs.items():
            data = '{it_k} = \'{it_v}\''.format(it_k = k,it_v = v)
            update_fields.append(data)
        update_fields.append('last_update_time={ut}'.format(ut = int(self.time.time())))

        self.advertiserModel.update({
            'fields':update_fields,
            'condition': 'id={id}'.format(id=id)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_follower(self, dicArgs):
        advertiserF = self.advertiserFollowModel.findOne({
            'fields':['id'],
            'condition': 'advertiser_id={id}'.format(id=dicArgs['id'])
        })
        if len(advertiserF)>0 :
            self.advertiserFollowModel.update({
                'fields':['validity=0'],
                'condition': 'advertiser_id={id}'.format(id=dicArgs['id'])
            })
            if len(list(dicArgs['follower']))>0:
                self.advertiserFollowModel.update({
                    'fields':['validity=1'],
                    'condition': 'advertiser_id={id} and user_id in ({uid})'.format(id=dicArgs['id'],uid=','.join(dicArgs['follower']))
                })
        else:
            userlist = self.adminUserModel.findMany({
                'fields':['id'],
            })
            if len(list(dicArgs['follower']))>0:
                for idx, i in enumerate(userlist):
                    self.advertiserFollowModel.insert({
                        'key': 'user_id, advertiser_id, validity',
                        'val':'{uid}, {aid}, {va}'.format(uid=i['id'], aid=dicArgs['id'], va= 1 if str(i['id']) in dicArgs['follower'] else 0)
                    })

        return 200

    def delete_advertiser(self, strId, userId):
        self.advertiserFollowModel.update({
            'fields':['validity=0'],
            'condition': "advertiser_id = {aid} and user_id = {uid}".format(aid=strId, uid=userId)
        })
        if self.model.db.status != 200:
            return 500

    def advertiser_detail(self, strId):
        dicAd = self.advertiserModel.findOne({
            'condition': 'id = {id}'.format(id=strId)
        })
        tupDataRole = self.adminUserModel.findMany({})
        dicUser = {i['id']: i['name'] for i in tupDataRole}
        followerlist = []
        data = self.advertiserFollowModel.findMany({
            'fields': ['user_id'],
            'condition': "advertiser_id = {id} and validity=1 ".format(id=int(strId))
        })
        for index in data:
            followerlist.append(dicUser.get(index['user_id'],'unknown'))
        dicAd['follower']=followerlist
        return dicAd

    def advertiser_follower(self, strId):
        tupDataRole = self.adminUserModel.findMany({
            'condition': 'status = 0'
        })
        dicUser = {i['id']: i['nickname'] for i in tupDataRole}
        followerlist = []
        data = self.advertiserFollowModel.findMany({
            'fields': ['user_id'],
            'condition': "advertiser_id = {id} and validity=1 ".format(id=int(strId))
        })
        for index in data:
            followerlist.append(dicUser.get(index['user_id'],'unknown'))
        return followerlist

    def advertiser_basic(self, strId):
        dicAd = self.advertiserModel.findOne({
            'fields':['id, company, company_short, brief, link, category, area, advertiser_status, sub_status'],
            'condition':'id = {id}'.format(id=strId)
        })
        return dicAd

    def advertiser_text(self, strId):
        dicAd = self.advertiserModel.findOne({
            'fields':['id, requirement, progress, product_info, audience_info, remark'],
            'condition': 'id = {id}'.format(id=strId)
        })
        return dicAd

    def advertiser_plan(self, strAdId):
        tupPlan = self.planModel.findMany({
            'fields':['id, title, brief, time_begin, time_end, money, status'],
            'condition': 'advertiser_id={ad_id}'.format(ad_id=strAdId)
        })
        for item in tupPlan:
            item['time_begin'] = self.formatTime(item.get('time_begin'), '%Y-%m-%d')
            item['time_end'] = self.formatTime(item.get('time_end'), '%Y-%m-%d')
        return tupPlan

    def getUserRole(self, userId):
        tupData = self.adminUserRoleModel.findManyAs(
            self.model.dicConfig['DB_ADMIN'] + '.user_role as ur', {
            'fields': ['r.name'],
            'join': self.model.dicConfig['DB_ADMIN'] + '.role as r ON (r.id = ur.role_id) ',
            'condition': 'ur.user_id = {uid}'.format(uid=userId)
        })
        return tupData