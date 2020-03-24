#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
现在新加入excel配置label(sheet)内容检测机制, 方法是在一般的config_template的空字典后再加一个可选的的列表(optional)，列表里可放置1个或多个配置表内容检测函数。
这些检测函数是对单张配置表的整体内容进行逻辑正确性检测。
如要使用此功能，需要在/backend/admin/upload/lable_check.py文件里增加同名的检测函数，否则会导致报错。

样例:

    def sample_template():
        return [
            ('id',        "    %s:{                       ",    'int'),
            ('version',    "   'version':    %s,    ",    'int'),
            ('END',               "    },                         ",    'None'),
        ], {}, ['content_check_func_1', 'content_check_func_2']

上例中的`['content_check_func_1', 'content_check_func_2']`就是内容检测函数列表

                                                    Juchen.Zeng 2015-11-26 17:13
"""

import settings

from admin.upload.check import *


def filter_tuple_6(s):
    return not """ (0, '', '', 0, False, 0), """ in s


def filter_tuple_3(s):
    return not """ (0, '', ''), """ in s


def filter_tuple(s):
    return not """ (0, 0), """ in s


def filter_exp(s):
    return ' 0,' not in s


def filter_str(s):
    return """ '', """ not in s


def filter_tuple_str_int(s):
    return not '''('', 1),''' in s


def filter_tuple_str_str_int(s):
    return not ''' 0, '',  '', 0,''' in s


def map_main_story():
    t = [
        ('order_ID', """'%s': {                   """, 'int'),
        ('stage_ID', """ 'stage_id'          : %s, """, 'str'),
        ('open_level', """ 'open_level'        : %s, """, 'int'),
        ('chapter', """ 'chapter'               : %s, """, 'int'),
        ('tmx', """ 'tmx'               : %s, """, 'str'),
        ('stage_name', """ 'stage_name'        : %s, """, 'unicode'),
        ('stage_story', """ 'stage_story'       : %s, """, 'unicode'),
        ('wanted', """ 'wanted'        : %s, """, 'int_list'),
        ('jingyingfirst', """ 'jingyingfirst'        : %s, """, 'int_list'),
        ('jingyingsweep', """ 'jingyingsweep'        : %s, """, 'int_list'),
        ('END', """ },                        """, 'None'),
    ]
    return t, {}


def fight_common():
    t = [
        ('fight_ID',             """'%s': {                      """ , 'int'),
        ('fight_boss',           """    'fight_boss'  : %s,          """ , 'str'),
        ('formation_id',         """    'formation_id'  : %s,        """ , 'int'),
        ('position1',            """    'position1'  : %s,           """ , 'int_list'),
        ('position2',            """    'position2'  : %s,           """ , 'int_list'),
        ('position3',            """    'position3'  : %s,           """ , 'int_list'),
        ('position4',            """    'position4'  : %s,           """ , 'int_list'),
        ('position5',            """    'position5'  : %s,           """ , 'int_list'),
        ('alternate1',           """    'alternate1' : %s,           """ , 'int_list'),
        ('alternate2',           """    'alternate2' : %s,           """ , 'int_list'),
        ('alternate3',           """    'alternate3' : %s,           """ , 'int_list'),
        ('alternate4',           """    'alternate4' : %s,           """ , 'int_list'),
        ('alternate5',           """    'alternate5' : %s,           """ , 'int_list'),
        ('team_rage',            """    'team_rage ' : %s,           """ , 'int'),
        ('enemy_rage',           """    'enemy_rage' : %s,           """ , 'int'),
        ('reward_exp_role',      """    'reward_exp_role'      : %s, """ , 'int'),
        ('reward_exp_character', """    'reward_exp_character' : %s, """ , 'int'),
        ('END',                  """},                               """ , 'None'),
    ]
    return t, {
    }

fight_boss = fight_common
fight_boss_hell = fight_common
fight_boss_purgatory = fight_common
fight_active = fight_common
fight_treasure = fight_common
fight_hero = fight_common
fight_common_hell = fight_common
fight_common_purgatory = fight_common


def map_title_detail_common():
    return [
        ('title_id',         """'%s': {                      """ , 'int'),
        ('title_img',        """    'title_img'            : %s, """ , 'str'),
        ('background',       """    'background'           : %s, """ , 'str'),
        ('loot_show',       """    'loot_show'             : %s, """ , 'str'),
        ('after_show',       """    'after_show'           : %s, """ , 'str'),
        ('max_sweep',        """    'max_sweep'            : %s, """ , 'int'),
        ('reward_first_base', """    'reward_first_base'   : %s, """ , 'int_list'),
        ('reward_first_rate', """    'reward_first_rate'   : %s, """ , 'int_list'),
        ('reward_sweep_base', """    'reward_sweep_base'   : %s, """ , 'int_list'),
        ('reward_sweep_rate', """    'reward_sweep_rate'   : %s, """ , 'int_list'),
        ('title_name',       """    'title_name'           : %s, """ , 'unicode'),
        ('title_name_after', """    'title_name_after'     : %s, """ , 'unicode'),
        ('title_detail',     """    'title_detail'         : %s, """ , 'unicode'),
        ('fight',            """    'fight_list'           : %s, """ , 'unicode_int_list'),
        ('action_point',     """    'action_point'         : %s, """ , 'int'),
        ('title_level',      """    'title_level'          : %s, """ , 'int'),
        ('title_x',          """    'title_x'              : %s, """ , 'int'),
        ('title_y',          """    'title_y'              : %s, """ , 'int'),
        ('END',              """},                           """ , 'None'),
    ], {}

map_title_detail_base = map_title_detail_common
map_title_detail_guild = map_title_detail_common
map_title_detail_hell = map_title_detail_common
map_title_detail_purgatory = map_title_detail_common


def enemy_soldier():
    return [
        ('enemy_ID',       """%s: {                   """ , 'str'),
        ('enemy_name',     """ 'enemy_name'     : %s, """ , 'unicode'),
        ('rgb_sort',       """ 'rgb_sort'          : %s, """, 'int'),
        ('img',            """ 'img'            : %s, """ , 'str'),
        ('animation',      """ 'animation'      : %s, """ , 'str'),
        ('is_boss',        """ 'is_boss'        : %s, """ , 'int'),
        ('race',           """ 'race'           : %s, """ , 'int'),
        ('career',         """ 'career'         : %s, """ , 'int'),
        ('patk',           """ 'patk'           : %s, """ , 'int'),
        ('matk',           """ 'matk'           : %s, """ , 'int'),
        ('def',            """ 'def'            : %s, """ , 'int'),
        ('speed',          """ 'speed'          : %s, """ , 'int'),
        ('hp',             """ 'hp'             : %s, """ , 'int'),
        ('lv',             """ 'lv'             : %s, """ , 'int'),
        ('skill1',         """ 'skill1'         : %s, """ , 'int_list'),
        ('skill2',         """ 'skill2'         : %s, """ , 'int_list'),
        ('skill3',         """ 'skill3'         : %s, """ , 'int_list'),
        ('loot_charactar', """ 'loot_character' : %s, """ , 'int_list'),
        ('loot_item',      """ 'loot_item'      : %s, """ , 'int_list'),
        ('loot_non',       """ 'loot_non'       : [-1, %s], """ , 'int'),
        ('hr',             """ 'hr'             : %s, """ , 'int'),
        ('dr',             """ 'dr'             : %s, """ , 'int'),
        ('subhurt',             """ 'subhurt'             : %s, """ , 'int'),
        ('crit',             """ 'crit'             : %s, """ , 'int'),
        ('fire',           """ 'fire'           : %s, """ , 'int'),
        ('water',          """ 'water'          : %s, """ , 'int'),
        ('wind',           """ 'wind'           : %s, """ , 'int'),
        ('earth',          """ 'earth'          : %s, """ , 'int'),
        ('fire_dfs',       """ 'fire_dfs'       : %s, """ , 'int'),
        ('water_dfs',      """ 'water_dfs'      : %s, """ , 'int'),
        ('wind_dfs',       """ 'wind_dfs'       : %s, """ , 'int'),
        ('earth_dfs',      """ 'earth_dfs'      : %s, """ , 'int'),
        ('END',            """},                     """ , 'None'),
    ], {}

enemy_essence = enemy_soldier
enemy_boss    = enemy_soldier
enemy_boss_hell = enemy_soldier
enemy_boss_purgatory = enemy_soldier
enemy_soldier_hell = enemy_soldier
enemy_soldier_purgatory = enemy_soldier
enemy_endless = enemy_soldier
enemy_endlessboss = enemy_soldier
enemy_activeboss = enemy_soldier
enemy_active = enemy_soldier
enemy_soldier_hard = enemy_soldier

enemy_boss_hard = enemy_soldier
enemy_hero = enemy_soldier

def error():
    return [(
             ('error_id', 'title', 'image', 'error_info',
              'button1', 'image1', 'button2', 'image2', 'button3', 'image3'),
             """  'error_%s': {
                     'title': %s,
                     'image': %s,
                     'error_info': %s,
                     'button1': %s, 'image1': %s,
                     'button2': %s, 'image2': %s,
                     'button3': %s, 'image3': %s,
             },
             """,
             ('int', 'str', 'str', 'unicode',
               'int_list', 'str', 'int_list', 'str', 'int_list', 'str',),
             )], {}

def character_exchange():
    return [(
            ('exchange_id', 'dirt_silver', 'dirt_gold',
                'item1', 'item2', 'item3', 'item4', 'item5'),
            """ %s: {'dirt_silver': %s, 'dirt_gold': %s,
                     'item': [%s, %s, %s, %s, %s] },""",
            ('int', 'int_list', 'int_list',
             'int_list', 'int_list', 'int_list', 'int_list', 'int_list')
            )
            ], {}

def character_break():
    return [
        ('character_ID', """%s: {                     """, 'str'),
        ('unique_id',   """    'unique_id'     : %s, """,   'int'),
        ('name',         """    'name'          : %s, """, 'unicode'),
        ('name1',         """    'name1'          : %s, """, 'unicode'),
        ('name2',         """    'name2'          : %s, """, 'unicode'),
        ('name3',         """    'name3'          : %s, """, 'unicode'),
        ('name4',         """    'name4'          : %s, """, 'unicode'),
        ('name5',         """    'name5'          : %s, """, 'unicode'),

        ('material1',     """    'material1'      : %s, """, 'int_list'),
        ('material2',     """    'material2'      : %s, """, 'int_list'),
        ('material3',     """    'material3'      : %s, """, 'int_list'),
        ('material4',     """    'material4'      : %s, """, 'int_list'),
        ('material5',     """    'material5'      : %s, """, 'int_list'),

        ('break_story1',  """    'break_story1'   : %s, """, 'unicode'),
        ('break_story2',  """    'break_story2'   : %s, """, 'unicode'),
        ('break_story3',  """    'break_story3'   : %s, """, 'unicode'),
        ('break_story4',  """    'break_story4'   : %s, """, 'unicode'),
        ('break_story5',  """    'break_story5'   : %s, """, 'unicode'),

        ('story_detail1',  """    'story_detail1'   : %s, """, 'unicode'),
        ('story_detail2',  """    'story_detail2'   : %s, """, 'unicode'),
        ('story_detail3',  """    'story_detail3'   : %s, """, 'unicode'),
        ('story_detail4',  """    'story_detail4'   : %s, """, 'unicode'),
        ('story_detail5',  """    'story_detail5'   : %s, """, 'unicode'),
        ('END', """},                                   """, 'None'),
    ], {}


def character_break_new():
    return [
        ('unique_id', """%s: {                     """, 'str'),
        ('character_ID',"""    'character_id'   : %s, """,   'int'),
        ('name',         """    'name'          : %s, """, 'unicode'),
        ('name1',         """    'name1'          : %s, """, 'unicode'),
        ('name2',         """    'name2'          : %s, """, 'unicode'),
        ('name3',         """    'name3'          : %s, """, 'unicode'),
        ('name4',         """    'name4'          : %s, """, 'unicode'),
        ('name5',         """    'name5'          : %s, """, 'unicode'),
        ('name6',         """    'name6'          : %s, """, 'unicode'),
        ('name7',         """    'name7'          : %s, """, 'unicode'),
        ('name8',         """    'name8'          : %s, """, 'unicode'),
        ('name9',         """    'name9'          : %s, """, 'unicode'),
        ('name10',         """    'name10'          : %s, """, 'unicode'),

        ('material1',     """    'material1'      : %s, """, 'int_list'),
        ('material2',     """    'material2'      : %s, """, 'int_list'),
        ('material3',     """    'material3'      : %s, """, 'int_list'),
        ('material4',     """    'material4'      : %s, """, 'int_list'),
        ('material5',     """    'material5'      : %s, """, 'int_list'),
        ('material6',     """    'material6'      : %s, """, 'int_list'),
        ('material7',     """    'material7'      : %s, """, 'int_list'),
        ('material8',     """    'material8'      : %s, """, 'int_list'),
        ('material9',     """    'material9'      : %s, """, 'int_list'),
        ('material10',     """    'material10'      : %s, """, 'int_list'),

        ('break_story1',  """    'break_story1'   : %s, """, 'unicode'),
        ('break_story2',  """    'break_story2'   : %s, """, 'unicode'),
        ('break_story3',  """    'break_story3'   : %s, """, 'unicode'),
        ('break_story4',  """    'break_story4'   : %s, """, 'unicode'),
        ('break_story5',  """    'break_story5'   : %s, """, 'unicode'),
        ('break_story6',  """    'break_story6'   : %s, """, 'unicode'),
        ('break_story7',  """    'break_story7'   : %s, """, 'unicode'),
        ('break_story8',  """    'break_story8'   : %s, """, 'unicode'),
        ('break_story9',  """    'break_story9'   : %s, """, 'unicode'),
        ('break_story10',  """    'break_story10'   : %s, """, 'unicode'),

        ('story_detail1',  """    'story_detail1'   : %s, """, 'unicode'),
        ('story_detail2',  """    'story_detail2'   : %s, """, 'unicode'),
        ('story_detail3',  """    'story_detail3'   : %s, """, 'unicode'),
        ('story_detail4',  """    'story_detail4'   : %s, """, 'unicode'),
        ('story_detail5',  """    'story_detail5'   : %s, """, 'unicode'),
        ('story_detail6',  """    'story_detail6'   : %s, """, 'unicode'),
        ('story_detail7',  """    'story_detail7'   : %s, """, 'unicode'),
        ('story_detail8',  """    'story_detail8'   : %s, """, 'unicode'),
        ('story_detail9',  """    'story_detail9'   : %s, """, 'unicode'),
        ('story_detail10',  """    'story_detail10'   : %s, """, 'unicode'),

        ('high_break',  """    'high_break'   : %s, """, 'int'),

        ('END', """},                                   """, 'None'),
    ], {}


def break_control():
    return [
        ('break_step',     """%s: {                     """, 'int'),
        ('hp_add',         """    'hp_add'          : %s, """, 'float'),
        ('need_level',     """    'need_level'      : %s, """, 'int'),
        ('ability_sort',     """    'ability_sort'      : %s, """, 'int'),
        ('ability_add',     """    'ability_add'      : %s, """, 'int'),
        ('END', """},                                   """, 'None'),
    ], {}

def dirt_shop():
    return [(
            ('id', 'item', 'dirt_sort', 'value', 'weight', 'is_positive', 'show_level'),
            """  %s: { 'item': %s, 'dirt_sort': %s, 'value': %s, 'weight': %s, 'is_positive': %s, 'show_level': %s}, """,
            ('int', 'int_list', 'int', 'int', 'int', 'int', 'int_list')
            )], {}

def character_detail():
    return [
        ('unique_id',     """%s: {                     """ , 'int'),
        ('character_ID',  """ 'character_ID' : %s,      """ , 'str'),
        ('name',          """ 'name'         : %s,      """ , 'unicode'),
        ('short_story',   """ 'short_story'  : %s,      """ , 'unicode'),
        ('story',         """ 'story'        : %s,      """ , 'unicode'),
        ('img',           """ 'img'          : %s,      """ , 'str'),
        ('rgb_sort',      """ 'rgb_sort'          : %s, """ , 'int'),
        ('race',          """ 'race'         : %s,      """ , 'int'),
        ('career',        """ 'career'       : %s,      """ , 'int'),
        ('animation',     """ 'animation'    : %s,      """ , 'str'),
        ('wake1',         """ 'wake1'        : %s,      """ , 'adv_str_int_list'),
        ('wake2',         """ 'wake2'        : %s,      """ , 'adv_str_int_list'),
        ('wake3',         """ 'wake3'        : %s,      """ , 'adv_str_int_list'),
        ('wake4',         """ 'wake4'        : %s,      """ , 'adv_str_int_list'),
        ('wake5',         """ 'wake5'        : %s,      """ , 'adv_str_int_list'),
        ('wake6',         """ 'wake6'        : %s,      """ , 'adv_str_int_list'),
        ('is_notice',     """ 'is_notice'    : %s,      """ , 'int'),
        ('type',          """ 'type'         : %s,      """ , 'int'),
        ('is_only',       """ 'is_only'      : %s,      """ , 'int'),
        ('quality',       """ 'quality'      : %s,      """ , 'int'),
        ('star',          """ 'star'         : %s,      """ , 'int'),
        ('star_max',      """ 'star_max'     : %s,      """ , 'int'),
        ('level_max',     """ 'level_max'    : %s,      """ , 'int'),
        ('base_patk',     """ 'base_patk'    : %s,      """ , 'int'),
        ('base_matk',     """ 'base_matk'    : %s,      """ , 'int'),
        ('base_def',      """ 'base_def'     : %s,      """ , 'int'),
        ('base_speed',    """ 'base_speed'   : %s,      """ , 'int'),
        ('base_hp',       """ 'base_hp'      : %s,      """ , 'int'),
        ('growth_patk',   """ 'growth_patk'  : %s,      """ , 'int'),
        ('growth_matk',   """ 'growth_matk'  : %s,      """ , 'int'),
        ('growth_def',    """ 'growth_def'   : %s,      """ , 'int'),
        ('growth_speed',  """ 'growth_speed' : %s,      """ , 'int'),
        ('growth_hp',     """ 'growth_hp'    : %s,      """ , 'int'),
        ('evo_food',      """ 'evo_food'    : %s,       """ , 'int'),
        ('chain',      """ 'chain'    : %s,       """ , 'int_list'),
        ('is_evo',      """ 'is_evo'    : %s,       """ , 'int'),
        ('evo_kind',      """ 'evo_kind': %s,       """ , 'int'),
        ('rebirth',       """ 'rebirth':  %s,       """ , 'int'),
        ('skill1_source', """ 'skill_1_source' : %s,    """ , 'int_list'),
        ('skill2_source', """ 'skill_2_source' : %s,    """ , 'int_list'),
        ('skill4_source', """ 'skill_4_source' : %s,    """ , 'int_list'),
        ('skill5_source', """ 'skill_5_source' : %s,    """ , 'int_list'),
        ('exchange_id',   """ 'exchange_id'    : %s,    """ , 'int'),
        ('break4', """ 'break4' : %s,    """ , 'int_list'),
        ('break5', """ 'break5' : %s,    """ , 'int_list'),
        ('super_evo', """ 'super_evo' : %s,    """ , 'int'),
        ('END',           """ },                        """ , 'None'),
    ], {}

def occupation():
    return [
        (('animation', 'occupation'),  """    %s: %s, """, ('str', 'int')),
    ], {}

def random_name():
    """# random_name: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        (('last_name', 'first_name'), """    %s: %s, """, ('unicode', 'unicode')),
    ], {}



def character_base():
    return [
        ('level', """%s: {                                """, 'int'),
        ('exp', """    'exp'                      : %s, """, 'int'),
        ('eaten_skill_exp', """    'eaten_skill_exp'          : %s, """, 'int'),
        ('sell_food', """    'sell_food'                : %s, """, 'int'),
        ('skill_strengthen_food', """    'skill_strengthen_food'   : %s, """, 'int'),
        ('END', """},                                   """, 'None'),
    ], {}

def character_base_rate():
    return [
        ('type', """%s: {                                  """, 'int'),
        ('exp_rate', """   'exp_rate'                     :%s, """, 'float'),
        ('eaten_skill_exp_rate', """   'eaten_skill_exp_rate'         :%s, """, 'float'),
        ('sell_food_rate', """   'sell_food_rate'               :%s, """, 'int'),
        ('skill_strengthen_food_rate', """   'skill_strengthen_food_rate'  :%s, """, 'float'),
        ('END', """},                                     """, 'None'),
    ], {}


def role():
    return [
        ('level',           """%s: {                   """ , 'int'),
        ('exp',             """ 'exp'             :%s, """ , 'int'),
        ('point',           """ 'point'           :%s, """ , 'int'),
        ('recover_point',   """ 'recover_point'   :%s, """ , 'int'),
        ('PVP_point',       """ 'PVP_point'       :%s, """ , 'int'),
        ('character_max',   """ 'character_max'   :%s, """ , 'int'),
        ('equip_max',       """ 'equip_max'   :%s, """ , 'int'),
        ('guild_boss',      """ 'guild_boss'  :%s, """ , 'int'),
        ('position_num',       """ 'position_num'   :%s, """ , 'int'),
        ('alternate_num',       """ 'alternate_num'   :%s, """ , 'int'),
        ('open_middlemap',  """ 'open_middlemap'  :%s, """ , 'int'),
        ('close_middlemap', """ 'close_middlemap' :%s, """ , 'int'),
        ('harbor',          """ 'harbor'          :%s, """ , 'int'),
        ('school',          """ 'school'          :%s, """ , 'int'),
        ('factory',         """ 'factory'         :%s, """ , 'int'),
        ('hospital',        """ 'hospital'        :%s, """ , 'int'),
        ('laboratory',      """ 'laboratory'      :%s, """ , 'int'),
        ('news',            """ 'news'            :%s, """ , 'unicode'),
        ('helper',          """ 'helper'          :%s, """ , 'unicode'),
        ('get_exp_min',    """ 'get_exp_min' : %s,      """, 'int'),
        ('soul_max',    """ 'soul_max' : %s,      """, 'int'),
        ('END',             """},                      """ , 'None'),
    ], {}


def role_detail():
    return [
        ('race_ID',        """%s: {                  """, 'int'),
        ('role_name',      """    'role_name'      : %s, """, 'unicode'),
        ('img',            """    'img'            : %s, """, 'str'),
        ('icon',           """    'icon'           : %s, """, 'str'),
        ('battle_icon',    """    'battle_icon'    : %s, """, 'str'),
        ('select_background',    """    'select_background'    : %s, """, 'str'),
        ('animation',      """    'animation'      : %s, """, 'str'),
        ('story',          """    'story'          : %s, """, 'unicode'),
        ('role_talent',    """    'role_talent'    : %s, """, 'int'),
        ('position1',      """    'position1'      : %s, """, 'int'),
        ('position2',      """    'position2'      : %s, """, 'int'),
        ('position3',      """    'position3'      : %s, """, 'int'),
        ('position4',      """    'position4'      : %s, """, 'int'),
        ('position5',      """    'position5'      : %s, """, 'int'),
        ('position6',      """    'position6'      : %s, """, 'int'),
        ('position7',      """    'position7'      : %s, """, 'int'),
        ('position8',      """    'position8'      : %s, """, 'int'),
        ('position9',      """    'position9'      : %s, """, 'int'),
        ('position10',     """    'position10'     : %s, """, 'int'),
        ('character_bag',  """    'character_bag'  : %s, """, 'int_list'),
        ('item',           """    'item'           : %s, """, 'int_list'),
        ('equip',           """    'equip'           : %s, """, 'int_list'),
        ('food_produce',   """    'food_produce'   : %s, """, 'int'),
        ('metal_produce',  """    'metal_produce'  : %s, """, 'int'),
        ('energy_produce', """    'energy_produce' : %s, """, 'int'),
        ('END',            """},                     """, 'None'),
    ], {}


def role_skill():
    """
    """
    return [
               ('skill_id', """%s: {                        """, 'int'),
               ('name', """ 'name'      :%s,            """, 'unicode'),
               ('icon', """ 'icon'     :%s,            """, 'str'),
               ('story', """ 'story'     :%s,            """, 'unicode'),
               ('race1', """ 'race1'     :%s,            """, 'int_list'),
               ('type1', """ 'type1'     :%s,            """, 'str'),
               ('value1', """ 'value1'    :%s,            """, 'int'),
               ('race2', """ 'race2'     :%s,            """, 'int_list'),
               ('type2', """ 'type2'     :%s,            """, 'str'),
               ('value2', """ 'value2'    :%s,            """, 'int'),
               ('END', """},                           """, 'None'),
    ], {}



def leader_skill():
    return [
        ('ID', """%s: {                          """, 'int'),
        ('name', """      'name'             : %s, """, 'unicode'),
        ('icon', """      'icon'             : %s, """, 'str'),
        ('story', """      'story'            : %s, """, 'unicode'),
        ('tree', """      'tree'             : %s, """, 'int'),
        ('xy', """      'xy'               : %s, """, 'int_list'),
        ('ready_time', """      'ready_time'       : %s, """, 'int'),
        ('cd', """      'cd'               : %s, """, 'int'),
        ('pre-skill', """      'pre_skill'        : %s, """, 'int_list'),
        ('max-level', """      'max_level'        : %s, """, 'int'),
        ('is_positive', """      'is_positive'      : %s, """, 'int'),
        ('base_effect1', """      'base_effect1'     : %s, """, 'int'),
        ('base_effect2', """      'base_effect2'     : %s, """, 'int'),
        ('add_effect1', """      'add_effect1'      : %s, """, 'int'),
        ('add_effect2', """      'add_effect2'      : %s, """, 'int'),
        ('script', """      'script'           : %s, """, 'str'),
        ('action', """      'action'           : %s, """, 'str'),
        ('END', """},                             """, 'None'),
    ], {}

def leader_skill_develop():
    return [
        ('ID', """%s: {                 """, 'int'),
        ('name', """    'name'      : %s, """, 'unicode'),
        ('star_cost1', """    'star_1'      : %s, """, 'int'),
        ('star_cost2', """    'star_2'      : %s, """, 'int'),
        ('star_cost3', """    'star_3'      : %s, """, 'int'),
        ('star_cost4', """    'star_4'      : %s, """, 'int'),
        ('star_cost5', """    'star_5'      : %s, """, 'int'),
        ('step'      , """    'step'            : %s, """, 'int'),
        ('END'       , """},                    """, 'None'),
    ], {}


def skill_detail():
    return [
        ('skill_ID',      """%s: {                   """ , 'int'),
        ('skill_name',    """ 'skill_name'     : %s, """ , 'unicode'),
        ('skill_story',   """ 'skill_story'    : %s, """ , 'unicode'),
        ('skill_icon',    """ 'skill_icon'     : %s, """ , 'str'),
        ('skill_type',    """ 'skill_type'     : %s, """ , 'str'),
        ('rate',          """ 'rate'           : %s, """ , 'int'),
        ('cd',            """ 'cd'             : %s, """ , 'int'),
        ('pre_cd',        """ 'pre_cd'         : %s, """ , 'int'),
        ('effect',        """ 'effect'         : %s, """ , 'int'),
        ('attr_effect',   """ 'attr_effect'    : %s, """ , 'int'),
        ('effect_lvchange',""" 'effect_lvchange': %s, """ , 'float'),
        ('skill_quality', """ 'skill_quality'  : %s, """ , 'int'),
        ('max_lv',        """ 'max_lv'         : %s, """ , 'int'),
        ('is_evolution',  """ 'is_evolution'   : %s, """ , 'int'),
        ('evo_food',      """ 'evo_food'      : %s,  """ , 'int'),
        ('is_learn',      """ 'is_learn'       : %s, """ , 'int'),
        ('action',        """ 'action'         : %s, """ , 'int'),
        ('sprite_py',     """ 'sprite_py'      : %s, """ , 'str'),
        ('resouce_type',  """ 'resource_type'  : %s, """ , 'int'),
        ('resouce_count', """ 'resource_count' : %s, """ , 'int'),
        ('attack_effect', """ 'attack_effect': %s,   """ , 'str'),
        ('effect_delay',  """ 'effect_delay': %s,    """ , 'int'),
        ('evo_story'   ,  """ 'evo_story':    %s,    """ , 'unicode'),
        ('END',           """ },                     """ , 'None'),
    ], {}

