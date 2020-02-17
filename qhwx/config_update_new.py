# -*- coding:utf-8 -*-
"""
@version: 0.0.1
@author: SevenCH
@license: 
@contact: MrSeven_Cheng@163.com
@site: https://github.com/MrSevenCheng
@software: PyCharm
@file: config_update.py
@time: 2019/11/15 10:35
"""
import os
import time

import numpy as np
import pandas as pd

from config import game_config

all_config_name_list = [
    'exp',  # 角色升官(经验)配置
    'gameparams',  # 基础配置
    'card',  # 幕僚配置
    'cardgold',  # 幕僚升级经验配置表
    'cardladder',  # 幕僚突破配置表
    'exp',  # 任务经验配置表
    'pve',  # 关卡配置表
    'npc',  # 关卡npc配置表
    'skill',  # 技能配置表
    'cardgold',  # 卡牌金币
    'harvest',  # 收获表
    'item',  # 道具表
    'box',  # 掉落包
    'combination',  # 合成表
    'prisoner',  # 犯人信息
    'judgement',  #
    'marketposition',  # 集市地图
    'marketprosperity',
    'marketbuildingup',
    'women',  # 红颜
    'womenskill',  # 红颜技能表
    'womenexp',  # 红颜亲密度相关表
    'womencomfortable',  # 厢房等级相关表
    'womenskillup',  # 红颜技能升级表
    'event',  # 事件表
    'marketpasserby',  # 集市npc信息表
    'childrenexp',  # 子嗣等级经验表
    'childrengraduate',  # 子嗣称号表
    'childrentalent',  # 子嗣天分表
    'chapter',  # 章节表
    'cardknowledge',  # 幕僚学识等级经验表
    'fashion',  # 时装配置表
    'affairs',  # 政务配表
    'maskword',  # 关键字屏蔽表
    'debatematch',  # 论战匹配规则
    'debatelottery',  # 论战战斗连胜奖励
    'store',  # 商店配置
    'storegoods',  # 商店商品配置
    'vip',  # 用户vip数据
    'advancement',  # 晋升阁道具
    'recharge',  # 充值
    'gift',  # 拜访道具
    'giftget',  # 好感度奖励
    'banquet',  # 设宴表
    'banquetgoto',  # 赴宴表
    'mail',  # 邮件类型表
    'fortune',  # 官运
    'activity',  # 活动表
    'activity1',  # 充值活动奖励配置表
    'activity2',  # 活动奖励配置表
    'leaguebuild',  # 联盟建设
    'leaguetechnology',  # 联盟科技
    'leaguebox',  # 联盟活跃度宝箱
    'leagueexp',  # 联盟升级所需经验
    'activity_reward_mapping',  # 活动ID,奖励ID匹配表
    'recharge_activity_reward_mapping',  # 充值活动ID,奖励ID匹配表
    'task',  # 任务
    'dailytaskbox',  # 日常任务宝箱奖励
    'debatelottery',  # 校场连胜奖励
    'sevenday',  # 七日登录
    'redbag',  # 红包
    'leaguefightreward',  # 联盟战奖励
    'beacon',  # 剿匪表
    'beaconbossrank',  # 烽火台Boss
    'beaconstrengthen',  # 强化弩炮
    'guide',  # 新手引导
    'noticelamp',  # 跑马灯
    'resourcestring',  # 犯人名称头像表
    "openmodule",  # 模块开启表
    "story",  # 剧情表
    "gossip",  # 流言蜚语信息
    "leveltask",  # 升官任务数据
    "moneytreeitem",  # 摇钱树商城条目信息
    "moneytree",  # 摇钱树
    "moneytreerank1",
    "moneytreerank2",
    "hit",  # 打板子
    "signingroup",  # 连续签到奖励类型组的定义
    "signin",  # 连续签到奖励数据
    "moneytreestage",  # 摇钱树阶段奖励
    "moneytreeexchange",  # 摇钱树积分兑换道具
    "vipstore",  # vip商店
    "moneytreeshop",  # 摇钱树商店
    "activitypurchasegift",  # 直购
    "activitynewpurchasegift",  # 直购
    "advancementweekgift",  # 晋升阁结算奖励信息
    "activitynewfund",  # 直购基金
    "activityfund",  # 直购基金
    "appearance",  # 府邸建筑装饰表
    "cardofficer",  # 佐官
    "womentitle",  # 红颜位分
    "leaguedailytask",  # 联盟日常任务
    "cg",  # cg剧情奖励
    "storyreward",  # 剧情选项奖励
    "robot",  # 机器人
]

special_config = ['party_config', 'party_confidant_config', 'money_tree_theme_daily_reward', 'operate_act_user_max_rank_reward_config']
party_confidant_config = {}  # {派系ID: [红颜ID]}        哪些红颜影响这个派系
party_config = {}  # {派系ID: [幕僚ID]}        哪些幕僚属于一个派系
money_tree_theme_daily_reward = {}  # 活动主题每日奖励信息
operate_act_user_max_rank_reward_config = {}  # type: dict[int, int]# 运营活动用户最大奖励排行配置


