# -*- coding:utf-8 -*-

import base


class wechat(base.base):
    def __init__(self, *args, **kwargs):
        super(wechat, self).__init__(*args, **kwargs)
        self.mediaCommonService = self.importService('media_common')
        self.media_wechat_service = self.importService('media_wechat')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        """列表页数据"""
        strMenu = 'media_wechat'
        intPage = int(self.I('page', '1'))
        uid = self.current_user.get('id')
        # 注意请保持html中元素的name与url中的参数名一致。
        dicSearchCondition = {
            'sort': self.I('sort', 'last_update_time_desc'),
            'page': intPage,
            'field': self.I('field'),
            'query': self.I('query'),
            'category': ','.join(self.I('category'))
            if isinstance(self.I('category'), list)
            else self.I('category'),
            'tag': ','.join(self.I('tag'))
            if isinstance(self.I('tag'), list)
            else self.I('tag'),
            'role': self.I('role'),
            'status': self.I('status'),
            'original': self.I('original'),
            'black_pr': self.I('black_pr'),
            'can_afford_article': self.I('can_afford_article'),
            'comment': self.I('comment'),
            'award': self.I('award'),
            'kol': self.I('kol'),
            'ad': self.I('ad'),
            'ad_type': self.I('ad_type'),
            'top_avg_read_num': ','.join(self.I('top_avg_read_num'))
            if isinstance(self.I('top_avg_read_num'), list)
            else self.I('top_avg_read_num'),
            'top_three_avg_read_num': ','.join(self.I('top_three_avg_read_num'))
            if isinstance(self.I('top_three_avg_read_num'), list)
            else self.I('top_three_avg_read_num'),
            'like_num': ','.join(self.I('like_num'))
            if isinstance(self.I('like_num'), list)
            else self.I('like_num'),
            'fans_num': ','.join(self.I('fans_num'))
            if isinstance(self.I('fans_num'), list)
            else self.I('fans_num'),
            'station': self.I('station'),
            'worth': self.I('worth'),
            'identify': self.I('identify'),
            'feedback': self.I('feedback'),
            'farm_level': self.I('farm_level'),
            'audience_province_id': self.I('audience_province_id'),
            'audience_city_id': self.I('audience_city_id'),
            'audience_county_id': self.I('audience_county_id'),
            'audience_gender': self.I('audience_gender'),
            'audience_age': ','.join(self.I('audience_age'))
            if isinstance(self.I('audience_age'), list)
            else self.I('audience_age'),
            'audience_career': ','.join(self.I('audience_career'))
            if isinstance(self.I('audience_career'), list)
            else self.I('audience_career'),
            'first_price': ','.join(self.I('first_price'))
            if isinstance(self.I('first_price'), list)
            else self.I('first_price'),
            'second_price': ','.join(self.I('second_price'))
            if isinstance(self.I('first_price'), list)
            else self.I('first_price'),
            'other_price': ','.join(self.I('other_price'))
            if isinstance(self.I('other_price'), list)
            else self.I('other_price')
        }
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        dicWechat = self.media_wechat_service.get_wechat_page(dicSearchCondition, uid)
        tupGroup = self.importService('admin_user').get_group(uid, 1)

        self.dicViewData['menu'] = strMenu
        self.dicViewData['wechat'] = dicWechat['wechat']
        self.dicViewData['json_wechat'] = self.json.dumps(dicWechat['wechat'])
        self.dicViewData['category'] = dicWechat['category']
        self.dicViewData['tag'] = dicWechat['tag']
        self.dicViewData['group'] = tupGroup
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/wechat?'
        if len(lisSearchCondition) > 0:
            page_url = '%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicWechat['count'], page_url)
        self.display('wechat', 'media')

    def detail(self):
        """详情页数据"""
        strMenu = 'media_wechat'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.media_wechat_service.check_follow(intId, uid)
        dicMedia = self.media_wechat_service.wechat_detail(intId)
        lstMediaSale = self.media_wechat_service.wechat_sale_result(intId)
        tupGroup = self.importService('admin_user').get_group(uid, 1)
        # print dicMedia
        self.dicViewData['menu'] = strMenu
        self.dicViewData['detail_info'] = dicMedia
        self.dicViewData['follow'] = follow
        self.dicViewData['group'] = tupGroup
        self.dicViewData['sale_result'] = lstMediaSale
        self.dicViewData['category_info'] = self.json.dumps(self.mediaCommonService.get_category_media())
        self.dicViewData['tag_info'] = self.json.dumps(self.mediaCommonService.get_tag())
        self.dicViewData['area_info'] = self.json.dumps(self.mediaCommonService.get_area())
        self.display('detail', 'media')

    def get_wechat_follow(self):
        wechat_follow = {}
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        wechat_follow['follow'] = self.media_wechat_service.check_follow(intId, uid)
        wechat_follow['group'] = self.importService('admin_user').get_group(uid, 1)
        self.out(200, '', wechat_follow)

    def msg_info(self):
        """图文数据"""
        media_id = self.I('media_id')
        res = self.media_wechat_service.msg_info(media_id)
        if not res:
            self.out(404)
        else:
            self.out(200, '', res)

    def update_wechat(self):
        """更新资料"""
        media_id = self.I('media_id')
        wechat_id = self.I('wechat_id')
        status = self.media_wechat_service.update_wechat_info(wechat_id, media_id)
        self.out(status)

    def update_value(self):
        """更新价值信息"""
        uid = self.current_user.get('id')
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'role': self.I('role') if self.I('role') else '0',
            'status': self.I('status') if self.I('status') else '0',
            'original': ','.join(self.I('original')) if self.I('original') else '0',
            'comment': self.I('comment') if self.I('comment') else '0',
            'award': self.I('award') if self.I('award') else '0',
            'kol': self.I('kol') if self.I('kol') else '0',
            'fans_num': self.I('fans_num') if self.I('fans_num') else '0',
            'top_avg_read_num': self.I('top_avg_read_num') if self.I('top_avg_read_num') else '0',
            'top_three_avg_read_num': self.I('top_three_avg_read_num') if self.I('top_three_avg_read_num') else '0',
            'like_num': self.I('like_num') if self.I('like_num') else '0'
        }
        self.media_wechat_service.update_wechat_detail(dicArgs, uid)
        self.redirect('/media/wechat?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_price(self):
        """更新刊例报价"""
        uid = self.current_user.get('id')
        dicArgs = {
            'id': self.I('id'),
            'black_pr': self.I('black_pr') if self.I('black_pr') else '0',
            'can_afford_article': self.I('can_afford_article') if self.I('can_afford_article') else '0',
            'ad': self.I('ad') if self.I('ad') else '0',
            'ad_type': ','.join(self.I('ad_type')) if self.I('ad_type') else None,
            'station': self.I('station') if self.I('station') else '0',
            'farm_level': self.I('farm_level') if self.I('farm_level') else '0',
            'worth': self.I('worth') if self.I('worth') else '0',
            'association': self.I('association') if self.I('association') else '0',
            'remark': self.I('remark'),
            'first_price': '0' if not self.I('first_price') else self.I('first_price'),
            'second_price': '0' if not self.I('second_price') else self.I('second_price'),
            'other_price': '0' if not self.I('other_price') else self.I('other_price')
        }
        # print dicArgs
        self.media_wechat_service.update_wechat_detail(dicArgs, uid)
        self.redirect('/media/wechat?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_audience(self):
        """更新受众信息"""
        uid = self.current_user.get('id')
        dicArgs = {
            'id': self.I('id'),
            'audience_gender': self.I('audience_gender') if self.I('audience_gender') else '0',
            'audience_province_id': '0' if self.I('audience_province_id') == '-1' else self.I('audience_province_id'),
            'audience_city_id': None if self.I('audience_city_id') == '-1' else self.I('audience_city_id'),
            'audience_county_id': None if self.I('audience_county_id') == '-1' else self.I('audience_county_id'),
            'audience_age': ','.join(self.I('audience_age')) if self.I('audience_age') else '0',
            'audience_career': ','.join(self.I('audience_career')) if self.I('audience_age') else '0'
        }
        # print dicArgs
        self.media_wechat_service.update_wechat_detail(dicArgs, uid)
        self.redirect('/media/wechat?a=detail&id={id}'.format(id=dicArgs['id']))

    @staticmethod
    def get_biz(link):
        if not link:
            return
        try:
            biz = link[link.index('__biz=') + len('__biz='): link.index('&')]
        except ValueError:
            biz = ''
        return biz

    def follow(self):
        """媒体跟踪功能"""
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        gid = self.I('group_id')
        if gid:
            gid = gid.split(',')
        else:
            gid = ['0']
        resp = self.media_wechat_service.follow(mid, uid, gid, remark, self.mediaConf)
        status, data = resp
        if status == 401:
            if '0' in data:
                self.out(status, '', ['默认'])
                return

            tupData = self.importService('admin_user').get_media_group(uid, 1, data)
            groupName = [item['name'] for item in tupData]
            self.out(status, '', groupName)
        else:
            self.out(status, '', data)

    def create(self):
        """新增功能"""
        url = self.I('url')

        from api.crawler import crawler
        dicInfo = crawler().official(url, '')
        dicInfo['url'] = url
        biz = dicInfo.get('biz')
        if not biz:
            self.out(401)
            return
        if not dicInfo.get('name'):
            self.out(401)
            return
        res = self.media_wechat_service.check_biz(biz)
        if res != 200:
            self.out(res)
            return
        status = self.media_wechat_service.create_wechat(dicInfo)
        self.out(status)
