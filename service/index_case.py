# -*- coding:utf-8 -*-

import base


class service(base.baseService):
    def __init__(self, model, param):
        base.baseService.__init__(self, model, param)
        # 首页自媒体
        self.yidao_caseModel = self.importModel('yidao_case')

    def query(self, intPage=1, intPageDataNum=10):
        """
        :func: 友链数据
        :param intPage: 页码
        :param intPageDataNum: 单页数据量
        """
        intDataNumStart = (intPage - 1) * intPageDataNum
        tupData, intRows = self.yidao_caseModel.findPaginate({
            'page': [intPage, intPageDataNum],
            'order': 'id asc'
        })
        # 数据整合及格式化
        # print tupData
        lisIndexInfo = []
        for idx, i in enumerate(tupData):
            i['idx'] = intDataNumStart + idx + 1
            i['id'] = i.get('id')
            i['advertiser'] = i.get('advertiser')
            i['demand_info'] = i.get('demand_info')
            i['media_name1'] = i.get('media_name1')
            i['media_name2'] = i.get('media_name2')
            i['market_effect'] = i.get('market_effect')
            i['create_time'] = self.formatTime(i.get('create_time'), '%Y-%m-%d')
            lisIndexInfo.append(i)
            # print lisIndexInfo
        return lisIndexInfo, intRows

    def Create(self, dicArgs):
        """
        :func: 新增友链
        :param dicArgs: 友链参数
        """
        # print dicArgs
        if 'case_advertiser' in dicArgs and 'case_demand_info' in dicArgs and \
                'case_media_name_1' in dicArgs and 'case_market_effect' in dicArgs:
            strAdvertiser = dicArgs['case_advertiser'][0]
            strDemand_info = dicArgs['case_demand_info'][0]
            strMedia_name_1 = dicArgs['case_media_name_1'][0]
            strMedia_name_2 = dicArgs['case_media_name_2'][0]
            strMarket_effect = dicArgs['case_market_effect'][0]
            # print strContent,strTitle,strType
            # desc 为sql 关键字 作为字段名需要``标识
            self.yidao_caseModel.insert({
                'key': 'advertiser, demand_info,media_name_1, media_name_2, market_effect,create_time',
                'val': '\'{advertiser}\', \'{demand_info}\', '
                       '\'{media_name_1}\',\'{media_name_2}\',\'{market_effect}\', {time}'.format(
                        advertiser=strAdvertiser, demand_info=strDemand_info, media_name_1=strMedia_name_1,
                        media_name_2=strMedia_name_2, market_effect=strMarket_effect, time=int(self.time.time())
                        )
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def update(self, dicArgs):
        """
        :func: 编辑友链
        :param dicArgs: 友链参数
        """

        if 'case_advertiser' in dicArgs and 'case_demand_info' in dicArgs and \
                'case_media_name_1' in dicArgs and 'case_market_effect' in dicArgs:
            strId = dicArgs['case_id'][0]
            strAdvertiser = dicArgs['case_advertiser'][0]
            strDemand_info = dicArgs['case_demand_info'][0]
            strMedia_name_1 = dicArgs['case_media_name_1'][0]
            strMedia_name_2 = dicArgs['case_media_name_2'][0]
            strMarket_effect = dicArgs['case_market_effect'][0]
            lisFields = ['advertiser = \'{advertiser}\''.format(advertiser=strAdvertiser),
                         'demand_info = \'{demand_info}\''.format(demand_info=strDemand_info),
                         # desc 为sql 关键字 作为字段名需要``标识
                         'media_name_1 = \'{media_name_1}\''.format(media_name_1=strMedia_name_1),
                         'media_name_2 = \'{media_name_2}\''.format(media_name_2=strMedia_name_2),
                         'market_effect = \'{market_effect}\''.format(market_effect=strMarket_effect)]
            self.yidao_caseModel.update({
                'fields': lisFields,
                'condition': 'id = {id}'.format(id=strId)
            })
            if self.model.db.status != 200:
                return {'statusCode': 601}
            return {'statusCode': 200}

    def delete(self, intId):
        """
        :func: 删除友链
        :param intId: 友链ID
        """
        self.yidao_caseModel.delete({
            'condition': 'id = {id}'.format(id=intId)
        })
        if self.model.db.status != 200:
            return {'statusCode': 601}
        return {'statusCode': 200}
