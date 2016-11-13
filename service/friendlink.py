# -*- coding:utf-8 -*-

import base as base


# 友情链接Service
class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)

        # 数据对象
        self.friendlinkModel = self.importModel('friendlink')

    def lists(self):
        tupData = self.friendlinkModel.findMany({
        })
        # lisData = []
        # if tupData:
        #    for item in tupData:

        #        lisData.append(item)

        return tupData
