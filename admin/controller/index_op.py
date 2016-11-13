# -*- coding:utf-8 -*-

import base


class banner(base.base):
    '''
    :func: banner管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'banner'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/banner?'
        # 获取首页数据和数目
        tupBanner = self.importService('index_banner').query(intPage, intPageDataNum)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = tupBanner
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, len(tupBanner), strPageUrl)
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增banner
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_banner').create(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/banner'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更banner
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_banner').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/banner'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除banner
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_banner').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/banner'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def uploadLogo(self):
        """
        :func: 更新logo
        """
        if not self._POST:
            self.redirect('/402')
            return
        if 'logo_image' in self.request.files:
            strFile = self.request.files['logo_image']
        else:
            self.redirect('/402')
            return

        from api.upload import upload

        dicLogo = upload(strFile[0]['body'])
        self.out(200, '', {
            'url': '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicLogo['key'], '-bannerx'),
            'key': dicLogo['key']
        })


class blog(base.base):
    '''
    :func: 博客管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/blog?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('admin_op_blog').blog(intPage, intPageDataNum, strSearch)
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'index_op')

    # def create(self):
    #     """
    #     :func: 新增blog
    #     """
    #     pass
    #
    # def edit(self):
    #     """
    #     :func: 编辑blog
    #     """
    #     pass

    def delete(self):
        """
        :func: 删除blog
        """
        intId = int(self.I('id'))
        dicResp = self.importService('admin_op_blog').blogDelete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/blog'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def top(self):
        """
        :func: blog置顶
        """
        intId = int(self.I('id'))
        dicResp = self.importService('admin_op_blog').blogTop(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/blog'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class friendlink(base.base):
    '''
    :func: 友链管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'friendlink'
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/friendlink?'
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('index_friendlink').query(intPage, intPageDataNum)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增友链
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_friendlink').friendlinkCreate(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/friendlink'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def edit(self):
        """
        :func: 变更友链
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_friendlink').friendlinkEdit(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/friendlink'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除友链
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_friendlink').friendlinkDelete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/friendlink'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def uploadLogo(self):
        """
        :func: 更新友链logo
        """
        if not self._POST:
            self.redirect('/402')
            return
        if 'logo' in self.request.files:
            strFile = self.request.files['logo']
        else:
            self.redirect('/402')
            return

        from api.upload import upload

        dicLogo = upload(strFile[0]['body'])
        self.out(200, '', {
            'url': '%s%s%s' % (self.dicConfig['PIC']['HOST'], dicLogo['key'], '-link'),
            'key': dicLogo['key']
        })


class wechat(base.base):
    '''
    :func: 互推管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/wechat?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('admin_op_wechat').winwin(intPage, intPageDataNum, strSearch)
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'index_op')

    def detail(self):
        '''
        :func: 查看互推详细信息
        '''
        intId = int(self.I('id'))
        dicResp = self.importService('admin_op_wechat').winwinDetail(intId)
        if dicResp['statusCode'] == 200:
            self.dicViewData['detail_info'] = dicResp['dicData']
            self.display('detail', 'index_op')
        else:
            self.redirect('/500')

    def updateStatus(self):
        """
        :func: 更新互推状态
        """
        intId = int(self.I('id'))
        intStatus = int(self.I('status'))
        dicResp = self.importService('admin_op_wechat').winwinUpdateStatus(intId, intStatus)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/winwin'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除互推条目
        """
        intId = int(self.I('id'))
        dicResp = self.importService('admin_op_wechat').winwinDelete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/wechat'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class demand(base.base):
    '''
    :func: 首页需求单管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'index_demand'
        # 获取首页数据

        lisIndexInfo = self.importService('index_demand').index()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增首页需求单
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_demand').create(args)
            if dicResp == 200:
                strRedirectUrl = '/index_op/demand'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更首页需求单
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_demand').update(args)
            if dicResp == 200:
                strRedirectUrl = '/index_op/demand'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除首页需求单
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_demand').delete(intId)
        #print dicResp
        if dicResp == 200:
            strRedirectUrl = '/index_op/demand'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class media(base.base):
    '''
    :func: 优秀自媒体
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'index_media'
        # 获取首页数据
        lisIndexInfo = self.importService('index_media').query()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增自媒体(推荐榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media').mediaCreate(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更自媒体(推荐榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media').mediaUpdate(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除自媒体(推荐榜)
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_media').mediaDelete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/media'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class media_revenue_top(base.base):
    '''
    :func: 热销榜
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'index_media_top'
        # 获取数据
        lisIndexInfo = self.importService('index_media_revenue_top').query()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增自媒体(收入榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media_revenue_top').create(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media_revenue_top'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更自媒体(收入榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media_revenue_top').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media_revenue_top'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除自媒体(收入榜)
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_media_revenue_top').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/media_revenue_top'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)


class media_star(base.base):
    '''
    :func: 明星自媒体
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'index_media_star'
        # 获取数据
        media_star = self.importService('index_media_star').query()
        self.dicViewData['menu'] = strMenu
        self.dicViewData['media_star'] = media_star
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增自媒体(明星榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media_star').create(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media_star'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更自媒体(明星榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_media_star').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/media_star'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除自媒体(明星榜)
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_media_star').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/media_star'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

class ad(base.base):
    '''
    :func: 刊例属性管理
    '''

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 20
        # 分页url
        strPageUrl = '/index_op/ad?'
        # 搜索内容
        strSearch = self.I('search')
        # 获取首页数据和数目
        lisIndexInfo, intRows = self.importService('admin_op_ad').index(intPage, intPageDataNum, strSearch)
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'index_op')

    def create(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_op_ad').create(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/ad'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('admin_op_ad').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/ad'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        intId = int(self.I('id'))
        dicResp = self.importService('admin_op_ad').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/ad'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

class notice(base.base):
    '''
    :func: 公告
    '''
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)
        self.index_notice = self.importService('index_notice')
        
    def index(self):
        strMenu = 'notice'
       # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 分页url
        tup_index_notice = self.importService('index_notice').query(intPage, 10)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_notice'] = tup_index_notice
        self.dicViewData['page_html'] = self.page(intPage, 10, len(tup_index_notice), '/index_op/notice?')
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增自媒体(推荐榜)
        """
        str_type    = self.I('type')
        str_title   = self.I('title')
        str_link    = self.I('link')
        
        self.index_notice.create(str_type, str_title, str_link)
        if self.index_notice.status == 200:
            self.redirect('/index_op/notice')
        else:
            self.redirect('/500')

    def update(self):
        """
        :func: 变更公告
        """
        str_id      = self.I('id')
        str_type    = self.I('type')
        str_title   = self.I('title')
        str_link    = self.I('link')
        
        self.index_notice.update(str_id, str_type, str_title, str_link)
        if self.index_notice.status == 200:
            self.redirect('/index_op/notice')
        else:
            self.redirect('/500')

    def delete(self):
        """
        :func: 删除公告
        """
        self.index_notice.delete(self.I('id'))
        if self.index_notice.status == 200:
            self.redirect('/index_op/notice')
        else:
            self.redirect('/500')


