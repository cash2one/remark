# -*- coding:utf-8 -*-

import base


class service(base.baseService):

    def __init__(self, _model, param):
        base.baseService.__init__(self, _model, param)
        self.mediaContentModel = self.importModel('mediaTool_content')
        self.mediaCommentModel = self.importModel('mediaTool_comment')

    def create_content(self, title, content, user_id):
        cur_time = int(self.time.time())
        self.mediaContentModel.insert({
            'key':'user_id, title, content, update_time, create_time',
            'val':'%s, \'%s\', \'%s\', %s, %s' % (user_id, title, content, cur_time, cur_time)
        })
        if self.model.db.status != 200:
            return 500
        return 200

    def get_content(self):
        tupData = self.mediaCommentModel.findManyAs(
            self.dicConfig['DB_PROJECT'] +'.media_content as mc', {
            'fields':['mc.*, user.name as name, user.nickname as nickname'],
            'join': self.dicConfig['DB_ADMIN'] + '.user as user ON (user.id = mc.user_id)',
            'condition':'user.status=0'
        })
        return tupData