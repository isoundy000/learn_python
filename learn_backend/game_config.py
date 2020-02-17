#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import cPickle as pickle
from datetime import datetime

from lib.utils.debug import print_log
from lib.utils import md5
from models.config import ConfigManager
from models.config import ConfigVersionManager
from models.config import ServerConfig
import return_msg_config as RMC
import settings


config_version = {}
# 子函数对应关系
sub_func_config = {}


# def make_version(value):
#     v = 0
#     m = md5(repr(value))
#     for k, i in enumerate(m):
#         n = int(k + ord(i))
#         v += (n % 16 + n % 15 + n % 14 + n % 13 + n / 2) + 10000 * k * ord(i)
#     return v


def make_version(value):
    return md5(repr(value))


def update_funcs_version(config_name, cv_manager=None, version=None):
    """# update_funcs_version: docstring
    args:
        con:    ---    arg
    returns:
        0    ---
    """
    cv_obj = cv_manager if cv_manager else ConfigVersionManager.get_config_version_obj(config_type=getattr(settings, 'CONFIG_TYPE', 1))
    versions = cv_obj.versions

    if versions.get(config_name, 0) != version:
        versions[config_name] = version
        globals()['config_version'][config_name] = version
        cv_obj.is_save = True
        if cv_manager is None:
            cv_obj.save()


def generate_sub_version(func_name, cv_manager=None):
    cv = cv_manager if cv_manager else ConfigVersionManager.get_config_version_obj(config_type=getattr(settings, 'CONFIG_TYPE', 1))
    func_config = sub_func_config.get(func_name, [])
    return make_version('|'.join([str(cv.versions.get(name, 0)) for name in func_config]))


############################################################
############# CONFIG_SUB_FUNCS_BEGIN
###################

def cityid_cityorderid_func(config_name, func_name, cv_manager, *args, **kwargs):
    cityid_cityorderid = {}
    chapterid_cityid = {}
    _d = globals().get('map_main_story')
    if _d:
        for _k, _v in _d.iteritems():
            cityid_cityorderid[_v['stage_id']] = _k
            if _v['chapter'] not in chapterid_cityid:
                chapterid_cityid[_v['chapter']] = [_v['stage_id']]
            else:
                chapterid_cityid[_v['chapter']].append(_v['stage_id'])
                chapterid_cityid[_v['chapter']].sort()

    globals()['cityid_cityorderid'] = cityid_cityorderid
    globals()['chapterid_cityid'] = chapterid_cityid
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('cityid_cityorderid', cv_manager, version)


def enemy_all_merge_func(config_name, func_name, cv_manager, *args, **kwargs):
    if config_name in globals():
        r = globals().get('enemy_all', {})
        d = globals()[config_name]
        r.update(d)
        del d, globals()[config_name]
        globals()['enemy_all'] = r
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('enemy_all', cv_manager, version)


def enemy_detail_merge_func(config_name, func_name, cv_manager, *args, **kwargs):
    if config_name in globals():
        r = globals().get('enemy_detail', {})
        d = globals()[config_name]
        r.update(d)
        globals()['enemy_detail'] = r
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('enemy_detail', cv_manager, version)


def enemy_soldier_sub_func(config_name, func_name, cv_manager, *args, **kwargs):
    if config_name in globals():
        r = {}
        version_data = {}
        d = globals()[config_name]
        for k, v in d.iteritems():
            key = 'enemy_soldier_%d' % (int(k) / 1000)
            if key not in r:
                r[key] = {k: v}
            else:
                r[key][k] = v
            if key not in version_data:
                version_data[key] = repr([vv for k, vv in v.iteritems()])
            else:
                version_data[key] += repr([vv for k, vv in v.iteritems()])
        globals().update(r)
        for k in r.iterkeys():
            version = make_version(version_data[k])
            update_funcs_version(k, cv_manager, version)


def middle_map_building_func(config_name, func_name, cv_manager, *args, **kwargs):
    r = globals().get('middle_building_mine', {})
    d = globals()[config_name]
    t = config_name.split('_')[1]
    for k, v in d.iteritems():
        v['type'] = t

    r.update(d)
    globals()['middle_building_mine'] = r
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('middle_building_mine', cv_manager, version)


def leader_skill_tree_func(config_name, func_name, cv_manager, *args, **kwargs):
    """# leader_skill_tree: 生成主角技能树
    """
    skill_tree0 = {}
    head = []
    tree_skill_list = {}
    leader_skill = globals()['leader_skill']
    for k, v in leader_skill.iteritems():
        if not k in skill_tree0:
            skill_tree0[k] = {}
        if v['tree'] not in tree_skill_list:
            tree_skill_list[v['tree']] = set([k])
        else:
            tree_skill_list[v['tree']].add(k)
        pre_k_list = v['pre_skill']
        if not pre_k_list:
            head.append(k)
        for pre_k in pre_k_list:
            pre_k = int(pre_k)
            if not pre_k in skill_tree0:
                skill_tree0[pre_k] = {}
            skill_tree0[pre_k][k] = skill_tree0[k]

    result = {}
    for h in head:
        result[leader_skill[h]['tree']] = {h: skill_tree0[h]}
    globals()['leader_skill_tree'] = result
    globals()['leader_skill_tree_skill_list'] = tree_skill_list
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('leader_skill_tree_skill_list', cv_manager, version)
        update_funcs_version('leader_skill_tree', cv_manager, version)


def did_drama_config(config_name, func_name, cv_manager, *args, **kwargs):
    """

    """
    tempDrama = globals()['drama'];
    fight_to_drama = {};

    for i in tempDrama:
        if (tempDrama[i]['fightID'] not in fight_to_drama):
            fight_to_drama[tempDrama[i]['fightID']] = [i];
        else:
            fight_to_drama[tempDrama[i]['fightID']].append(i);

    globals()['fight_to_drama'] = fight_to_drama;
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('fight_to_drama', cv_manager, version)


def formation_attack_config(config_name, func_name, cv_manager, *args, **kwargs):
    """# formation_attack_config: docstring
    """
    if config_name in globals():
        r = globals().get('formation_attack', {})
        d = globals()[config_name]
        t = int(config_name.split('_')[1])

        r[t] = d
        globals()['formation_attack'] = r
        del d, globals()[config_name]
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('formation_attack', cv_manager, version)


def charge_scheme_func(config_name, func_name, cv_manager, *args, **kwargs):
    """充值定单配置，额外增加商品id到配置的映射配置
    """
    d = globals()[config_name]
    new_r = {}
    for buy_id, obj in d.iteritems():
        new_r[obj['cost']] = buy_id

    globals()['charge_scheme'] = new_r


def reward_target_sort_func(config_name, func_name, cv_manager, *args, **kwargs):
    """增加 target_sort 到配置ID的映射配置
    """
    d = globals()[config_name]
    target_key = '%s_target_sort' % config_name
    new_r = {}
    for award_id, obj in d.iteritems():
        new_r.setdefault(obj['target_sort'], []).append(award_id)

    globals()[target_key] = new_r


def active_fight_forever_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    d_sort = sorted(d.iteritems(), key=lambda x: x[0])
    target_key = '%s_sort' % config_name
    globals()[target_key] = d_sort


def active_chapter_func(config_name, func_name, cv_manager, *args, **kwargs):
    key = 'all_active_chapter'
    d = globals()[config_name]
    all_config = globals().get(key, {})
    all_config.update(d)
    globals()[key] = all_config


def last_name_fist_name_func(config_name, func_name, cv_manager, *args, **kwargs):
    """# last_name_fist_name_func:
    args:
        confi:    ---    arg
    returns:
        0    ---
    """
    d = globals()[config_name]

    globals()['random_last_name'] = d.keys()
    globals()['random_first_name'] = [i for i in d.values() if i]
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('random_last_name', cv_manager, version)
        update_funcs_version('random_first_name', cv_manager, version)


def online_award_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    x = sorted(d.iteritems(), key=lambda x: x[1]['second'])
    globals()['online_award_sort'] = x


def guide_button_open_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    # TODO: 新手引导配置调整， 为了兼容老的客户端，先暂时保留guide_button_open，增加新配置guide_button_open_new
    # 待到删档的时候再删除配置 先暂时保留guide_button_open
    x = {}
    new_x = {}
    for k, v in d.iteritems():
        for kk, vv in v.iteritems():
            for i in vv.get('open_button', []):
                x[i] = kk
                new_x[i] = [k, kk]
    globals()['guide_button_open'] = x
    globals()['guide_button_open_new'] = new_x
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('guide_button_open', cv_manager, version)
        update_funcs_version('guide_button_open_new', cv_manager, version)


def characterid_uniqid_func(config_name, func_name, cv_manager, *args, **kwargs):
    """# characterid_uniqid_func: 卡牌的characterid_uniqid对应表
    """
    d = globals()[config_name]
    x = {}
    for k, v in d.iteritems():
        char_id = v['character_ID']
        if char_id not in x:
            x[char_id] = {v['star']: k}
        else:
            x[char_id][v['star']] = k
    globals()['characterid_uniqid_config'] = x


def characterbook_func(config_name, func_name, cv_manager, *args, **kwargs):
    globals()['%s_%s' % (config_name, 'sort')] = [v['character_id']
                                                  for v in globals()[config_name].itervalues()]


def equipbook_func(config_name, func_name, cv_manager, *args, **kwargs):
    globals()['%s_%s' % (config_name, 'sort')] = [v['equip_id']
                                                  for v in globals()[config_name].itervalues()]


def fight_config_func(config_name, func_name, cv_manager, *args, **kwargs):
    """# leader_skill_tree: 生成主角技能树
    """
    if config_name in globals():
        d = globals().get('map_fight', {})
        d.update(globals()[config_name])
        globals()['map_fight'] = d
        del globals()[config_name]
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('map_fight', cv_manager, version)


