# -*- coding:utf-8 -*-

import base

class wechat_friend(base.base):
    def __init__(self, *args, **kwargs):
        super(wechat_friend, self).__init__(*args, **kwargs)
        self.wechatFriendService = self.importService('media_wechat_friend')
        self.mediaService = self.importService('media')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_wechat_friend'
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
            'forward_price': ','.join(self.I('forward_price'))
                           if isinstance(self.I('forward_price'), list)
                           else self.I('forward_price'),
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
        dicWechatFriend = self.wechatFriendService.get_wechat_friend_page(dicSearchCondition)
        # pprint(dicWechatFriend['WechatFriend'])
        self.dicViewData['menu'] = strMenu
        self.dicViewData['wechat_friend'] = dicWechatFriend['wechat_friend']
        self.dicViewData['json_wechat_friend'] = self.json.dumps(dicWechatFriend['wechat_friend'])
        self.dicViewData['category'] = dicWechatFriend['category']
        self.dicViewData['tag'] = dicWechatFriend['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/wechat_friend?'
        if len(lisSearchCondition) > 0:
            page_url='%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicWechatFriend['count'], page_url)

        self.display('wechat_friend', 'media')


    def detail(self):
        strMenu = 'media_wechat_friend'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.wechatFriendService.check_follow(intId, uid)
        dicMedia = self.wechatFriendService.wechat_friend_detail(intId)
        lstMediaSale = self.wechatFriendService.wechat_friend_sale_result(intId)
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
        self.wechatFriendService.update_wechat_friend_detail(dicArgs)
        self.redirect('/media/wechat_friend?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_value(self):
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'comment': self.I('comment') if self.I('comment') else '0',
            'kol': self.I('kol') if self.I('kol') else '0',
            'fans_num': self.I('fans_num') if self.I('fans_num') else '0',
        }
        self.wechatFriendService.update_wechat_friend_detail(dicArgs)
        self.redirect('/media/wechat_friend?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_price(self):
        dicArgs = {
            'id': self.I('id'),
            'black_pr': self.I('black_pr') if self.I('black_pr') else '0',
            'ad': self.I('ad') if self.I('ad') else '0',
            'ad_type': ','.join(self.I('ad_type')) if self.I('ad_type') else None,
            'worth': self.I('worth') if self.I('worth') else '0',
            'association': self.I('association') if self.I('association') else '0',
            'remark': self.I('remark'),
            'forward_price': '0' if not self.I('forward_price') else self.I('forward_price'),
            'other_price': '0' if not self.I('other_price') else self.I('other_price')
        }
        self.wechatFriendService.update_wechat_friend_detail(dicArgs)
        self.redirect('/media/wechat_friend?a=detail&id={id}'.format(id=dicArgs['id']))

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
        self.wechatFriendService.update_wechat_friend_detail(dicArgs)
        self.redirect('/media/wechat_friend?a=detail&id={id}'.format(id=dicArgs['id']))

    def follow(self):
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        resp = self.wechatFriendService.follow(mid, uid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        dicArgs = {
            'name': self.I('wechat_friend_name'),
            'brief': self.I('wechat_friend_brief'),
            'avatar': self.I('wechat_friend_avatar'),
            'wechat_id': self.I('wechat_friend_wechat_id'),
            'forward_price': self.I('wechat_friend_forward_price')
        }
        status = self.wechatFriendService.create_wechat_friend(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/wechat_friend'
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
            'name': self.I('wechat_friend_name'),
            'brief': self.I('wechat_friend_brief'),
            'avatar': self.I('wechat_friend_avatar'),
            'wechat_id': self.I('wechat_friend_wechat_id'),
        }
        status = self.wechatFriendService.update_wechat_friend_base(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/wechat_friend?a=detail&id=%s' % pid
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        strId = self.I('id')
        strGender = self.I('gender')
        strAd = self.I('ad')
        strKol = self.I('kol')
        status = self.wechatFriendService.update_WechatFriend(strId, strGender, strAd, strKol)
        self.out(status)
