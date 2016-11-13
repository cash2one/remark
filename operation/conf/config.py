#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 配置文件

APP_CONF = {
    # WEB title
    'title': '一道自媒体交易平台管理',
}

PASSTIME = 1296000      # 60*60*24*15  15天,用户操作的模块记录的过期时间
ACCESSINDEX = 50        # 最近超过30次，退出用户，并禁用用户
ACCESSTIME = 10        # 最近10秒，退出用户，并禁用用户