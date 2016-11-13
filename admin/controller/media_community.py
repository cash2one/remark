# -*- coding:utf-8 -*-

import base

class community(base.base):
    def __init__(self, *args, **kwargs):
        super(community, self).__init__(*args, **kwargs)
        self.communityService = self.importService('media_community')
        self.mediaService = self.importService('media')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_community'
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
            'status': self.I('status'),
            'ad': self.I('ad'),
            'audience_gender': self.I('audience_gender'),
            'audience_age': ','.join(self.I('audience_age'))
                            if isinstance(self.I('audience_age'), list)
                            else self.I('audience_age'),
            'audience_career': ','.join(self.I('audience_career'))
                               if isinstance(self.I('audience_career'), list)
                               else self.I('audience_career'),
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
        dicCommunity = self.communityService.get_community_page(dicSearchCondition)
        # pprint(dicCommunity['Community'])
        self.dicViewData['menu'] = strMenu
        self.dicViewData['community'] = dicCommunity['community']
        self.dicViewData['json_community'] = self.json.dumps(dicCommunity['community'])
        self.dicViewData['category'] = dicCommunity['category']
        self.dicViewData['tag'] = dicCommunity['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/community?'
        if len(lisSearchCondition) > 0:
            page_url='%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicCommunity['count'], page_url)

        self.display('community', 'media')


    def detail(self):
        strMenu = 'media_community'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.communityService.check_follow(intId, uid)
        dicMedia = self.communityService.community_detail(intId)
        lstMediaSale = self.communityService.community_sale_result(intId)
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
        self.communityService.update_community_detail(dicArgs)
        self.redirect('/media/community?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_value(self):
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'status': self.I('status') if self.I('status') else '0',
        }
        self.communityService.update_community_detail(dicArgs)
        self.redirect('/media/community?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_price(self):
        dicArgs = {
            'id': self.I('id'),
            'ad': self.I('ad') if self.I('ad') else '0',
            'remark': self.I('remark'),
            'other_price': '0' if not self.I('other_price') else self.I('other_price')
        }
        self.communityService.update_community_detail(dicArgs)
        self.redirect('/media/community?a=detail&id={id}'.format(id=dicArgs['id']))

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
        self.communityService.update_community_detail(dicArgs)
        self.redirect('/media/community?a=detail&id={id}'.format(id=dicArgs['id']))

    def follow(self):
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        resp = self.communityService.follow(mid, uid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        dicArgs = {
            'name': self.I('community_name'),
            'brief': self.I('community_brief'),
            'avatar': self.I('community_avatar'),
            'population': self.I('community_population')
        }
        status = self.communityService.create_community(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/community'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

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
        pid = self.I('id')
        dicArgs = {
            'id': pid,
            'name': self.I('community_name'),
            'brief': self.I('community_brief'),
            'avatar': self.I('community_avatar'),
            'population': self.I('community_population')
        }
        status = self.communityService.update_community_base(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/community?a=detail&id=%s' % pid
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        strId = self.I('id')
        strGender = self.I('gender')
        strAd = self.I('ad')
        strKol = self.I('kol')
        status = self.communityService.update_Community(strId, strGender, strAd, strKol)
        self.out(status)
