# -*- coding:utf-8 -*-

import base


class relation(base.base):
    def __init__(self, *args, **kwargs):
        super(relation, self).__init__(*args, **kwargs)
        self.mediaCommonService = self.importService('media_common')
        self.mediaSearchService = self.importService('media_search')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        dicSearchCondition = {
            'query': self.I('query'),
            'field': self.I('field'),
            'page': int(self.I('page', '1')),
            'relation_type': 1
        }
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        tupResp, rows = self.mediaCommonService.get_contact_page(dicSearchCondition)
        page_url = '/media/relation?'
        if len(lisSearchCondition) > 0:
            page_url = '%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['index_info'] = tupResp
        self.dicViewData['condition'] = dicSearchCondition
        self.dicViewData['page_html'] = self.page(dicSearchCondition['page'], 10, rows, page_url)
        self.display('relation', 'media')

    def get_data(self):
        dicSearchCondition = {
            'query': self.I('query'),
            'field': self.I('field'),
            'page': int(self.I('page', '1')),
            'relation_type': self.I('relation_type', 1)
        }
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        tupResp, rows = self.mediaCommonService.get_contact_page(dicSearchCondition)
        page_url = '/media/relation?'
        if len(lisSearchCondition) > 0:
            page_url = '%s%s' % (page_url, '&'.join(lisSearchCondition))
        # dicViewData['index_info'] = tupResp
        # dicViewData['condition'] = dicSearchCondition
        # dicViewData['page_html'] = self.page(dicSearchCondition['page'], 10, rows, page_url)
        self.out(200, '', {'index_info': tupResp,
                           'condition': dicSearchCondition,
                           'page_html': self.page(dicSearchCondition['page'], 10, rows, page_url)})

    def detail(self):
        cid = self.I('id')
        dicData = self.mediaCommonService.get_contact_detail(cid)
        media = self.mediaSearchService.get_media_by_contact(cid)
        self.dicViewData['detail_info'] = dicData
        self.dicViewData['media'] = media
        self.display('detail', 'media')