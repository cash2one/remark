# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        self.userMenu = self.importModel('user_menu')

    def getMenu(self, menu_level):
        tupData = self.userMenu.findMany({
                'fields': ['main_access','menu_info','menu_name','menu_route','menu_id','parent_id','is_exsit_child'],
                'condition': 'menu_level=%d' % menu_level
            })
        return tupData

    def get_child_Menu(self, parent_id):
        tupData = self.userMenu.findMany({
                'fields': ['main_access','menu_info','menu_name','menu_route'],
                'condition': 'parent_id=%d' % parent_id
            })
        return tupData