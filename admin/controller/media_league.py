# -*- coding: utf-8 -*-

import base


class league(base.base):
    def __init__(self, *args, **kwargs):
        super(league, self).__init__(*args, **kwargs)
        self.leagueService = self.importService('media_league')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_league'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/media/league?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        tupIndexInfo, intRows = self.importService('media_league').get_league(intPage, intPageDataNum, strSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['league'] = tupIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('league', 'media')

    def detail(self):
        strMenu = 'media_league'
        _id = self.I('id')
        dicLeague = self.leagueService.get_league_detail(_id)
        # print dicMedia
        res = self.leagueService.get_league_media(_id)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['media'] = res.get('media', [])
        self.dicViewData['category'] = res.get('category', [])
        self.dicViewData['tag'] = res.get('tag', [])
        self.dicViewData['detail_info'] = dicLeague
        self.display('detail', 'media')

    def create(self):
        dicArgs = {
            'name': self.I('league_name'),
            'description': self.I('league_description'),
        }
        status = self.leagueService.create_league(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/league'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

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
        self.leagueService.update_league(dicArgs)
        self.redirect('/media/league?a=detail&id={id}'.format(id=dicArgs['id']))

    def update(self):
        dicArgs = {
            'id': self.I('id'),
            'name': self.I('league_name'),
            'description': self.I('league_description'),
        }
        status = self.leagueService.update_league(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/league?a=detail&id={id}'.format(id=dicArgs['id'])
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def add_media(self):
        league_id = self.I('league_id')
        media_id = self.I('media_id')
        status = self.leagueService.add_media(league_id, media_id)
        self.out(status)

    def remove_media(self):
        league_id = self.I('id')
        media_id = self.I('media_id')
        status = self.leagueService.remove_media(league_id, media_id)
        if status == 200:
            strRedirectUrl = '/media/league?a=detail&id={id}'.format(id=league_id)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)
