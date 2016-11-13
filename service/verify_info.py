# -*- coding: utf-8 -*-

import base as base


# 需求Service
class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.verifyModel = self.importModel('verify_info')

    def get_component_verify_ticket(self):
        res = self.verifyModel.findOne({
            'condition': 'name = "component_verify_ticket"'
        })
        return res.get('value', '')

    def set_component_verify_ticket(self, strTicket):
        res = self.verifyModel.findOne({
            'condition': 'name = "component_verify_ticket"'
        })
        if not res:
            self.verifyModel.insert({
                'key': 'name, value, expires_in, last_update_time',
                'val': '"%s", "%s", "%s", "%s"' % ('component_verify_ticket', strTicket, 0, int(self.time.time()))
            })
        else:
            self.verifyModel.update({
                'fields': ['value="%s"' % strTicket, 'last_update_time="%s"' % int(self.time.time())],
                'condition': 'name = "component_verify_ticket"'
            })
        if self.model.db.status != 200:
            return 500
        return 200