# -*- coding:utf-8 -*-

import base

class advertiser(base.base):
    advertiserStatus_init = ["","销售线索","接触中","意向客户","成交客户"]
    # status4=["","执行中","暂停调整"]
    status4=["","稳定客户","短期客户"]

    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.user_id = self.current_user.get('id')
        self.project_service = self.importService('project_advertiser')
        self.mediaCommonService = self.importService('media_common')


    def index(self):
        strMenu = 'project_advertiser'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 搜索内容
        listSearch = {
            "searchType":self.I('searchType'),
            "search_txt":self.I('search_txt'),
            "search_level":self.I('search_level'),
            "sub_status":self.I('sub_status')
        }
        lisSearchCondition = []
        for key in listSearch:
            value = listSearch[key]
            if key != 'page' and value and value != '-1' and value != ',':
                lisSearchCondition.append("%s=%s" % (key, value))
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/advertiser?'
        if len(lisSearchCondition) > 0:
            strPageUrl='%s%s' % (strPageUrl, '&'.join(lisSearchCondition))
        tupData, intRows = self.project_service.get_advertiser(intPage, intPageDataNum, listSearch)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['advertiser'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['listSearch'] = listSearch
        self.display('advertiser', 'project')

    def detail(self):
        '''
        :func: 查看详细信息
        '''
        intId = int(self.I('id'))
        strType = self.I('type') or 'look'
        tupPlan = self.project_service.advertiser_plan(intId)
        self.dicViewData['plan'] = tupPlan
        uid = self.current_user.get('id')
        userData = self.importService('admin_user').get_user_data(uid)
        self.dicViewData['name'] = userData[0]['nickname']
        self.dicViewData['id'] = intId
        if strType == 'look':
            self.display('detail', 'project')
        else:
            self.display('update', 'project')

    def get_basic(self):
        '''
        名    称：获取广告主基本信息
        链    接：/project/advertiser?a=get_basic&id=8667
        状 态：
               200：请求正常,403：用户无访问权限,500：请求失败
        @params out:
                      company：公司全称
                company_short：公司简称
                        brief：公司介绍
                        link ：官网信息
                    category ：行业信息
                        area ：地区信息
            advertiser_status：广告主状态
                   sub_status: 二级状态
        '''
        intId = int(self.I('id'))
        dicAdvertiser_value = self.project_service.advertiser_basic(intId)
        dataDic = {}
        dataDic['detail_info_value'] = dicAdvertiser_value
        self.out(200, '', dataDic)

    def get_contact(self):
        '''
        名    称：获取广告主联系方式
        链    接：/project/advertiser?a=get_contact&id=8667
        状    态：
               200：请求正常,403：用户无访问权限,500：请求失败
        @params out:
                contact_person   ：联系人
                contact_position ：职位
                contact_phone    ：手机
                contact_tel      ：座机
                contact_wechat   ：微信
                contact_qq       ：QQ
                contact_email    ：邮件
                contact_other    : 其它
                last_update_time :最后一更新时间
        '''
        intId = int(self.I('id'))
        dicResp = self.mediaCommonService.get_contact(intId, relation_type=2)
        dataDic = {}
        if dicResp:
            dataDic['detail_info_value'] = dicResp
            self.out(200, '', dataDic)
            return
        self.out(404)

    def get_text(self):
        '''
        名    称：获取广告主需求
        链    接：/project/advertiser?a=get_text&id=8667
        状    态：
               200：请求正常,403：用户无访问权限,500：请求失败
        @params out:
                requirement     ：需求
                progress 		：广告主跟踪
                product_info    ：产品分析
                audience_info   ：受众分析
                remark          ：备注
        '''
        intId = int(self.I('id'))
        dicAdvertiser_value = self.project_service.advertiser_text(intId)
        dataDic = {}
        dataDic['detail_info_value'] = dicAdvertiser_value
        self.out(200, '', dataDic)

    def get_plan(self):
        '''
        名    称：获取投放计划
        链    接：/project/advertiser?a=get_plan&id=8667
        状    态：
               200：请求正常,403：用户无访问权限,500：请求失败
        @params out:
                title       ：投放计划
                brief 		：简介
                time_begin  ：开始投放时间
                time_end    ：结束投放时间
                money       ：预算总额
                status      ：投放状态(1 准备中, 2 进行中, 3 已结束)
        '''
        intId = int(self.I('id'))
        tupPlan = self.project_service.advertiser_plan(intId)
        dataDic = {}
        dataDic['plan'] = tupPlan
        self.out(200, ' ', dataDic)

    def create(self):
        dicArgs = {
            'company': self.I('advertiser_company'),
            'link': self.I('advertiser_link'),
            'remark': self.I('advertiser_remark'),
            'product_info': self.I('advertiser_product_info'),
            'audience_info': self.I('advertiser_audience_info')
        }
        # print dicArgs
        status = self.project_service.create_advertiser(dicArgs)
        self.out(status)

    def update_basic(self):
        sub_status=0
        id = self.I('id')
        if self.I('advertiser_status')=="4" :
            sub_status= self.I('sub_status')
        dicArgs = {
            'company': self.I('advertiser_company'),
            'company_short': self.I('advertiser_company_short'),
            'brief': self.I('advertiser_brief'),
            'link': self.I('advertiser_link'),
            'category': self.I('advertiser_category'),
            'area': self.I('advertiser_area'),
            'advertiser_status': self.I('advertiser_status'),
            'sub_status': sub_status,
        }
        status = self.project_service.update_advertiser(dicArgs, id)
        self.out(status)

    def update_text(self):
        id = self.I('id')
        dicArgs = {
            'company': self.I('advertiser_company'),
            'requirement': self.I('advertiser_requirement'),
            'progress': self.I('advertiser_progress'),
            'remark': self.I('advertiser_remark'),
            'product_info': self.I('advertiser_product_info'),
            'audience_info': self.I('advertiser_audience_info'),
        }
        #print dicArgs
        status = self.project_service.update_advertiser(dicArgs, id)
        self.out(status)

    def delete(self):
        strId = self.I('id')
        self.project_service.delete_advertiser(strId, self.user_id)
        self.redirect('/project/advertiser')

    def get_user(self):
        strId = self.I('id')
        userId = self.user_id
        if strId:
            tupData = self.project_service.getUser(strId, userId)
        else:
            tupData = self.project_service.getUser('', userId)
        if tupData:
            statusCode = 200
        else:
            statusCode = 404
        self.out(statusCode, '', tupData)

    def add_contact(self):
        '''
        名    称：添加广告主联系人
        链    接：/project/advertiser?a=add_contact
        状    态：
               200：请求正常,401：用户信息重复, 403：用户无操做权限,500：请求失败
        @params in:
                id                          ：广告主id
                advertiser_contact_person   ：联系人
                advertiser_contact_position ：职位
                advertiser_contact_phone    ：手机
                advertiser_contact_tel      ：座机
                advertiser_contact_wechat   ：微信
                advertiser_contact_qq       ：QQ
                advertiser_contact_email    : 邮件
                advertiser_contact_other    : 其它
                last_update_time            : 最后一更新时间
        '''
        dicArg = {
            'relation_type': 2,
            'relation_id': self.I('id'),
            'contact_person': self.I('advertiser_contact_person'),
            'contact_position': self.I('advertiser_contact_position'),
            'contact_phone': self.I('advertiser_contact_phone'),
            'contact_qq': self.I('advertiser_contact_qq'),
            'contact_wechat': self.I('advertiser_contact_wechat'),
            'contact_email': self.I('advertiser_contact_email'),
            'contact_tel': self.I('advertiser_contact_tel'),
            'contact_other': self.I('advertiser_contact_other')
        }
        status = self.mediaCommonService.add_contact(dicArg)
        self.out(status)

    def delete_contact(self):
        '''
        名    称：删除广告主联系人
        链    接：/project/advertiser?a=delete_contact
        状    态：
               200：请求正常,403：用户无操做权限,500：请求失败
        @params in:
            contact_id  ： 联系人id
        '''
        dicArgs = {
            "contact_id" : self.I('id'),
            "relation_id" : self.I('relation_id'),
            "relation_type": 2
        }
        status = self.mediaCommonService.del_contact(dicArgs)
        self.out(status)

    def update_contact(self):
        '''
        名    称：修改广告主联系人
        链    接：/project/advertiser?a=update_contact
        状    态：
               200：请求正常,401：用户信息重复, 403：用户无操做权限,500：请求失败
        @params in:
                id                          : 广告主id
                contact_id                  ：联系人id
                advertiser_contact_person   ：联系人
                advertiser_contact_position ：职位
                advertiser_contact_phone    ：手机
                advertiser_contact_tel      ：座机
                advertiser_contact_wechat   ：微信
                advertiser_contact_qq       ：QQ
                advertiser_contact_email    : 邮件
                advertiser_contact_other    : 其它
                last_update_time            : 最后一更新时间
        '''
        dicArg = {
            'id': self.I('contact_id'),
            'contact_person': self.I('advertiser_contact_person'),
            'contact_position': self.I('advertiser_contact_position'),
            'contact_phone': self.I('advertiser_contact_phone'),
            'contact_qq': self.I('advertiser_contact_qq'),
            'contact_wechat': self.I('advertiser_contact_wechat'),
            'contact_email': self.I('advertiser_contact_email'),
            'contact_tel': self.I('advertiser_contact_tel'),
            'contact_other': self.I('advertiser_contact_other')
        }
        status = self.mediaCommonService.update_contact(dicArg)
        self.out(status)

    def update_follower(self):
        '''
        名    称：更新广告主跟踪人
        链    接：/project/advertiser?a=update_follower
        状    态：
               200：请求正常,403：用户无操做权限,500：请求失败
        @params in:
                id                          : 广告主id
                follower                    ：跟踪人id
        '''
        dicArgs = {
            'id':self.I('id'),
            'follower': self.I('follower').split(',')
        }
        status = self.project_service.update_follower(dicArgs)
        self.out(status)

    def get_follower(self):
        '''
        名    称：获取广告主跟踪人
        链    接：/project/advertiser?a=get_follower
        @params in:
                id                          : 广告主id
        '''
        intId = self.I('id')
        if intId:
            userData = []
            if not self.isGod:
                userId = self.user_id
                tupRoleName = self.importService('project_advertiser').getUserRole(userId)
                roleData = [item['name'] for item in tupRoleName]
                if 'market_mg' in roleData:
                    userData = self.project_service.advertiser_follower(intId)
                else:
                    self.out(403)
                    return False
            else:
                userData = self.project_service.advertiser_follower(intId)

            data = {}
            tmpData = {}
            tmpData['follower'] = userData
            data['detail_info_value'] = tmpData
            self.out(self.CODE['SERIVCE_OK'], 'get data success', data)
        else:
            self.out(self.CODE['SERIVCE_PARAM_ERROR'], 'input data error', '')