def check_all_files(check_path, file_ext=''):
    list_files = []
    # 列出文件夹下所有的目录与文件
    cur_list = os.listdir(check_path)
    for i in range(0, len(cur_list)):
        file_path = os.path.join(check_path, cur_list[i])
        if os.path.isdir(file_path):
            list_files.extend(check_all_files(file_path, file_ext))
        if os.path.isfile(file_path):
            if file_ext != '':
                if file_path[len(file_ext) * -1:] == file_ext:
                    list_files.append([cur_list[i], file_path])
            else:
                list_files.append([cur_list[i], file_path])
    return list_files


def write_config(file_name, config_date):
    """
    :param file_name: 文件名
    :param config_date: 配置数据
    :return:
    """
    dic_config = {}
    if file_name == 'gameparams':
        for key, value in dic.items():
            dic_config[key] = value['num']
    else:
        dic_config = config_date

    path_str = path_config + '/' + file_name + '.py'
    fo = open(path_str, "w")
    # str = "{0} = {1}".format('game_config_' + file_name, dic_config)
    str = "{0} = {1}".format(file_name, dic_config)
    fo.write(str)


mapping_type = {
    'int': 'int',
    'string': 'str',
    'float': 'float64',
    'object': 'object',
    'stringlist': 'str',
    'array': 'str'

}

path_config = os.path.join(str(os.path.abspath(os.path.join(os.getcwd(), "../.."))), "config", "config_file")

if __name__ == "__main__":
    path = os.path.join(str(os.path.abspath(os.path.join(os.getcwd(), "../.."))), "confparser", "xlsxfile")
    path = r"%s" % path
    file_list = check_all_files(path, 'csv')
    print('start -------------------------------------')

    def time2stamp(a):
        timeArray = time.localtime(int(a))
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    for file in file_list:
        file_path = r"%s" % file[1]
        file_name = file[0].split('.')[0]
        df = pd.DataFrame(pd.read_csv(file_path))
        df['6'] = df['6'].apply(time2stamp)
        df.to_csv('/tmp/pycharm_project_60/confparser/xlsxfile/new.csv', encoding='utf-8')

    #     print(file_name)
    #     if file_name not in all_config_name_list:
    #         continue
    #     df = pd.DataFrame(pd.read_excel(file_path))
    #     columns_list = df.columns.values.tolist()
    #     type_config = df.iloc[1].tolist()
    #     dic_1 = dict(zip(columns_list, type_config))
    #     # df.rename(columns=dic_1, inplace=True)
    #     df.drop([0, 1], inplace=True)
    #     df.reset_index(drop=True, inplace=True)
    #     num = 0
    #     for i in columns_list:
    #         try:
    #             df[i] = df[i].astype(dtype=mapping_type[type_config[num]])
    #             num += 1
    #         except Exception as e:
    #             print(e)
    #     # if True in list(df.isnull().any()):
    #     #     break
    #     # df_1[item] = df_1[item].astype(dtype='float64')
    #     try:
    #         if file_name == 'gameparams':
    #             df.drop(['id', 'name'], axis=1, inplace=True)
    #             df.set_index(keys="field", inplace=True)
    #         else:
    #             df.set_index(keys="id", inplace=True)
    #     except Exception as e:
    #         print(e)
    #     df.replace(to_replace=np.NaN, value='', inplace=True)
    #     df = df.T
    #     dic = df.to_dict()
    #     write_config(file_name, dic)
    #
    # for config_name in special_config:
    #     if config_name == 'party_config':  # 幕僚属于哪一类派系
    #         for key, val in game_config.card.items():
    #             party_id = int(val['party'])
    #             if party_config.get(party_id):
    #                 party_config[party_id].append(key)
    #             else:
    #                 party_config[party_id] = [key]
    #         write_config("party_config", party_config)
    #
    #     if config_name == 'party_confidant_config':  # 哪些红颜影响幕僚派系
    #         for key, val in game_config.women.items():
    #             party_ids = map(int, str(val['partycard']).split(','))
    #             for party_id in party_ids:
    #                 if party_confidant_config.get(party_id):
    #                     party_confidant_config[party_id].append(key)
    #                 else:
    #                     party_confidant_config[party_id] = [key]
    #         write_config("party_confidant_config", party_confidant_config)
    #
    #     if config_name == 'money_tree_theme_daily_reward':
    #         for key, val in game_config.moneytreeshop.items():
    #             if val["freenum"] < 1:
    #                 continue
    #             theme_id = val["groupid"]
    #             money_tree_theme_daily_reward.setdefault(theme_id, {}).update({val["itemid"]: val["freenum"]})
    #         write_config("money_tree_theme_daily_reward", money_tree_theme_daily_reward)
    #
    #     if config_name == 'operate_act_user_max_rank_reward_config':
    #         for key, val in game_config.moneytreerank1.items():
    #             group_id = int(val["groupid"])
    #             config_max_rank = int(val["rankpara"].split(",")[1])
    #             if config_max_rank > operate_act_user_max_rank_reward_config.get(group_id, 0):
    #                 operate_act_user_max_rank_reward_config[group_id] = config_max_rank
    #         write_config("operate_act_user_max_rank_reward_config", operate_act_user_max_rank_reward_config)


    print('end -------------------------------------')

    # df.to_csv("/tmp/pycharm_project_60/confparser/item.csv", encoding="utf-8")
    # df.to_csv(path_config + '/' + str(file_name) + ".csv", encoding="utf-8")
    # reload(game_config)
