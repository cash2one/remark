# -*- coding:utf-8 -*-

import base as base

# 需求列表
class List(base.base):

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)


    def index(self):

        # 获取参数
        intPage         = int(self.I('page', '1'))
        strDemandFormId = self.I('demand_form', '')
        strCategoryId   = self.I('category', '')
        strTagId        = self.I('tag', '')
        strStatusId     = self.I('status', '')
        strMoney        = self.I('money', '')
        dicSearchCondition = {
            'page'          : intPage,
            'demand_form'   : strDemandFormId,
            'category'      : strCategoryId,
            'tag'           : strTagId,
            'status'        : strStatusId,
            'money'         : strMoney,
            'time_begin'    : self.I('time_begin', ''),
            'time_end'      : self.I('time_end', ''),
            'money_begin'   : self.I('money_begin', ''),
            'money_end'     : self.I('money_end', ''),
        }
        
        listSearchCondition = []
        listSearchCondition.append("a=index")
        for key, value in dicSearchCondition.items():
            if key <> 'page' and value <> '':
                listSearchCondition.append("%s=%s" % (key, value))
        
        demandService = self.importService('demand')
        dicDemandList = demandService.demandList(dicSearchCondition)
        self.dicViewData['list']            = dicDemandList['list']
        self.dicViewData['demand_form']     = dicDemandList['demand_form']
        self.dicViewData['category']        = dicDemandList['category']
        self.dicViewData['tag']             = dicDemandList['tag']
        self.dicViewData['status']          = dicDemandList['status']
        self.dicViewData['search_condition']= dicSearchCondition
        self.dicViewData['page']            = self.page(intPage, 10, dicDemandList['count'], '/list?%s' % ('&'.join(listSearchCondition)))
        
        self.display('index')
