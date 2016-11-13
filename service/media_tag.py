# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        self.mediaTagModel = self.importModel('media_tag')

    def get_media_tag_all(self):
        return self.mediaTagModel.findMany({
            'fields': ['media_id', 'tag_id'],
        })

    def del_list(self, strOfficialId):
        """ del item by official's id

        @params strOfficialId string official's id
        """

        self.mediaTagModel.delete({
            'condition': 'media_id = "%s"' % strOfficialId
        })
