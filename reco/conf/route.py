#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 路由配置
# 增加控制器, 导入控制器文件引用类，并修改route list

# 自定义控制器，增加路由
from controller.media_reco import media_reco
from controller.take_order_rank import take_order_rank
from controller.similary_media import similary_media

route = [
    (r"/demand_take_order_rank",   take_order_rank),
    (r"/demand_media_reco",        media_reco),
    (r"/media_similary_media",     similary_media)]
