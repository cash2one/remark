# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 首页自媒体
        self.index_notice_model = self.importModel('index_notice')

    def query(self, intPage=1, intPageDataNum=2):
        """
        :func: 友链数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        """
        # intDataNumStart = (intPage - 1) * intPageDataNum
        tupData, intRows = self.index_notice_model.findPaginate({
            'page': [intPage, intPageDataNum],
            'order': 'last_update_time desc'
        })
        
        # 数据整合及格式化
        for k, item in enumerate(tupData):
            item['last_update_time'] = self.formatTime(item.get('last_update_time'), '%Y-%m-%d')
        return tupData

    def create(self, str_type, str_title, str_link):
        """
        :func: 新增公告
        """

        self.index_notice_model.insert({
                'key': 'type, title, link, last_update_time',
                'val': '"%s", "%s", "%s", %d' % (str_type, str_title, str_link, int(self.time.time()))
            })
        if self.model.db.status != 200:
            self.status = 601

    def update(self, str_id, str_type, str_title, str_link):
        """
        :func: 编辑公告
        """
        lis_field = ['type = "%s"' % str_type,
                     'title = "%s"' % str_title,
                     'link = "%s"' % str_link,
                     'last_update_time = %d' % int(self.time.time())]

        self.index_notice_model.update({
                'fields': lis_field,
                'condition': 'id = %s' % str_id
            })
        if self.model.db.status != 200:
            self.status = 601

    def delete(self, str_id):
        """
        :func: 删除公告
        """
        self.index_notice_model.delete({
                'condition': 'id = %s' % str_id
            })
        if self.model.db.status != 200:
            self.status = 601
