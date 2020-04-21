#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import copy

SORT        = u'SORT       : 第%d回合'
ATTACK      = u'ATTACK     : 位置%(src)-3s<%(src_name)s> 发动 普通攻击, 位置%(des)s<%(des_name)s> 受到伤害(%(hurt)s)'
SKILL       = u'SKILL      : 位置%(src)-3s<%(src_name)s> 发动 技能(%(name)2s), 位置%(des)s<%(des_name)s> 受到伤害(%(hurt)s)'
SKILL_HP    = u'SKILL      : 位置%(src)-3s<%(src_name)s> 发动 技能(%(name)2s), 位置%(desh)s<%(desh_name)s> 恢复血量(%(health)s)'
SKILL_MIX   = u'SKILL      : 位置%(src)-3s<%(src_name)s> 发动 技能(%(name)2s), 位置%(desh)s<%(desh_name)s> 恢复血量(%(health)s), 位置%(des)s<%(des_name)s> 受到伤害(%(hurt)s)'
DEATH       = u'DEATH      : 位置%(src)-3s<%(src_name)s> 死亡'
SBT         = u'SBT        : 位置(%s) 替补上场'
NEXT        = u'next       : 位置%(src)-3s<%(src_name)s>'
REMOVE_BUFF = u'REMOVE_BUFF: 位置%(src)-3s<%(src_name)s> 移除 技能BUFF(%(name)2s)'
ADD_BUFF    = u'ADD_BUFF   : 位置%(src)-3s<%(src_name)s> 添加 技能BUFF(%(name)2s)'
WINER       = u'WINER      : 位置%(src)-3s<%(src_name)s> 胜利'
BUFF_SKILL  = u'BUFF_SKILL : 位置%(src)-3s<%(src_name)s>的技能BUFF(%(name)2s), 位置%(des)-3s<%(des_name)s> 受到伤害(%(hurt)s)'
BUFF_SKILL_HP = u'BUFF_SKILL : 位置%(src)-3s<%(src_name)s>的技能BUFF(%(name)2s), 位置%(desh)-3s<%(des_name)s> 恢复血量(%(health)s)'
SKILL_HERO  = u'SKILL_HERO : skill_hero'
DRAMA       = u'DRAMA      : drama'


