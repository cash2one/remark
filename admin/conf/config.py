#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 配置文件

APP_CONF = {
    # WEB title
    'title': '一道自媒体交易平台管理',
}

PASSTIME = 1296000      # 60*60*24*15  15天,用户操作的模块记录的过期时间
ACCESSINDEX = 50        # 最近超过30次，退出用户，并禁用用户
ACCESSTIME = 10         # 最近10秒，退出用户，并禁用用户


MEDIA_CONF = {
    'media_group_max':200,    # 自媒体一个分组最多200
    'media_down_max':200,     # 自媒体导出200限制
    'meida_down_day_max':20,  # 一个用户一天最多下载10次
}
