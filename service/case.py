# -*- coding:utf8 -*-

import base


class service(base.baseService):
    """ 案例Service
    """

    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        #self.areaModel = self.importModel('area')

    def get_demand_id(self,page_num,each_page_num):
        tupdate = self.importModel('demand').findPaginateAs('demand as d',{
                'fields' : ['d.id'],
                'condition' : 'd.status = 4',
                'page': [page_num,each_page_num],
                'order': 'd.time_end desc'
                })
        #print lis_demand
        lis_demand = list(tupdate[0])
        all_num = tupdate[1]
        if lis_demand :
            for i,item in enumerate(lis_demand):
                lis_demand[i] = item['id']
                #print item
        return  lis_demand,all_num

    def get_media_demand_id(self,media_id,page_num,each_page_num):
        tupdata = self.importModel('demand_order').findMany({
            'fields' : ['demand_id'],
            'condition' : 'status = 4 and media_id = {mid}'.format(mid = media_id),
            'page': [page_num,each_page_num],
            'order': 'create_time desc',
        })
        lis_id = []
        if tupdata:
            for i,item in enumerate(tupdata):
                lis_id.append(item['demand_id'])
        #print lis_id
        return lis_id




    def get_all_read(self,did):
        ##TODO
        return

    def get_amount(self,did):
        # 成交金额,成交自媒体数
        tup_data = self.importModel('demand_order').findMany({
                'fields' : ['sum(price) as total','count(*) as num'],
                'condition' : 'demand_id = {demand_id}'.format(demand_id = did)
                })
        if tup_data[0].has_key('total'):
            tup_data[0]['total'] = int(tup_data[0]['total'])
        #print tup_data
        return tup_data

    def get_media_id(self,did):
        lis_media = list(self.importModel('demand_order').findMany({
                'fields' : ['media_id'],
                'condition' : 'demand_id = {demand_id}'.format(demand_id = did)
                }))
        if lis_media :
            for i,item in enumerate(lis_media):
                lis_media[i] = item['media_id']
        return lis_media
    def get_demand_info(self,did):
        tup_data = self.importModel('demand').findMany({
                'fields' : ['id','title','form'],
                'condition' : 'id = {demand_id}'.format(demand_id = did)
                })
        demand_info = {}
        tup_take_order_num = self.importModel('demand_take_order').findMany({
            'fields':['count(*) as take_order_num'],
            'condition' : 'demand_id = {demand_id}'.format(demand_id = did)
        })
        if tup_take_order_num:
            demand_info['take_order_num'] = tup_take_order_num[0]['take_order_num']
        if tup_data:
            dic_demand_info = self.importService('demand').detail(str(did))
            #print dic_demand_info
            form_name = self.importModel('demand_form').findOne({
                    'condition': 'id = "%s"' % tup_data[0]['form']
                })

            demand_info['form_name'] = ""
            if form_name:
                demand_info['form_name'] = form_name['name']
            dic_amount = self.get_amount(tup_data[0]['id'])
            demand_info['gender'] = dic_demand_info['audience_gender']
            demand_info['category'] = dic_demand_info['category']
            demand_info['tag'] = dic_demand_info['tag']
            demand_info['area'] = dic_demand_info['area']
            demand_info['category'] = dic_demand_info['category']
            demand_info['original'] = dic_demand_info['original']
            demand_info['view'] = dic_demand_info['view']
            demand_info['num'] = dic_demand_info['num']#自媒体数要求
            demand_info['audience_num'] = dic_demand_info['audience_num']
            demand_info['title'] = tup_data[0]['title']
            demand_info['id'] = tup_data[0]['id']
            demand_info['media_num'] = dic_amount[0]['num']
            demand_info['total_price'] = dic_amount[0]['total']
            all_media_id = self.get_media_id(did)
            all_media_info = []
            if all_media_id :
                for mid in all_media_id :
                    all_media_info.append(self.get_media_info(mid,did))
            demand_info['media_info'] = all_media_info

        return  demand_info
    def get_media_trade(self,mid,did):
        order_info = self.importModel('demand_order').findOne({
            'fields':['media_price_id','price'],
            'condition': 'media_id = {media_id} and demand_id = {demand_id} '.format(media_id = mid,demand_id = did)
        })
        #print did
        #print order_info
        if  order_info.has_key('media_price_id'):
            mprice_id = order_info['media_price_id']
            lis_data = self.importService('media').media_attr_value_info(mprice_id)
        else:
            lis_data = []
        if  order_info.has_key('price'):
            real_price = order_info['price']
        else:
            real_price = ''

        price = {}
        if lis_data:
            price = lis_data[0]
            price['attr_value_info'] = price['attr_value_info'].values()[0]
        feedback_info = self.importModel('demand_wechat_feedback').findOne({
            'fields':['url','picture_1','picture_2','picture_3'],
            'condition': 'media_id = {media_id} and demand_id = {demand_id} '.format(media_id = mid,demand_id = did)
        })
        # if not feedback_info :
        #     feedback_info = {'url':''}
        if feedback_info.has_key('picture_1'):
            feedback_info['picture_1'] = self.getAvatarUrl(feedback_info['picture_1'], 'avatar')
        if feedback_info.has_key('picture_2'):
            feedback_info['picture_2'] = self.getAvatarUrl(feedback_info['picture_2'], 'avatar')
        if feedback_info.has_key('picture_3'):
            feedback_info['picture_3'] = self.getAvatarUrl(feedback_info['picture_3'], 'avatar')
        #print feedback_info
        trade_info = {}
        if price:
            trade_info['price'] = price
        trade_info['real_price'] = real_price
        trade_info['feedback'] = feedback_info
        #print trade_info
        return  trade_info


    def get_media_info(self,mid,did):
        dic_media_info  = self.importService('media').media_basic(mid)
        dic_media_detail = self.importService('media').detail(mid)
        trade_info = self.get_media_trade(mid,did)
        media_info={}
        media_info['id'] = mid
        if dic_media_info.has_key('avatar') :
            media_info['avatar'] = dic_media_info['avatar']
        if dic_media_info.has_key('name') :
            media_info['name'] = dic_media_info['name']
        for key in dic_media_detail:
            media_info[key] = dic_media_detail[key]
        media_info['trade'] = trade_info
        #print media_info
        return media_info

    def case_view(self,page_num,each_page_num):

        all_did = self.get_demand_id(page_num,each_page_num)
        case_list = []
        #print all_did
        if all_did[0]:
            for item in all_did[0]:
                # if item == 2280 :
                #     print item
                #     print self.get_demand_info(item)
                case_list.append(self.get_demand_info(item))

        for item in case_list:
            if len(item['media_info']) > 7 :
                item['media_info'] = item['media_info'][0:7]
        return case_list,all_did[1]

    def case_detail(self,did):
        #print did
        data = self.get_demand_info(did)
        import pprint
        #pprint.pprint(data)
        return data

    def media_case_index(self,mid,page_num,each_page_num):
        lis_id = self.get_media_demand_id(mid,page_num,each_page_num)
        #print lis_id
        lis_data = []
        def map_append(x):
            lis_data.append(self.get_media_info(mid,x))

        map(map_append,lis_id)
        return lis_data

    def media_case_detail(self,mid,page_num,each_page_num):
        media_case = self.media_case_index(mid,page_num,each_page_num)
        tupdate = self.importModel('demand_order').findMany({
            'fields':['count(*) as all_num','sum(price) as amount'],
            'condition': 'media_id = {media_id} and status =4 '.format(media_id = mid)
        })
        return media_case ,tupdate[0]

