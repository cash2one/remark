# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'demand_media_tag'

    def insert(self, intDemandId, strTagId):
        self.db.b_commit = True
        try:
            for tag_id in strTagId.split(","):
                self.db.insert(self.strTableName, {
                    'key': 'demand_id, tag_id',
                    'val': '%s, %s' % (intDemandId, tag_id)
                })
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']
