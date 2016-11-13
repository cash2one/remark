# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 首页搜索引擎
        self.index_seo_model = self.importModel('index_seo')

    def getSeo(self, args):
        if 'tag' not in args:
            return 401, ''
        seoData = self.index_seo_model.findOne({
            'fields':['keywords, description, update_time'],
            'condition':'tag = {tag}'.format(tag = args['tag'][0])
        })
        return 200, seoData

    def update(self, args):
        if not ('keywords' in args or 'description' in args or 'tag' in args):
            return 401

        if len(args['keywords'])>512 or len(args['description'])>512:
            return 401

        cur_time = int(self.time.time())
        self.index_seo_model.update({
            'fields':['keywords = \'{ky}\''.format(ky = args['keywords'][0]),
                      'description = \'{ds}\''.format(ds = args['description'][0]),
                      'update_time = {ct}'.format(ct = cur_time)
                    ],
            'condition':'tag = {tag}'.format(tag = args['tag'][0])
        })
        if self.model.db.status != 200:
            self.status = 500
        return 200

