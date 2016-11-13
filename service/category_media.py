# -*- coding:utf-8 -*-

import base as base


# 分类Service
class service(base.baseService):
    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        # 数据对象
        self.categoryModel = self.importModel('category_media')

    def commonUse(self):
        """ 常用分类
        """

        tupData = self.categoryModel.findMany({
            'order': 'sort asc'
        })
        # if tupData:
        #     for item in tupData:
        #         pass

        return tupData

    def getCategory(self, strCategoryId):
        """ 通过分类ID获取分类信息
        """

        # 去重
        lisCategoryId = []

        lisCategoryIdTemp = strCategoryId.split(',')
        if lisCategoryIdTemp:
            for item in lisCategoryIdTemp:
                if item not in lisCategoryId:
                    lisCategoryId.append(item)

        # 获取分类信息
        tupCategory = self.categoryModel.findMany({
            'condition': 'id in (%s)' % ','.join(lisCategoryId),
        })

        return tupCategory

    def get_one_category(self, strCategoryId):
        """ get one category info by category's id

        @params strCategoryId string category's id
        """

        if not strCategoryId:
            return {}

        dic_category = self.categoryModel.findOne({
            'condition': 'id = "%s"' % strCategoryId
        })
        if dic_category:
            return dic_category
        return {}

    def getAll(self):
        """ 获取所有分类
        """

        # lisCategory = []
        # dicCategory = {}

        tupData = self.categoryModel.findMany({
            'order': 'sort asc'
        })
        return tupData

        # if tupData:
        #    # 遍历所有分类，按父级重组
        #    for item in tupData:
        #        if item['parent_id'] == 0:
        #            lisCategory.append(item)
        #        else:
        #            if item['parent_id'] not in dicCategory.keys():
        #                dicCategory[item['parent_id']] = []
        #
        #            dicCategory[item['parent_id']].append(item)
        #
        # return {'parent': lisCategory, 'child': dicCategory}

        # def getCategoryByDemandId(self, strDemandId):
        #     """ 通过demand_id获取分类信息
        #
        #     @params strDemandId string demand_id，多个用,号拼接
        #     """
        #
        #     tupCategory = self.categoryModel.findMany({
        #         'condition': ''
        #     })
