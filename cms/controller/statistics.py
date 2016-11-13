# -*- coding:utf-8 -*-

import base
import json


class statistics(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'statistics_realtime'
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
        strPageUrl = '/statistics/web?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 获取首页数据和数目
        lisIndexInfo, intRows,list_date = self.importService('admin_statistics').index(
            intPage, intPageDataNum, strTimeStart, strTimeEnd
        )
        #autho pan yang 通过listindexinfo获得对应日期，并重新包装加入对应的uv pv信息
        lisIndexInfo_eric=[]
        #print list_date
        for item in lisIndexInfo :
            listitem = list(item)
            date=listitem[0]
            stat=self.importService('eric_stat').findstat(date)
            listitem.extend(stat)
            temp=self.importService('eric_stat').find_demand_num(date)
            #print temp
            listitem.append(temp)
            lisIndexInfo_eric.append(listitem)

        wait_order = self.importService('eric_stat').find_wait_order()
        in_appeal = self.importService('eric_stat').find_in_appeal()
        complete = self.importService('eric_stat').find_complete()
        in_demand = self.importService('eric_stat').find_in_demand()
        wait_feedback = self.importService('eric_stat').find_wait_feedback()
        #print wait_order

        dicTotal = self.importService('admin_statistics').total()
        dicToday = self.importService('admin_statistics').today()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['wait_feedback'] = wait_feedback
        self.dicViewData['in_demand'] = in_demand
        self.dicViewData['in_appeal'] = in_appeal
        self.dicViewData['wait_order'] = wait_order
        self.dicViewData['complete']=complete
        self.dicViewData['total'] = dicTotal
        self.dicViewData['today'] = dicToday
        self.dicViewData['index_info'] = lisIndexInfo_eric#重新包装后带有uv pv ip信息的
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index','statistics')

    # def export(self):
    #     # TODO 导出结果到excel
    #     pass
class business(base.base):
    def initialize(self):
        base.base.initialize(self)

    def index(self):
        strMenu = 'statistics_business'
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
        strPageUrl = '/statistics/business?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 获取首页数据和数目
        lisIndexInfo, intRows, list_date = self.importService('admin_statistics').index(
            intPage, intPageDataNum, strTimeStart, strTimeEnd
        )
        #autho pan yang 通过listindexinfo获得对应日期，并重新包装加入对应的uv pv信息
        lisIndexInfo_eric=[]
        business_eric=[]
        for item in lisIndexInfo :
            listitem = list(item)
            date=listitem[0]
            stat=self.importService('eric_stat').findstat(date)
            listitem.extend(stat)
            temp=self.importService('eric_stat').find_demand_num(date)
            #print temp
            listitem.append(temp)
            lisIndexInfo_eric.append(listitem)
            #print stat

        #获取echarts数据
        for date in list_date:
            date_data=[]
            stat=self.importService('eric_stat').findstat(date)
            temp=self.importService('eric_stat').find_demand_num(date)
            temp['user_login']=stat[0]['stat_user_day']
            date_data.append(date)
            date_data.append(temp)
            business_eric.append(date_data)


        dicTotal = self.importService('admin_statistics').total()
        dicToday = self.importService('admin_statistics').today()
        json_business =json.dumps(business_eric)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['business'] = json_business
        self.dicViewData['total'] = dicTotal
        self.dicViewData['today'] = dicToday
        self.dicViewData['index_info'] = lisIndexInfo_eric#重新包装后带有uv pv ip信息的
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index','statistics')


class operation(base.base):
    def initialize(self):
        base.base.initialize(self)

    def index(self):
        strMenu = 'statistics_operation'
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
        strPageUrl = '/statistics/operation?start={start}&end={end}'.format(start=strTimeStart, end=strTimeEnd)
        # 获取首页数据和数目
        lisIndexInfo, intRows, list_date = self.importService('admin_statistics').index(
            intPage, intPageDataNum, strTimeStart, strTimeEnd
        )
        #autho pan yang 通过listindexinfo获得对应日期，并重新包装加入对应的uv pv信息
        lisIndexInfo_eric=[]

        operation_eric=[]
        for item in lisIndexInfo :
            listitem = list(item)
            date=listitem[0]
            stat=self.importService('eric_stat').findstat(date)
            listitem.extend(stat)
            temp=self.importService('eric_stat').find_demand_num(date)
            #print temp
            listitem.append(temp)
            lisIndexInfo_eric.append(listitem)


        #获取echarts数据
        for date in list_date:
            date_data=[]
            stat=self.importService('eric_stat').findstat(date)
            stat_merge=dict(stat[0].items()+stat[1].items())
            date_data.append(date)
            date_data.append(stat_merge)
            operation_eric.append(date_data)


        dicTotal = self.importService('admin_statistics').total()
        dicToday = self.importService('admin_statistics').today()
        json_operation =json.dumps(operation_eric)
        self.dicViewData['operation'] = json_operation
        #print json_operation
        self.dicViewData['menu'] = strMenu
        self.dicViewData['total'] = dicTotal
        self.dicViewData['today'] = dicToday
        self.dicViewData['index_info'] = lisIndexInfo_eric#重新包装后带有uv pv ip信息的
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index','statistics')