# -*- coding:utf-8 -*-

import base
import json

class media_reco(base.base):


    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        # 引用Service
        self.demand_service = self.importService('demand')
        self.media_service = self.importService('media')


    # 列表

    def index(self):

        str_demand_id    = self.I('id')
        tup_demand_category = self.demand_service.demandCategory(str_demand_id)
        tup_demand_tag = self.demand_service.demandTag(str_demand_id)

        ### 相似自媒体
        lisMedia = []

        tup_similry_media  = self.media_service.media_reco(tup_demand_category)

        for media in tup_similry_media:
            score = 0.0

            media['tag'] = self.media_service.media_tag(media['id'])
            if len(media['tag']) == 0:
                continue

            same_tag_num = 0
            for tag_a in tup_demand_tag:
                for tag_b in media['tag']:
                    if tag_a['tag_id'] == tag_b['tag_id']:
                        same_tag_num = same_tag_num + 1
            if same_tag_num == 0:
                continue

            sum_tag_num = len(tup_demand_tag) + len(media['tag']) - same_tag_num
            score = score + same_tag_num * 1.0 / sum_tag_num
            media_detail = self.media_service.media_basic(str(media['id']))

            lisMedia.append([score, media_detail])

        if len(lisMedia) > 0:
            lisMedia.sort(key=lambda x:x[0], reverse=True)
        else:
            idxMediaService             = self.importService('index_media')
            for media in idxMediaService.query():
                media['id'] = media['media_id']

                lisMedia.append([1.0, media])

        jsonresult = json.dumps(lisMedia[0:4])
        callback = '%s(%s)' % (self.I('callback'), jsonresult)  # jsonresult就是客户端中接收到的res
        self.write(callback)
        return


        # n=0
        # strDemandId = self.I('demand_id')
        #
        # demand_tag = []
        # oa_term=self.demandService.demandTag(strDemandId)
        # for term in oa_term:
        #     demand_tag.append(term.get('tag_id'))
        # tupOAlist =self.demandService.demand_media(strDemandId)
        # tunOAidlist=[]
        # for term in tupOAlist:
        #     tunOAidlist.append(term.get('media_id'))
        #
        # sort_user = []
        # # 推荐
        # alloa = self.media_tagModel.findMany({
        #     'fields': ['media_id', 'tag_id'],
        #     # 'condition': 'id< 1000'
        # })
        # alloa_list = list(alloa)
        # sort_media_all = []
        # sort_result = []
        # sort_result3 = []
        # sort_result2 = []
        # sort_result1 = []
        # for item in alloa_list:
        #     if item.get('tag_id') in demand_tag:
        #         sort_media_all.append(item.get('media_id'))
        # sort_media_all.sort()
        # for n, item in enumerate(sort_media_all):
        #     num = sort_media_all.count(item)
        #     dic_media_sort = {}
        #     dic_media_sort['media_id'] = item
        #     dic_media_sort['num'] = num
        #     if num == 3:
        #         sort_result3.append(dic_media_sort)
        #     elif num == 2:
        #         sort_result2.append(dic_media_sort)
        #     else:
        #         sort_result1.append(dic_media_sort)
        #     del sort_media_all[n:n + num]
        # i3 = len(sort_result3)
        # i2 = len(sort_result2)
        # i1 = len(sort_result1)
        #
        # if i3 >= 4:
        #     sort_result = sort_result3[0:4]
        # elif i3 + i2 >= 4:
        #     sort_result = sort_result3
        #     n = 0
        #     while len(sort_result) < 4:
        #         sort_result.append(sort_result2[n])
        #         n += 1
        # else:
        #     sort_result = sort_result3
        #     sort_result.extend(sort_result2)
        #     n = 0
        #     while len(sort_result) < 4:
        #         sort_result.append(sort_result1[n])
        #         n += 1
        # user_reco = []
        # sort_reco = []
        #
        # sort_result_info = self.mediaService.media_info(sort_result[0].get('media_id'))
        # #while len(sort_result) != 0:
        # #    user_info_reco = self.mediaService.find_user(sort_result[0].get('media_id'))
        # #    sort_result_info = self.mediaService.media_info(sort_result[0].get('media_id'))
        # #    if isinstance(user_info_reco, list) and user_info_reco[0].get('user_id') not in user_reco:
        # #       # print 1
        # #        user_reco.append(user_info_reco[0].get('user_id'))
        # #        user_reco_list.append(sort_result_info)
        # #        sort_reco.append(user_reco_list)
        # #    else:
        # #       # print 2
        # #        for repeat in sort_reco:
        # #            if repeat[0].get('user_id') == user_reco_list[0].get('user_id'):
        # #                #print 3
        # #                repeat.append(sort_result_info)
        # #    del sort_result[0]
        # list_abc = []
        # for item in sort_result:
        #     sort_result_info = self.mediaService.media_info(sort_result[0].get('media_id'))
        #     list_abc.append(sort_result_info);
        #
        # #result = []
        # #result.append(sort_user)
        # #result.append(sort_reco)
        # #if result:
        # #    statusCode = 200
        # #else:
        # #    statusCode = 404
        # c = self.I('callback')
        # jsonresult = json.dumps(list_abc)
        # callback = '%s(%s)' % (c, jsonresult)  # jsonresult就是客户端中接收到的res
        # self.write(callback)
