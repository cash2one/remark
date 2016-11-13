# -*- coding:utf-8 -*-

import base as base

class Area(base.base):
    """ 城市控制器
    """

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.areaService = self.importService('area')

    def index(self):
        
        # 跳转到首页
        self.redirect('/')

        return

    def get_list(self):
        """ 获取需市列表
        """

        # 获取参数
        strParentId = self.I('parent_id')
        strParentId = strParentId if strParentId else 0

        tupData = self.areaService.get_list(strParentId)
        if tupData:
            self.out(200, '', tupData)
        else:
            self.out(500)
        
