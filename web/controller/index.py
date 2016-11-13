# -*- coding:utf-8 -*-

from base import base

# 首页
class index(base):

    def initialize(self):
        config = {'isDataBase' : True}
        base.initialize(self, config)

    # 首页面板数据
    def index(self):
        # 引入service
        idxBannerService            = self.importService('index_banner')
        idx_notice_ervice           = self.importService('index_notice')
        idxDemandService            = self.importService('index_demand')
        idxMediaService             = self.importService('index_media')
        idxMediaStarService         = self.importService('index_media_star')
        idxMediaRevenueTopService   = self.importService('index_media_revenue_top')
        yidaoCaseService            = self.importService('index_case')
        friendlinkService           = self.importService('friendlink')

        # 输出到模板
        self.dicViewData['banner']              = idxBannerService.query()
        self.dicViewData['notice']              = idx_notice_ervice.query()
        self.dicViewData['demand']              = idxDemandService.query()
        self.dicViewData['media']               = idxMediaService.query()
        self.dicViewData['media_star']          = idxMediaStarService.query()
        self.dicViewData['media_revenue_top']   = idxMediaRevenueTopService.query()
        self.dicViewData['yidao_case']          = yidaoCaseService.query()
        self.dicViewData['friendlink']          = friendlinkService.lists()

        self.display('index_v2')

    def getSeo(self):
        """
        :func: 获取平台首页搜索引擎信息 tag = 1 平台首页
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.out(401)
                return
            status, data = self.importService('index_seo').getSeo(args)
            if status==200:
                self.out(200, '', data)
            else:
                self.out(500)
        else:
            self.out(401)