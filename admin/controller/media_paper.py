# -*- coding:utf-8 -*-

import base

class paper(base.base):
    def __init__(self, *args, **kwargs):
        super(paper, self).__init__(*args, **kwargs)
        self.paperService = self.importService('media_paper')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_paper'
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
        # print dicSearchCondition
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        # print lisSearchCondition
        dicPaper = self.paperService.get_paper_page(dicSearchCondition)
        # pprint(dicPaper['Paper'])
        self.dicViewData['menu'] = strMenu
        self.dicViewData['paper'] = dicPaper['paper']
        self.dicViewData['json_paper'] = self.json.dumps(dicPaper['paper'])
        self.dicViewData['category'] = dicPaper['category']
        self.dicViewData['tag'] = dicPaper['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/paper?'
        if len(lisSearchCondition) > 0:
            page_url='%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicPaper['count'], page_url)

        self.display('paper', 'media')


    def detail(self):
        strMenu = 'project_paper'
        intId = int(self.I('id'))
        uid = self.current_user.get('id')
        follow = self.paperService.check_follow(intId, uid)
        dicMedia = self.paperService.paper_detail(intId)
        lstMediaSale = self.paperService.paper_sale_result(intId)
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
            'contact_phone': self.I('contact_phone'),
            'contact_qq': self.I('contact_qq'),
            'contact_wechat': self.I('contact_wechat'),
            'contact_email': self.I('contact_email')
        }
        # print dicArgs
        self.paperService.update_paper_detail(dicArgs)
        self.redirect('/media/paper?a=detail&id={id}'.format(id=dicArgs['id']))

    def update_value(self):
        dicArgs = {
            'id': self.I('id'),
            'category_media_id': None if self.I('category_media_id') == '' else self.I('category_media_id'),
            'tag': ','.join(self.I('tag')) if isinstance(self.I('tag'), list) else self.I('tag'),
            'role': self.I('role') if self.I('role') else '0',
            'comment': self.I('comment') if self.I('comment') else '0',
            'award': self.I('award') if self.I('award') else '0',
            'kol': self.I('kol') if self.I('kol') else '0',
            'fans_num': self.I('fans_num') if self.I('fans_num') else '0',
        }
        self.paperService.update_paper_detail(dicArgs)
        self.redirect('/media/paper?a=detail&id={id}'.format(id=dicArgs['id']))

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
            'other_price': '0' if not self.I('other_price') else self.I('other_price')
        }
        self.paperService.update_paper_detail(dicArgs)
        self.redirect('/media/paper?a=detail&id={id}'.format(id=dicArgs['id']))

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
        self.paperService.update_paper_detail(dicArgs)
        self.redirect('/media/paper?a=detail&id={id}'.format(id=dicArgs['id']))

    def follow(self):
        mid = self.I('media_id')
        remark = self.I('remark')
        uid = self.current_user.get('id')
        resp = self.paperService.follow(mid, uid, remark)
        status, data = resp
        self.out(status, '', data)

    def create(self):
        dicArgs = {
            'name': self.I('paper_name'),
            'brief': self.I('paper_brief'),
            'avatar': self.I('paper_avatar'),
            'description': self.I('paper_description')
        }
        status = self.paperService.create_paper(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/paper'
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
            'name': self.I('paper_name'),
            'brief': self.I('paper_brief'),
            'avatar': self.I('paper_avatar'),
            'description': self.I('paper_description')
        }
        status = self.paperService.update_paper_base(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/paper?a=detail&id=%s' % pid
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def update(self):
        strId = self.I('id')
        strGender = self.I('gender')
        strAd = self.I('ad')
        strKol = self.I('kol')
        status = self.paperService.update_Paper(strId, strGender, strAd, strKol)
        self.out(status)
