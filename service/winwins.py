# -*- coding:utf-8 -*-

import base as base


# 互推Service
class service(base.baseService):
    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        # 数据对象
        self.winwinsModel = self.importModel('winwins')
        self.winwinsLinkModel = self.importModel('winwinslink')

    def lists(self):
        """ 推荐互推列表
        """

        # 互推数据
        tupData = self.winwinsModel.findMany()
        lisData = []
        lisWinwinsId = []
        dicWinwinsUser = {}
        if tupData:
            for item in tupData:
                lisWinwinsId.append(str(item['id']))

                # 处理时间
                objCreateTime = item['start_date'].timetuple()
                item['start_date'] = '%s.%s.%s' % (objCreateTime.tm_year, objCreateTime.tm_mon, objCreateTime.tm_mday)
                lisData.append(item)

            # 获取互推用户数据
            tupWinwinsUser = self.winwinsLinkModel.findMany({
                'condition': 'winwin_id in (%s) and invite_status = 1' % ','.join(lisWinwinsId)
            })
            if tupWinwinsUser:
                for item in tupWinwinsUser:

                    # 处理图片
                    item['pic'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['avatar'], '-avatarx')

                    if item['winwin_id'] not in dicWinwinsUser.keys():
                        dicWinwinsUser[item['winwin_id']] = {
                            'data': [],
                            'count': 0
                        }

                    if dicWinwinsUser[item['winwin_id']]['count'] <= 3:
                        dicWinwinsUser[item['winwin_id']]['data'].append(item)

                    dicWinwinsUser[item['winwin_id']]['count'] += 1

        return [lisData, dicWinwinsUser]

    def get_one(self, str_uuid):
        """ 单条互推信息

        @params str_uuid string 互推特别ID
        """

        dic_winwin = self.winwinsModel.find_one({
            'condition': 'uuid = "%s"' % str_uuid
        })

        return dic_winwin

    def get_list(self, intPage, intStatus, strUserId=None):
        """ 互推列表

        @params intPage int 分页页码
        @params intStatus int 状态
        @params strUserId string 用户ID
        """

        # 变量
        lisWinwinId = []  # 互推ID
        dicWinwinsOfficial = {}  # 加入互推的自媒体

        strCondition = ''  # 查询条件

        intPageCount = 20
        strStartLimit = intPage * intPageCount if intPage > 1 else 0

        # 查询自己的互推
        lisWinwin = []
        if strUserId:
            # 获取自己所有自媒体
            lisOfficialId = []
            officialService = self.importService('official')
            tupOfficial = officialService.official_my_un(strUserId)
            if tupOfficial:
                for item in tupOfficial:
                    lisOfficialId.append(str(item['id']))

                # 读取互推
                strCondition = 'officialaccount_id in (%s)' % ','.join(lisOfficialId)
                if intStatus:
                    strCondition += ' and w.status = "%s"' % intStatus

                lisWinwin = self.winwinsLinkModel.paginate({
                    'fields': ['w.*', 'wl.invite_status'],
                    'join': 'pt_winwins as w ON (wl.winwin_id =  w.id)',
                    'condition': strCondition,
                    'limit': ['%s' % strStartLimit, '%s' % intPageCount],
                    'order': 'w.id desc',
                    'page': intPage
                })
        else:
            str_date_now = self.formatTime(int(self.time.time()), '%Y-%m-%d')
            if intStatus == '0' or not intStatus:
                strCondition = 'status = 0 and start_date >= %s' % str_date_now
            if intStatus == '1':
                strCondition = 'status = 1 and start_date <= %s' % str_date_now

            lisWinwin = self.winwinsModel.paginate({
                'condition': strCondition,
                'limit': ['%s' % strStartLimit, '%s' % intPageCount],
                'order': 'id desc',
                'page': intPage
            })

        if lisWinwin:
            int_time_now = int(self.time.time())  # 当前时间戳
            for k, item in enumerate(lisWinwin[0]):
                lisWinwin[0][k]['start'] = False
                # 处理时间
                if item['start_date']:
                    objCreateTime = item['start_date'].timetuple()
                    lisWinwin[0][k]['start_date'] = '%s/%s' % (objCreateTime.tm_mon, objCreateTime.tm_mday)
                    str_start_date = '%s/%s/%s' % (objCreateTime.tm_mon, objCreateTime.tm_mday, objCreateTime.tm_year)

                    if strUserId:
                        # 处理状态
                        int_start_date = int(self.timetostr(str_start_date + ' 23:59:59'))
                        if item['status'] == 1 and int_time_now > int_start_date:
                            lisWinwin[0][k]['status_text'] = '已完成'

                        elif item['status'] == 0 and int_time_now > int_start_date:
                            lisWinwin[0][k]['status_text'] = '已过期'
                        elif item['status'] == 1 and int_time_now <= int_start_date:
                            if item['invite_status'] == 2:
                                lisWinwin[0][k]['status_text'] = '已拒绝'
                            else:
                                lisWinwin[0][k]['status_text'] = '已开始'
                                lisWinwin[0][k]['start'] = True
                        elif item['status'] == 0 and int_time_now <= int_start_date:
                            if item['invite_status'] == 0:
                                lisWinwin[0][k]['status_text'] = '申请中'
                            elif item['invite_status'] == 1:
                                lisWinwin[0][k]['status_text'] = '已加入'
                    else:
                        lisWinwin[0][k]['status_text'] = ''
                else:
                    lisWinwin[0][k]['status_text'] = '已过期'

                if item['id']:
                    lisWinwinId.append(str(item['id']))

            if lisWinwinId:
                # 处理加入自媒体
                dicWinwinsOfficial = self.winwin_official(lisWinwinId)

            # 重组数据
            for k, item in enumerate(lisWinwin[0]):
                lisWinwin[0][k]['official'] = {}
                if item['id'] in dicWinwinsOfficial.keys():
                    lisWinwin[0][k]['official'] = dicWinwinsOfficial[item['id']]

        return lisWinwin

    def winwin_official(self, winwin_id):
        """ 加入互推的自媒体信息

        @params winwin_id str/list 互推ID
        """

        # 变量
        strWinwinId = ','.join(winwin_id) if isinstance(winwin_id, list) else winwin_id
        dicWinwinsUser = {}

        # 获取互推用户数据
        tupWinwinsUser = self.winwinsLinkModel.findMany({
            'condition': 'winwin_id in (%s)' % strWinwinId
        })
        if tupWinwinsUser:
            for item in tupWinwinsUser:

                # 处理图片
                item['pic'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['avatar'], '-avatarx')
                item['qrcode'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['qrcode'], '-avatar')

                if item['winwin_id'] not in dicWinwinsUser.keys():
                    dicWinwinsUser[item['winwin_id']] = {
                        'data': [],
                        'count': 0
                    }

                if dicWinwinsUser[item['winwin_id']]['count'] <= 3:
                    dicWinwinsUser[item['winwin_id']]['data'].append(item)

                dicWinwinsUser[item['winwin_id']]['count'] += 1

        return dicWinwinsUser

    def winwin_link_and_winwin(self, str_winwin_link_id, str_user_id):
        """ 读取一条申请及互推信息

        @params str_winwin_link_id string 申请ID
        @params str_user_id string 用户ID
        """

        if not str_winwin_link_id or not str_user_id:
            return 401

        dic_winwin = self.winwinsLinkModel.find_one({
            'fields': ['w.*', 'wl.invite_status'],
            'join': 'pt_winwins as w ON (wl.winwin_id = w.id)',
            'condition': 'wl.id = "%s"' % str_winwin_link_id
        })
        if not dic_winwin:
            return 601

        # 判断当前用户是否组织者
        if str_user_id != dic_winwin['user_id']:
            return 603

        # 执行修改
        int_invite_status = 1 if dic_winwin['invite_status'] == 0 else 0
        self.winwinsLinkModel.update({
            'fields': ['invite_status = "%s"' % int_invite_status],
            'condition': 'id = "%s"' % str_winwin_link_id
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def create(self, str_user_id, str_start_date, str_description):
        """ 创建互推基本信息

        @params str_user_id string 用户ID
        @params str_start_date string 开始时间
        @params str_description string 介绍
        """

        if not str_user_id or not str_start_date or not str_description:
            return {'status': 401, 'winwin_id': None}

        # 处理时间

        # 生成UUID
        str_uuid = self.salt(22)

        # 添加数据

        int_winwin_id = self.winwinsModel.insert({
            'key': 'uuid, user_id, start_date, description',
            'val': '"%s", "%s", "%s", "%s"' % (
                str_uuid,
                str_user_id,
                str_start_date,
                str_description
            )
        })
        if self.model.db.status != 200:
            return {'status': 601}
        return {'status': 200, 'winwin_id': int_winwin_id}

    def winwin_update_my(self, dicData):
        """ 更新我的互推

        @params dicData dict 
            dicData['user_id'] 用户ID
            dicData['start_date'] 开始时间
            dicData['description'] 互推介绍
            dicData['title'] 标题
            dicData['content'] 内容
            dicData['uuid'] 互推特别ID
        """

        if not dicData['uuid'] or not dicData['user_id']:
            return 401

        lis_fields = []

        if dicData['start_date']:
            lis_fields.append('start_date = "%s"' % dicData['start_date'])

        if dicData['description']:
            lis_fields.append('description = "%s"' % dicData['description'])

        if dicData['title']:
            lis_fields.append('title = "%s"' % dicData['title'])

        if dicData['content']:
            lis_fields.append('content = "%s"' % dicData['content'])

        self.winwinsModel.update({
            'fields': lis_fields,
            'condition': 'uuid = "%s" and user_id = "%s"' % (dicData['uuid'], dicData['user_id'])
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def winwin_update_style_my(self, str_user_id, str_uuid, str_style_id):
        """ 修改互推style

        @params str_user_id string 用户ID
        @params str_uuid string 互推特别ID
        @params str_style_id string 类型ID
        """

        if not str_user_id or not str_uuid or not str_style_id:
            return 401

        self.winwinsModel.update({
            'fields': ['style = "%s"' % str_style_id],
            'condition': 'uuid = "%s" and user_id = "%s"' % (str_uuid, str_user_id)
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def winwin_join(self, str_winwin_id, str_official_id):
        """ 自媒体加入互推

        @params str_winwin_id string 互推ID
        @params str_official_id string 自媒体ID
        """

        if not str_winwin_id or not str_official_id:
            return 401

        # 写数据
        self.winwinsLinkModel.insert({
            'key': 'winwin_id, officialaccount_id, created_at',
            'val': '"%s", "%s", "%s"' % (
                str_winwin_id,
                str_official_id,
                self.formatTime(int(self.time.time()))
            )
        })
        if self.model.db.status != 200:
            return 601
        return 200

    def winwin_start(self, str_uuid, str_user_id):
        """ 开始互推

        @params str_uuid string 互推特别ID
        @params str_user_id string 用户ID
        """

        if not str_uuid or not str_user_id:
            return 401

        self.winwinsModel.update({
            'fields': ['status = 1'],
            'condition': 'user_id = "%s" and uuid = "%s"' % (str_user_id, str_uuid)
        })
        if self.model.db.status != 200:
            return 601
        return 200
