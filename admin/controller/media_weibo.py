# -*- coding:utf-8 -*-

import base

class weibo(base.base):
    def __init__(self, *args, **kwargs):
        super(weibo, self).__init__(*args, **kwargs)
        self.weiboService = self.importService('media_weibo')
        self.mediaService = self.importService('media')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_weibo'
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
            'status': self.I('status'),
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
            'avg_forward_num': ','.join(self.I('avg_forward_num'))
                            if isinstance(self.I('avg_forward_num'), list)
                            else self.I('avg_forward_num'),
            'avg_like_num': ','.join(self.I('avg_like_num'))
                            if isinstance(self.I('avg_like_num'), list)
                            else self.I('avg_like_num'),
            'avg_comment_num': ','.join(self.I('avg_comment_num'))
                            if isinstance(self.I('avg_comment_num'), list)
                            else self.I('avg_comment_num'),
            'worth': self.I('worth'),
            'farm_level': self.I('farm_level'),
            'audience_gender': self.I('audience_gender'),
            'audience_age': ','.join(self.I('audience_age'))
                            if isinstance(self.I('audience_age'), list)
                            else self.I('audience_age'),
            'audience_career': ','.join(self.I('audience_career'))
                               if isinstance(self.I('audience_career'), list)
                               else self.I('audience_career'),
            'one_price': ','.join(self.I('one_price'))
                           if isinstance(self.I('one_price'), list)
                           else self.I('one_price'),
            'forward_price': ','.join(self.I('forward_price'))
                            if isinstance(self.I('forward_price'), list)
                            else self.I('forward_price'),
            'comment_price': ','.join(self.I('comment_price'))
                           if isinstance(self.I('comment_price'), list)
                           else self.I('comment_price'),
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
        dicWeibo = self.weiboService.get_weibo_page(dicSearchCondition)
        # pprint(dicWeibo['Weibo'])
        self.dicViewData['menu'] = strMenu
        self.dicViewData['weibo'] = dicWeibo['weibo']
        self.dicViewData['json_weibo'] = self.json.dumps(dicWeibo['weibo'])
        self.dicViewData['category'] = dicWeibo['category']
        self.dicViewData['tag'] = dicWeibo['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/weibo?'
        if len(lisSearchCondition) > 0:
            page_url='%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicWeibo['count'], page_url)

        self.display('weibo', 'media')


    def detail(self):
        strMenu = 'media_weibo'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.weiboService.check_follow(intId, uid)
        dicMedia = self.weiboService.weibo_detail(intId)
        lstMediaSale = self.weiboService.weibo_sale_result(intId)
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
        self.weiboService.update_weibo_detail(dicArgs)
        self.redirect('/media/weibo?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_value(self):
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'role': self.I('role') if self.I('role') else '0',
            # 'comment': self.I('comment') if self.I('comment') else '0',
            # 'award': self.I('award') if self.I('award') else '0',
            'status': self.I('status') if self.I('status') else '0',
            'kol': self.I('kol') if self.I('kol') else '0',
            'fans_num': self.I('fans_num') if self.I('fans_num') else '0',
            'avg_forward_num': self.I('avg_forward_num') if self.I('avg_forward_num') else '0',
            'avg_like_num': self.I('avg_like_num') if self.I('avg_like_num') else '0',
            'avg_comment_num': self.I('avg_comment_num') if self.I('avg_comment_num') else '0'
        }
        self.weiboService.update_weibo_detail(dicArgs)
        self.redirect('/media/weibo?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_price(self):
        dicArgs = {
            'id': self.I('id'),
            'black_pr': self.I('black_pr') if self.I('black_pr') else '0',
            'can_afford_article': self.I('can_afford_article') if self.I('can_afford_article') else '0',
            'ad': self.I('ad') if self.I('ad') else '0',
            'ad_type': ','.join(self.I('ad_type')) if self.I('ad_type') else None,
            'farm_level': self.I('farm_level') if self.I('farm_level') else '0',
            'worth': self.I('worth') if self.I('worth') else '0',
            'association': self.I('association') if self.I('association') else '0',
            'remark': self.I('remark'),
            'one_price': self.I('one_price') if self.I('one_price') else '0',
            'forward_price': self.I('forward_price') if self.I('forward_price') else '0',
            'comment_price': self.I('comment_price') if self.I('comment_price') else '0',
            'other_price': self.I('other_price') if self.I('other_price') else '0'
        }
        self.weiboService.update_weibo_detail(dicArgs)
        self.redirect('/media/weibo?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_audience(self):
        dicArgs = {
            'id': self.I('id'),
            'audience_gender': self.I('audience_gender') if self.I('audience_gender') else '0',
            'audience_province_id':  '0' if self.I('audience_province_id') == '-1' else self.I('audience_province_id'),
            'audience_city_id':  None if self.I('audience_city_id') == '-1' else self.I('audience_city_id'),
            'audience_county_id':  None if self.I('audience_county_id') == '-1' else self.I('audience_county_id'),
            'audience_age':  ','.join(self.I('audience_age')) if self.I('audience_age') else '0',
            'audience_career':  ','.join(self.I('audience_career')) if self.I('audience_age') else '0'
        }
        self.weiboService.update_weibo_detail(dicArgs)
        self.redirect('/media/weibo?a=detail&id={id}'.format(id=dicArgs['id']))

    def follow(self):
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        resp = self.weiboService.follow(mid, uid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        url = self.I('url')

        from api.weibo import Crawler

        dicInfo = Crawler().crawl_with_url(url)
        if not dicInfo.get('name'):
            self.out(401)
            return
        status = self.weiboService.create_weibo(dicInfo)
        self.out(status)

    def create_more(self):
        urls = self.I('url')
        from api.weibo import Crawler
        data = []
        c = Crawler()
        for url in urls.split('\n'):
            url = url.strip()
            dicInfo = c.crawl_with_url(url)
            if not dicInfo.get('name'):
                data.append({'url': url, 'status': '无效'})
                continue
            status = self.weiboService.create_weibo(dicInfo)
            data.append({'url': url, 'status': '成功' if status == 200 else '失败'})
        self.out(200, '', data)

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

        from api.weibo import Crawler
        # print url, mid
        dicInfo = Crawler().crawl_with_url(url)
        dicInfo['id'] = mid
        # print dicInfo
        if not dicInfo.get('name'):
            self.out(401)
            return
        status = self.weiboService.update_weibo_base(dicInfo)
        self.out(status)

    def update(self):
        strId = self.I('id')
        strGender = self.I('gender')
        strAd = self.I('ad')
        strKol = self.I('kol')
        status = self.weiboService.update_Weibo(strId, strGender, strAd, strKol)
        self.out(status)
