# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'demand_extra'

    def insert(self, intDemandId, dicData):
        """ 创建数据
        """
        self.db.b_commit = True
        try:
            self.db.insert(
                self.strTableName,
                {
                    'key': 'demand_id, original, num, view, audience_num, audience_gender, '
                           'article_status, origin_link, doc_path, extra_info, create_time',
                    'val': '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' %
                           (intDemandId, dicData['original'], dicData['num'], dicData['view'],
                            dicData['audience_num'], dicData['audience_gender'], dicData['article_status'],
                            dicData['origin_link'], dicData['doc_path'], dicData['extra_info'], dicData['create_time'])
                }
            )
        except Exception, e:
            print e
            self.db.status = self.db.dicConfig['DB_ERROR']
