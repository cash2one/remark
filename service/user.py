# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        self.user_model = self.importModel('user')
        self.media_model = self.importModel('media')

        self.area_service = self.importService('area')

    def index(self, intPage, intPageDataNum, intTimeStart, intTimeEnd, strSearch):
        '''
        :func: 获取用户简要信息
        :param intPage: 页码
        :param intPageDataNum: 单页数据条数
        :param intTimeStart: 筛选的起始时间
        :param intTimeEnd: 筛选的结束时间
        :param strSearch: 搜索的内容
        '''
        # 当前页起始序号
        # intDataNumStart = (intPage - 1) * intPageDataNum
        # 筛选时间条件
        timeCondition = ''
        if intTimeStart != 0 and intTimeEnd != 0:
            timeCondition = 'create_time > {start} and create_time < {end}'.format(
                start=intTimeStart, end=intTimeEnd
            )
        elif intTimeEnd != 0:
            timeCondition = 'create_time < {end}'.format(end=intTimeEnd)
        elif intTimeStart != 0:
            timeCondition = 'create_time > {start}'.format(start=intTimeStart)
        # 搜索条件
        searchCondition = ''
        if strSearch and searchCondition:
            searchCondition = ' and nickname like \'%{search}%\''.format(search=strSearch)
        elif strSearch:
            searchCondition = 'nickname like \'%{search}%\''.format(search=strSearch)
        # 用户简要信息
        tupData, intRows = self.user_model.findPaginate({
            'condition': '{time}{search}'.format(time=timeCondition, search=searchCondition),
            'page': [intPage, intPageDataNum],
            'order': 'create_time desc'
        })

        # 数据格式化
        if tupData:
            for idx, item in enumerate(tupData):
                item['vip_label'] = self.get_vip_label(item['vip'])
                item['status_label'] = self.get_status(item.get('status'))
                item['gender_label'] = self.get_gender(item.get('gender'))
                item['create_time'] = self.formatTime(item.get('create_time', 0), '%Y-%m-%d')
                item['area'] = self.importService('area').get_area(item.get('province_id'),item.get('city_id'),item.get('count_id'))
                item['media_num'] = self.has_media_num(item.get('id'))
        return tupData, intRows

    def get_user(self, str_user_id):
        """ 通过user_id获取一条用户信息

        @params strUserId string 用户ID
        """

        dic_user = self.user_model.findOne({
            'condition': 'id = %s' % str_user_id
        })

        return dic_user

    def get_user_basic(self, str_user_id):
        """ 通过user_id获取一条用户信息

        @params strUserId string 用户ID
        """

        dic_user = self.get_user(str_user_id)
        if dic_user:
            if not dic_user['nickname']:
                dic_user['nickname'] = '一道用户'
            dic_user['avatar'] = self.getAvatarUrl(dic_user['avatar'])
            dic_user['vip'] = self.get_vip_label(dic_user['vip'])
            dic_user['province'] = self.area_service.get_area_name_one(dic_user['province_id'])
            dic_user['city'] = self.area_service.get_area_name_one(dic_user['city_id'])
            dic_user['county'] = self.area_service.get_area_name_one(dic_user['county_id'])

        return dic_user

    def get_user_detail(self, str_user_id):
        """ 通过user_id获取一条用户信息

        @params strUserId string 用户ID
        """

        dic_user = self.get_user(str_user_id)
        if dic_user:
            dic_user['avatar'] = self.getAvatarUrl(dic_user['avatar'])
            dic_user['area'] = self.area_service.get_area(dic_user['province_id'], dic_user['city_id'],
                                                          dic_user['county_id'])
            dic_user['create_time'] = self.formatTime(dic_user.get('create_time'), '%Y-%m-%d')
            dic_user['status_name'] = self.get_status(dic_user['status'])
        return dic_user

    def get_vip_label(self, num):
        return {0: '普通会员', 1: '高级会员'}.get(num, '普通会员')

    def getOneAndCity(self, str_user_id):
        """ 获取单个用户信息和相关城市信息
        """
        dicUser = self.user_model.findOne({
            'condition': 'id = %s' % str_user_id
        })
        if not dicUser:
            self.status = 601
            return

        # 处理头像
        dicUser['avatar'] = self.getAvatarUrl(dicUser['avatar'])

        # 处理城市
        strCityId = dicUser['city_id']
        strProvince = ''
        strCity = ''
        # strCounty = ''
        if strCityId and strCityId != 'None':
            cityService = self.importService('area')
            tupCity = cityService.get_area_by_id(strCityId)
            if tupCity:
                for item in tupCity:
                    if item['level'] == 1:
                        strProvince = item['name']
                    if item['level'] == 2:
                        strCity = item['name']
                    # if item['level'] == 3:
                    #     strCounty = item['name']

        strLocal = '%s %s' % (strProvince, strCity) if strProvince else '未知'
        dicUser['local'] = strLocal

        return dicUser

    def detail(self, str_user_id):
        '''
        :func: 查看用户详细信息
        :param str_user_id: 用户ID
        '''
        dic_user = self.get_user_detail(str_user_id)
        if dic_user:
            dic_user['vip_label'] = self.get_vip_label(dic_user['vip'])
            media_service = self.importService('media')
            dic_user['media'] = media_service.my_media(str_user_id)
            dic_user['area'] =  self.importService('area').get_area(dic_user.get('province_id'),dic_user.get('city_id'),dic_user.get('count_id'))
            #print dic_user
        return dic_user

    def has_media_num(self,user_id):
        media_num = self.importModel('media').findMany({
            'fields':['count(*) as num'],
            'condition': 'user_id = {uid} '.format(uid = user_id)
        })
        return media_num[0].get('num')
    def updateStatus(self,intId,dicArgs):
        if 'status_update' in dicArgs:
            strstatus = dicArgs['status_update'][0]
            self.user_model.update({
                'fields': ['status = \'{status}\''.format(status=strstatus),],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def updateVip(self,intId,dicArgs):
        if 'vip_update' in dicArgs:
            strVip = dicArgs['vip_update'][0]
            self.user_model.update({
                'fields': ['vip = \'{vip}\''.format(vip=strVip),],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def updateContact(self, intId, dicArgs):
        '''
        :func: 更新用户联系方式
        :param intId: 用户ID
        :param dicArgs: 更新的内容
        '''
        if 'contact_qq' in dicArgs and 'contact_phone' in dicArgs and 'contact_email' in dicArgs:
            strQq = dicArgs['contact_qq'][0]
            strPhone = dicArgs['contact_phone'][0]
            strEmail = dicArgs['contact_email'][0]
            self.user_model.update({
                'fields': ['qq = \'{qq}\''.format(qq=strQq),
                           'phone = \'{phone}\''.format(phone=strPhone),
                           'email = \'{email}\''.format(email=strEmail)],
                'condition': 'id = {id}'.format(id=intId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def get_user_and_wechat(self, str_user_id):
        """ 通过用户ID获取用户及微信登录信息
        """

        dicUser = self.user_model.findOneAs('user as u', {
            'fields': ['u.*', 'uw.openid', 'uw.nickname as wechat_nickname'],
            'join': 'user_wechat as uw ON (u.id = uw.user_id)',
            'condition': 'u.id = "%s"' % str_user_id
        })

        return dicUser

    def get_wechat_by_openid(self, strOpenId):
        """ 通过openid读取微信信息

        @params strOpenId string opendid
        """
        user_wechat_model = self.importModel('user_wechat')
        dicUser = user_wechat_model.findOneAs('user_wechat as uw', {
            'fields': ['uw.*'],
            'condition': 'uw.openid = "%s"' % strOpenId,
            'join': 'user as u ON (uw.user_id = u.id)'
        })

        return dicUser

    def updateUser(self, dicData):
        """ 更新用户信息
        """

        if 'user_id' not in dicData.keys():
            return 401

        lisFields = []
        if 'nickname' in dicData.keys():
            lisFields.append('nickname = "%s"' % dicData['nickname'])

        if 'city_id' in dicData.keys():
            lisAreas = dicData['city_id'].split(',')
            try:
                strProviceId = lisAreas[0]
                lisFields.append('province_id = "%s"' % strProviceId)
                strCityId = lisAreas[1]
                lisFields.append('city_id = "%s"' % strCityId)
                strCountyId = lisAreas[2]
                lisFields.append('county_id = "%s"' % strCountyId)
            except IndexError:
                pass

        if 'avatar' in dicData.keys():
            lisFields.append('avatar = "%s"' % dicData['avatar'])

        if 'phone' in dicData.keys():
            lisFields.append('phone = "%s"' % dicData['phone'])

        self.user_model.update({
            'fields': lisFields,
            'condition': 'id = "%s"' % dicData['user_id']
        })
        return self.model.db.status

    def notification(self,user_id):
        if not user_id :
            return 601
        tupdata = self.importModel('message').findMany({
            'condition':'user_id = {uid}'.format(uid = user_id),
            'order': 'create_time desc'
        })

        for item in tupdata :
            item['format_time'] = self.formatTime(item['create_time'], '%Y-%m-%d %H:%M')
            if item['type'] == 0:
                item['type_name'] = '系统通知'
            elif item['type'] == 1:
                itemg['type_name'] = '邀请接单'
        return tupdata

    def update_notification(self,user_id,postdata):
        if not (user_id and postdata) :
            return 601
        lis_msg_id = postdata['id']
        for item in lis_msg_id :
            self.importModel('message').update({
                'fields' : ['status=0'],
                'condition' : 'user_id = {uid} and id = {mid}'.format(uid = user_id ,mid = item)
            })
            if self.model.db.status != 200:
                self.status = 601
        return

    def show_notification(self,user_id):
        tup_new_msg_all =  self.importModel('message').findMany({
            'condition':'user_id = {uid} and status = 1 '.format(uid = user_id),
            'order': 'create_time desc'
        })
        tup_old_msg = self.importModel('message').findMany({
            'condition':'user_id = {uid} and status = 0 '.format(uid = user_id),
            'order': 'create_time desc'
        })
        # 显示前10条未读消息，如不到十条，用旧消息填充
        lis_show_msg =list(tup_new_msg_all)
        if len(lis_show_msg) >= 10 :
            lis_show_msg = lis_show_msg
        elif (len(lis_show_msg)+len(tup_old_msg) > 10):
            lis_show_msg.extend(tup_old_msg[0:(10-1-len(lis_show_msg))])
        else:
            lis_show_msg.extend(tup_old_msg)

        for item in lis_show_msg :
            item['format_time'] = self.formatTime(item['create_time'], '%Y-%m-%d %H:%M')
            if item['type'] == 0:
                item['type_name'] = '系统通知'
            elif item['type'] == 1:
                item['type_name'] = '邀请接单'
        return lis_show_msg

    def index_msg(self, user_id):
        msg_model = self.importModel('message')
        new_msg = msg_model.findMany({
                'condition' : 'user_id = {uid} and status = 1 '.format(uid = user_id )
            })

        # 读了才update成已读

        return new_msg

    def update_index_msg(self,user_id):
         self.importModel('message').update({
                'fields' : ['status=0'],
                'condition' : 'user_id = {uid} '.format(uid = user_id )
            })
         if self.model.db.status != 200:
            self.status = 601

    @staticmethod
    def get_status(status):
        if status == 0:
            return '正常'
        elif status == 1:
            return '用户注销'
        elif status == 3:
            return '平台禁用'
        return '不知'

    @staticmethod
    def get_gender(status):
        if status == 1:
            return '女性'
        elif status == 2:
            return '男性'
        return '不知'

    def update_wechat_data(self, dicData):
        """更新微信绑定信息"""
        user_wechat_model = self.importModel('user_wechat')
        user_wechat_model.update({
            'fields': ['user_id="%s"' % dicData['user_id'],
                       'nickname="%s"' % dicData['nickname'],
                       'sex="%s"' % dicData['sex'],
                       'province="%s"' % dicData['province'],
                       'city="%s"' % dicData['city'],
                       'county="%s"' % dicData['county'],
                       'headimgurl="%s"' % dicData['headimgurl'],
                       'privilege="%s"' % dicData['privilege']],
            'condition': 'openid="%s"' % dicData['openid']
        })
        if self.model.db.status != 200:
            self.status = 601

    def create_wechat_data(self, dicData):
        """ 添加微信数据

        @params dicData dict
        """
        user_wechat_model = self.importModel('user_wechat')
        user_wechat_model.insert({
            'key': 'user_id, \
                province, \
                openid, \
                headimgurl, \
                city, \
                county, \
                sex, \
                unionid, \
                privilege, \
                nickname, \
                status, \
                create_time',
            'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
                dicData['user_id'],
                dicData['province'],
                dicData['openid'],
                dicData['headimgurl'],
                dicData['city'],
                dicData['country'],
                dicData['sex'],
                dicData['unionid'],
                dicData['privilege'],
                dicData['nickname'],
                0,
                int(self.time.time()),
            )
        })
        if self.model.db.status != 200:
            self.status = 601

    def unbind_wechat(self, strUserId):
        """ 解绑微信

        @params strUserId string 用户ID
        """
        user_wechat_model = self.importModel('user_wechat')
        user_wechat_model.delete({
            'condition': 'user_id = "%s"' % strUserId
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
