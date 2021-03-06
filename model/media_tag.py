# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'media_tag'

    def insert(self, str_media_id, str_tag_id):
        self.db.b_commit = True
        try:
            for tag_id in str_tag_id.split(","):
                self.db.insert(self.strTableName, {
                    'key': 'media_id, tag_id',
                    'val': '%s, %s' % (str_media_id, tag_id)
                })
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']

