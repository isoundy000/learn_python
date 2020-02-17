#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
获得mixi牧场的所有配置信息，存入mxfarm_config.py中，mxfarm_config可以直接被引用
mxfarm_config:
    config = {
    }
'''


def get_all_config():
    import os, sys

    cur_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + os.pardir + os.sep
    # sys.path.insert(0, os.path.join(cur_dir, ".."))
    sys.path.append(os.path.join(cur_dir))

    try:
        import game_config
        from models.config import Config as ConfigModel
    except:
        import settings
        settings.set_evn('dev_new', '1')    # settings.set_evn('dev', 'h1')
        import game_config
        from models.config import Config as ConfigModel

    # from apps.config import game_config
    common_config_name_list = game_config.config_name_list
    # game_config_name_list = game_config.all_config_name_list

    config_dict = {}
    for config_key, config_sub_func, is_show_in_admin, is_modifable, xls_table_name, need_download, _ in game_config.config_name_list:
        _c = ConfigModel.get(config_key)
        config_dict[config_key] = _c.value

    filename = cur_dir + '/test/local_config.py'
    f = open(filename, 'w')
    d = str(config_dict)

    f.write('config='+d)
    f.close()
    return filename


if __name__ == '__main__':
    get_all_config()