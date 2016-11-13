# -*- coding:utf-8 -*-

import base
import json

class similary_media(base.base):
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

        self.media_service      = self.importService('media')

    # 列表
    def index(self):
        str_media_id    = self.I('id')
        media_tag = self.media_service.media_tag(str_media_id)

        ### 相似自媒体
        tup_similry_media  = self.media_service.similry_media(str_media_id)

        lisMedia = []
        for media in tup_similry_media:
            ## 过滤自己
            if str_media_id == str(media['id']):
                continue

            score = 0.0

            media['tag'] = self.media_service.media_tag(media['id'])
            if len(media['tag']) == 0:
                continue

            same_tag_num = 0
            for tag_a in media_tag:
                for tag_b in media['tag']:
                    if tag_a['tag_id'] == tag_b['tag_id']:
                        same_tag_num = same_tag_num + 1
            if same_tag_num == 0:
                continue

            sum_tag_num = len(media_tag) + len(media['tag']) - same_tag_num
            score = score + same_tag_num * 1.0 / sum_tag_num
            media_detail = self.media_service.media_basic(str(media['id']))

            lisMedia.append([score, media_detail])

        if len(lisMedia) > 0:
            lisMedia.sort(key=lambda x:x[0], reverse=True)
        else:
            idxMediaService             = self.importService('index_media')
            for media in idxMediaService.query():
                media['id'] = media['media_id']

                ## 过滤自己
                if str_media_id == str(media['id']):
                    continue

                lisMedia.append([1.0, media])
        jsonresult = json.dumps(lisMedia[0:4])
        callback = '%s(%s)' % (self.I('callback'), jsonresult)  # jsonresult就是客户端中接收到的res
        self.write(callback)
        return 
        # 推荐
        #alloa = self.media_tag_service.get_media_tag_all()
        #alloa_list = list(alloa)
        ##print alloa_list
        #sort_media_all = []
        #sort_result = []
        #sort_result3 = []
        #sort_result2 = []
        #sort_result1 = []
        ##print len(same_cate_list)
        #cate_num =0 #相同行业不足4时，返回相同行业数据的个数
        #notinlist=[]
        #notinlist.append(long(strMediaId))
        #print notinlist
        #if len(same_cate_list)<4:
        #    cate_num = len(same_cate_list)
        #    for item in same_cate_list:
        #        dic_media_id ={}
        #        dic_media_id['media_id'] = item
        #        sort_result.append(dic_media_id)
        #        notinlist.append(item)
        #
        #
        #    #print same_cate_list
        #    #print sort_result
        #    for item in alloa_list:
        #        if (item.get('tag_id') in media_tag)and(item.get('media_id')not in notinlist):
        #            sort_media_all.append(item.get('media_id'))
        #        #print sort_media_all
        #else:
        #    for item in alloa_list:
        #        if (item.get('tag_id') in media_tag)and(item.get('media_id')in same_cate_list):
        #            sort_media_all.append(item.get('media_id'))
        #sort_media_all.sort()
        #print  sort_media_all
        #passnum=0
        #for n, item in enumerate(sort_media_all):
        #    #print sort_media_all
        #    #print n
        #    #print item
        #    num = sort_media_all.count(item)
        #    #print num
        #    if n>=passnum:
        #        #print "large"
        #        dic_media_sort = {}
        #        dic_media_sort['media_id'] = item
        #        dic_media_sort['num'] = num
        #        if num == 3:
        #            sort_result3.append(dic_media_sort)
        #        elif num == 2:
        #            sort_result2.append(dic_media_sort)
        #        else:
        #            sort_result1.append(dic_media_sort)
        #        passnum=n+num
        #    #else:
        #        #print "small"
        #    #print sort_media_all
        #    #del sort_media_all[n:n + num]
        #    #print sort_result2
        #    #print sort_result1
        #    #print  passnum
        #i3 = len(sort_result3)
        #i2 = len(sort_result2)
        #i1 = len(sort_result1)
        #print i1,i2,i3
        #if i3+i2+i1<4-cate_num:
        #    tup_media = self.importModel('media').findMany({
        #        'fields':['id'],
        #    })
        #    all_media = random.sample(tup_media,4)
        #    print all_media
        #    sort_result_info=[]
        #    #print sort_result
        #    for item in all_media:
        #        sort_result_info.append(self.media_service.media_info(item.get('id')))
        #
        #    c = self.I('callback')
        #    print 1111
        #    print sort_result_info
        #    jsonresult = json.dumps(sort_result_info)
        #
        #    #print jsonresult
        #    callback = '%s(%s)' % (c, jsonresult)  # jsonresult就是客户端中接收到的res
        #    self.write(callback)
        #        #print "not enough"
        #    return
        #
        #if i3 >= (4-cate_num):
        #    sort_result.extend(sort_result3[0:4-cate_num])
        #elif i3 + i2 >= 4-cate_num:
        #    sort_result.extend(sort_result3)
        #    n = 0
        #    #print sort_result2
        #    while len(sort_result) < 4:
        #
        #        sort_result.append(sort_result2[n])
        #        n += 1
        #else:
        #    sort_result.extend(sort_result3)
        #    sort_result.extend(sort_result2)
        #    n = 0
        #    while len(sort_result) < 4:
        #        sort_result.append(sort_result1[n])
        #        n += 1
        #sort_result_info=[]
        ##print sort_result
        #for item in sort_result:
        #    sort_result_info.append(self.media_service.media_info(item.get('media_id')))

        
        ###############################################################################
        callback = self.I('callback')
        jsonresult = json.dumps(sort_result_info)

        callback = '%s(%s)' % (c, jsonresult)  # jsonresult就是客户端中接收到的res
        self.write(callback)
