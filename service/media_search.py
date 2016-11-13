# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.mediaModel = self.importModel('project_media')
        self.mediaTagModel = self.importModel('project_media_tag')
        self.mediaCommonService = self.importService('media_common')
        self.statisticsService = self.importService('admin_statistics')

    def get_count_time(self, ctype):
        if ctype == 'today_create':
            return 'm.create_time >= %s' % self.statisticsService.day_start()
        elif ctype == 'today_update':
            return 'm.last_update_time >= %s' % self.statisticsService.day_start()
        elif ctype == 'week_create':
            return 'm.create_time >= %s' % self.statisticsService.last_week()
        elif ctype == 'week_update':
            return 'm.last_update_time >= %s' % self.statisticsService.last_week()
        elif ctype == 'month_create':
            return 'm.create_time >= %s' % self.statisticsService.last_month()
        elif ctype == 'month_update':
            return 'm.last_update_time >= %s' % self.statisticsService.last_month()

    def get_search_page(self, dicData):
        listCondition = []
        listJoin = []
        if dicData['uid']:
            listCondition.append('m.user_id = %s' % dicData['uid'])
        if dicData['ctype']:
            ctype_str = self.get_count_time(dicData['ctype'])
            if ctype_str:
                listCondition.append(ctype_str)
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_tag mt on (m.id = mt.media_id)')
        if dicData['audience_province_id'] and dicData['audience_province_id'] != '-1':
            listCondition.append('m.audience_province_id = %s' % dicData['audience_province_id'])
        if dicData['audience_city_id'] and dicData['audience_city_id'] != '-1':
            listCondition.append('m.audience_city_id = %s' % dicData['audience_city_id'])
        if dicData['audience_county_id'] and dicData['audience_county_id'] != '-1':
            listCondition.append('m.audience_county_id = %s' % dicData['audience_county_id'])
        if dicData['audience_gender'] and dicData['audience_gender'] != '-1':
            listCondition.append('m.audience_gender = %s' % dicData['audience_gender'])
        if dicData['audience_age']:
            listCondition.append('m.audience_age like \'%{age}%\''.format(age=dicData['audience_age']))
        if dicData['audience_career']:
            listCondition.append('m.audience_career like \'%{career}%\''.format(career=dicData['audience_career']))
        # 查询词
        if dicData['query']:
            dicField = {'1': 'name', '4': 'brief', '5': 'contact_phone',
                        '6': 'contact_qq', '7': 'contact_wechat', '8': 'remark', '9': 'all'}
            strField = dicData['field']
            strQuery = dicData['query']
            strCol = dicField[strField]
            # 搜索条件
            if strField == '9':
                searchCondition = '(m.name like \'%{key}%\' or m.brief like \'%{key}%\' ' \
                                  'or m.identify like \'%{key}%\' or m.remark like \'%{key}%\')'.format(key=strQuery)
            else:
                searchCondition = 'm.{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
            listCondition.append(searchCondition)
        join_cond = ' join '.join(listJoin)
        # 查询
        tupData, count = self.mediaModel.findPaginateAs(
            self.dicConfig['DB_PROJECT'] + '.media as m',
            {
                'condition': ' and '.join(listCondition),
                'join': join_cond,
                'page': [dicData['page'], 10],
                'order': 'm.last_update_time desc'
            },
            cacheRow=True
        )
        # 数据格式化
        lisSearch = []
        if tupData:
            dic_search = {}
            for k, item in enumerate(tupData, 1):
                if 'tag_id' in item:
                    item.pop('tag_id')
                item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
                item['create_time'] = self.formatTime(item['create_time'], '%Y-%m-%d')
                item['platform'] = self.media_platform(item['platform_id'])
                dic_search[item['id']] = item
            lisSearch = dic_search.values()
            lisSearch.sort(key=lambda i: i['last_update_time'], reverse=True)
        return {'search': lisSearch,
                'count': count,
                'category': self.mediaCommonService.get_category_media(),
                'tag': self.mediaCommonService.get_tag()}

    @staticmethod
    def media_platform(platform_id):
        platforms = {
            2: ('wechat', '微信公众号'), 4: ('paper', '报纸'), 5: ('wechat_friend', '朋友圈'),
            6: ('zhihu', '知乎'), 7: ('weibo', '微博'), 8: ('community', '社群'), 9: ('toutiao', '头条号')
        }
        return platforms.get(platform_id)

    def get_media_by_contact(self, cid):
        pcr = self.importModel('project_contact_relation')
        res = pcr.findManyAs(
            self.dicConfig['DB_PROJECT'] + '.contact_relation as cr',
            {
                'condition': 'contact_id = %s and relation_type = 1' % cid,
                'join': self.dicConfig['DB_PROJECT'] + '.media as m on (m.id=cr.relation_id)',
                'order': 'm.last_update_time desc'
            }
        )
        rtn = []
        for item in res:
            if not item['name']:
                continue
            item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
            item['create_time'] = self.formatTime(item['create_time'], '%Y-%m-%d')
            item['platform'] = self.media_platform(item['platform_id'])
            rtn.append(item)
        return rtn
