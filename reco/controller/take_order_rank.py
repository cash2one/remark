# -*- coding:utf-8 -*-

import base
import json

# 需求
class take_order_rank(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.demand_service      = self.importService('demand')
        self.media_service       = self.importService('media')
        self.media_tag_service  = self.importService('media_tag')

    # 列表
    def index(self):
        strDemandId = self.I('id')
        
        tupDemandCategory   = self.demand_service.demandCategory(strDemandId)
        tupDemandTag        = self.demand_service.demandTag(strDemandId)
        
        tupMedia = self.demand_service.demand_take_order(strDemandId)
        #print tupMedia
        lisMedia = []
        if tupMedia:
            for media in tupMedia:
                score = 0.0
                for demand_cate in tupDemandCategory:
                    if media['media_category']['cate_id'] == demand_cate['cate_id']:
                        score = 1.0
                        break
                
                same_tag_num = 0
                for media_tag in media['media_tag']:
                    for demand_tag in tupDemandTag:
                        if media_tag['tag_id'] == demand_tag['tag_id']:
                            same_tag_num = same_tag_num + 1
                sum_tag_num = len(media['media_tag']) + len(tupDemandTag) - same_tag_num
            
                score = score + same_tag_num * 1.0 / sum_tag_num
                lisMedia.append([score, media])
            
        lisMedia.sort(key=lambda x:x[0], reverse=True) 

        jsonresult = json.dumps(lisMedia)
        callback = '%s(%s)' % (self.I('callback'), jsonresult)  # jsonresult就是客户端中接收到的res
        self.write(callback)
        return
        
        # 接单自媒体排序
        #for term in tupMedia:
        #    tmp = []
        #    dic_oa = {}
        #    tup_oacate = self.media_tagModel.findMany({
        #        'fields:': ['media_id'],
        #        'condition': 'tag_id="%s"' % term,
        #    })
        #    dic_oa['oa_id'] = term;
        #    for term_cate in tup_oacate:
        #        cate_temp = term_cate.get('tag_id')
        #        if cate_temp in demand_tag:
        #            tmp.append(cate_temp)
        #
        #    dic_oa['cate_num'] = len(tmp)
        #    sort_oa.append(dic_oa)
        #sort_oa.sort(reverse=True)
        ##print sort_oa
        ##################################
        ### 同一个用户放在一起
        #user_list = []  # user exist
        #while len(sort_oa) != 0:
        #    sort_oa_info = self.mediaService.detail(sort_oa[0].get('oa_id'))
        #    user_info = self.mediaService.find_user(sort_oa[0].get('oa_id'))
        #    if user_info==404:
        #        del sort_oa[0]
        #        #print 404
        #        user_info=self.mediaService.find_user(sort_oa[0].get('oa_id'))
        #    else:
        #        user_info_list = list(user_info)
        #        if user_info_list[0].get('user_id') not in user_list:
        #           # print 1
        #            user_list.append(user_info_list[0].get('user_id'))
        #            user_info_list.append(sort_oa_info)
        #            sort_user.append(user_info_list)
        #            del sort_oa[0]
        #        else:
        #            #print 2
        #            for repeat in sort_user:
        #                if repeat[0].get('user_id') == user_info_list[0].get('user_id'):
        #                   # print 3
        #                    repeat.append(sort_oa_info)
        #                    del sort_oa[0]
        #
        ##print 4
        #sortjson = json.dumps(sort_user)
        #result=[]
        #result.append(sort_user)
        ##result.append(sort_reco)
        #if result:
        #    statusCode = 200
        #else:
        #    statusCode = 404
        #c = self.I('callback')
        #jsonresult = json.dumps(sort_user)
        ##print sort_reco
        ##print jsonresult
        #callback = '%s(%s)' % (c, jsonresult)  # jsonresult就是客户端中接收到的res
        #self.write(callback)
        ##print callback

