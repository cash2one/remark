# -*- coding:utf-8 -*-

import base as base


# 博客Service
class service(base.baseService):
    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        # 数据对象
        self.blogModel = self.importModel('blog')

    def lists(self):

        tupBlog = self.blogModel.findMany()
        listBlog = []
        if tupBlog:
            for item in tupBlog:
                # 处理图片
                item['pic'] = '%s%s%s' % (self.dicConfig['PIC']['HOST'], item['thumb'], self.dicConfig['PIC']['SUFFIX'])
                # 处理时间
                objCreateTime = item['create_at'].timetuple()
                item['create_at'] = '%s.%s.%s' % (objCreateTime.tm_year, objCreateTime.tm_mon, objCreateTime.tm_mday)
                listBlog.append(item)
        return listBlog
