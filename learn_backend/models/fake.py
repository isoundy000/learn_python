#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import new
import time
import copy
import weakref
import random
import game_config

from lib.utils import merge_dict
from lib.utils.debug import print_log


def EmptyObj(name='Request', base=None, d=None, **karg):
    ''' 生成一个新的空对象
        name --- 类的名字
        base --- 类的父类
        d --- namespace dict
    '''
    if not base:
        base = (object,)
    if not isinstance(base, tuple):
        base = (base,)
    if not d:
        d = {}
    return new.classobj(name, base, d)(**karg)


def empty_func(*args, **kwargs):
    '''
    空函数
    :param args:
    :param kwargs:
    :return:
    '''
    pass


empty_method = empty_func.__call__      # 空函数


def EmptyModelObj(raw_class, uid, server_name):
    """# EmptyModelObj: docstring 返回一个空对象
    args:
        raw_class:    ---    arg
    returns:
        0    ---
    """
    obj = raw_class(uid)
    obj.get = empty_func
    obj.save = empty_func
    obj._server_name = server_name
    return obj


def fake_card_skill(card_info, skill_num):
    """# fake_skill: docstring 伪造的卡牌技能信息
    args:
        card_info, :    ---    arg    card_info卡牌信息  skill_name: skill1、skill2
    returns:
        0    ---
    """
    if card_info.get(skill_num):
        return {
            'lv': card_info[skill_num][1],
            'exp': 0,
            's': int(card_info[skill_num][0]),
            'avail': 2
        }
    else:
        return {
            'lv': 1,
            'exp': 1,
            's': 0,
            'avail': 0,
        }


def fake_card_info(card_config_id, c_id, card_info):
    """# fake_card: 伪造卡牌信息
    args:
        card_info:    ---    arg        card_config_id: 10021p1, c_id: 10021 敌人信息
    returns:
        0    ---
    """
    c = card_info
    return {
        'id': card_config_id,
        'c_id': c_id,
        'lv': card_info['lv'],
        'exp': 0,
        'pos': 0,
        's_1': fake_card_skill(c, 'skill1'),
        's_2': fake_card_skill(c, 'skill2'),
        's_3': fake_card_skill(c, 'skill3'),
        's_4': fake_card_skill(c, 'skill4'),
        's_5': fake_card_skill(c, 'skill5'),
        'patk': c['patk'],      # 物攻
        'matk': c['matk'],      # 魔攻
        'def': c['def'],
        'speed': c['speed'],
        'hp': c['hp'],
        'is_boss': c['is_boss'],    # 是否是boss
        'level_max': 99,
        'quality': 5,
        'star': 5,
        'hr': c.get('hr', 95),  # 命中，若配置没上则用以前默认值，下同
        'dr': c.get('dr', 0),  # 闪避
        'subhurt': min(c.get('subhurt', 0), 100),  # 减伤，上限100
        'crit': c.get('crit', 10),  # 暴击
        'race': c['race'],      # 种族
        'career': c['career'],  # 职业
        'animation': c['animation'],    # 动画
        'rgb_sort': c['rgb_sort'],
        'fire': c.get('fire', 0),
        'water': c.get('water', 0),
        'wind': c.get('wind', 0),
        'earth': c.get('earth', 0),
        'fire_dfs': c.get('fire_dfs', 0),
        'water_dfs': c.get('water_dfs', 0),
        'wind_dfs': c.get('wind_dfs', 0),
        'earth_dfs': c.get('earth_dfs', 0),
    }