def skill_levelup():
    return [
            (('skill_level', 'skill_exp_0', 'skill_exp_1', 'skill_exp_2', 'skill_exp_3', 'skill_exp_4', 'skill_exp_5', 'skill_exp_6', 'skill_exp_7'), """     %s: (%s, %s, %s, %s, %s, %s, %s, %s),   """, ('int', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int')),
    ], {}

def skill_learn():
    return [
        (('original_id', 'learn_id'), """    %s: %s, """, ('int', 'int')),
    ], {}

def building_factory():
    return [
        ('build_id', """%s: {                      """, 'int'),
        ('building_name', """    'building_name' : %s,  """, 'unicode'),
        ('quality', """    'quality'       : %s,  """, 'int'),
        ('image', """    'image'         : %s,  """, 'str'),
        ('levelup', """    'levelup'       : %s,  """, 'int'),
        ('END', """},                         """, 'None'),
    ], {}

building_harbor = building_factory
building_hospital = building_factory
building_school = building_factory
building_laboratory = building_factory

def building():
    return [
        ('build_id', """ %s: {                 """ , 'int'),
        ('building_name', """ 'building_name' : %s, """ , 'unicode'),
        ('describe', """ 'describe'  : %s,     """ , 'unicode'),
        ('quality', """ 'quality'       : %s, """ , 'int'),
        ('icon', """ 'icon'         : %s,  """ , 'str'),
        ('harbor', """ 'harbor'        : %s, """ , 'int'),
        ('school', """ 'school'        : %s, """ , 'int'),
        ('factory', """ 'factory'       : %s, """ , 'int'),
        ('hospital', """ 'hospital'      : %s, """ , 'int'),
        ('laboratory', """ 'laboratory'    : %s, """ , 'int'),
        ('END', """ },                    """ , 'None'),
    ], {}


def food_mine():
    return [
        ('build_id'      , """%s : {                     """, 'int'),
        ('building_name' , """    'building_name'  : %s, """, 'unicode'),
        ('image'         , """    'image'          : %s, """, 'int'),
        ('quality'       , """    'quality'        : %s, """, 'int'),
        ('food_produce' , """    'produce'        : %s, """, 'int'),
        ('END'           , """},                         """, 'None'),
    ], {}


def guide_manual():
    return [
        ('id'       , """%s : {             """, 'int'),
        ('icon'     , """    'icon'  : %s,  """, 'str'),
        ('word'     , """    'word'  : %s,  """, 'unicode'),
        ('manual'   , """    'manual': %s,  """, 'unicode'),
        ('button'    , """    'button' : %s,  """, 'str'),
        ('inreview' , """    'inreview' : %s,  """, 'int'),
        ('is_guide' , """    'is_guide' : %s,  """, 'int'),
        ('END'      , """},                 """, 'None'),
    ], {}

def metal_mine():
    return [
        ('build_id'         , """%s : {                     """, 'int'),
        ('building_name'    , """    'building_name'  : %s, """, 'unicode'),
        ('image'            , """    'image'          : %s, """, 'int'),
        ('quality'          , """    'quality'        : %s, """, 'int'),
        ('metal_produce' , """    'produce'        : %s, """, 'int'),
        ('END'              , """},                         """, 'None'),
    ], {}

def energy_mine():
    return [
        ('build_id'      , """%s : {                     """, 'int'),
        ('building_name' , """    'building_name'  : %s, """, 'unicode'),
        ('image'         , """    'image'          : %s, """, 'int'),
        ('quality'       , """    'quality'        : %s, """, 'int'),
        ('energy_produce', """    'produce'        : %s, """, 'int'),
        ('END'           , """},                         """, 'None'),
    ], {}

def building_base_harbor():
    return [
        ('build_level', """%s : {                    """, 'int'),
        ('skill_groove', """      'skill_groove': %s, """, 'int'),
        ('tree', """      'tree':         %s, """, 'int'),
        ('END', """},                        """, 'None'),
    ], {}

def character_strengthen():
    """# character_strengthen: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('level'             , """%s: {                         """, 'int') ,
        ('need_star'         , """    'need_star'         : %s, """, 'int') ,
        ('need_time'         , """    'need_time'         : %s, """, 'int') ,
        ('need_food'         , """    'need_food'         : %s, """, 'int') ,
        ('add_patk'          , """    'add_patk'          : %s, """, 'int') ,
        ('need_crstal_patk'  , """    'need_crstal_patk'  : %s, """, 'int_list') ,
        ('add_matk'          , """    'add_matk'          : %s, """, 'int') ,
        ('need_crstal_matk'  , """    'need_crstal_matk'  : %s, """, 'int_list') ,
        ('add_def'           , """    'add_def'           : %s, """, 'int') ,
        ('need_crstal_def'   , """    'need_crstal_def'   : %s, """, 'int_list') ,
        ('add_speed'         , """    'add_speed'         : %s, """, 'int') ,
        ('need_crstal_speed' , """    'need_crstal_speed' : %s, """, 'int_list') ,
        ('add_hp'            , """    'add_hp'            : %s, """, 'int') ,
        ('need_crstal_hp'    , """    'need_crstal_hp'    : %s, """, 'int_list') ,
        ('need_level'        , """    'need_level'        : %s, """, 'int') ,
        ('END', """},                            """, 'None'),
    ], {}


def character_train_rate():
    return [
        ('train_ID',        """%s: {        """ , 'int'),
        ('name',            """    'name': %s,            """ , 'unicode'),
        ('exp_rate',        """    'exp_rate': %s,        """ , 'int'),
        ('extra_food_rate', """    'extra_food_rate': %s, """ , 'int'),
        ('coin_cost',       """    'coin_cost': %s,       """ , 'int'),
        ('need_vip',        """    'need_vip': %s,       """ , 'int'),
        ('END', """},                            """, 'None'),
    ], {}

def character_train_time():
    return [
        ('time_ID',        """%s: {        """ , 'int'),
        ('name',            """    'name': %s,            """ , 'unicode'),
        ('time',            """    'time': %s,        """ , 'int'),
        ('extra_food_rate', """    'extra_food_rate': %s, """ , 'int'),
        ('coin_cost',       """    'coin_cost': %s,       """ , 'int'),
        ('need_vip',        """    'need_vip': %s,       """ , 'int'),
        ('END', """},                            """, 'None'),
    ], {}

def character_train_position():
    return [
        ('position',        """ 'stove_%s': {        """ , 'int'),
        ('open_sort',       """    'open_sort': %s,    """ , 'int'),
        ('value',           """    'value': %s,        """ , 'int_list'),
        ('END', """},                            """, 'None'),
    ], {}

def evolution():
    return [
        ('ID',        """ %s: {        """ , 'int'),
        ('step',           """    'step': %s,        """ , 'int'),
        ('degree',       """    'degree': %s,    """ , 'int_list'),
        ('exp',          """    'exp'   : %s,    """ , 'int'),
        ('level_off',    """    'level_off': %s,    """ , 'int'),
        ('need_level',   """    'need_level': %s,    """ , 'int'),
        ('skill',        """    'skill': %s,    """ , 'int_list'),
        ('story',        """    'story': %s,    """ , 'unicode'),
        ('maxlv',        """    'maxlv': %s,    """ , 'int'),
        ('all',        """    'all': %s,    """ , 'float'),
        ('attr0',       """    'attr0': %s,    """ , 'int_list'),
        ('attr1',       """    'attr1': %s,    """ , 'int_list'),
        ('attr2',       """    'attr2': %s,    """ , 'int_list'),
        ('attr3',       """    'attr3': %s,    """ , 'int_list'),
        ('attr4',       """    'attr4': %s,    """ , 'int_list'),
        ('attr5',       """    'attr5': %s,    """ , 'int_list'),
        ('type0',       """    'type0': %s,    """ , 'int_list'),
        ('type1',       """    'type1': %s,    """ , 'int_list'),
        ('type2',       """    'type2': %s,    """ , 'int_list'),
        ('type3',       """    'type3': %s,    """ , 'int_list'),
        ('type4',       """    'type4': %s,    """ , 'int_list'),
        ('type5',       """    'type5': %s,    """ , 'int_list'),
        ('player_level',       """    'player_level': %s,    """ , 'int'),
        ('END', """},                            """, 'None'),
    ], {}

evolution_3 = evolution
evolution_4 = evolution
evolution_5 = evolution

# TODO building_base_school废弃
def building_base_school():
    return [
        ('build_level', """ %s: {                  """, 'int'),
        ('train_groove', """    'train_groove': %s, """, 'int'),
        ('get_exp_min', """    'get_exp_min' : %s, """, 'int'),
        ('END', """},                      """, 'None'),
    ], {}

def character_train():
    return [
        ('star', """%s: [                 """, 'int'),
        ('quality0', """    %s, """, 'int'),
        ('quality1', """    %s, """, 'int'),
        ('quality2', """    %s, """, 'int'),
        ('quality3', """    %s, """, 'int'),
        ('quality4', """    %s, """, 'int'),
        ('quality5', """    %s, """, 'int'),
        ('quality6', """    %s, """, 'int'),
        ('END', """],                      """, 'None'),
    ], {}

def enchant():
    return [
        ('quality', """%s: {                 """, 'int'),
        ('piece', """   'piece': %s, """, 'int'),
        ('atk_max', """   'atk_max': %s, """, 'int'),
        ('atk_rate', """   'atk_rate': %s, """, 'int_list'),
        ('def_max', """   'def_max': %s, """, 'int'),
        ('def_rate', """   'def_rate': %s, """, 'int_list'),
        ('END', """},                      """, 'None'),
    ], {}

def reward_pk():
    return [
        ('reward_id', """%s: {                 """, 'int'),
        ('sort', """   'sort': %s, """, 'int'),
        ('rank', """   'rank': %s, """, 'int_list', check_int_list_args(2)),
        ('reward', """   'reward': %s, """, 'int_list', check_reward(),),
        ('mail', """   'mail': %s, """, 'unicode'),
        ('END', """},                      """, 'None'),
    ], {}

def formation():
    return [
        ('formation_id',"""int(%s.replace('formation_', '')): {                 """, 'str'),
        ('position_A', """    'position_a': %s, """, 'int'),
        ('position_B', """    'position_b': %s, """, 'int'),
        ('position_C', """    'position_c': %s, """, 'int'),
        ('position_D', """    'position_d': %s, """, 'int'),
        ('position_E', """    'position_e': %s, """, 'int'),
        ('position_F', """    'position_f': %s, """, 'int'),
        ('alternate1', """    'alternate1': %s, """, 'int'),
        ('alternate2', """    'alternate2': %s, """, 'int'),
        ('alternate3', """    'alternate3': %s, """, 'int'),
        ('alternate4', """    'alternate4': %s, """, 'int'),
        ('alternate5', """    'alternate5': %s, """, 'int'),
        ('icon',       """    'icon'      : %s, """, 'str'),
        ('END',        """},  """, 'None'),
    ], {}

def formation_1():
    return [
        ('position',       """%s: [     """, 'int'),
        ('formation_1',    """      %s, """, 'int_list'),
        ('formation_2',    """      %s, """, 'int_list'),
        ('formation_3',    """      %s, """, 'int_list'),
        ('formation_4',    """      %s, """, 'int_list'),
        ('formation_5',    """      %s, """, 'int_list'),
        ('formation_6',    """      %s, """, 'int_list'),
        ('END',            """],        """, 'None'),
    ], {}
formation_2 = formation_1
formation_3 = formation_1
formation_4 = formation_1
formation_5 = formation_1
formation_6 = formation_1


def suit():
    return [
        ('suit_ID',     """  %s: { """,      'int'),
        ('name',     """  'name': %s, """,      'unicode'),
        ('part',     """  'part': %s, """,      'int_list'),
        ('effect_2',     """  'effect_2': %s, """,      'int_list'),
        ('effect_3',     """  'effect_3': %s, """,      'int_list'),
        ('effect_4',     """  'effect_4': %s, """,      'int_list'),
        ('END', """},                        """, 'None'),
    ], {}

def equip():
    return [
        ('unique_equip_id', """%s: {                     """, 'int'),
        ('equip_id',      """ 'equip_id'             : %s, """, 'int'),
        ('afterlife',      """ 'afterlife'             : %s, """, 'int'),
        ('chain_id',      """ 'chain_id'             : %s, """, 'int'),
        ('name',      """ 'name'             : %s, """, 'unicode'),
        ('image', """ 'image'            : %s, """, 'str'),
        ('suit',      """ 'suit'             : %s, """, 'int'),
        ('exchange_id', """ 'exchange_id'          : %s, """, 'int'),
        ('sort',      """ 'sort'             : %s, """, 'int'),
        ('quality', """ 'quality'          : %s, """, 'int'),
        ('evolution', """ 'evolution'             : %s, """, 'int'),
        ('evolution_id', """ 'evolution_id'             : %s, """, 'int'),
        ('sell_metal', """ 'sell_metal'          : %s, """, 'int'),
        ('is_resolve', """ 'is_resolve'       : %s, """, 'int'),
        ('ability1', """ 'ability1'         : %s, """, 'int'),
        ('value1', """ 'value1'           : %s, """, 'int'),
        ('level_add1', """ 'level_add1'       : %s, """, 'int'),
        ('ability2', """ 'ability2'         : %s, """, 'int'),
        ('value2', """ 'value2'           : %s, """, 'int'),
        ('level_add2', """ 'level_add2'       : %s, """, 'int'),
        ('refine_id', """ 'refine_id'       : %s, """, 'int'),
        ('activation', """ 'activation'       : %s, """, 'str'),
        ('activation_level', """ 'activation_level'       : %s, """, 'int'),
        ('melting', """ 'melting'       : %s, """, 'int'),
        ('END', """},                        """, 'None'),
    ], {}

def equip_st():
    return [
        ('st_level', """%s: {                      """, 'int'),
        ('rate',      """ 'rate'             : %s, """, 'int'),
        ('metalcore',      """ 'metalcore'   : %s, """, 'int'),
        ('metal',          """ 'metal'       : %s, """, 'int'),
        ('false_back',     """ 'false_back'  : %s, """, 'int'),
        ('phsc',      """ 'patk'             : %s, """, 'int_list'),
        ('mgc',       """ 'matk'             : %s, """, 'int_list'),
        ('dfs',       """ 'def'              : %s, """, 'int_list'),
        ('speed',     """ 'speed'            : %s, """, 'int_list'),
        ('max_rate',  """ 'max_rate'         : %s, """, 'int'),
        ('END', """},                        """, 'None'),
    ], {}

def equip_exchange():
    return [(
            ('exchange_id', 'metal', 'metalcore',
                'item1', 'item2', 'item3', 'item4', 'item5'),
            """ %s: {'metal': %s, 'metalcore': %s,
                     'item': [%s, %s, %s, %s, %s] },""",
            ('int', 'int_list', 'int_list',
             'int_list', 'int_list', 'int_list', 'int_list', 'int_list')
            )
            ], {}

def equip_evolution():
    return [
        ('evolution_id', """%s:{                      """, 'int'),
        ('equip_material_1', """ 'equip_material_1'   : %s,   """, 'int_list', check_reward(),),
        ('equip_material_2', """ 'equip_material_2'   : %s,   """, 'int_list', check_reward(),),
        ('equip_material_3', """ 'equip_material_3'   : %s,   """, 'int_list', check_reward(),),
        ('metal', """ 'metal'           : %s,   """, 'int'),
        ('END', """},                       """, 'None'),
    ], {};

#def equip_max_strongthen():
#    return [
#        ('quality', """%s:{                      """, 'int'),
#        ('max_strongthen', """ 'max_strongthen'     : %s,   """, 'int'),
#        ('END', """},                        """, 'None'),
#    ], {};

def equip_strongthen():
    return [
        ('level', """%s:{                        """, 'int'),
        #('time', """ 'time'              :%s,""", 'int'),
        #('foo d', """ 'food'             :%s,""", 'int'),
        ('metal', """ 'metal'          :%s,""", 'int'),
        #('energy', """ 'energy'            :%s,""", 'int'),
        ('quality0', """ 'quality0'          :%s,""", 'int'),
        ('quality1', """ 'quality1'          :%s,""", 'int'),
        ('quality2', """ 'quality2'          :%s,""", 'int'),
        ('quality3', """ 'quality3'          :%s,""", 'int'),
        ('quality4', """ 'quality4'          :%s,""", 'int'),
        ('quality5', """ 'quality5'          :%s,""", 'int'),
        ('quality6', """ 'quality6'          :%s,""", 'int'),
        ('quality7', """ 'quality7'          :%s,""", 'int'),
        ('quality8', """ 'quality8'          :%s,""", 'int'),
        ('need_item', """ 'need_item'          :%s,""", 'int_list'),
        ('END', """},                       """, 'None'),
    ], {}

def middle_map():
    return [
        ('unique_ID'       , """%s: {                       """    , 'str') ,
        ('middle_mapid'    , """    'middle_mapid'    : %s, """    , 'int') ,
        ('banner'          , """    'banner'          : %s, """    , 'str') ,
        ('name'            , """    'name'            : %s, """    , 'unicode') ,
        ('earth_name'      , """    'earth_name'      : %s, """    , 'str') ,
        ('map_data'        , """    'map_data'        : %s, """    , 'str') ,
        ('need_chapter'    , """    'need_chapter'    : %s, """    , 'int') ,
        ('open_level'      , """    'open_level'      : %s, """    , 'int') ,
        ('close_level'     , """    'close_level'     : %s, """    , 'int') ,
        ('line'            , """    'line'            : %s, """    , 'int') ,
        ('END'             , """},                          """    , 'None') ,
    ], {}

def middle_resource():
    return [
        ('resource_ID', """%s: {                """ , 'int'),
        ('name', """ 'name'        : %s, """ , 'unicode'),
        ('background'      , """    'background'      : %s, """    , 'str'),
        ('detail', """ 'detail'      : %s, """ , 'unicode'),
        ('img', """ 'img'         : %s, """ , 'str'),
        ('reward', """ 'reward'         : %s, """ , 'int_list', check_reward(),),
        ('fight', """ 'fight'       : %s, """ , 'int_list'),
        ('END', """},                   """ , 'None'),
    ], {}

def middle_mine():
    """# middle_mine: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('build_id',         """ %s: {                    """ , 'int'),
        ('building_name',    """ 'name'        : %s,      """ , 'unicode'),
        ('image',            """ 'image'            : %s, """ , 'str'),
        ('background'      , """    'background'      : %s, """    , 'str'),
        ('fight',            """ 'fight'            : %s, """ , 'int_list'),
        ('reward_base',      """ 'reward_base'      : %s, """ , 'int_list', check_reward(),),
        ('reward_item',      """ 'reward_item'      : %s, """ , 'int_list', check_reward(),),
        ('Y',                """ 'y'          : %s,       """ , 'int'),
        ('X',                """ 'x'          : %s,       """ , 'int'),
        ('detail',           """ 'detail'      : %s,      """ , 'unicode'),
        ('END',              """ },                       """ , 'None'),
    ], {}


def gacha():
    return [
        ('gacha_ID',     """%s:{                   """ , 'int'),
        ('star_time',    """ 'star_time'     : %s, """ , 'str'),
        ('gacha_name',    """ 'gacha_name'     : %s, """ , 'str'),
        ('gacha_team',   """ 'gacha_team'    : %s, """ , 'int'),
        ('image',        """ 'image'         : %s, """ , 'str'),
        ('image_word',   """ 'image_word'    : %s, """ , 'str'),
        ('image_active', """ 'image_active'  : %s, """ , 'str'),
        ('end_time',     """ 'end_time'      : %s, """ , 'str'),
        ('gacha_sort',   """ 'gacha_sort'    : %s, """ , 'int'),
        ('gacha_num',    """ 'gacha_num'     : %s, """ , 'int'),
        ('consume_sort', """ 'consume_sort'  : %s, """ , 'int'),
        ('value',        """ 'value'         : %s, """ , 'int'),
        ('get_num',      """ 'get_num'       : %s, """ , 'int'),
        ('quality',      """ 'quality'       : %s, """ , 'int'),
        ('get_card',     """ 'get_card'      : %s, """ , 'int_list'),
        ('add_point',    """ 'add_point'     : %s, """ , 'int'),
        ('bad_item',     """ 'bad_item'      : %s, """ , 'int_list'),
        ('bad_point',    """ 'bad_point'     : %s, """ , 'int'),
        ('good_item',    """ 'good_item'     : %s, """ , 'int_list'),
        ('good_point',   """ 'good_point'    : %s, """ , 'int'),
        ('piece',        """ 'piece'         : %s, """ , 'int_list'),
        ('story',        """ 'story'         : %s, """ , 'unicode'),
        ('use_level',    """ 'use_level'     : %s, """ , 'int_list'),
        ('use_gacha',    """ 'use_gacha'     : %s, """ , 'int_list'),
        ('is_box',       """ 'is_box'        : %s, """ , 'int'),
        ('reward',       """ 'reward'        : %s, """ , 'int_list', check_reward(),),
        ('time_sort',    """ 'time_sort'     : %s, """ , 'int'),
        ('add_num',      """ 'add_num'       : %s, """ , 'int'),
        ('add_card',     """ 'add_card'      : %s, """ , 'int_list'),
        ('END',          """ },                    """ , 'None'),
    ], {};

def gacha_box():
    return [(
             ('box_id', 'team_card'),
              """ %s: %s, """,
             ('int', 'int_list')
            )], {}

def guild_level():
    return [
        ('level'      , """%s: {""" , 'int') ,
        ('cost'       , """    'cost': %s       , """ , 'int') ,
        ('member_num' , """    'member_num': %s , """ , 'int') ,
        ('percent' ,    """    'percent': %s ,    """ , 'int') ,
        ('level_des'  , """    'level_des': %s  , """ , 'unicode') ,
        ('next_des'   , """    'next_des': %s   , """ , 'unicode') ,
        ('END', """ },                """ , 'None'),
    ], {}

def guild_level_reward():
    return [
        ('guild_level_step'      , """%s: {""" , 'int') ,
        ('guild_reward'       , """    'guild_reward': %s       , """ , 'int') ,
        ('limit' , """    'limit': %s , """ , 'int') ,
        ('is_open' , """    'is_open': %s , """ , 'int') ,
        ('END', """ },                """ , 'None'),
    ], {}

def guild_shop():
    return [
        ('level'      , """%s: {""" , 'int') ,
        ('cost'       , """    'cost': %s       , """ , 'int') ,
        ('level_des'  , """    'level_des': %s  , """ , 'unicode') ,
        ('next_des'   , """    'next_des': %s   , """ , 'unicode') ,
        ('END', """},                    """, 'None'),
    ], {}


def guild_shop_item():
    return [
        ('shop'           , """%s: {           """ , 'int')  ,
        ('shop_icon'      , """    'shop_icon': %s      , """ , 'str')  ,
        ('need_shoplevel' , """    'need_shoplevel': %s , """ , 'int')  ,
        ('shop_reward'    , """    'shop_reward': %s    , """ , 'int_list', check_reward(),)  ,
        ('need_gongxian'  , """    'need_gongxian': %s  , """ , 'int')  ,
        ('times'          , """    'times': %s          , """ , 'int')  ,
        ('total_num'      , """    'total_num': %s      , """ , 'int')  ,
        ('refresh'        , """    'refresh': %s        , """ , 'int')  ,
        ('show_level'     , """    'show_level': %s     , """ , 'int_list')  ,
        ('show_type'      , """    'show_type': %s      , """ , 'int')  ,
        ('END'            , """}                        , """ , 'None') ,
    ], {}

def guild_GVGplayer():
    return [
        ('level'     , """%s: {""" , 'int')  ,
        ('add'       , """    'add': %s       , """ , 'int')  ,
        ('cost'      , """    'cost': %s      , """ , 'int')  ,
        ('level_des' , """    'level_des': %s , """ , 'unicode')  ,
        ('next_des'  , """    'next_des': %s  , """ , 'unicode')  ,
        ('END'       , """}                   , """ , 'None') ,
    ], {}

guild_bossplayer = guild_GVGplayer
guild_middleplayer = guild_GVGplayer

def guild_GVGmonster():
    return [
        ('level'     , """%s: {""" , 'int')  ,
        ('add'       , """    'add': %s       , """ , 'int')  ,
        ('cost'      , """    'cost': %s      , """ , 'int')  ,
        ('level_des' , """    'level_des': %s , """ , 'unicode')  ,
        ('next_des'  , """    'next_des': %s  , """ , 'unicode')  ,
        ('END'       , """}                   , """ , 'None') ,
    ], {}

def guild_GVGhome():
    return [
        ('level'     , """%s: {""" , 'int')  ,
        ('add'       , """    'add': %s       , """ , 'int')  ,
        ('cost'      , """    'cost': %s      , """ , 'int')  ,
        ('level_des' , """    'level_des': %s , """ , 'unicode')  ,
        ('next_des'  , """    'next_des': %s  , """ , 'unicode')  ,
        ('END'       , """}                   , """ , 'None') ,
    ], {}


def guild_tech():
    """# guild_tech: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('tech_ID'    , """%s: { """            , 'int') ,
        ('des'        , """    'des': %s        , """    , 'unicode') ,
        ('excel_name' , """    'excel_name': %s , """    , 'str')     ,
        ('icon'       , """    'icon': %s       , """    , 'str')     ,
        ('open_level' , """    'open_level': %s , """    , 'int')     ,
        ('END'        , """}                    , """    , 'None')    ,
    ], {}

def guild_funtion():
    return [
        ('funtion_ID' , """%s: {""" , 'int')  ,
        ('des'        , """    'des': %s        , """ , 'unicode')  ,
        ('open_level' , """    'open_level': %s , """ , 'int')  ,
        ('END'        , """}                    , """ , 'None') ,
    ], {}

def guild_fight():
    return [
        ("build_id"         , """%s: {                        """, 'int'),
        ("building_name"   , """    'building_name': %s             , """, 'unicode'),
        ("sort"              , """    'sort': %s              , """, 'int'),
        ("score"            , """    'score': %s     , """, 'int'),
        ("life_1"           , """    'life_1': %s        , """, 'int'),
        ("life_2"           , """    'life_2': %s , """, 'int'),
        ('END'              , """}                          , """, 'None'),
    ], {}

# def guild_fight():
#     return [
#         ("ID"               , """%s: {                        """, 'int'),
#         ("name"             , """    'name': %s             , """, 'unicode'),
#         ("tmx"              , """    'tmx': %s              , """, 'str'),
#         ("random_fight"     , """    'random_fight': %s     , """, 'int_list'),
#         ("flag_need"        , """    'flag_need': %s        , """, 'int'),
#         ("reward_guildcash" , """    'reward_guildcash': %s , """, 'int'),
#         ("open_type"        , """    'open_type': %s        , """, 'int_list'),
#         ("refresh_win1"     , """    'refresh_win1': %s     , """, 'int_list'),
#         ("refresh_win2"     , """    'refresh_win2': %s     , """, 'int_list'),
#         ("refresh_win3"     , """    'refresh_win3': %s     , """, 'int_list'),
#         ("refresh_win4"     , """    'refresh_win4': %s     , """, 'int_list'),
#         ("refresh_lose1"    , """    'refresh_lose1': %s    , """, 'int_list'),
#         ("refresh_lose2"    , """    'refresh_lose2': %s    , """, 'int_list'),
#         ("refresh_lose3"    , """    'refresh_lose3': %s    , """, 'int_list'),
#         ("refresh_lose4"    , """    'refresh_lose4': %s    , """, 'int_list'),
#         ("reward_huoyue"    , """    'reward_huoyue': %s    , """, 'int_list'),
#         ("des"              , """    'des': %s              , """, 'unicode'),
#         ('END'              , """}                          , """, 'None'),
#     ], {}

def daily_award():
    return [
        ('score', """%s : {               """, 'int'),
        ('icon', """ 'icon'   :%s,""", 'str'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('END', """ },                  """, 'None'),
    ], {}

daily_award_loop = daily_award

def week_award():
    return [
        ('score', """%s : {               """, 'int'),
        ('icon', """ 'icon'   :%s,""", 'str'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('END', """ },                  """, 'None'),
    ], {}

def month_award():
    return [
        ('score', """%s : {               """, 'int'),
        ('icon', """ 'icon'   :%s,""", 'str'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('END', """ },                  """, 'None'),
    ], {}

def month_award_coin():
    return [
        ('score', """%s : {               """, 'int'),
        ('icon', """ 'icon'     :%s,""", 'str'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('pay',   """ 'pay'     :%s,""", 'int'),
        ('END', """ },                  """, 'None'),
    ], {}


def month_award_coin_loop():
    return [
        ('id', """%s : {               """, 'int'),
        ('reriod',   """ 'reriod'     :%s,""", 'int'),
        ('score',   """ 'score'     :%s,""", 'int'),
        ('icon', """ 'icon'     :%s,""", 'str'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('pay',   """ 'pay'     :%s,""", 'int'),
        ('END', """ },                  """, 'None'),
    ], {}


def online_award():
    return [
        ('score', """%s : {               """, 'int'),
        ('second', """ 'second'   :%s,""", 'int'),
        ('award', """ 'award'   :%s,""", 'int_list', check_reward(),),
        ('END', """ },                  """, 'None'),
    ], {}

def chain():
    """# chain: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('chain_ID'       , """%s: { """                , 'int') ,
        ('name'           , """    'name': %s           , """    , 'unicode')  ,
        ('condition_sort' , """    'condition_sort': %s , """    , 'str')      ,
        ('data'           , """    'data': %s           , """    , 'int_list') ,
        ('effect'         , """    'effect': %s         , """    , 'int_list') ,
        ('des'            , """    'des': %s            , """    , 'unicode')  ,
        ('END'            , """ }                       , """    , 'None')     ,
    ], {}


def drama():
    """

    """
    return [
               ('dramaID', """%s :{                """, 'int'),
               ('fightID', """ 'fightID'       :%s,""", 'int'),
               ('start_sort', """ 'start_sort'    :%s,""", 'int'),
               ('data', """ 'data'          :%s,""", 'int'),
               ('drama_detail', """ 'drama_detail'  :%s,""", 'unicode_int_list'),
               ('END', """},                   """, 'None'),
    ], {}

def item():
    return [
            ('item_id', """%s:{              """, 'int'),
            ('name', """ 'name'        :%s,""", 'unicode'),
            ('story', """ 'story'       :%s,""", 'unicode'),
            ('icon', """ 'icon'        :%s,""", 'str'),
            ('quality', """ 'quality'        :%s,""", 'int'),
            ('shade', """ 'shade'        :%s,""", 'str'),
            ('stack', """'stack'        :%s,""", 'int'),
            ('is_sell', """'is_sell'      :%s,""", 'int'),
            ('is_use', """'is_use'       :%s,""", 'int'),
            ('use_num', """'use_num'       :%s,""", 'int'),
            ('use_effect', """'use_effect'   :%s,""", 'int_single_list'),
            ('sort',      """'sort'   :%s,""", 'int'),
            ('is_show', """'is_show'       :%s,""", 'int'),
            ('daily_use', """'daily_use'   :%s,""", 'int'),
            ('END', """},                   """, 'None'),
    ], {}

unify_ios_item = unify_android_item = item

def box():
    return [
        (('box_id',
          'reward1', 'num1','level1',
          'reward2', 'num2','level2',
          'reward3', 'num3','level3',
          'reward4', 'num4','level4',
          'reward5', 'num5','level5',
          'reward6', 'num6','level6',
          'reward7', 'num7','level7',
          'reward8', 'num8','level8',
          'reward9', 'num9','level9',
          'reward10', 'num10','level10',
          ),

         """%s: [{'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 {'reward': %s, 'num': %s, 'level': %s},
                 ], """,

                                    ('int',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                      'int_list', 'int','int_list',
                                    ),
                                    (None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                      check_reward(is_random=True), None, None,
                                    )),
    ], {}

unify_ios_box = unify_android_box = box

def chapter():
    """# chapter: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('chapter_ID',    """%s: {                 """ , 'int'),
        ('chapter_name',  """    'chapter_name'  : %s, """ , 'unicode'),
        ('is_hard',       """    'is_hard'       : %s, """ , 'int'),
        ('is_show',       """    'is_show'       : %s, """ , 'int'),
        ('open_level',    """    'open_level'    : %s, """ , 'int'),
        ('resource',      """    'resource'      : %s, """ , 'str'),
        ('banner',         """    'banner'      : %s,    """ , 'str'),
        ('music',         """    'music'      : %s,    """ , 'str'),
        ('chapter_story', """    'chapter_story' : %s, """ , 'unicode'),
        ('hidden_order',  """    'hidden_order'  : %s, """ , 'int'),
        ('battlepoint',   """    'battlepoint'   : %s, """ , 'int'),
        ('END',           """},                    """ , 'None'),
    ], {}

def arena_award():
    return [('id',          """%s: {""",    'int'),
            ('start_rank',  """ 'start_rank': %s, """, 'int'),
            ('end_rank',    """ 'end_rank': %s, """, 'int'),
            ('per_point',   """ 'per_point': %s, """, 'int'),
            ('per_food',  """ 'per_food': %s, """, 'int'),
            ('per_metal',  """ 'per_metal': %s, """, 'int'),
            ('per_energy',      """ 'per_energy': %s, """, 'int'),
            ('day_money',      """ 'day_money': %s, """, 'int'),
            ('END', """},                   """, 'None'),
    ], {}

def arena_award_milestone():
    return [('ID',          """%s: {""",    'int'),
            ('rank',        """ 'rank': %s, """, 'int', check_int_list_args(2)),
            ('reward',      """ 'reward': %s, """, 'int_list', check_reward(),),
            ('END', """},                   """, 'None'),
    ], {}

def arena_shop():
    return [('shop',        """%s: {""",            'int'),
            ('shop_icon', """ 'shop_icon': %s, """, 'str'),
            ('shop_reward', """ 'shop_reward': %s, """, 'int_list', check_reward(),),
            ('need_point',  """ 'need_point': %s, """, 'int'),
            ('times', """ 'times': %s, """, 'int'),
            ('refresh', """ 'refresh': %s, """, 'int'),
            ('show_level', """ 'show_level': %s, """, 'int_list'),
            ('END', "        ""},                   """, 'None'),
    ], {}

