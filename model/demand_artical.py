# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'demand_article'

    def insert(self, intDemandId, dicData):
        """ 创建营销内容数据

        @params intDemandId int 营销需求ID
        @params dicData dict 内容数据
        """

        self.db.insert(self.strTableName, {
            'key': 'demand_id, artical_title, artical_author, artical_body, origin_link',
            'val': '"%s", "%s", "%s", "%s", "%s"' % (intDemandId, dicData['artical_title'], 
                dicData['artical_author'], dicData['artical_content'], dicData['artical_origin_url'])
        })

        return self.db.cursor.lastrowid