def fake_single_card_info(card_obj):
    """# fake_single_card_info: docstring 伪造卡牌信息
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    self = card_obj
    def fname(card_dict, **kwargs):
        """# fname: docstring
        args:
            arg:    ---    arg
        returns:
            0    ---
        """
        if isinstance(card_dict, (int, basestring)):    # 数字或者字符串
            card_dict = self._cards[card_dict]          # 获取卡牌中的信息 self == card_obj
        return card_dict
    return fname


def fake_single_pets_info(pets_obj):
    """# fake_single_pets_info: docstring  伪造宠物卡牌信息
    args:
        arg:    ---    arg
    returns:
        0    ---
    """
    self = pets_obj
    def fname(pets_dict, **kwargs):
        """# fname: docstring
        args:
            arg:    ---    arg
        returns:
            0    ---
        """
        if isinstance(pets_obj, (int, basestring)):
            pets_dict = self._pets[pets_dict]
        return pets_dict

    return fname


def map_battle_user(fight_id, fight_config, sort=1):
    """# battle_user: docstring 生产地图块战斗数据
    args:
        user_config:    ---    arg
    returns:
        0    ---
    """
    if sort == 1:
        enemy_config = game_config.enemy_all
    else:
        enemy_config = game_config.afterlife_enemy

    # 首发
    cards = {}
    alignment_1 = [-1] * 5                          # 战斗位置
    alignment_2 = [-1] * 5
    for i in xrange(1, 6):
        card_id = fight_config['position' + str(i)]
        if card_id:
            c_id = str(card_id)
            enemy_info = enemy_config[str(card_id)]
            card_id = str(card_id) + 'p%d' % i
            card_info = fake_card_info(card_id, c_id, enemy_info)
            cards[card_info['id']] = card_info      # 卡牌id: card_info
            card_info['pos'] = i                    # 1-5 卡牌出战位置
            alignment_1[i - 1] = card_info['id']    # 战斗位置

    for i in xrange(1, 6):
        card_id = fight_config['alternate' + str(i)]
        if card_id:
            c_id = str(card_id)
            enemy_info = enemy_info[str(card_id)]
            card_id = str(card_id) + 'a%d' % i
            card_info = fake_card_info(card_id, c_id, enemy_info)
            cards[card_info['id']] = card_info
            card_info['pos'] = i + 10               # 替补11-15
            alignment_2[i - 1] = card_info['id']

    card_obj = EmptyObj(name="MapEnemyCard", d={
        'uid': fight_id,                            # 战斗的人 第几场战斗
        'alignment': [alignment_1, alignment_2],    # 出战|替补
        'add_exp': empty_method,                    # 增加经验空函数
        '_cards': cards,                            # 卡牌信息
        'formation': {
            'current': fight_config['formation_id'],    # 当前阵型
            'own': [fight_config['formation_id']]       # 自己拥有的阵型
        },
        'assistant': ['-1'] * 9,                    # 助威
        'destiny': ['-1'] * 9,                      # 命运
    })
    setattr(card_obj, 'single_card_info', fake_single_card_info(card_obj))

    skill_obj = EmptyObj(name="MapEnemySkill", d={
        'uid': fight_id,
        'skill': {},
    })

    user_obj = EmptyObj(name="MapEnemy", d={
        'uid': fight_id,
        'level': 1,
        'role': 0,
        'exp': 0,
        'food': 0,
        'skill': skill_obj,
        'cards': card_obj,
        'HAS_LEADER': False,        # 是否是主角
    })

    # 剧情传递
    if fight_id in game_config.fight_to_drama:
        _drama = game_config.fight_to_drama[fight_id]
        setattr(user_obj, 'pve_drama', _drama)      # 设置人打机器人打剧情
    # getattr(user_obj, 'drama', None)
    return user_obj


def new_fight_forever_battle_user(fight_id, fight_config):
    '''
    新的战斗
    :param fight_id: 战斗id
    :param fight_config: 战斗配置
    :return:
    '''
    enemy_config = game_config.new_fight_enemy

    # 首发
    cards = {}
    alignment_1 = [-1] * 5
    alignment_2 = [-1] * 5
    for i in xrange(1, 6):
        card_id = fight_config['position' + str(i)]
        if card_id:
            c_id = str(card_id)
            enemy_info = enemy_config[str(card_id)]
            card_id = str(card_id) + 'p%d' % i
            card_info = fake_card_info(card_id, c_id, enemy_info)
            cards[card_info['id']] = card_info
            card_info['pos'] = i
            alignment_1[i - 1] = card_info['id']

    for i in xrange(1, 6):
        card_id = fight_config['alternate' + str(i)]
        if card_id:
            c_id = str(card_id)
            enemy_info = enemy_config[str(card_id)]
            card_id = str(card_id) + 'a%d' % i
            card_info = fake_card_info(card_id, c_id, enemy_info)
            cards[card_info['id']] = card_info
            card_info['pos'] = i + 10
            alignment_2[i - 1] = card_info['id']

    card_obj = EmptyObj(name="MapEnemyCard", d={
        'uid': fight_id,
        'alignment': [alignment_1, alignment_2],
        'add_exp': empty_method,
        '_cards': cards,
        'formation': {
            'current': fight_config['formation_id'],
            'own': [fight_config['formation_id']]
        },
        'assistant': ['-1'] * 9,
        'destiny': ['-1'] * 9,
    })
    setattr(card_obj, 'single_card_info', fake_single_card_info(card_obj))

    skill_obj = EmptyObj(name="MapEnemySkill", d={
        'uid': fight_id,
        'skill': {},
    })

    user_obj = EmptyObj(name="MapEnemy", d={
        'uid': fight_id,
        'level': 1,
        'role': random.choice(range(1, 5)),         # 角色头像随机
        'exp': 0,
        'food': 0,
        'skill': skill_obj,
        'cards': card_obj,
        'HAS_LEADER': False,
    })
    # 剧情传递
    # if(fight_id in game_config.fight_to_drama):
    #    _drama = game_config.fight_to_drama[fight_id]
    #    setattr(user_obj, 'pve_drama', _drama)
    # getattr(user_obj, 'drama', None)
    return user_obj


def fake_get_skill_copy(skill_obj):
    """# fake_get_skill_copy: docstring 伪造技能的copy
    args:
        skill_obj:    ---    arg
    returns:
        0    ---
    """
    self = skill_obj
    def get_skill_copy():
        """
        得到技能数据副本
        """
        _base = {
            'skill': {      # 用户已经学会的主角技能，对应等级
                101: 1
            },
            'skill_1': 0,   # 用户装载的第一个技能，0表示没有
            'skill_2': 0,
            'skill_3': 0,
        }
        r = {}
        for k in _base.iterkeys():
            r[k] = getattr(self, k)
        return copy.deepcopy(r)
    return get_skill_copy


def robot_for_skill_test(uid, skill=None):
    """# robot_for_admin_test: docstring 机器人为了技能测试
    args:
        uid:    ---    arg
    returns:
        0    ---
    """
    enemy_config = {
        'enemy_name': unicode('''防爆警察丧尸''', 'utf-8'),
        'img': 'icon_fangbaojingcha.png',
        'animation': 'fangbaojingcha',
        'is_boss': 0,
        'race': 2,
        'career': 2,
        'patk': 1000,
        'matk': 1000,
        'def': 500,
        'speed': 200,
        'hp': 100000,
        'lv': 10,
        'skill1': [],
        'skill2': [],
        'skill3': [],
        'skill4': [],
        'skill5': [],
        'loot_charactar': [[1, 20], [2, 20]],   # 掉落的卡牌
        'loot_item': [[30001, 60]],             # 掉落的道具
        'loot_non': 100,
        'rgb_sort': 0,
    }

    # 首发
    cards = {}
    alignment_1 = [-1] * 5
    alignment_2 = [-1] * 5
    for i in xrange(1, 6):
        card_id = str(i)
        enemy_info = enemy_config               # 敌人信息
        card_info = fake_card_info(card_id, card_id, enemy_info)
        cards[card_info['id']] = card_info
        card_info['pos'] = i
        alignment_1[i - 1] = card_info['id']

    for i in xrange(1, 6):
        card_id = str(i + 10)
        enemy_info = enemy_config
        card_info = fake_card_info(card_id, card_id, enemy_info)
        cards[card_info['id']] = card_info
        card_info['pos'] = i + 10
        alignment_2[i - 1] = card_info['id']

    if skill is not None:
        cards[alignment_1[0]['s_1']] = {        # 第一个出战卡牌的第一个技能
            'lv': 1,
            'exp': 1,
            's': skill,
            'avail': 2,
        }

    card_obj = EmptyObj(name='MapEnemyCard', d={    # 地图块的卡牌
        'uid': uid,
        'alignment': [alignment_1, alignment_2],
        'add_exp': empty_method,
        '_cards': cards,
        'formation': {
            'current': 1,
        },
        'assistant': ['-1'] * 9,                # 助威
        'destiny': ['-1'] * 9,                  # 命运
    })
    setattr(card_obj, 'single_card_info', fake_single_card_info(card_obj))

    skill_obj = EmptyObj(name="MapEnemySkill", d={
        'uid': uid,
        'skill': {},
        'skill_1': 0,                           # 用户装载的第一个技能，0表示没有
        'skill_2': 0,
        'skill_3': 0,
    })
    setattr(skill_obj, 'get_skill_copy', fake_get_skill_copy(skill_obj))

    equip_pos = {}
    ass_equip_pos = {}
    for i in range(10):
        equip_pos[i] = [0] * 4                  # 出战卡牌的装备信息
        equip_pos[i + 100] = [0] * 4

    equip_obj = EmptyObj(name='MapEnemyEquip', d={  # 地图块的装备
        'uid': uid,
        '_equip': {},
        'equip_pos': equip_pos,
        'ass_equip_pos': ass_equip_pos,         # 助威装备
    })

    drama_obj = EmptyObj(name='MapEnemyDrama', d={
        'uid': uid,
        'checkFight': empty_func,
    })

    user_obj = EmptyObj(name="MapEnemy", d={
        'uid': uid,
        'name': u'我是英雄',
        'level': 1,
        'exp': 0,
        'role': 0,
        'food': 0,
        'skill': skill_obj,                     # 技能对象
        'cards': card_obj,                      # 卡牌对象
        'equip': equip_obj,                     # 装备对象
        'drama': drama_obj,                     # 剧情对象
        'HAS_LEADER': True,                     # 是否是主角
    })
    return user_obj


def robot(robot_uid, server_name, rank=0, spec_level=0, signal=None):
    """# robot: 产生一个很拟人的机器人
    args:
        arg:    ---    arg
        rank:    机器人排名，根据此排名随机相关属性
        spec_level:    指定卡牌、用户、技能 等的级别
        robot_config_name='robot'
    returns:
        0    ---
    formation_type_config = {
        'formation_id': 1,          # 阵型
        'position1': 3800,          # 出战卡牌
        'position2': 5300,
        'position3': 3000,
        'position4': 4100,
        'position5': 4000,
        'position6': 1400,          # 替补卡牌
        'position7': 4700,
        'position8': 1000,
    },
    robot_config = {
        'formation_type': [1,2,3,4,5,6,7,8,9,10],   #
        'role': 1,                  # 机器人头像
        'role_level': [41,50],      # 机器人等级
        'character_level': [67,85], # 卡牌等级
        'evo_level': [10,14],       # 进阶等级
        'skill_level': [22,23],     # 技能等级
        'leader_skill_1_key': 201,  # 主角技能的key
        'leader_skill_1_level': 5,  # 主角技能的等级
        'leader_skill_2_key': 212,
        'leader_skill_2_level': 5,
        'leader_skill_3_key': 232,
        'leader_skill_3_level': 4,
    }
    """
    uid = robot_uid
    rank = rank or int(robot_uid.split('_')[1])
    import game_config
    # robot_config = getattr(game_config, robot_config_name)[uid]
    if signal == 'new_arena':
        robot_config = game_config.godfield_arena_robot[uid]        # 神域的机器人
    else:
        robot_config = game_config.robot[uid]
    ######################################################
    # ## card
    from models.cards import Cards
    card_obj = EmptyModelObj(Cards, uid, server_name)

    formation_type = robot_config['formation_type'][rank % len(robot_config['formation_type'])]     # 1 % 10 求余数
    formation_config = game_config.formation_type[formation_type]   # 阵型信息 编队

    card_obj.formation = {
        'own': [formation_config['formation_id']],
        'current': formation_config['formation_id'],
    }

    tmp = {
        'skill_level': 1,
        'character_level': 1,
        'evo_level': 0,
        'role_level': 1,
    }

    if spec_level:
        tmp['character_level'] = spec_level
        tmp['role_level'] = spec_level
    else:
        for k in tmp:
            v = robot_config[k]
            v = range(v[1], v[0] - 1, -1)       # 50, 40  [50、49、...、40]
            v = v[rank % len(v)]
            tmp[k] = v

    for _ in range(1, tmp['role_level']):       # 角色等级
        card_obj.add_position_num(_)

    # 根据玩家等级限制上阵卡牌数量
    position_num = {'position_num': card_obj.position_num, 'alternate_num': card_obj.alternate_num}
    for i in range(1, 9):
        if i <= 5:
            _tp = 'position_num'
            pos = i
        else:
            _tp = 'alternate_num'
            pos = i + 5

        if position_num[_tp] <= 0:
            continue
        c_id = formation_config['position%s' % i]   # 编队卡牌
        if not c_id:
            continue
        card_id = card_obj.new(
            c_id,
            lv=tmp['character_level'],
            evo=tmp['evo_level'],
        )
        for _ in '12345':
            if 's_%s' % _ in card_obj._cards[card_id]:
                card_obj._cards[card_id]['s_%s' % _]['lv'] = tmp['skill_level']

        card_obj.set_alignment(card_id, pos)
        position_num[_tp] -= 1
        # ## card
        ######################################################

        ######################################################
        # ## leader_skill
        from models.skill import Skill
        leader_skill_obj = EmptyModelObj(Skill, uid, server_name)
        for i in '123':
            s = robot_config['leader_skill_%s_key' % i]
            s_level = robot_config['leader_skill_%s_level' % i]
            leader_skill_obj.skill[s] = s_level
            setattr(leader_skill_obj, 'skill_' + i, s)
        # ## leader_skill
        ######################################################

        ######################################################
        # ## equip
        from models.equip import Equip
        equip_obj = EmptyModelObj(Equip, uid, server_name)
        # ## equip
        ######################################################

        ######################################################
        # ## drama
        from models.drama import Drama
        drama_obj = EmptyModelObj(Drama, uid, server_name)
        # ## drama
        ######################################################

        #######################################################
        # ## user
        # uid
        # user_name
        # role
        # level
        # exp
        # ## user
        ######################################################

        ######################################################
        # ## arena
        from models.arena import Arena
        arena_obj = EmptyModelObj(Arena, uid, server_name)
        # ## arena
        ######################################################

        from models.user import User as UserM

        first_name = game_config.random_first_name[rank % len(game_config.random_first_name)]
        last_name = game_config.random_last_name[rank % len(game_config.random_last_name)]

        user_m = EmptyModelObj(UserM, uid, server_name)
        user_m.name = first_name + last_name
        user_m.role = robot_config['role']
        user_m.level = tmp['role_level']
        user_m.regist_time = time.time() - 3600 * 24 * 10   # 注册时间戳
        user_m.active_time = time.time() - 3600 * 2
        user_m.continue_login_days = 5

        from logics.user import User
        user = User(uid, user_m_obj=user_m)
        user.get = empty_func
        user.exp = user_m.exp
        for i in User._model_property_candidate_list:
            setattr(user, i[0], None)
        user.cards = card_obj
        setattr(card_obj, 'weak_user', weakref.proxy(user))
        user.equip = equip_obj
        setattr(equip_obj, 'weak_user', weakref.proxy(user))
        user.drama = drama_obj
        setattr(drama_obj, 'weak_user', weakref.proxy(user))
        user.leader_skill = leader_skill_obj
        setattr(leader_skill_obj, 'weak_user', weakref.proxy(user))
        user.arena = arena_obj
        setattr(arena_obj, 'weak_user', weakref.proxy(user))
        # ## user
        #######################################################

        return user


def pyramid_robot(robot_uid, robot_name, server_name, rank=0, spec_level=0, index=3, evo_level=0):
    """# robot: 产生一个很拟人的机器人  金字塔机器人
    args:
        arg:    ---    arg
        rank:    机器人排名，根据此排名随机相关属性
        spec_level:    指定卡牌、用户、技能 等的级别
        第三个参数  robot_config_name='robot'
    returns:
        0    ---
    formation_type_config = {
        'formation_id': 1,
        'position1': 3800,
        'position2': 5300,
        'position3': 3000,
        'position4': 4100,
        'position5': 4000,
        'position6': 1400,
        'position7': 4700,
        'position8': 1000,
    },
    robot_config = {
        'formation_type': [1,2,3,4,5,6,7,8,9,10],
        'role': 1,
        'role_level': [41,50],
        'character_level': [67,85],
        'evo_level': [10,14],
        'skill_level': [22,23],
        'leader_skill_1_key': 201,
        'leader_skill_1_level': 5,
        'leader_skill_2_key': 212,
        'leader_skill_2_level': 5,
        'leader_skill_3_key': 232,
        'leader_skill_3_level': 4,
    }
    """
    uid = robot_uid.split('_')[index]
    uid = int(uid)
    import game_config
    robot_config = game_config.pyramid_robot.get('robot_%s' % uid)
    ######################################################
    # ## card
    from models.cards import Cards
    card_obj = EmptyModelObj(Cards, robot_uid, server_name)
    if not robot_name:
        formation_type = robot_config['formation_type'][rank % len(robot_config['formation_type'])]
    else:
        formation_type = random.choice(robot_config['formation_type'])
    formation_config = game_config.formation_type.get(formation_type)
    card_obj.formation = {
        'own': [formation_config['formation_id']],
        'current': formation_config['formation_id'],
    }

    tmp = {
        'skill_level': 1,
        'character_level': 1,
        'evo_level': 0,
        'role_level': 1,
    }

    if spec_level:      # 指定卡牌、用户等级
        tmp['character_level'] = spec_level
        tmp['role_level'] = spec_level
        tmp['evo_level'] = evo_level
    else:
        for k in tmp:
            v = robot_config[k]
            v = range(v[1], v[0] - 1, -1)
            v = v[rank % len(v)]
            tmp[k] = v

    for _ in range(1, tmp['role_level']):
        card_obj.add_position_num(_)

    # 根据玩家等级限制上阵卡牌数量
    position_num = {'position_num': card_obj.position_num, 'alternate_num': card_obj.alternate_num}
    for i in range(1, 9):
        if i <= 5:
            _tp = 'position_num'
            pos = i
        else:
            _tp = 'alternate_num'
            pos = i + 5

        if position_num[_tp] <= 0:
            continue
        c_id = formation_config['position%s' % i]
        if not c_id:
            continue
        card_id = card_obj.new(
            c_id,
            lv=tmp['character_level'],
            evo=tmp['evo_level'],
        )
        for _ in '12345':
            if 's_%s' % _ in card_obj._cards[card_id]:
                card_obj._cards[card_id]['s_%s' % _]['lv'] = tmp['skill_level']

        card_obj.set_alignment(card_id, pos)
        position_num[_tp] -= 1
    # ## card
    ######################################################

    ######################################################
    # ## leader_skill
    from models.skill import Skill
    leader_skill_obj = EmptyModelObj(Skill, robot_uid, server_name)
    for i in '123':
        s = robot_config['leader_skill_%s_key' % i]
        s_level = robot_config['leader_skill_%s_level' % i]
        leader_skill_obj.skill[s] = s_level
        setattr(leader_skill_obj, 'skill_' + i, s)
    # ## leader_skill
    ######################################################

    ######################################################
    # ## equip
    from models.equip import Equip
    equip_obj = EmptyModelObj(Equip, robot_uid, server_name)
    # ## equip
    ######################################################

    ######################################################
    # ## drama
    from models.drama import Drama
    drama_obj = EmptyModelObj(Drama, robot_uid, server_name)
    # ## drama
    ######################################################

    #######################################################
    # ## user
    # uid
    # user_name
    # role
    # level
    # exp

    ######################################################
    # ## arena
    from models.arena import Arena
    arena_obj = EmptyModelObj(Arena, robot_uid, server_name)
    # ## arena
    ######################################################

    from models.user import User as UserM

    first_name = game_config.random_first_name[rank % len(game_config.random_first_name)]
    last_name = game_config.random_last_name[rank % len(game_config.random_last_name)]

    user_m = EmptyModelObj(UserM, robot_uid, server_name)
    # user_m.name = first_name + last_name
    user_m.name = robot_name or first_name + last_name
    user_m.role = robot_config['role']
    user_m.level = tmp['role_level']
    user_m.regist_time = time.time() - 3600 * 24 * 10  # 注册时间戳
    user_m.active_time = time.time() - 3600 * 2
    user_m.continue_login_days = 5

    from logics.user import User
    user = User(robot_uid, user_m_obj=user_m)
    user.get = empty_func
    user.exp = user_m.exp
    for i in User._model_property_candidate_list:
        setattr(user, i[0], None)
    user.cards = card_obj
    setattr(card_obj, 'weak_user', weakref.proxy(user))
    user.equip = equip_obj
    setattr(equip_obj, 'weak_user', weakref.proxy(user))
    user.drama = drama_obj
    setattr(drama_obj, 'weak_user', weakref.proxy(user))
    user.leader_skill = leader_skill_obj
    setattr(leader_skill_obj, 'weak_user', weakref.proxy(user))
    user.arena = arena_obj
    setattr(arena_obj, 'weak_user', weakref.proxy(user))
    # ## user
    #######################################################

    return user


def generate_temple_robot(robot_uid, server_name, formation_index, rank=0):
    """# robot: 产生一个很拟人的机器人
    """
    import game_config
    robot_int_id = int(robot_uid.split('_')[1])
    robot_config = game_config.temple_robot.get(robot_int_id)
    ######################################################
    # ## card
    from models.cards import Cards
    card_obj = EmptyModelObj(Cards, robot_uid, server_name)

    robot_name = robot_config['name']
    if not rank:
        rank = robot_int_id + robot_config['temple_reward']

    formation_type = robot_config['formation_type'][rank % len(robot_config['formation_type'])]

    formation_config = game_config.temple_formation.get(formation_type)

    card_obj.formation = {
        'own': [formation_config['formation_id']],
        'current': formation_config['formation_id'],
    }

    tmp = {
        'skill_level': 1,
        'character_level': 1,
        'evo_level': 0,
        'role_level': 1,
    }

    for k in tmp:
        v = robot_config[k]
        v = range(v[1], v[0] - 1, -1)
        v = v[rank % len(v)]
        tmp[k] = v

    for _ in range(1, tmp['role_level']):
        card_obj.add_position_num(_)

    # 根据玩家等级限制上阵卡牌数量
    position_num = {'position_num': card_obj.position_num, 'alternate_num': card_obj.alternate_num}

    formation_offset = (formation_index - 1) * 8

    for i in range(1, 9):
        if i <= 5:
            _tp = 'position_num'
            pos = i
        else:
            _tp = 'alternate_num'
            pos = i + 5

        if position_num[_tp] <= 0:
            continue
        c_id = formation_config['position%s' % (i + formation_offset)]
        if not c_id:
            continue
        card_id = card_obj.new(
            c_id,
            lv=tmp['character_level'],
            evo=tmp['evo_level'],
        )
        for _ in '12345':
            if 's_%s' % _ in card_obj._cards[card_id]:
                card_obj._cards[card_id]['s_%s' % _]['lv'] = tmp['skill_level']

        card_obj.set_alignment(card_id, pos)
        position_num[_tp] -= 1

    # ## card
    ######################################################

    ######################################################
    # ## leader_skill
    from models.skill import Skill
    leader_skill_obj = EmptyModelObj(Skill, robot_uid, server_name)
    for i in '123':
        s = robot_config['leader_skill_%s_key' % i]
        s_level = robot_config['leader_skill_%s_level' % i]
        leader_skill_obj.skill[s] = s_level
        setattr(leader_skill_obj, 'skill_' + i, s)
    # ## leader_skill
    ######################################################

    ######################################################
    # ## equip
    from models.equip import Equip
    equip_obj = EmptyModelObj(Equip, robot_uid, server_name)
    # ## equip
    ######################################################

    ######################################################
    # ## drama
    from models.drama import Drama
    drama_obj = EmptyModelObj(Drama, robot_uid, server_name)
    # ## drama
    ######################################################
    #######################################################
    # ## user
    # uid
    # user_name
    # role
    # level
    # exp

    ######################################################
    # ## arena
    from models.arena import Arena
    arena_obj = EmptyModelObj(Arena, robot_uid, server_name)
    # ## arena
    ######################################################

    from models.user import User as UserM

    user_m = EmptyModelObj(UserM, robot_uid, server_name)
    user_m.name = robot_name
    user_m.role = robot_config['role']
    user_m.level = tmp['role_level']
    user_m.regist_time = time.time() - 3600 * 24 * 10  # 注册时间戳
    user_m.active_time = time.time() - 3600 * 2
    user_m.continue_login_days = 5

    from logics.user import User
    user = User(robot_uid, user_m_obj=user_m)
    user.get = empty_func
    user.exp = user_m.exp
    for i in User._model_property_candidate_list:
        setattr(user, i[0], None)
    user.cards = card_obj
    setattr(card_obj, 'weak_user', weakref.proxy(user))
    user.equip = equip_obj
    setattr(equip_obj, 'weak_user', weakref.proxy(user))
    user.drama = drama_obj
    setattr(drama_obj, 'weak_user', weakref.proxy(user))
    user.leader_skill = leader_skill_obj
    setattr(leader_skill_obj, 'weak_user', weakref.proxy(user))
    user.arena = arena_obj
    setattr(arena_obj, 'weak_user', weakref.proxy(user))
    # ## user
    #######################################################

    return user


class EquipClass():
    '''装备类'''
    def __init__(self, data):
        self.data = data

    def __call__(self, equip_id, *args, **kwargs):
        return self.data.get(equip_id, {})


class EquipSuitClass():
    '''装备套装类'''
    def __init__(self, data):
        self.data = data

    def __call__(self, pos, *args, **kwargs):
        return self.data.get(pos, {})


class EquipDecreaseClass():
    '''装备减少属性'''
    def __init__(self, data):
        self.data = data

    def __call__(self, equip_id, equip_forge, *args, **kwargs):
        d = self.data.get(equip_id, {})
        if d:
            for k, v in d.iteritems():
                if k not in equip_forge:        # equip_forge装备锻造
                    equip_forge[k] = {}
                merge_dict(equip_forge[k], v)
        return equip_forge


class SkillClass():
    '''技能的类'''
    def __init__(self, data):
        self.data = data

    def __call__(self, *args, **kwargs):
        return self.data


def fake_data_for_user(user):
    """ 从user对象构建数据

    :param user:
    :return:
    """
    _cards = {}
    # 阵型上的卡牌信息
    alignment = user.cards.alignment
    for ali in alignment:
        for card_id in ali:
            if card_id in user.cards._cards:
                _cards[card_id] = user.cards.single_card_info(card_id, for_battle=True)
    # 加入助威的卡信息
    for card_id in user.cards.assistant:
        if card_id in user.cards._cards:
            _cards[card_id] = user.cards.single_card_info(card_id, for_battle=True)
    # 加入命运的卡信息
    for card_id in user.cards.destiny:
        if card_id in user.cards._cards:
            _cards[card_id] = user.cards.single_card_info(card_id, for_battle=True)
    cards_data = {
        '_cards': _cards,   # 卡牌信息
        'formation': user.cards.formation,      # 数据库中关于阵型的记录, 数据结构
        'assistant': user.cards.assistant,
        'assistant_effect': user.cards.assistant_effect,    # 计算助威效果
        'destiny': user.cards.destiny,
        'alignment': alignment,
        'open_position': user.cards.open_position,  # 当前已开启站位
    }

    skill_data = {
        'get_skill_copy': user.skill.get_skill_copy(),
    }

    equip_data = {
        'equip_pos': user.equip.equip_pos,
        'ass_equip_pos': user.equip.ass_equip_pos
    }
    all_equip = user.equip.get_all_equip_pos(is_formation=False)
    equip_single_info = {}
    for equip_id in all_equip:
        equip_single_info[equip_id] = user.equip.single_info(equip_id)
    decrease = {}
    for equip_id in user.equip.get_equip_pos():
        decrease[equip_id] = user.equip.attack_and_defender_attr_point(equip_id)
    equip_data['suit_effect'] = user.equip.suit_effects()
    equip_data['single_info'] = equip_single_info
    equip_data['decrease'] = decrease

    pets_single_info = {}
    for pet_id in user.pets.pet_pos:
        if pet_id not in ['0', '-1']:
            pets_single_info[pet_id] = user.pets.single_pet_info(pet_id)

    pets_data = {
        'pet_pos': user.pets.pet_pos,
        '_pets': pets_single_info,
    }

    data = {
        'cards': cards_data,
        'equip': equip_data,
        'skill': skill_data,
        'pets': pets_data,
        'commander': {},        # 统帅
        'role': user.role,
        'name': user.name,
        'uid': user.uid,
        'server_name': user.user_m._server_name,
        'combat': user.combat,
    }

    return copy.deepcopy(data)


def fake_user_for_data(data):
    """ 从数据构建user对象

    :param user:
    :param data:
    """
    uid = data['uid']

    cards = data['cards']

    server_name = data['server_name']

    # 卡牌
    card_obj = EmptyObj(name="MapEnemyCard", d={
        'uid': uid,
        'NONE_CARD_ID_FLAG': '-1',
        'alignment': cards['alignment'],
        'add_exp': empty_method,
        '_cards': cards['_cards'],
        'formation': cards['formation'],
        'assistant': cards['assistant'],
        'assistant_effect': cards.get('assistant_effect', {'active_status': '-1'}),
        'destiny': cards.get('destiny', ['-1'] * 9),
        'open_position': cards.get('open_position', []),
        '_server_name': server_name,
    })
    setattr(card_obj, 'single_card_info', fake_single_card_info(card_obj))

    skill = data['skill']

    # 技能
    skill_obj = EmptyObj(name="MapEnemySkill", d={
        'uid': uid,
        'get_skill_copy': SkillClass(skill['get_skill_copy']),  # 获取技能的类
        '_server_name': server_name,
    })

    # 装备
    equip = data['equip']

    equip_obj = EmptyObj(name='MapEnemyEquip', d={
        'uid': uid,
        'equip_pos': equip['equip_pos'],
        'ass_equip_pos': equip.get('ass_equip_pos', {}),
        'single_info': EquipClass(equip['single_info']),
        'suit_effect': EquipSuitClass(equip.get('suit_effect', {})),
        'attack_and_defender_attr_point': EquipDecreaseClass(equip.get('decrease', {})),
        '_equip': equip['single_info'],
        '_server_name': server_name,
    })

    pets = data.get('pets', {})

    pets_obj = EmptyObj(name='MapEnemyPets', d={
        'uid': uid,
        'pet_pos': pets.get('pet_pos', []),
        '_pets': pets.get('_pets', {}),
    })
    setattr(pets_obj, 'single_pet_info', fake_single_pets_info(pets_obj))

    # 战斗剧情
    drama_obj = EmptyObj(name='MapEnemyDrama', d={
        'uid': uid,
        'checkFight': empty_func,
        'completionFight': empty_func,
        '_server_name': server_name,
    })

    user_obj = EmptyObj(name="MapEnemy", d={
        'uid': uid,
        'name': data['name'],
        'level': data['level'],
        'exp': 0,
        'role': data['role'],
        'skill': skill_obj,
        'cards': card_obj,
        'equip': equip_obj,
        'drama': drama_obj,
        'pets': pets_obj,
        'HAS_LEADER': True,
        'association_name': data.get('association_name', ''),   # 工会名字
        'combat': data.get('combat', 0),
        '_server_name': server_name,
        'vip': 0,
    })

    return user_obj



def god_arena_robot(robot_uid, server_name, rank=0, spec_level=0, signal=None, formation_index=1):
    """# robot: 产生一个神域竞技场机器人
    """
    uid = robot_uid
    rank = rank or int(robot_uid.split('_')[1])
    import game_config
    if signal == 'new_arena':
        robot_config = game_config.godfield_arena_robot[uid]
    else:
        robot_config = game_config.robot[uid]
    ######################################################
    # ## card
    from models.cards import Cards
    card_obj = EmptyModelObj(Cards, uid, server_name)

    formation_type = robot_config['formation_type'][rank % len(robot_config['formation_type'])]
    formation_config = game_config.godfield_formation[formation_type]

    card_obj.formation = {
        'own': [formation_config['formation_id']],
        'current': formation_config['formation_id'],
    }

    tmp = {
        'skill_level': 1,
        'character_level': 1,
        'evo_level': 0,
        'role_level': 1,
    }
    if spec_level:  # 指定卡牌、用户等级
        tmp['character_level'] = spec_level
        tmp['role_level'] = spec_level
    else:
        for k in tmp:
            v = robot_config[k]
            v = range(v[1], v[0] - 1, -1)
            v = v[rank % len(v)]
            tmp[k] = v

    for _ in range(1, tmp['role_level']):
        card_obj.add_position_num(_)

    # 根据玩家等级限制上阵卡牌数量
    position_num = {'position_num': card_obj.position_num, 'alternate_num': card_obj.alternate_num}

    formation_offset = (formation_index - 1) * 8

    for i in range(1, 9):
        if i <= 5:
            _tp = 'position_num'
            pos = i
        else:
            _tp = 'alternate_num'
            pos = i + 5

        if position_num[_tp] <= 0:
            continue
        c_id = formation_config['position%s' % (i + formation_offset)]
        if not c_id:
            continue
        card_id = card_obj.new(
            c_id,
            lv=tmp['character_level'],
            evo=tmp['evo_level'],
        )
        for _ in '12345':
            if 's_%s' % _ in card_obj._cards[card_id]:
                card_obj._cards[card_id]['s_%s' % _]['lv'] = tmp['skill_level']

        card_obj.set_alignment(card_id, pos)
        position_num[_tp] -= 1
    # ## card
    ######################################################

    ######################################################
    # ## leader_skill
    from models.skill import Skill
    leader_skill_obj = EmptyModelObj(Skill, uid, server_name)
    for i in '123':
        s = robot_config['leader_skill_%s_key' % i]
        s_level = robot_config['leader_skill_%s_level' % i]
        leader_skill_obj.skill[s] = s_level
        setattr(leader_skill_obj, 'skill_' + i, s)
    # ## leader_skill
    ######################################################

    ######################################################
    # ## equip
    from models.equip import Equip
    equip_obj = EmptyModelObj(Equip, uid, server_name)
    # ## equip
    ######################################################

    ######################################################
    # ## drama
    from models.drama import Drama
    drama_obj = EmptyModelObj(Drama, uid, server_name)
    # ## drama
    ######################################################

    #######################################################
    # ## user
    # uid
    # user_name
    # role
    # level
    # exp

    ######################################################
    # ## arena
    from models.arena import Arena
    arena_obj = EmptyModelObj(Arena, uid, server_name)
    from models.god_arena import GodArena as GArena
    god_arena_obj = EmptyModelObj(GArena, uid, server_name)
    # ## arena
    ######################################################

    from models.user import User as UserM

    first_name = game_config.random_first_name[rank % len(game_config.random_first_name)]
    last_name = game_config.random_last_name[rank % len(game_config.random_last_name)]

    user_m = EmptyModelObj(UserM, uid, server_name)
    user_m.name = first_name + last_name
    user_m.role = robot_config['role']
    user_m.level = tmp['role_level']
    user_m.regist_time = time.time() - 3600 * 24 * 10  # 注册时间戳
    user_m.active_time = time.time() - 3600 * 2
    user_m.continue_login_days = 5

    from logics.user import User
    user = User(uid, user_m_obj=user_m)
    user.get = empty_func
    user.exp = user_m.exp
    for i in User._model_property_candidate_list:
        setattr(user, i[0], None)
    user.cards = card_obj
    setattr(card_obj, 'weak_user', weakref.proxy(user))
    user.equip = equip_obj
    setattr(equip_obj, 'weak_user', weakref.proxy(user))
    user.drama = drama_obj
    setattr(drama_obj, 'weak_user', weakref.proxy(user))
    user.leader_skill = leader_skill_obj
    setattr(leader_skill_obj, 'weak_user', weakref.proxy(user))
    user.arena = arena_obj
    setattr(arena_obj, 'weak_user', weakref.proxy(user))
    user.god_arena = god_arena_obj
    setattr(god_arena_obj, 'weak_user', weakref.proxy(user))
    # ## user
    #######################################################

    return user