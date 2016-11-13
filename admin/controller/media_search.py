# -*- coding:utf-8 -*-

import base


class search(base.base):
    def __init__(self, *args, **kwargs):
        super(search, self).__init__(*args, **kwargs)
        self.media_search_service = self.importService('media_search')
        self.mediaCommonService = self.importService('media_common')

    def initialize(self, config=None):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'media_search'
        intPage = int(self.I('page', '1'))
        # 注意请保持html中元素的name与url中的参数名一致。
        dicSearchCondition = {
            'page': intPage,
            'field': self.I('field'),
            'query': self.I('query'),
            'uid': self.I('uid'),
            # 统计类型
            'ctype': self.I('ctype'),
            'category': ','.join(self.I('category'))
            if isinstance(self.I('category'), list) else self.I('category'),
            'tag': ','.join(self.I('tag'))
            if isinstance(self.I('tag'), list) else self.I('tag'),
            'audience_province_id': self.I('audience_province_id'),
            'audience_city_id': self.I('audience_city_id'),
            'audience_county_id': self.I('audience_county_id'),
            'audience_gender': self.I('audience_gender'),
            'audience_age': ','.join(self.I('audience_age'))
            if isinstance(self.I('audience_age'), list) else self.I('audience_age'),
            'audience_career': ','.join(self.I('audience_career'))
            if isinstance(self.I('audience_career'), list) else self.I('audience_career'),
        }
        lisSearchCondition = []
        for key in dicSearchCondition:
            value = dicSearchCondition[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        dicSearch = self.media_search_service.get_search_page(dicSearchCondition)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['search'] = dicSearch['search']
        self.dicViewData['json_search'] = self.json.dumps(dicSearch['search'])
        self.dicViewData['category'] = dicSearch['category']
        self.dicViewData['tag'] = dicSearch['tag']
        self.dicViewData['condition'] = dicSearchCondition
        page_url = '/media/search?'
        if len(lisSearchCondition) > 0:
            page_url = '%s%s' % (page_url, '&'.join(lisSearchCondition))
        self.dicViewData['page_html'] = self.page(intPage, 10, dicSearch['count'], page_url)
        self.display('search', 'media')