class ParseBattle(object):

    def __init__(self, battle_result, game_config):
        self.process = []
        self.rounds = 0
        self.game_config = game_config
        self.battle_result = battle_result
        self.atk_team = battle_result['init']['atk']
        self.def_team = battle_result['init']['dfd']

    def parse(self):
        '''
        解析战斗过程
        :return:
        '''
        for i, data in sorted(self.battle_result['battle'].iteritems(), key=lambda x: int(x[0])):
            flag, param = data['flag'], data['param']
            func = getattr(self, 'parse_%s' % flag, None)
            if callable(func):
                temp = func(param)
            else:
                temp = '%s --- %s' % (flag, param)
            self.process.append(temp)

    def get_name(self, card_id):
        '''
        获取卡牌的名称
        :param card_id:
        :return:
        '''
        if card_id in self.game_config.character_detail:
            name = self.game_config.character_detail[card_id]['name']
        else:
            name = card_id
        return '%s(%s)' % (name, card_id)

    def get_obj(self, posid):
        '''
        获取一个位置的卡牌对象数据
        :param posid: 位置
        :return:
        '''
        if posid >= 100:
            obj = self.def_team[posid - 100]
        else:
            obj = self.atk_team[posid]

        if not isinstance(obj, dict):
            return {'card_id': obj}
        return obj

    def parse_sort(self, param):
        '''
        解析回合数
        :param param:
        :return:
        '''
        self.rounds += 1
        return SORT % self.rounds

    def parse_attack(self, param):
        '''
        解析攻击
        :param param:
        :return:
        '''
        src, des = param['src'], param['dec']   # 攻击|防守
        src_obj = self.get_obj(src)
        des_obj = self.get_obj(des)
        param.update(src_name=self.get_name(src_obj['card_id']),
                     des_name=self.get_name(des_obj['card_id']))
        return ATTACK % param

    def parse_skill(self, param):
        '''
        解析技能
        :param param:
        :return:
        '''
        # {'src': 0, 'name': 'andy_copter', 'des': [100, 101, 102], 'hurt': {100: 63998, 101: 0, 102: 31999}, 'desh': 0,
        #  'health': 9599, 'skillid': 430}
        # {'skillid': 910, 'name': 'ace_s1', 'src': selfPositionId, 'des': tempDid, 'hurt': tempHurt}
        # {'skillid': 920, 'name': 'ace_s2', 'src': selfPositionId, 'desh': -1}
        # {'skillid': 430, 'name': 'andy_copter', 'src': selfPositionId, 'des': enemylist, 'hurt': hurtlist,
        #  'desh': selfPositionId, 'health': health}
        # {'name': 'buff_mgc'}
        if 'desh' in param and 'des' not in param:
            # 只是回血的
            desh = param['desh']
            health = param.setdefault('health', 0)
            src_id = self.get_obj(param['src'])['card_id']

            if not isinstance(desh, list):
                desh = [desh]
                health = [health]

            desh_names = '%s' * len(desh)
            desh_name = []
            for d in desh:
                desh_obj = self.get_obj(d)
                desh_name.append(self.get_name(desh_obj['card_id']))

            param.update(desh=desh, health=health,
                         src_name=self.get_name(src_id),
                         desh_name=desh_names % tuple(desh_name))

            return SKILL_HP % param

        if 'desh' not in param and 'des' in param:
            # 只是伤害的
            src, des, hurt = param['src'], param['des'], param.setdefault('hurt', 0)
            src_obj = self.get_obj(src)

            if not isinstance(des, list):
                des, hurt = [des], [hurt]

            des_names = '%s' % len(des)
            des_name = []
            for i, d in enumerate(des):
                des_obj = self.get_obj(d)
                des_name.append(self.get_name(des_obj['card_id']))

            param.update(src_name=self.get_name(src_obj['card_id']), des_name=des_names % tuple(des_name))

            return SKILL % param

        if 'desh' in param and 'des' in param:
            # 有回血，也有伤害的
            desh, health = param['desh'], param.setdefault('health', 0)
            des, hurt = param['des'], param.setdefault('hurt', 0)
            src_id = self.get_obj(param['src'])['card_id']

            if not isinstance(desh, list):
                desh = [desh]
                health = [health]

            desh_names = '%s' * len(desh)
            desh_name = []
            for d in desh:
                desh_obj = self.get_obj(d)
                desh_name.append(self.get_name(desh_obj['card_id']))

            param.update(desh=desh, health=health, desh_name=desh_names % tuple(desh_name))

            if not isinstance(des, list):
                des, hurt = [des], [hurt]

            des_names = '%s' * len(des)
            des_name = []
            for i, d in enumerate(des):
                des_obj = self.get_obj(d)
                des_name.append(self.get_name(des_obj['card_id']))

            # desh_name=self.get_name(desh_obj['card_id'])
            param.update(src_name=self.get_name(src_id), des_name=des_names % tuple(des_name))

            return SKILL_MIX % param

        return 'SKILL   : %s' % param

    def parse_death(self, param):
        '''
        解析死亡
        :param param:
        :return:
        '''
        src_name = self.get_obj(param)['card_id']
        param = dict(src_name=self.get_name(src_name), src=param)
        return DEATH % param

    def parse_sbt(self, param):
        '''
        解析xxx上场
        :param param:
        :return:
        '''
        return SBT % param

    def parse_next(self, param):
        '''
        下一个卡牌
        :param param:
        :return:
        '''
        # {"src": tempPositionid}
        card_id = self.get_obj(param['src'])['card_id']
        param.update(src_name=self.get_name(card_id))
        return NEXT % param

    def parse_remove_buff(self, param):
        '''
        xxx位置哪张卡牌 移除buff
        :param param:
        :return:
        '''
        # {u'src': 100, u'name': u''}
        card_id = self.get_obj(param['src'])['card_id']
        param.update(src_name=self.get_name(card_id))
        return REMOVE_BUFF % param

    def parse_add_buff(self, param):
        '''
        添加buff {u'msg': {}, u'src': 103, u'name': u'buff_luffy'}
        :param param:
        :return:
        '''
        card_id = self.get_obj(param['src'])['card_id']
        param.update(src_name=self.get_name(card_id))
        return ADD_BUFF % param

    def parse_winer(self, param):
        '''
        解析哪个位置的卡牌胜利
        :param param:
        :return:
        '''
        card_id = self.get_obj(param)['card_id']
        param = dict(src_name=self.get_name(card_id), src=param)
        return WINER % param

    def parse_buff_skill(self, param):
        '''
        解析技能buff
        :param param:
        :return:
        '''
        # {u'src': 100, u'health': 241340.45, u'desh': 100, u'name': u'buff_tempHp_skill'}
        # {'name': 'buff_fire', 'src': positionid, 'des': positionid, 'hurt': tempHurt}
        # {u'src': 100, u'desh': 100, u'name': u'buff_tempHp_skill'}
        if 'desh' in param:
            param.setdefault('health', 0)                       # 治疗
            src_id = self.get_obj(param['src'])['card_id']
            des_id = self.get_obj(param['desh'])['card_id']
            text = BUFF_SKILL_HP
        else:
            param.setdefault('hurt', 0)                         # 伤害
            src_id = self.get_obj(param['src'])['card_id']
            des_id = self.get_obj(param['des'])['card_id']
            text = BUFF_SKILL

        param.update(src_name=self.get_name(src_id), des_name=self.get_name(des_id))

        return text % param


def parse_battle_result(battle_result, game_config):
    '''
    解析战斗结果
    :param battle_result:
    :param game_config:
    :return:
    '''
    battle_result = copy.deepcopy(battle_result)
    battle = ParseBattle(battle_result, game_config)
    battle.parse()
    return battle.process