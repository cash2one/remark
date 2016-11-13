# -*- coding:utf-8 -*-

import base

class zhihu(base.base):
    def __init__(self, *args, **kwargs):
        super(zhihu, self).__init__(*args, **kwargs)
        self.zhihuService = self.importService('media_zhihu')
        self.mediaService = self.importService('media')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_zhihu'
        intPage = int(self.I('page', '1'))
        dicSearchCondition = {
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
            'black_pr': self.I('black_pr'),
            'can_afford_article': self.I('can_afford_article'),
            'comment': self.I('comment'),
            'award': self.I('award'),
            'kol': self.I('kol'),
            'ad': self.I('ad'),
            'ad_type': self.I('ad_type'),
            'fans_num': ','.join(self.I('fans_num'))
                        if isinstance(self.I('fans_num'), list)
                        else self.I('fans_num'),
            'total_ask_num': ','.join(self.I('total_ask_num'))
                        if isinstance(self.I('total_ask_num'), list)
                        else self.I('total_ask_num'),
            'total_answer_num': ','.join(self.I('total_answer_num'))
                        if isinstance(self.I('total_answer_num'), list)
                        else self.I('total_answer_num'),
            'total_like_num': ','.join(self.I('total_like_num'))
                        if isinstance(self.I('total_like_num'), list)
                        else self.I('total_like_num'),
            'total_thank_num': ','.join(self.I('total_thank_num'))
                        if isinstance(self.I('total_thank_num'), list)
                        else self.I('total_thank_num'),
            'total_favorite_num': ','.join(self.I('total_favorite_num'))
                        if isinstance(self.I('total_favorite_num'), list)
                        else self.I('total_favorite_num'),
            'total_share_num': ','.join(self.I('total_share_num'))
                        if isinstance(self.I('total_share_num'), list)
                        else self.I('total_share_num'),
            'total_record_num': ','.join(self.I('total_record_num'))
                        if isinstance(self.I('total_record_num'), list)
                        else self.I('total_record_num'),
            'total_view_num': ','.join(self.I('total_view_num'))
                        if isinstance(self.I('total_view_num'), list)
                        else self.I('total_view_num'),
            'station': self.I('station'),
            'worth': self.I('worth'),
            'farm_level': self.I('farm_level'),
            'audience_gender': self.I('audience_gender'),
            'audience_age': ','.join(self.I('audience_age'))
                            if isinstance(self.I('audience_age'), list)
                            else self.I('audience_age'),
            'audience_career': ','.join(self.I('audience_career'))
                               if isinstance(self.I('audience_career'), list)
                               else self.I('audience_career'),
            'ask_price': ','.join(self.I('ask_price'))
                           if isinstance(self.I('ask_price'), list)
                           else self.I('ask_price'),
            'answer_price': ','.join(self.I('answer_price'))
                            if isinstance(self.I('answer_price'), list)
                            else self.I('answer_price'),
            'other_price': ','.join(self.I('other_price'))
                            if isinstance(self.I('other_price'), list)
                            else self.I('other_price')
        }
        # print dicSearchCondition
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        # print lisSearchCondition
        dicZhihu = self.zhihuService.get_zhihu_page(dicSearchCondition)
        # pprint(dicZhihu['Zhihu'])
        self.dicViewData['menu'] = strMenu
        self.dicViewData['zhihu'] = dicZhihu['zhihu']
        self.dicViewData['json_zhihu'] = self.json.dumps(dicZhihu['zhihu'])
        self.dicViewData['category'] = dicZhihu['category']
        self.dicViewData['tag'] = dicZhihu['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/zhihu?'
        if len(lisSearchCondition) > 0:
            page_url='%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicZhihu['count'], page_url)

        self.display('zhihu', 'media')


    def detail(self):
        strMenu = 'media_zhihu'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.zhihuService.check_follow(intId, uid)
        dicMedia = self.zhihuService.zhihu_detail(intId)
        lstMediaSale = self.zhihuService.zhihu_sale_result(intId)
        # print dicMedia
        self.dicViewData['menu'] = strMenu
        self.dicViewData['detail_info'] = dicMedia
        self.dicViewData['follow'] = follow
        self.dicViewData['sale_result'] = lstMediaSale
        self.dicViewData['category_info'] = self.json.dumps(self.mediaCommonService.get_category_media())
        self.dicViewData['tag_info'] = self.json.dumps(self.mediaCommonService.get_tag())
        self.dicViewData['area_info'] = self.json.dumps(self.mediaCommonService.get_area())
        self.display('detail', 'media')

    def update_contact(self):
        dicArgs = {
            'id': self.I('id'),
            'contact_person': self.I('contact_person'),
            'contact_phone': self.I('contact_phone'),
            'contact_qq': self.I('contact_qq'),
            'contact_wechat': self.I('contact_wechat'),
            'contact_email': self.I('contact_email')
        }
        # print dicArgs
        self.zhihuService.update_zhihu_detail(dicArgs)
        self.redirect('/media/zhihu?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_value(self):
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'role': self.I('role') if self.I('role') else '0',
            'kol': self.I('kol') if self.I('kol') else '0',
            'fans_num': self.I('fans_num') if self.I('fans_num') else '0',
            'total_ask_num': self.I('total_ask_num') if self.I('total_ask_num') else '0',
            'total_answer_num': self.I('total_answer_num') if self.I('total_answer_num') else '0',
            'total_like_num': self.I('total_like_num') if self.I('total_like_num') else '0',
            'total_thank_num': self.I('total_thank_num') if self.I('total_thank_num') else '0',
            'total_favorite_num': self.I('total_favorite_num') if self.I('total_favorite_num') else '0',
            'total_share_num': self.I('total_share_num') if self.I('total_share_num') else '0',
            'total_record_num': self.I('total_record_num') if self.I('total_record_num') else '0',
            'total_view_num': self.I('total_view_num') if self.I('total_view_num') else '0',
        }
        self.zhihuService.update_zhihu_detail(dicArgs)
        self.redirect('/media/zhihu?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_price(self):
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
            'ask_price': '0' if not self.I('ask_price') else self.I('ask_price'),
            'answer_price': '0' if not self.I('answer_price') else self.I('answer_price'),
            'other_price': '0' if not self.I('other_price') else self.I('other_price')
        }
        self.zhihuService.update_zhihu_detail(dicArgs)
        self.redirect('/media/zhihu?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_audience(self):
        dicArgs = {
            'id': self.I('id'),
            'audience_gender': self.I('audience_gender') if self.I('audience_gender') else '0',
            'audience_province_id':  '0' if self.I('media_audience_province') == '-1' else self.I('media_audience_province'),
            'audience_city_id':  None if self.I('media_audience_city') == '-1' else self.I('media_audience_city'),
            'audience_county_id':  None if self.I('media_audience_county') == '-1' else self.I('media_audience_county'),
            'audience_age':  ','.join(self.I('audience_age')) if self.I('audience_age') else '0',
            'audience_career':  ','.join(self.I('audience_career')) if self.I('audience_age') else '0'
        }
        self.zhihuService.update_zhihu_detail(dicArgs)
        self.redirect('/media/zhihu?a=detail&id={id}'.format(id=dicArgs['id']))

    def follow(self):
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        resp = self.zhihuService.follow(mid, uid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        url = self.I('url')
        status = self.zhihuService.check_url(url)
        if status != 200:
            self.out(status)
            return

        from api.zhihu import Crawler

        dicInfo = Crawler().crawl_with_url(url)
        if not dicInfo.get('name'):
            self.out(401)
            return
        status = self.zhihuService.create_zhihu(dicInfo)
        self.out(status)

    def upload_avatar(self):
        """
        :func: 更新头像
        """
        if not self._POST:
            self.redirect('/402')
            return
        if 'avatar_image' in self.request.files:
            strFile = self.request.files['avatar_image']
        else:
            self.redirect('/402')
            return

        from api.upload import upload

        dicLogo = upload(strFile[0]['body'])
        self.out(200, '', {
            'url': '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicLogo['key'], '-avatar'),
            'key': dicLogo['key']
        })

    def update_base(self):
        url = self.I('url')
        mid = self.I('id')

        from api.zhihu import Crawler
        # print url, mid
        dicInfo = Crawler().crawl_with_url(url)
        dicInfo['id'] = mid
        # print dicInfo
        if not dicInfo.get('name'):
            self.out(401)
            return
        status = self.zhihuService.update_zhihu_base(dicInfo)
        self.out(status)


    def update(self):
        strId = self.I('id')
        strGender = self.I('gender')
        strAd = self.I('ad')
        strKol = self.I('kol')
        status = self.zhihuService.update_Zhihu(strId, strGender, strAd, strKol)
        self.out(status)
