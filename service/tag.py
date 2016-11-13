# -*- coding:utf-8 -*-

import base as base


class service(base.baseService):

    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.tagModel = self.importModel('tag')

    def get_tag(self, str_media_id):
        """ get media's tag

        @params str_media_id string media's id
        """
        
        return self.tagModel.findManyAs('media_tag as mt', {
            'fields': ['t.id', 't.name'],
            'join': 'tag as t ON (mt.tag_id = t.id)',
            'condition': 'mt.media_id = "%s"' % str_media_id,
            'order': 't.sort asc'
        })

    def get_list(self):
        """ get list
        """
        
        tupData = self.tagModel.findMany({
            'order': 'sort asc'
        })

        return tupData
