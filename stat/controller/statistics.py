# -*- coding:utf-8 -*-

import base


class statistics(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 7
        # 筛选时间
        strTimeStart = self.I('start')
        strTimeEnd = self.I('end')
        # 分页url
        strPageUrl = '/statistics?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('statistics_admin').index(
            intPage, intPageDataNum, strTimeStart, strTimeEnd
        )
        dicTotal = self.importService('statistics_admin').total()
        dicToday = self.importService('statistics_admin').today()
        self.dicViewData['total'] = dicTotal
        self.dicViewData['today'] = dicToday
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index')

    # def export(self):
    #     # TODO 导出结果到excel
    #     pass
