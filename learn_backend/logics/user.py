#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import datetime
import weakref
import itertools
import traceback

from lib import utils
from lib.utils.debug import print_log_maker
from lib.utils.debug import print_log as debug_print
import settings
import game_config
from models.user import User as UserM
from models.user import UidServer
from models.payment import Payment
from models import fake
from logics import notice
from logics import guide
from logics.gift import add_gift
from models.open_door import OpenDoorRank
from lib.utils import round_float_or_str, generate_rank_score
from lib.utils import get_local_ip


class User(object):
    """# User: 用户类，现在当作所有model的数据容器"""
    @classmethod
    def print_log(cls, *args, **kwargs):
        print_log_maker(2)(*args, **kwargs)

    def __init__(self, uid, user_m_obj=None):
        self.uid = uid
        if user_m_obj is not None:
            self.user_m = user_m_obj
        else:
            self.user_m = UserM.get(uid)
        self._server_name = self.user_m._server_name
        self.user_m.update_action_point()
        self.add_countdown = self.user_m.add_countdown              # 倒计时 结束时间点endtime: func函数
        self.method = None
        self.level_change = []      # 等级变化，(1, 2)表示从1级升到2级
        self.ACTION_POINT_UPDATE_RATE = self.user_m.ACTION_POINT_UPDATE_RATE
        self.HAS_LEADER = self.user_m.HAS_LEADER
        self.world_id = game_config.new_world.get(self._server_name, {}).get('world_id', '')
        self.father_server_name = settings.get_father_server(self._server_name)
        # self.config_type = settings.SERVERS.get(self._server_name, {}).get('config_type', 1)
        self.config_type = settings.get_config_type(self.father_server_name)

        super(User, self).__init__()

    @classmethod
    def get(cls, uid, server_name=''):
        if server_name == 'master' or settings.SERVICE_NAME == 'master':
            # server = UidServer.get(uid).server
            if uid != 'test':
                server = uid[:-7]
            else:
                server = server_name
            user_m = UserM.get(uid, server)
        elif server_name:
            user_m = UserM.get(uid, server_name)
        else:
            user_m = UserM.get(uid)

        o = cls(uid, user_m_obj=user_m)
        # o.countdown()
        return o

    def save(self):
        self.user_m.save()

    def set_active_time(self):
        """设定用户最后活跃时间
        """
        ts = int(time.time())
        self.activetime_event_check(self.user_m.active_time)
        self.user_m.update_login_stats(ts)
        if self.online_award:                           # 已经激活的在线时长奖励
            return
        if len(self.online_award_done) == len(game_config.online_award):    # 所有在线时长奖励已经领取完了
            return

        online_time = self.user_m.get_online_time(ts)
        for k, v in game_config.online_award_sort:
            if online_time >= v['second'] and k not in self.online_award_done:
                self.online_award.append(k)
                break

    def activetime_event_check(self, ts):
        """ 检查与活跃时间标记相关的活动，如老玩家回归。"""
        ERROR_HEAD = "ACTIVETIME EVENT FUNC BUG!!!"
        try:
            self.king.recall_check(ts, self.level)  # 检查是否老玩家回归
        except:
            debug_print(ERROR_HEAD, traceback.print_exc())

    def get_online_award_expire(self):
        """
        return -1, -1 奖励都领完；
                award_id, 0， 可领奖；
                award_id, 正整数，可领奖倒计时
        """
        if len(self.online_award_done) == len(game_config.online_award_sort):
            return -1, -1
        elif self.online_award:
            return self.online_award[0], 0
        else:
            online_time = self.user_m.get_online_time()
            for k, v in game_config.online_award_sort:
                if k not in self.online_award_done:
                    return k, v['second'] - online_time
            return -1, -1
    
    def update_online_status(self, ts=None):
        """更新用户在线状态，用于后台统计
        """
        self.user_m.redis.zadd(self.user_m.online_user_key(), **{self.uid: ts or int(time.time())})
    
    def new_update_online_status(self, ts=None):
        """# 将每天的活跃人数单独记在一个key里
        """
        date_prefix = str(datetime.datetime.now())[:10]
        new_key = self.user_m.online_user_key() + date_prefix
        self.user_m.redis.zadd(new_key, **{self.uid: ts or int(time.time())})

    def update_regist_status(self, ts=None):
        """# 记录用户注册时间，用于后台统计
        """
        self.user_m.redis.zadd(self.user_m.regist_user_key(), **{self.uid: ts or int(time.time())})

    def update_combat_rank(self, combat=None, save=False):
        """
        更新战力排行榜
        :param combat:
        :param save:
        :return:
        """
        cur_combat = combat or self.combat
        if cur_combat > self.cards.max_combat:
            self.cards.max_combat = cur_combat
            rank_key = self.user_m.get_combat_rank_key()
            r = self.user_m.get_father_redis(rank_key)
            r.zadd(rank_key, **{self.uid: generate_rank_score(cur_combat)})
            
            if self.open_door and self.world_id:
                open_door_rank = OpenDoorRank(self.world_id)
                open_door_rank.update_combat(self.uid, generate_rank_score(cur_combat))
            
            if save:
                self.cards.save()
            # r.zremrangebyrank(rank_key, 0, -(100 + 1))

    def check_changtianyou_mobile_pay(self, change_lvs=None, for_test=False):
        '''
        检查充值奖励 畅天游冲话费
        :param change_lvs:
        :param for_test:
        :return:
        '''
        if not for_test:
            if 'cmge' not in self.account.lower() or not self.mobile or not change_lvs or not self.regist_time:
                return

        # 充值队列放 主库里
        redis = Payment.redis
        key = Payment.mobile_pay_award_prefix
        backup_key = Payment.mobile_pay_award_backup_prefix
        # 邀请朋友注册奖励
        if len(self._request_code['slave']) >= 4:
            for uid in self._request_code['slave']:
                if User.get(uid).level < 20:
                    break
            else:
                if 'req' not in self.mobile_award:
                    uniq_id = '%s_%s_%s' % (self.mobile, 1000, 'request')
                    if not redis.zscore(backup_key, uniq_id):
                        redis.rpush(key, [self.uid, self.mobile, 1000, 'request'])
                        redis.zadd(backup_key, **{uniq_id: int(time.time())})    # [uid, mobilephone_num, rmb(分), tp]
                        self.mobile_award['req'] = [1]

        # 等级奖励
        if 'lv' not in self.mobile_award:
            self.mobile_award['lv'] = []

        # 升级到20就给 2块
        common_level_award = 20
        if common_level_award <= self.level:
            if common_level_award not in self.mobile_award['lv']:
                uniq_id = '%s_%s_%s' % (self.mobile, 200, 'request')
                if not redis.zscore(backup_key, uniq_id):
                    redis.rpush(key, [self.uid, self.mobile, 200, 'lv'])
                    redis.zadd(backup_key, **{uniq_id: int(time.time())})
                    self.mobile_award['lv'].append(common_level_award)

        # 2014年5月20日12：00~5月30日12：00
        start_time, end_time = 1400558400, 1401422400
        if not start_time <= self.regist_time <= end_time:
            return

        # 充值100块奖励， 最多两月有效期
        now = time.time()
        if now < end_time + 3600 * 24 * 60:
            if self.vip_exp / self.user_m.PAYMENT_RATE >= 100:

                first_level_award = 1                           # 充值就先返还20
                if first_level_award not in self.mobile_award['lv']:
                    redis.rpush(key, [self.uid, self.mobile, 2000, 'lv%s' % first_level_award])
                    self.mobile_award['lv'].append(first_level_award)

                for lv in [20, 30, 40, 50]:
                    uniq_id = '%s_%s_%s' % (self.mobile, lv, 'lv')
                    if not redis.zscore(backup_key, uniq_id):
                        if lv == 20 and lv <= self.level:
                            if self.mobile_award['lv'].count(lv) <= 1:
                                redis.rpush(key, [self.uid, self.mobile, 2000, 'lv%s' % lv])
                                redis.zadd(backup_key, **{uniq_id: int(time.time())})
                                self.mobile_award['lv'].append(lv)
                                continue
                        if lv <= self.level and lv not in self.mobile_award['lv']:
                            redis.rpush(key, [self.uid, self.mobile, 2000, 'lv%s' % lv])
                            redis.zadd(backup_key, **{uniq_id: int(time.time())})
                            self.mobile_award['lv'].append(lv)

    def checkout_request_code_gift(self, change_lvs=None):
        '''
        检查请求礼物 邀请别人的奖励
        :param change_lvs:
        :return:
        '''
        if not change_lvs:
            return
        # 给师傅发奖
        change_lvs = set(change_lvs)
        for master_uid in self._request_code['master']:
            master = User.get(master_uid)
            master_info = master._request_code['slave'].get(self.uid)
            if not master_info:
                continue
            ids = [x for x, y in game_config.request_code.iteritems()
                    if y['level'][0] <= self.level and x not in master_info['gift'] + master_info['done'] \
                    and master._request_slave_gift.get(x, 0) < UserM.MAX_REQUEST_CODE_SLAVE_NUM]

            if ids:
                master_info['gift'].extend(ids)
                master_info['gift'].sort()
                master.save()

        # # 给徒弟发奖
        # for slave_uid in self._request_code['slave']:
        #     slave = User.get(slave_uid)
        #     slave_info = slave._request_code['master'].get(self.uid)
        #     if not slave_info:
        #         continue
        #     ids = [x for x, y in game_config.request_code.iteritems()
        #             if y['level'][0] <= self.level and x not in slave_info['gift'] + slave_info['done']]
        #     if ids:
        #         slave_info['gift'].extend(ids)
        #         slave_info['gift'].sort()
        #         slave.save()

    def update_level_rank(self):
        '''
        更新等级排行
        :return:
        '''
        rank_key = self.user_m.get_level_rank_key()
        r = self.user_m.get_father_redis(rank_key)
        r.zadd(rank_key, **{self.uid, generate_rank_score(self.level)})
        r.zremrangebyrank(rank_key, 0, -(100 + 1))

    def set_pre_battle(self, toggle):
        """
        设置是否演示战前动画
        :param toggle:
        :return:
        """
        self.user_m.set_pre_battle(toggle)
        self.user_m.save()
        return toggle

    def get_top(self, num=20, page=0, tp='combat', p_key=''):
        '''
        获取各种排行榜
        :param num: 获取的数量
        :param page: 第几页
        :param tp: 排行榜类型
        :param p_key: key
        :return:
        '''
        # r = self.user_m.redis
        p_key = p_key or ''
        if tp == 'combat':
            p_key = self.user_m.get_combat_rank_key()
        elif tp == 'level':
            p_key = self.user_m.get_level_rank_key()
        elif tp == 'gacha_score':
            p_key = self.gacha.get_gacha_score_rank_key()
        elif tp == 'orange_card':
            p_key = self.cards.get_orange_card_rank_key()
        elif tp == 'purple_card':
            p_key = self.cards.get_purple_card_rank_key()
        elif tp == 'equipment':
            p_key = self.user_m.get_equipment_rank_key()
        elif tp == 'world_regain':
            p_key = self.user_m.get_world_regain_rank_key()
        elif tp == 'commander':
            p_key = self.user_m.get_commander_rank_key()
        elif tp == 'like':
            p_key = self.user_m.get_like_rank_key()

        r = self.user_m.get_father_redis(p_key)

        start_rank = page * num + 1
        end_rank = start_rank + num
        ranks = range(start_rank, end_rank)
        pipe = r.pipeline()
        users = []
        for rank in ranks:
            pipe.zrevrange(p_key, rank - 1, rank - 1, withscores=True, score_cast_func=round_float_or_str)

        for rs, user_rank in itertools.izip(pipe.execute(), ranks):
            if rs:
                [(user_id, user_score)] = rs
                users.append((user_id, user_rank, user_score))

        data = {}

        data['top'] = self.get_users_info(users, tp)
        data['cur_page'] = page
        data['count'] = r.zcard(p_key)

        return data

    def get_users_info(self, users, tp='combat'):
        """
        返回用户详细信息
        args：
            users:[(uid, rank, score), (uid, rank, score)]
        return:
            list
        """
        users_list = []

        for uid, rank, score in users:
            if tp in {'orange_card', 'purple_card'}:
                rank_key = uid                                          # 唯一标识
                uid, card_id = uid.split('_')

            u = self.get(uid)
            if u and u.regist_time:
                info = {
                    'uid': u.uid,
                    'level': u.level,
                    'name': u.name,
                    'rank_key': u.uid,
                    'rank': rank,
                    'role': u.role,
                    'combat': score if tp == 'combat' else u.combat,
                    'guild_name': u.association_name,
                    'score': score,
                    'parise_flag': uid in self.like_log.get(tp, []),    # 点赞标记
                }

                if tp in {'orange_card', 'purple_card'}:
                    info['config_id'] = int(card_id.split('-')[0])
                    info['rank_key'] = rank_key

                users_list.append(info)

        return users_list

    def check_and_remove_items(self, items, remove=True):
        '''
        检查items中的东西是否足够，若够，则删除这些东西，若不够，则返回错误码
        :param items:   物品list，如[[1,0,11000],[2,0,10200],[6,1902,15],[7,12001,1]]
                        第一个表示种类，第二个为id，第三个为数量
                        种类列表：
                        1、食品，占位，参数数量,权重；[1,0,100]
                        2、金属，占位，参数数量,权重；[2,0,100]
                        3、能源，占位，能源数量,权重；[3,0,100]
                        4、能晶，占位，能晶数量,权重；[4,100]
                        5、卡牌，卡牌ID,数量,权重；[5,4,1]
                        6、道具，ID,数量,权重；[6,4,1]
                        7、装备,ID，数量,权重；[7,4,1]
                        9、钻石,占位，数量,权重[9,0,1]
                        10、强能之尘，占位，数量：[10,0,1]
                        11、超能之尘，占位，数量：[11,0,1]
                        14、星灵，占位，数量[14,0,200]
                        15、金币，占位，数量[15,0,500]
                        16、精炼石，占为，数量[16,0,300]
                        21、魔光碎片，占为，数量[21,0,200]
                        23、洗炼石，占为，数量[23,0,200]
                        31、木材，占为，数量[31,0,200]
                        32、魂石，占为，数量[32,0,200]
                        33、初级锻造石，占为，数量[33,0,200]
                        34、中级锻造石，占为，数量[34,0,200]
                        35、高级锻造石，占为，数量[35,0,200]
        :param remove:  是否在检查后删除这些物品，默认为是
        :return:    所有物品均存在且可用则返回0，否则返回错误状态码
        '''
        if not items:
            return 0

        need_items = {}
        need_equips = {}
        need_cards = {}
        need_else = {}

        for item_tp, item_id, num in items:
            if item_id in [1, 2, 3, 4, 9, 10, 11, 14, 15, 16, 21, 23, 31, 32, 33, 34, 35]:
                if item_tp in need_else:
                    need_else[item_tp] += num
                else:
                    need_else[item_tp] = num

            if item_tp in [5, 6, 7]:
                if item_tp == 5:
                    need = need_cards
                elif item_tp == 6:
                    need = need_items
                elif item_tp == 7:
                    need = need_equips
                if item_id in need:
                    need[item_id] += num
                else:
                    need[item_id] = num

        for genre, quantity in need_else.items():
            if genre == 1:
                if self.food < quantity:
                    return 'error_5'                # 食物不足
            elif genre == 2:
                if self.metal < quantity:
                    return 'error_6'                # 金属不足
            elif genre == 3:
                if self.energy < quantity:
                    return 'error_7'                # 能源不足
            elif genre == 4:
                if self.crystal < quantity:
                    return 'error_8'                # 能晶不足
            elif genre == 9:
                if self.coin < quantity:
                    return 'error_4'                # 钻石不足
            elif genre == 10:
                if self.dirt_silver < quantity:
                    return 'error_19'               # 强能之尘不足
            elif genre == 11:
                if self.dirt_gold < quantity:
                    return 'error_18'               # 超能之尘不足
            elif genre == 14:
                if self.star < quantity:
                    return 'error_12'               # 星灵不足
            elif genre == 15:
                if self.silver < quantity:
                    return 'error_13'               # 金币不足
            elif genre == 16:
                if self.metalcore < quantity:
                    return 'error_16'               # 精炼石不足
            elif genre == 21:
                if self.enchant < quantity:
                    return 'error_40'               # 魔光碎片不足
            elif genre == 23:
                if self.refine_stone < quantity:
                    return 'error_23'               # 洗炼石不足
            elif genre == 31:
                if self.wood < quantity:
                    return 'error_35'               # 木材不足
            elif genre == 32:
                if self.soul_stone < quantity:
                    return 'error_36'               # 魂石不足
            elif genre == 33:
                if self.small_forge_stone < quantity:
                    return 'error_37'               # 初级锻造石不足
            elif genre == 34:
                if self.middle_forge_stone < quantity:
                    return 'error_38'               # 中级锻造石不足
            elif genre == 35:
                if self.high_forge_stone < quantity:
                    return 'error_39'               # 高级锻造石不足

        for k, v in need_items.items():
            if self.item.get_item_count(k) < v:
                return 5                            # 道具不足

        # 判断装备是否够，并将符合条件的较弱的装备放进need_equip_ids方便后面删除
        need_equip_ids = []
        if need_equips:
            avaliable_equips = {}
            all_pos_equip = self.equip.get_all_equip_pos(is_formation=False)
            for k, v in self.equip._equip.iteritems():
                if k not in all_pos_equip:
                    if v['c_id'] in avaliable_equips:
                        avaliable_equips[v['c_id']].append((k, v['lv']))
                    else:
                        avaliable_equips[v['c_id']] = [(k, v['lv'])]

            for _c_id, _need_num in need_equips.items():
                id_lv = avaliable_equips.get(_c_id, [])
                if _need_num > len(id_lv):
                    return 6                        # 没有足够数量的空闲装备可做材料
                id_lv.sort(key=lambda x: x[1])
                need_equip_ids.extend(id_lv[:_need_num])

        # 判断卡牌是否够，并将符合条件的较弱的卡牌放进need_card_ids方便后面删除
        need_card_ids = []
        if need_cards:
            avaliable_cards = {}
            for k, v in self.cards._cards.iteritems():
                if not v['pos'] and self.cards.is_remove_able(k):
                    if v['c_id'] in avaliable_cards:
                        avaliable_cards[v['c_id']].append((k, v['lv'], v['evo']))
                    else:
                        avaliable_cards[v['c_id']] = [(k, v['lv'], v['evo'])]

            for _c_id, _need_num in need_cards.items():
                id_lv = avaliable_cards.get(_c_id, [])
                if _need_num > len(id_lv):
                    return 7  # 没有足够数量的空闲卡牌可做材料
                id_lv.sort(key=lambda x: (x[2], x[1]))
                need_card_ids.extend(id_lv[:_need_num])

        # 删除各项物资
        if remove:
            item_save = equip_save = card_save = else_save = False
            for _id, _lv in need_equip_ids:
                self.equip.remove(_id)
                equip_save = True
            for k, v in need_items.items():
                self.item.del_item(k, v)
                item_save = True
            for _id, _lv, _evo in need_card_ids:
                self.cards.remove(_id)
                card_save = True
            for genre, quantity in need_else.items():
                else_save = True
                if genre == 1:
                    self.food -= quantity
                elif genre == 2:
                    self.metal -= quantity
                elif genre == 3:
                    self.energy -= quantity
                elif genre == 4:
                    self.crystal -= quantity
                elif genre == 9:
                    self.coin -= quantity
                elif genre == 10:
                    self.dirt_silver -= quantity
                elif genre == 11:
                    self.dirt_gold -= quantity
                elif genre == 14:
                    self.star -= quantity
                elif genre == 15:
                    self.silver -= quantity
                elif genre == 16:
                    self.metalcore -= quantity
                elif genre == 21:
                    self.enchant -= quantity
                elif genre == 23:
                    self.refine_stone -= quantity
                elif genre == 31:
                    self.wood -= quantity
                elif genre == 32:
                    self.soul_stone -= quantity
                elif genre == 33:
                    self.small_forge_stone -= quantity
                elif genre == 34:
                    self.middle_forge_stone -= quantity
                elif genre == 35:
                    self.high_forge_stone -= quantity

            if else_save:
                self.save()
            if card_save:
                self.cards.save()
            if equip_save:
                self.equip.save()
            if item_save:
                self.item.save()

        return 0

    def get_online_award(self):
        '''
        获取在线奖励
        :return:
        '''
        reward = {}
        if self.online_award:
            score = self.online_award.pop()
            self.online_award_done.append(score)
            self.user_m.online_time = time.time()
            reward = add_gift(self, game_config.online_award[score]['award'])
        return reward

    def add_gift(self, gift_config, cur_data={}, save=True):
        """# add_gift: docstring
        args:
            gift_config, cur_data={}, save=True:    ---    arg
        returns:
            0    ---
        """
        return add_gift(self, gift_config, cur_data, save)

    def get_free_train_times(self):
        '''
        获取训练次数
        :return:
        '''
        return self.free_train_times    # + game_config.vip[self.vip]['free_fast_train']

    @staticmethod
    def map_enemy(cls, fight_id, fight_config, sort=1):
        '''
        地图的敌人
        :param cls:
        :param fight_id:
        :param fight_config:
        :param sort:
        :return:
        '''
        return fake.map_battle_user(fight_id, fight_config, sort=sort)

    @property
    def combat(self):
        """队伍整体的战斗力
        """
        alignment = self.cards.alignment
        combat_point = 0
        for card_id in itertools.chain(alignment[0], alignment[1]):
            if card_id in self.cards._cards:
                info = self.cards.single_card_info(card_id, for_battle=True)
                combat_point += self.calc_combat(info)

        return int(combat_point)

    def calc_enemy_combat(self, enemy_obj):
        """计算怪物的 战力"""
        combat_point = 0
        for card_id in enemy_obj.cards._cards:
            info = enemy_obj.cards.single_card_info(card_id)
            combat_point += self.calc_combat(info, is_user=False)
        return int(combat_point)

    def calc_combat(self, info, is_user=True):
        """计算一个卡片的战斗力
        args:
            info: 卡片数据
            is_user: 是否是真实玩家(包括机器人)，区别出地图里 虚拟生成的怪物
        returns:
            数字: 一个卡片的战斗力
        """
        # base = sum(info[attr] * rate for attr, rate in game_config.combat_base.iteritems())
        base = dict([(attr, info[attr]) for attr in game_config.combat_base])

        # 增加属性伤害效果
        attr_types = ['fire', 'water', 'wind', 'earth', 'fire_dfs', 'water_dfs', 'wind_dfs', 'earth_dfs']
        attr_value = 0
        for attr_type in attr_types:
            attr_value += info.get(attr_type, 0)

        if is_user:     # 用户才有装备，地图里的怪没有
            _mappings = ['patk', 'matk', 'def', 'speed', 'hp']
            if info['pos'] > 0:
                # 卡牌的pos为 1~5 和 11~15 装备的pos 为 0~9,需转换一下
                pos = info['pos'] - 1 if info['pos'] < 10 else info['pos'] - 6
                for equip_id in self.equip.equip_pos[pos]:
                    if equip_id != 0:
                        _temp = self.equip.single_info(equip_id, combat=True)
                        for i in _mappings:
                            base[i] += _temp[i]
                        # 装备附魔效果增加的属性伤害计入attr_value
                        for i in attr_types:
                            attr_value += _temp.get(i, 0)

                temp = self.equip.suit_effect(pos, self.equip.equip_pos[pos])   # 套装增幅
                for i in _mappings:
                    base[i] += temp[i]
                for i in attr_types:
                    attr_value += temp.get(i, 0)

        base = sum([base[attr] * rate for attr, rate in game_config.combat_base.iteritems()])
        skill_coefficient = 0
        for s in ('s_1', 's_2', 's_3', 's_4', 's_5'):
            skill = info.get(s)
            if skill and skill['avail'] == 2 and skill['s'] in game_config.skill_detail:
                quality = game_config.skill_detail[skill['s']]['skill_quality']
                skill_coefficient += game_config.skill_detail[skill['lv']][quality]

        return base * (1 + skill_coefficient) + attr_value

    @property
    def god_combat_1(self):
        combat_point = self.god_field_combat(god_formation=1)
        return combat_point

    @property
    def god_combat_2(self):
        combat_point = self.god_field_combat(god_formation=2)
        return combat_point

    @property
    def god_combat_3(self):
        combat_point = self.god_field_combat(god_formation=3)
        return combat_point

    def god_field_combat(self, god_formation):
        """队伍整体的战斗力
        """
        combat_point = 0
        for _index, card_id in enumerate(self.god_field.god_field_ids[god_formation]):
            if card_id in ['0', '-1']: continue
            if card_id in self.cards._cards:
                info = self.cards.single_card_info(card_id, for_battle=True, god_formation=god_formation)
                combat_point += self.god_calc_combat(info, _index, god_formation)
        return int(combat_point)
    
    def god_calc_combat(self, info, _index, god_formation, is_user=True):
        """计算一个卡片的战斗力
        args:
            info: 卡片数据
            is_user: 是否是真实玩家(包括机器人)，区别出地图里 虚拟生成的怪物
        returns:
            数字: 一个卡片的战斗力
        """
        # base = sum(info[attr] * rate for attr, rate in game_config.combat_base.iteritems())
        base = dict([(attr, info[attr]) for attr in game_config.combat_base])
        
        # 增加属性伤害效果
        attr_types = ['fire', 'water', 'wind', 'earth', 'fire_dfs', 'water_dfs', 'wind_dfs', 'earth_dfs']
        attr_value = 0
        for attr_type in attr_types:
            attr_value += info.get(attr_type, 0)
        
        if is_user:     # 用户才有装备，地图里的怪没有
            _mappings = ['patk', 'matk', 'def', 'speed', 'hp']
            # 神域的装备阵型
            if god_formation == 1:
                equip_pos = self.equip.equip_pos_1
            elif god_formation == 2:
                equip_pos = self.equip.equip_pos_2
            elif god_formation == 3:
                equip_pos = self.equip.equip_pos_3
            else:
                equip_pos = {}
            
            for equip_id in equip_pos.get(_index, []):
                if equip_id != 0:
                    _temp = self.equip.single_info(equip_id, combat=True)
                    for i in _mappings:
                        base[i] += _temp[i]
                    # 装备附魔效果增加的属性伤害计入attr_value
                    for i in attr_types:
                        attr_value += _temp.get(i, 0)

            temp = self.equip.suit_effect(_index, equip_pos.get(_index, []))  # 套装增幅
            for i in _mappings:
                base[i] += temp[i]
            for i in attr_types:
                attr_value += temp.get(i, 0)
        
        base = sum([base[attr] * rate for attr, rate in game_config.combat_base.iteritems()])
        skill_coefficient = 0
        for s in ('s_1', 's_2', 's_3', 's_4', 's_5'):
            skill = info.get(s)
            if skill and skill['avail'] == 2 and skill['s'] in game_config.skill_detail:
                quality = game_config.skill_detail[skill['s']]['skill_quality']
                skill_coefficient += game_config.combat_skill[skill['lv']][quality]
        
        return base * (1 + skill_coefficient) + attr_value

    def countdown(self):
        """# countdown:
            func的返回值：
                0, [clean_func, ]
                    0 表示该任务完成，需要从countdown_func_list中清除
                    [], 每个元素是清理函数

        args:
            :    ---    arg
        returns:
            0    ---
        """
        now = time.time()
        new_list = []
        list_change = False
        for t in self.countdown_func_list:
            end_time, class_instance, flag = t
            if now > int(end_time) or int(end_time) == -1:
                need_remain, clean_func_list = class_instance.run(self)
                if need_remain:
                    if need_remain < 0:
                        # 如果need_remain是负数，则这个数字表示下次运行时间
                        tt = (-need_remain, t[1])
                        list_change = True
                    else:
                        tt = t
                    new_list.append(tt)
                for cf in clean_func_list:
                    if callable(cf):
                        cf()
                continue
            new_list.append(t)
        if list_change or len(new_list) < len(self.countdown_func_list):
            self.countdown_func_list = new_list
            self.save()

    def remove_countdown(self, flag):
        """
        移除指定时间回调函数
        """
        for i, v in enumerate(self.user_m.countdown_func_list):
            end_time, callback_func, tempflag = v
            if tempflag == flag:
                del self.user_m.countdown_func_list[i]
                self.save()
                break
        
    def get_user_info(self, new_version=True):
        """
        获取一个用户简单数据
        :param new_version:
        :return:
        """
        # 主战卡牌
        alignment_info = []
        for card_id in self.cards.alignment[0]:
            alignment_info.append(self.cards.single_card_info(card_id) if str(card_id) != self.cards.NONE_CARD_ID_FLAG else {})

        # 主战和替补卡牌信息
        _cards = {}
        alignment = self.cards.alignment
        for ali in alignment:
            for card_id in ali:
                if card_id in self.cards._cards:
                    _cards[card_id] = self.cards.single_card_info(card_id)

        # 加入助威的卡信息
        for card_id in self.cards.assistant:
            if card_id in self.cards._cards:
                _cards[card_id] = self.cards.single_card_info(card_id)

        # 加入命运的卡信息
        for card_id in self.cards.destiny:
            if card_id in self.cards._cards:
                _cards[card_id] = self.cards.single_card_info(card_id)

        # 装备信息
        _equips = {}
        for equip_id in self.equip.get_all_equip_pos(is_formation=False):
            _equips[equip_id] = self.equip.single_info(equip_id)

        data = {
            'uid': self.uid,
            'name': self.name,
            'level': self.level,
            'role': self.role,
            'online': self.user_m.online,               # 是否在线
            'association_id': self.association_id,
            'association_name': self.association_name,  # 工会名
            'combat': self.combat,
            'alignment_info': alignment_info,           # 主战卡牌信息
        }
        if new_version:
            data['new_data'] = {
                # 新版本 个人信息#
                'user': {
                    'uid': self.uid,
                    'name': self.name,
                    'level': self.level,
                    'role': self.role,
                    'association_name': self.association_name,
                    'association_id': self.association_id,
                    'combat': self.combat,
                },
                'cards': _cards,
                'alignment': self.cards.alignment,      # 主战和替补
                'formation': self.cards.formation,      # 出战的阵型
                'equip': _equips,                       # 装备信息
                'equip_pos': self.equip.equip_pos,      # 主战和替补位置上的装备
                'ass_equip_pos': self.equip.ass_equip_pos,  # 助威装备
                'open_position': self.cards.open_position,  # 当前已开启站位
                'assistant': self.cards.assistant,      # 助威的卡信息
                'assistant_effect': self.cards.assistant_effect,    # 助威效果
                'destiny': self.cards.destiny,          # 命运
                'gem_pos': self.gem.gem_pos,            # 宝石
                'medal_pos': self.medal.medal_pos,      # 勋章
                # 新版本 个人信息#
            }
        return data

    def is_cards_full(self):
        """# is_cards_full: 卡牌包裹是否已满
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return len(self.cards._cards) >= game_config.role[self.level]['character_max'] + self.cards.bag_extend

    def is_equip_full(self):
        """# is_equip_full: 装备包裹是否已满
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return len(self.equip._equip) >= game_config.role[self.level]['equip_max'] + self.equip.bag_extend

    def is_gem_full(self):
        """ 觉醒宝石包裹是否已满

        :return:
        """
        return (self.gem._gem) >= self.gem.GEM_MAX + self.gem.bag_extend

    def is_soul_full(self):
        """# is_soul_full: 英魂卡牌包裹是否已满
        args:
            :    ---    arg
        returns:
            0    ---
        """
        return len(self.soul._souls) >= game_config.role[self.level].get('soul_max', 0) + self.soul.bag_extend

    def add_goods(self, goods_data):
        """统一加物品接口

        goods_data = {
            'exp': 0,     # 经验
            'coin': 0,    # 金币
            'food': 0,    # 食物
            'metal': 0,   # 金属
            'energy': 0,  # 能源
            'crystal': 0, # 能晶
            'action_point': 0, # 体力
            'item': [(1, 2), (2, 2)]      # 道具列表[(id, num), (id, num)]
            'cards': [(1, 2), (2, 2)]     # 卡牌列表[(id, num), (id, num)]
            'equip': [(1, 2), (2, 2)]     # 装备列表[(id, num), (id, num)]
        }
        args:
            goods_data: 格式化好的物品数据
        returns:
            {}: 统一的返回数据
        """
        temp = {'food': 0, 'coin': 0, 'metal': 0, 'energy': 0, 'crystal': 0, 'exp': 0,
                'action_point': 0, 'item': [], 'cards': [], 'equip': [], 'gem': []}

        for key, value in goods_data.iteritems():
            if not value: continue
            if key == 'coin':
                self.coin += value
                temp['coin'] += value

            elif key == 'food':
                self.food += value
                temp['food'] += value

            elif key == 'metal':
                self.metal += value
                temp['metal'] += value

            elif key == 'energy':
                self.energy += value
                temp['energy'] += value

            elif key == 'crystal':
                self.crystal += value
                temp['crystal'] += value

            elif key == 'action_point':
                self.action_point += value
                temp['action_point'] += value

            elif key == 'exp':
                self.exp += value
                temp['exp'] += value

            elif key == 'item':
                for _id, num in value:
                    self.item.add_item(_id, num, immediate=True)
                    temp['item'].append(_id)
                self.item.save()

            elif key == 'cards':
                for _id, num in value:
                    for _ in xrange(num):
                        tempid = self.cards.new(_id)
                        temp['cards'].append(tempid)
                self.cards.save()

            elif key == 'equip':
                for _id, num in value:
                    for _ in xrange(num):
                        tempid = self.equip.new(_id)
                        temp['equip'].append(tempid)
                self.equip.save()

            elif key == 'gem':
                for _id, num in value:
                    for _ in xrange(num):
                        tempid = self.gem.add(_id)
                        temp['gem'].append(tempid)
                self.gem.save()

            elif key == 'medal':
                for _id, num in value:
                    for _ in xrange(num):
                        medalnum = self.medal.add_medal(_id)
                        temp['metal'].append(medalnum)
                self.medal.save()

        self.save()
        return temp

    def update_session_and_expired(self, sid, expired):
        """ 更新session和过期时间

        :return:
        """
        if self.sid == sid and self.expired == expired:
            return False

        self.sid = sid
        self.expired = expired
        return True

    def session_expired(self, session):
        """ 检查session是否过期

        :param session:
        :return:
        """
        if self.expired:
            if self.expired < time.time():
                return True
            elif self.sid != session:
                return True
            else:
                return False
        else:
            return True

    ############### User Property BEGIN ################

    def foo(atr):
        doc = "The foo property."

        def fget(self):
            return getattr(self.user_m, atr)

        def fset(self, value):
            if atr == 'coin' and self.user_m.coin < value:
                try:
                    self.user_m.coin_logs.append((int(time.time()), get_local_ip(), self.user_m.coin, value,
                                                  self.method, getattr(settings, 'ENVPROCS', None)))
                    self.user_m.coin_logs = self.user_m.coin_logs[-500:]
                except:
                    traceback.print_exc()
            setattr(self.user_m, atr, value)

        # def fdel(self):
        #     del self.__dict__[atr]
        return {
            'doc': doc,
            'fget': fget,
            'fset': fset,
            # 'fdel': fdel,
        }

    property_keys = UserM._attrs.keys()
    property_keys.extend([
        'food_pool_max', 'metal_pool_max', 'energy_pool_max'
    ])
    special_property = ['uid', 'exp', 'action_point', 'coin_logs']
    for atr in property_keys:
        if atr in special_property: continue
        locals()[atr] = property(**foo(atr))
    del atr

    LEVEL_UP_DATA_UPDATE = [    # 当升级的时候，根据某一项配置，执行的某一个函数
        # (model在logics.user中的property名字，model中需要运行的函数名（参数是level))

        ('user_m', 'set_action_point_max'),         # 升级时提升action_point最大值
        ('user_m', 'level_up_add_action_point'),    # 升级时提升action_point
        ('cards', 'add_position_num'),              # 升级送 出战卡个数
        # ('cards', 'add_new_formation'),             # 升级送新的阵型
        # ('cards', 'add_new_open_position'),         # 开启新的站位
        ('user_m', 'level_up_add_harbor_school_factory_hospital_laboratory')    # 升级的时候给几个功能建筑加等级
    ]

    def add_pay_award(self, open_gift=0, price=0, product_id=0):
        """
        添加充值的奖励
        :param open_gift: 开启类型
        :param price: 钱
        :param product_id: 商品id
        :return:
        """
        if price:
            if self.daily_award.can_coin_award_loop():
                self.daily_award.coin_award_loop['pay_rmb'] += price
            else:
                self.daily_award.coin_award['pay_rmb'] += price

            self.daily_award.save()
        if open_gift == 1:  # 周卡
            if not self.pay_award.week['pay_dt']:
                self.pay_award.week['reward'] = game_config.get_config(self._server_name, 'week_award')
                self.pay_award.week['pay_dt'] = utils.get_datetime_str()
                self.pay_award.save()
            else:           # 重复买给钻石补偿
                self.coin += 980
        elif open_gift == 2:    # 月卡
            if not self.pay_award.month['pay_dt']:
                self.pay_award.month['reward'] = game_config.get_config(self._server_name, 'month_award')
                self.pay_award.month['pay_dt'] = utils.get_datetime_str()
                self.pay_award.save()
            else:           # 重复买给钻石补偿
                self.coin += 300
        elif open_gift == 3:    # 成长计划
            if not self.grow_gift.open():
                self.coin += price * 11
        elif open_gift == 4:    # 限时礼包
            charge_config = game_config.get_config(self._server_name, 'charge').get(product_id)
            lv = charge_config.get('reward_id', 0)
            config = game_config.get_config(self._server_name, 'level_gift').get(lv)
            if config and lv in self.level_gift:
                self.level_gift.pop(lv)
                content_format = game_config.return_msg_config.get('level_gift', '')
                content = content_format % {'name': charge_config['name']}
                message = self.notify._generate_custom_notify(
                    unicode('level_gift', 'utf-8'), content, config['reward']
                )
                self.notify.add_message(message, save=True)
            else:
                self.coin += price * 11

    def add_vip_exp(self, add_exp):
        '''
        增加vip经验
        :param add_exp: 经验值
        :return:
        '''
        if not add_exp:
            return
        next_exp = self.vip_exp + add_exp
        next_level = self.vip
        while 1:
            if next_level + 1 not in game_config.vip:
                break
            if next_exp >= game_config.vip[next_level]['need_exp']:
                next_level += 1
                continue
            break

        self.vip_exp = next_exp
        self.vip = next_level
        flag = self.notify.send_charge_reward()
        if flag:
            self.notify.save()

    def auto_vip_reward(self):
        """ 自动领取每周vip奖励

        :return:
        """
        # 领取每周vip奖励
        vip_reward_config = game_config.vip_reward.get(self.vip)
        if vip_reward_config:
            week = time.strftime("%W")
            if self.vip_week != week:
                self.vip_week = week
                message = self.notify._generate_custom_notify('vip_every_week_reward',
                            vip_reward_config['mail'], vip_reward_config['reward'])
                self.notify.add_message(message, True)
                self.save()

    def exp():
        doc = "The exp property."

        def fget(self):
            return getattr(self.user_m, 'exp')

        def fget(self, value):
            role_config = game_config.role
            next_level_exp_need = role_config[self.level]['exp']
            level = self.level
            self.level_change.append((level, next_level_exp_need))

            level_up_data_update_cache = {  # 升级后需要执行一些函数，为了减少创建和获取对象的开销，做这个cache
                # '配置表_配置列_property名字_函数名字' : ( 配置，函数)
            }

            while next_level_exp_need <= value:
                if level + 1 not in role_config:
                    value = next_level_exp_need
                    break
                value -= next_level_exp_need
                level += 1
                next_level_exp_need = role_config[level]['exp']
                self.level_change.append((level, next_level_exp_need))

                # 针对每一次升级，更新数据
                for t in self.LEVEL_UP_DATA_UPDATE:
                    k = '_'.join(t)
                    if k not in level_up_data_update_cache:
                        t_model = getattr(self, t[0])
                        t_func = getattr(t_model, t[1])
                        level_up_data_update_cache[k] = t_func
                        self.user_m._add_model_save(t_model)
                    else:
                        t_func = level_up_data_update_cache[k]
                    t_func(level)

            setattr(self.user_m, 'exp', value)
            self.level = level
            # 每次增加exp  level_change里都会添加一个 元素(level, next_level_exp_need)，与前端约定的 升级步骤
            # 如果多次加exp未升级的话 level_change里就会有多个重复的 元素，需要去重
            _change = []
            for i in self.level_change:
                if i not in _change:
                    _change.append(i)
            self.level_change = _change
            # 升级广播
            if len(self.level_change) > 1:
                change_lvs = [x[0] for x in self.level_change[1:]]
                flag = False
                for stove_id, v in game_config.character_train_position.iteritems():
                    if v['open_sort'] == 1 and v['value'] and v['value'][0] in change_lvs:
                        stove = getattr(self.school, stove_id, None)
                        if stove and not stove['available']:
                            stove['available'] = 1
                            flag = True

                if flag:
                    self.school.save()

                notice.notice_4_level_up(self, change_lvs=change_lvs)
                guide.mark_guide_4_level_up(self, change_lvs=change_lvs)
                flag = self.notify.send_level_up_gift(save=False)
                self.update_level_rank()
                self.checkout_request_code_gift(change_lvs=change_lvs)
                # 畅天游冲话费
                self.check_changtianyou_mobile_pay(change_lvs)

                if self.vip >= 1:
                    self.daily_award.open_viplogin_award(force_save=False)      # 每日奖励, 开启vip登录奖励
                if flag:
                    self.user_m._add_model_save(self.notify)
                # 升级奖励
                for _lv in game_config.level_gift:
                    if _lv in change_lvs:
                        self.level_gift[_lv] = int(time.time()) + self.user_m.LEVEL_GIFT_EXPIRE     # 等级变化奖励时间有效期

        return locals()

    # 主角的经验
    exp = property(**exp())

    def action_point():
        doc = "The action_point property."

        def fget(self):
            return self.user_m.action_point

        def fset(self, value):
            # 做减法的时候, 如果当前行动点数已经为最大值，做减法的同时
            # 需要把最后更新时间定为当前时刻
            if value < self.user_m.action_point:
                if self.user_m.action_point >= self.user_m.action_point_max:
                    self.user_m.action_point_updatetime = time.time()
                # 把消耗的体力纪录到全服消耗的方法中
                action_point = self.user_m.action_point - value
                # self.large_super_all.use_coin_or_action_point(action_point=int(action_point))
            self.user_m.action_point = value        # 赋值当前的体力

        return locals()

    # 主角的行动力
    action_point = property(**action_point())

    #####################
    ####### 公会一大堆
    #############

    def all_association():
        doc = "所有工会的列表"
        def fget(self):
            if not getattr(self, "_all_association", None):
                from models.association import AllAssociation as all_associationM
                _all_association = all_associationM.get(self.uid, self._server_name)
                setattr(self, "_all_association", _all_association)
            return self._all_association

        def fget(self, value):
            self._all_association = value

        def fdel(self):
            del self._all_association

        return locals()

    all_association = property(**all_association())

    def association():
        doc = "用户参加的工会"
        def fget(self):
            if not getattr(self, "_association", None):
                from models.association import Association as associationM
                _association = associationM.get(self.association_id, self._server_name)
                setattr(self, "_association", _association)
            return self._association

        def fset(self, value):
            self._association = value

        def fdel(self):
            del self._association

        return locals()

    association = property(**association())

    def association_log():
        doc = "The association_log property."
        def fget(self):
            if not getattr(self, "_association_log", None):
                from models.association import AssociationLog as association_logM
                _association_log = association_logM.get(self.association_id, self._server_name)
                setattr(self, "_association_log", _association_log)
            return self._association_log

        def fset(self, value):
            self._association_log = value

        def fdel(self):
            del self._association_log

        return locals()

    association_log = property(**association_log())

    def association_buy_log():
        doc = "公会的购买日志"
        def fget(self):
            if not getattr(self, "_association_buy_log", None):
                from models.association import AssociationBuyLog as association_buy_logM
                _association_buy_log = association_buy_logM(self.association_id, self._server_name)
                setattr(self, "_association_buy_log", _association_buy_log)
            return self._association_buy_log

        def fget(self, value):
            self._association_buy_log = value

        def fdel(self):
            del self._association_buy_log

        return locals()

    association_buy_log = property(**association_buy_log())

    def association_user():
        doc = "用户工会数据"
        def fget(self):
            if not getattr(self, "_association_user", None):
                from models.association import AssociationUser as association_userM
                _association_user = association_userM.get(self.uid, self._server_name)
                setattr(self, "_association_user", _association_user)
            return self._association_user

        def fset(self, value):
            self._association_user = value

        def fdel(self):
            del self._association_user

        return locals()

    association_user = property(**association_user())

    def refresh_guild_fight_reward(self):
        """
        自动领取世界争霸钻石消耗奖励
        :param server:
        :return:
        """
        if self.guild_fight_reward:
            cost = self.guild_fight_reward
            config_info = game_config.guild_fight_buy
            for key, value in config_info.iteritems():
                # 判断手动领奖  领了哪些的奖
                cost1 = value['cost']
                if cost >= cost1:
                    # 发送奖励邮件
                    content = value['mail'] % {'cost': cost}
                    message = self.notify._generate_custom_notify(unicode('guild_fight_reward', 'utf-8'), content, value['reward'])
                    self.notify.add_message(message, True)

            # 清空数据
            self.clean()

    def clean(self):
        # 清空数据的方法
        self.guild_fight_reward = 0
        self.guild_reward_log = []

    #############
    ####### 公会一大堆
    #####################

    ############### User Property END ##################

    _model_property_candidate_list = [
        # property name,    module,                     class
        ('cards', 'cards', 'Cards'),
        ('handbook', 'cards', 'Handbook'),              # 图鉴
        ('code', 'code', 'Code'),                       # 激活码
        ('daily_award', 'daily_award', 'Daily_award'),  # 每日奖励
        ('drama', 'drama', 'Drama'),                    # 战斗剧情
        ('equip', 'equip', 'Equip'),                    # 装备
        ('gacha', 'gacha', 'Gacha'),                    # 抽卡
        ('gift', 'gift', 'Gift'),                       # 礼物
        ('item', 'item', 'Item'),                       # 道具
        ('reward', 'reward', 'Reward'),                 # 奖励
        ('skill', 'skill', 'Skill'),                    # 英雄技能
        ('notify', 'notify', 'Notify'),                 # 各种邮件通知
        ('commander', 'commander', 'Commander'),        # 统帅
        ('gem', 'gem', 'Gem'),                          # 宝石系统
        ('step', 'logging', 'Step'),                    # 步骤记录
        ('pets', 'pets', 'Pets'),                       # 宠物
        ('medal', 'medal', 'Medal'),                    # 勋章
    ]

    def property_template(i):
        doc = "The %s property." % i[0]
        def fget(self):
            if not getattr(self, "_%s" % i[0], None):
                m = __import__('models', globals(), fromlist=[i[1], i[2]])
                server = self.user_m._server_name
                temp = m.__dict__[i[1]].__dict__[i[2]].get(self.uid, server)
                setattr(temp, 'weak_user', weakref.proxy(self))
                setattr(self, "_%s" % i[0], temp)
            return getattr(self, '_%s' % i[0])

        def fset(self, value):
            setattr(self, '_%s' % i[0], value)

        def fdel(self):
            del self.__dict__['_%s' % i[0]]

        return {
            'doc': doc,
            'fget': fget,
            'fset': fset,
            'fdel': fdel,
        }

    for k in _model_property_candidate_list:
        locals()[k[0]] = property(**property_template(k))