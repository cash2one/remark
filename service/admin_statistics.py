# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.demandModel = self.importModel('demand')
        # 订单
        self.demand_order_model = self.importModel('demand_order')
        # 联盟
        self.unionModel = self.importModel('union')
        # 自媒体
        self.mediaModel = self.importModel('media')
        # 用户
        self.userModel = self.importModel('user')

    def index(self, intPage, intPageDataNum, strTimeStart, strTimeEnd):
        """
        :func: 数据统计
        :param intPage: 页码
        :param intPageDataNum: 单页数据
        :param strTimeStart: 起始时间
        :param strTimeEnd: 截至时间
        """
        # TODO 数据库时间字段统一成类型为int的create_time后，fields和condition可以统一处理
        # 处理缺失日期的分页，根据页数及每页展示的数据变更起始时间作为分页
        # 默认最近七天
        if not strTimeEnd and not strTimeStart:
            strTimeEnd = str(self.datetime.date.today())
            strTimeStart = str(self.datetime.date.today() - self.datetime.timedelta(days=7))
        # 截至日期缺失默认当天
        elif not strTimeEnd:
            strTimeEnd = str(self.datetime.date.today())
        # 起始日期缺失默认以最早时间作为起始日期
        elif not strTimeStart:
            strTimeStart = min(
                self.demand_order_model.findOne({
                    'fields': ['date_format(from_unixtime(min(create_time)),\'%Y-%m-%d\') as day']}).get('day'),
                # self.unionModel.getOne({
                #     'fields': ['date_format(min(create_time),\'%Y-%m-%d\') as day']}).get('day'),
                self.mediaModel.findOne({
                    'fields': ['date_format(from_unixtime(min(create_time)),\'%Y-%m-%d\') as day']}).get('day'),
                self.userModel.findOne({
                    'fields': ['date_format(from_unixtime(min(create_time)),\'%Y-%m-%d\') as day']}).get('day')
            )

        # 计算总天数
        strDayToDate = lambda s: self.datetime.datetime.strptime(s, '%Y-%m-%d').date()
        dateDays = strDayToDate(strTimeEnd) - strDayToDate(strTimeStart)
        intRows = dateDays.days
        # print dateDays
        # 当前页偏移总数
        intDataNum = (intPage - 1) * intPageDataNum
        # 字符串时间偏移函数
        # useCase: strDayDelta('2015-06-30', 7) --> '2015-07-07'
        strDayDelta = lambda s, dt: str(self.datetime.datetime.strptime(s, '%Y-%m-%d').date() +
                                        self.datetime.timedelta(days=dt))
        # 每页截至时间
        strTimePageEnd = strDayDelta(strTimeEnd, -intDataNum)
        # 每页起始时间
        strTimePageStart = strDayDelta(strTimeEnd, -(intDataNum + intPageDataNum - 1))
        strTimePageStart = strTimePageStart if strTimePageStart > strTimeStart else strTimeStart
        # 构建当前页每一天的数据字典
        dicDate = {}
        listDate = []
        strTimeTemp = strTimePageStart
        strDateTemp = strTimeStart
        while strDateTemp <= strTimeEnd:
            listDate.append(strDateTemp.decode('utf8'))
            strDateTemp = strDayDelta(strDateTemp, 1)
        while strTimeTemp <= strTimePageEnd:
            # count 字典不能共享
            dicDate.setdefault(strTimeTemp.decode('utf8'),
                               {'union_counts': 0, 'media_counts': 0,
                                'user_counts': 0, 'demand_counts': 0,
                                'demand_online_counts': 0, 'demand_success_counts': 0,
                                'demand_cancel_counts': 0, 'demand_appeal_counts': 0,
                                'demand_wait_rcv_counts': 0, 'demand_wait_fbk_counts': 0,
                                'demand_feedback_counts': 0}
                               )
            strTimeTemp = strDayDelta(strTimeTemp, 1)
        # 筛选时间条件
        timeCond = 'date_format(from_unixtime(create_time),\'%Y-%m-%d\') ' \
                   'BETWEEN \'{start}\' and \'{end}\''.format(start=strTimePageStart, end=strTimePageEnd)
        # timeCondUion = 'date_format(create_time,\'%Y-%m-%d\') ' \
        #                'BETWEEN \'{start}\' and \'{end}\''.format(start=strTimePageStart, end=strTimePageEnd)
        timeCondMedia = 'date_format(from_unixtime(create_time),\'%Y-%m-%d\') ' \
                        'BETWEEN \'{start}\' and \'{end}\''.format(start=strTimePageStart, end=strTimePageEnd)
        # 总需求单数
        tupDataDemand = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demand in tupDataDemand:
            dicDate[demand['day']]['demand_counts'] = demand['count']
        # 已撤销订单数
        tupDataDemandCancel = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = -2 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandCancel in tupDataDemandCancel:
            dicDate[demandCancel['day']]['demand_cancel_counts'] = demandCancel['count']
        # 等待接单订单数
        tupDataDemandWaitRcv = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = 1 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandWaitRcv in tupDataDemandWaitRcv:
            dicDate[demandWaitRcv['day']]['demand_wait_rcv_counts'] = demandWaitRcv['count']
        # 等待反馈订单数
        tupDataDemandWaitFbk = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = 2 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandWaitFbk in tupDataDemandWaitFbk:
            dicDate[demandWaitFbk['day']]['demand_wait_fbk_counts'] = demandWaitFbk['count']
        # 已反馈订单数
        tupDataDemandFeedback = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = 3 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandFeedback in tupDataDemandFeedback:
            dicDate[demandFeedback['day']]['demand_feedback_counts'] = demandFeedback['count']
        # 申诉中订单数
        tupDataDemandAppeal = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = 4 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandAppeal in tupDataDemandAppeal:
            dicDate[demandAppeal['day']]['demand_appeal_counts'] = demandAppeal['count']
        # 交易成功订单数
        tupDataDemandSuccess = self.demand_order_model.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} and status = 5 group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for demandSuccess in tupDataDemandSuccess:
            dicDate[demandSuccess['day']]['demand_success_counts'] = demandSuccess['count']
        # 已上线订单数
        for day in dicDate:
            dicDate[day]['demand_online_counts'] = dicDate[day]['demand_cancel_counts'] + \
                                                   dicDate[day]['demand_wait_rcv_counts'] + \
                                                   dicDate[day]['demand_wait_fbk_counts'] + \
                                                   dicDate[day]['demand_feedback_counts'] + \
                                                   dicDate[day]['demand_appeal_counts'] + \
                                                   dicDate[day]['demand_success_counts']
        # 联盟数
        # tupDataUnion = self.unionModel.findMany({
        #     'fields': ['date_format(create_time,\'%Y-%m-%d\') as day', 'count(*) as count'],
        #     'condition': '{time} group by day'.format(time=timeCondUion),
        #     'order': 'day desc'
        # })
        # for union in tupDataUnion:
        #     dicDate[union['day']]['union_counts'] = union['count']
        # 自媒体数
        tupDataMedia = self.mediaModel.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} group by day'.format(time=timeCondMedia),
            'order': 'day desc'
        })
        for media in tupDataMedia:
            dicDate[media['day']]['media_counts'] = media['count']
        # 用户数
        tupDataUser = self.userModel.findMany({
            'fields': ['date_format(from_unixtime(create_time),\'%Y-%m-%d\') as day', 'count(*) as count'],
            'condition': '{time} group by day'.format(time=timeCond),
            'order': 'day desc'
        })
        for user in tupDataUser:
            dicDate[user['day']]['user_counts'] = user['count']
        # 按日期排序
        lisData = sorted(dicDate.iteritems(), key=lambda i: i[0], reverse=True)
        return lisData, intRows, listDate

    def total(self):
        """
        :func: 统计用户 自媒体 联盟 订单总数
        """
        intUserTotals = self.userModel.getRows({'fields': ['count(*) as count']})
        intMediaTotals = self.mediaModel.getRows({'fields': ['count(*) as count']})
        intUnionTotals = 0
        # intUnionTotals = self.unionModel.getRows({'fields': ['count(*) as count']})
        intDemandTotals = self.demandModel.getRows({'fields': ['count(*) as count']})
        dicTotal = {'user_total': intUserTotals,
                    'media_total': intMediaTotals,
                    'union_total': intUnionTotals,
                    'demand_total': intDemandTotals}
        return dicTotal

    def today(self):
        """
        :func: 统计当天 用户 自媒体 联盟 订单数
        """
        strToday = self.time.strftime('%Y-%m-%d 00:00:00')
        intToday = int(self.time.mktime(self.time.strptime(strToday, '%Y-%m-%d 00:00:00')))
        # int time
        intUserToday = self.userModel.getRows({
            'fields': ['count(*) as count'],
            'condition': 'create_time >= {today}'.format(today=intToday)
        })
        # int time
        intMediaToday = self.mediaModel.getRows({
            'fields': ['count(*) as count'],
            'condition': 'create_time >= {today}'.format(today=intToday)
        })
        # date_time
        intUnionToday = 0
        # intUnionToday = self.unionModel.getRows({
        #     'fields': ['count(*) as count'],
        #     'condition': 'create_time >= \'{today}\''.format(today=strToday)
        # })
        # int time
        intDemandToday = self.demandModel.getRows({
            'fields': ['count(*) as count'],
            'condition': 'create_time >= {today}'.format(today=intToday)
        })
        dicToday = {'user_today': intUserToday,
                    'media_today': intMediaToday,
                    'union_today': intUnionToday,
                    'demand_today': intDemandToday}
        return dicToday

    def day_start(self):
        t = int(self.time.mktime(self.time.strptime(
            self.time.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S'
        )))
        return t

    def last_week(self):
        # 最近7天
        return self.day_start() - 7 * 86400

    def last_month(self):
        # 最近30天
        return self.day_start() - 30 * 86400

    def week_start(self):
        # 本周
        t = self.day_start() - int(self.time.strftime('%w')) * 86400
        return t

    def month_start(self):
        # 本月
        t = int(self.time.mktime(self.time.strptime(
            self.time.strftime('%Y-%m-01 00:00:00'), '%Y-%m-%d %H:%M:%S'
        )))
        return t

    def media_statistics_by_platform(self):
        intToday = self.day_start()
        intWeek = self.last_week()
        print "INTWEEK", intWeek
        intMonth = self.last_month()
        platform = self.importModel('project_platform').findMany({})
        platform = {i['id']: i['label'] for i in platform if i['id'] != 1 and i['id'] != 3}
        pids = set(platform.keys())
        media_today_update = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by platform_id' % intToday
        })
        pid_today_update = set([i['platform_id'] for i in media_today_update])
        for j in (pids - pid_today_update):
            media_today_update += ({'platform_id': j, 'count': 0},)
        media_today_create = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by platform_id' % intToday
        })
        pid_today_create = set([i['platform_id'] for i in media_today_create])
        for j in (pids - pid_today_create):
            media_today_create += ({'platform_id': j, 'count': 0},)

        media_week_update = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by platform_id' % intWeek
        })
        pid_week_update = set([i['platform_id'] for i in media_week_update])
        for j in (pids - pid_week_update):
            media_week_update += ({'platform_id': j, 'count': 0},)
        media_week_create = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by platform_id' % intWeek
        })
        pid_week_create = set([i['platform_id'] for i in media_week_create])
        for j in (pids - pid_week_create):
            media_week_create += ({'platform_id': j, 'count': 0},)

        media_month_update = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by platform_id' % intMonth
        })
        pid_month_update = set([i['platform_id'] for i in media_month_update])
        for j in (pids - pid_month_update):
            media_month_update += ({'platform_id': j, 'count': 0},)
        media_month_create = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by platform_id' % intMonth
        })
        pid_month_create = set([i['platform_id'] for i in media_month_create])
        for j in (pids - pid_month_create):
            media_month_create += ({'platform_id': j, 'count': 0},)

        media_total = self.importModel('project_media').findMany({
            'fields': ['platform_id', 'count(*) as count'],
            'condition': '1 group by platform_id'
        })
        pid_total = set([i['platform_id'] for i in media_total])
        for j in (pids - pid_total):
            media_total += ({'platform_id': j, 'count': 0},)

        return {'today_update': media_today_update,
                'today_create': media_today_create,
                'week_update': media_week_update,
                'week_create': media_week_create,
                'month_update': media_month_update,
                'month_create': media_month_create,
                'total': media_total,
                'platform': platform}

    def media_statistics_by_user(self):
        print "xxxxxxxxxxxxxxxxxxxxxxxxx"
        intToday = self.day_start()

        intWeek = self.last_week()
        intMonth = self.last_month()
        print intToday,intWeek,intMonth
        user = self.importModel('admin_user').findMany({})
        roles = self.importModel('admin_role_permission').findMany({
            'condition': 'permission_id = 22'
        })
        rids = set([str(i['role_id']) for i in roles])
        if rids:
            users = self.importModel('admin_user_role').findMany({
                'condition': 'role_id in (%s)' % ','.join(rids)
            })
            nml_users = self.importModel('admin_user').findMany({
                'condition': 'status = 0'
            })
            uids = set(i['user_id'] for i in users) & set(j['id'] for j in nml_users)
            user = {i['id']: i['nickname'] if i['nickname'] else i['name'] for i in user if i['id'] in uids}
        else:
            user = {i['id']: i['nickname'] if i['nickname'] else i['name'] for i in user}
        pids = set(user.keys())
        media_today_update = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by user_id' % intToday
        })
        pid_today_update = set([i['user_id'] for i in media_today_update])
        for j in (pids - pid_today_update):
            media_today_update += ({'user_id': j, 'count': 0},)
        media_today_create = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by user_id' % intToday
        })
        pid_today_create = set([i['user_id'] for i in media_today_create])
        for j in (pids - pid_today_create):
            media_today_create += ({'user_id': j, 'count': 0},)

        media_week_update = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by user_id' % intWeek
        })
        pid_week_update = set([i['user_id'] for i in media_week_update])
        for j in (pids - pid_week_update):
            media_week_update += ({'user_id': j, 'count': 0},)
        media_week_create = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by user_id' % intWeek
        })
        pid_week_create = set([i['user_id'] for i in media_week_create])
        for j in (pids - pid_week_create):
            media_week_create += ({'user_id': j, 'count': 0},)

        media_month_update = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'last_update_time >= %s group by user_id' % intMonth
        })
        pid_month_update = set([i['user_id'] for i in media_month_update])
        for j in (pids - pid_month_update):
            media_month_update += ({'user_id': j, 'count': 0},)
        media_month_create = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': 'create_time >= %s group by user_id' % intMonth
        })
        pid_month_create = set([i['user_id'] for i in media_month_create])
        for j in (pids - pid_month_create):
            media_month_create += ({'user_id': j, 'count': 0},)

        media_total = self.importModel('project_media').findMany({
            'fields': ['user_id', 'count(*) as count'],
            'condition': '1 group by user_id'
        })
        pid_total = set([i['user_id'] for i in media_total])
        for j in (pids - pid_total):
            media_total += ({'user_id': j, 'count': 0},)

        return {'today_update': media_today_update,
                'today_create': media_today_create,
                'week_update': media_week_update,
                'week_create': media_week_create,
                'month_update': media_month_update,
                'month_create': media_month_create,
                'total': media_total,
                'user': user}
