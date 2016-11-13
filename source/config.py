# -*- coding:utf-8 -*-



## 配置优先级 命令参数 > 应用配置 > 全局配置
def merge_config(command_setting, global_setting, app_setting):
    setting = global_setting

    for key, value in command_setting.items():
        setting[key] = value

    for key, value in setting[setting['mode']].items():
        setting[key] = value

    for key, value in app_setting.items():
        if not command_setting.has_key(key):
            setting[key] = value

    return setting
