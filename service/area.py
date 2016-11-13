# -*- coding:utf-8 -*-

import base as base


class service(base.baseService):
    """ 城市Service
    """

    def __init__(self, model, param):

        base.baseService.__init__(self, model, param)

        self.areaModel = self.importModel('area')

    def get_list(self, strParentId):
        """ 获取城市列表

        @params strParentId string 父ID
        """

        tupData = self.areaModel.findMany({
            'condition': 'parent = "%s"' % strParentId
        })

        return tupData

    def get_area_by_id(self, strId):
        """ 通过ID获取城市信息

        @params strId string 城市ID，多个用,事分割
        """

        tupData = self.areaModel.findMany({
            'condition': 'id in (%s)' % strId,
            'order': 'level asc'
        })

        return tupData

    def get_area_name(self, strId):
        """ 通过ID获取城市信息

        @params strId string 城市ID，多个用,事分割
        """

        tupData = self.areaModel.findMany({
            'fields': ['name'],
            'condition': 'id in (%s)' % strId,
            'order': 'level asc'
        })

        return tupData

    def get_area_name_one(self, strId):
        """ 通过ID获取城市信息

        @params strId string 城市ID
        """

        dicName = self.areaModel.findOne({
            'fields': ['name'],
            'condition': 'id in (%s)' % strId,
            'order': 'level asc'
        })
        if dicName:
            return dicName['name']
        return ""

    def get_area(self, province, city=None, county=None):
        # 通过参数查询地区名称
        if province == 0:
            area = '全国性'
        else:
            area = ''
            # get area name
            areaService = self.importService('area')
            lisAreaId = [str(province)]
            if city:
                lisAreaId.append(str(city))

            if county:
                lisAreaId.append(str(county))

            strAreaId = ','.join(lisAreaId)
            tupArea = areaService.get_area_by_id(strAreaId)
            if tupArea:
                for item in tupArea:
                    area = area + item['name']
        return area
