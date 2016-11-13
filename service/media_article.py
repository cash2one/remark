# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, _model, param):

        base.baseService.__init__(self, _model, param)

        self.mediaArticleModel = self.importModel('media_article')

    def list(self, strBiz):
        result = self.mediaArticleModel.findMany({
            'condition': {'biz': strBiz},
            'order': 'post_day desc'
        })
        return result[:5]

    def get_read_num(self, strBiz):
        today = self.datetime.date.today()
        timedelta = self.datetime.timedelta
        dates = []
        read_nums = []
        for i in range(7, 0, -1):
            day = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            res = self.mediaArticleModel.findOne({
                'condition': {'biz': strBiz, 'post_day': day, 'article_idx': '1'}
            })
            read_num = res.get('readnum_pm', 0)
            read_nums.append(read_num)
            dates.append(day)
        if not read_nums:
            return {'status': 404, 'data': {}}
        return {'status': 200, 'data': {'date': dates, 'read_num': read_nums}}