def map_title_detail_func(config_name, func_name, cv_manager, *args, **kwargs):
    """# map_title_detail_func: 合并地图
    """
    if config_name in globals():
        d = globals().get('map_title_detail', {})
        d.update(globals()[config_name])
        del globals()[config_name]
        globals()['map_title_detail'] = d
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('map_title_detail', cv_manager, version)


def map_title_detail_mapping_func(config_name, func_name, cv_manager, *args, **kwargs):
    """

    :param config_name:
    :param func_name:
    :param cv_manager:
    :param args:
    :param kwargs:
    :return:
    """
    if config_name in globals():
        data = {}
        config = globals()[config_name]
        for building_id, value in config.iteritems():
            data[building_id] = config_name
        if 'map_title_detail_mapping' not in globals():
            globals()['map_title_detail_mapping'] = data
        else:
            globals()['map_title_detail_mapping'].update(data)


def commander_recipe_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = {}
    config = globals().get(config_name, {})
    for recipe, v in config.iteritems():
        for item in v['part']:
            d[item] = recipe
    globals()['%s_index' % config_name] = d


def ranking_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = {}
    ranks = []
    cfg_ids = []
    config = globals().get(config_name, {})
    for cfg_id, obj in sorted(config.iteritems()):
        ranks.append(obj['rank'][0])
        cfg_ids.append(cfg_id)

    globals()['ranking_sort'] = {'ranks': ranks, 'cfg_ids': cfg_ids}


def reward_gacha_func(config_name, func_name, cv_manager, *args, **kwargs):
    reward_gacha_sort = {}
    config = globals().get(config_name, {})
    for cfg_id, obj in config.iteritems():
        reward_gacha_sort.setdefault(obj['target_sort'], []).append(cfg_id)
    globals()['reward_gacha_sort'] = reward_gacha_sort


def auto_sweep_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = {}
    config = globals().get(config_name, {})
    for title_id, v in config.iteritems():
        item_id = v.get('item_id', '')
        if not item_id:
            continue
        if item_id not in d:
            d[item_id] = {}
        d[v['item_id']][title_id] = v
    globals()[config_name] = d


def make_timestamp_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    for v in d.itervalues():
        for _key in ['start_time', 'end_time']:
            # 兼容老配置里没有 开始、结束时间的情况
            if _key in v:
                if v['exchange_time'] == 1 and isinstance(v[_key], basestring):
                    try:
                        v[_key] = time.mktime(datetime.strptime(v[_key], '%Y/%m/%d %H:%M').timetuple())
                    except:
                        v[_key] = 0  # 如果配置格式错误，开始和结束时间默认变为0


