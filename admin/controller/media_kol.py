# -*- coding: utf-8 -*-

import base


class kol(base.base):
    def __init__(self, *args, **kwargs):
        super(kol, self).__init__(*args, **kwargs)
        self.kolService = self.importService('media_kol')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_kol'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/media/kol?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        tupIndexInfo, intRows = self.importService('media_kol').get_kol(intPage, intPageDataNum, strSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['kol'] = tupIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('kol', 'media')

    def detail(self):
        strMenu = 'media_kol'
        _id = self.I('id')
        dicKol = self.kolService.get_kol_detail(_id)
        # print dicMedia
        res = self.kolService.get_kol_media(_id)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['media'] = res.get('media', [])
        self.dicViewData['category'] = res.get('category', [])
        self.dicViewData['tag'] = res.get('tag', [])
        self.dicViewData['detail_info'] = dicKol
        self.display('detail', 'media')

    def create(self):
        dicArgs = {
            'name': self.I('kol_name'),
            'area': self.I('kol_area'),
            'company': self.I('kol_company'),
            'description': self.I('kol_description'),
        }
        status = self.kolService.create_kol(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/kol'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    # def update_contact(self):
    #     dicArgs = {
    #         'id': self.I('id'),
    #         'contact_person': self.I('contact_person'),
    #         'contact_phone': self.I('contact_phone'),
    #         'contact_qq': self.I('contact_qq'),
    #         'contact_wechat': self.I('contact_wechat'),
    #         'contact_email': self.I('contact_email')
    #     }
    #     # print dicArgs
    #     self.kolService.update_kol(dicArgs)
    #     self.redirect('/media/kol?a=detail&id={id}'.format(id=dicArgs['id']))

    def update(self):
        dicArgs = {
            'id': self.I('id'),
            'name': self.I('kol_name'),
            'role': self.I('kol_role'),
            'area': self.I('kol_area'),
            'company': self.I('kol_company'),
            'description': self.I('kol_description'),
            'write_price': self.I('kol_write_price'),
            'other_price': self.I('kol_other_price'),
            'remark': self.I('kol_remark')
        }
        status = self.kolService.update_kol(dicArgs)
        if status == 200:
            strRedirectUrl = '/media/kol?a=detail&id={id}'.format(id=dicArgs['id'])
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def add_media(self):
        kol_id = self.I('kol_id')
        media_id = self.I('media_id')
        status = self.kolService.add_media(kol_id, media_id)
        self.out(status)

    def remove_media(self):
        kol_id = self.I('id')
        media_id = self.I('media_id')
        status = self.kolService.remove_media(kol_id, media_id)
        if status == 200:
            strRedirectUrl = '/media/kol?a=detail&id={id}'.format(id=kol_id)
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)
