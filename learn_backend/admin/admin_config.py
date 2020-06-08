#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings

# 权限列表(自动与index匹配)
permissions = [
    {
        "code": "super",
        "description": u"超级管理权限,能干全部事情"
    }
]

# 基础页标签列表
base_page_list = ['/%s%s' % (settings.URL_PARTITION, x) for x in ['/admin/left/', '/admin/index/', '/admin/main/']]

# 左侧目录连接配置表
left_href = {
    'battle_test': {
        'path': '/%s/admin/battle_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'模拟战斗',
    },
    'gacha_test': {
        'path': '/%s/admin/gacha_test/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'模拟gacha',
    },
    'server_overview': {
        'path': '/%s/admin/server_overview/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'充值及在线总数'
    },
    'status_inquiry': {
        'path': '/%s/admin/status_inquiry/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'服务器运行查询'
    },
    'server_list': {
        'path': '/%s/admin/server_list/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'分服配置'
    },
    'config': {
        'path': '/%s/admin/config/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'游戏配置'
    },
    'user': {
        'path': '/%s/admin/user/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'用户'
    },
    'user_cards': {
        'path': '/%s/admin/user_cards/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'用户卡牌'
    },
    'skill': {
        'path': '/%s/admin/skill/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'上传技能'
    },
    'give_card': {
        'path': '/%s/admin/give_card/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送卡牌'
    },
    'give_equip': {
        'path': '/%s/admin/give_equip/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送装备'
    },
    'give_item': {
        'path': '/%s/admin/give_item/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送道具'
    },
    'give_seed': {
        'path': '/%s/admin/give_seed/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送无主之地的种子'
    },
    'give_material': {
        'path': '/%s/admin/give_material/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送勋章碎片'
    },
    'give_medal': {
        'path': '/%s/admin/give_medal/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送勋章'
    },
    'refresh_outlets': {
            'path': '/%s/admin/refresh_outlets/' % settings.URL_PARTITION,
            'target': 'content',
            'name': u'刷新限购商城'
    },
    'give_gem': {
        'path': '/%s/admin/give_gem/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'送觉醒宝石'
    },
    'give_pet': {
            'path': '/%s/admin/give_pet/' % settings.URL_PARTITION,
            'target': 'content',
            'name': u'送宠物'
    },
    'code_index': {
        'path': '/%s/admin/code_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'激活码'
    },
    'add_admin': {
        'path': '/%s/admin/add_admin/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'修改管理员'
    },
    'open_box_index': {
        'path': '/%s/admin/open_box_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'开宝箱'
    },
    'virtual_index': {
        'path': '/%s/admin/virtual_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'虚拟充值'
    },
    'sys_time_index': {
        'path': '/%s/admin/sys_time_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'修改系统时间'
    },
    'adminlog_index': {
        'path': '/%s/admin/adminlog_index/' % settings.URL_PARTITION,
        'target': 'content',
        'name': u'日志首页',
    },
}

