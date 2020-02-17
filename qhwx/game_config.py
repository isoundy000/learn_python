# -*- coding:utf-8 -*-

import os

from apps.commands.config_update import check_all_files
from apps.net.web.utils.import_lib import import_by_name

noticelamp = {}
banquet = {}
skill = {}
beaconbossrank = {}
mail = {}
prisoner = {}
store = {}
childrentalent = {}
guide = {}
story = {}
chapter = {}
task = {}
event = {}
judgement = {}
box = {}
cg = {}
fortune = {}
maskword = {}
leaguefightreward = {}
cardgold = {}
npc = {}
moneytreerank2 = {}
redbag = {}
signin = {}
womenexp = {}
advancementweekgift = {}
marketposition = {}
activitypurchasegift = {}
advancement = {}
leaguedailytask = {}
activity1 = {}
activitynewfund = {}
leagueexp = {}
moneytree = {}
openmodule = {}
moneytreestage = {}
cardknowledge = {}
marketpasserby = {}
activityfund = {}
womenskill = {}
activity = {}
signingroup = {}
moneytreeshop = {}
resourcestring = {}
vipstore = {}
activitynewpurchasegift = {}
marketprosperity = {}
leaguebuild = {}
sevenday = {}
moneytreeitem = {}
moneytreeexchange = {}
card = {}
affairs = {}
fashion = {}
womenskillup = {}
gameparams = {}
combination = {}
giftget = {}
cardladder = {}
vip = {}
childrengraduate = {}
womentitle = {}
gossip = {}
activity2 = {}
harvest = {}
leaguetechnology = {}
dailytaskbox = {}
banquetgoto = {}
womencomfortable = {}
marketbuildingup = {}
leaguebox = {}
pve = {}
gift = {}
robot = {}
cardofficer = {}
moneytreerank1 = {}
beaconstrengthen = {}
recharge = {}
beacon = {}
debatematch = {}
women = {}
exp = {}
storegoods = {}
debatelottery = {}
item = {}
storyreward = {}
hit = {}
appearance = {}

path = os.path.join(os.path.dirname(os.path.join(__file__)), "config_file")
dic_file_names = check_all_files(path)
for name, name_path in dic_file_names:
    py_name = name.split(".")[0]
    if py_name not in locals().keys():
        continue
    exec("%s = %s" % (py_name, import_by_name("config.config_file.%s.%s" % (py_name, py_name))))