def make_super_commander(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    make_super_commander = {}
    commander_tree_skill = {}
    if d:
        for _k, _v in d.iteritems():
            if _v['race'] not in make_super_commander:
                make_super_commander[_v['race']] = [_k]
            else:
                make_super_commander[_v['race']].append(_k)

            if _v['tree'] not in commander_tree_skill:
                commander_tree_skill[_v['tree']] = [_k]
            else:
                commander_tree_skill[_v['tree']].append(_k)
    globals()['commander_tree_skill'] = commander_tree_skill
    globals()['exchange_super_commander'] = make_super_commander


def make_festival_daily(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['shop_id'] = k
        if version not in data:
            data[version] = {}

        data[version][k] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def make_festival_shop(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['shop_id'] = k
        if version not in data:
            data[version] = {}

        data[version][k] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def make_festival_exchange(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['exchange_id'] = k
        if version not in data:
            data[version] = {}

        data[version][k] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def exchangeid_by_itemid_func(config_name, func_name, cv_manager, *args, **kwargs):
    # 道具id 反向索引兑换id
    exchangeid_by_itemid = {}
    _d = globals().get('exchange')
    if _d:
        for _k, _v in _d.iteritems():
            exchangeid_by_itemid[_v['need_item']] = _k

    globals()['exchangeid_by_itemid'] = exchangeid_by_itemid


def adver_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    for v in d.itervalues():
        for _key in ['start_time', 'end_time']:
            # 兼容老配置里没有 开始、结束时间的情况
            if _key in v and isinstance(v[_key], basestring):
                v[_key] = time.mktime(time.strptime(v[_key], '%Y/%m/%d %H:%M:%S'))


def date_str_to_ts_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    for v in d.itervalues():
        for _key in ['start_time', 'end_time']:
            if _key in v and isinstance(v[_key], basestring):
                try:
                    v[_key] = time.mktime(time.strptime(v[_key], '%Y/%m/%d %H:%M:%S'))
                except:
                    v[_key] = time.mktime(time.strptime(v[_key], '%Y-%m-%d %H:%M'))


def month_award_coin_loop_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        reriod = v['reriod']
        v['id'] = k
        if reriod not in data:
            data[reriod] = {}

        data[reriod][v['score']] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def group_rank_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['active_id'] = k
        if version not in data:
            data[version] = {}

        data[version][v['rank']] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def group_shop_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['shop_id'] = k
        if version not in data:
            data[version] = {}

        data[version][k] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def super_all_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    config_data = pickle.loads(pickle.dumps(d))
    data = {}
    for k, v in config_data.iteritems():
        if 'version' not in v:
            break
        version = v['version']
        v['id'] = k
        if version not in data:
            data[version] = {}

        data[version][k] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data

    for v in d.itervalues():
        for _key in ['start_time', 'end_time']:
            if _key in v and isinstance(v[_key], basestring):
                try:
                    v[_key] = time.mktime(time.strptime(v[_key], '%Y/%m/%d %H:%M:%S'))
                except:
                    v[_key] = time.mktime(time.strptime(v[_key], '%Y-%m-%d %H:%M'))


def super_rich_func(config_name, func_name, cv_manager, *args, **kwargs):
    d = globals()[config_name]
    data = {}
    for k, v in d.iteritems():
        if 'version' not in v or 'rank' not in v:
            break
        version = v['version']
        v['id'] = k
        if version not in data:
            data[version] = {}

        data[version][v['rank']] = v
    new_config_name = '%s_mapping' % config_name
    globals()[new_config_name] = data


def map_mapping_func(config_name, func_name, cv_manager, *args, **kwargs):
    """ map对应关系, {city: [build_id, build_id]}

    :param config_name:
    :param func_name:
    :param cv_manager:
    :param args:
    :param kwargs:
    :return:
    """
    d = globals()[config_name]
    data = {}
    for city, value in d.iteritems():
        data[city] = sorted([str(pos) for row in value for pos in row if pos > 0])
    globals()['%s_mapping' % config_name] = data


def chapter_func(config_name, func_name, cv_manager, *args, **kwargs):
    """ chapter

    :param config_name:
    :param func_name:
    :param cv_manager:
    :param args:
    :param kwargs:
    :return:
    """
    d = globals()[config_name]
    data = {}
    for chapter_id, value in d.iteritems():
        if value.get('is_show', 1):
            is_hard = value['is_hard']
            if is_hard not in data:
                data[is_hard] = [chapter_id]
            else:
                data[is_hard].append(chapter_id)
    sorted_data = {}
    for sort, value in data.iteritems():
        sorted_data[sort] = sorted(value)
    globals()['%s_mapping' % config_name] = sorted_data
    if sub_func_config[func_name][-1] == config_name or kwargs.get('force', False):
        version = generate_sub_version(func_name, cv_manager)
        update_funcs_version('%s_mapping' % config_name, cv_manager, version)


###################
############# CONFIG_SUB_FUNCS_END
############################################################


###################
############# CONFIG_OTHER_END
############################################################


def generate_other_version(other_name):
    other_config = globals()[other_name]
    other_list = [(k, v) for k, v in other_config.iteritems()]
    other_list.sort(key=lambda x: x[0])
    return make_version(other_list)


school_train_time_config = {
    # 类型，时间，需要的宝石
    1: (3600 * 2, 0),
    2: (3600 * 4, 1),
    3: (3600 * 8, 2),
    4: (3600 * 24, 3),
}


update_funcs_version('school_train_time_config', version=generate_other_version('school_train_time_config'))


school_train_type_config = {
    # 类型，加成，需要的宝石
    1: (100, 0),
    2: (120, 1),
    3: (150, 2),
    4: (200, 3),
}

update_funcs_version('school_train_type_config', version=generate_other_version('school_train_type_config'))


building_type = ['harbor', 'school', 'factory', 'hospital', 'laboratory', 'metal', 'energy', 'food']


# 开宝箱会触发特殊效果的box_id们
BOX_REWARD_BOX_IDS = (13, 42, 99999, 99994, 99967, 99861, 99833, 99810, 99792)

###################
############# CONFIG_OTHER_END
############################################################


def is_config_out():
    """# get_config_ver: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    cv = ConfigVersionManager.get_config_version_obj(config_type=getattr(settings, 'CONFIG_TYPE', 1))
    vers = cv.versions
    if globals().get('config_version', {}) != vers:
        from lib.db import dict_diff
        update, remove_keys = dict_diff(globals().get('config_version', {}), vers)
        print_log(update)
    return globals().get('config_version', {}) == vers


config_name_list = (
    # (config_key,  config_sub_func,            is_show_in_admin, is_modifiable, xls_table_name, send_to_client, is_master
    ('zhanwei',     (cityid_cityorderid_func,),  1,                 1,             'zhanwei',        1, 0, ),
    ('map_main_story', (cityid_cityorderid_func,), 1, 1, 'main_story', 1, 1,),
    ('map_fight', (                        ), 0, 0, 'map_fight', 1, 1,),
    ('fight_common', (fight_config_func,), 1, 1, 'fight_common', 0, 1,),
    ('fight_boss', (fight_config_func,), 1, 1, 'fight_boss', 0, 1,),
    ('fight_active', (fight_config_func,), 1, 1, 'fight_active', 0, 1,),
    ('fight_treasure', (fight_config_func,), 1, 1, 'fight_treasure', 0, 1,),
    ('fight_hero', (fight_config_func,), 1, 1, 'fight_hero', 0, 1,),
    ('fight_common_purgatory', (fight_config_func,), 1, 1, 'fight_common_purgatory', 0, 1,),
    ('fight_common_hell', (fight_config_func,), 1, 1, 'fight_common_hell', 0, 1,),
    ('fight_boss_hell', (fight_config_func,), 1, 1, 'fight_boss_hell', 0, 1,),
    ('fight_boss_purgatory', (fight_config_func,), 1, 1, 'fight_boss_purgatory', 0, 1,),
    ('map', (map_mapping_func,), 1, 1, 'map', 1, 1,),
    ('map_title_detail', (                        ), 0, 0, 'title_detail', 1, 1,),
    (
    'map_title_detail_base', (map_title_detail_mapping_func, map_title_detail_func,), 1, 1, 'title_detail_base', 0, 1,),
    ('map_title_detail_common', (map_title_detail_func,), 1, 1, 'title_detail_common', 0, 1,),
    ('map_title_detail_guild', (map_title_detail_func,), 1, 1, 'title_detail_guild', 0, 1,),
    ('map_title_detail_hell', (map_title_detail_mapping_func,), 1, 1, 'title_detail_hell', 1, 1,),
    ('map_title_detail_purgatory', (map_title_detail_mapping_func,), 1, 1, 'title_detail_purgatory', 1, 1,),
    ('enemy_boss', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_boss', 0, 1,),
    ('enemy_essence', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_essence', 0, 1,),
    ('enemy_endless', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_endless', 0, 1,),
    ('enemy_active', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_active', 0, 1,),
    ('enemy_endlessboss', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_endlessboss', 0, 1,),
    ('enemy_activeboss', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_activeboss', 0, 1,),
    ('enemy_soldier_hard', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_soldier_hard', 0, 1,),
    ('enemy_boss_hard', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_boss_hard', 0, 1,),
    ('enemy_boss_hell', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_boss_hell', 0, 1,),
    ('enemy_boss_purgatory', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_boss_purgatory', 0, 1,),
    ('enemy_soldier_hell', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_soldier_hell', 0, 1,),
    ('enemy_soldier_purgatory', (enemy_detail_merge_func, enemy_all_merge_func,), 1, 1, 'enemy_soldier_purgatory', 0,
     1,),
    ## TODO 临时让前端不再下载enemy_soldier @2014.06.07
    # ('enemy_soldier',            (enemy_all_merge_func, ), 1, 1, 'enemy_soldier'       , 0, 1, ) ,
    # ('enemy_detail',             (                        ), 0, 0, 'enemy_detail'            , 0, 1, ) ,
    ## TODO 临时让前端不再下载enemy_soldier @2014.06.07
    ######################
    ('enemy_soldier', (enemy_soldier_sub_func, enemy_all_merge_func,), 1, 1, 'enemy_soldier', 0, 1,),
    ('enemy_hero', (enemy_soldier_sub_func, enemy_all_merge_func,), 1, 1, 'enemy_hero', 0, 1,),
    ('enemy_detail', (                        ), 0, 0, 'enemy_detail', 1, 1,),

    ('enemy_all', (                        ), 0, 0, 'enemy_all', 0, 1,),
    ('cityid_cityorderid', (                        ), 0, 0, 'cityid_cityorderid', 1, 1,),
    ('chapterid_cityid', (                        ), 0, 0, 'chapterid_cityid', 1, 1,),
    ('character_detail', (characterid_uniqid_func,), 1, 1, 'character_detail', 1, 1,),
    ('character_book', (characterbook_func,), 1, 1, 'character_book', 1, 1,),
    ('equip_book', (equipbook_func,), 1, 1, 'equip_book', 1, 1,),
    ('character_exchange', (                        ), 1, 1, 'character_exchange', 1, 1,),
    ('character_break', (                        ), 1, 1, 'break', 1, 1,),
    ('character_break_new', (                        ), 1, 1, 'break_new', 1, 1,),
    ('break_control', (                        ), 1, 1, 'break_control', 1, 1,),
    ('dirt_shop', (                        ), 1, 1, 'dirt_shop', 1, 1,),
    ('characterid_uniqid_config', (                        ), 0, 0, 'characterid_uniqid_config', 0, 1,),
    ('occupation', (                        ), 1, 1, 'occupation', 1, 1,),
    ('character_base', (                        ), 1, 1, 'character_base', 1, 1,),
    ('character_base_rate', (                        ), 1, 1, 'character_base_rate', 1, 1,),
    ('role', (                        ), 1, 1, 'role', 1, 1,),
    ('role_detail', (                        ), 1, 1, 'role_detail', 1, 1,),
    ('role_skill', (                        ), 1, 1, 'role_skill', 1, 1,),
    ('leader_skill', (leader_skill_tree_func,), 1, 1, 'leader_skill', 1, 1,),
    ('leader_skill_tree', (                        ), 0, 0, 'leader_skill_tree', 1, 1,),
    ('leader_skill_develop', (                        ), 1, 1, 'leader_skill_develop', 1, 1,),
    ('skill_detail', (                        ), 1, 1, 'skill_detail', 1, 1,),
    ('skill_levelup', (                        ), 1, 1, 'skill_levelup', 1, 1,),

    ('building_base_harbor', (                        ), 1, 1, 'building_base_harbor', 1, 1,),

    ('formation', (                        ), 1, 1, 'formation', 1, 1,),
    ('formation_attack', (                        ), 1, 0, 'formation_attack', 1, 1,),
    ('formation_1', (formation_attack_config,), 0, 1, 'formation_1', 0, 1,),
    ('formation_2', (formation_attack_config,), 0, 1, 'formation_2', 0, 1,),
    ('formation_3', (formation_attack_config,), 0, 1, 'formation_3', 0, 1,),
    ('formation_4', (formation_attack_config,), 0, 1, 'formation_4', 0, 1,),
    ('formation_5', (formation_attack_config,), 0, 1, 'formation_5', 0, 1,),
    ('formation_6', (formation_attack_config,), 0, 1, 'formation_6', 0, 1,),
    ('character_train_rate', (                        ), 1, 1, 'character_train_rate', 1, 1,),
    ('character_train_time', (                        ), 1, 1, 'character_train_time', 1, 1,),
    ('character_train_position', (                        ), 1, 1, 'character_train_position', 1, 1,),
    ('evolution', (                        ), 1, 1, 'evolution', 1, 1,),
    ('evolution_3', (                        ), 1, 1, 'evolution_3', 1, 1,),
    ('evolution_4', (                        ), 1, 1, 'evolution_4', 1, 1,),
    ('evolution_5', (                        ), 1, 1, 'evolution_5', 1, 1,),

    ('character_strengthen', (                        ), 1, 1, 'character_strengthen', 1, 1,),
    ('building_base_school', (                        ), 1, 1, 'building_base_school', 1, 1,),  # TODO 废弃
    ('character_train', (                        ), 1, 1, 'character_train', 1, 1,),
    ('school_train_time_config', (                        ), 0, 0, 'school_train_time_config', 1, 1,),
    ('school_train_type_config', (                        ), 0, 0, 'school_train_type_config', 1, 1,),
    ('equip', (                        ), 1, 1, 'equip', 1, 1,),
    ('equip_st', (                        ), 1, 1, 'equip_st', 1, 1,),
    ('equip_exchange', (                        ), 1, 1, 'equip_exchange', 1, 1,),
    ('suit', (                        ), 1, 1, 'suit', 1, 1,),
    ('equip_evolution', (                        ), 1, 1, 'equip_evolution', 1, 1,),
    ('equip_strongthen', (                        ), 1, 1, 'equip_strongthen', 1, 1,),
    ('middle_map', (                        ), 1, 1, 'middle_map', 1, 1,),
    ('middle_map_data', (                        ), 1, 1, 'middle_map_data', 1, 1,),
    ('middle_resource', (middle_map_building_func,), 1, 1, 'middle_resource', 0, 1,),
    ('middle_mine', (middle_map_building_func,), 1, 1, 'middle_mine', 0, 1,),
    ('middle_building_mine', (                        ), 0, 0, 'middle_building_mine', 1, 1,),
    ('gacha', (                        ), 1, 1, 'gacha', 1, 1,),
    ('gacha_box', (                        ), 1, 1, 'gacha_box', 0, 1,),
    ('guild_level', (                        ), 1, 1, 'guild_level', 1, 1,),
    ('guild_shop', (                        ), 1, 1, 'guild_shop', 1, 1,),
    ('guild_shop_item', (                        ), 1, 1, 'guild_shop_item', 1, 1,),
    ('guild_GVGplayer', (                        ), 1, 1, 'guild_GVGplayer', 1, 1,),
    ('guild_GVGmonster', (                        ), 1, 1, 'guild_GVGmonster', 1, 1,),
    ('guild_GVGhome', (                        ), 1, 1, 'guild_GVGhome', 1, 1,),
    ('guild_bossplayer', (                        ), 1, 1, 'guild_bossplayer', 1, 1,),
    ('guild_middleplayer', (                        ), 1, 1, 'guild_middleplayer', 1, 1,),
    ('guild_tech', (                        ), 1, 1, 'guild_tech', 1, 1,),
    ('guild_funtion', (                        ), 1, 1, 'guild_funtion', 1, 1,),
    ('guild_fight', (                        ), 1, 1, 'guild_fight', 1, 1,),
    ('guild_fight_reward', (                       ), 1, 1, 'guild_fight_reward', 0, 1,),
    ('guild_fight_time', (                       ), 1, 1, 'guild_fight_time', 0, 1,),
    ('gvg_map', (                        ), 1, 1, 'gvg_map', 1, 1,),
    ('daily_award', (                        ), 1, 1, 'daily_award', 1, 1,),
    ('chain', (                        ), 1, 1, 'chain', 1, 1,),
    ('week_award', (                        ), 1, 1, 'week_award', 1, 1,),
    ('month_award', (                        ), 1, 1, 'month_award', 1, 1,),
    ('month_award_coin', (                        ), 1, 1, 'month_award_coin', 1, 1,),
    ('month_award_coin_loop', (month_award_coin_loop_func,), 1, 1, 'month_award_coin_loop', 1, 1,),
    ('online_award', (online_award_func,), 1, 1, 'online_award', 1, 1,),
    ('drama', (did_drama_config,), 1, 1, 'drama', 1, 1,),
    ('item', (                        ), 1, 1, 'item', 1, 1,),
    ('unify_ios_item', (                        ), 1, 1, 'unify_ios_item', 1, 1,),
    ('unify_android_item', (                        ), 1, 1, 'unify_android_item', 1, 1,),
    ('exchange', (exchangeid_by_itemid_func,), 1, 1, 'exchange', 1, 1,),
    ('box', (                        ), 1, 1, 'box', 1, 1,),
    ('unify_ios_box', (                        ), 1, 1, 'unify_ios_box', 1, 1,),
    ('unify_android_box', (                        ), 1, 1, 'unify_android_box', 1, 1,),
    ('whats_inside', (                        ), 1, 1, 'whats_inside', 1, 1,),
    ('chapter', (chapter_func,), 1, 1, 'chapter', 1, 1,),
    ('chapter_mapping', (                        ), 0, 0, 'chapter_mapping', 1, 1,),
    ('arena_award', (                        ), 1, 1, 'arena_award', 1, 1,),
    ('arena_award_milestone', (                        ), 1, 1, 'arena_award_milestone', 1, 1,),
    ('arena_shop', (                        ), 1, 1, 'arena_shop', 1, 1,),
    ('shop', (                        ), 1, 1, 'shop', 1, 1,),
    ('card_shop', (                        ), 1, 1, 'card_shop', 0, 1,),
    ('vip_shop', (                        ), 1, 1, 'VIPshop', 1, 1,),
    ('server_shop', (                        ), 1, 1, 'server_shop', 1, 1,),
    ('metal_core_shop', (                        ), 1, 1, 'metal_core_shop', 1, 1,),
    ('guide', (guide_button_open_func,), 1, 1, 'guide', 1, 1,),
    ('guide_button_open', (                        ), 0, 0, 'guide_button_open', 1, 1,),
    ('guide_button_open_new', (                        ), 0, 0, 'guide_button_open_new', 1, 1,),
    ('button_open', (                        ), 1, 1, 'button_open', 1, 1,),
    ('guide_team', (                        ), 1, 1, 'guide_team', 1, 1,),
    ('guide_manual', (                        ), 1, 1, 'guide_manual', 1, 1,),
    ('loadingtips', (                        ), 1, 1, 'loadingtips', 1, 1,),
    ('loading', (                        ), 1, 1, 'loading', 1, 1,),
    ('charge', (charge_scheme_func,), 1, 1, 'buykubi', 1, 1,),
    ('code', (                        ), 1, 1, 'code', 1, 1,),
    ('combat_base', (                        ), 1, 1, 'point', 1, 1,),
    ('combat_skill', (                        ), 1, 1, 'level', 1, 1,),
    ('opening', (reward_target_sort_func,), 1, 1, 'Opening', 1, 1,),
    ('reward_daily', (reward_target_sort_func,), 1, 1, 'daily', 1, 1,),
    ('reward_once', (reward_target_sort_func,), 1, 1, 'once', 1, 1,),
    ('reward_gift', (                        ), 1, 1, 'gift', 0, 1,),
    ('reward_diary', (reward_target_sort_func,), 1, 1, 'diary', 1, 1,),
    ('level_reward', (                        ), 1, 1, 'levelreward', 0, 1,),
    ('chargereward', (                        ), 1, 1, 'chargereward', 0, 1,),
    ('dailyscore', (                        ), 1, 1, 'dailyscore', 1, 1,),
    ('diaryscore', (                        ), 1, 1, 'diaryscore', 1, 1,),
    ('level_gift', (                        ), 1, 1, 'level_gift', 1, 1,),
    ('notice', (                        ), 1, 1, 'notice', 1, 1,),
    ('adver', (adver_func,), 1, 1, 'adver', 1, 1,),
    ('adver_guild', (adver_func,), 1, 1, 'adver_guild', 1, 1,),
    ('adver_inheritance', (adver_func,), 1, 1, 'adver_inheritance', 1, 1,),
    ('server_adver', (                        ), 1, 1, 'server_adver', 1, 1,),
    ('notice_active', (                        ), 1, 1, 'notice_active', 1, 1,),
    ('robot', (                        ), 1, 1, 'robot', 0, 1,),
    ('formation_type', (                        ), 1, 1, 'formation_type', 0, 1,),
    ('version', (                        ), 1, 1, 'version', 0, 1,),
    ('active', (                        ), 1, 1, 'active', 1, 1,),
    ('all_active_chapter', (                        ), 1, 0, 'all_active_chapter', 0, 1,),
    ('active_chapter', (active_chapter_func,), 1, 1, 'active_chapter', 1, 1,),
    ('hero_chapter', (active_chapter_func,), 1, 1, 'hero_chapter', 1, 1,),
    ('active_fight_forever', (active_fight_forever_func,), 1, 1, 'active_fight_forever', 1, 1,),
    ('active_detail', (                        ), 1, 1, 'active_detail', 1, 1,),
    ('star_reward', (                        ), 1, 1, 'star_reward', 1, 1,),
    ('race', (                        ), 1, 1, 'race', 1, 1,),
    ('random_name', (last_name_fist_name_func,), 1, 1, 'random_name', 0, 1,),
    ('random_last_name', (                        ), 0, 0, 'random_last_name', 1, 1,),
    ('random_first_name', (                        ), 0, 0, 'random_first_name', 1, 1,),
    ('error', (                        ), 1, 1, 'error', 1, 1,),
    ('vip', (                        ), 1, 1, 'vip', 1, 1,),
    ('pay', (                        ), 1, 1, 'pay', 1, 1,),
    ('world_boss', (                        ), 1, 1, 'world_boss', 1, 1,),
    ('world_boss_reward', (                        ), 1, 1, 'world_boss_reward', 1, 1,),
    ('wanted', (reward_target_sort_func,), 1, 1, 'wanted', 1, 1,),
    ('godgift', (                        ), 1, 1, 'godgift', 1, 1,),
    ('godgift_pvp', (                        ), 1, 1, 'godgift_PVP', 0, 1,),
    ('commander_type', (                        ), 1, 1, 'commander_type', 1, 1,),
    ('commander_recipe', (commander_recipe_func,), 1, 1, 'commander_recipe', 1, 1,),
    ('commander_level', (                        ), 1, 1, 'commander_level', 1, 1,),
    ('assistant', (                        ), 1, 1, 'assistant', 1, 1,),
    ('destiny', (                        ), 1, 1, 'destiny', 1, 1,),
    ('assistant_random', (                        ), 1, 1, 'assistant_random', 1, 1,),
    ('vip_guide', (                        ), 1, 1, 'VIPguide', 1, 1,),
    ('outlets', (                        ), 1, 1, 'outlets', 1, 1,),
    ('outlets_team', (                        ), 1, 1, 'outlets_team', 1, 1,),
    ('inreview', (                        ), 1, 1, 'inreview', 1, 1,),
    ('resoucequality', (                        ), 1, 1, 'resoucequality', 1, 1,),
    ('request_code', (                        ), 1, 1, 'request_code', 1, 1,),
    ('login_reward', (                        ), 1, 1, 'login_reward', 0, 1,),
    ('box_reward_new', (                        ), 1, 1, 'box_reward_new', 1, 1,),
    ('box_reward', (                        ), 1, 1, 'box_reward_9', 0, 1,),
    ('box_reward_42', (                        ), 1, 1, 'box_reward_42', 0, 1,),
    ('box_reward_99999', (                        ), 1, 1, 'box_reward_99999', 0, 1,),
    ('box_reward_99994', (                        ), 1, 1, 'box_reward_99994', 0, 1,),
    ('box_reward_99967', (                        ), 1, 1, 'box_reward_99967', 0, 1,),
    ('box_reward_99861', (                        ), 1, 1, 'box_reward_99861', 0, 1,),
    ('box_reward_99833', (                        ), 1, 1, 'box_reward_99833', 0, 1,),
    ('box_reward_99810', (                        ), 1, 1, 'box_reward_99810', 0, 1,),
    ('box_reward_99792', (                        ), 1, 1, 'box_reward_99792', 0, 1,),
    ('gacha_reward_score', (                        ), 1, 1, 'gacha_reward_score', 0, 1,),
    ('guild_boss', (                        ), 1, 1, 'guild_boss', 1, 1,),
    ('guild_boss_reward', (                        ), 1, 1, 'guild_boss_reward', 0, 1,),
    ('item_integration', (                        ), 1, 1, 'item_integration', 0, 1,),
    ('ranking', (ranking_func,), 1, 1, 'ranking', 1, 1,),
    ('integration_shop', (                        ), 1, 1, 'Integration_shop', 1, 1,),
    ('reward_gacha', (reward_gacha_func,), 1, 1, 'reward_gacha', 0, 1,),
    ('gacha_score', (                        ), 1, 1, 'gacha_score', 1, 1,),
    ('gacha_gift', (                        ), 1, 1, 'gacha_gift', 1, 1,),
    ('loot_id', (                        ), 1, 1, 'loot_id', 0, 1,),
    ('integration_world', (                        ), 1, 1, 'integration_world', 1, 1,),
    ('auto_sweep', (auto_sweep_func,), 1, 1, 'auto_sweep', 1, 1,),
    ('logreward', (                        ), 1, 1, 'logreward', 0, 1,),
    ('treasure', (                        ), 1, 1, 'treasure', 1, 1,),
    ('map_treasure', (                     ), 1, 1, 'map_treasure', 1, 1,),
    ('map_treasure_detail_battle', (                     ), 1, 1, 'treasure_detail_battle', 1, 1,),
    ('map_treasure_battle_point', (                     ), 1, 1, 'treasure_battle_point', 0, 1,),
    ('player_boss', (                        ), 1, 1, 'player_boss', 1, 1,),
    ('scorewall', (                        ), 1, 1, 'scorewall', 0, 1,),
    ('one_piece', (                        ), 1, 1, 'one_piece', 1, 1,),
    ('one_piece_exchange', (                        ), 1, 1, 'one_piece_exchange', 1, 1,),
    ('one_piece_reduce', (                        ), 1, 1, 'one_piece_reduce', 1, 1,),
    ('one_piece_rate', (                        ), 1, 1, 'one_piece_rate', 1, 1,),
    ('one_piece_rank_reward', (                        ), 1, 1, 'one_piece_rank_reward', 1, 1,),
    ('server_one_piece', (                        ), 1, 1, 'server_one_piece', 1, 1,),
    ('server_one_piece_exchange', (                        ), 1, 1, 'server_one_piece_exchange', 1, 1,),
    ('server_one_piece_reduce', (                        ), 1, 1, 'server_one_piece_reduce', 1, 1,),
    ('server_one_piece_rate', (                        ), 1, 1, 'server_one_piece_rate', 1, 1,),
    ('server_one_piece_rank_reward', (                        ), 1, 1, 'server_one_piece_rank_reward', 1, 1,),
    ('roulette', (                        ), 1, 1, 'roulette', 1, 1,),
    ('roulette_rank_reward', (                        ), 1, 1, 'roulette_rank_reward', 1, 1,),
    ('roulette_ranktime', (                        ), 1, 1, 'roulette_ranktime', 0, 1,),
    ('roulette_reward', (                        ), 1, 1, 'roulette_reward', 1, 1,),
    ('server_roulette', (                        ), 1, 1, 'server_roulette', 1, 1,),
    ('server_roulette_rank_reward', (                ), 1, 1, 'server_roulette_rank_reward', 1, 1,),
    ('server_roulette_ranktime', (                   ), 1, 1, 'server_roulette_ranktime', 0, 1,),
    ('server_roulette_reward', (               ), 1, 1, 'server_roulette_reward', 1, 1,),
    ('daily_award_loop', (                        ), 1, 1, 'daily_award_loop', 1, 1,),
    ('super_rich', (super_rich_func,), 1, 1, 'super_rich', 1, 1,),
    ('super_all', (super_all_func,), 1, 1, 'super_all', 1, 1,),
    ('server_super_rich', (super_rich_func,), 1, 1, 'server_super_rich', 1, 1,),
    ('server_super_all', (super_all_func,), 1, 1, 'server_super_all', 1, 1,),
    ('omni_exchange', (make_timestamp_func,), 1, 1, 'omni_exchange', 1, 1,),
    ('server_exchange', (                      ), 1, 1, 'server_exchange', 1, 1,),
    ('active_recharge', (                        ), 1, 1, 'active_recharge', 1, 1,),
    ('server_active_recharge', (                        ), 1, 1, 'server_active_recharge', 1, 1,),
    ('active_show', (                        ), 1, 1, 'active_show', 1, 1,),
    ('recall_active_show', (                        ), 1, 1, 'recall_active_show', 1, 1,),
    ('book_character', (                        ), 1, 1, 'book_character', 1, 1,),
    ('book_equip', (                        ), 1, 1, 'book_equip', 1, 1,),
    ('face_icon', (                        ), 1, 1, 'face_icon', 1, 1,),
    ('limit_hero_score', (                        ), 1, 1, 'limit_hero_score', 1, 1,),
    ('limit_hero_rank', (                        ), 1, 1, 'limit_hero_rank', 0, 1,),
    ('limit_time_reward', (                        ), 1, 1, 'limit_time_reward', 0, 1,),
    ('bandit', (                        ), 1, 1, 'bandit', 1, 1,),
    ('server_bandit', (                        ), 1, 1, 'server_bandit', 1, 1,),
    ('tree_shop', (                        ), 1, 1, 'tree_shop', 1, 1,),
    ('equip_gacha', (                        ), 1, 1, 'equip_gacha', 1, 1,),
    ('equip_gacha_box', (                        ), 1, 1, 'equip_gacha_box', 0, 1,),
    ('equip_reward_gacha', (                     ), 1, 1, 'equip_reward_gacha', 0, 1,),
    ('equip_gacha_score', (                        ), 1, 1, 'equip_gacha_score', 1, 1,),
    ('equip_gacha_gift', (                        ), 1, 1, 'equip_gacha_gift', 1, 1,),
    ('equip_gacha_reward_score', (                        ), 1, 1, 'equip_gacha_reward_score', 0, 1,),
    ('equip_loot_id', (                        ), 1, 1, 'equip_loot_id', 0, 1,),
    ('group_show', (                        ), 1, 1, 'group_show', 1, 1,),
    ('group_score', (                        ), 1, 1, 'group_score', 1, 1,),
    ('group_shop', (group_shop_func,), 1, 1, 'group_shop', 1, 1,),
    ('group_rank', (group_rank_func,), 1, 1, 'group_rank', 1, 1,),
    ('gem', (                        ), 1, 1, 'gem', 1, 1,),
    ('group_version', (                        ), 1, 1, 'group_version', 1, 1,),
    ('server_group_show', (                        ), 1, 1, 'server_group_show', 1, 1,),
    ('server_group_score', (                        ), 1, 1, 'server_group_score', 1, 1,),
    ('server_group_shop', (group_shop_func,), 1, 1, 'server_group_shop', 1, 1,),
    ('server_group_rank', (group_rank_func,), 1, 1, 'server_group_rank', 1, 1,),
    ('server_group_version', (                        ), 1, 1, 'server_group_version', 1, 1,),
    ('mining', (                        ), 1, 1, 'mining', 0, 1,),
    ('deadandalive', (                        ), 1, 1, 'deadandalive', 1, 1,),
    ('enchant', (                        ), 1, 1, 'enchant', 1, 1,),
    ('foundation', (                       ), 1, 1, 'foundation', 1, 1,),
    ('reward_pk', (                        ), 1, 1, 'reward_pk', 1, 1,),
    ('server_inreview', (                       ), 1, 1, 'server_inreview', 1, 1,),
    ('server_hero', (                       ), 1, 1, 'server_hero', 1, 1,),
    ('server_foundation', (                       ), 1, 1, 'server_foundation', 1, 1,),
    ('server_limit_hero', (                       ), 1, 1, 'server_limit_hero', 1, 1,),
    ('server_limit_time', (                       ), 1, 1, 'server_limit_time', 1, 1,),
    ('exchange_card', (                       ), 1, 1, 'exchange_card', 1, 1,),
    ('auto_consume_reward', (                       ), 1, 1, 'auto_consume_reward', 0, 1,),
    ('guild_fight_buy', (                       ), 1, 1, 'guild_fight_buy', 1, 1,),
    ('new_world', (                       ), 1, 1, 'new_world', 1, 1,),
    ('contract', (                       ), 1, 1, 'contract', 1, 1,),
    ('contract_score_reward', (                       ), 1, 1, 'contract_score_reward', 1, 1,),
    ('contract_detail', (                       ), 1, 1, 'contract_detail', 1, 1,),
    ('contract_rate', (                       ), 1, 1, 'contract_rate', 1, 1,),
    ('contract_fire_cup', (                       ), 1, 1, 'contract_fire_cup', 1, 1,),
    ('contract_reduce', (                       ), 1, 1, 'contract_reduce', 1, 1,),
    ('contract_reward', (                       ), 1, 1, 'contract_reward', 1, 1,),
    ('server_contract', (                       ), 1, 1, 'server_contract', 1, 1,),
    ('server_contract_score_reward', (                       ), 1, 1, 'server_contract_score_reward', 1, 1,),
    ('server_contract_detail', (                       ), 1, 1, 'server_contract_detail', 1, 1,),
    ('server_contract_rate', (                       ), 1, 1, 'server_contract_rate', 1, 1,),
    ('server_contract_fire_cup', (                       ), 1, 1, 'server_contract_fire_cup', 1, 1,),
    ('server_contract_reduce', (                       ), 1, 1, 'server_contract_reduce', 1, 1,),
    ('server_contract_reward', (                       ), 1, 1, 'server_contract_reward', 1, 1,),
    ('maze_mine', (                       ), 1, 1, 'maze_mine', 1, 1,),
    ('maze_stage', (                       ), 1, 1, 'maze_stage', 1, 1,),
    ('maze_buff', (                       ), 1, 1, 'maze_buff', 1, 1,),
    ('maze_item', (                       ), 1, 1, 'maze_item', 1, 1,),
    ('maze_reward', (                       ), 1, 1, 'maze_reward', 1, 1,),
    ('maze_top_reward', (                       ), 1, 1, 'maze_top_reward', 1, 1,),
    ('pyramid_notice', (                       ), 1, 1, 'pyramid_notice', 1, 1,),
    ('pyramid', (                       ), 1, 1, 'pyramid', 1, 1,),
    ('pyramid_level', (                       ), 1, 1, 'pyramid_level', 1, 1,),
    ('pyramid_robot', (                       ), 1, 1, 'pyramid_robot', 1, 1,),
    ('pyramid_lucky', (                       ), 1, 1, 'pyramid_lucky', 1, 1,),
    ('pyramid_wanted', (                       ), 1, 1, 'pyramid_wanted', 1, 1,),
    ('escort_shop_free', (                       ), 1, 1, 'escort_shop_free', 1, 1,),
    ('escort_shop_charged', (                       ), 1, 1, 'escort_shop_charged', 1, 1,),
    ('escort_buff', (                       ), 1, 1, 'escort_buff', 1, 1,),
    ('escort_exchange', (                       ), 1, 1, 'escort_exchange', 1, 1,),
    ('escort_opentime', (                       ), 1, 1, 'escort_opentime', 1, 1,),
    ('escort_shop_charged_team', (                       ), 1, 1, 'escort_shop_charged_team', 1, 1,),
    ('escort_shop_free_team', (                       ), 1, 1, 'escort_shop_free_team', 1, 1,),
    ('escort_quality', (                       ), 1, 1, 'escort_quality', 1, 1,),
    ('pyramid_hatred', (                       ), 1, 1, 'pyramid_hatred', 1, 1,),
    ('escort_hatred', (                       ), 1, 1, 'escort_hatred', 1, 1,),
    ('hatred_formula', (                       ), 1, 1, 'hatred_formula', 1, 1,),
    ('player_recall', (                       ), 1, 1, 'player_recall', 1, 1,),
    ('recall_charge_reward', (                       ), 1, 1, 'recall_charge_reward', 1, 1,),
    ('new_word_reward', (                       ), 1, 1, 'new_word_reward', 1, 1,),
    ('active_consume', (                       ), 1, 1, 'active_consume', 1, 1,),
    ('active_inreview', (                       ), 1, 1, 'active_inreview', 1, 1,),
    ('worker', (                       ), 1, 1, 'worker', 1, 1,),
    ('seed', (                       ), 1, 1, 'seed', 1, 1,),
    ('farm_open', (                       ), 1, 1, 'farm_open', 1, 1,),
    ('super_evolution', (                       ), 1, 1, 'super_evolution', 1, 1,),
    ('wheel', (                       ), 1, 1, 'wheel', 1, 1,),
    ('vip_wheel_reward', (                       ), 1, 1, 'vip_wheel_reward', 1, 1,),
    ('bounty_order', (                       ), 1, 1, 'bounty_order', 1, 1,),
    ('bounty_reward', (                       ), 1, 1, 'bounty_reward', 1, 1,),
    ('bounty_detail', (                       ), 1, 1, 'bounty_detail', 1, 1,),
    ('equip_refine', (                       ), 1, 1, 'equip_refine', 1, 1,),
    ('pet_detail', (                       ), 1, 1, 'pet_detail', 1, 1,),
    ('pet_strengthen', (                       ), 1, 1, 'pet_strengthen', 1, 1,),
    ('pet_base', (                       ), 1, 1, 'pet_base', 1, 1,),
    ('pet_evolution', (                       ), 1, 1, 'pet_evolution', 1, 1,),
    ('pet_corral', (                       ), 1, 1, 'pet_corral', 1, 1,),
    ('pet_skill_detail', (                       ), 1, 1, 'pet_skill_detail', 1, 1,),
    ('pet_skill_levelup', (                       ), 1, 1, 'pet_skill_levelup', 1, 1,),
    ('grow_gift', (                       ), 1, 1, 'grow_gift', 1, 1,),
    ('guild_level_reward', (                       ), 1, 1, 'guild_level_reward', 1, 1,),
    ('super_evo_team', (                       ), 1, 1, 'super_evo_team', 1, 1,),
    ('daily_new', (                       ), 1, 1, 'daily_new', 1, 1,),
    ('recall_mission', (                       ), 1, 1, 'recall_mission', 1, 1,),
    ('recall_time', (                       ), 1, 1, 'recall_time', 1, 1,),
    ('recall_reward', (                       ), 1, 1, 'recall_reward', 1, 1,),
    ('recall_seven', (                       ), 1, 1, 'recall_seven', 1, 1,),
    ('recall_coin', (                       ), 1, 1, 'recall_coin', 1, 1,),
    ('recall_active_recharge', (                       ), 1, 1, 'recall_active_recharge', 1, 1,),
    ('daily_score_new', (                       ), 1, 1, 'daily_score_new', 1, 1,),
    ('server_bounty_order', (                       ), 1, 1, 'server_bounty_order', 1, 1,),
    ('server_bounty_reward', (                         ), 1, 1, 'server_bounty_reward', 1, 1,),
    ('server_bounty_detail', (                       ), 1, 1, 'server_bounty_detail', 1, 1,),
    ('server_wheel', (                       ), 1, 1, 'server_wheel', 1, 1,),
    ('server_vip_wheel_reward', (                       ), 1, 1, 'server_vip_wheel_reward', 1, 1,),
    ('team_boss', (                       ), 1, 1, 'team_boss', 1, 1,),
    ('team_boss_reward', (                       ), 1, 1, 'team_boss_reward', 1, 1,),
    ('team_boss_exchange', (                       ), 1, 1, 'team_boss_exchange', 1, 1,),
    ('team_boss_score', (                       ), 1, 1, 'team_boss_score', 1, 1,),
    ('adventure_level', (                        ), 1, 1, 'adventure_level', 1, 1),
    ('adventure_stage', (                        ), 1, 1, 'adventure_stage', 1, 1),
    ('adventure_top_score', (                        ), 1, 1, 'adventure_top_score', 1, 1),
    ('adventure_exchange', (                        ), 1, 1, 'adventure_exchange', 1, 1),
    ('normal_exchange', (make_timestamp_func,), 1, 1, 'normal_exchange', 1, 1),
    ('redpacket', (                    ), 1, 1, 'redpacket', 1, 1),
    ('league_world', (                        ), 1, 1, 'league_world', 1, 1),
    ('league_time', (                        ), 1, 1, 'league_time', 1, 1),
    ('league_exchange', (                        ), 1, 1, 'league_exchange', 1, 1),
    ('league_reward', (                        ), 1, 1, 'league_reward', 1, 1),
    ('exchange_equip', (                           ), 1, 1, 'exchange_equip', 1, 1),
    ('exchange_equip_shop', (                           ), 1, 1, 'exchange_equip_shop', 1, 1),
    ('vip_reward', (                        ), 1, 1, 'vip_reward', 1, 1),
    ('team_pk_world', (                        ), 1, 1, 'team_pk_world', 1, 1),
    ('adver_pk', (adver_func,), 1, 1, 'adver_pk', 1, 1),
    ('team_pk_time', (                        ), 1, 1, 'team_pk_time', 1, 1),
    ('team_pk_reward', (                        ), 1, 1, 'team_pk_reward', 1, 1),
    ('team_pk_exchange', (                        ), 1, 1, 'team_pk_exchange', 1, 1),
    ('medal', (                        ), 1, 1, 'medal', 1, 1),
    ('material', (                        ), 1, 1, 'material', 1, 1),
    ('position', (                        ), 1, 1, 'position', 1, 1),
    ('super_commander_detail', (make_super_commander,), 1, 1, 'super_commander_detail', 1, 1),
    ('super_commander_tree', (                        ), 1, 1, 'super_commander_tree', 1, 1),
    ('hero_race', (                        ), 1, 1, 'hero_race', 1, 1),
    ('leader_base_mission', (                        ), 1, 1, 'leader_base_mission', 1, 1),
    ('leader_skill_advanced', (                        ), 1, 1, 'leader_skill_advanced', 1, 1),
    ('festival', (                        ), 1, 1, 'festival', 1, 1),
    ('festival_daily', (make_festival_daily,), 1, 1, 'festival_daily', 1, 1),
    ('festival_shop', (make_festival_shop,), 1, 1, 'festival_shop', 1, 1),
    ('festival_exchange', (make_festival_exchange,), 1, 1, 'festival_exchange', 1, 1),
    ('pet_follow', (                        ), 1, 1, 'pet_follow', 1, 1),
    ('server_link', (                        ), 1, 1, 'server_link', 1, 1),
    ('large_super_all', (                        ), 1, 1, 'large_super_all', 1, 1),
    ('large_super_rich', (super_rich_func,), 1, 1, 'large_super_rich', 1, 1),
    ('large_super_rich_all', (super_rich_func,), 1, 1, 'large_super_rich_all', 1, 1),
    ('large_roulette', (                        ), 1, 1, 'large_roulette', 1, 1,),
    ('large_roulette_reward', (                        ), 1, 1, 'large_roulette_reward', 1, 1,),
    ('large_pond', (                        ), 1, 1, 'large_pond', 0, 1,),
    ('equip_set_level', (                        ), 1, 1, 'equip_set_level', 1, 1),
    ('equip_set_random', (                        ), 1, 1, 'equip_set_random', 1, 1),
    ('equip_set_cost', (                        ), 1, 1, 'equip_set_cost', 1, 1),
    ('soul_detail', (                        ), 1, 1, 'soul_detail', 1, 1),
    ('soul_gacha', (                        ), 1, 1, 'soul_gacha', 1, 1),
    ('soul_exp', (                        ), 1, 1, 'soul_exp', 1, 1),
    ('fast_material_cost', (                        ), 1, 1, 'fast_material_cost', 1, 1),
    ('peak_arena_reward', (                        ), 1, 1, 'peak_arena_reward', 1, 1),
    ('peak_arena_shop', (                        ), 1, 1, 'peak_arena_shop', 1, 1),
    ('peak_arena_milestone', (                        ), 1, 1, 'peak_arena_milestone', 1, 1),
    ('rocker_machine', (                        ), 1, 1, 'rocker_machine', 1, 1),
    ('rocker_machine_reward', (                        ), 1, 1, 'rocker_machine_reward', 1, 1),
    ('score_reward', (                        ), 1, 1, 'score_reward', 1, 1),
    ('equip_set_rate', (                        ), 1, 1, 'equip_set_rate', 1, 1,),
    ('god_field_time', (                        ), 1, 1, 'god_field_time', 1, 1),
    ('god_field_fight_time', (                        ), 1, 1, 'god_field_fight_time', 1, 1),
    ('god_field_rank_reward', (                        ), 1, 1, 'god_field_rank_reward', 1, 1),
    ('god_field_exchange', (                        ), 1, 1, 'god_field_exchange', 1, 1),
    ('god_field_team', (                        ), 1, 1, 'god_field_team', 1, 1),
    ('temple_number', (                        ), 1, 1, 'temple_number', 1, 1),
    ('temple_num', (                        ), 1, 1, 'temple_num', 1, 1),
    ('temple_robot', (                        ), 1, 1, 'temple_robot', 1, 1),
    ('temple_formation', (                        ), 1, 1, 'temple_formation', 1, 1),
    ('pet_refresh', (                        ), 1, 1, 'pet_refresh', 1, 1,),
    ('clone_lane', (                        ), 1, 1, 'clone_lane', 1, 1,),
    ('afterlife', (                        ), 1, 1, 'afterlife', 1, 1,),
    ('afterlife_chapter', (                        ), 1, 1, 'afterlife_chapter', 1, 1,),
    ('afterlife_enemy', (                        ), 1, 1, 'afterlife_enemy', 1, 1,),
    ('afterlife_fight', (                        ), 1, 1, 'afterlife_fight', 1, 1,),
    ('new_vip_reward', (                        ), 1, 1, 'new_vip_reward', 1, 1,),
    ('red_bag', (                        ), 1, 1, 'red_bag', 1, 1,),
    ('system_red_bag', (                        ), 1, 1, 'system_red_bag', 1, 1,),
    ('gringotts', (                        ), 1, 1, 'gringotts', 1, 1,),
    ('gringotts_rate', (                        ), 1, 1, 'gringotts_rate', 1, 1,),
    ('gringotts_VIP', (                        ), 1, 1, 'gringotts_VIP', 1, 1,),
    ('new_rocker', (                        ), 1, 1, 'new_rocker', 1, 1,),
    ('new_rocker_reward', (                        ), 1, 1, 'new_rocker_reward', 1, 1,),
    ('server_pk_world', (                        ), 1, 1, 'server_pk_world', 1, 1,),
    ('server_pk_time', (                        ), 1, 1, 'server_pk_time', 1, 1,),
    ('server_pk_reward', (                        ), 1, 1, 'server_pk_reward', 1, 1,),
    ('server_pk_exchange', (                        ), 1, 1, 'server_pk_exchange', 1, 1,),
    ('version_reward', (                        ), 1, 1, 'version_reward', 1, 1,),
    ('role_attri_add', (                        ), 1, 1, 'role_attri_add', 1, 1,),
    ('godfield_arena_robot', (                        ), 1, 1, 'godfield_arena_robot', 0, 1,),
    ('godfield_arena', (                        ), 1, 1, 'godfield_arena', 1, 1,),
    ('godfield_arena_reward', (                        ), 1, 1, 'godfield_arena_reward', 1, 1,),
    ('godfield_arena_shop', (                        ), 1, 1, 'godfield_arena_shop', 1, 1,),
    ('godfield_formation', (                        ), 1, 1, 'godfield_formation', 0, 1,),
    ('new_fight_forever', (                        ), 1, 1, 'new_fight_forever', 1, 1,),
    ('new_fight_fight', (                        ), 1, 1, 'new_fight_fight', 1, 1,),
    ('new_fight_enemy', (                        ), 1, 1, 'new_fight_enemy', 1, 1,),
)


def generate_sub_func():
    """ 生成子函数

    :return:
    """
    global sub_func_config
    for config in config_name_list:
        sub_func = config[1]
        for sub in sub_func:
            if sub.func_name not in sub_func_config:
                sub_func_config[sub.func_name] = [config[0]]
            else:
                sub_func_config[sub.func_name].append(config[0])


generate_sub_func()


def load_single(config_name_tuple, cv_manager, config_type=1):
    """# load_single: docstring
    args:
        config_name:    ---    arg
    returns:
        0    ---
    """
    # _i = config_name_tuple
    config_key, config_sub_func, is_show_in_admin, is_modifable, xls_table_name, need_download, is_master = config_name_tuple

    if not is_modifable: return
    _c = ConfigManager.get_config_obj(config_key, config_type=config_type)

    if isinstance(_c.value, str) or isinstance(_c.value, unicode):
        globals()[config_key] = eval(_c.value)
    else:
        globals()[config_key] = _c.value
    if config_sub_func:
        for _f in config_sub_func:
            _f(config_key, _f.func_name, cv_manager)


def load_all(force=False):
    """# load_all: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    print_log('reload all')
    config_type = getattr(settings, 'CONFIG_TYPE', 1)

    cv = ConfigVersionManager.get_config_version_obj(config_type=getattr(settings, 'CONFIG_TYPE', 1))
    vers = cv.versions
    local_vers = globals().get('config_version', {})
    need_new_client_config_version = False
    if not local_vers:
        print 'no version, force loaded, ', local_vers
        force = True

    for _i in config_name_list:
        if _i[0] not in vers:
            vers[_i[0]] = 0
            # cv.save()
            cv.is_save = True
        if force or local_vers.get(_i[0]) != vers[_i[0]]:
            # local_vers[_i[0]] = vers[_i[0]]
            if _i[3]:
                load_single(_i, cv, config_type=config_type)
            need_new_client_config_version = True

    if getattr(cv, 'is_save', False):
        cv.save()

    # globals()['config_version'].update(local_vers)
    if need_new_client_config_version:
        globals()['config_version'] = vers
        make_client_config_version()

    # globals()['config_version'].update(cliver)


all_config_version = ''
client_config_version = {}


def make_client_config_list(client_config, cv):
    """ 创建客户端配置list


    :return:
    """
    for i in config_name_list:
        if i[0] not in [
                'map_title_detail',
                'map_title_detail_hell',
                'map_title_detail_purgatory',
                'building_base_school',
                'shop',
                'metal_core_shop',
                'code',
                'chain',
                'reward_once',
                'vip',
                'month_award',
                'equip',
                'equip_strongthen',
                'vip_shop',
                'skill_detail',
                'skill_levelup',
                'evolution_3',
                'vip_guide',
                'evolution_4',
                'evolution_5',
                'active_chapter',
                'hero_chapter',
                'star_reward',
                'opening',
                'pay',
                'character_detail',
                'character_strengthen',
                'character_train_time',
                'character_train_rate',
                'daily_award',
                'role',
                'suit',
                'level_gift',
                'loadingtips',
                'exchange',
                'box',
                'equip_exchange',
                'guide_team',
                'guide_manual',
                'online_award',
                'button_open',
                'wanted',
                'reward_daily',
                'dirt_shop',
                'equip_evolution',
                'drama',
                'fight_to_drama',
                'item',
                'random_last_name',
                'random_first_name',
                'adver',
                'adver_guild',
                'adver_inheritance',
                'server_adver',
                'month_award_coin',
                'month_award_coin_loop',
                'error',
                'reward_diary',
                'commander_type',
                'guide',
                'guide_button_open',
                'guide_button_open_new',
                'arena_shop',
                'reward_once',
                'character_break',
                'character_break_new',
                'break_control',
                'character_book',
                'equip_book',
                'integration_world',
                'active_detail',
                'character_exchange',
                'charge',
                'gacha',
                'active',
                'gacha_gift',
                'inreview',
                'notice_active',
                'loading',
                'auto_sweep',
                'request_code',
                'map_main_story',
                'middle_map',
                'middle_building_mine',
                'player_boss',
                'one_piece',
                'one_piece_exchange',
                'one_piece_rate',
                'one_piece_rank_reward',
                'server_one_piece',
                'server_one_piece_exchange',
                'server_one_piece_rate',
                'server_one_piece_rank_reward',
                'roulette',
                'roulette_rank_reward',
                'roulette_reward',
                'server_roulette',
                'server_roulette_rank_reward',
                'server_roulette_reward',
                'treasure',
                'map_treasure',
                'map_treasure_detail_battle',
                'daily_award_loop',
                'active_fight_forever',
                'omni_exchange',
                'server_exchange',
                'active_recharge',
                'server_active_recharge',
                'active_show',
                'recall_active_show',
                'super_rich',
                'super_all',
                'server_super_rich',
                'server_super_all',
                'book_equip',
                'book_character',
                'guild_funtion',
                'face_icon',
                'bandit',
                'server_bandit',
                'tree_shop',
                'guild_fight',
                'guild_GVGplayer',
                'guild_GVGmonster',
                'guild_GVGhome',
                'equip_gacha',
                'equip_gacha_gift',
                'group_show',
                'group_score',
                'group_shop',
                'group_rank',
                'group_version',
                'server_group_show',
                'server_group_score',
                'server_group_shop',
                'server_group_rank',
                'server_group_version',
                'deadandalive',
                'enchant',
                'foundation',
                'character_base',
                'occupation',
                'combat_skill',
                'gem',
                'commander_type',
                'commander_recipe',
                'reward_pk',
                'server_foundation',
                'server_inreview',
                'server_hero',
                'server_limit_hero',
                'exchange_card',
                'dailyscore',
                'guild_fight_buy',
                'new_world',
                'contract',
                'contract_score_reward',
                'contract_detail',
                'contract_rate',
                'contract_fire_cup',
                'contract_reduce',
                'contract_reward',
                'server_contract',
                'server_contract_score_reward',
                'server_contract_detail',
                'server_contract_rate',
                'server_contract_fire_cup',
                'server_contract_reduce',
                'server_contract_reward',
                'guild_shop',
                'whats_inside',
                'chapter',
                'chapter_mapping',
                'leader_skill',
                'maze_mine',
                'maze_stage',
                'maze_buff',
                'maze_item',
                'maze_reward',
                'maze_top_reward',
                'pyramid_notice',
                'pyramid',
                'pyramid_level',
                'pyramid_robot',
                'pyramid_lucky',
                'pyramid_wanted',
                'escort_shop_free',
                'escort_shop_charged',
                'escort_buff',
                'escort_exchange',
                'escort_opentime',
                'guild_shop_item',
                'leader_skill',
                'player_recall',
                'recall_reward',
                'recall_charge_reward',
                'race',
                'equip_st',
                'assistant',
                'destiny',
                'active_consume',
                'assistant_random',
                'limit_hero_score',
                'worker',
                'seed',
                'farm_open',
                'super_evolution',
                'cityid_cityorderid',
                'wheel',
                'vip_wheel_reward',
                'bounty_order',
                'bounty_reward',
                'bounty_detail',
                'server_limit_time',
                'equip_refine',
                'pet_detail',
                'pet_strengthen',
                'pet_base',
                'pet_evolution',
                'pet_corral',
                'pet_skill_detail',
                'pet_skill_levelup',
                'grow_gift',
                'arena_award',
                'guild_level_reward',
                'super_evo_team',
                'daily_new',
                'daily_score_new',
                'recall_mission',
                'recall_time',
                'recall_seven',
                'recall_coin',
                'recall_active_recharge',
                'server_bounty_order',
                'server_bounty_reward',
                'server_bounty_detail',
                'commander_level',
                'server_wheel',
                'server_vip_wheel_reward',
                'team_boss',
                'team_boss_reward',
                'team_boss_exchange',
                'team_boss_score',
                'adventure_level',
                'adventure_stage',
                'adventure_top_score',
                'adventure_exchange',
                'normal_exchange',
                'redpacket',
                'league_world',
                'league_time',
                'league_exchange',
                'league_reward',
                'exchange_equip',
                'exchange_equip_shop',
                'team_pk_world',
                'adver_pk',
                'team_pk_time',
                'team_pk_reward',
                'team_pk_exchange',
                'medal',
                'material',
                'position',
                'super_commander_detail',
                'super_commander_tree',
                'hero_race',
                'leader_base_mission',
                'leader_skill_advanced',
                'festival',
                'festival_daily',
                'festival_shop',
                'festival_exchange',
                'pet_follow',
                'server_link',
                'large_super_all',
                'large_super_rich',
                'large_super_rich_all',
                'equip_set_level',
                'equip_set_random',
                'equip_set_cost',
                'soul_detail',
                'soul_gacha',
                'soul_exp',
                'large_roulette',
                'large_roulette_reward',
                'large_pond',
                'active_inreview',
                'fast_material_cost',
                'peak_arena_reward',
                'peak_arena_shop',
                'peak_arena_milestone',
                'rocker_machine',
                'rocker_machine_reward',
                'score_reward',
                'equip_set_rate',
                'god_field_time',
                'god_field_fight_time',
                'god_field_rank_reward',
                'god_field_exchange',
                'god_field_team',
                'temple_number',
                'temple_num',
                'temple_robot',
                'pet_refresh',
                'clone_lane',
                'afterlife',
                'afterlife_chapter',
                'afterlife_enemy',
                'afterlife_fight',
                'new_vip_reward',
                'red_bag',
                'system_red_bag',
                'gringotts',
                'gringotts_rate',
                'gringotts_VIP',
                'new_rocker',
                'new_rocker_reward',
                'server_pk_world',
                'server_pk_time',
                'server_pk_reward',
                'server_pk_exchange',
                'week_award',
                'version_reward',
                'role_attri_add',
                'unify_ios_item',
                'unify_ios_box',
                'unify_android_item',
                'unify_android_box',
                'role_attri_add',
                'godfield_arena',
                'godfield_arena_reward',
                'godfield_arena_shop',
                'new_fight_forever',
                'new_fight_fight',
                'new_fight_enemy',
            ]:
            continue
        if i[5] and cv.get(i[0]):
            client_config[i[0]] = cv[i[0]]
    # TODO 为了暂时不让前端下载 enemy信息 @2014.06.07
    # for k, v in globals().iteritems():
    #    if k.startswith('enemy_soldier_') and not k == 'enemy_soldier_sub_func':
    #        client_config[k] = cv[k]
    keys = client_config.keys()
    keys.sort()
    l = []
    for k in keys:
        l.append(str(client_config[k]))

    return l


def make_client_config_version():
    """# make_client_config_version: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    l = make_client_config_list(client_config_version, globals()['config_version'])

    globals()['all_config_version'] = md5(''.join(l))


def make_client_config_version_for_test():
    """# make_client_config_version: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    client_config_version_for_test = {}
    for i in config_name_list:
        if i[5] and config_version.get(i[0]):
            client_config_version_for_test[i[0]] = config_version[i[0]]
    # for k, v in globals().iteritems():
    #     if k.startswith('enemy_soldier_') and not k == 'enemy_soldier_sub_func':
    #         client_config_version_for_test[k] = config_version[k]
    return all_config_version, client_config_version_for_test


load_all()


# 全局报错提示 以配置为准
return_msg_config = RMC.return_msg_config
for k, v in globals()['error'].iteritems():
    return_msg_config[k] = v['error_info']


# 获取级别不足的全局提示信息
def get_error_14_msg(lv):
    msg = return_msg_config.get('error_14') % lv
    return msg


def check_building_open(building):
    """ 检查建筑是否开启

    :param building:
    :return:
    """
    building_str = str(building)
    sort = globals()['map_title_detail_mapping'].get(building_str)
    if sort == "map_title_detail_base":
        return 0 in globals()['chapter_mapping']
    elif sort == "map_title_detail_hell":
        return 3 in globals()['chapter_mapping']
    elif sort == "map_title_detail_purgatory":
        return 4 in globals()['chapter_mapping']
    else:
        return True


def get_map_title_detail_config(building):
    building_str = str(building)
    sort = globals()['map_title_detail_mapping'].get(building_str)
    if sort == "map_title_detail_base":
        return globals()['map_title_detail'].get(building_str)
    elif sort == "map_title_detail_hell":
        return globals()['map_title_detail_hell'].get(building_str)
    elif sort == "map_title_detail_purgatory":
        return globals()['map_title_detail_purgatory'].get(building_str)
    else:
        return globals()['map_title_detail'].get(building_str)


city_building_step_data = {}


def city_building_step_mapping(city):
    """ city and building and step 对应关系

    :param city:
    :return:
    """
    global city_building_step_data
    city_data = city_building_step_data.get(city)
    if not city_data:
        buildings = globals()['map_mapping'].get(city, [])
        city_data = dict([(building, range(len(get_map_title_detail_config(building)['fight_list'])))] for building in buildings)
        city_building_step_data[city] = city_data

    return city_data


# 所有配置版本号除进程所加载的配置版本号
all_config_versions = {}
# 所有客户端版本号除进程所加载的配置版本号
all_client_config_versions = {}
# 获取所有配置,除进程加载的
all_configs = {}


def get_config_version(config_type):
    global all_config_versions
    global all_client_config_versions
    global all_configs

    config_version_obj = ConfigVersionManager.get_config_version_obj(config_type=config_type)

    if config_type in all_client_config_versions:
        if all_client_config_versions.get(config_type, {}) == config_version_obj.versions:
            return all_client_config_versions[config_type]

    def get_client_config_version():
        client_version = {}

        l = make_client_config_list(client_version, config_version_obj.versions)

        return client_version, md5(''.join(l))

    all_configs.pop(config_type, None)

    game_config_version, all_config_version = get_client_config_version()

    all_client_config_versions[config_type] = {
        'all_config_version': all_config_version,
        'game_config_version': game_config_version,
    }
    all_config_versions[config_type] = config_version_obj.versions
    return all_client_config_versions[config_type]


def get_config(server, config_name):
    """

    :param server:
    :param config_name:
    :return:
    """
    global all_configs

    config_type = settings.get_config_type(server)

    # config_type = settings.SERVERS.get(server, {}).get('config_type', 1)

    if config_type == getattr(settings, 'CONFIG_TYPE', 1):
        return globals()[config_name]

    get_config_version(config_type)

    config_value = all_configs.get(config_type, {}).get(config_name)

    if config_value:
        return config_value

    config_obj = ConfigManager.get_config_obj(config_name, config_type=config_type)
    # TODO 暂不支持config_sub_func方法
    if isinstance(config_obj.value, str) or isinstance(config_obj.value, unicode):
        value = eval(config_obj.value)
    else:
        value = config_obj.value

    if config_type in all_configs:
        all_configs[config_type][config_name] = value
    else:
        all_configs[config_type] = {config_name: value}

    return value


# 记录服务器配置
all_server_config = {}
def get_server_name(server_name):
    if not all_server_config.get(server_name, {}).get('name'):
        reload_server_config()
    return all_server_config.get(server_name, {}).get('name', server_name)


def reload_server_config():
    """ 加载服配置, 请根据需要增加字段, 现在支持name

    """
    global all_server_config

    sc = ServerConfig.get()
    for server, value in sc.config_value.iteritems():
        if server not in settings.SERVERS:
            continue
        all_server_config[server] = {'name': value['name'], 'is_open': value['is_open'],'open_time': value.get('open_time', -1)}


reload_server_config()


def get_server_config(server):
    server = settings.get_father_server(server)
    config = all_server_config.get(server, {})
    if not config.get('is_open'):
        reload_server_config()
        config = all_server_config.get(server, {})
    if not config:
        reload_server_config()
        config = all_server_config.get(server, {})
    return config


cache_formation_index_config = {}
def get_formation_index(current):
    global cache_formation_index_config
    index = cache_formation_index_config.get(current)
    if index is not None:
        return index
    if current not in globals()['formation']:
        current = 1
    formation_config = globals()['formation'][current]
    index = [v1 for k1, v1 in sorted([(k, v) for k, v in formation_config.iteritems() if 'position_' in k], key=lambda x: x[0])].index(0)
    cache_formation_index_config[current] = index
    return index