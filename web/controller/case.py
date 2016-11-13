# -*- coding:utf-8 -*-

import base

# 首页
class case(base.base):

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.caseService = self.importService('case')

    def index(self):

        #print 111
        intPage = int(self.I('page', '1'))
        case_list = self.caseService.case_view(intPage,15)
        #print case_list
        case_num = case_list[1]
        page_info = self.page(intPage,9,case_num,'/case?a=index')
        self.dicViewData['list'] = case_list[0]
        self.dicViewData['case_num'] = case_num
        self.dicViewData['page'] = page_info
        #print page_info
        self.display('index')

    def detail(self):
        did = self.I('id')
        if did:
            detail_data = self.caseService.case_detail(did)
            self.dicViewData['detail'] = detail_data
            #print detail_data
        self.display('detail')

