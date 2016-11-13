# -*- coding:utf-8 -*-

import base as base

class Media(base.base):
    """ 自媒体
    """

    def initialize(self):
        config = {'isDataBase' : True, 'isMongoDB': True}
        base.base.initialize(self, config)

    def index(self):
        # 获取参数
        intPage = int(self.I('page', '1'))
        dicSearchCondition = {
            'page'              : intPage,
            'category'          : self.I('category', ''),
            'tag'               : self.I('tag', ''),
            'value_level'       : self.I('value_level', ''),
            'audience_gender'   : self.I('audience_gender', ''),
            'identify'          : self.I('identify', ''),
            'original'          : self.I('original', ''),
            'audience_province' : self.I('audience_province', ''),
            'audience_city'     : self.I('audience_city', ''),
            'audience_county'   : self.I('audience_county', ''),
            'query'             : self.I('query', '')
        }
    
        listSearchCondition = []
        listSearchCondition.append("a=index")
        for key, value in dicSearchCondition.items():
            if key <> 'page' and value <> '':
                listSearchCondition.append("%s=%s" % (key, value))
    
        # 自媒体列表
        mediaService = self.importService('media')
        dicMediaList = mediaService.list(dicSearchCondition)
        self.dicViewData['list']            = dicMediaList['list']
        self.dicViewData['category']        = dicMediaList['category']
        self.dicViewData['tag']             = dicMediaList['tag']
        self.dicViewData['value_level']     = mediaService.get_all_value_level()
        self.dicViewData['audience_gender'] = mediaService.get_all_audience_gender()
        self.dicViewData['identify']        = mediaService.get_all_identify()
        self.dicViewData['original']        = mediaService.get_all_original()
        self.dicViewData['search_condition']= dicSearchCondition
        self.dicViewData['page'] = self.page(intPage, 10, dicMediaList['count'], '/media?%s' % ('&'.join(listSearchCondition)))
        
        self.display('index')

    def view(self):
        """ 自媒体详情
        """

        # 请求参数
        dicRequestData = {
            'oa_id': self.I('id')
        }
        if not self.current_user['user_id']:
            login=0
        else:
            login=1

        # 如果没有ID，跳转404
        if not dicRequestData['oa_id']:
            self.redirect('/404')
            return

        # get media
        mediaService = self.importService('media')
        tupprice = mediaService.media_price(dicRequestData['oa_id'])
        dicMedia = mediaService.detail(dicRequestData['oa_id'])
        strBiz = mediaService.get_biz(dicRequestData['oa_id'])
        lisArticle = self.importService('media_article').list(strBiz)
        media_case = self.importService('case').media_case_detail(dicRequestData['oa_id'],1,3)
        # print media_case
        dicMedia['price_info']=tupprice
        if not dicMedia:
            self.redirect('/404')
            return
        self.dicViewData['login'] = login
        self.dicViewData['media'] = dicMedia
        self.dicViewData['media_case'] = ()
        self.dicViewData['media_article'] = lisArticle
        self.dicViewData['RECO_HOST'] = self.dicConfig['RECO_HOST']

        self.display('view')

    def media_case_create(self):
        """ create anli

        step:
        1. check user logined
        2. check request params
        3. check owner
        """

        if not self.current_user['user_id']:
            self.out(604)
            return

        strOfficialId = self.I('official_id')
        strUrl = self.I('url')
        dicRequestData = {
            'user_id': self.current_user['user_id'],
            'oa_id': strOfficialId,
            'url': strUrl
        }

        intStatus = 0 #self.officialService.anli_create(dicRequestData)
        self.out(intStatus)

    def case(self):
        self.display('case');

    def area(self):
        """ 读取城市信息
        """

        str_type = self.I('t')
        str_parent_id = self.I('parent_id')

        if str_type == 'province':
            parent_id = 0
        else:
            parent_id = str_parent_id

        # 读取所有省份信息
        cityService = self.importService('city')
        tupData = cityService.get_list(parent_id)
        if tupData:
            if str_type == 'province':
                # 根据首字母组合数据
                dicProvince = {}
                for item in tupData:
                    if item['f'] not in dicProvince:
                        dicProvince[item['f']] = []

                    dicProvince[item['f']].append({
                        'id': item['id'],
                        'name': item['name']
                    })

                self.out(200, '', dicProvince)
            else:
                self.out(200, '', tupData)
        else:
            self.out(601, '', {})

    def get_read_num(self):
        strMediaId = self.I('media_id')
        strBiz = self.importService('media').get_biz(strMediaId)
        dicResp = self.importService('media_article').get_read_num(strBiz)
        self.out(dicResp['status'], '', dicResp['data'])


