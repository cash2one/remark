#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 路由配置
# 增加控制器, 导入控制器文件引用类，并修改route list

# import tornado.web
# import config

# 自定义控制器，增加路由
from controller.index import Index

from controller.user import user
from controller.error import error
from controller.account import Account
from controller.login import Login
from controller.wechat_login import WechatLogin
from controller.image_upload import ImageUpload
from controller.media import Media

import controller.admin_user as au

route = [
    (r"/", Index),
    (r"/login", Login),
    (r"/account", Account),
    (r"/wechat_login", WechatLogin),
    (r"/user", user),
    (r"/admin_user/center", au.center),
    (r"/media", Media),

    (r"/image_upload", ImageUpload),
    (r".*", error),
]
