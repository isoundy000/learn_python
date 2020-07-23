#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/23


c = {
	441011000: FTRoomDefine(bigRoomId = 44101, parentId = 0, roomId = 441011000, gameId = 44, configId = 101, controlId = 1, shadowId = 0, serverId = GR0044001_999, tableCount = 0, shadowRoomIds = [441011001], configure = {
    'fishPool': 44101,
    'hasrobot': 1,
    'isMatch': 1,
    'matchConf': {
        'bullet': 5000,
        'desc': '',
        'discountTime': ['2018-10-20 00:00:00', '2018-10-23 23:59:59'],
        'fees': [{
            'count': 50,
            'itemId': 'item:3106',
            'params': {
                'failure': 'ID_ROOM_44101_FAILURE_1'
            }
        }, {
            'count': 33,
            'itemId': 'item:3106',
            'params': {
                'failure': 'ID_ROOM_44101_FAILURE_2'
            }
        }],
        'fishPool': 44101,
        'playingTime': 120,
        'rank.rewards': [{
            'desc': 'ID_ROOM_44101_RANK_DESC_1',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 1,
                'start': 1
            },
            'rewards': [{
                'count': 5000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_2',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 2,
                'start': 2
            },
            'rewards': [{
                'count': 2000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_3',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 3,
                'start': 3
            },
            'rewards': [{
                'count': 1000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_4',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 6,
                'start': 4
            },
            'rewards': [{
                'count': 8,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_5',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 10,
                'start': 7
            },
            'rewards': [{
                'count': 5,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_6',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 15,
                'start': 11
            },
            'rewards': [{
                'count': 3,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_7',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 20,
                'start': 16
            },
            'rewards': [{
                'count': 2,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_8',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 30,
                'start': 21
            },
            'rewards': [{
                'count': 1,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_9',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 50,
                'start': 31
            },
            'rewards': [{
                'count': 5000,
                'itemId': 'user:chip'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_10',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 100,
                'start': 51
            },
            'rewards': [{
                'count': 2000,
                'itemId': 'user:chip'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_11',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 9999,
                'start': 101
            },
            'rewards': [{
                'count': 600,
                'itemId': 'user:chip'
            }]
        }],
        'rule': 'ID_ROOM_44101_RULE_1',
        'stages': [{
            'name': 'ID_ROOM_44101_STAGES_NAME',
            'rise.user.count': 10000,
            'seat.principles': 5,
            'type': 2
        }],
        'start': {
            'close.times': 360,
            'fee.type': 1,
            'list.matchtimes': [10],
            'maxGameTimes': 30,
            'maxplaytime': 600,
            'prepare.times': 0,
            'reward.times': 180,
            'signin.times': 0,
            'start.speed': 5,
            'table.times': 600,
            'times': {
                'days': {
                    'count': 365,
                    'first': '',
                    'interval': '1d'
                },
                'times_in_day': {
                    'count': 800,
                    'first': '9:00',
                    'interval': 10
                }
            },
            'type': 3,
            'user.maxsize': 300,
            'user.minsize': 1,
            'user.next.group': 0
        },
        'table.seat.count': 1,
        'tips': {
            'infos': ['ID_ROOM_44101_TIPS_INFOS'],
            'interval': 5
        }
    },
    'maxCoin': -1,
    'maxGunLevel': 2115,
    'maxLevel': 999,
    'maxSkillLevel': 12,
    'minCoin': -1,
    'minGunLevel': 2101,
    'minLevel': 15,
    'multiple': 1,
    'name': 'ID_ROOM_NAME_44101',
    'robotUserMaxCount': 500,
    'sceneName': 'string_44101',
    'showLevel': 1,
    'skill_item': {
        '14119': {
            'cd_time': 1,
            'count_0': 1,
            'count_1': 100,
            'duration': 10,
            'name': 14119,
            'play_times': 444,
            'replace_name': 1137
        },
        '14120': {
            'cd_time': 18,
            'count_0': 1,
            'count_1': 200,
            'duration': 18,
            'name': 14120,
            'play_times': 444,
            'replace_name': 1137
        }
    },
    'tableConf': {
        'fishGroupsName': 'string_44101',
        'gameMode': 1,
        'maxSeatN': 4
    },
    'typeName': 'fish_time_point_match',
    'gameTableCount': 10,
    'gameServerCount': 1
}),
441011001: FTRoomDefine(bigRoomId = 44101, parentId = 441011000, roomId = 441011001, gameId = 44, configId = 101, controlId = 1, shadowId = 1, serverId = GT0044001_999, tableCount = 10, shadowRoomIds = [], configure = {
    'fishPool': 44101,
    'hasrobot': 1,
    'isMatch': 1,
    'matchConf': {
        'bullet': 5000,
        'desc': '',
        'discountTime': ['2018-10-20 00:00:00', '2018-10-23 23:59:59'],
        'fees': [{
            'count': 50,
            'itemId': 'item:3106',
            'params': {
                'failure': 'ID_ROOM_44101_FAILURE_1'
            }
        }, {
            'count': 33,
            'itemId': 'item:3106',
            'params': {
                'failure': 'ID_ROOM_44101_FAILURE_2'
            }
        }],
        'fishPool': 44101,
        'playingTime': 120,
        'rank.rewards': [{
            'desc': 'ID_ROOM_44101_RANK_DESC_1',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 1,
                'start': 1
            },
            'rewards': [{
                'count': 5000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_2',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 2,
                'start': 2
            },
            'rewards': [{
                'count': 2000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_3',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 3,
                'start': 3
            },
            'rewards': [{
                'count': 1000,
                'itemId': 'user:coupon'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_4',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 6,
                'start': 4
            },
            'rewards': [{
                'count': 8,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_5',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 10,
                'start': 7
            },
            'rewards': [{
                'count': 5,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_6',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 15,
                'start': 11
            },
            'rewards': [{
                'count': 3,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_7',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 20,
                'start': 16
            },
            'rewards': [{
                'count': 2,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_8',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 30,
                'start': 21
            },
            'rewards': [{
                'count': 1,
                'itemId': 'item:1301'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_9',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 50,
                'start': 31
            },
            'rewards': [{
                'count': 5000,
                'itemId': 'user:chip'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_10',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 100,
                'start': 51
            },
            'rewards': [{
                'count': 2000,
                'itemId': 'user:chip'
            }]
        }, {
            'desc': 'ID_ROOM_44101_RANK_DESC_11',
            'message': 'ID_CONFIG_RANKING_MAIL_MSG_44101',
            'ranking': {
                'end': 9999,
                'start': 101
            },
            'rewards': [{
                'count': 600,
                'itemId': 'user:chip'
            }]
        }],
        'rule': 'ID_ROOM_44101_RULE_1',
        'stages': [{
            'name': 'ID_ROOM_44101_STAGES_NAME',
            'rise.user.count': 10000,
            'seat.principles': 5,
            'type': 2
        }],
        'start': {
            'close.times': 360,
            'fee.type': 1,
            'list.matchtimes': [10],
            'maxGameTimes': 30,
            'maxplaytime': 600,
            'prepare.times': 0,
            'reward.times': 180,
            'signin.times': 0,
            'start.speed': 5,
            'table.times': 600,
            'times': {
                'days': {
                    'count': 365,
                    'first': '',
                    'interval': '1d'
                },
                'times_in_day': {
                    'count': 800,
                    'first': '9:00',
                    'interval': 10
                }
            },
            'type': 3,
            'user.maxsize': 300,
            'user.minsize': 1,
            'user.next.group': 0
        },
        'table.seat.count': 1,
        'tips': {
            'infos': ['ID_ROOM_44101_TIPS_INFOS'],
            'interval': 5
        }
    },
    'maxCoin': -1,
    'maxGunLevel': 2115,
    'maxLevel': 999,
    'maxSkillLevel': 12,
    'minCoin': -1,
    'minGunLevel': 2101,
    'minLevel': 15,
    'multiple': 1,
    'name': 'ID_ROOM_NAME_44101',
    'robotUserMaxCount': 500,
    'sceneName': 'string_44101',
    'showLevel': 1,
    'skill_item': {
        '14119': {
            'cd_time': 1,
            'count_0': 1,
            'count_1': 100,
            'duration': 10,
            'name': 14119,
            'play_times': 444,
            'replace_name': 1137
        },
        '14120': {
            'cd_time': 18,
            'count_0': 1,
            'count_1': 200,
            'duration': 18,
            'name': 14120,
            'play_times': 444,
            'replace_name': 1137
        }
    },
    'tableConf': {
        'fishGroupsName': 'string_44101',
        'gameMode': 1,
        'maxSeatN': 4
    },
    'typeName': 'fish_time_point_match',
    'gameTableCount': 10,
    'gameServerCount': 1
})
}
