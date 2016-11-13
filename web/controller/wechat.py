# -*- coding:utf-8 -*-

import base

class Wechat(base.base):
    """ 互推
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.winwinService = self.importService('winwins')

    def index(self):
        """ 互推首页
        """

        # 获取参数
        intPage = self.I('page')
        intPage = int(intPage) if intPage else 1
        strStatus = self.I('status')

        lisWinwin = self.winwinService.get_list(intPage, strStatus)

        self.dicViewData['winwin'] = lisWinwin[0]
        self.dicViewData['menu'] = 'all'
        self.dicViewData['status'] = strStatus
        self.dicViewData['page'] = self.page(intPage, 20, lisWinwin[1], '/winwin?')

        self.display('index')

    def my(self):
        """ 我的互推
        """
        
        # 获取参数
        intPage = self.I('page')
        intPage = int(intPage) if intPage else 1
        strStatus = self.I('status')

        if not self.current_user['user_id']:
            self.redirect('/404')
            return

        lisWinwin = self.winwinService.get_list(intPage, strStatus, self.current_user['user_id'])

        self.dicViewData['winwin'] = lisWinwin[0]
        self.dicViewData['menu'] = 'my'
        self.dicViewData['status'] = strStatus
        self.dicViewData['page'] = self.page(intPage, 20, lisWinwin[1], '/winwin?')

        self.display('index')

    def view(self):
        """ 互推详情
        """

        # 获取请求参数
        str_uuid = self.I('id')
        
        # 变量
        str_user_id = self.current_user['user_id']
        dic_winwin = {'uuid': 0, 'start_date': 0, 'description': '', 'title': '', 'content': '', 'style': 0, 'id': 0} # 互推信息
        boo_is_creater = False # 是否组织者
        boo_is_over = False # 互推是否已过期
        boo_is_member = False # 是否参与者
        boo_is_start = False # 是否开始互推
        int_time_now = int(self.time.time()) # 当前时间戳
        str_time_now = self.formatTime(int_time_now, '%Y-%m-%d') # 当前时间
        lis_member = [] # 已参与自媒体
        lis_member_apply = [] # 申请参与中的自媒体
        lis_member_my = [] # 我已经参与的自媒体ID
        tup_official_my = () # 我的自媒体

        # 名片样式
        lis_style = [
            {'id': 1, 'name': '鸦青', 'background': '#323c46', 'color': '#fff'},
            {'id': 2, 'name': '明黄', 'background': '#ffee00', 'color': '#000'},
            {'id': 3, 'name': '竹青', 'background': '#1e645a', 'color': '#fff'},
            {'id': 4, 'name': '红赤', 'background': '#ff0055', 'color': '#fff'},
            {'id': 5, 'name': '牙白', 'background': '#fafaef', 'color': '#000'},
            {'id': 6, 'name': '月白', 'background': '#d8ecf3', 'color': '#000'},
        ]

        # 有UUID时，执行互推详情，如果没有，就是添加界面
        if str_uuid:

            # 读取互推数据
            dic_winwin = self.winwinService.get_one(str_uuid)

            # 判断是否组织者

            if str_user_id and str_user_id == dic_winwin['user_id']:
                boo_is_creater = True

            # 判断是否已开始
            if dic_winwin['status'] == 1:
                boo_is_start = True

            # 判断互推是否过期
            int_start_date = int(self.timetostr(dic_winwin['start_date']))
            if int_time_now > int_start_date:
                boo_is_over = True

            # 参加互推的自媒体
            dic_official = self.winwinService.winwin_official(dic_winwin['id'])
            if dic_official:
                for item in dic_official[dic_winwin['id']]['data']:
                    if item['invite_status'] == 1:
                        lis_member.append(item)
                    else:
                        lis_member_apply.append(item)

                    # 自己已参与的自媒体
                    if str_user_id and item['user_id'] == str_user_id:
                        lis_member_my.append(item['officialaccount_id'])

            # 当前用户自媒体
            if str_user_id:
                officialService = self.importService('official')
                tup_official_my = officialService.official_my_un(str_user_id)

        # 输出
        self.dicViewData['winwin'] = dic_winwin
        self.dicViewData['is_creater'] = boo_is_creater
        self.dicViewData['is_member'] = boo_is_member
        self.dicViewData['is_over'] = boo_is_over
        self.dicViewData['is_start'] = boo_is_start
        self.dicViewData['time_now'] = str_time_now
        self.dicViewData['style'] = lis_style
        self.dicViewData['member'] = lis_member
        self.dicViewData['member_apply'] = lis_member_apply
        self.dicViewData['member_my'] = lis_member_my
        self.dicViewData['official_my'] = tup_official_my

        self.display('view')

    def create(self):
        """ 创建互推
        """

        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)
        
        # 获取参数
        str_start_date = self.I('start_date') # 互推开始时间（截止报名时间）
        str_description = self.I('description') # 互推介绍

        dic_result = self.winwinService.create(str_user_id, str_start_date, str_description)

        self.out(dic_result['status'], '', dic_result['winwin_id'])

    def update(self):
        """ 编辑互推
        """
        
        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)

        # 获取参数
        dicRequestData = {
            'user_id': str_user_id,
            'start_date': self.I('start_date'), # 互推开始时间（截止报名时间）
            'description': self.I('description'), # 互推介绍
            'title': self.I('title'), # 互推标题
            'content': self.I('content'), # 互推内容
            'uuid': self.I('id') # 互推特别ID
        }

        int_status = self.winwinService.winwin_update_my(dicRequestData)
        
        self.out(int_status)

    def update_style(self):
        """ 修改style
        """
        
        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)

        # 获取参数
        str_uuid = self.I('id')
        str_style_id = self.I('style_id')
        
        if not str_uuid:
            self.out(401)

        int_status = self.winwinService.winwin_update_style_my(str_user_id, str_uuid, str_style_id)

        self.out(int_status)

    def join(self):
        """ 加入自媒体到互推
        """

        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)

        # 获取参数
        str_winwin_id = self.I('winwin_id')
        str_official_id = self.I('official_id')

        int_status = self.winwinService.winwin_join(str_winwin_id, str_official_id)

        self.out(int_status)

    def agree_refuse(self):
        """ 同意拒绝申请
        """
        
        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)

        # 获取参数
        str_winwin_link_id = self.I('id')

        # 读取申请及互推信息
        int_status = self.winwinService.winwin_link_and_winwin(str_winwin_link_id, str_user_id)
        
        self.out(int_status)

    def start(self):
        """ 开始互推
        """
        
        # 判断用户是否登录
        str_user_id = self.current_user['user_id']
        if not str_user_id:
            self.out(301)

        # 获取参数
        str_uuid = self.I('id')

        if not str_uuid:
            self.out(401)

        int_status = self.winwinService.winwin_start(str_uuid, str_user_id)

        self.out(int_status)