# user页面下的二级页面路径,用于控制特殊管理员不能更改相应数据
secondary_links = {
    'code_': u'生成、显示激活码',
    "give_item_commit": u'赠送道具',
    "give_card_commit": u'赠送卡牌',
    "give_equip_commit": u'赠送装备',
    "give_gem_commit": u'赠送觉醒宝石',
    "open_positions": u'开启所有站位、卡牌可出战数量',
    "open_formations": u'开启所有阵型',
    "recapture_all_building": u'抢占所有城市',
    "del_card": u'删除用户卡牌',
    "upload": u'上传配置',
    "server_change": u'修改服务器设置',
    "server_config_type": u'查看nginx类型',
    "set_user_value": u'修改用户属性',
    "upload_skill": u'上传技能至服务器',
    "user_attr": u'查看用户各功能模块数据',
    "user_reset": u'重置用户 功能模块',
    "del_skill_script": u'删除技能脚本',
    "open_leader_skill": u'获得所有主角技能',
    "change_arena_rank": u'修改竞技场排名',
    "finish_all_guide": u'跳过新手引导',
    "virtual_pay": u'后台提交虚拟充值',
    "pay_person": u'用户充值查询',
    "pay_index": u'充值详情',
    "pay_day": u'每日充值详情',
    "send_notify": u'发送系统邮件',
    "ad_activate_count": u'ad激活',
    "export": u'导出用户数据',
    "spend_person": u'用户消费查询',
    "ad_youxiduo_count": u'ad游戏多激活',
    "del_item": u'删除玩家道具',
    "del_equip": u'删除玩家装备',
    "adminlog_search_by_name": u"日志查询",
    "adminlog_search_by_time": u"日志查询",
    "modify_admin": u"修改管理员",
    "search_approval": u"查询审批后的数据",
    "for_approval": u"进行审批",
    "approval_index": u"审批首页",
    "del_soul": u'删除玩家英魂',
    "limit_hero_rank": u'限时神将排名',
    "super_active_rank": u'宇宙最强排名',
    "refresh_enemy_uid": u'神域刷新敌人',
    "mv_account": u'替换账号',
    "modify_guild": u'修改自身公会异常数据',
}


# view method mapping permissions
# mappings: view函数映射关系
#     path: view path
#     index: 是否是管理后台的导航页面
#     permissions: 额外指定的权限列表

views_perms_mappings = {
    "index": [
        {
            "path": '/%s/admin/user/show/' % settings.URL_PARTITION,
            "name": '查看用户',
            "order": 0,
            "permissions": "show_user"
        },
        {
            "path": '/%s/admin/user/' % settings.URL_PARTITION,
            "name": '修改用户',
            "order": 0,
            "permissions": "edit_user",
        },
        {
            "path": '/%s/admin/game_setting/' % settings.URL_PARTITION,
            "name": '游戏设置',
            "order": 0,
            "permissions": "game_setting",
        },
        {
            "path": '/%s/admin/give_gifts/' % settings.URL_PARTITION,
            "name": '赠送礼物',
            "order": 0,
            "permissions": "give_gifts",
        },
        {
            "path": '/%s/admin/pk/' % settings.URL_PARTITION,
            "name": '技能测试',
            "order": 0,
            "permissions": "pk",
        },
        {
            "path": '/%s/admin/change_password/' % settings.URL_PARTITION,
            "name": '修改密码',
            "order": 0,
            "permissions": "change_password",
        },
        {
            "path": '/%s/admin/moderator/moderator_list/' % settings.URL_PARTITION,
            "name": '管理员管理',
            "order": 0,
            "permissions": "super",
        },
        {
            "path": '/%s/admin/paystat/mixi_pay/' % settings.URL_PARTITION,
            "name": '充值统计',
            "order": 0,
            "permissions": "mixi_pay",
        },
        {
            "path": '/%s/admin/logout/' % settings.URL_PARTITION,
            "name": '登出',
            "order": 0,
            "permissions": "all",
        }
    ],

    "mappings": [
        {
            "path": r'^/%s/admin/main/$' % settings.URL_PARTITION,
            "permissions": "all"
        }
    ]
}

# 管理后台安全校验码
ADMIN_SECRET_KEY = 's3avlj$=vk16op_s1g!xyilse9azcu&oh#wln8_@!b+_p7-+@='

# index更新, 自动添加相应权限管理
old_permissions = permissions[:]
def is_in_permissions(key,):
    for item in old_permissions:
        if key in ('all', item['code']):
            return True
    return False


for item in views_perms_mappings['index']:
    perm = item['permissions']
    if is_in_permissions(perm):
        continue
    permissions.append({
        "code": perm,
        "description": item["name"]
    })

# 获得视图所有KEY值
def get_all_href_key():
    # 全部视图
    term = left_href.copy()
    # del term['all']
    return term.keys()