def shop():
    return [
        ('shop', """%s: {""", 'int'),
        ('shop_reward', """ 'shop_reward' : %s, """, 'int_list', check_reward(),),
        ('shop_type',  """ 'shop_type' : %s, """, 'int'),
        ('need_sort',  """ 'need_sort' : %s, """, 'int'),
        ('need_value', """ 'need_value': %s, """, 'int_list'),
        ('sell_off',   """ 'sell_off'  : %s, """, 'int'),
        ('sell_sort',  """ 'sell_sort' : %s, """, 'int'),
        ('sell_max',   """ 'sell_max'  : %s, """, 'int'),
        ('sell_time',   """ 'sell_time'  : %s, """, 'str'),
        ('server_sell_time',   """ 'server_sell_time'  : %s, """, 'str'),
        ('show_level', """ 'show_level' : %s, """, 'int_list'),
        ('im_use', """ 'im_use' : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def card_shop():
    return [
        ('shop', """%s: {""", 'int'),
        ('week', """ 'week' : %s, """, 'int'),
        ('shop_reward',  """ 'shop_reward' : %s, """, 'int_list', check_reward(),),
        ('need_value', """ 'need_value': %s, """, 'int'),
        ('show_value', """ 'show_value': %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def vip_shop():
    return [
        ('shop_id', """%s: {""", 'int'),
        ('name', """ 'name' : %s, """, 'unicode'),
        ('need_vip',  """ 'need_vip' : %s, """, 'int'),
        ('false_coin', """ 'false_coin': %s, """, 'int'),
        ('need_coin',   """ 'need_coin'  : %s, """, 'int'),
        ('reward',  """ 'reward' : %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}


def guide():
    return [
        ('guide_id', """%s: {""", 'int'),
        ('id',         """ 'id'        : %s, """, 'int'),
        ('guide_team', """ 'guide_team': %s, """, 'int'),
        ('goto',       """ 'goto'      : %s, """, 'int'),
        ('open_button', """ 'open_button': %s, """, 'int_list'),
        ('drama',      """ 'drama'     : %s, """, 'int'),
        ('END', """},""", 'None'),
    ],{}


def server_shop():
    return [
        ('shop',        """%s: {""",                'int'),
        ('show_id',     """ 'show_id' : %s, """,    'int'),
        ('shop_reward', """ 'shop_reward' : %s, """,'int_list', check_reward(),),
        ('need_coin',   """ 'need_coin'  : %s, """, 'int'),
        ('sell_max',    """ 'sell_max': %s, """,    'int'),
        ('start_time',  """ 'start_time' : %s, """, 'str'),
        ('end_time',    """ 'end_time' : %s, """,   'str'),
        ('END', """},   """, 'None'),
    ], {}

def loading():
    return [
        ('level',             """%s: {             """ , 'int'),
        ('loadingtips',       """    'loadingtips': %s,       """ , 'int_list'),
        ('loading_animition', """    'loading_animition': %s, """ , 'str_list'),
        ('END',               """},""", 'None'),
    ], {}


def loadingtips():
    return [
        ('tips_ID',     """%s: {                  """ , 'int'),
        ('tips_detail', """    'tips_detail': %s, """ , 'unicode'),
        ('END',         """},""", 'None'),
    ], {}


def button_open():
    return [
        (('button_id', 'open_word'), """%s: %s, """, ('int', 'unicode')),
    ], {}

def guide_team():
    return [
        ('team_id', """%s: {""", 'int'),
        ('open_sort',         """ 'open_sort'        : %s, """, 'int'),
        ('open_value', """ 'open_value': %s, """, 'int'),
        ('guide_sort',       """ 'guide_sort'      : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def charge():
    return [
        ('buy_id', """%s: {""", 'int'),
        ('coin',  """ 'coin' : %s, """, 'int'),
        ('gift_coin',""" 'gift_coin' : %s, """, 'int'),
        ('is_double',""" 'is_double' : %s, """, 'int'),
        ('buy_times',""" 'buy_times' : %s, """, 'int'),
        ('cost',  """ 'cost' : %s, """, 'str'),
        ('icon',  """ 'icon' : %s, """, 'str'),
        ('des',   """ 'des'  : %s, """, 'unicode'),
        ('name',  """ 'name' : %s, """, 'unicode'),
        ('price', """ 'price': %s, """, 'int'),
        ('open_gift', """ 'open_gift': %s, """, 'int'),
        ('is_show', """ 'is_show': %s, """, 'int'),
        ('reward_ID', """ 'reward_id': %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def code():
    return [
        ('code_ID', """%s: {""", 'int'),
        ('name',         """ 'name'        : %s, """, 'unicode'),
        ('open',         """ 'open'        : %s, """, 'str'),
        ('type',         """ 'type'        : %s, """, 'int'),
        ('vip',         """ 'vip'        : %s, """, 'int'),
        ('close',        """ 'close'       : %s, """, 'str'),
        ('server',        """ 'server'       : %s, """, 'str'),
        ('refresh',        """ 'refresh'   : %s, """, 'int'),
        ('reward_des',   """ 'reward_des'  : %s, """, 'unicode'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('icon',      """ 'icon'     : %s, """, 'str'),
        ('END', """},""", 'None'),
    ], {}


def combat_base():
    return [
        (('sort', 'point'), """%s: %s,""", ('str', 'float')),
    ], {}

def combat_skill():
    return [
        ('level', """%s: {""", 'int'),
        ('quality_0', """ 0: %s, """, 'float'),
        ('quality_1', """ 1: %s, """, 'float'),
        ('quality_2', """ 2: %s, """, 'float'),
        ('quality_3', """ 3: %s, """, 'float'),
        ('quality_4', """ 4: %s, """, 'float'),
        ('quality_5', """ 5: %s, """, 'float'),
        ('quality_6', """ 6: %s, """, 'float'),
        ('quality_7', """ 7: %s, """, 'float'),
        ('END', """},""", 'None'),
    ], {}

def opening():
    return [
        ('opening_id', """%s: {""", 'int'),
        ('name',        """ 'name'       : %s, """, 'unicode'),
        ('title',        """ 'title'       : %s, """, 'str'),
        ('banner',        """ 'banner'       : %s, """, 'str'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_data': %s, """, 'int_list'),
        ('target_data1', """ 'target_data1': %s, """, 'int_list'),
        ('all_num',      """ 'all_num'   : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def reward_daily():
    return [
        ('daily_ID', """%s: {""", 'int'),
        ('icon',        """ 'icon'       : %s, """, 'str'),
        ('name',        """ 'name'       : %s, """, 'unicode'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('rate',        """ 'rate'       : %s, """, 'int'),
        ('open_sort',   """ 'open_sort'  : %s, """, 'int'),
        ('open_data',   """ 'open_data'  : %s, """, 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('reward_score', """ 'reward_score': %s, """, 'int'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_data': %s, """, 'int_list'),
        ('target_data1', """ 'target_data1': %s, """, 'int_list'),
        ('finish_open', """ 'finish_open': %s, """, 'int_list'),
        ('close_sort',   """ 'close_sort'  : %s, """, 'int'),
        ('close_data',   """ 'close_data'  : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def reward_once():
    return [
        ('once_ID', """%s: {""", 'int'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('open_sort',   """ 'open_sort'  : %s, """, 'int'),
        ('open_data',   """ 'open_data'  : %s, """, 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_data': %s, """, 'int_list'),
        ('END', """},""", 'None'),
    ], {}

def reward_gift():
    return [
        ('gift_id', """%s: {""", 'int'),
        ('time',      """ 'time'     : %s, """, 'str'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}

def level_gift():
    return [
        ('level', """%s: {""", 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('coin',        """ 'coin'       : %s, """, 'int'),
        ('buy',        """ 'buy'       : %s, """, 'int'),
        ('des',        """ 'des'       : %s, """, 'unicode'),
        ('END', """},""", 'None'),
    ], {}

def dailyscore():
    return [
        ('score',  """   %s: { """,  'int'),
        ('level', """ 'level': %s, """, 'int_list'),
        ('reward', """ 'reward': %s, """, 'int_list', check_reward(),),
        ('level2', """ 'level2': %s, """, 'int_list'),
        ('reward2', """ 'reward2': %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}

def diaryscore():
    return [
        ('score',  """   %s: { """,  'int'),
        ('reward', """ 'reward': %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}

def reward_diary():
    return [
        ('diary_ID',  """   %s: { """,  'int'),
        ('story', """ 'story': %s, """, 'unicode'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_data': %s, """, 'int_list'),
        ('reward_score', """ 'reward_score': %s, """, 'int'),
        ('num',         """ 'num': %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}

def wanted():
    return [
        ('wantedID',  """   %s: { """,  'int'),
        ('name', """ 'name': %s, """, 'unicode'),
        ('story', """ 'story': %s, """, 'unicode'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_data': %s, """, 'int_list'),
        ('target_data1', """ 'target_data1': %s, """, 'int_list'),
        ('reward',      """ 'reward': %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}

def notice():
    return [
        ('ID', """%s:{""", 'int',),
        ('trigger', "'trigger': %s,", 'int'),
        ('trigger_sort', "'trigger_sort': %s,", 'int'),
        ('notice_level', "'notice_level': %s,", 'int'),
        ('text', "'text': %s,", 'unicode'),
        ('is_self', "'is_self': %s", 'int'),
        ('END', """},""", 'None')
    ], {}


def adver_base():
    return [
        ('adver_id', """%s:{""", 'int',),
        ('adver_type', "'adver_type': %s,", 'int'),
        ('mark', "'mark': %s,", 'int'),
        ('start_time', "'start_time': %s,", 'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time', "'end_time': %s,", 'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('banner', "'banner': %s,", 'str'),
        ('title', "'title': %s,", 'unicode'),
        ('ad_title', "'ad_title': %s,", 'unicode'),
        ('word', "'word': %s,", 'unicode'),
        ('time', "'time': %s,", 'unicode'),
        ('server_time', "'server_time': %s,", 'unicode'),
        ('END', """},""", 'None')
    ], {}

adver = adver_base
adver_guild = adver_base
adver_inheritance = adver_base

def server_adver():
    return [
        ('adver_id', """%s:{""", 'int',),
        ('adver_type', "'adver_type': %s,", 'int'),
        ('mark', "'mark': %s,", 'int'),
        ('start_time', "'start_time': %s,", 'str'),
        ('end_time', "'end_time': %s,", 'str'),
        ('banner', "'banner': %s,", 'str'),
        ('title', "'title': %s,", 'unicode'),
        ('ad_title', "'ad_title': %s,", 'unicode'),
        ('word', "'word': %s,", 'unicode'),
        ('time', "'time': %s,", 'unicode'),
        ('server_time', "'server_time': %s,", 'unicode'),
        ('END', """},""", 'None')
    ], {}

def robot():
    """# robot: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('user_id',               """'robot_%s': {         """ , 'int'),
        ('top',                   "'top': %s,"                 , 'int_list'),
        ('formation_type',        "'formation_type': %s,"      , 'int_list'),
        ('role',                  "'role': %s,"                , 'int'),
        ('role_level',            "'role_level': %s,"          , 'int_list'),
        ('character_level',       "'character_level': %s,"     , 'int_list'),
        ('evo_level',             "'evo_level': %s,"           , 'int_list'),
        ('skill_level',           "'skill_level': %s,"         , 'int_list'),
        ('leader_skill_1_key',    "'leader_skill_1_key': %s,"  , 'int'),
        ('leader_skill_1_level',  "'leader_skill_1_level': %s,", 'int'),
        ('leader_skill_2_key',    "'leader_skill_2_key': %s,"  , 'int'),
        ('leader_skill_2_level',  "'leader_skill_2_level': %s,", 'int'),
        ('leader_skill_3_key',    "'leader_skill_3_key': %s,"  , 'int'),
        ('leader_skill_3_level',  "'leader_skill_3_level': %s,", 'int'),
        ('END',                "},", 'None')
    ], {}

def formation_type():
    return [
        ('typeID',   "%s:{                  ", 'int',),
        ('formation_ID',          "'formation_id': %s,"    , 'int'),
        ('position1',             "'position1': %s,"       , 'int'),
        ('position2',             "'position2': %s,"       , 'int'),
        ('position3',             "'position3': %s,"       , 'int'),
        ('position4',             "'position4': %s,"       , 'int'),
        ('position5',             "'position5': %s,"       , 'int'),
        ('position6',             "'position6': %s,"       , 'int'),
        ('position7',             "'position7': %s,"       , 'int'),
        ('position8',             "'position8': %s,"       , 'int'),
        ('END',                "},", 'None')
    ], {}

def exchange():
    return [
        ('id', """%s:{""", 'int',),
        ('change_sort', "'change_sort': %s,", 'int'),
        ('change_id', "'change_id': %s,", 'int_list', check_reward(),),
        ('need_food', "'need_food': %s,", 'int'),
        ('need_metal', "'need_metal': %s,", 'int'),
        ('need_item', "'need_item': %s,", 'int'),
        ('need_num', "'need_num': %s,", 'int_list'),
        ('refesh', "'refesh': %s,", 'int'),
        ('change_time', "'change_time': %s,", 'int'),
        ('shade', "'shade': %s,", 'str'),
        ('END', """},""", 'None')
    ], {}


if settings.ENV_NAME in [settings.ENV_IOS, settings.ENV_STG_IOS, settings.ENV_TEST_IOS]:
    def version():
        return [
            ('server_name', """%s:{""", 'str',),
            ('version', "'version': %s,", 'str'),
            ('url', "'url': %s,", 'str'),
            ('msg', "'msg': %s,", 'unicode'),
            ('END', "},", 'None')
        ], {}
else:
    def version():
        pts = {'sogou','androidcmge','itools','pp','duoku','37wan','jinli',
               'huawei','youle','360','xiaomi','anzhi','wandoujia','91',
               'kuaiyong','tongbu','cmge','4399','lenovo','vivo','yingyonghui',
               'youku','uc','jinshan','downjoy','oppo',
               'qitian', 'xmw', 'putao', 'muzhiwan', 'qiku', 'nduo', 'zhangyue', '49you',
               'ewan', 'kuaiwan', 'pps', 'haima', 'kugou', '37wana545', '37wana668', '37wana669', '37wana729',
               'pipa', 'mogu'}

        d = [('server_name', """%s:{""", 'str',),]
        for pt in pts:
            d.append((pt, "'%s':" % pt + '%s,', 'unicode_list'))
        d.append(('END', "},", 'None'))
        return d, {}


def active():
    return [
        ('active_id' , """%s: {                """, 'int') ,
        ('button'    , """    'button': %s,    """, 'str') ,
        ('open_time_word', """    'open_time_word': %s, """, 'unicode'),
        ('banner'    , """    'banner': %s,    """, 'str') ,
        ('des'       , """    'des': %s,       """, 'unicode') ,
        ('active_chapterID'  , """ 'active_chapterID': %s,       """, 'int_list') ,
        ('level'       , """    'level': %s,       """, 'int_list') ,
        ('is_see'       , """    'is_see': %s,       """, 'int') ,
        ('reward_show',       "'reward_show': %s," , 'int_list', check_reward(),),
        ('END'       , """},                   """, 'None'),
    ], {}


def active_chapter():
    return [
        ('active_chapterID',   "%s:{                  ", 'str',),
        ('ccb_resouce',        "'ccb_resouce': %s,"    , 'str'),
        ('active_detail',      "'active_detail': %s,"  , 'int_list'),
        ('open',               "'open': %s,"           , 'int_list'),
        ('lever',               "'level': %s,"           , 'int_list'),
        ('minus_sort', "'minus_sort': %s,"     , 'int'),
        ('times',              "'times': %s,"          , 'int'),
        ('time_sort',          "'time_sort': %s,"      , 'int'),
        ('vip_buy',            "'vip_buy': %s,"        , 'int_list'),
        ('button',            "'button': %s,"          , 'str'),
        ('banner',            "'banner': %s,"          , 'str'),
        ('open_time_word',    "'open_time_word': %s,"      , 'unicode'),
        ('des',            "'des': %s,"      , 'unicode'),
        ('is_see',            "'is_see': %s,"      , 'int'),
        ('reward_show',       "'reward_show': %s," , 'int_list', check_reward(),),
        ('loot',              "'loot': %s,       " , 'int'),
        ('exp_role',          "'exp_role': %s,   " , 'int'),
        ('exp_character',     "'exp_character': %s," , 'int'),
        ('action_point',      "'action_point': %s," , 'int'),
        ('END',                "},", 'None')
    ], {}


def hero_chapter():
    return [
        ('active_chapterID',   "%s:{                  ", 'str',),
        ('ccb_resouce',        "'ccb_resouce': %s,"    , 'str'),
        ('active_detail',      "'active_detail': %s,"  , 'int_list'),
        ('open',               "'open': %s,"           , 'int_list'),
        ('lever',               "'level': %s,"           , 'int_list'),
        ('minus_sort', "'minus_sort': %s,"     , 'int'),
        ('times',              "'times': %s,"          , 'int'),
        ('time_sort',          "'time_sort': %s,"      , 'int'),
        ('vip_buy',            "'vip_buy': %s,"        , 'int_list'),
        ('button',            "'button': %s,"          , 'str'),
        ('banner',            "'banner': %s,"          , 'str'),
        ('open_time_word',    "'open_time_word': %s,"      , 'unicode'),
        ('des',            "'des': %s,"      , 'unicode'),
        ('is_see',            "'is_see': %s,"      , 'int'),
        ('reward_show',       "'reward_show': %s," , 'int_list'),
        ('loot',              "'loot': %s,       " , 'int'),
        ('exp_role',          "'exp_role': %s,   " , 'int'),
        ('exp_character',     "'exp_character': %s," , 'int'),
        ('action_point',      "'action_point': %s," , 'int'),
        ('own',               "'own': %s," ,          'str'),
        ('END',                "},", 'None')
    ], {}


def active_detail():
    return [
        ('active_ID',      "%s:{                  ", 'str',),
        ('active_name',    "'active_name': %s,    ", 'unicode'),
        ('combat_need',    "'combat_need': %s,    ", 'int'),
        ('boss_resource',    "'boss_resource': %s,", 'str'),
        ('back_resource',    "'back_resource': %s,", 'str'),
        ('rgb',             "'rgb': %s,           ", 'int'),
        ('active_des',      "'active_des': %s,    ", 'unicode'),
        ('fight',           "'fight': %s,         ", 'unicode_int_list'),
        ('action_point',    "'action_point': %s,  ", 'int'),
        ('reward',          "'reward': %s,        ", 'int_list', check_reward(),),
        ('reward2',          "'reward2': %s,        ", 'int_list', check_reward(),),
        ('reward2_time',    "'reward2_time': %s,", 'str'),
        ('times',           "'times' : %s,        ", 'int'),
        ('reward_first_base', "'reward_first_base': %s,        ", 'int_list', check_reward(),),
        ('reward_first_rate', "'reward_first_rate': %s,        ", 'int_list', check_reward(is_random=True),),
        ('reward_sweep_base', "'reward_sweep_base': %s,        ", 'int_list', check_reward(),),
        ('reward_sweep_rate', "'reward_sweep_rate': %s,        ", 'int_list', check_reward(is_random=True),),
        ('background',          "'background': %s,        ", 'str'),
        ('level',      "'level': %s," , 'int_list'),
        ('END',                "},", 'None')
    ], {}

def active_fight_forever():
    return [
        ('fight_level',      " %s:{                 ", 'int',),
        ('name',             "'name': %s,           ", 'unicode'),
        ('animation',        "'animation': %s,      ", 'str'),
        ('background',        "'background': %s,      ", 'str'),
        ('fight',            "'fight': %s,          ", 'int'),
        ('reward',           "'reward': %s,         ", 'int_list', check_reward(),),
        ('reward2',           "'reward2': %s,         ", 'int_list', check_reward(),),
        ('reward2_time',        "'reward2_time': %s,      ", 'str'),
        ('fight_num',        "'fight_num': %s,      ", 'int'),
        ('END',                "},", 'None')
    ], {}

def star_reward():
    return [
        ('id',      " %s:{                 ", 'int',),
        ('icon',             "'icon': %s,           ", 'str'),
        ('star',             "'star': %s,           ", 'int'),
        ('reward',           "'reward': %s,         ", 'int_list', check_reward(),),
        ('quality',          "'quality': %s,        ", 'int'),
        ('END',                "},", 'None')
    ], {}

def race():
    return [
        ('race_ID',      "%s:{                  ", 'int',),
        ('name',         "'name': %s,           ", 'unicode'),
        ('END',                "},", 'None')
    ], {}

def vip():
    return [
        ('vip_lv',       " %s:{                             ", 'int',),
        ('need_exp',           "'need_exp': %s,             ", 'int'),
        ('fight_skip',         "'fight_skip': %s,           ", 'int'),
        ('exp_inherit',        "'exp_inherit': %s,          ", 'int'),
        ('sweep_fast',         "'sweep_fast': %s,           ", 'int'),
        ('world_boss_skip',    "'world_boss_skip': %s,      ", 'int'),
        ('active_times',       "'active_times': %s,         ", 'int'),
        ('sweep_times',        "'sweep_times': %s,          ", 'int'),
        ('arena_skip',         "'arena_skip': %s,           ", 'int'),
        ('fast_quest',         "'fast_quest': %s,           ", 'int'),
        ('world_boss_revive',  "'world_boss_revive': %s,    ", 'int'),
        ('world_boss_auto',    "'world_boss_auto': %s,      ", 'int'),
        ('fast_train',         "'fast_train': %s,      ", 'int'),
        ('buy_point',     "'buy_point': %s,      ", 'int'),
        ('buy_arena',     "'buy_arena': %s,      ", 'int'),
        ('refresh_dirtshop',     "'refresh_dirtshop': %s,      ", 'int'),
        ('auto_fight',           "'auto_fight': %s,            ", 'int'),
        ('treasure_time',           "'treasure_time': %s,            ", 'int'),
        ('story',     "'story': %s,      ", 'unicode'),
        ('buy_godlike',     "'buy_godlike': %s,      ", 'int'),
        ('buy_wakuang2',     "'buy_wakuang2': %s,      ", 'int'),
        ('train_times',     "'train_times': %s,      ", 'int'),
        ('END',                "},", 'None')
    ], {}

def pay():
    return [
        ('pay_id',       " %s:{             ", 'int',),
        ('coin',         " 'coin': %s,      ", 'int_list'),
        ('END',          " },               ", 'None')
    ], {}

def world_boss():
    return [
        ('world_boss',       " %s:{                  ", 'int',),
        ('image',            "'image': %s,           ", 'str'),
        ('time_sort', "'time_sort': %s,       ", 'int'),
        ('open',             "'open': %s,            ", 'str'),
        ('close',            "'close': %s,           ", 'str'),
        ('limit_lv',         "'limit_lv': %s,        ", 'int'),
        ('background',       "'background': %s,    ", 'str'),
        ('reward_id',        "'reward_id': %s,       ", 'int'),
        ('enemy_id',         "'enemy_id': %s,        ", 'int'),
        ('hp_add_5',           "'hp_add_5': %s,          ", 'int'),
        ('hp_add_10',          "'hp_add_10': %s,          ", 'int'),
        ('hp_add_13',          "'hp_add_13': %s,          ", 'int'),
        ('hp_add_15',          "'hp_add_15': %s,          ", 'int'),
        ('reduce',             "'reduce': %s,          ", 'int'),
        ('END',                "},", 'None')
    ], {}

def world_boss_reward():
    return [
        ('reward_id',       " %s:{                   ", 'int',),
        ('kill',           "'kill': %s,              ", 'int_list', check_reward(),),
        ('top1',           "'top1': %s,              ", 'int_list', check_reward(),),
        ('top2',           "'top2': %s,              ", 'int_list', check_reward(),),
        ('top3',           "'top3': %s,              ", 'int_list', check_reward(),),
        ('top10',          "'top10': %s,             ", 'int_list', check_reward(),),
        ('all_player',     "'all_player': %s,        ", 'int_list', check_reward(),),
        ('guild1',         "'guild1': %s,            ", 'int_list'),
        ('guild2',         "'guild2': %s,            ", 'int_list'),
        ('guild3',         "'guild3': %s,            ", 'int_list'),
        ('END',                "},", 'None')
    ], {}

def godgift():
        return [
        ('ID',       " %s:{                   ", 'int',),
        ('level',         "'level': %s,            ", 'int_list'),
        ('cost',          "'cost': %s,            ", 'int'),
        ('reward',         "'reward': %s,            ", 'int_list', check_reward(is_random=True),),
        ('END',                "},", 'None')
    ], {}

godgift_pvp = godgift

def character_book():
    return [
        ('book_id',         " %s:{                   ", 'int',),
        ('character_id',    "'character_id': %s,            ", 'int'),
        ('is_see',          "'is_see': %s,            ", 'int'),
        ('END',                "},", 'None')
    ], {}

def equip_book():
    return [
        ('book_id',         " %s:{                   ", 'int',),
        ('equip_id',        "'equip_id': %s,            ", 'int'),
        ('sort',            "'sort': %s,              ", 'int'),
        ('is_see',          "'is_see': %s,            ", 'int'),
        ('go_to',            "'go_to': %s,            ", 'int_list'),
        ('END',                "},", 'None')
    ], {}

def level_reward():
    return [
        ('ID',         " %s:{                   ", 'int',),
        ('title',      "'title': %s,            ", 'unicode'),
        ('need_level',          "'need_level': %s,            ", 'int'),
        ('icon',                "'icon': %s,              ", 'str'),
        ('reward',              "'reward': %s,            ", 'int_list', check_reward(),),
        ('des',                 "'des': %s,               ", 'unicode'),
        ('END',                "},", 'None')
    ], {}

def chargereward():
    return [
        ('ID',         " %s:{                   ", 'int',),
        ('title',      "'title': %s,            ", 'unicode'),
        ('need_charge',         "'need_charge': %s,            ", 'int'),
        ('icon',                "'icon': %s,              ", 'str'),
        ('reward',              "'reward': %s,            ", 'int_list', check_reward(),),
        ('des',                 "'des': %s,               ", 'unicode'),
        ('END',                "},", 'None')
    ], {}

def commander_type():
    return [
        ('level',         " %s:{                   ", 'int',),
        ('exp',                 "'exp': %s,            ", 'int'),
        ('add_patk',            "'add_patk': %s,              ", 'int'),
        ('add_matk',            "'add_matk': %s,              ", 'int'),
        ('add_def',             "'add_def': %s,              ", 'int'),
        ('add_hp',              "'add_hp': %s,              ", 'int'),
        ('add_speed',           "'add_speed': %s,              ", 'int'),
        ('add_hp2',             "'add_hp2'  : %s,              ", 'int'),
        ('add_hp3',             "'add_hp3'  : %s,               ", 'int'),
        ('add_firedfs',         "'add_firedfs'  : %s,           ", 'int'),
        ('add_waterdfs',        "'add_waterdfs'  : %s,          ", 'int'),
        ('add_winddfs',         "'add_winddfs'  : %s,           ", 'int'),
        ('add_earthdfs',        "'add_earthdfs'  : %s,          ", 'int'),
        ('END',                "},", 'None')
    ], {}

def commander_recipe():
    return [
        ('recipe_ID',         " %s:{                       ", 'int',),
        ('name',                  "'name': %s,            ", 'unicode'),
        ('part',                  "'part': %s,            ", 'int_list'),
        ('PVE_rate',              "'pve_rate': %s,        ", 'float'),
        ('PVP_rate',              "'pvp_rate': %s,        ", 'float'),
        ('exp',                   "'exp': %s,             ", 'int'),
        ('sort',                  "'sort': %s,            ", 'int'),
        ('is_show',               "'is_show': %s,         ", 'int'),
        ('icon',                  "'icon': %s,            ", 'str'),
        ('quality',               "'quality': %s,         ", 'int'),
        ('reward',                "'reward': %s,          ", 'int_list', check_reward(),),
        ('type',                  "'type': %s,            ", 'int'),
        ('END',                "},", 'None')
    ], {}
item_recipe = commander_recipe

def item_recipe_show():
    return [
        ('sort_id',   "%s: {            ", 'int',),
        ('name',       "    'name':  %s, ", 'unicode',),
        ('item_image', "    'item_image':  %s, ", 'str',),
        ('image',      "    'image': %s, ", 'str',),
        ('item_id',    "    'item_id': %s, ", 'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def commander_level():
    return [
        ('sort',   "%s: {            ", 'int',),
        ('show_level',      "    'show_level':  %s, ", 'int',),
        ('able_level',      "    'able_level': %s, ", 'int',),
        ('END',        "},               ", 'None')
    ], {}


def assistant():
    return [
        ('position',   "%s: {            ", 'int',),
        ('sort',       "    'sort':  %s, ", 'int',),
        ('price',      "    'price': %s, ", 'int',),
        ('actlv',      "    'actlv': %s, ", 'int',),
        ('activation',      "    'activation': %s, ", 'int_list', check_reward(),),
        ('level_up',      "    'level_up': %s, ", 'int_list',),
        ('cardlimit',      "    'cardlimit': %s, ", 'int',),
        ('att_type',      "    'att_type': %s, ", 'int',),
        ('att_value',      "    'att_value': %s, ", 'int',),
        ('ability1',      "    'ability1': %s, ", 'int_list',),
        ('att_type2',      "    'att_type2': %s, ", 'int',),
        ('ability2',      "    'ability2': %s, ", 'int_list',),
        ('card',      "    'card': %s, ", 'int_list',),
        ('card_ability',      "    'card_ability': %s, ", 'int',),
        ('card_value',      "    'card_value': %s, ", 'float',),
        ('refresh',      "    'refresh': %s, ", 'int',),
        ('lock',      "    'lock': %s, ", 'int',),
        ('max_ability1',      "    'max_ability1': %s, ", 'int',),
        ('max_ability2',      "    'max_ability2': %s, ", 'int',),
        ('END',        "},               ", 'None')
    ], {}


def destiny():
    return [
        ('position',   "%s: {            ", 'int',),
        ('sort',       "    'sort':  %s, ", 'int',),
        ('price',      "    'price': %s, ", 'int',),
        ('limit_lv',      "    'limit_lv': %s, ", 'int',),
        ('END',        "},               ", 'None')
    ], {}


def assistant_random():
    return [
        ('ID',   "%s: {            ", 'int',),
        ('ability',       "    'ability':  %s, ", 'float',),
        ('weight',      "    'weight': %s, ", 'int',),
        ('quality',      "    'quality': %s, ", 'int',),
        ('END',        "},               ", 'None')
    ], {}


def vip_guide():
    return [
        ('vipguide',   "%s: {            ",   'int',),
        ('title',       "    'title':  %s, ", 'unicode',),
        ('lv',          "    'lv': %s, ",     'int',),
        ('reward',      "    'reward': %s, ", 'int_list', check_reward(),),
        ('coin',        "    'coin': %s, ",   'int',),
        ('END',        "},               ", 'None')
    ], {}

def outlets():
        return [
        ('outlets_id',   "%s: {            ",   'int',),
        ('team',         "    'team': %s, ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def outlets_team():
        return [
        ('team_id',     "%s: {            ",   'int',),
        ('num',          "    'num': %s, ",    'int',),
        ('reward1',      "    'reward1': %s, ",    'int_list', check_reward(),),
        ('level1',       "    'level1':  %s, ",    'int_list',),
        ('coin1',         "   'coin1': %s, ",      'int',),

        ('reward2',      "    'reward2': %s, ",    'int_list', check_reward(),),
        ('level2',       "    'level2':  %s, ",    'int_list',),
        ('coin2',         "   'coin2': %s, ",      'int',),

        ('reward3',      "    'reward3': %s, ",    'int_list', check_reward(),),
        ('level3',       "    'level3':  %s, ",    'int_list',),
        ('coin3',         "   'coin3': %s, ",      'int',),

        ('reward4',      "    'reward4': %s, ",    'int_list', check_reward(),),
        ('level4',       "    'level4':  %s, ",    'int_list',),
        ('coin4',         "   'coin4': %s, ",      'int',),

        ('reward5',      "    'reward5': %s, ",    'int_list', check_reward(),),
        ('level5',       "    'level5':  %s, ",    'int_list',),
        ('coin5',         "   'coin5': %s, ",      'int',),
        ('END',        "},               ", 'None')
    ], {}

def inreview():
    return [
        ('ID',   "%s: {            ",   'int',),
        ('is_open',      "    'is_open': %s, ",    'int',),
        ('name',         "    'name': %s, ",    'unicode',),
        ('story',        "    'story': %s, ",   'unicode',),
        ('show_lv',        "    'show_lv': %s, ",   'int',),
        ('END',        "},               ", 'None')
    ], {}

def resoucequality():
    return [
        ('resource_ID',   "%s: {            ",   'int',),
        ('quailty0',         "    'quailty0': %s, ",    'int_list',),
        ('quailty1',         "    'quailty1': %s, ",    'int_list',),
        ('quailty2',         "    'quailty2': %s, ",    'int_list',),
        ('quailty3',         "    'quailty3': %s, ",    'int_list',),
        ('quailty4',         "    'quailty4': %s, ",    'int_list',),
        ('quailty5',         "    'quailty5': %s, ",    'int_list',),
        ('quailty6',         "    'quailty6': %s, ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def request_code():
    return [
        ('request_id',   "%s: {            ",   'int',),
        ('level',      "    'level': %s,  ",    'int_list',),
        ('player',     "    'player': %s, ",    'int_list', check_reward(),),
        ('quest',      "    'quest': %s,  ",    'int_list', check_reward(),),
        ('END',        "},               ", 'None')
    ], {}

def notice_active():
    return [
        ('id',   "%s: {            ",   'int',),
        ('word',       "    'word': %s,   ",    'unicode',),
        ('reward',     "    'reward': %s, ",    'int_list', check_reward(),),
        ('END',        "},               ", 'None')
    ], {}

def whats_inside():
    return [
        ('id',   "%s: {            ",   'int',),
        ('whats_inside',      "    'whats_inside': %s,  ",    'int_list', check_reward(is_random=True),),
        ('END',        "},               ", 'None')
    ], {}

def login_reward():
    return [
        ('ID',   "%s: {              ",   'int',),
        ('open',        "    'open': %s,   ",    'str',),
        ('close',       "    'close': %s,  ",    'str',),
        ('reward',      "    'reward': %s,  ",    'int_list', check_reward(),),
        ('des',         "    'des': %s,  ",       'unicode',),
        ('times',       "    'times': %s,  ",     'int',),
        ('level',       "    'level': %s,  ",     'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def reward_gacha():
    return [
        ('reward_gacha_ID', "%s: {                  ",   'int'),
        #('story',           "    'story'       : %s,",   'unicode'),
        ('target_sort',     "    'target_sort' : %s,",   'int'),
        ('target_data',     "    'target_data' : %s,",   'int'),
        ('reward_score',    "    'reward_score': %s,",   'int'),
        ('END', "},", 'None')
    ], {}

def gacha_score():
    return [
        ('score',  "%s: {",   'int'),
        ('reward', "    'reward': %s,",   'int_list', check_reward(),),
        ('END', "},", 'None')
    ], {}

def gacha_gift():
    return [
        ('rank_id', "%s: {               ",   'int'),
        ('rank',     "    'rank'    : %s,",   'int'),
        ('rank_low', "    'rank_low': %s,",   'int'),
        ('reward',   "    'reward'  : %s,",   'int_list', check_reward(),),
        ('END', "},", 'None')
    ], {}

def box_reward():
    return [
        (('ID', 'num', 'reward'),
         """%s: [{'nums': %s, 'reward': %s, 'num': 1}], """,
         ('int', 'int_single_list', 'int_list'),
        (None, None, check_reward())),
    ], {}

box_reward_42 = box_reward
box_reward_99999 = box_reward
box_reward_99994 = box_reward
box_reward_99967 = box_reward
box_reward_99861 = box_reward
box_reward_99833 = box_reward
box_reward_99810 = box_reward
box_reward_99792 = box_reward

def item_integration():
    return [
        ('item_id',   "%s: {              ",   'int',),
        ('name',        "    'name'        : %s,",    'unicode'),
        ('integration', "    'integration' : %s,",    'int'),
        ('END',        "},               ", 'None')
    ], {}

def integration_shop():
    return [
        ('shop',   "%s: {              ",   'int',),
        ('shop_reward', "    'shop_reward': %s,",    'int_list', check_reward(),),
        ('need_sort',   "    'need_sort'  : %s,",    'int'),
        ('need_value',  "    'need_value' : %s,",    'int_list'),
        ('sell_off',    "    'sell_off'   : %s,",    'int'),
        ('sell_sort',   "    'sell_sort'  : %s,",    'int'),
        ('sell_max',    "    'sell_max'   : %s,",    'int'),
        ('show_level',  "    'show_level' : %s,",    'int_list'),
        ('im_use',      "    'im_use'     : %s,",    'int'),
        ('END',        "},               ", 'None')
    ], {}

def ranking():
    return [
        ('ranking_ID',   "%s: {      ",    'int',),
        ('icon',   "    'icon'  : %s,",    'str'),
        ('name',   "    'name'  : %s,",    'unicode'),
        ('story',  "    'story' : %s,",    'unicode'),
        ('team',   "    'team'  : %s,",    'int'),
        ('reward', "    'reward': %s,",    'int_list', check_reward(),),
        ('rank',   "    'rank'  : %s,",    'int_list', check_int_list_args(2)),
        ('END',        "},               ", 'None')
    ], {}


def integration_world():
    return [
        ('id',   "%s: {              ",   'int',),
        ('icon',        "    'icon': %s,   ",    'str',),
        ('top',         "    'top': %s,  ",      'int',),
        ('world_reward',"    'reward': %s,  ",   'int_list', check_reward(),),
        ('world_id',"    'world_id': %s,  ",   'int',),
        ('END',        "},               ", 'None')
    ], {}

def auto_sweep():
    return [
        ('title_id',   "%s: {              ",   'str',),
        ('stage_id',    "    'stage_id': %s,   ",    'str',),
        ('chapter_id',  "    'chapter_id': %s, ",    'int',),
        ('item_id',  "       'item_id': %s, ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def gacha_reward_score():
    return [
        ('ID',   "%s: {              ",   'int',),
        ('open',        "    'open': %s,   ",    'str',),
        ('close',       "    'close': %s,  ",    'str',),
        ('score',       "    'score': %s,  ",    'int',),
        ('reward',      "    'reward': %s,  ",    'int_list', check_reward(),),
        ('des',         "    'des': %s,  ",       'unicode',),
        ('times',       "    'times': %s,  ",     'int',),
        ('END',        "},               ", 'None')
    ], {}

def guild_boss():
    return [
        ('world_boss',       " %s:{                  ", 'int',),
        ('image',            "'image': %s,           ", 'str'),
        ('time_sort', "'time_sort': %s,       ", 'int'),
        ('open',             "'open': %s,            ", 'str'),
        ('close',            "'close': %s,           ", 'str'),
        ('limit_lv',         "'limit_lv': %s,        ", 'int'),
        ('background',       "'background': %s,    ", 'str'),
        ('reward_id',        "'reward_id': %s,       ", 'int'),
        ('enemy_id',         "'enemy_id': %s,        ", 'int'),
        ('hp_add_5',           "'hp_add_5': %s,          ", 'int'),
        ('hp_add_10',          "'hp_add_10': %s,          ", 'int'),
        ('hp_add_13',          "'hp_add_13': %s,          ", 'int'),
        ('hp_add_15',          "'hp_add_15': %s,          ", 'int'),
        ('reduce',             "'reduce': %s,          ", 'int'),
        ('END',                "},", 'None')
    ], {}

def guild_boss_reward():
    return [
        ('reward_id',       " %s:{                   ", 'int',),
        ('kill',           "'kill': %s,              ", 'int_list', check_reward(),),
        ('top1',           "'top1': %s,              ", 'int_list'),
        ('top2',           "'top2': %s,              ", 'int_list'),
        ('top3',           "'top3': %s,              ", 'int_list'),
        ('top10',          "'top10': %s,             ", 'int_list'),
        ('all_player',     "'all_player': %s,        ", 'int_list', check_reward(),),
        ('guild1',         "'guild1': %s,            ", 'int_list'),
        ('guild2',         "'guild2': %s,            ", 'int_list'),
        ('guild3',         "'guild3': %s,            ", 'int_list'),
        ('END',                "},", 'None')
    ], {}

def loot_id():
    return [(
             ('id', 'sort'),
            """ %s: %s,""",
            ('int', 'int')
    )], {}


def logreward():
    return [
        ('ID',         "%s: {              ",    'int',),
        ('day_id',    "    'day_id': %s, ",    'int',),
        ('open',       "    'open': %s,    ",    'str',),
        ('close',      "    'close': %s,   ",    'str',),
        ('title',      "    'title': %s,   ",    'unicode',),
        ('severid',    "    'severid': %s, ",    'str_list',),
        ('level',      "    'level': %s,   ",    'int_list',),
        ('reward',     "    'reward': %s,  ",    'int_list', check_reward(),),
        ('des',        "    'des': %s,     ",    'unicode',),
        ('version',    "    'version': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def player_boss():
    return [
        ('id',         "%s: {               ",    'int',),
        ('reward',     "    'reward': %s,   ",    'int_list', check_reward(),),
        ('condition',  "    'condition': %s,",    'int',),
        ('mail',       "    'mail': %s,     ",    'unicode',),
        ('END',        "},                  ",    'None')
    ], {}


# 赛亚人
def super_rich():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',   " 'version': %s,",     'int',),
        ('rank',   " 'rank': %s,",     'int',),
        ('start_time',   " 'start_time': %s,",     'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time',     " 'end_time' : %s,",      'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('reward_12',    " 'reward_12': %s, ",     'int_list', check_reward(),),
        ('reward_21',    " 'reward_21': %s, ",     'int_list', check_reward(),),
        ('reward_24',    " 'reward_24': %s, ",     'int_list', check_reward(),),
        ('des',          " 'des': %s,       ",     'unicode',),
        ('notice',   " 'notice': %s,",     'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


# 神龙
def super_all():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',   " 'version': %s,",     'int',),
        ('start_time',   " 'start_time': %s,",     'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time',     " 'end_time' : %s," ,     'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('score',        " 'score': %s, "    ,     'int',),
        ('base',         " 'base': %s, "     ,     'int',),
        ('reward',       " 'reward': %s, "   ,     'int_list', check_reward(),),
        ('show',         " 'show'  : %s, "   ,     'int_list', check_reward(),),
        ('shop_id',      " 'shop_id': %s, "   ,    'int',),
        ('notice',      " 'notice': %s, "   ,    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


# 新服赛亚人
def server_super_rich():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',   " 'version': %s,",     'int',),
        ('rank',   " 'rank': %s,",     'int',),
        ('reward_12',    " 'reward_12': %s, ",     'int_list',),
        ('reward_21',    " 'reward_21': %s, ",     'int_list',),
        ('reward_24',    " 'reward_24': %s, ",     'int_list',),
        ('des',          " 'des': %s,       ",     'unicode',),
        ('notice',   " 'notice': %s,",     'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


# 新服神龙
def server_super_all():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',   " 'version': %s,",     'int',),
        ('score',        " 'score': %s, "    ,     'int',),
        ('base',         " 'base': %s, "     ,     'int',),
        ('reward',       " 'reward': %s, "   ,     'int_list',),
        ('show',         " 'show'  : %s, "   ,     'int_list',),
        ('shop_id',      " 'shop_id': %s, "   ,    'int',),
        ('notice',      " 'notice': %s, "   ,    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def scorewall():
    return [
        (('id', 'level'),
         """%s:  %s,""",
         ('str', 'int')),
    ], {}


def map_treasure_detail_battle():
    return [
        ('title_id',         """'%s': {                      """ , 'int'),
        ('title_img',        """    'title_img'            : %s, """ , 'str'),
        ('title_name',       """    'title_name'           : %s, """ , 'unicode'),
        ('title_detail',       """    'title_detail'           : %s, """ , 'unicode'),
        ('title_name_after', """    'title_name_after'     : %s, """ , 'unicode'),
        ('tips_detail', """    'tips_detail'     : %s, """ , 'unicode'),
        ('loot_show_image', """    'loot_show_image'     : %s, """ , 'int_list'),
        ('loot_show',       """    'loot_show'             : %s, """ , 'str'),
        ('after_show',       """    'after_show'           : %s, """ , 'str'),
        ('background',       """    'background'           : %s, """ , 'str'),
        ('sort',      """    'sort'          : %s, """ , 'int'),
        ('fight',            """    'fight_list'           : %s, """ , 'unicode_int_list'),
        ('buff_detail',          """    'buff_detail'              : %s, """ , 'int_list'),
        ('reward_sort',          """    'reward_sort'              : %s, """ , 'int'),
        ('reward_num',          """    'reward_num'              : %s, """ , 'int'),
        ('reward_detail',          """    'reward_detail'  : %s, """ , 'int_list', check_reward(is_random=True),),
        ('END',              """},                           """ , 'None'),
    ], {}


def treasure():
    return [
        ('id',         """'%s': {                      """ , 'int'),
        ('name',        """    'name'            : %s, """ , 'unicode'),
        ('boss_resource',       """    'boss_resource'           : %s, """ , 'str'),
        ('map_id',       """    'map_id'           : %s, """ , 'int'),
        ('size_x',       """    'size_x'           : %s, """ , 'int'),
        ('size_y',       """    'size_y'           : %s, """ , 'int'),
        ('combat_need',       """    'combat_need'           : %s, """ , 'int'),
        ('what_inside', """    'what_inside'     : %s, """ , 'int_list', check_reward(is_random=True),),
        ('hp_basic',            """    'hp_basic'           : %s, """ , 'int'),
        ('hp_heal_time',      """    'hp_heal_time'          : %s, """ , 'int'),
        ('hp_heal_percent',          """    'hp_heal_percent'              : %s, """ , 'int'),
        ('map_random',          """    'map_random'              : %s, """ , 'int_list'),
        ('total_reward1',          """    'total_reward1'        : %s, """ , 'int_list', check_reward(is_random=True),),
        ('reward_num1',          """    'reward_num1'              : %s, """ , 'int'),
        ('percent1',          """    'percent1'              : %s, """ , 'int'),
        ('total_reward2',          """    'total_reward2'        : %s, """ , 'int_list', check_reward(is_random=True),),
        ('reward_num2',          """    'reward_num2'              : %s, """ , 'int'),
        ('percent2',          """    'percent2'              : %s, """ , 'int'),
        ('total_reward3',          """    'total_reward3'        : %s, """ , 'int_list', check_reward(is_random=True),),
        ('reward_num3',          """    'reward_num3'              : %s, """ , 'int'),
        ('percent3',          """    'percent3'              : %s, """ , 'int'),
        ('total_reward4',          """    'total_reward4'        : %s, """ , 'int_list', check_reward(is_random=True),),
        ('reward_num4',          """    'reward_num4'              : %s, """ , 'int'),
        ('percent4',          """    'percent4'              : %s, """ , 'int'),
        ('help_reward',          """    'help_reward'        : %s, """ , 'int_list', check_reward(is_random=True),),
        ('END',              """},                           """ , 'None'),
    ], {}


def map_treasure_battle_point():
    return [
        ('id',         """'%s': {                      """ , 'int'),
        ('self_up',        """    'self_up'            : %s, """ , 'int'),
        ('self_down',       """    'self_down'           : %s, """ , 'int'),
        ('match_up',       """    'match_up'           : %s, """ , 'int'),
        ('match_down',       """    'match_down'           : %s, """ , 'int'),
        ('arena_rank',       """    'arena_rank'           : %s, """ , 'int'),
        ('END',              """},                           """ , 'None'),
    ], {}


def roulette():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',"    'start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time',   "    'end_time': %s,   ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('refresh_price', "    'refresh_price': %s,   ",    'int',),
        ('price',      "    'price': %s, ",    'int',),
        ('price_10',   "    'price_10': %s,   ",    'int',),
        ('score',      "    'score': %s, ",    'int',),
        ('score_10',   "    'score_10': %s,   ",    'int',),
        ('day_refresh_num', "    'day_refresh_num': %s,  ",    'int',),
        ('day_num',        "    'day_num': %s,     ",    'int',),
        ('best_must_reward', "    'best_must_reward': %s, ",    'int',),
        ('must_reward',    "    'must_reward': %s, ",    'int',),
        ('instruction',    "    'instruction': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_roulette():
    return [
        ('version',    "%s: {              ",    'int',),
        ('refresh_price', "    'refresh_price': %s,   ",    'int',),
        ('price',      "    'price': %s, ",    'int',),
        ('price_10',   "    'price_10': %s,   ",    'int',),
        ('score',      "    'score': %s, ",    'int',),
        ('score_10',   "    'score_10': %s,   ",    'int',),
        ('day_refresh_num', "    'day_refresh_num': %s,  ",    'int',),
        ('day_num',        "    'day_num': %s,     ",    'int',),
        ('best_must_reward', "    'best_must_reward': %s, ",    'int',),
        ('must_reward',    "    'must_reward': %s, ",    'int',),
        ('instruction',    "    'instruction': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def roulette_rank_reward():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('reward_time',"    'reward_time': %s,    ",    'str',),
        ('rank',   "    'rank': %s,   ",    'int_single_list', check_int_list_args(2)),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('final_reward', "    'final_reward': %s,   ",    'int_list', check_reward(),),
        ('final_mail',      "    'final_mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_roulette_rank_reward():
    return [
        ('id',    "%s: {              ",    'int',),
        ('team',   "    'team': %s,   ",    'int',),
        ('rank',   "    'rank': %s,   ",    'int_single_list', check_int_list_args(2)),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('final_reward', "    'final_reward': %s,   ",    'int_list', check_reward(),),
        ('final_mail',      "    'final_mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def roulette_ranktime():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('reward_time',"    'reward_time': %s,    ",    'str',),
        ('rank',   "    'rank': %s,   ",    'int_single_list', check_int_list_args(2)),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_roulette_ranktime():
    return [
        ('id',    "%s: {              ",    'int',),
        ('team',   "    'team': %s,   ",    'int',),
        ('rank',   "    'rank': %s,   ",    'int_single_list', check_int_list_args(2)),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def roulette_reward():
    return [
        ('version',    "%s: {              ",    'int',),
        ('limit_ins',"    'limit_ins': %s,    ",    'unicode',),
        ('day_limite_reward',"    'day_limite_reward': %s,    ",    'int_list', check_reward(),),
        ('best_limite_reward',   "    'best_limite_reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('limite_reward',   "    'limite_reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward1', "    'common_reward1': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward2', "    'common_reward2': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward3', "    'common_reward3': %s,   ",    'int_list', check_reward(is_random=True),),
        ('reward_chance', "    'reward_chance': %s, ",    'int_list',),
        ('best_reward_show', "    'best_reward_show': %s, ",    'int_list',),
        ('reward_show', "    'reward_show': %s, ",    'int_list',),
        ('common_reward1_show', "    'common_reward1_show': %s, ",    'int_list',),
        ('common_reward2_show', "    'common_reward2_show': %s, ",    'int_list',),
        ('common_reward3_show', "    'common_reward3_show': %s, ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def book_character():
    return [
        ('id',         "%s: {              ",    'int',),
        ('book_id',       "    'book_id': %s,    ",    'int',),
        ('need_item',        "    'need_item': %s,     ",    'int_list', check_reward(),),
        ('out_item',        "    'out_item': %s,     ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}

def book_equip():
    return [
        ('id',         "%s: {              ",    'int',),
        ('book_id',       "    'book_id': %s,    ",    'int',),
        ('need_item',        "    'need_item': %s,     ",    'int_list', check_reward(),),
        ('out_item',        "    'out_item': %s,     ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}


def gem():
    return [
        ('gem_id',        "%s: {               ",    'str',),
        ('last_name',      "    'last_name': %s,   ",    'unicode'),
        ('first_name',     "    'first_name': %s,   ",    'unicode'),
        ('team',           "    'team': %s,   ",    'int'),
        ('icon',          "    'icon': %s,",    'str',),
        ('career',        "    'career': %s,     ",    'int',),
        ('quality',       "    'quality': %s,     ",    'int',),
        ('ability',       "    'ability': %s,     ",    'int',),
        ('value',         "    'value': %s,     ",    'int',),
        ('ability2',       "    'ability2': %s,     ",    'int',),
        ('value2',         "    'value2': %s,     ",    'int',),
        ('exchange',         "    'exchange': %s,     ",    'int_list',),
        ('need_gem',         "    'need_gem': %s,     ",    'int',),
        ('gem_num',          "    'gem_num': %s,",    'int',),
        ('iron',           "    'iron': %s,   ",    'int'),
        ('need_item',        "    'need_item': %s,     ",    'int_list', check_reward(),),
        ('END',           "},                  ",    'None')
    ], {}


def server_roulette_reward():
    return [
        ('day_id',    "%s: {              ",    'int',),
        ('limit_ins',"    'limit_ins': %s,    ",    'unicode',),
        ('day_limite_reward',"    'day_limite_reward': %s,    ",    'int_list', check_reward(),),
        ('best_limite_reward',   "    'best_limite_reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('limite_reward',   "    'limite_reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward1', "    'common_reward1': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward2', "    'common_reward2': %s,   ",    'int_list', check_reward(is_random=True),),
        ('common_reward3', "    'common_reward3': %s,   ",    'int_list', check_reward(is_random=True),),
        ('reward_chance', "    'reward_chance': %s, ",    'int_list',),
        ('best_reward_show', "    'best_reward_show': %s, ",    'int_list',),
        ('reward_show', "    'reward_show': %s, ",    'int_list',),
        ('common_reward1_show', "    'common_reward1_show': %s, ",    'int_list',),
        ('common_reward2_show', "    'common_reward2_show': %s, ",    'int_list',),
        ('common_reward3_show', "    'common_reward3_show': %s, ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def omni_exchange():
    return [
        ('id',         "%s: {               ",    'int',),
        ('show_id',     "    'show_id': %s,   ",    'int'),
        ('type',  "    'type': %s,",    'int',),
        ('exchange_type',       "    'exchange_type': %s,     ",    'int',),
        ('exchange_num',  "    'exchange_num': %s,",    'int',),
        ('exchange_time',  "    'exchange_time': %s,",    'int',),
        ('start_time',  "    'start_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M")),
        ('end_time',  "    'end_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M")),
        ('material_type',  "    'material_type': %s,",    'int',),
        ('step',  "    'step': %s,",    'int',),
        ('break',  "    'break': %s,",    'int',),
        ('strengthen',  "    'strengthen': %s,",    'int',),
        ('equip_st',  "    'equip_st': %s,",    'int',),
        ('need_item',  "    'need_item': %s,",    'int_list', check_reward(),),
        ('out_item1',  "    'out_item1': %s,",    'int_list', check_reward(),),
        ('out_item2',  "    'out_item2': %s,",    'int_list', check_reward(),),
        ('out_item3',  "    'out_item3': %s,",    'int_list', check_reward(),),
        ('out_item4',  "    'out_item4': %s,",    'int_list', check_reward(),),
        ('out_item5',  "    'out_item5': %s,",    'int_list', check_reward(),),
        ('END',        "},                  ",    'None')
    ], {}


def server_exchange():
    return [
        ('id',         "%s: {               ",    'int',),
        ('show_id',     "    'show_id': %s,   ",    'int'),
        ('exchange_num',  "    'exchange_num': %s,",    'int',),
        ('exchange_time',  "    'exchange_time': %s,",    'int',),
        ('start_time',  "    'start_time': %s,",    'str',),
        ('end_time',  "    'end_time': %s,",    'str',),
        ('material_type',  "    'material_type': %s,",    'int',),
        ('step',  "    'step': %s,",    'int',),
        ('break',  "    'break': %s,",    'int',),
        ('strengthen',  "    'strengthen': %s,",    'int',),
        ('equip_st',  "    'equip_st': %s,",    'int',),
        ('need_item',  "    'need_item': %s,",    'int_list', check_reward(),),
        ('out_item1',  "    'out_item1': %s,",    'int_list', check_reward(),),
        ('out_item2',  "    'out_item2': %s,",    'int_list', check_reward(),),
        ('out_item3',  "    'out_item3': %s,",    'int_list', check_reward(),),
        ('out_item4',  "    'out_item4': %s,",    'int_list', check_reward(),),
        ('out_item5',  "    'out_item5': %s,",    'int_list', check_reward(),),
        ('END',        "},                  ",    'None')
    ], {}


def active_recharge():
    return [
        ('id',    "%s: {              ",    'int',),
        ('show_id',        "'show_id': %s, ",        'int',),
        ('charge_type',    "'charge_type': %s, ",    'int',),
        ('repeat',         "'repeat': %s, ",         'int',),
        ('show_time',      "'show_time': %s, ",      'unicode',),
        ('start_time',     "'start_time': %s, ",     'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('end_time',       "'end_time': %s, ",    'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('num_type',       "'num_type': %s, ",    'int',),
        ('num',            "'num': %s, ",         'int',),
        ('reward',         "'reward': %s, ",      'int_list', check_reward(),),
        ('level',          "'level': %s, ",       'int_list',),
        ('server_id',      "'server_id': %s, ",   'str_list',),
        ('des',            "'des': %s, ",         'unicode',),
        ('des_f',          "'des_f': %s, ",       'unicode',),
        ('charge_id',          "'charge_id': %s, ",       'int',),
        ('END',        "},                 ",   'None')
    ], {}

recall_active_recharge = active_recharge

def active_consume():
    return [
        ('id',    "%s: {              ",    'int',),
        ('show_id',        "'show_id': %s, ",        'int',),
        ('consume_type',    "'consume_type': %s, ",    'int',),
        ('repeat',         "'repeat': %s, ",         'int',),
        ('show_time',      "'show_time': %s, ",      'unicode',),
        ('start_time',     "'start_time': %s, ",     'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('end_time',       "'end_time': %s, ",    'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('num',            "'num': %s, ",         'int',),
        ('reward',         "'reward': %s, ",      'int_list', check_reward(),),
        ('level',          "'level': %s, ",       'int_list',),
        ('server_id',      "'server_id': %s, ",   'str_list',),
        ('des',            "'des': %s, ",         'unicode',),
        ('END',        "},                 ",   'None')
    ], {}


def server_active_recharge():
    return [
        ('id',    "%s: {              ",    'int',),
        ('show_id',        "'show_id': %s, ",        'int',),
        ('charge_type',    "'charge_type': %s, ",    'int',),
        ('repeat',         "'repeat': %s, ",         'int',),
        ('start_time',     "'start_time': %s, ",     'str',),
        ('end_time',       "'end_time': %s, ",    'str',),
        ('num',            "'num': %s, ",         'int',),
        ('reward',         "'reward': %s, ",      'int_list', check_reward(),),
        ('level',          "'level': %s, ",       'int_list',),
        ('des',            "'des': %s, ",         'unicode',),
        ('charge_id',          "'charge_id': %s, ",       'int',),
        ('END',        "},                 ",   'None')
    ], {}


def active_show():
    return [
        ('id',    "%s: {              ",    'int',),
        ('sort',           "'sort': %s, ",         'int',),
        ('show',           "'show': %s, ",         'int',),
        ('show_id',        "'show_id': %s, ",      'int',),
        ('mark',           "'mark': %s, ",         'int',),
        ('start_time',     "'start_time': %s, ",   'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('end_time',       "'end_time': %s, ",     'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('active_start_time',     "'active_start_time': %s, ",   'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('active_end_time',       "'active_end_time': %s, ",     'str', check_time(tformat="%Y-%m-%d,%H:%M"),),
        ('server_id',       "'server_id': %s, ",     'str_list',),
        ('level',       "'level': %s, ",     'int_list',),
        ('banner',       "'banner': %s, ",     'str',),
        ('title',       "'title': %s, ",     'str',),
        ('END',        "},                 ",     'None')
    ], {}

recall_active_show = active_show

def face_icon():
    return [
        ('id',    "%s: {              ",    'int',),
        ('icon',           "'icon': %s, ",         'str',),
        ('vip',            "'vip': %s, " ,         'int',),
        ('END',        "},                 ",     'None')
    ], {}


def limit_hero_score():
    return [
        ('id',    "%s: {              ",           'int',),
        ('version',      "'version': %s,        ",        'int',),
        ('start_time',        "'start_time': %s, ",       'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',        "'end_time': %s,        ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('score',           "'score': %s, ",       'int',),
        ('reward',        "'reward': %s, ",   'int_list', check_reward(),),
        ('server',           "'server': %s, ",     'str',),
        ('notice',           "'notice': %s, ",     'unicode',),
        ('END',        "},                 ",      'None')
    ], {}

def limit_hero_rank():
    return [
        ('id',    "%s: {              ",           'int',),
        ('version',      "'version': %s,        ",        'int',),
        ('rank',           "'rank': %s, ",    'int_list', check_int_list_args(2)),
        ('reward',        "'reward': %s, ",   'int_list', check_reward(),),
        ('server',           "'server': %s, ",     'str',),
        ('END',        "},                 ",      'None')
    ], {}

def limit_time_reward():
    return [
        ('id',    "%s: {              ",           'int',),
        ('version',      "'version': %s,        ",        'int',),
        ('time',           "'time': %s, ",         'str',),
        ('rank',        "'rank': %s, ",       'int_list', check_int_list_args(2)),
        ('reward',        "'reward': %s, ",   'int_list', check_reward(),),
        ('server',           "'server': %s, ",     'str',),
        ('END',        "},                 ",      'None')
    ], {}

def bandit():
    return [
        ('active_id',    "%s: {                    ",        'int',),
        ('version',        "'version': %s,        ",        'int',),
        ('start_time',        "'start_time': %s,        ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',        "'end_time': %s,        ",        'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('id',        "'id': %s,        ",        'int',),
        ('coin',        "'coin': %s,        ",        'int',),
        ('git_coin',    "'git_coin': %s,    ",        'int_list',),
        ('reward_coin', "'reward_coin': %s, ",        'int_list',),
        ('notice', "'notice': %s, ",        'unicode',),
        ('END',        "},                  ",      'None')
    ], {}


def server_bandit():
    return [
        ('id',    "%s: {                    ",        'int',),
        ('coin',        "'coin': %s,        ",        'int',),
        ('git_coin',    "'git_coin': %s,    ",        'int_list',),
        ('reward_coin', "'reward_coin': %s, ",        'int_list',),
        ('END',        "},                  ",      'None')
    ], {}

def tree_shop():
    return [
        ('shop',           "%s: {              ",    'int',),
        ('shop_reward', " 'shop_reward': %s,  ",    'int_list',),
        ('need_sort',    " 'need_sort': %s,  ",    'int',),
        ('need_value',   " 'need_value': %s,  ",    'int_single_list',),
        ('sell_off',     " 'sell_off': %s,  ",    'int',),
        ('sell_sort',    " 'sell_sort': %s,  ",    'int',),
        ('sell_max',     " 'sell_max': %s,  ",    'int',),
        ('show_level',     " 'show_level': %s,  ",    'int_single_list',),
        ('END',        "},                 ",    'None')
    ], {}


def guild_fight_reward():
    return [
        ('guild_fight_id',    "%s: {              ",    'int',),
        ('guild_fight_reward',  "'reward': %s, ",       'int_list',),
        ('word',  "'word': %s, ",       'unicode',),
        ('END',        "},                 ",     'None')
    ], {}


def guild_fight_time():
    return [
        ('id',    "%s: {              ",    'int',),
        ('start_week',  "'start_week': %s, ",       'int',),
        ('start_time',  "'start_time': %s, ",       'str', check_time(tformat="%H:%M:%S"),),
        ('end_week',  "'end_week': %s, ",       'int',),
        ('end_time',  "'end_time': %s, ",       'str', check_time(tformat="%H:%M:%S"),),
        ('script',  "'script': %s, ",       'str',),
        ('END',        "},                 ",     'None')
    ], {}


def group_show():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",     'int',),
        ('sort',  "'sort': %s, ",       'int',),
        ('item',  "'item': %s, ",       'int_list', check_reward(),),
        ('END',        "},                 ",     'None')
        ], {}


def deadandalive():
    return [
        ('level',    "%s: {              ",    'int',),
        ('award',  "'award': %s, ",       'int_list', check_reward(),),
        ('END',        "},                 ",     'None')
    ], {}


def group_score():
    return [
        ('version',    "%s: {              ",    'int',),
        ('score',  "'score': %s, ",       'int',),
        ('score_add',  "'score_add': %s, ",       'int_list',),
        ('score_add_max',  "'score_add_max': %s, ",       'int',),
        ('min_score',  "'min_score': %s, ",       'int',),
        ('reward',  "'reward': %s, ",       'int_list', check_reward(),),
        ('END',        "},                 ",     'None')
    ], {}


def group_shop():
    return [
        ('shop_id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",       'int',),
        ('num',  "'num': %s, ",       'int',),
        ('reward',  "'reward': %s, ",       'int_list', check_reward(),),
        ('coin',  "'coin': %s, ",       'int',),
        ('selloff',  "'selloff': %s, ",       'int',),
        ('END',        "},                 ",     'None')
    ], {}


def group_rank():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",       'int',),
        ('rank',  "'rank': %s, ",       'int',),
        ('diamond_off',  "'diamond_off': %s, ",       'int',),
        ('des',  "'des': %s, ",       'unicode',),
        ('END',        "},                 ",     'None')
    ], {}


def group_version():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time', "'start_time': %s, ",     'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',   "'end_time': %s, ",       'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('date',       "'date': %s, ",           'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('des',        "'des': %s,  ",       'unicode',),
        ('notice_1',        "'notice_1': %s,  ",       'unicode',),
        ('notice_2',        "'notice_2': %s,  ",       'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_group_show():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",     'int',),
        ('sort',  "'sort': %s, ",       'int',),
        ('item',  "'item': %s, ",       'int_list',),
        ('END',        "},                 ",     'None')
    ], {}


def server_group_score():
    return [
        ('version',    "%s: {              ",    'int',),
        ('score',  "'score': %s, ",       'int',),
        ('score_add',  "'score_add': %s, ",       'int_list',),
        ('score_add_max',  "'score_add_max': %s, ",       'int',),
        ('min_score',  "'min_score': %s, ",       'int',),
        ('reward',  "'reward': %s, ",       'int_list',),
        ('END',        "},                 ",     'None')
    ], {}


def server_group_shop():
    return [
        ('shop_id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",       'int',),
        ('num',  "'num': %s, ",       'int',),
        ('reward',  "'reward': %s, ",       'int_list',),
        ('coin',  "'coin': %s, ",       'int',),
        ('selloff',  "'selloff': %s, ",       'int',),
        ('END',        "},                 ",     'None')
    ], {}


def server_group_rank():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',  "'version': %s, ",       'int',),
        ('rank',  "'rank': %s, ",       'int',),
        ('diamond_off',  "'diamond_off': %s, ",       'int',),
        ('des',  "'des': %s, ",       'unicode',),
        ('END',        "},                 ",     'None')
    ], {}


def server_group_version():
    return [
        ('version',    "%s: {              ",    'int',),
        ('des',        "'des': %s,  ",       'unicode',),
        ('notice_1',        "'notice_1': %s,  ",       'unicode',),
        ('notice_2',        "'notice_2': %s,  ",       'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def equip_gacha():
    return [
        ('gacha_ID',     """%s:{                   """ , 'int'),
        ('star_time',    """ 'star_time'     : %s, """ , 'str'),
        ('gacha_name',    """ 'gacha_name'     : %s, """ , 'str'),
        ('gacha_team',   """ 'gacha_team'    : %s, """ , 'int'),
        ('image',        """ 'image'         : %s, """ , 'str'),
        ('image_word',   """ 'image_word'    : %s, """ , 'str'),
        ('image_active', """ 'image_active'  : %s, """ , 'str'),
        ('end_time',     """ 'end_time'      : %s, """ , 'str'),
        ('gacha_sort',   """ 'gacha_sort'    : %s, """ , 'int'),
        ('gacha_num',    """ 'gacha_num'     : %s, """ , 'int'),
        ('consume_sort', """ 'consume_sort'  : %s, """ , 'int'),
        ('value',        """ 'value'         : %s, """ , 'int'),
        ('get_num',      """ 'get_num'       : %s, """ , 'int'),
        ('quality',      """ 'quality'       : %s, """ , 'int'),
        ('get_card',     """ 'get_card'      : %s, """ , 'int_list'),
        ('add_point',    """ 'add_point'     : %s, """ , 'int'),
        ('bad_item',     """ 'bad_item'      : %s, """ , 'int_list', check_reward(),),
        ('bad_point',    """ 'bad_point'     : %s, """ , 'int'),
        ('good_item',    """ 'good_item'     : %s, """ , 'int_list', check_reward(),),
        ('good_point',   """ 'good_point'    : %s, """ , 'int'),
        ('piece',        """ 'piece'         : %s, """ , 'int_list'),
        ('story',        """ 'story'         : %s, """ , 'unicode'),
        ('use_level',    """ 'use_level'     : %s, """ , 'int_list'),
        ('use_gacha',    """ 'use_gacha'     : %s, """ , 'int_list'),
        ('is_box',       """ 'is_box'        : %s, """ , 'int'),
        ('reward',       """ 'reward'        : %s, """ , 'int_list', check_reward(),),
        ('END',          """ },                    """ , 'None'),
    ], {}

def equip_gacha_box():
    return [(
             ('box_id', 'team_card'),
              """ %s: %s, """,
             ('int', 'int_list')
            )], {}

def equip_gacha_reward_score():
    return [
        ('ID',   "%s: {              ",   'int',),
        ('open',        "    'open': %s,   ",    'str',),
        ('close',       "    'close': %s,  ",    'str',),
        ('score',       "    'score': %s,  ",    'int',),
        ('reward',      "    'reward': %s,  ",    'int_list', check_reward(),),
        ('des',         "    'des': %s,  ",       'unicode',),
        ('times',       "    'times': %s,  ",     'int',),
        ('END',        "},               ", 'None')
    ], {}

def equip_reward_gacha():
    return [
        ('reward_gacha_ID', "%s: {                  ",   'int'),
        #('story',           "    'story'       : %s,",   'unicode'),
        ('target_sort',     "    'target_sort' : %s,",   'int'),
        ('target_data',     "    'target_data' : %s,",   'int'),
        ('reward_score',    "    'reward_score': %s,",   'int'),
        ('END', "},", 'None')
    ], {}

def equip_gacha_score():
    return [
        ('score',  "%s: {",   'int'),
        ('reward', "    'reward': %s,",   'int_list', check_reward(),),
        ('END', "},", 'None')
    ], {}

def equip_gacha_gift():
    return [
        ('rank_id', "%s: {               ",   'int'),
        ('rank',     "    'rank'    : %s,",   'int'),
        ('rank_low', "    'rank_low': %s,",   'int'),
        ('reward',   "    'reward'  : %s,",   'int_list', check_reward(),),
        ('END', "},", 'None')
    ], {}

def equip_loot_id():
    return [(
             ('id', 'sort'),
            """ %s: %s,""",
            ('int', 'int')
    )], {}


def mining():
    return [
        ('player_level',    "%s: {              ",    'int',),
        ('reward',       "'reward': %s, ",        'int_list', check_reward(),),
        ('rent1',        "'rent1': %s, ",         'int_list', check_reward(),),
        ('rent2',        "'rent2': %s, ",         'int_list', check_reward(),),
        ('rent3',        "'rent3': %s, ",         'int_list', check_reward(),),
        ('END',          "},                     ",     'None')
    ], {}


def foundation():
    return [
        ('active_id',   "%s: {              ",   'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('start_time',       "    'start_time': %s,  ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',       "    'end_time': %s,  ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('id',       "    'id': %s,  ",    'int',),
        ('need_coin',       "    'need_coin': %s,  ",    'int',),
        ('reward_show',      "    'reward_show': %s,  ",    'int_list', check_reward(),),
        ('day1',      "    'day1': %s,  ",    'int_list', check_reward(),),
        ('day2',      "    'day2': %s,  ",    'int_list', check_reward(),),
        ('day3',      "    'day3': %s,  ",    'int_list', check_reward(),),
        ('day4',      "    'day4': %s,  ",    'int_list', check_reward(),),
        ('day5',      "    'day5': %s,  ",    'int_list', check_reward(),),
        ('day6',      "    'day6': %s,  ",    'int_list', check_reward(),),
        ('day7',      "    'day7': %s,  ",    'int_list', check_reward(),),
        ('server_id',"    'server_id': %s,  ",    'str_list',),
        ('notice', "'notice': %s, ",        'unicode',),
        ('END',        "},               ", 'None')
    ],{}


def server_inreview():
    return [
        ('ID',   "%s: {            ",   'int',),
        ('is_open',      "    'is_open': %s, ",    'int',),
        ('name',         "    'name': %s, ",    'unicode',),
        ('story',        "    'story': %s, ",   'unicode',),
        ('show_lv',        "    'show_lv': %s, ",   'int',),
        ('default',        "    'default': %s, ",   'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def server_foundation():
    return [
        ('active_id',   "%s: {              ",   'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('id',       "    'id': %s,  ",    'int',),
        ('need_coin',       "    'need_coin': %s,  ",    'int',),
        ('reward_show',      "    'reward_show': %s,  ",    'int_list', check_reward(),),
        ('day1',      "    'day1': %s,  ",    'int_list', check_reward(),),
        ('day2',      "    'day2': %s,  ",    'int_list', check_reward(),),
        ('day3',      "    'day3': %s,  ",    'int_list', check_reward(),),
        ('day4',      "    'day4': %s,  ",    'int_list', check_reward(),),
        ('day5',      "    'day5': %s,  ",    'int_list', check_reward(),),
        ('day6',      "    'day6': %s,  ",    'int_list', check_reward(),),
        ('day7',      "    'day7': %s,  ",    'int_list', check_reward(),),
        ('server_id',"    'server_id': %s,  ",    'str_list',),
        ('notice', "'notice': %s, ",        'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def server_hero():
    return [
        ('id',              "%s: {              ",          'int',),
        ('version',            "'version': %s, ",            'int',),
        ('rank',            "'rank': %s, ",                 'int_list',),
        ('reward',          "'reward': %s, ",               'int_list', check_reward(),),
        ('start_time',      "'start_time': %s, ",           'str',),
        ('end_time',        "'end_time': %s, ",             'str',),
        ('END',             "},                 ",          'None')
    ], {}


def server_limit_hero():
    return [
        ('id',              "%s: {              ",          'int',),
        ('version',            "'version': %s, ",            'int',),
        ('score',           "'score': %s, ",                'int',),
        ('reward',          "'reward': %s, ",               'int_list', check_reward(),),
        ('start_time',      "'start_time': %s, ",           'str',),
        ('end_time',        "'end_time': %s, ",             'str',),
        ('notice',           "'notice': %s, ",     'unicode',),
        ('END',             "},                 ",          'None')
    ], {}


def server_limit_time():
    return [
        ('id',    "%s: {              ",           'int',),
        ('version',            "'version': %s, ",            'int',),
        ('time',           "'time': %s, ",         'str',),
        ('rank',        "'rank': %s, ",       'int_list', check_int_list_args(2)),
        ('reward',        "'reward': %s, ",   'int_list', check_reward(),),
        ('END',        "},                 ",      'None')
    ], {}


def one_piece():
    return [
        ('version',        "%s: {               ",    'int',),
        ('id',       "    'id': %s,    ",    'int',),
        ('start_time',       "    'start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',         "    'end_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('free_reward',      "    'free_reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('show_ranking',     "    'show_ranking': %s,   ",    'int',),
        ('max_score',        "    'max_score': %s,     ",    'int',),
        ('one_coin',         "    'one_coin': %s,     ",    'int',),
        ('ten_coin',         "    'ten_coin': %s,     ",    'int',),
        ('max_rate',         "    'max_rate': %s,      ",    'int',),
        ('vip_limit',        "    'vip_limit': %s,     ",    'int',),
        ('server_score',    "    'server_score': %s,   ",    'int_list',),
        ('score_1',          "    'score_1': %s,        ",    'int',),
        ('reward_1',         "    'reward_1': %s,       ",    'int_list', check_reward(),),
        ('score_2',          "    'score_2': %s,        ",    'int',),
        ('reward_2',         "    'reward_2': %s,       ",    'int_list', check_reward(),),
        ('score_3',          "    'score_3': %s,        ",    'int',),
        ('reward_3',         "    'reward_3': %s,       ",    'int_list', check_reward(),),
        ('notice',      "    'notice': %s, ",    'unicode',),
        ('END',           "},                  ",    'None')
    ], {}


def one_piece_reduce():
    return [
        ('id',        "%s: {               ",    'int',),
        ('day_1',          "    'day_1': %s,        ",    'int',),
        ('day_2',          "    'day_2': %s,        ",    'int',),
        ('day_3',          "    'day_3': %s,        ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def one_piece_rate():
    return [
        ('active_id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('id',          "    'id': %s,        ",    'int',),
        ('show_id',          "    'show_id': %s,        ",    'int',),
        ('reward',          "    'reward': %s,        ",    'int_list', check_reward(),),
        ('score',          "    'score': %s,        ",    'int',),
        ('rate',          "    'rate': %s,        ",    'int',),
        ('has_reduce',          "    'has_reduce': %s,        ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def one_piece_exchange():
    return [
        ('id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('sort',          "    'sort': %s,        ",    'int',),
        ('reward',        "    'reward': %s,      ",    'int_list', check_reward(),),
        ('limit_num',    "    'limit_num': %s,   ",    'int',),
        ('need_key_num',    "    'need_key_num': %s,   ",    'int',),
        ('player_limit',    "    'player_limit': %s,   ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def one_piece_rank_reward():
    return [
        ('id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('reward_time',"    'reward_time': %s,    ",    'str',),
        ('rank',   "    'rank': %s,   ",    'int_single_list', check_int_list_args(2)),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_one_piece():
    return [
        ('version',        "%s: {               ",    'int',),
        ('id',       "    'id': %s,    ",    'int',),
        ('free_reward',      "    'free_reward': %s,   ",    'int_list',),
        ('show_ranking',     "    'show_ranking': %s,   ",    'int',),
        ('max_score',        "    'max_score': %s,     ",    'int',),
        ('one_coin',         "    'one_coin': %s,     ",    'int',),
        ('ten_coin',         "    'ten_coin': %s,     ",    'int',),
        ('max_rate',         "    'max_rate': %s,      ",    'int',),
        ('vip_limit',        "    'vip_limit': %s,     ",    'int',),
        ('server_score',    "    'server_score': %s,   ",    'int_list',),
        ('score_1',          "    'score_1': %s,        ",    'int',),
        ('reward_1',         "    'reward_1': %s,       ",    'int_list',),
        ('score_2',          "    'score_2': %s,        ",    'int',),
        ('reward_2',         "    'reward_2': %s,       ",    'int_list',),
        ('score_3',          "    'score_3': %s,        ",    'int',),
        ('reward_3',         "    'reward_3': %s,       ",    'int_list',),
        ('notice',      "    'notice': %s, ",    'unicode',),
        ('END',           "},                  ",    'None')
    ], {}


def server_one_piece_reduce():
    return [
        ('id',        "%s: {               ",    'int',),
        ('day_1',          "    'day_1': %s,        ",    'int',),
        ('day_2',          "    'day_2': %s,        ",    'int',),
        ('day_3',          "    'day_3': %s,        ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def server_one_piece_rate():
    return [
        ('active_id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('id',          "    'id': %s,        ",    'int',),
        ('show_id',          "    'show_id': %s,        ",    'int',),
        ('reward',          "    'reward': %s,        ",    'int_list',),
        ('score',          "    'score': %s,        ",    'int',),
        ('rate',          "    'rate': %s,        ",    'int',),
        ('has_reduce',          "    'has_reduce': %s,        ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def server_one_piece_exchange():
    return [
        ('id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('sort',          "    'sort': %s,        ",    'int',),
        ('reward',        "    'reward': %s,      ",    'int_list',),
        ('limit_num',    "    'limit_num': %s,   ",    'int',),
        ('need_key_num',    "    'need_key_num': %s,   ",    'int',),
        ('player_limit',    "    'player_limit': %s,   ",    'int',),
        ('END',           "},                  ",    'None')
    ], {}


def server_one_piece_rank_reward():
    return [
        ('id',        "%s: {               ",    'int',),
        ('version',          "    'version': %s,        ",    'int',),
        ('rank',   "    'rank': %s,   ",    'int_single_list',),
        ('rank_reward', "    'rank_reward': %s,   ",    'int_list',),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def exchange_card():
    return [
        ('exchange_id',   "%s: {              ",   'int',),
        ('select',    "    'select': %s,   ",    'int',),
        ('show_card',       "    'show_card': %s,  ",    'str',),
        ('cost',      "    'cost': %s,  ",    'int_list', check_reward(),),
        ('card1',      "    'card1': %s,  ",    'str',),
        ('card2',      "    'card2': %s,  ",    'str',),
        ('card3',      "    'card3': %s,  ",    'str',),
        ('card4',      "    'card4': %s,  ",    'str',),
        ('card5',      "    'card5': %s,  ",    'str',),
        ('reward1',      "    'reward1': %s,  ",    'int_list', check_reward(is_random=True),),
        ('level1',      "    'level1': %s,  ",    'int_list',),
        ('reward2',      "    'reward2': %s,  ",    'int_list', check_reward(is_random=True),),
        ('level2',      "    'level2': %s,  ",    'int_list',),
        ('first_reward',      "    'first_reward': %s,  ",    'int_list', check_reward(is_random=True),),
        ('gift_num',      "    'gift_num': %s,  ",    'int_list',),
        ('gift_reward',      "    'gift_reward': %s,  ",    'int_list', check_reward(is_random=True),),
        ('END',        "},               ", 'None')
    ], {}


def auto_consume_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('need_score',  "    'need_score': %s,  ",    'int',),
        ('reward',      "    'reward': %s,  ",    'int_list',),
        ('config_type',  "    'config_type': %s,  ",    'int',),
        ('END',        "},                 ",    'None')
    ],{}


def guild_fight_buy():
    return [
        ('id',    "%s: {              ",    'int',),
        ('cost',"    'cost': %s,    ",    'int',),
        ('reward', "    'reward': %s,   ",    'int_list', check_reward(),),
        ('mail',      "    'mail': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ],{}

def contract():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',"    'start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',   "    'end_time': %s,   ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('score_add',   "    'score_add': %s,   ",    'int_list',),
        ('score_add_max',   "    'score_add_max': %s,   ",    'int',),
        ('rate',   "    'rate': %s,   ",    'int',),
        ('fire_score', "    'fire_score': %s,   ",    'int',),
        ('fire_time', "    'fire_time': %s,   ",    'int',),
        ('fire_des',      "    'fire_des': %s, ",    'unicode',),
        ('contract_des',      "    'contract_des': %s, ",    'unicode',),
        ('notice',      "    'notice': %s, ",    'unicode',),
        ('day',   "    'day': %s,   ",    'int'),
        ('END',        "},                 ",    'None')
    ], {}

def contract_score_reward():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('cost',"    'cost': %s,    ",    'int',),
        ('reward',   "    'reward': %s,   ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}

def contract_detail():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('coin',   "    'coin': %s,   ",    'int',),
        ('max_score', "    'max_score': %s,   ",    'int',),
        ('max_rate',      "    'max_rate': %s, ",    'int',),
        ('vip_limit',      "    'vip_limit': %s, ",    'int',),
        ('server_score',      "    'server_score': %s, ",    'int_list',),
        ('reward_show_base',      "    'reward_show_base': %s, ",    'int_list', check_reward(),),
        ('reward_show_final',      "    'reward_show_final': %s, ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}

def contract_rate():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('reward',   "    'reward': %s,   ",    'int_list', check_reward(is_random=True),),
        ('score', "    'score': %s,   ",    'int',),
        ('rate',      "    'rate': %s, ",    'int',),
        ('has_reduce',      "    'has_reduce': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}

def contract_fire_cup():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',      "    'version': %s, ",    'int',),
        ('fire_id',      "    'fire_id': %s, ",    'int',),
        ('id',      "    'id': %s, ",    'int',),
        ('coin',      "    'coin': %s, ",    'int',),
        ('server_player',      "    'server_player': %s, ",    'int_list',),
        ('max_score',      "    'max_score': %s, ",    'int',),
        ('reward_send',      "    'reward_send': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}

def contract_reduce():
    return [
        ('id',    "%s: {              ",    'int',),
        ('day_1',"    'day_1': %s,    ",    'int',),
        ('day_2',"    'day_2': %s,    ",    'int',),
        ('day_3',"    'day_3': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}

def contract_reward():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('gamer',"    'gamer': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list', check_reward(),),
        ('time',"    'time': %s,    ",    'str',),
        ('mail',"    'mail': %s,    ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract():
    return [
        ('version',    "%s: {              ",    'int',),
        ('score_add',   "    'score_add': %s,   ",    'int_list',),
        ('score_add_max',   "    'score_add_max': %s,   ",    'int',),
        ('rate',   "    'rate': %s,   ",    'int',),
        ('fire_score', "    'fire_score': %s,   ",    'int',),
        ('fire_time', "    'fire_time': %s,   ",    'int',),
        ('fire_des',      "    'fire_des': %s, ",    'unicode',),
        ('contract_des',      "    'contract_des': %s, ",    'unicode',),
        ('notice',      "    'notice': %s, ",    'unicode',),
        ('day',   "    'day': %s,   ",    'int'),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_score_reward():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('cost',"    'cost': %s,    ",    'int',),
        ('reward',   "    'reward': %s,   ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_detail():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('coin',   "    'coin': %s,   ",    'int',),
        ('max_score', "    'max_score': %s,   ",    'int',),
        ('max_rate',      "    'max_rate': %s, ",    'int',),
        ('vip_limit',      "    'vip_limit': %s, ",    'int',),
        ('server_score',      "    'server_score': %s, ",    'int_list',),
        ('reward_show_base',      "    'reward_show_base': %s, ",    'int_list',),
        ('reward_show_final',      "    'reward_show_final': %s, ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_rate():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('reward',   "    'reward': %s,   ",    'int_list',),
        ('score', "    'score': %s,   ",    'int',),
        ('rate',      "    'rate': %s, ",    'int',),
        ('has_reduce',      "    'has_reduce': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_fire_cup():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',      "    'version': %s, ",    'int',),
        ('fire_id',      "    'fire_id': %s, ",    'int',),
        ('id',      "    'id': %s, ",    'int',),
        ('coin',      "    'coin': %s, ",    'int',),
        ('server_player',      "    'server_player': %s, ",    'int_list',),
        ('max_score',      "    'max_score': %s, ",    'int',),
        ('reward_send',      "    'reward_send': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_reduce():
    return [
        ('id',    "%s: {              ",    'int',),
        ('day_1',"    'day_1': %s,    ",    'int',),
        ('day_2',"    'day_2': %s,    ",    'int',),
        ('day_3',"    'day_3': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def server_contract_reward():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('id',"    'id': %s,    ",    'int',),
        ('gamer',"    'gamer': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list',),
        ('time',"    'time': %s,    ",    'str',),
        ('mail',"    'mail': %s,    ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def new_world():
    return [
        ('server_id',    "%s: {              ",    'str',),
        ('world_id',"    'world_id': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def pyramid_notice():
    return [
        ('ID',    "%s: {              ",    'int',),
        ('trigger_sort',"    'trigger_sort': %s,    ",    'int',),
        ('trigger',"    'trigger': %s,    ",    'int',),
        ('is_self',"    'is_self': %s,    ",    'int',),
        ('notice_level',"    'notice_level': %s,    ",    'int',),
        ('text',"    'text': %s,    ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def pyramid():
    return [
        ('id',    "%s: {              ",    'int',),
        ('morale',"    'morale': %s,    ",    'int',),
        ('morale_recovery',"    'morale_recovery': %s,    ",    'int',),
        ('morale_recovery_time',"    'morale_recovery_time': %s,    ",    'int',),
        ('pay_add_morale',"    'pay_add_morale': %s,    ",    'int',),
        ('add_morale',"    'add_morale': %s,    ",    'int',),
        ('morale_decrease',"    'morale_decrease': %s,    ",    'int', ),
        ('challenge_times',"    'challenge_times': %s,    ",    'int',),
        ('pay_add_time',"    'pay_add_time': %s,    ",    'int',),
        ('show_banner',"    'show_banner': %s,    ",    'unicode',),
        ('gap_time',"    'gap_time': %s,    ",    'str',),
        ('time_reward',"    'time_reward': %s,    ",    'int_list',),
        ('pay_sweep',"    'pay_sweep': %s,    ",    'int',),
        ('mail',"    'mail': %s,    ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}

def pyramid_level():
    return [
        ('id',    "%s: {              ",    'int',),
        ('player_num',"    'player_num': %s,    ",    'int',),
        ('reward_show',"    'reward_show': %s,    ",    'int_list', check_reward(),),
        ('reward_base',"    'reward_base': %s,    ",    'int_list', check_reward(),),
        ('reward_rate',"    'reward_rate': %s,    ",    'int_list', check_reward(),),
        ('reward_rate_number',"    'reward_rate_number': %s,    ",    'int',),
        ('reward_time',"    'reward_time': %s,    ",    'int',),
        ('reward_score',"    'reward_score': %s,    ",    'int',),
        ('robot_id',"    'robot_id': %s,    ",    'int_list',),
        ('shortcut',"    'shortcut': %s,    ",    'int',),
        ('mail',"    'mail': %s,    ",    'unicode',),
        ('mail_wanted',"    'mail_wanted': %s,    ",    'unicode',),
        ('extra_reward_mail',"    'extra_reward_mail': %s,    ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}

def pyramid_robot():
    return [
        ('robot_id',               """'robot_%s': {         """ , 'int'),
        ('name',     """  'name': %s, """,      'unicode'),
        ('formation_type',        "'formation_type': %s,"      , 'int_list'),
        ('role',                  "'role': %s,"                , 'int'),
        ('role_level',            "'role_level': %s,"          , 'int_list'),
        ('character_level',       "'character_level': %s,"     , 'int_list'),
        ('evo_level',             "'evo_level': %s,"           , 'int_list'),
        ('skill_level',           "'skill_level': %s,"         , 'int_list'),
        ('leader_skill_1_key',    "'leader_skill_1_key': %s,"  , 'int'),
        ('leader_skill_1_level',  "'leader_skill_1_level': %s,", 'int'),
        ('leader_skill_2_key',    "'leader_skill_2_key': %s,"  , 'int'),
        ('leader_skill_2_level',  "'leader_skill_2_level': %s,", 'int'),
        ('leader_skill_3_key',    "'leader_skill_3_key': %s,"  , 'int'),
        ('leader_skill_3_level',  "'leader_skill_3_level': %s,", 'int'),
        ('END',                "},", 'None')
    ], {}

def pyramid_lucky():
    return [
        ('id',    "%s: {              ",    'int',),
        ('lucky_level',"    'lucky_level': %s,    ",    'int_list'),
        ('lucky_situation', "    'lucky_situation': %s,   ",    'int_list'),
        ('lucky_time',      "    'lucky_time': %s, ",    'str'),
        ('reward',      "    'reward': %s, ",    'int_list', check_reward(),),
        ('mail', """   'mail': %s, """, 'unicode'),
        ('END',        "},                 ",    'None')
    ], {}

def pyramid_wanted():
    return [
        ('wanted_ID',    "%s: {              ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('refresh', "    'refresh': %s,   ",    'int',),
        ('rate',      "    'rate': %s, ",    'int',),
        ('reward',      "    'reward': %s, ",    'int_list', check_reward(),),
        ('story', """   'story': %s, """, 'unicode'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_date', """ 'target_date': %s, """, 'int'),
        ('target_data1', """ 'target_data1': %s, """, 'int'),
        ('END',        "},                 ",    'None')
    ], {}

def pyramid_hatred():
    return [
        ('floor',    "%s: {              ",    'int',),
        ('hatred_num',"    'hatred_num': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_hatred():
    return [
        ('quality',    "%s: {              ",    'int',),
        ('hatred_num',"    'hatred_num': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_shop_free():
    return [
        ('id',    "%s: {              ",    'int',),
        ('team',"    'team': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_shop_free_team():
    return [
        ('team_id',    "%s: {              ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list', check_reward(),),
        ('cost',"    'cost': %s,    ",    'int',),
        ('validity',"    'validity': %s,    ",    'int',),
        ('quality',"    'quality': %s,    ",    'int',),
        ('off',"    'off': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_shop_charged():
    return [
        ('id',    "%s: {              ",    'int',),
        ('team',"    'team': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_shop_charged_team():
    return [
        ('team_id',    "%s: {              ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list', check_reward(),),
        ('cost',"    'cost': %s,    ",    'int',),
        ('validity',"    'validity': %s,    ",    'int',),
        ('quality',"    'quality': %s,    ",    'int',),
        ('off',"    'off': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def escort_opentime():
    return [
        ('id',    "%s: {              ",    'int'),
        ('start_time',"    'start_time': %s,    ",    'str',),
        ('end_time',"    'end_time': %s,    ",    'str'),
        ('END',        "},                 ",    'None')
    ],{}


def escort_buff():
    return [(
        ('buff_id', 'Probability'),
            """ %s: %s,""",
            ('int', 'int')
    )],{}


def escort():
    return [
        ('refresh_cost',"    'refresh_cost': %s,    ",    'int'),
        ('buff_cost',"    'buff_cost': %s,    ",    'int'),
        ('employment_cost',"    'employment_cost': %s,    ",    'int'),
        ('rob_cost',"    'rob_cost': %s,    ",    'int'),
        ('rob_score_success',"    'rob_score_success': %s,    ",    'int'),
        ('rob_score_fail',"    'rob_score_fail': %s,    ",    'int'),
        ('item_id',"    'item_id': %s,    ",    'int'),
        ('escort_times',"    'escort_times': %s,    ",    'int'),
        ('rob_times',"    'rob_times': %s,    ",    'int'),
        ('rob_purchase_times',"    'rob_purchase_times': %s,    ",    'int'),
        ('buff_free_times',"    'buff_free_times': %s,    ",    'int'),
        ('shop_free_refresh_times',"    'shop_free_refresh_times': %s,    ",    'int'),

    ], {}


def escort_exchange():
    return [
        ('id',   "%s: {              ",   'int',),
        ('cost',  "    'cost': %s,  ",    'int',),
        ('reward',      "    'reward': %s,  ",    'int_list', check_reward(),),
        ('limits',  "    'limits': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}

def escort_quality():
    return [
        ('quality',   "%s: {              ",   'int',),
        ('team',      "    'team': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def escort_mail():
    return [
        ('escort_mail', """   'escort_mail': %s, """, 'unicode'),
        ('rob_mail', """   'rob_mail': %s, """, 'unicode'),
    ],{}


def hatred_formula():
    return [
        ('id',    "%s: {              ",    'int',),
        ('condition',"    'condition': %s,    ",    'str',),
        ('formula',"    'formula': %s,    ",    'str',),
        ('END',        "},                 ",    'None')
    ], {}


def maze_mine():
    return [
        ('level',    "%s: {              ",    'int',),
        ('stage1',"    'stage1': %s,    ",    'int',),
        ('score1',"    'score1': %s,    ",    'int',),
        ('stage2',"    'stage2': %s,    ",    'int',),
        ('score2',"    'score2': %s,    ",    'int',),
        ('stage3',"    'stage3': %s,    ",    'int',),
        ('score3',"    'score3': %s,    ",    'int',),
        ('stage4',"    'stage4': %s,    ",    'int',),
        ('score4',"    'score4': %s,    ",    'int',),
        ('stage5',"    'stage5': %s,    ",    'int',),
        ('score5',"    'score5': %s,    ",    'int',),
        ('stage6',"    'stage6': %s,    ",    'int',),
        ('score6',"    'score6': %s,    ",    'int',),
        ('stage7',"    'stage7': %s,    ",    'int',),
        ('score7',"    'score7': %s,    ",    'int',),
        ('stage8',"    'stage8': %s,    ",    'int',),
        ('score8',"    'score8': %s,    ",    'int',),
        ('stage9',"    'stage9': %s,    ",    'int',),
        ('score9',"    'score9': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def maze_stage():
    return [
        ('stage_id',    "%s: {              ",    'int',),
        ('name',"    'name': %s,    ",    'unicode',),
        ('icon',"    'icon': %s,    ",    'str',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('fight',"    'fight': %s,    ",    'str',),
        ('buff',"    'buff': %s,    ",    'int_list',),
        ('item',"    'item': %s,    ",    'int_list',),
        ('shop',"    'shop': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def maze_buff():
    return [
        ('buff_id',    "%s: {              ",    'int',),
        ('name',"    'name': %s,    ",    'unicode',),
        ('icon',"    'icon': %s,    ",    'str',),
        ('story',"    'story': %s,    ",    'unicode',),
        ('quality',"    'quality': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('rate',"    'rate': %s,    ",    'int',),
        ('value',"    'value': %s,    ",    'int',),
        ('time_sort',"    'time_sort': %s,    ",    'int',),
        ('times',"    'times': %s,    ",    'int',),
        ('script',"    'script': %s,    ",    'str',),
        ('END',        "},                 ",    'None')
    ], {}


def maze_item():
    return [
        ('item_id',    "%s: {              ",    'int',),
        ('name',"    'name': %s,    ",    'unicode',),
        ('icon',"    'icon': %s,    ",    'str',),
        ('story',"    'story': %s,    ",    'unicode',),
        ('quality',"    'quality': %s,    ",    'int',),
        ('sort',"    'sort': %s,    ",    'int',),
        ('effect',"    'effect': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def maze_reward():
    return [
        ('score',    "%s: {              ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}


def maze_top_reward():
    return [
        ('top',    "%s: {              ",    'int',),
        ('reward',"    'reward': %s,    ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}


def player_recall():
    return [
        ('id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('reward',      "    'reward': %s,  ",    'int_list', check_reward(),),
        ('END',        "},               ", 'None')
    ], {}


def recall_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('reward',      "    'reward': %s,  ",    'int_list',),
        ('des',        "    'des': %s, ",   'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def recall_seven():
    return [
        ('day_id',   "%s: {              ",   'int',),
        ('reward_old',      "    'reward_old': %s,  ",    'int_list',),
        ('reward_new',      "    'reward_new': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}


def recall_coin():
    return [
        ('day_id',   "%s: {              ",   'int',),
        ('reward_ratio',      "    'reward_ratio': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}
# 现在暂时定为和daily_new一样的格式

#def recall_mission():
#    return [
#        ('dayly_ID',   "%s: {              ",   'int',),
#        ('reward',      "    'reward': %s,  ",    'int_list',),
#        ('icon',       "    'icon': %s,  ",    'str',),
#        ('name',       "    'name': %s,  ",    'unicode',),
#        ('story',       "    'story': %s,  ",    'unicode',),
#        ('target_sort',       "    'target_sort': %s,  ",    'int',),
#        ('target_data',       "    'target_data': %s,  ",    'int',),
#        ('target_data1',       "    'target_data1': %s,  ",    'int',),
#        ('reward',      "    'reward': %s,  ",    'int_list',),
#        ('END',        "},               ", 'None')
#    ], {}


def recall_time():
    return [
        ('id',   "%s: {              ",   'int',),
        ('login_time',       "    'login_time': %s,  ",    'str',),
        ('start_time',       "    'start_time': %s,  ",    'str',),
        ('end_time',       "    'end_time': %s,  ",    'str',),
        ('limit_lv',       "    'limit_lv': %s,  ",    'int',),
        ('rebate_rate',       "    'rebate_rate': %s,  ",    'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def recall_charge_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('percent',       "    'percent': %s,  ",    'int',),
        ('limit',       "    'limit': %s,  ",    'int',),
        ('des',        "    'des': %s, ",   'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def metal_core_shop():
    return [
        ('shop',    "%s: {              ",    'int',),
        ('shop_reward',"    'shop_reward': %s,    ",    'int_list', check_reward(),),
        ('need_sort',"    'need_sort': %s,    ",    'int',),
        ('need_value',"    'need_value': %s,    ",    'int_list',),
        ('sell_off',"    'sell_off': %s,    ",    'int',),
        ('sell_sort',"    'sell_sort': %s,    ",    'int',),
        ('sell_max',"    'sell_max': %s,    ",    'int',),
        ('show_level',"    'show_level': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def new_word_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('rank',       "    'rank': %s,  ",    'int_list', check_int_list_args(2)),
        ('reward',       "    'reward': %s,  ",    'int_list', check_reward(),),
        ('mail',        "    'mail': %s, ",   'unicode',),
        ('END',        "},               ", 'None')
    ], {}

def active_inreview():
    return [
        ('ID',   "%s: {              ",   'int',),
        ('is_open',       "    'is_open': %s,  ",    'int',),
        ('show_lv',       "    'show_lv': %s,  ",    'int',),
        ('default',       "    'default': %s,  ",    'int',),
        ('name',       "    'name': %s,  ",    'str',),
        ('story',       "    'story': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}

def worker():
    return [
        ('worker_id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('value',       "    'value': %s,  ",    'int',),
        ('weight',       "    'weight': %s,  ",    'int',),
        ('is_pay',       "    'is_pay': %s,  ",    'int',),
        ('name',       "    'name': %s,  ",    'unicode',),
        ('icon',       "    'icon': %s,  ",    'str',),
        ('quality',       "    'quality': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}

def seed():
    return [
        ('seed_id',   "%s: {              ",   'int',),
        ('name',       "    'name': %s,  ",    'unicode',),
        ('icon',       "    'icon': %s,  ",    'str',),
        ('shade',       "    'shade': %s,  ",    'str',),
        ('building',       "    'building': %s,  ",    'str',),
        ('quality',       "    'quality': %s,  ",    'int',),
        ('time',       "    'time': %s,  ",    'int',),
        ('reward',       "    'reward': %s,  ",    'int_list', check_reward(is_random=True),),
        ('END',        "},               ", 'None')
    ], {}

def farm_open():
    return [
        ('farm_id',   "%s: {              ",   'int',),
        ('open_sort',       "    'open_sort': %s,  ",    'int',),
        ('value',       "    'value': %s,  ",    'int',),
        ('name',       "    'name': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}

def super_evo_team():
    return [
        ('team_id',   "%s: {              ",   'int',),
        ('card_need',       "    'card_need': %s,  ",    'int',),
        ('ability_add',       "    'ability_add': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}

def super_evolution():
    return [
        ('super_id',   "%s: {              ",   'int',),
        ('level_1_need',       "    'level_1_need': %s,  ",    'int_list',),
        ('level_2_need',       "    'level_2_need': %s,  ",    'int_list',),
        ('level_3_need',       "    'level_3_need': %s,  ",    'int_list',),
        ('level_4_need',       "    'level_4_need': %s,  ",    'int_list',),
        ('level_5_need',       "    'level_5_need': %s,  ",    'int_list',),
        ('level_6_need',       "    'level_6_need': %s,  ",    'int_list',),
        ('level_7_need',       "    'level_7_need': %s,  ",    'int_list',),
        ('level_8_need',       "    'level_8_need': %s,  ",    'int_list',),
        ('level_9_need',       "    'level_9_need': %s,  ",    'int_list',),
        ('level_1_add',       "    'level_1_add': %s,  ",    'int_list',),
        ('level_2_add',       "    'level_2_add': %s,  ",    'int_list',),
        ('level_3_add',       "    'level_3_add': %s,  ",    'int_list',),
        ('level_4_add',       "    'level_4_add': %s,  ",    'int_list',),
        ('level_5_add',       "    'level_5_add': %s,  ",    'int_list',),
        ('level_6_add',       "    'level_6_add': %s,  ",    'int_list',),
        ('level_7_add',       "    'level_7_add': %s,  ",    'int_list',),
        ('level_8_add',       "    'level_8_add': %s,  ",    'int_list',),
        ('level_9_add',       "    'level_9_add': %s,  ",    'int_list',),
        ('skill4_open',       "    'skill4_open': %s,  ",    'int',),
        ('skill5_open',       "    'skill5_open': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def wheel():
    return [
        ('version',   "%s: {              ",   'int',),
        ('start_time',       "    'start_time': %s,  ",    'str',),
        ('end_time',       "    'end_time': %s,  ",    'str',),
        ('refresh_time',       "    'refresh_time': %s,  ",    'int',),
        ('need_sort',       "    'need_sort': %s,  ",    'int',),
        ('need_num',       "    'need_num': %s,  ",    'int',),
        ('super_item',       "    'super_item': %s,  ",    'int_list', check_reward(),),
        ('daily_limit',       "    'daily_limit': %s,  ",    'int',),
        ('refresh',       "    'refresh': %s,  ",    'int',),
        ('refresh_cost',       "    'refresh_cost': %s,  ",    'int_list',),
        ('normal_reward',       "    'normal_reward': %s,  ",    'int_list', check_reward(is_random=True),),
        ('super_reward',       "    'super_reward': %s,  ",    'int_list', check_reward(is_random=True),),
        ('tips',       "    'tips': %s,  ",    'unicode',),
        ('notice',       "    'notice': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}

def vip_wheel_reward():
    return [
        ('reward_time',   "%s: {              ",   'int',),
        ('vip1',       "    'vip1': %s,  ",    'int',),
        ('vip2',       "    'vip2': %s,  ",    'int',),
        ('vip3',       "    'vip3': %s,  ",    'int',),
        ('vip4',       "    'vip4': %s,  ",    'int',),
        ('vip5',       "    'vip5': %s,  ",    'int',),
        ('vip6',       "    'vip6': %s,  ",    'int',),
        ('vip7',       "    'vip7': %s,  ",    'int',),
        ('vip8',       "    'vip8': %s,  ",    'int',),
        ('vip9',       "    'vip9': %s,  ",    'int',),
        ('vip10',       "    'vip10': %s,  ",    'int',),
        ('vip11',       "    'vip11': %s,  ",    'int',),
        ('vip12',       "    'vip12': %s,  ",    'int',),
        ('vip13',       "    'vip13': %s,  ",    'int',),
        ('vip14',       "    'vip14': %s,  ",    'int',),
        ('vip15',       "    'vip15': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def bounty_order():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',"    'start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',   "    'end_time': %s,   ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('charge_type',      "    'charge_type': %s, ",    'int',),
        ('reward_show_1', "    'reward_show_1': %s,   ",    'int_list',  check_reward(),),
        ('charge_num1',      "    'charge_num1': %s, ",    'int',),
        ('reward_show_2',   "    'reward_show_2': %s,   ",    'int_list', check_reward(),),
        ('charge_num2',      "    'charge_num2': %s, ",    'int',),
        ('reward_show_3',   "    'reward_show_3': %s,   ",    'int_list', check_reward(),),
        ('charge_num3',      "    'charge_num3': %s, ",    'int',),
        ('refresh',   "    'refresh': %s,   ",    'int',),
        ('tips',    "    'tips': %s, ",    'unicode',),
        ('notice',    "    'notice': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def bounty_reward():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',"    'version': %s,    ",    'int',),
        ('team_id',"    'team_id': %s,    ",    'int',),
        ('sort',      "    'sort': %s, ",    'int',),
        ('reward',   "    'reward': %s,   ",    'int_list', check_reward(),),
        ('END',        "},                 ",    'None')
    ], {}


def bounty_detail():
    return [
        ('id',    "%s: {              ",    'int',),
        ('team',      "    'team': %s, ",    'int',),
        ('version',      "    'version': %s, ",    'int',),
        ('rate',      "    'rate': %s, ",    'int',),
        ('story',      "    'story': %s, ",    'unicode',),
        ('open_sort',      "    'open_sort': %s, ",    'int',),
        ('open_data',      "    'open_data': %s, ",    'int',),
        ('target_sort',      "    'target_sort': %s, ",    'int',),
        ('target_data',      "    'target_data': %s, ",    'int',),
        ('close_sort',      "    'close_sort': %s, ",    'int',),
        ('close_data',      "    'close_data': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def equip_refine():
    return [
        ('refine_id',   "%s: {              ",   'int',),
        ('refine_ability',       "    'refine_ability': %s,  ",    'int_list',),
        ('fast_refine_min',       "    'fast_refine_min': %s,  ",    'int_list',),
        ('fast_refine_mid',       "    'fast_refine_mid': %s,  ",    'int_list',),
        ('fast_refine_max',       "    'fast_refine_max': %s,  ",    'int_list',),
        ('refine_min_1',       "    'refine_min_1': %s,  ",    'int_list',),
        ('refine_min_2',       "    'refine_min_2': %s,  ",    'int_list',),
        ('refine_min_cost',       "    'refine_min_cost': %s,  ",    'int_list',),
        ('refine_mid_1',       "    'refine_mid_1': %s,  ",    'int_list',),
        ('refine_mid_2',       "    'refine_mid_2': %s,  ",    'int_list',),
        ('refine_mid_cost',       "    'refine_mid_cost': %s,  ",    'int_list',),
        ('refine_max_1',       "    'refine_max_1': %s,  ",    'int_list',),
        ('refine_max_2',       "    'refine_max_2': %s,  ",    'int_list',),
        ('refine_max_cost',       "    'refine_max_cost': %s,  ",    'int_list',),
        ('refine_control_1',       "    'refine_control_1': %s,  ",    'int_list',),
        ('refine_control_2',       "    'refine_control_2': %s,  ",    'int_list',),
        ('extra_break_1',       "    'extra_break_1': %s,  ",    'int',),
        ('extra_ability_1',       "    'extra_ability_1': %s,  ",    'int_list',),
        ('extra_discrip_1',       "    'extra_discrip_1': %s,  ",    'unicode',),
        ('extra_break_2',       "    'extra_break_2': %s,  ",    'int',),
        ('extra_ability_2',       "    'extra_ability_2': %s,  ",    'int_list',),
        ('extra_discrip_2',       "    'extra_discrip_2': %s,  ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def pet_detail():
    return [
        ('unique_pet_id',     """%s: {                     """ , 'int'),
        ('pet_id',        """ 'pet_id'       : %s,      """ , 'str'),
        ('name',          """ 'name'         : %s,      """ , 'unicode'),
        ('short_story',   """ 'short_story'  : %s,      """ , 'unicode'),
        ('story',         """ 'story'        : %s,      """ , 'unicode'),
        ('img',           """ 'img'          : %s,      """ , 'str'),
        ('animation',     """ 'animation'    : %s,      """ , 'str'),
        ('is_only',       """ 'is_only'      : %s,      """ , 'int'),
        ('is_notice',     """ 'is_notice'    : %s,      """ , 'int'),
        ('is_evo',        """ 'is_evo'       : %s,      """ , 'int'),
        ('rgb_sort',      """ 'rgb_sort'     : %s,      """ , 'int'),
        ('race',          """ 'race'         : %s,      """ , 'int'),
        ('career',        """ 'career'       : %s,      """ , 'int'),
        ('star',          """ 'star'         : %s,      """ , 'int'),
        ('quality',       """ 'quality'      : %s,      """ , 'int'),
        ('type',          """ 'type'         : %s,      """ , 'int'),
        ('star_max',      """ 'star_max'     : %s,      """ , 'int'),
        ('level_max',     """ 'level_max'    : %s,      """ , 'int'),
        ('base_patk',     """ 'base_patk'    : %s,      """ , 'int'),
        ('base_matk',     """ 'base_matk'    : %s,      """ , 'int'),
        ('base_def',      """ 'base_def'     : %s,      """ , 'int'),
        ('base_speed',    """ 'base_speed'   : %s,      """ , 'int'),
        ('base_hp',       """ 'base_hp'      : %s,      """ , 'int'),
        ('growth_patk',   """ 'growth_patk'  : %s,      """ , 'int'),
        ('growth_matk',   """ 'growth_matk'  : %s,      """ , 'int'),
        ('growth_def',    """ 'growth_def'   : %s,      """ , 'int'),
        ('growth_speed',  """ 'growth_speed' : %s,      """ , 'int'),
        ('growth_hp',     """ 'growth_hp'    : %s,      """ , 'int'),
        ('skill1_source', """ 'skill_1_source' : %s,    """ , 'int_list'),
        ('skill2_source', """ 'skill_2_source' : %s,    """ , 'int_list'),
        ('resolve_id',    """ 'resolve_id' : %s,        """ , 'int'),
        ('resolve_num',   """ 'resolve_num'  : %s,      """ , 'int'),
        ('END',           """ },                        """ , 'None'),
    ], {}


def pet_strengthen():
    return [
        ('level'             , """%s: {                         """, 'int') ,
        ('need_star'         , """    'need_star'         : %s, """, 'int') ,
        ('need_time'         , """    'need_time'         : %s, """, 'int') ,
        ('need_food'         , """    'need_food'         : %s, """, 'int') ,
        ('add_patk'          , """    'add_patk'          : %s, """, 'int') ,
        ('need_crstal_patk'  , """    'need_crstal_patk'  : %s, """, 'int_list') ,
        ('add_matk'          , """    'add_matk'          : %s, """, 'int') ,
        ('need_crstal_matk'  , """    'need_crstal_matk'  : %s, """, 'int_list') ,
        ('add_def'           , """    'add_def'           : %s, """, 'int') ,
        ('need_crstal_def'   , """    'need_crstal_def'   : %s, """, 'int_list') ,
        ('add_speed'         , """    'add_speed'         : %s, """, 'int') ,
        ('need_crstal_speed' , """    'need_crstal_speed' : %s, """, 'int_list') ,
        ('add_hp'            , """    'add_hp'            : %s, """, 'int') ,
        ('need_crstal_hp'    , """    'need_crstal_hp'    : %s, """, 'int_list') ,
        ('need_level'        , """    'need_level'        : %s, """, 'int') ,
        ('END', """},                            """, 'None'),
    ], {}

def pet_base():
    return [
        ('level', """%s: {                              """, 'int'),
        ('exp', """    'exp'                      : %s, """, 'int'),
        ('player_level', """'player_level'        : %s, """, 'int'),
        ('END', """},                                   """, 'None'),
    ], {}


def pet_evolution():
    return [
        ('ID',        """ %s: {        """ , 'int'),
        ('step',           """    'step': %s,        """ , 'int'),
        ('degree',       """    'degree': %s,    """ , 'int_list'),
        ('exp',          """    'exp'   : %s,    """ , 'int'),
        ('player_level',       """    'player_level': %s,    """ , 'int'),
        ('need_level',   """    'need_level': %s,    """ , 'int'),
        ('level_off',    """    'level_off': %s,    """ , 'int'),
        ('skill',        """    'skill': %s,    """ , 'int_list'),
        ('story',        """    'story': %s,    """ , 'unicode'),
        ('maxlv',        """    'maxlv': %s,    """ , 'int'),
        ('all',        """    'all': %s,    """ , 'float'),
        ('attr0',       """    'attr0': %s,    """ , 'int_list'),
        ('attr1',       """    'attr1': %s,    """ , 'int_list'),
        ('attr2',       """    'attr2': %s,    """ , 'int_list'),
        ('attr3',       """    'attr3': %s,    """ , 'int_list'),
        ('attr4',       """    'attr4': %s,    """ , 'int_list'),
        ('attr5',       """    'attr5': %s,    """ , 'int_list'),
        ('type0',       """    'type0': %s,    """ , 'int_list'),
        ('type1',       """    'type1': %s,    """ , 'int_list'),
        ('type2',       """    'type2': %s,    """ , 'int_list'),
        ('type3',       """    'type3': %s,    """ , 'int_list'),
        ('type4',       """    'type4': %s,    """ , 'int_list'),
        ('type5',       """    'type5': %s,    """ , 'int_list'),
        ('END', """},                            """, 'None'),
    ], {}


def pet_corral():
    return [
        ('position',     """ %s: {               """,   'int'),
        ('is_open',      """    'is_open': %s,   """,   'int'),
        ('sort',         """    'sort': %s,      """,   'int'),
        ('price',        """    'price'   : %s,  """,   'int'),
        ('limit_lv',     """    'limit_lv': %s,  """,   'int'),
        ('END', """},                            """, 'None'),
    ], {}


def pet_skill_detail():
    return [
        ('skill_ID',      """%s: {                   """ , 'int'),
        ('skill_name',    """ 'skill_name'     : %s, """ , 'unicode'),
        ('skill_story',   """ 'skill_story'    : %s, """ , 'unicode'),
        ('skill_icon',    """ 'skill_icon'     : %s, """ , 'str'),
        ('skill_type',    """ 'skill_type'     : %s, """ , 'str'),
        ('rate',          """ 'rate'           : %s, """ , 'int'),
        ('cd',            """ 'cd'             : %s, """ , 'int'),
        ('pre_cd',        """ 'pre_cd'         : %s, """ , 'int'),
        ('skill_quality', """ 'skill_quality'  : %s, """ , 'int'),
        ('max_lv',        """ 'max_lv'         : %s, """ , 'int'),
        ('effect',        """ 'effect'         : %s, """ , 'int'),
        ('effect_lvchange',""" 'effect_lvchange': %s, """ , 'float'),
        ('is_evolution',  """ 'is_evolution'   : %s, """ , 'int'),
        ('evo_food',      """ 'evo_food'      : %s,  """ , 'int'),
        ('sprite_py',     """ 'sprite_py'      : %s, """ , 'str'),
        ('resouce_type',  """ 'resource_type'  : %s, """ , 'int'),
        ('resouce_count', """ 'resource_count' : %s, """ , 'int'),
        ('attack_effect', """ 'attack_effect': %s,   """ , 'str'),
        ('effect_delay',  """ 'effect_delay': %s,    """ , 'int'),
        ('is_learn',      """ 'is_learn'       : %s, """ , 'int'),
        ('action',        """ 'action'         : %s, """ , 'int'),
        ('evo_story'   ,  """ 'evo_story':    %s,    """ , 'unicode'),
        ('attr_effect',   """ 'attr_effect'    : %s, """ , 'int'),
        ('END',           """ },                     """ , 'None'),
    ], {}


def pet_skill_levelup():
    return [
            (('skill_level',
              'skill_exp_0', 'skill_exp_1', 'skill_exp_2', 'skill_exp_3',
              'skill_exp_4', 'skill_exp_5', 'skill_exp_6', 'skill_exp_7',
              'stone_cost_0', 'stone_cost_1', 'stone_cost_2', 'stone_cost_3',
              'stone_cost_4', 'stone_cost_5', 'stone_cost_6', 'stone_cost_7'),
             """%s: {'skill_exp': (%s, %s, %s, %s, %s, %s, %s, %s), 'stone_cost': (%s, %s, %s, %s, %s, %s, %s, %s)},""",
             ('int',
              'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int',
              'int', 'int', 'int', 'int', 'int', 'int', 'int', 'int')),
    ], {}


def grow_gift():
    return [
        ('level',   "%s: {              ",   'int',),
        ('reward',  "    'reward': %s,  ",   'int_list',),
        ('END',     "},                 ",   'None')
    ], {}


def daily_new():
    return [
        ('daily_ID', """%s: {""", 'int'),
        ('icon',        """ 'icon_name'       : %s, """, 'str'),
        ('name',        """ 'name'       : %s, """, 'unicode'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('open_sort',   """ 'open_sort'  : %s, """, 'int'),
        ('open_data',   """ 'open_data'  : %s, """, 'int'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_data', """ 'target_data': %s, """, 'int'),
        ('target_data1', """ 'target_data1': %s, """, 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('score', """ 'score': %s, """, 'int'),
        ('close_sort',   """ 'close_sort'  : %s, """, 'int'),
        ('close_data',   """ 'close_data'  : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}


def recall_mission():
    return [
        ('daily_ID', """%s: {""", 'int'),
        ('icon',        """ 'icon'       : %s, """, 'str'),
        ('name',        """ 'name'       : %s, """, 'unicode'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('open_sort',   """ 'open_sort'  : %s, """, 'int'),
        ('open_data',   """ 'open_data'  : %s, """, 'int'),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_data', """ 'target_data': %s, """, 'int'),
        ('target_data1', """ 'target_data1': %s, """, 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('score', """ 'score': %s, """, 'int'),
        ('close_sort',   """ 'close_sort'  : %s, """, 'int'),
        ('close_data',   """ 'close_data'  : %s, """, 'int'),
        ('END', """},""", 'None'),
    ], {}


def daily_score_new():
    return [
        ('score', """%s: {""", 'int'),
        ('level', """ 'level': %s, """, 'int_list'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('level2', """ 'level2': %s, """, 'int_list'),
        ('reward2',      """ 'reward2'     : %s, """, 'int_list', check_reward(),),
        ('END', """},""", 'None'),
    ], {}


def server_bounty_order():
    return [
        ('version',"""                        %s: {   """,          'int'),
        ('charge_type',"""    'charge_type':        %s ,  """,           'int'),
        ('reward_show_1',"""   'reward_show_1': %s, """,               'int_list'),
        ('charge_num1',""" 'charge_num1':       %s, """,             "int"),
        ('reward_show_2',"""   'reward_show_2': %s, """,             'int_list'),
        ('charge_num2',"""    'charge_num2':   %s,    """,           'int'),
        ('reward_show_3',"""   'reward_show_3': %s, """,              'int_list'),
        ('charge_num3',""" 'charge_num3':       %s, """,                 'int'),
        ('refresh',""" 'refresh':               %s,   """,               'int'),
        ('tips',"""    'tips':                  %s,  """,              'unicode'),
        ('notice',"""  'notice':                %s,    """,          'unicode'),
        ('END',"""                              } ,""",                 'None'),
    ],  {}


def server_bounty_reward():
    return [
        ('id',"""                             %s:       {  """,         'int'),
        ('version',"""  'version':             %s,      """,                'int'),
        ('sort',"""  'sort':                   %s,          """,           'int'),
        ('reward',"""   'reward':               %s,    """   ,           'int_list'),
        ('END', """              },                   """   ,       'None'),
    ], {}


def server_bounty_detail():
    return [
        ('id',"""                           %s:  {    """,           'int'),
        ('team',"""      'team':               %s,  """,                'int'),
        ('rate',  """   'rate':                  %s,  """,                'int'),
        ('story',"""  'story':                 %s,    """,           'unicode'),
        ('open_sort',"""  'open_sort':         %s, """,             'int'),
        ('open_data',"""  'open_data':         %s,    """,           'int'),
        ('target_sort',"""    'target_sort':      %s,  """,              'int'),
        ('target_data',"""    'target_data':       %s,   """,        'int'),
        ('close_sort',""" 'close_sort':            %s,    """,          'int'),
        ('close_data',""" 'close_data':            %s,   """,        'int'),
        ('END',"""    } ,  """,                  'None'),
    ], {}


def server_wheel():
    return [
        ('version',   "%s: {              ",   'int',),
        ('refresh_time',       "    'refresh_time': %s,  ",    'int',),
        ('need_sort',       "    'need_sort': %s,  ",    'int',),
        ('need_num',       "    'need_num': %s,  ",    'int',),
        ('super_item',       "    'super_item': %s,  ",    'int_list',),
        ('daily_limit',       "    'daily_limit': %s,  ",    'int',),
        ('refresh',       "    'refresh': %s,  ",    'int',),
        ('refresh_cost',       "    'refresh_cost': %s,  ",    'int_list',),
        ('normal_reward',       "    'normal_reward': %s,  ",    'int_list',),
        ('super_reward',       "    'super_reward': %s,  ",    'int_list',),
        ('tips',       "    'tips': %s,  ",    'unicode',),
        ('notice',       "    'notice': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def server_vip_wheel_reward():
    return [
        ('reward_time',   "%s: {              ",   'int',),
        ('vip1',       "    'vip1': %s,  ",    'int',),
        ('vip2',       "    'vip2': %s,  ",    'int',),
        ('vip3',       "    'vip3': %s,  ",    'int',),
        ('vip4',       "    'vip4': %s,  ",    'int',),
        ('vip5',       "    'vip5': %s,  ",    'int',),
        ('vip6',       "    'vip6': %s,  ",    'int',),
        ('vip7',       "    'vip7': %s,  ",    'int',),
        ('vip8',       "    'vip8': %s,  ",    'int',),
        ('vip9',       "    'vip9': %s,  ",    'int',),
        ('vip10',       "    'vip10': %s,  ",    'int',),
        ('vip11',       "    'vip11': %s,  ",    'int',),
        ('vip12',       "    'vip12': %s,  ",    'int',),
        ('vip13',       "    'vip13': %s,  ",    'int',),
        ('vip14',       "    'vip14': %s,  ",    'int',),
        ('vip15',       "    'vip15': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def team_boss():
    return [
        ('boss_id',   "%s: {              ",   'int',),
        ('time_sort',       "    'time_sort': %s,  ",    'int_list',),
        ('donation_open',       "    'donation_open': %s,  ",    'str',),
        ('donation_close',       "    'donation_close': %s,  ",    'str',),
        ('open',       "    'open': %s,  ",    'str',),
        ('insert_time',       "    'insert_time': %s,  ",    'str',),
        ('sec_time',       "    'sec_time': %s,  ",    'str',),
        ('thr_time',       "    'thr_time': %s,  ",    'str',),
        ('close',       "    'close': %s,  ",    'str',),
        ('background',       "    'background': %s,  ",    'str',),
        ('enemy_id',       "    'enemy_id': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def team_boss_score():
    return [
        ('reward_id',   "%s: {              ",   'int',),
        ('team1_point',       "    'team1_point': %s,  ",    'int',),
        ('team2_point',       "    'team2_point': %s,  ",    'int',),
        ('team3_point',       "    'team3_point': %s,  ",    'int',),
        ('team10_point',       "    'team10_point': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def team_boss_reward():
    return [
        ('reward_id',   "%s: {              ",   'int',),
        ('kill',       "    'kill': %s,  ",    'int_list',),
        ('team1',       "    'team1': %s,  ",    'int_list',),
        ('team2',       "    'team2': %s,  ",    'int_list',),
        ('team3',       "    'team3': %s,  ",    'int_list',),
        ('team10',       "    'team10': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}


def team_boss_exchange():
    return [
        ('id',   "%s: {              ",   'int',),
        ('reward',       "    'reward': %s,  ",    'int_list',),
        ('cost',       "    'cost': %s,  ",    'int',),
        ('limits',       "    'limits': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def adventure_level():
    return[
        ('level', """                %s: {             """,      'int'),
        ('enemy1', """   'enemy1':    %s,              """,      'int_list'),
        ('enemy2', """   'enemy2':    %s,              """,      'int_list'),
        ('enemy3', """   'enemy3':    %s,              """,      'int_list'),
        ('enemy4', """   'enemy4':    %s,              """,      'int_list'),
        ('enemy5', """   'enemy5':    %s,              """,      'int_list'),
        ('enemy6', """   'enemy6':    %s,              """,      'int_list'),
        ('enemy7', """   'enemy7':    %s,              """,      'int_list'),
        ('enemy8', """   'enemy8':    %s,              """,      'int_list'),
        ('enemy9', """   'enemy9':    %s,              """,      'int_list'),
        ('reward', """   'reward':    %s,              """,      'int_list'),
        ('END',    """   },                            """,      'None'),
    ], {}


def adventure_stage():
    return [
        ('stage_id',            """              %s:{             """,       'int'),
        ('name',                """  'name':     %s,              """,       'str'),
        ('des',                 """  'des':      %s,              """,       'str'),
        ('icon',                """  'icon':     %s,              """,       'str'),
        ('hp',                  """  'hp':       %s,              """,       'int_list'),
        ('attack',              """  'attack':   %s,              """,       'int_list'),
        ('sort',                """  'sort':     %s,              """,       'int'),
        ('effect',              """  'effect':   %s,              """,       'int'),
        ('effect_sort',         """  'effect_sort':   %s,         """,       'int'),
        ('reward',              """  'reward':   %s,              """,       'int_list'),
        ('END',                 """         },                    """,       'None'),
    ], {}


def adventure_top_score():
    return [
        ('id',         """                    %s:{              """,        'int'),
        ('start_rank', """   'start_rank':    %s,               """,        'int'),
        ('end_rank',   """   'end_rank':      %s,               """,        'int'),
        ('per_point',  """   'per_point':     %s,               """,        'int'),
        ('END',        """         },                           """,       'None'),
    ], {}


def adventure_exchange():
    return [
        ('id',         """                    %s:{              """,        'int'),
        ('reward',     """   'reward':        %s,               """,        'int_list'),
        ('des',        """   'des':           %s,               """,        'unicode'),
        ('cost',       """   'cost':          %s,               """,        'int'),
        ('limits',     """   'limits':        %s,               """,        'int'),
        ('END',        """         },                           """,       'None'),
    ], {}


def normal_exchange():
    return [
        ('id',         "%s: {               ",    'int',),
        ('show_id',     "    'show_id': %s,   ",    'int'),
        ('type',  "    'type': %s,",    'int',),
        ('exchange_type',       "    'exchange_type': %s,     ",    'int',),
        ('exchange_num',  "    'exchange_num': %s,",    'int',),
        ('exchange_time',  "    'exchange_time': %s,",    'int',),
        ('start_time',  "    'start_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M")),
        ('end_time',  "    'end_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M")),
        ('material_type',  "    'material_type': %s,",    'int',),
        ('step',  "    'step': %s,",    'int',),
        ('break',  "    'break': %s,",    'int',),
        ('strengthen',  "    'strengthen': %s,",    'int',),
        ('equip_st',  "    'equip_st': %s,",    'int',),
        ('need_item',  "    'need_item': %s,",    'int_list', check_reward(),),
        ('out_item1',  "    'out_item1': %s,",    'int_list', check_reward(),),
        ('out_item2',  "    'out_item2': %s,",    'int_list', check_reward(),),
        ('out_item3',  "    'out_item3': %s,",    'int_list', check_reward(),),
        ('out_item4',  "    'out_item4': %s,",    'int_list', check_reward(),),
        ('out_item5',  "    'out_item5': %s,",    'int_list', check_reward(),),
        ('END',        "},                  ",    'None')
    ], {}


def redpacket():
    return [
        ('packet_id',         "%s: {               ",    'int',),
        ('start_time',  "    'start_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time',  "    'end_time': %s,",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('title',  "    'title': %s,",    'unicode',),
        ('word',  "    'word': %s,",    'unicode',),
        ('reward',  "    'reward': %s,",    'int_list', check_reward(),),
        ('level',  "    'level': %s,",    'int_single_list',),
        ('banner',  "    'banner': %s,",    'str',),
        ('END',        "},                  ",    'None')
    ], {}


def exchange_equip():
    return [
        ('exchange_id',         "%s: {               ",    'int',),
        ('melting_need',     "    'melting_need': %s,   ",    'int_single_list'),
        ('metal',     "    'metal': %s,   ",    'int'),
        ('quality',      "    'quality': %s,    ",    'int'),
        ('first_reward', "    'first_reward': %s, ",    'int_list', check_reward(is_random=True)),
        ('equip_reward', "    'equip_reward': %s, ",    'int_list', check_reward(is_random=True)),
        ('num',       "    'num': %s,     ",    'int'),
        ('gift_num',       "    'gift_num': %s,     ",    'int_single_list'),
        ('gift_reward',  "    'gift_reward': %s,",    'int_list', check_reward(is_random=True)),
        ('END',        "},                  ",    'None')
    ], {}


def exchange_equip_shop():
    return [
        ('id',         "%s: {               ",    'int',),
        ('item',       "    'item': %s,   ",    'int_list'),
        ('sort',       "    'sort': %s,   ",    'int'),
        ('value',      "    'value': %s,  ",    'int'),
        ('weight',     "    'weight': %s, ",    'int'),
        ('show_level', "    'show_level': %s, ",    'int_single_list'),
        ('END',        "},                  ",    'None')
    ], {}


def league_time():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',"    'start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('apply_end_time',"    'apply_end_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('fight_start_time',"    'fight_start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('fight_end_time',"    'fight_end_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('sum_start_time',"    'sum_start_time': %s,    ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('end_time',   "    'end_time': %s,   ",    'str', check_time(tformat="%Y/%m/%d %H:%M:%S"),),
        ('END',        """         },                           """,       'None'),
    ], {}


def league_world():
    return [
        ('server_id',    "%s: {              ",    'str',),
        ('world_id',"    'world_id': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def league_exchange():
    return [
        ('id',         """                    %s:{              """,        'int'),
        ('reward',     """   'reward':        %s,               """,        'int_list'),
        ('des',        """   'des':           %s,               """,        'unicode'),
        ('cost',       """   'cost':          %s,               """,        'int'),
        ('times',       """   'times':          %s,               """,        'int'),
        ('refresh',       """   'refresh':          %s,               """,        'int'),
        ('show_level',     """   'show_level':        %s,               """,        'int_list'),
        ('END',        """         },                           """,       'None'),
    ], {}


def league_reward():
    return [
        ('id',         """                    %s:{              """,        'int'),
        ('team',       """   'team':          %s,               """,        'int'),
        ('rank',        "'rank': %s, ",       'int_list', check_int_list_args(2)),
        ('des',        """   'des':           %s,               """,        'unicode'),
        ('reward',     """   'reward':        %s,               """,        'int_list'),
        ('integration',        """   'integration':           %s,               """,        'int'),
        ('mail',        """   'mail':           %s,               """,        'unicode'),
        ('END',        """         },                           """,       'None'),
    ], {}


def vip_reward():
    return [
        ('id',         "%s: {               ",    'int',),
        ('reward',  "    'reward': %s,",    'int_list', check_reward(),),
        ('mail',  "    'mail': %s,",    'unicode',),
        ('END',        "},                  ",    'None')
    ], {}


def medal():
    return [
        ('medal_id',         "%s: {               ",    'str',),
        ('name',         """    'name'          : %s, """, 'unicode'),
        ('icon',           """    'icon'           : %s, """, 'str'),
        ('price',       """   'price':          %s,               """,        'int'),
        ('quality',       """   'quality':          %s,               """,        'int'),
        ('effect',     """   'effect':        %s,               """,        'int_list'),
        ('material',     """   'material':        %s,               """,        'int_list'),
        ('des',     """   'des':        %s,               """,        'unicode'),
        ('time',       """   'time':          %s,               """,        'int'),
        ('END',        "},                  ",    'None')
    ], {}


def material():
    return [
        ('material_id',         "%s: {               ",    'str',),
        ('name',         """    'name'          : %s, """, 'unicode'),
        ('icon',           """    'icon'           : %s, """, 'str'),
        ('price',       """   'price':          %s,               """,        'int'),
        ('quality',       """   'quality':          %s,               """,        'int'),
        ('material',     """   'material':        %s,               """,        'int_list'),
        ('exchange_item',     """   'exchange_item':        %s,               """,        'int_list'),
        ('exchange_coin',     """   'exchange_coin':        %s,               """,        'int'),
        ('des',     """   'des':        %s,               """,        'unicode'),
        ('END',        "},                  ",    'None')
    ], {}


def position():
    return [
        ('position_id',         "%s: {               ",    'str',),
        ('adv_level',     """   'adv_level':        %s,               """,        'int'),
        ('END',        "},                  ",    'None')
    ], {}


def adver_pk():
    return [
        ('adver_id', """%s:{""", 'int',),
        ('adver_type', "'adver_type': %s,", 'int'),
        ('mark', "'mark': %s,", 'int'),
        ('start_time', "'start_time': %s,", 'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('end_time', "'end_time': %s,", 'str', check_time(tformat="%Y/%m/%d %H:%M:%S")),
        ('banner', "'banner': %s,", 'str'),
        ('title', "'title': %s,", 'unicode'),
        ('ad_title', "'ad_title': %s,", 'unicode'),
        ('word', "'word': %s,", 'unicode'),
        ('time', "'time': %s,", 'unicode'),
        ('server_time', "'server_time': %s,", 'unicode'),
        ('END', """},""", 'None')
    ], {}


def team_pk_world():
    return [
        ('server',    "%s: {              ",    'str',),
        ('world_id',"    'world_id': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def team_pk_time():
    return [
        ('id',   "%s: {              ",   'int',),
        ('time_sort',       "    'time_sort': %s,  ",    'int_list',),
        ('donation_open_time',       "    'donation_open_time': %s,  ",    'str',),
        ('donation_close_time',       "    'donation_close_time': %s,  ",    'str',),
        ('ready_time',       "    'ready_time': %s,  ",    'str',),
        ('open_time',       "    'open_time': %s,  ",    'str',),
        ('pk_close_time',       "    'pk_close_time': %s,  ",    'str',),
        ('close_time',       "    'close_time': %s,  ",    'str',),
        ('reward_time',       "    'reward_time': %s,  ",    'str',),
        ('boss_id',       "    'boss_id': %s,  ",    'int',),
        ('boss_hp',       "    'boss_hp': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def team_pk_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('team_reward',       "    'team_reward': %s,  ",    'int_list',),
        ('reward_member',       "    'reward_member': %s,  ",    'int_list',),
        ('reward_ordinary',       "    'reward_ordinary': %s,  ",    'int_list',),
        ('reward_member_score',       "    'reward_member_score': %s,  ",    'int',),
        ('reward_ordinary_score',       "    'reward_ordinary_score': %s,  ",    'int',),
        ('mail_member',       "    'mail_member': %s,  ",    'unicode',),
        ('mail_ordinary',       "    'mail_ordinary': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def team_pk_exchange():
    return [
        ('id',   "%s: {              ",   'int',),
        ('reward',       "    'reward': %s,  ",    'int_list',),
        ('des',       "    'des': %s,  ",    'unicode',),
        ('cost',       "    'cost': %s,  ",    'int',),
        ('times',       """   'times':          %s,               """,        'int'),
        ('refresh',       """   'refresh':          %s,               """,        'int'),
        ('limits',       "    'limits': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}


def super_commander_detail():
    return [
        ('id', """%s: {                          """, 'int'),
        ('name', """      'name'             : %s, """, 'unicode'),
        ('story', """      'story'            : %s, """, 'unicode'),
        ('icon', """      'icon'             : %s, """, 'str'),
        ('quality', """      'quality'             : %s, """, 'int'),
        ('tree', """      'tree'             : %s, """, 'int'),
        ('xy', """      'xy'               : %s, """, 'int_list'),
        ('race', """      'race'               : %s, """, 'int'),
        ('max_level', """      'max_level'        : %s, """, 'int'),
        ('effect_1', """      'effect_1'        : %s, """, 'int_list'),
        ('effect_2', """      'effect_2'        : %s, """, 'int_list'),
        ('effect_3', """      'effect_3'        : %s, """, 'int_list'),
        ('effect_4', """      'effect_4'        : %s, """, 'int_list'),
        ('effect_5', """      'effect_5'        : %s, """, 'int_list'),
        ('cost1', """      'cost1'               : %s, """, 'int_list'),
        ('cost2', """      'cost2'               : %s, """, 'int_list'),
        ('cost3', """      'cost3'               : %s, """, 'int_list'),
        ('cost4', """      'cost4'               : %s, """, 'int_list'),
        ('cost5', """      'cost5'               : %s, """, 'int_list'),
        ('step', """      'step'               : %s, """, 'int_list'),
        ('END', """},                             """, 'None'),
    ], {}


def super_commander_tree():
    return [
        ('tree_id',         "%s: {               ",    'int',),
        ('name', """      'name'             : %s, """, 'unicode'),
        ('race', """      'race'             : %s, """, 'int'),
        ('des', """      'des'             : %s, """, 'unicode'),
        ('open_sort', """      'open_sort'               : %s, """, 'int'),
        ('data', """      'data'             : %s, """, 'int'),
        ('END', """},                             """, 'None'),
    ], {}


def hero_race():
    return [
        ('id',         "%s: {               ",    'int',),
        ('race', """      'race'             : %s, """, 'int'),
        ('is_see', """      'is_see'             : %s, """, 'int'),
        ('END', """},                             """, 'None'),
    ], {}


def leader_base_mission():
    return [
        ('mission_id',         "%s: {               ",    'int',),
        ('sort', """      'sort'             : %s, """, 'int'),
        ('refresh', """      'refresh'             : %s, """, 'int'),
        ('rate', """      'rate'             : %s, """, 'int'),
        ('reward', """      'reward'             : %s, """, 'int_list'),
        ('story', """      'story'            : %s, """, 'unicode'),
        ('target_sort', """      'target_sort'             : %s, """, 'int'),
        ('target_data', """      'target_data'             : %s, """, 'int'),
        ('target_data1', """      'target_data1'             : %s, """, 'int'),
        ('open_sort', """      'open_sort'             : %s, """, 'int'),
        ('open_data', """      'open_data'             : %s, """, 'int'),
        ('close_sort', """      'close_sort'             : %s, """, 'int'),
        ('close_data', """      'close_data'             : %s, """, 'int'),
        ('END', """},                             """, 'None'),
    ], {}


def server_link():
    return [
        ('server_id',         "%s: {               ",    'str',),
        ('world_id',     """   'world_id':        %s,               """,        'int'),
        ('country_id',     """   'country_id':        %s,               """,        'int'),
        ('score',     """   'score':        %s,               """,        'int'),
        ('END',        "},                  ",    'None')
    ], {}, ['check_server_link']


def leader_skill_advanced():
    return [
        ('id',         "%s: {               ",    'int',),
        ('name', """      'name'             : %s, """, 'unicode'),
        ('story', """      'story'            : %s, """, 'unicode'),
        ('max_level', """      'max_level'        : %s, """, 'int'),
        ('cost6', """      'cost6'               : %s, """, 'int_list'),
        ('cost7', """      'cost7'               : %s, """, 'int_list'),
        ('cost8', """      'cost8'               : %s, """, 'int_list'),
        ('add_effect3', """      'add_effect3'        : %s, """, 'int'),
        ('base_effect4', """      'base_effect4'        : %s, """, 'int'),
        ('add_effect4', """      'add_effect4'        : %s, """, 'int'),
        ('END',        "},                  ",    'None')
    ], {}


def large_roulette():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',"    'start_time': %s,    ",    'str',),
        ('end_time',   "    'end_time': %s,   ",    'str',),
        ('refresh_price', "    'refresh_price': %s,   ",    'int',),
        ('price',      "    'price': %s, ",    'int',),
        ('price_10',   "    'price_10': %s,   ",    'int',),
        ('score',      "    'score': %s, ",    'int',),
        ('score_10',   "    'score_10': %s,   ",    'int',),
        ('day_refresh_num', "    'day_refresh_num': %s,  ",    'int',),
        ('day_num',        "    'day_num': %s,     ",    'int',),
        ('best_must_reward', "    'best_must_reward': %s, ",    'int',),
        ('must_reward',    "    'must_reward': %s, ",    'int',),
        ('instruction',    "    'instruction': %s, ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def large_pond():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version', "    'version': %s,   ",    'int',),
        ('fire_id', "    'fire_id': %s,   ",    'int',),
        ('id', "         'id': %s,   ",         'int',),
        ('coin',         "    'coin': %s, ",    'int',),
        ('server_player',      "    'server_player': %s, ",    'int_list',),
        ('max_score',      "    'max_score': %s, ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def large_roulette_reward():
    return [
        ('version',    "%s: {              ",    'int',),
        ('limit_ins',"    'limit_ins': %s,    ",    'unicode',),
        ('day_limite_reward_00',"    'day_limite_reward_00': %s,    ",    'int_list',),
        ('best_limite_reward_00',   "    'best_limite_reward_00': %s,   ",    'int_list',),
        ('limite_reward_00',   "    'limite_reward_00': %s,   ",    'int_list',),
        ('day_limite_reward_12',"    'day_limite_reward_12': %s,    ",    'int_list',),
        ('best_limite_reward_12',   "    'best_limite_reward_12': %s,   ",    'int_list',),
        ('limite_reward_12',   "    'limite_reward_12': %s,   ",    'int_list',),
        ('day_limite_reward_21',"    'day_limite_reward_21': %s,    ",    'int_list',),
        ('best_limite_reward_21',   "    'best_limite_reward_21': %s,   ",    'int_list',),
        ('limite_reward_21',   "    'limite_reward_21': %s,   ",    'int_list',),
        ('common_reward1', "    'common_reward1': %s,   ",    'int_list',),
        ('common_reward2', "    'common_reward2': %s,   ",    'int_list',),
        ('common_reward3', "    'common_reward3': %s,   ",    'int_list',),
        ('reward_chance', "    'reward_chance': %s, ",    'int_list',),
        ('best_reward_show', "    'best_reward_show': %s, ",    'int_list',),
        ('reward_show', "    'reward_show': %s, ",    'int_list',),
        ('common_reward1_show', "    'common_reward1_show': %s, ",    'int_list',),
        ('common_reward2_show', "    'common_reward2_show': %s, ",    'int_list',),
        ('common_reward3_show', "    'common_reward3_show': %s, ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def large_super_all():
    return [
        ('id',         "%s: {               ",    'int',),
        ('version',     """   'version':        %s,               """,        'int'),
        ('start_time',     """   'start_time':        %s,               """,        'str'),
        ('end_time',     """   'end_time':        %s,               """,        'str'),
        ('action_point',     """   'action_point':        %s,               """,        'int'),
        ('percent',     """   'percent':        %s,               """,        'int'),
        ('base',     """   'base':        %s,               """,        'int'),
        ('reward',     """   'reward':        %s,               """,        'int_list'),
        ('des',     """   'des':        %s,               """,        'unicode'),
        ('notice',     """   'notice':        %s,               """,        'unicode'),
        ('END',        "},                  ",    'None')
    ], {}


def festival():
    return [
        ('festival_id',         "%s: {               ",    'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('show_time',       "    'show_time': %s,  ",    'str',),
        ('type', """      'type'        : %s, """, 'int'),
        ('banner', """      'banner'               : %s, """, 'str'),
        ('icon', """      'icon'               : %s, """, 'str'),
        ('des', """      'des'             : %s, """, 'unicode'),
        ('END',        "},                  ",    'None')
    ], {}


def festival_daily():
    return [
        ('id',         "%s: {               ",    'int',),
        ('version', """      'version'        : %s, """, 'int'),
        ('score', """      'score'        : %s, """, 'int'),
        ('icon', """      'icon'               : %s, """, 'str'),
        ('award', """      'award'               : %s, """, 'int_list'),
        ('time', """      'time'               : %s, """, 'str'),
        ('END',        "},                  ",    'None')
    ], {}


def large_super_rich():
    return [
        ('id',         "%s: {               ",    'int',),
        ('version',     """   'version':        %s,               """,        'int'),
        ('rank',     """   'rank':        %s,               """,        'int'),
        ('start_time',     """   'start_time':        %s,               """,        'str'),
        ('end_time',     """   'end_time':        %s,               """,        'str'),
        ('reward_12',     """   'reward_12':        %s,               """,        'int_list'),
        ('reward_21',     """   'reward_21':        %s,               """,        'int_list'),
        ('reward_24',     """   'reward_24':        %s,               """,        'int_list'),
        ('mail',     """   'mail':        %s,               """,        'unicode'),
        ('END',        "},                  ",    'None')
    ], {}


def festival_shop():
    return [
        ('shop_id',         "%s: {               ",    'int',),
        ('version', """      'version'        : %s, """, 'int'),
        ('shop_reward1', """      'shop_reward1'               : %s, """, 'int_list'),
        ('shop_reward2', """      'shop_reward2'               : %s, """, 'int_list'),
        ('shop_reward3', """      'shop_reward3'               : %s, """, 'int_list'),
        ('shop_reward4', """      'shop_reward4'               : %s, """, 'int_list'),
        ('value', """      'value'        : %s, """, 'int'),
        ('sell_max', """      'sell_max'        : %s, """, 'int'),
        ('time', """      'time'        : %s, """, 'str'),
        ('END',        "},                  ",    'None')
    ], {}


def large_super_rich_all():
    return [
        ('id',         "%s: {               ",    'int',),
        ('version',     """   'version':        %s,               """,        'int'),
        ('rank',     """   'rank':        %s,               """,        'int'),
        ('show12',     """   'show12':        %s,               """,        'int_list'),
        ('show21',     """   'show21':        %s,               """,        'int_list'),
        ('show24',     """   'show24':        %s,               """,        'int_list'),
        ('reward_12',     """   'reward_12':        %s,               """,        'int_list'),
        ('reward_21',     """   'reward_21':        %s,               """,        'int_list'),
        ('reward_24',     """   'reward_24':        %s,               """,        'int_list'),
        ('notice',     """   'notice':        %s,               """,        'unicode'),
        ('mail',     """   'mail':        %s,               """,        'unicode'),
        ('END',        "},                  ",    'None')
    ], {}


def festival_exchange():
    return [
        ('exchange_id',         "%s: {               ",    'int',),
        ('version', """      'version'        : %s, """, 'int'),
        ('ex_num', """      'ex_num'        : %s, """, 'int'),
        ('need_item', """      'need_item'               : %s, """, 'int_list'),
        ('out_item1', """      'out_item1'               : %s, """, 'int_list'),
        ('out_item2', """      'out_item2'               : %s, """, 'int_list'),
        ('out_item3', """      'out_item3'               : %s, """, 'int_list'),
        ('out_item4', """      'out_item4'               : %s, """, 'int_list'),
        ('time', """      'time'               : %s, """, 'str'),
        ('END',        "},                  ",    'None')
    ], {}


def pet_follow():
    return [
        ('position',         "%s: {               ",    'int',),
        ('sort', """      'sort'             : %s, """, 'int'),
        ('price', """      'price'            : %s, """, 'int'),
        ('vip', """      'vip'        : %s, """, 'int'),
        ('value', """      'value'               : %s, """, 'int'),
        ('END',        "},                  ",    'None')
    ], {}


def equip_set_level():
    return [
        ('level',         "%s: {               ",    'int',),
        ('need', """      'need'             : %s, """, 'int'),
        ('add1', """      'add1'            : %s, """, 'int'),
        ('add2', """      'add2'        : %s, """, 'int'),
        ('add3', """      'add3'               : %s, """, 'int'),
        ('add4', """      'add4'               : %s, """, 'int'),
        ('END',        "},                  ",    'None')
    ], {}


def equip_set_random():
    return [
        ('id',         "%s: {               ",    'int',),
        ('ability', """      'ability'             : %s, """, 'float'),
        ('weight', """      'weight'            : %s, """, 'int'),
        ('quality', """      'quality'        : %s, """, 'int'),
        ('sort', """      'sort'               : %s, """, 'int'),
        ('equip_sort', """      'equip_sort'               : %s, """, 'int_list'),
        ('enemy', """      'enemy'               : %s, """, 'int_list'),
        ('END',        "},                  ",    'None')
    ], {}


def equip_set_cost():
    return [
        ('id',         "%s: {               ",    'int',),
        ('cost', """      'cost'               : %s, """, 'int_list'),
        ('END',        "},                  ",    'None')
    ], {}


def soul_detail():
    return [
        ('soul_id',      """    %s:{                            """,        'int'),
        ('quality',      """   'quality':        %s,            """,        'int'),
        ('name',         """   'name':           %s,            """,        'unicode'),
        ('icon',         """   'icon':           %s,            """,        'str'),
        ('des',          """   'des':            %s,            """,        'unicode'),
        ('max_level',    """   'max_level':      %s,            """,        'int'),
        ('ability',      """   'ability':        %s,            """,        'int'),
        ('value',        """   'value':          %s,            """,        'int'),
        ('level_add',    """   'level_add':      %s,            """,        'float'),
        ('exp_type',     """   'exp_type':       %s,            """,        'int'),
        ('exp',          """   'exp':            %s,            """,        'int'),
        ('sort',          """   'sort':            %s,            """,        'int'),
        ('sell_food',          """   'sell_food':            %s,            """,        'int'),
        ('END',          """    },                              """,        'None'),
    ], {}


def soul_gacha():
    return [
        ('gacha_id',     """    %s:{                            """,        'int'),
        ('statue',       """   'statue':         %s,            """,        'int'),
        ('quality',      """   'quality':        %s,            """,        'int'),
        ('need_meet',    """   'need_meet':      %s,            """,        'int'),
        ('add_rate',     """   'add_rate':       %s,            """,        'int'),
        ('back_rate',    """   'back_rate':      %s,            """,        'int'),
        ('soul_box',     """   'soul_box':       %s,            """,        'int_list'),
        ('END',          """    },                              """,        'None'),
    ], {}


def soul_exp():
    return [
        ('soul_level',        """    %s:{                       """,    'int'),
        ('need_exp_type1',    """   'need_exp_type1':    %s,    """,    'int'),
        ('need_exp_type2',    """   'need_exp_type2':    %s,    """,    'int'),
        ('need_exp_type3',    """   'need_exp_type3':    %s,    """,    'int'),
        ('need_exp_type4',    """   'need_exp_type4':    %s,    """,    'int'),
        ('need_exp_type5',    """   'need_exp_type5':    %s,    """,    'int'),
        ('END',               """    },                         """,    'None'),
    ], {}


def fast_material_cost():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('sort',    """   'sort':    %s,    """,    'int'),
        ('material_1',    """   'material_1':    %s,    """,    'int_list'),
        ('material_2',    """   'material_2':    %s,    """,    'int'),
        ('cost',    """   'cost':    %s,    """,    'int'),
        ('END',               """    },                         """,    'None'),
    ], {}


def peak_arena_reward():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('win',    """   'win':    %s,    """,    'int'),
        ('reward',    """   'reward':    %s,    """,    'int_list'),
        ('extra_reward',    """   'extra_reward':    %s,    """,    'int_list'),
        ('extra_reward_time',    """   'extra_reward_time':    %s,    """,    'str'),
        ('END',               """    },                         """,    'None'),
    ], {}


def peak_arena_shop():
    return [
        ('shop_id',        """    %s:{                       """,    'int'),
        ('shop_icon',    """   'shop_icon':    %s,    """,    'str'),
        ('reward',    """   'reward':    %s,    """,    'int_list'),
        ('need_point',    """   'need_point':    %s,    """,    'int'),
        ('times',    """   'times':    %s,    """,    'int'),
        ('refresh',    """   'refresh':    %s,    """,    'int'),
        ('show_level',    """   'show_level':    %s,    """,    'int_list'),
        ('END',               """    },                         """,    'None'),
    ], {}


def peak_arena_milestone():
    return [
        ('once_ID',        """    %s:{                       """,    'int'),
        ('icon',    """   'icon':    %s,    """,    'str'),
        ('name',    """   'name':    %s,    """,    'unicode'),
        ('team',    """   'team':    %s,    """,    'int'),
        ('story',       """ 'story'      : %s, """, 'unicode'),
        ('open_sort',   """ 'open_sort'  : %s, """, 'int'),
        ('open_data',   """ 'open_data'  : %s, """, 'int'),
        ('reward',      """ 'reward'     : %s, """, 'int_list', check_reward(),),
        ('target_sort', """ 'target_sort': %s, """, 'int'),
        ('target_data', """ 'target_data': %s, """, 'int'),
        ('target_data1', """ 'target_data1': %s, """, 'int'),
        ('finish_open', """ 'finish_open': %s, """, 'int'),
        ('END',               """    },     """,    'None'),
    ], {}


def rocker_machine():
    return [
        ('version',        """    %s:{                       """,    'int'),
        ('start_time',    """   'start_time':    %s,    """,    'str'),
        ('end_time',    """   'end_time':    %s,    """,    'str'),
        ('price_1',    """   'price_1':    %s,    """,    'int'),
        ('price_5',    """   'price_5':    %s,    """,    'int'),
        ('price_10',    """   'price_10':    %s,    """,    'int'),
        ('score_1',    """   'score_1':    %s,    """,    'int'),
        ('score_5',    """   'score_5':    %s,    """,    'int'),
        ('score_10',    """   'score_10':    %s,    """,    'int'),
        ('must_point_num',    """   'must_point_num':    %s,    """,    'int_list'),
        ('must_reward',    """   'must_reward':    %s,    """,    'int_list'),
        ('END',               """    },                         """,    'None'),
    ], {}


def rocker_machine_reward():
    return [
        ('active_id',        """    %s:{                       """,    'int'),
        ('version',    """   'version':    %s,    """,    'int'),
        ('num_id',    """   'num_id':    %s,    """,    'int'),
        ('reward_1',    """   'reward_1':    %s,    """,    'int_list'),
        ('reward_2',    """   'reward_2':    %s,    """,    'int_list'),
        ('reward_3',    """   'reward_3':    %s,    """,    'int_list'),
        ('time_1',    """   'time_1':    %s,    """,    'int'),
        ('time_5',    """   'time_5':    %s,    """,    'int'),
        ('time_10',    """   'time_10':    %s,    """,    'int'),
        ('END',               """    },                         """,    'None'),
    ], {}


def score_reward():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('version',    """   'version':    %s,    """,    'int'),
        ('reward_time',    """   'reward_time':    %s,    """,    'str'),
        ('rank', """   'rank': %s, """, 'int_list', check_int_list_args(2)),
        ('rank_reward', """   'rank_reward': %s, """, 'int_list', check_reward(),),
        ('mail', """   'mail': %s, """, 'unicode'),
        ('END',               """    },                         """,    'None'),
    ], {}


def equip_set_rate():
    return [
        ('rate_id',    "%s: {              ",    'int',),
        ('rate_num',"    'rate_num': %s,    ",    'float',),
        ('END',        "},                 ",    'None')
     ], {}


def god_field_time():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('start_time',    """   'start_time':    %s,    """,    'str'),
        ('refresh_time1',    """   'refresh_time1':    %s,    """,    'str'),
        ('refresh_time2',    """   'refresh_time2':    %s,    """,    'str'),
        ('end_time',    """   'end_time':    %s,    """,    'str'),
        ('close_time',    """   'close_time':    %s,    """,    'str'),
        ('cost',    """   'cost':    %s,    """,    'int'),
        ('END',               """    },                         """,    'None'),
    ], {}


def god_field_fight_time():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('start_time',    """   'start_time':    %s,    """,    'str'),
        ('end_time1',    """   'end_time1':    %s,    """,    'str'),
        ('end_time2',    """   'end_time2':    %s,    """,    'str'),
        ('end_time3',    """   'end_time3':    %s,    """,    'str'),
        ('end_time4',    """   'end_time4':    %s,    """,    'str'),
        ('end_time5',    """   'end_time5':    %s,    """,    'str'),
        ('send_time',    """   'send_time':    %s,    """,    'str'),
        ('close_time',    """   'close_time':    %s,    """,    'str'),
        ('END',               """    },                         """,    'None'),
    ], {}


def god_field_rank_reward():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('des',    """   'des':    %s,    """,    'unicode'),
        ('reward',    """   'reward':    %s,    """,    'int_list'),
        ('mail',    """   'mail':    %s,    """,    'unicode'),
        ('END',               """    },                         """,    'None'),
    ], {}


def god_field_exchange():
    return [
        ('id',   "%s: {              ",   'int',),
        ('reward',       "    'reward': %s,  ",    'int_list',),
        ('des',       "    'des': %s,  ",    'unicode',),
        ('cost1',       "    'cost1': %s,  ",    'int',),
        ('cost2',       "    'cost2': %s,  ",    'int',),
        ('times',       """   'times':          %s,               """,        'int'),
        ('refresh',       """   'refresh':          %s,               """,        'int'),
        ('show_level',       "    'show_level': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}


def god_field_team():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('combat_down',       "    'combat_down': %s,  ",    'int',),
        ('combat_up',       "    'combat_up': %s,  ",    'int',),
        ('combat_int',       "    'combat_int': %s,  ",    'int',),
        ('END',               """    },                         """,    'None'),
    ], {}

def temple_number():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('temple_diff',       "    'temple_diff': %s,  ",    'int',),
        ('temple_battle_need',       "    'temple_battle_need': %s,  ",    'int',),
        ('temple_rate',       "    'temple_rate': %s,  ",    'int_list',),
        ('temple_reward1',       "    'temple_reward1': %s,  ",    'int_list',),
        ('temple_reward2',       "    'temple_reward2': %s,  ",    'int_list',),
        ('temple_reward3',       "    'temple_reward3': %s,  ",    'int_list',),
        ('temple_reward4',       "    'temple_reward4': %s,  ",    'int_list',),
        ('refresh_time',       "    'refresh_time': %s,  ",    'int',),
        ('robot_diff',       "    'robot_diff': %s,  ",    'int_list',),
        ('END',               """    },                         """,    'None'),
    ], {}

def temple_num():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('battle_num',       "    'battle_num': %s,  ",    'float',),
        ('END',               """    },                         """,    'None'),
    ], {}

def temple_robot():
    return [
        ('id',               """ %s: {         """ , 'int'),
        ('name',     """  'name': %s, """,      'unicode'),
        ('temple_reward',         "'temple_reward': %s, "      , 'int'),
        ('formation_type',        "'formation_type': %s,"      , 'int_list'),
        ('role',                  "'role': %s,"                , 'int'),
        ('role_level',            "'role_level': %s,"          , 'int_list'),
        ('character_level',       "'character_level': %s,"     , 'int_list'),
        ('evo_level',             "'evo_level': %s,"           , 'int_list'),
        ('skill_level',           "'skill_level': %s,"         , 'int_list'),
        ('leader_skill_1_key',    "'leader_skill_1_key': %s,"  , 'int'),
        ('leader_skill_1_level',  "'leader_skill_1_level': %s,", 'int'),
        ('leader_skill_2_key',    "'leader_skill_2_key': %s,"  , 'int'),
        ('leader_skill_2_level',  "'leader_skill_2_level': %s,", 'int'),
        ('leader_skill_3_key',    "'leader_skill_3_key': %s,"  , 'int'),
        ('leader_skill_3_level',  "'leader_skill_3_level': %s,", 'int'),
        ('END',                "},", 'None')
    ], {}

def temple_formation():
    return [
        ('typeID',   " %s:{                  ", 'int',),
        ('formation_ID',          "'formation_id': %s,"    , 'int'),
        ('position1',             "'position1': %s,"       , 'int'),
        ('position2',             "'position2': %s,"       , 'int'),
        ('position3',             "'position3': %s,"       , 'int'),
        ('position4',             "'position4': %s,"       , 'int'),
        ('position5',             "'position5': %s,"       , 'int'),
        ('position6',             "'position6': %s,"       , 'int'),
        ('position7',             "'position7': %s,"       , 'int'),
        ('position8',             "'position8': %s,"       , 'int'),
        ('position9',             "'position9': %s,"       , 'int'),
        ('position10',             "'position10': %s,"       , 'int'),
        ('position11',             "'position11': %s,"       , 'int'),
        ('position12',             "'position12': %s,"       , 'int'),
        ('position13',             "'position13': %s,"       , 'int'),
        ('position14',             "'position14': %s,"       , 'int'),
        ('position15',             "'position15': %s,"       , 'int'),
        ('position16',             "'position16': %s,"       , 'int'),
        ('position17',             "'position17': %s,"       , 'int'),
        ('position18',             "'position18': %s,"       , 'int'),
        ('position19',             "'position19': %s,"       , 'int'),
        ('position20',             "'position20': %s,"       , 'int'),
        ('position21',             "'position21': %s,"       , 'int'),
        ('position22',             "'position22': %s,"       , 'int'),
        ('position23',             "'position23': %s,"       , 'int'),
        ('position24',             "'position24': %s,"       , 'int'),
        ('END',                "},", 'None')
    ], {}




def pet_refresh():
    return [
        ('id',         "%s: {               ",    'int',),
        ('value_add', """      'value_add'             : %s, """, 'int_list'),
        ('refresh_dirt', """      'refresh_dirt'            : %s, """, 'int_list'),
        ('refresh_range', """      'refresh_range'        : %s, """, 'int_list'),
        ('refresh_cost', """      'refresh_cost'        : %s, """, 'int'),
        ('END',        "},                  ",    'None')
    ], {}


def clone_lane():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',       "    'start_time': %s,  ",    'str',),
        ('end_time',       "    'end_time': %s,  ",    'str',),
        ('secret_reward',       "    'secret_reward': %s,  ",    'int_list',),
        ('reward_1',       "    'reward_1': %s,  ",    'int_list',),
        ('reward_1_show',       "    'reward_1_show': %s,  ",    'int_list',),
        ('reward_2',       "    'reward_2': %s,  ",    'int_list',),
        ('reward_2_show',       "    'reward_2_show': %s,  ",    'int_list',),
        ('reward_3',       "    'reward_3': %s,  ",    'int_list',),
        ('reward_3_show',       "    'reward_3_show': %s,  ",    'int_list',),
        ('reward_4',       "    'reward_4': %s,  ",    'int_list',),
        ('reward_4_show',       "    'reward_4_show': %s,  ",    'int_list',),
        ('reward_5',       "    'reward_5': %s,  ",    'int_list',),
        ('score',       "    'score': %s,  ",    'int_list',),
        ('score_max',"    'score_max': %s,    ",    'int',),
        ('price',"    'price': %s,    ",    'int_list',),
        ('price_all',"    'price_all': %s,    ",    'int_list',),
        ('cost',"    'cost': %s,    ",    'int_list',),
        ('notice',"    'notice': %s,    ",    'unicode',),
        ('des',"    'des': %s,    ",    'unicode',),
        ('des_1',"    'des_1': %s,    ",    'unicode',),
        ('secret_reward_point',"    'secret_reward_point': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def afterlife():
    return [
        ('life_id',    "%s: {              ",    'int',),
        ('afterlife_id',       "    'afterlife_id': %s,  ",    'int',),
        ('limit_evo',       "    'limit_evo': %s,  ",    'int',),
        ('afterlife_material',       "    'afterlife_material': %s,  ",    'int_list',),
        ('afterlife_point',       "    'afterlife_point': %s,  ",    'int',),
        ('active_chapterID',       "    'active_chapterID': %s,  ",    'str',),
        ('building',       "    'building': %s,  ",    'int',),
        ('des1',       "    'des1': %s,  ",    'unicode',),
        ('des2',       "    'des2': %s,  ",    'unicode',),
        ('des3',       "    'des3': %s,  ",    'unicode',),
        ('drama_id',       "    'drama_id': %s,  ",    'int',),
        ('mission1',       "    'mission1': %s,  ",    'unicode',),
        ('mission2',       "    'mission2': %s,  ",    'unicode',),
        ('mission3',       "    'mission3': %s,  ",    'unicode',),
        ('END',        "},                 ",    'None')
    ], {}


def afterlife_chapter():
    return [
        ('active_chapterID',   "%s:{                  ", 'str',),
        ('ccb_resouce',        "'ccb_resouce': %s,"    , 'str'),
        ('fight_ID',      "'fight_ID': %s,"  , 'int'),
        ('open',               "'open': %s,"           , 'int_list'),
        ('time_sort',          "'time_sort': %s,"      , 'int'),
        ('level',               "'level': %s,"           , 'int_list'),
        ('minus_sort', "'minus_sort': %s,"     , 'int'),
        ('times',              "'times': %s,"          , 'int'),
        ('vip_buy',            "'vip_buy': %s,"        , 'int_list'),
        ('button',            "'button': %s,"          , 'str'),
        ('banner',            "'banner': %s,"          , 'str'),
        ('open_time_word',    "'open_time_word': %s,"      , 'unicode'),
        ('des',            "'des': %s,"      , 'unicode'),
        ('is_see',            "'is_see': %s,"      , 'int'),
        ('reward_show',       "'reward_show': %s," , 'int_list'),
        ('loot',              "'loot': %s,       " , 'int'),
        ('exp_role',          "'exp_role': %s,   " , 'int'),
        ('exp_character',     "'exp_character': %s," , 'int'),
        ('action_point',      "'action_point': %s," , 'int'),
        ('own',               "'own': %s," ,          'str'),
        ('sort',               "'sort': %s," ,          'int'),
        ('END',                "},", 'None')
    ], {}


def afterlife_fight():
    t = [
        ('fight_ID',             """'%s': {                      """ , 'int'),
        ('fight_boss',           """    'fight_boss'  : %s,          """ , 'str'),
        ('formation_id',         """    'formation_id'  : %s,        """ , 'int'),
        ('position1',            """    'position1'  : %s,           """ , 'int_list'),
        ('position2',            """    'position2'  : %s,           """ , 'int_list'),
        ('position3',            """    'position3'  : %s,           """ , 'int_list'),
        ('position4',            """    'position4'  : %s,           """ , 'int_list'),
        ('position5',            """    'position5'  : %s,           """ , 'int_list'),
        ('alternate1',           """    'alternate1' : %s,           """ , 'int_list'),
        ('alternate2',           """    'alternate2' : %s,           """ , 'int_list'),
        ('alternate3',           """    'alternate3' : %s,           """ , 'int_list'),
        ('alternate4',           """    'alternate4' : %s,           """ , 'int_list'),
        ('alternate5',           """    'alternate5' : %s,           """ , 'int_list'),
        ('team_rage',            """    'team_rage ' : %s,           """ , 'int'),
        ('enemy_rage',           """    'enemy_rage' : %s,           """ , 'int'),
        ('reward_exp_role',      """    'reward_exp_role'      : %s, """ , 'int'),
        ('reward_exp_character', """    'reward_exp_character' : %s, """ , 'int'),
        ('END',                  """},                               """ , 'None'),
    ]
    return t, {}


def afterlife_enemy():
    return [
        ('enemy_ID',       """%s: {                   """ , 'str'),
        ('enemy_name',     """ 'enemy_name'     : %s, """ , 'unicode'),
        ('rgb_sort',       """ 'rgb_sort'          : %s, """, 'int'),
        ('img',            """ 'img'            : %s, """ , 'str'),
        ('animation',      """ 'animation'      : %s, """ , 'str'),
        ('is_boss',        """ 'is_boss'        : %s, """ , 'int'),
        ('race',           """ 'race'           : %s, """ , 'int'),
        ('career',         """ 'career'         : %s, """ , 'int'),
        ('patk',           """ 'patk'           : %s, """ , 'int'),
        ('matk',           """ 'matk'           : %s, """ , 'int'),
        ('def',            """ 'def'            : %s, """ , 'int'),
        ('speed',          """ 'speed'          : %s, """ , 'int'),
        ('hp',             """ 'hp'             : %s, """ , 'int'),
        ('lv',             """ 'lv'             : %s, """ , 'int'),
        ('skill1',         """ 'skill1'         : %s, """ , 'int_list'),
        ('skill2',         """ 'skill2'         : %s, """ , 'int_list'),
        ('skill3',         """ 'skill3'         : %s, """ , 'int_list'),
        ('loot_charactar', """ 'loot_character' : %s, """ , 'int_list'),
        ('loot_item',      """ 'loot_item'      : %s, """ , 'int_list'),
        ('loot_non',       """ 'loot_non'       : [-1, %s], """ , 'int'),
        ('hr',             """ 'hr'             : %s, """ , 'int'),
        ('dr',             """ 'dr'             : %s, """ , 'int'),
        ('subhurt',             """ 'subhurt'             : %s, """ , 'int'),
        ('crit',             """ 'crit'             : %s, """ , 'int'),
        ('fire',           """ 'fire'           : %s, """ , 'int'),
        ('water',          """ 'water'          : %s, """ , 'int'),
        ('wind',           """ 'wind'           : %s, """ , 'int'),
        ('earth',          """ 'earth'          : %s, """ , 'int'),
        ('fire_dfs',       """ 'fire_dfs'       : %s, """ , 'int'),
        ('water_dfs',      """ 'water_dfs'      : %s, """ , 'int'),
        ('wind_dfs',       """ 'wind_dfs'       : %s, """ , 'int'),
        ('earth_dfs',      """ 'earth_dfs'      : %s, """ , 'int'),
        ('END',            """},                     """ , 'None'),
    ], {}


def new_vip_reward():
    return [
        ('vip',    "%s: {              ",    'int',),
        ('day1',"    'day1': %s,    ",    'int_list',),
        ('day2',"    'day2': %s,    ",    'int_list',),
        ('day3',"    'day3': %s,    ",    'int_list',),
        ('day4',"    'day4': %s,    ",    'int_list',),
        ('day5',"    'day5': %s,    ",    'int_list',),
        ('day6',"    'day6': %s,    ",    'int_list',),
        ('day7',"    'day7': %s,    ",    'int_list',),
        ('everyday',"    'everyday': %s,    ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def red_bag():
    return [
        ('id',    "%s: {              ",    'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('coin_rate',       "    'coin_rate': %s,  ",    'int_list',),
        ('start_rate',       "    'start_rate': %s,  ",    'int',),
        ('end_rate',       "    'end_rate': %s,  ",    'int',),
        ('start_num',       "    'start_num': %s,  ",    'int',),
        ('end_num',       "    'end_num': %s,  ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def system_red_bag():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',       "    'start_time': %s,  ",    'str',),
        ('end_time',       "    'end_time': %s,  ",    'str',),
        ('reward_time',       "    'reward_time': %s,  ",    'int_list',),
        ('coin_num',       "    'coin_num': %s,  ",    'int',),
        ('bag_num',       "    'bag_num': %s,  ",    'int',),
        ('code_coin',       "    'code_coin': %s,  ",    'int',),
        ('background',       "    'background': %s,  ",    'str',),
        ('des1',       "    'des1': %s,  ",    'unicode',),
        ('des2',       "    'des2': %s,  ",    'unicode',),
        ('des3',       "    'des3': %s,  ",    'unicode',),
        ('des4',       "    'des4': %s,  ",    'unicode',),
        ('code_list',       "    'code_list': %s,  ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def gringotts():
    return [
        ('version',    "%s: {              ",    'int',),
        ('start_time',       "    'start_time': %s,  ",    'str',),
        ('end_time',       "    'end_time': %s,  ",    'str',),
        ('charge_reward',       "    'charge_reward': %s,  ",    'int_list',),
        ('max_coin',       "    'max_coin': %s,  ",    'int',),
        ('time1',       "    'time1': %s,  ",    'int',),
        ('time2',       "    'time2': %s,  ",    'int',),
        ('time3',       "    'time3': %s,  ",    'int',),
        ('coin_point1',       "    'coin_point1': %s,  ",    'int_list',),
        ('coin_point2',       "    'coin_point2': %s,  ",    'int_list',),
        ('coin_point3',       "    'coin_point3': %s,  ",    'int_list',),
        ('quickly_point',       "    'quickly_point': %s,  ",    'int',),
        ('des1',       "    'des1': %s,  ",    'unicode',),
        ('refresh_coin',       "    'refresh_coin': %s,  ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def gringotts_rate():
    return [
        ('active_id',    "%s: {              ",    'int',),
        ('version',       "    'version': %s,  ",    'int',),
        ('id',       "    'id': %s,  ",    'int',),
        ('limit',       "    'limit': %s,  ",    'int',),
        ('coin_down',       "    'coin_down': %s,  ",    'int_list',),
        ('refresh_rate_down',       "    'refresh_rate_down': %s,  ",    'int_list',),
        ('coin_up',       "    'coin_up': %s,  ",    'int_list',),
        ('refresh_rate_up',       "    'refresh_rate_up': %s,  ",    'int_list',),
        ('END',        "},                 ",    'None')
    ], {}


def gringotts_VIP():
    return [
        ('VIP_id',    "%s: {              ",    'int',),
        ('free_times',       "    'free_times': %s,  ",    'int',),
        ('charge_coin',       "    'charge_coin': %s,  ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def new_rocker():
    return [
        ('id',        """    %s:{                       """,    'int'),
        ('version',    """   'version':    %s,    """,    'int'),
        ('rate',    """   'rate':    %s,    """,    'int'),
        ('times',    """   'times':    %s,    """,    'int'),
        ('END',        "},                 ",    'None')
    ], {}


def new_rocker_reward():
    return [
        ('version',        """    %s:{                       """,    'int'),
        ('start_time',    """   'start_time':    %s,    """,    'str'),
        ('end_time',    """   'end_time':    %s,    """,    'str'),
        ('theme_reward1',    """   'theme_reward1':    %s,    """,    'int_list'),
        ('theme_reward2',    """   'theme_reward2':    %s,    """,    'int_list'),
        ('theme_reward3',    """   'theme_reward3':    %s,    """,    'int_list'),
        ('price_1',    """   'price_1':    %s,    """,    'int'),
        ('price_2',    """   'price_2':    %s,    """,    'int'),
        ('price_3',    """   'price_3':    %s,    """,    'int'),
        ('score_max',    """   'score_max':    %s,    """,    'int'),
        ('score',    """   'score':    %s,    """,    'int_list'),
        ('score_false_probability',    """   'score_false_probability':    %s,    """,    'float'),
        ('score_probability',    """   'score_probability':    %s,    """,    'float'),
        ('notice',    """   'notice':    %s,    """,    'unicode'),
        ('des1',    """   'des1':    %s,    """,    'unicode'),
        ('des2',    """   'des2':    %s,    """,    'unicode'),
        ('END',        "},                 ",    'None')
    ], {}


def server_pk_world():
    return [
        ('server',    "%s: {              ",    'str',),
        ('world_id',"    'world_id': %s,    ",    'int',),
        ('END',        "},                 ",    'None')
    ], {}


def server_pk_time():
    return [
        ('id',   "%s: {              ",   'int',),
        ('time_sort',       "    'time_sort': %s,  ",    'int_list',),
        ('select_open_time',       "    'select_open_time': %s,  ",    'str',),
        ('select_player',       "    'select_player': %s,  ",    'str',),
        ('select_close_time',       "    'select_close_time': %s,  ",    'str',),
        ('ready_time',       "    'ready_time': %s,  ",    'str',),
        ('open_time',       "    'open_time': %s,  ",    'str',),
        ('pk_close_time',       "    'pk_close_time': %s,  ",    'str',),
        ('close_time',       "    'close_time': %s,  ",    'str',),
        ('reward_time',       "    'reward_time': %s,  ",    'str',),
        ('boss_id',       "    'boss_id': %s,  ",    'int',),
        ('boss_id1',       "    'boss_id1': %s,  ",    'int',),
        ('boss_hp',       "    'boss_hp': %s,  ",    'int',),
        ('END',        "},               ", 'None')
    ], {}


def server_pk_reward():
    return [
        ('id',   "%s: {              ",   'int',),
        ('sort',       "    'sort': %s,  ",    'int',),
        ('reward_member',       "    'reward_member': %s,  ",    'int_list',),
        ('reward_member_score',       "    'reward_member_score': %s,  ",    'int',),
        ('mail_member',       "    'mail_member': %s,  ",    'unicode',),
        ('END',        "},               ", 'None')
    ], {}


def server_pk_exchange():
    return [
        ('id',   "%s: {              ",   'int',),
        ('reward',       "    'reward': %s,  ",    'int_list',),
        ('des',       "    'des': %s,  ",    'unicode',),
        ('cost',       "    'cost': %s,  ",    'int',),
        ('times',       """   'times':          %s,               """,        'int'),
        ('refresh',       """   'refresh':          %s,               """,        'int'),
        ('limits',       "    'limits': %s,  ",    'int_list',),
        ('END',        "},               ", 'None')
    ], {}


def version_reward():
    return [
        ('id', """%s: {""", 'int'),
        ('version_name',         """ 'version_name'        : %s, """, 'str'),
        ('gift',      """ 'gift'     : %s, """, 'int_list', check_reward(),),
        ('old_version_notice',   """ 'old_version_notice'  : %s, """, 'unicode'),
        ('new_version_notice',   """ 'new_version_notice'  : %s, """, 'unicode'),
        ('END', """},""", 'None'),
    ], {}


def role_attri_add():
    return [
        ('id', """%s: {""", 'int'),
        ('skill_add',       "    'skill_add': %s,  ",    'int_list',),
        ('skill_add_level',       "    'skill_add_level': %s,  ",    'int_list',),
        ('cost_coin',       "    'cost_coin': %s,  ",    'int',),
        ('need_level',       "    'need_level': %s,  ",    'int',),
        ('fight_level',       "    'fight_level': %s,  ",    'int',),
        ('END', """},""", 'None'),
    ], {}

def godfield_arena_reward():
    return [('stage_id',          """%s: {""",    'int'),
            ('stage_reward',     """ 'stage_reward'        : %s, """ , 'int_list'),
            ('player_num',  """ 'player_num': %s, """, 'int'),
            ('daily_reward',  """ 'daily_reward': %s, """, 'int_list'),
            ('fight_reward',  """ 'fight_reward': %s, """, 'int_list'),
            ('refresh_times',  """ 'refresh_times': %s, """, 'int'),
            ('refresh_coins',  """ 'refresh_coins': %s, """, 'int'),
            ('END', """},                   """, 'None'),
    ], {}


def godfield_arena():
    return [('id',          """%s: {""",    'int'),
            ('stage_id',  """ 'stage_id': %s, """, 'int'),
            ('start_level',    """ 'start_level': %s, """, 'int'),
            ('end_level',   """ 'end_level': %s, """, 'int'),
            ('start_rank',  """ 'start_rank': %s, """, 'int'),
            ('end_rank',  """ 'end_rank': %s, """, 'int'),
            ('per_point',   """ 'per_point': %s, """, 'int'),
            ('per_food',  """ 'per_food': %s, """, 'int'),
            ('per_metal',  """ 'per_metal': %s, """, 'int'),
            ('per_energy',      """ 'per_energy': %s, """, 'int'),
            ('END', """},                   """, 'None'),
    ], {}


# 新竞技场分为若干个阶段，每个阶段的机器人战斗力不同, 相比robot方法增加了stage_id，用来判断机器人属于哪个阶段
def godfield_arena_robot():
    """# robot: docstring
    args:
        :    ---    arg
    returns:
        0    ---
    """
    return [
        ('user_id',               """'robot_%s': {         """ , 'int'),
        ('top',                   "'top': %s,"                 , 'int_list'),
        ('formation_type',        "'formation_type': %s,"      , 'int_list'),
        ('role',                  "'role': %s,"                , 'int'),
        ('role_level',            "'role_level': %s,"          , 'int_list'),
        ('character_level',       "'character_level': %s,"     , 'int_list'),
        ('evo_level',             "'evo_level': %s,"           , 'int_list'),
        ('skill_level',           "'skill_level': %s,"         , 'int_list'),
        ('leader_skill_1_key',    "'leader_skill_1_key': %s,"  , 'int'),
        ('leader_skill_1_level',  "'leader_skill_1_level': %s,", 'int'),
        ('leader_skill_2_key',    "'leader_skill_2_key': %s,"  , 'int'),
        ('leader_skill_2_level',  "'leader_skill_2_level': %s,", 'int'),
        ('leader_skill_3_key',    "'leader_skill_3_key': %s,"  , 'int'),
        ('leader_skill_3_level',  "'leader_skill_3_level': %s,", 'int'),
        ('stage_id',                  "'stage_id': %s,"                , 'int'),
        ('END',                "},", 'None')
    ], {}

# 神域竞技场商店
godfield_arena_shop = arena_shop

def godfield_formation():
    return [
        ('typeID',   "%s:{                  ", 'int',),
        ('formation_ID',          "'formation_id': %s,"    , 'int'),
        ('position1',             "'position1': %s,"       , 'int'),
        ('position2',             "'position2': %s,"       , 'int'),
        ('position3',             "'position3': %s,"       , 'int'),
        ('position4',             "'position4': %s,"       , 'int'),
        ('position5',             "'position5': %s,"       , 'int'),
        ('position6',             "'position6': %s,"       , 'int'),
        ('position7',             "'position7': %s,"       , 'int'),
        ('position8',             "'position8': %s,"       , 'int'),
        ('position9',             "'position9': %s,"       , 'int'),
        ('position10',            "'position10': %s,"      , 'int'),
        ('position11',            "'position11': %s,"      , 'int'),
        ('position12',            "'position12': %s,"      , 'int'),
        ('position13',            "'position13': %s,"      , 'int'),
        ('position14',            "'position14': %s,"      , 'int'),
        ('position15',            "'position15': %s,"      , 'int'),
        ('position16',            "'position16': %s,"      , 'int'),
        ('position17',            "'position17': %s,"      , 'int'),
        ('position18',            "'position18': %s,"      , 'int'),
        ('position19',            "'position19': %s,"      , 'int'),
        ('position20',            "'position20': %s,"      , 'int'),
        ('position21',            "'position21': %s,"      , 'int'),
        ('position22',            "'position22': %s,"      , 'int'),
        ('position23',            "'position23': %s,"      , 'int'),
        ('position24',            "'position24': %s,"      , 'int'),
        ('END',                "},", 'None')
    ], {}


def new_fight_forever():
    return [
        ('active_chapterID',               "%s: {         " , 'int'),
        ('fight_ID',          "'fight_ID': %s,"                 , 'int'),
        ('reward_show',       "'reward_show': %s,"      , 'int_list'),
        ('reward_first',      "'reward_first': %s,"                , 'int_list'),
        ('target_sort',       "'target_sort': %s,"          , 'int'),
        ('target_data',       "'target_data': %s,"     , 'int'),
        ('target_des',        "'target_des': %s,"           , 'unicode'),
        ('need_star',         "'need_star': %s,"         , 'int'),
        ('reset_num',         "'reset_num': %s,"         , 'int'),
        ('END',                "},", 'None')
    ], {}

def new_fight_fight():
    return [
        ('fight_ID',               "%s: {         " , 'int'),
        ('formation_id',          "'formation_id': %s,"                 , 'int'),
        ('position1',             "'position1': %s,"       , 'int'),
        ('position2',             "'position2': %s,"       , 'int'),
        ('position3',             "'position3': %s,"       , 'int'),
        ('position4',             "'position4': %s,"       , 'int'),
        ('position5',             "'position5': %s,"       , 'int'),
        ('position6',             "'position6': %s,"       , 'int'),
        ('position7',             "'position7': %s,"       , 'int'),
        ('position8',             "'position8': %s,"       , 'int'),
        ('position9',             "'position9': %s,"       , 'int'),
        ('position10',            "'position10': %s,"      , 'int'),
        ('position11',            "'position11': %s,"      , 'int'),
        ('position12',            "'position12': %s,"      , 'int'),
        ('position13',            "'position13': %s,"      , 'int'),
        ('position14',            "'position14': %s,"      , 'int'),
        ('position15',            "'position15': %s,"      , 'int'),
        ('reward_exp_role',       "'reward_exp_role': %s,"      , 'int'),
        ('reward_exp_character',  "'reward_exp_character': %s,"      , 'int'),
        ('END',                "},", 'None')
    ], {}


def new_fight_enemy():
    return [
        ('enemy_ID',       """%s: {                   """ , 'str'),
        ('enemy_name',     """ 'enemy_name'     : %s, """ , 'unicode'),
        ('c_id',     """ 'c_id'     : %s, """ , 'int'),
        ('rgb_sort',       """ 'rgb_sort'          : %s, """, 'int'),
        ('img',            """ 'img'            : %s, """ , 'str'),
        ('animation',      """ 'animation'      : %s, """ , 'str'),
        ('is_boss',        """ 'is_boss'        : %s, """ , 'int'),
        ('race',           """ 'race'           : %s, """ , 'int'),
        ('career',         """ 'career'         : %s, """ , 'int'),
        ('patk',           """ 'patk'           : %s, """ , 'int'),
        ('matk',           """ 'matk'           : %s, """ , 'int'),
        ('def',            """ 'def'            : %s, """ , 'int'),
        ('speed',          """ 'speed'          : %s, """ , 'int'),
        ('hp',             """ 'hp'             : %s, """ , 'int'),
        ('lv',             """ 'lv'             : %s, """ , 'int'),
        ('level_max',             """ 'level_max'             : %s, """ , 'int'),
        ('step',             """ 'step'             : %s, """ , 'int'),
        ('exp',             """ 'exp'             : %s, """ , 'int'),
        ('battle_point',   """ 'battle_point'        : %s, """ , 'int'),
        ('quality',        """ 'quality'             : %s, """ , 'int'),
        ('skill1',         """ 'skill1'         : %s, """ , 'int_list'),
        ('skill2',         """ 'skill2'         : %s, """ , 'int_list'),
        ('skill3',         """ 'skill3'         : %s, """ , 'int_list'),
        ('loot_charactar', """ 'loot_character' : %s, """ , 'int_list'),
        ('loot_item',      """ 'loot_item'      : %s, """ , 'int_list'),
        ('loot_non',       """ 'loot_non'       : [-1, %s], """ , 'int'),
        ('hr',             """ 'hr'             : %s, """ , 'int'),
        ('dr',             """ 'dr'             : %s, """ , 'int'),
        ('subhurt',             """ 'subhurt'             : %s, """ , 'int'),
        ('crit',             """ 'crit'             : %s, """ , 'int'),
        ('fire',           """ 'fire'           : %s, """ , 'int'),
        ('water',          """ 'water'          : %s, """ , 'int'),
        ('wind',           """ 'wind'           : %s, """ , 'int'),
        ('earth',          """ 'earth'          : %s, """ , 'int'),
        ('fire_dfs',       """ 'fire_dfs'       : %s, """ , 'int'),
        ('water_dfs',      """ 'water_dfs'      : %s, """ , 'int'),
        ('wind_dfs',       """ 'wind_dfs'       : %s, """ , 'int'),
        ('earth_dfs',      """ 'earth_dfs'      : %s, """ , 'int'),
        ('END',            """},                     """ , 'None'),
    ], {}