class case(base.base):
    '''
    :func: 案例
    '''
    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        strMenu = 'index_case'
       # 页码
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1
        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/index_op/case?'
        # 搜索内容
        #strSearch = self.I('search')
        # 获取首页数据和数目
        #intRows = 1
        lisIndexInfo, intRows = self.importService('index_case').query(intPage, intPageDataNum)
        self.dicViewData['menu'] = strMenu
        self.dicViewData['index_info'] = lisIndexInfo
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.display('index', 'index_op')

    def create(self):
        """
        :func: 新增自媒体(推荐榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_case').Create(args)

            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/case'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def update(self):
        """
        :func: 变更自媒体(推荐榜)
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.redirect('/500')
                return
            dicResp = self.importService('index_case').update(args)
            if dicResp['statusCode'] == 200:
                strRedirectUrl = '/index_op/case'
            else:
                strRedirectUrl = '/500'
            self.redirect(strRedirectUrl)

    def delete(self):
        """
        :func: 删除自媒体(推荐榜)
        """
        intId = int(self.I('id'))
        dicResp = self.importService('index_case').delete(intId)
        if dicResp['statusCode'] == 200:
            strRedirectUrl = '/index_op/case'
        else:
            strRedirectUrl = '/500'
        self.redirect(strRedirectUrl)

class seo(base.base):

    def initialize(self):
        config = {'isDataBase' : True}
        base.base.initialize(self, config)

    def index(self):
        self.display('index', 'index_op')

    def getSeo(self):
        """
        :func: 查询搜索引擎
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

    def update(self):
        """
        :func: 新增搜索引擎
        """
        if self._POST:
            args = self.request.arguments
            if not isinstance(args, dict):
                self.out(401)
                return
            status = self.importService('index_seo').update(args)
            self.out(status)
        else:
            self.out(401)

