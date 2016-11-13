# -*- coding:utf-8 -*-

import base


class media_common(base.base):
    def __init__(self, *args, **kwargs):
        super(media_common, self).__init__(*args, **kwargs)
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        self.redirect('/')

    def get_media_cart(self):
        uid = self.current_user.get('id')
        tupData = self.mediaCommonService.get_media_cart(uid)
        self.out(200, '', tupData)

    def add_media_cart(self):
        uid = self.current_user.get('id')
        mid = self.I('media_id')
        status = self.mediaCommonService.add_media_cart(uid, mid)
        self.out(status)

    def del_media_cart(self):
        uid = self.current_user.get('id')
        mid = self.I('media_id')
        status = self.mediaCommonService.del_media_cart(uid, mid)
        self.out(status)

    def clear_media_cart(self):
        uid = self.current_user.get('id')
        status = self.mediaCommonService.clear_media_cart(uid)
        self.out(status)

    def get_category_media(self):
        tupResp = self.mediaCommonService.get_category_media()
        if tupResp:
            self.out(200, '', tupResp)
            return
        self.out(404)

    def get_tag(self):
        tupResp = self.mediaCommonService.get_tag()
        if tupResp:
            self.out(200, '', tupResp)
            return
        self.out(404)

    def get_area(self):
        pid = self.I('parent_id', 0)
        tupResp = self.mediaCommonService.get_area(pid)
        if tupResp:
            self.out(200, '', tupResp)
            return
        self.out(404)

    def get_contact(self):
        mid = self.I('id')
        rtype = self.I('relation_type', 1)
        tupResp = self.mediaCommonService.get_contact(mid, rtype)
        if tupResp:
            self.out(200, '', tupResp)
            return
        self.out(404)

    def add_contact(self):
        dicArg = {
            'relation_type': self.I('relation_type', 1),
            # 媒体id
            'relation_id': self.I('id'),
            'contact_person': self.I('contact_person'),
            'contact_position': self.I('contact_position'),
            'contact_phone': self.I('contact_phone'),
            'contact_qq': self.I('contact_qq'),
            'contact_wechat': self.I('contact_wechat'),
            'contact_email': self.I('contact_email'),
            'contact_tel': self.I('contact_tel'),
            'contact_other': self.I('contact_other')
        }
        status = self.mediaCommonService.add_contact(dicArg)
        self.out(status)

    def update_contact(self):
        dicArg = {
            'id': self.I('contact_id'),
            'contact_person': self.I('contact_person'),
            'contact_position': self.I('contact_position'),
            'contact_phone': self.I('contact_phone'),
            'contact_qq': self.I('contact_qq'),
            'contact_wechat': self.I('contact_wechat'),
            'contact_email': self.I('contact_email'),
            'contact_tel': self.I('contact_tel'),
            'contact_other': self.I('contact_other')
        }
        status = self.mediaCommonService.update_contact(dicArg)
        self.out(status)

    def del_contact(self):
        dicArg = {
            'contact_id': self.I('contact_id'),
            'relation_id': self.I('relation_id'),
            'relation_type': self.I('relation_type', 1)
        }
        status = self.mediaCommonService.del_contact(dicArg)
        self.out(status)
