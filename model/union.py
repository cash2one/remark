# -*- coding:utf-8 -*-

import base


class model(base.baseDBModel):
    def __init__(self, _model):
        base.baseDBModel.__init__(self, _model.db)
        self.strTableName = 'pt_unions'
        self.strTableNameMember = 'pt_unions_members'
        self.strTableNameCategory = 'pt_unions_categorys'

