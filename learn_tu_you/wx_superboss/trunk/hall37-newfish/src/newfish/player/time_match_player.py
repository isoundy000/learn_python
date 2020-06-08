#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import random

from freetime.util import log as ftlog
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.player.player_base import FishPlayer
from newfish.entity.match_record import MatchRecord
from newfish.player.player_buffer import FishPlayerBuffer


class FishTimeMatchPlayer(FishPlayer):
    """
    回馈赛的玩家
    """

    def __init__(self, table, seatIndex, clientId=None):
        super(FishTimeMatchPlayer, self).__init__(table, seatIndex, clientId)

    def _loadUserData(self):
        super(FishTimeMatchPlayer, self)._loadUserData()
        record = MatchRecord.loadRecord()