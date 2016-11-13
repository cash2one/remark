# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'demand_category_media'
        
    def insert(self, intDemandId, strCateMediaId):
        self.db.b_commit = True
        try:
            for cate_media_id in strCateMediaId.split(","):
                self.db.insert(self.strTableName, {
                    'key': 'demand_id, cate_media_id',
                    'val': '%s, %s' % (intDemandId, cate_media_id)
                })
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']

