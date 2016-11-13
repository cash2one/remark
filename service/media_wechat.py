# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.wechatModel = self.importModel('wechat')
        self.mediaModel = self.importModel('project_media')
        self.mediaWechatModel = self.importModel('project_media_wechat')
        self.msgModel = self.importModel('project_media_msg')
        self.mediaTagModel = self.importModel('project_media_tag')
        self.demand_service = self.importService('demand')
        self.mediaCommonService = self.importService('media_common')


    def check_follow(self, mid, uid):
        if mid:
            searchCondition = 'status=1 and user_id=%s and media_id=%s' % (uid, mid)
        else:
            searchCondition = 'status=1 and user_id=%s' % (uid)

        res = self.importModel('project_media_follow').findMany({
            'condition': '%s' % searchCondition
        })
        return res

    def get_wechat_page(self, dicData, uid):
        """获取列表页数据"""
        if dicData.get('status') == '3':
            listCondition = ['m.platform_id = 2']
        else:
            listCondition = ['m.platform_id = 2 and m.status != 3']
        listJoin = []
        if dicData['category']:
            listCondition.append('m.category_media_id in (%s)' % dicData['category'])
        if dicData['tag']:
            listCondition.append('mt.tag_id in (%s)' % dicData['tag'])
            listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_tag mt on (m.id = mt.media_id)')
        if dicData['role'] and dicData['role'] != '-1':
            listCondition.append('m.role = %s' % dicData['role'])
        if dicData['status'] and dicData['status'] != '-1':
            listCondition.append('m.status = %s' % dicData['status'])
        if dicData['original'] and dicData['original'] != '-1':
            listCondition.append('mw.original = %s' % dicData['original'])
        if dicData['black_pr'] and dicData['black_pr'] != '-1':
            listCondition.append('m.black_pr = %s' % dicData['black_pr'])
        if dicData['can_afford_article'] and dicData['can_afford_article'] != '-1':
            listCondition.append('m.can_afford_article = %s' % dicData['can_afford_article'])
        if dicData['comment'] and dicData['comment'] != '-1':
            listCondition.append('m.comment = %s' % dicData['comment'])
        if dicData['award'] and dicData['award'] != '-1':
            listCondition.append('m.award = %s' % dicData['award'])
        if dicData['kol'] and dicData['kol'] != '-1':
            listCondition.append('m.kol = %s' % dicData['kol'])
        if dicData['ad'] and dicData['ad'] != '-1':
            listCondition.append('m.ad = %s' % dicData['ad'])
        if dicData['ad_type'] and dicData['ad_type'] != '-1':
            listCondition.append('m.ad_type like \'%{atp}%\''.format(atp=dicData['ad_type']))
        if dicData['station'] and dicData['station'] != '-1':
            listCondition.append('m.station = %s' % dicData['station'])
        if dicData['worth'] and dicData['worth'] != '-1':
            listCondition.append('m.worth = %s' % dicData['worth'])
        if dicData['identify'] and dicData['identify'] == '1':
            listCondition.append('m.identify != ""')
        if dicData['identify'] and dicData['identify'] == '2':
            listCondition.append('m.identify = ""')
        right_join = ''
        if dicData['feedback'] and dicData['feedback'] == '1':
            listCondition.append('m.id != 0')
            right_join = '(select DISTINCT f.media_id from ' + self.dicConfig[
                'DB_PROJECT'] + '.feedback as f) as r on(m.id = r.media_id)'
        if dicData['farm_level'] and dicData['farm_level'] != '-1':
            listCondition.append('m.farm_level = %s' % dicData['farm_level'])
        if dicData['fans_num'] and dicData['fans_num'] != ',':
            fn = self.build_interval_condition('m.fans_num', dicData['fans_num'])
            if fn: listCondition.append(fn)
        if dicData['first_price'] and dicData['first_price'] != ',':
            fp = self.build_interval_condition('m.first_price', dicData['first_price'])
            if fp: listCondition.append(fp)
        if dicData['second_price'] and dicData['second_price'] != ',':
            sp = self.build_interval_condition('m.second_price', dicData['second_price'])
            if sp: listCondition.append(sp)
        if dicData['other_price'] and dicData['other_price'] != ',':
            op = self.build_interval_condition('m.other_price', dicData['other_price'])
            if op: listCondition.append(op)
        if dicData['top_avg_read_num'] and dicData['top_avg_read_num'] != ',':
            trn = self.build_interval_condition('mw.top_avg_read_num', dicData['top_avg_read_num'])
            if trn: listCondition.append(trn)
        else:
            trn = self.build_interval_condition('mw.top_avg_read_num', '0,')
            if trn: listCondition.append(trn)
        if dicData['top_three_avg_read_num'] and dicData['top_three_avg_read_num'] != ',':
            rn = self.build_interval_condition('mw.top_three_avg_read_num', dicData['top_three_avg_read_num'])
            if rn: listCondition.append(rn)
        if dicData['like_num'] and dicData['like_num'] != ',':
            ln = self.build_interval_condition('mw.like_num', dicData['like_num'])
            if ln: listCondition.append(ln)
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
            dicField = {'1': 'name', '2': 'wechat_id', '3': 'biz', '4': 'brief', '8': 'remark', '9': 'all'}
            strField = dicData['field']
            strQuery = dicData['query']
            strCol = dicField[strField]
            # 搜索条件
            if strField == '2' or strField == '3':
                searchCondition = 'mw.{col} = \'{key}\''.format(col=strCol, key=strQuery)
            elif strField == '9':
                searchCondition = '(m.name like \'%{key}%\' or m.brief like \'%{key}%\' ' \
                                  'or m.identify like \'%{key}%\' or m.remark like \'%{key}%\')'.format(key=strQuery)
            else:
                searchCondition = 'm.{col} like \'%{key}%\''.format(col=strCol, key=strQuery)
            listCondition.append(searchCondition)
        listJoin.append(self.dicConfig['DB_PROJECT'] + '.media_wechat mw on (m.id = mw.media_id)')
        # print ' and '.join(listCondition)
        join_cond = ' join '.join(listJoin)
        join_cond = join_cond + 'right join' + right_join if right_join else join_cond
        col, sc = self.sort_condition(dicData.get('sort'))
        # 查询
        tupData, count = self.mediaModel.findPaginateAs(
            self.dicConfig['DB_PROJECT'] + '.media as m',
            {
                'fields':['m.id, m.name, mw.media_id, identify, wechat_id, brief, original, like_num, top_avg_read_num, top_three_avg_read_num, '
                          'first_price, m.remark, last_update_time'],
                'condition': ' and '.join(listCondition),
                'join': join_cond,
                'page': [dicData['page'], 10],
                'order': self.build_order_condition(col, sc)
            },
            cacheRow=True
        )

        group_data = self.check_follow(None, uid)
        group = [ item['media_id'] for item in group_data]
        # 数据格式化
        lisWechat = []
        if tupData:
            dic_wechat = {}
            for k, item in enumerate(tupData, 1):
                if 'tag_id' in item:
                    item.pop('tag_id')
                item['last_update_time'] = self.formatTime(item['last_update_time'], '%Y-%m-%d')
                item['follow'] = True if item['id'] in group else False
                dic_wechat[item['id']] = item

            lisWechat = dic_wechat.values()
            lisWechat.sort(
                key=lambda i: i[col], reverse=True if sc == 'desc' else False
            )
        # print lisWechat
        return {'wechat': lisWechat,
                'count': count,
                'category': self.mediaCommonService.get_category_media(),
                'tag': self.mediaCommonService.get_tag()}

    @staticmethod
    def build_order_condition(col, sc):
        """排序分解"""
        media_cols = {'id', 'name', 'comment', 'first_price', 'create_time', 'last_update_time'}
        tbl = 'm' if col in media_cols else 'mw'
        order_cond = '{tbl}.{col} {sc}'.format(tbl=tbl, col=col, sc=sc)
        return order_cond

    @staticmethod
    def sort_condition(sort_str):
        """排序条件"""
        if not sort_str:
            return 'm.last_update_time desc'
        if sort_str.endswith('_desc'):
            col, sc = sort_str[:-5], 'desc'
        else:
            col, sc = sort_str, 'asc'
        return col, sc

    @staticmethod
    def build_interval_condition(col, value):
        """限定范围查询"""
        strCondition = ''
        start, end = value.split(',')
        if start and end:
            strCondition = '%s between %s and %s' % (col, float(start), float(end))
        elif start:
            strCondition = '%s >= %s' % (col, float(start))
        elif end:
            strCondition = '%s <= %s' % (col, float(end))
        return strCondition

    def wechat_detail(self, intId):
        """详细信息"""
        dicMedia = self.mediaModel.findOne({
            'condition': 'id={id}'.format(id=intId)
        })
        dicMediaWechat = self.mediaWechatModel.findOne({
            'condition': 'media_id={mid}'.format(mid=intId)
        })
        tupMediaTag = self.mediaTagModel.findMany({
            'condition': 'media_id={mid}'.format(mid=intId)
        })
        tupUser = self.importModel('admin_user').findMany({})
        dicUser = {i['id']: i['nickname'] for i in tupUser}
        old_tags = []
        if dicMedia['tags']:
            old_tags = dicMedia['tags'].split(',')
        strTag = ','.join(old_tags + [str(i['tag_id']) for i in tupMediaTag])
        # print strTag
        dicMediaWechat.pop('id')
        dicMedia.update(dicMediaWechat)
        dicMedia['create_time'] = self.formatTime(dicMedia['create_time'], '%Y-%m-%d')
        dicMedia['post_time'] = self.formatTime(dicMedia['post_time'], '%Y-%m-%d')
        dicMedia['last_update_time'] = self.formatTime(dicMedia['last_update_time'], '%Y-%m-%d')
        dicMedia['category'] = self.category(dicMedia['category_media_id'])
        dicMedia['tag'] = self.tag(strTag)
        dicMedia['url'] = dicMedia['url'].replace('&amp;', '&') if dicMedia['url'] else ''
        dicMedia['original_label'] = self.original(dicMedia['original'])
        dicMedia['audience_gender'] = self.audience_gender(dicMedia['audience_gender'])
        dicMedia['audience_area'] = self.audience_area(
            dicMedia['audience_province_id'], dicMedia['audience_city_id'], dicMedia['audience_county_id'])
        dicMedia['audience_age'] = self.audience_age(dicMedia['audience_age'])
        dicMedia['audience_career'] = self.audience_career(dicMedia['audience_career'])
        dicMedia['ad_type'] = self.ad_type(dicMedia['ad_type'])
        dicMedia['role'] = self.role(dicMedia['role'])
        dicMedia['status'] = self.status(dicMedia['status'])
        dicMedia['black_pr'] = self.radio_format(dicMedia['black_pr'])
        dicMedia['can_afford_article'] = self.radio_format(dicMedia['can_afford_article'])
        dicMedia['comment'] = self.radio_format(dicMedia['comment'])
        dicMedia['award'] = self.radio_format(dicMedia['award'])
        dicMedia['kol'] = self.radio_format(dicMedia['kol'])
        dicMedia['ad'] = self.radio_format(dicMedia['ad'])
        dicMedia['station'] = self.radio_format(dicMedia['station'])
        dicMedia['association'] = self.radio_format(dicMedia['association'])
        dicMedia['worth'] = self.radio_format(dicMedia['worth'])
        dicMedia['src_type'] = self.src_type(dicMedia['src_type'])
        dicMedia['farm_level'] = self.farm_level(dicMedia['farm_level'])
        dicMedia['user'] = dicUser.get(dicMedia['user_id'], '系统')
        return dicMedia

    def wechat_sale_result(self, intId):
        """投放历史数据"""
        tupData = self.importModel('project_feedback').findManyAs(
            self.dicConfig['DB_PROJECT'] + '.feedback as f',
            {
                'fields': ['f.*', 'dm.link as link', 'dm.money as money', 'm.name as media_name',
                           'pd.name as plan_demand_name'],
                'join': self.dicConfig['DB_PROJECT'] + '.media as m ON(f.media_id = m.id) LEFT JOIN ' +
                        self.dicConfig[
                            'DB_PROJECT'] + '.demand_media as dm ON(f.plan_demand_id = dm.plan_demand_id and f.media_id = dm.media_id) LEFT JOIN ' +
                        self.dicConfig['DB_PROJECT'] + '.plan_demand as pd ON(f.plan_demand_id = pd.id)',
                'condition': 'f.media_id = %s' % intId,
                'order': 'id desc'
            }
        )
        for i, item in enumerate(tupData, 1):
            item['web_demand_name'] = '-'
            if item['demand_id']:
                demand_info = self.demand_service.detail(str(item['demand_id']))
                if demand_info:
                    item['web_demand_name'] = demand_info['title']
                else:
                    item['demand_id'] = 0

        return tupData

    def update_wechat_info(self, wechat_id, media_id):
        """更新资料"""
        from api.sogou import Crawler
        res = Crawler().crawl_with_wechat_id(wechat_id, comment=True)
        name = res.get('name')
        if not name:
            return 404
        status = self.update_info(media_id, res)
        return status

    def update_media_part(self, mid, dicArg):
        """更新资料基本信息部分"""
        media_cols = ['name', 'brief', 'identify', 'avatar', 'status']
        dicMedia = {'last_update_time': int(self.time.time())}
        for m_col in media_cols:
            if m_col in dicArg:
                dicMedia[m_col] = dicArg[m_col]
        mediaFields = []
        for k in dicMedia:
            mediaFields.append('{k}="{v}"'.format(k=k, v=dicMedia[k]))
        # 更新媒体基本信息
        self.mediaModel.update({
            'fields': mediaFields,
            'condition': 'id={id}'.format(id=mid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_wechat_part(self, mid, dicArg):
        """更新资料公众号信息部分"""
        wechat_cols = ['qrcode', 'biz', 'gh_id']
        dicWechat = {}
        for w_col in wechat_cols:
            if w_col in dicArg:
                dicWechat[w_col] = dicArg[w_col]
        wechatFields = ['media_id="%s"' % mid]
        for k in dicWechat:
            wechatFields.append('{k}="{v}"'.format(k=k, v=dicWechat[k]))
        # 更新公众号资料
        self.mediaWechatModel.update({
            'fields': wechatFields,
            'condition': 'media_id="{mid}"'.format(mid=mid)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_msg_part(self, mid, dicArg):
        """更新资料图文信息部分"""
        msg_cols = ['url', 'title', 'idx', 'original', 'post_time', 'read_num', 'like_num', 'comment_num']
        dicMsg = {}
        for s_col in msg_cols:
            if s_col in dicArg:
                dicMsg[s_col] = dicArg[s_col]
        msgFields = []
        for k in dicMsg:
            msgFields.append('{k}="{v}"'.format(k=k, v=dicMsg[k]))

        import hashlib
        now = int(self.time.time())
        url_key = hashlib.md5(dicMsg['url']).hexdigest()
        ex = self.msgModel.findOne({'condition': 'url_key="%s"' % url_key})
        if ex:
            self.msgModel.update({
                'fields': ['title="%s"' % dicMsg['title'],
                           'idx=%s' % dicMsg['idx'],
                           'read_num=%s' % dicMsg['read_num'],
                           'like_num=%s' % dicMsg['like_num'],
                           'comment_num=%s' % dicMsg['comment_num'],
                           'last_update_time=%s' % now],
                'condition': 'url_key="%s"' % url_key
            })
        else:
            self.msgModel.insert({
                'key': 'media_id, url, url_key, title, original, post_time, '
                       'idx, read_num, like_num, comment_num, create_time, last_update_time',
                'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' % (
                    mid, dicMsg['url'], url_key, dicMsg['title'], dicMsg['original'], dicMsg['post_time'],
                    dicMsg['idx'], dicMsg['read_num'], dicMsg['like_num'], dicMsg['comment_num'], now, now
                )
            })
        if self.model.db.status != 200:
            return 500
        return 200

    @staticmethod
    def avg(seq):
        if not seq:
            return 0
        return sum(seq) / len(seq)

    @staticmethod
    def get_idx(link):
        """图文位置"""
        if not link:
            return 1
        return link[link.index('idx=') + len('idx='): link.index('idx=') + len('idx=') + 1]

    def update_avg_num(self, mid):
        """更新平均阅读数等信息"""
        data = self.msgModel.findMany({
            'condition': 'media_id=%s' % mid
        })
        # print data
        if not data:
            return 200
        top_read, read, like = [], [], []
        for item in data:
            if item['idx'] == 1:
                top_read.append(item['read_num'])
            read.append(item['read_num'])
            like.append(item['like_num'])
        self.mediaWechatModel.update({
            'fields': ['top_three_avg_read_num=%s' % self.avg(read),
                       'top_avg_read_num=%s' % self.avg(top_read),
                       'like_num=%s' % self.avg(like)],
            'condition': 'media_id=%s' % mid
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def update_info(self, mid, dicArg):
        """更新资料分解"""
        now = int(self.time.time())
        # 帐号状态
        if 'post_time' in dicArg:
            dt = now - dicArg['post_time']
            if dt > 30 * 24 * 3600:
                status = 3
            elif dt < 7 * 24 * 3600:
                status = 1
            else:
                status = 2
            dicArg['status'] = status
        # 简介
        if 'brief' in dicArg:
            dicArg['brief'] = dicArg['brief'].replace('"', '\'')
        # 图文链接
        if 'url' in dicArg:
            dicArg['url'] = dicArg['url'].replace('&amp;', '&')
        # 图文位置
        dicArg['idx'] = self.get_idx(dicArg['url'])

        # 更新信息
        status = self.update_media_part(mid, dicArg)
        if status != 200:
            return status
        status = self.update_wechat_part(mid, dicArg)
        if status != 200:
            return status
        status = self.update_msg_part(mid, dicArg)
        if status != 200:
            return status
        # 计算并更新平均阅读数，头条平均阅读数，平均点赞数
        status = self.update_avg_num(mid)
        if status != 200:
            return status
        return 200

    def msg_info(self, media_id, limit=6):
        """图文列表"""
        res = self.importModel('project_media_msg').findMany({
            'condition': 'media_id="{mid}"'.format(mid=media_id),
            'order': 'post_time desc'
        })
        rtn = res[:limit]
        for i in rtn:
            i['original'] = '原创' if i['original'] else '-'
            i['title'] = i['title'] if i['title'] else '查看原文'
            i['post_time'] = self.formatTime(i['post_time'], '%Y-%m-%d')
        return rtn

    @staticmethod
    def src_type(num):
        _all = {0: '入驻', 1: '新指', 2: '人工', 3: '搜狗', 4: '乐微推', 5: '新榜', 6: '新媒矿'}
        return _all.get(num, '-')

    @staticmethod
    def farm_level(num):
        _all = {0: '-', 1: '无', 2: '轻度', 3: '严重'}
        return num, _all.get(num, '-')

    @staticmethod
    def radio_format(num, option=2):
        if option == 3:
            return num, {0: '不限', 1: '是', 2: '否'}.get(num, '-')
        return num, {1: '是', 2: '否'}.get(num, '-')

    @staticmethod
    def role(num):
        return num, {1: '企业', 2: '个人', 3:'企业品牌号'}.get(num, '-')

    @staticmethod
    def status(num):
        return num, {1: '活跃号', 2: '一般号', 3: '僵尸号'}.get(num, '-')

    @staticmethod
    def ad_type(ad_type):
        # print ad_type, type(ad_type)
        if ad_type == 'None' or ad_type == '0' or not ad_type:
            return {}
        _all = {'1': '软广', '2': '硬广'}
        rtn = {i: _all.get(i) for i in ad_type.split(',')}
        return rtn

    def update_wechat_detail(self, dicArg, uid=0):
        """更新详细信息"""
        dicWechat = {}
        if 'tag' in dicArg:
            tags = dicArg.pop('tag')
            lst_tag = tags.split(',') if tags else []
            media_id = dicArg['id']
            self.mediaTagModel.delete({'condition': 'media_id={mid}'.format(mid=media_id)})
            for tag_id in lst_tag:
                self.mediaTagModel.insert({'key': 'media_id, tag_id', 'val': '%s, %s' % (media_id, tag_id)})
        if 'original' in dicArg:
            dicWechat['original'] = dicArg.pop('original')
        if 'top_avg_read_num' in dicArg:
            dicWechat['top_avg_read_num'] = dicArg.pop('top_avg_read_num')
        if 'top_three_avg_read_num' in dicArg:
            dicWechat['top_three_avg_read_num'] = dicArg.pop('top_three_avg_read_num')
        if 'like_num' in dicArg:
            dicWechat['like_num'] = dicArg.pop('like_num')
        mediaFields = []
        for k in dicArg:
            if k == 'id':
                continue
            if dicArg[k] is None:
                mediaFields.append('{k}={v}'.format(k=k, v='null'))
            else:
                mediaFields.append('{k}=\'{v}\''.format(k=k, v=dicArg[k]))
        mediaFields.append('last_update_time={ut}'.format(ut=int(self.time.time())))
        mediaFields.append('user_id={uid}'.format(uid=uid))
        self.mediaModel.update({
            'fields': mediaFields,
            'condition': 'id={id}'.format(id=dicArg['id'])
        })
        if self.model.db.status != 200:
            return 500
        mediaWechatFields = []
        if dicWechat:
            for k in dicWechat:
                mediaWechatFields.append('{k}={v}'.format(k=k, v=dicWechat[k]))
            self.mediaWechatModel.update({
                'fields': mediaWechatFields,
                'condition': 'media_id={id}'.format(id=dicArg['id'])
            })
        if self.model.db.status != 200:
            return 500
        return 200

    def category(self, num):
        if num is None:
            return
        dicData = self.importModel('project_category_media').findOne({
            'condition': 'id = {id}'.format(id=num)
        })
        return {dicData.get('id', ''): dicData.get('name', '')}

    def tag(self, tag):
        if tag == 'None' or tag is None or tag == '':
            return {}
        tupData = self.importModel('project_tag').findMany({
            'condition': 'id in ({tag})'.format(tag=tag)
        })
        rtn = {str(i['id']): i['name'] for i in tupData}
        return rtn

    @staticmethod
    def original(num):
        return '原创' if num == 1 else '-'

    @staticmethod
    def audience_gender(num):
        return num, {0: '不限', 1: '偏女性', 2: '偏男性'}.get(num, '-')

    def audience_area(self, province, city, county):
        if province == 0:
            return '全国性'
        else:
            area = self.importService('area').get_area(province, city, county)
            return area

    @staticmethod
    def audience_age(age):
        if age == '0' or age is None or age == '':
            return {}
        _all = {'1': '70后', '2': '80后', '3': '85后', '4': '90后', '5': '95后', '6': '其它'}
        rtn = {i: _all.get(i) for i in age.split(',')}
        # print rtn
        return rtn

    @staticmethod
    def audience_career(career):
        if career == '0' or career is None or career == '':
            return {}
        _all = {'1': '工薪阶层', '2': '白领', '3': '高管', '4': '创业者',
                '5': '企事业单位', '6': '国企', '7': '公职人员', '8': '自由职业者'}
        rtn = {i: _all.get(i) for i in career.split(',')}
        return rtn

    def check_biz(self, biz):
        # print biz
        res = self.mediaWechatModel.findOne({
            'condition': 'biz="%s"' % biz
        })
        if res:
            return 601
        return 200

    def follow(self, mid, uid, gid, remark, mediaConf):
        follow_model = self.importModel('project_media_follow')
        res = self.check_follow(mid, uid)
        if res:
            follow_model.delete({
                'condition': 'user_id=%s and media_id=%s' % (uid, mid)
            })
            follow = 0
        else:
            # print "gid = ",gid
            data = follow_model.findMany({
                'fields': ['count(1) as counts, group_id'],
                'condition': 'status=1 group by group_id'
            })
            groupData = {item['group_id']: item['counts'] for item in data}
            errorGroup = []
            for item in gid:
                if int(item) in groupData and groupData[int(item)] >= mediaConf['media_group_max']:
                    errorGroup.append(item)
            if errorGroup:
                return 401, errorGroup

            if gid:
                for i in gid:
                    follow_model.insert({
                        'key': 'user_id, media_id, group_id, remark, create_time',
                        'val': '%s, %s, %s, "%s", %s' % (uid, mid, i, remark, int(self.time.time()))
                    })
            follow = 1
        if self.model.db.status != 200:
            return 500, {}
        return 200, {'follow': follow}


    def create_wechat(self, dicData):
        now = int(self.time.time())
        mediaId = self.mediaModel.insert({
            'key': 'user_id, name, brief, avatar, src_type, create_time, last_update_time',
            'val': '%s, "%s", "%s", "%s", %s, %s, %s' % (
                0, dicData['name'], dicData['features'].replace('"', u'“'), dicData['avatar'], 2, now, now)
        })
        self.mediaWechatModel.insert({
            'key': 'media_id, wechat_id, qrcode, biz, gh_id',
            'val': '%s, "%s", "%s", "%s", "%s"' % (mediaId, dicData['wechat_id'], dicData['qrcode'],
                                                   dicData['biz'], dicData['user_name'])
        })
        if self.model.db.status != 200:
            return 500
        return 200
