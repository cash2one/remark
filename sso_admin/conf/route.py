#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 路由配置
# 增加控制器, 导入控制器文件引用类，并修改route list

import tornado.web
import config

# 自定义控制器，增加路由
import controller.account as Account

route = [
    (r"/login", Account.Account),
    (r"/logout", Account.Account),
    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=config.CONF['static_path'])),
]

setting = config.CONF
