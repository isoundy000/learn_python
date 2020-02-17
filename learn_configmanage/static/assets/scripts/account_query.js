/**
 * Created by liuzhaoyang on 15/9/7.
 */

handleDatePickers();
handleTimePickers();
$("#start_date").val(getNowFormatDate(1));
$("#end_date").val(getNowFormatDate(0));

$("#usegold_start_date").val(getNowFormatDate(1));
$("#usegold_end_date").val(getNowFormatDate(0));

$("#start_time").val("00:00:00");
$("#end_time").val("23:59:59");

getPartnerData($("#select_channel"));
var $select_gameserver = $("#select_gameserver");
var $select_game_query = $("#select_game_query");
var $use_gold_server = $("#use_gold_server");
var $select_chujian_gameserver = $("#select_chujian_gameserver");
var $role_info_button_txt = $('#role_info_button_txt');

getGameServerData($select_gameserver, 1);
getGameServerData($select_game_query, 2);
getGameServerData($use_gold_server, 1);
getGameServerData($select_chujian_gameserver, 1);
var server_id = 0;

var CONFIG = ["general","pet2_attr","pet2_fragment","equip","props","soul","copy","star_copy","map", "star_map"];
var GLOBAL_DATA = {};

var QUALITY_CSS = {
    2: "green",
    3: "blue",
    4: "purple",
    5: "yellow",
    6: "red"
};
var GENERAL_QUALITY = {
    2:"绿色",
    3:"蓝色",
    4:"紫色",
    5:"橙色",
    6: "红色"
};


var USE_GOLD_TYPE = {
    "begin7day": "7日礼包",
    "recruit": "武将招募",
    "blackmarket_refresh": "黑市商店刷新",
    "blackmarkguy": "黑市商店购买",
    "mozhaoshop": "蛋蛋商店",
    "mysteryshop_refresh": "神魂商店",
    "trial": "冠军试炼商店",
    "shop": "道具商城",
    "activity_q": "时装商城",
    "fashiondress_buy": "时装商城购买",
    "protagonist_fashion_reset": "时装商城重置",
    "giftbag": "礼包商城",
    "encounter_exp": "高人指点",
    "encounter_general": "奇遇武将",
    "encounter_search": "卷宗寻宝",
    "encounter_shop": "奇遇道具",
    "copykillreset": "重置副本",
    "coincopybuy": "银币副本挑战次数",
    "expcopybuy": "经验副本挑战次数",
    "stonecopybuy": "锻造石副本挑战次数",
    "zhenfucopybuy": "阵符副本挑战次数",
    "upstarcopybuy": "升星石副本挑战次数",
    "stamina": "购买体力",
    "energy": "购买杀气",
    "athletics": "竞技场",
    "mieshendianmodupcdclear": "灭神殿清除CD",
    "mieshendianreset": "灭神殿重置",
    "watchstarEx": "观星台",
    "watchstar_change": "观星台兑换",
    "friendcopy": "好友副本",
    "worldboss1": "浴火重生",
    "penglai3cardopen": "蓬莱仙岛翻牌",

    "penglai3dice": "蓬莱仙岛随机",
    "penglai3reset": "蓬莱仙岛重置",
    "kingmanbuy": "王的男人",
    "patrol": "天庭银座",
    "overpasschangeboss": "过关斩将",
    "ovserpassbuy": "过关斩将购买",
    "generalfoster": "伙伴培养",
    "wingactivation": "翅膀激活",
    "equipbaptizepreview": "装备洗练",
    "general_reset": "伙伴重生",
    "equip_reset": "装备重生",
    "gangcreate": "创建公会",
    "gangpray": "公会拜神",
    "gangsetname": "公会改名",
    "inspiregold": "公会战鼓舞",
    "petpassiveskillreset": "技能重置",
    "soulhunt": "猎命",
    "instrumentforgepreview": "法宝锻造",
    "cornucopia_buy": "聚宝盆",
    "gemdiscountshop": "珍品折扣兑换",
    "gemdiscountshop1": "珍品折扣兑换1",
    "gemdiscountshop2": "珍品折扣兑换2",
    "gemdiscountshop3": "珍品折扣兑换3",
    "growplan": "成长计划",
    "limit_buy": "限时商店购买",
    "limit_refresh": "限时商店刷新",
    "vip_welfare_exchange": "vip福利",
    "olddriver": "老司机",
    "dragonboatluckdraw": "大转盘",
    "spinampwin": "老虎鸡",
    "god_down": "八戒圆梦",
    "timegift": "限时礼包",
    "trigger_gift": "触发礼包"
};

$('.dropdown-menu a').click(function () {
    $role_info_button_txt.text($(this).text());
     $select_gameserver.change();
});

$select_gameserver.change(function () {
    "use strict";
    server_id = $(this).val();
    $('#role_info').typeahead('destroy');
    if ($role_info_button_txt.text() === '角色名称') {
        $('#role_info').typeahead({
            source: function (query, process) {
                return $.ajax({
                    url: '/get/role/like_name',
                    type: 'get',
                    dataType: 'json',
                    data: {server_id: server_id, role_name: query},
                    success: function (result) {
                        return process(result);
                    }
                });
            }
        });
    }
});
$select_gameserver.change();


$select_game_query.on("change", function(e){
    e.preventDefault();
    var game_id = $(this).val();
    var div_role = $("#div_role");
    if(game_id == 0){
        div_role.addClass("hidden");
        $("#recharge_role_id").val("");
    }
    else{
        div_role.removeClass("hidden");
    }
});

$select_game_query.change();

$("#btn_usegold").on("click", function(e){
    e.preventDefault();
    var server_id = $("#use_gold_server").val();
    var role_id = $("#usegold_role_id").val();
    var start_date = $("#usegold_start_date").val();
    var start_time = $("#start_time").val();
    var end_date = $("#usegold_end_date").val();
    var end_time = $("#end_time").val();
    var start = start_date + " " + start_time;
    var end = end_date + " " + end_time;
    var ajax_source = "/queryrolegold";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "opt",
            "sClass": "center",
            "sTitle": "操作类型"
        },
        {
            "mDataProp": "num",
            "sClass": "center",
            "sTitle": "数量"
        },
        {
            "mDataProp": "time",
            "sClass": "center",
            "sTitle": "时间"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html2 = USE_GOLD_TYPE[aData.opt];
        $('td:eq(1)', nRow).html(str_html2);
        return nRow;
    };
    var data = {
        server_id: server_id, role_id: role_id, start: start, end: end, query_type: $('#query_type_gold').val()
    };
    dataTablePage($("#usegold_table"), aoColumns, ajax_source, data, false, fnRowCallback);
});


var rechargeValidation = function () {
    var form1 = $('#recharge_query_form');
    var rules = {
        // recharge_role_id: {
        //     required: true
        // }
    };
    var messages = {
        // recharge_role_id: {
        //     required: "请输入角色编号或名称"
        // }
    };
    var submitFunc = function () {
        var select_game_query = $("#select_game_query").val();
        var start_date = $("#start_date").val();
        var end_date = $("#end_date").val();
        var recharge_role_id = $("#recharge_role_id").val();
        var select_channel = $("#select_channel").val();
        var ajax_source = "/queryrechargeinfo";
        var aoColumns = [
            {
                "mDataProp": "id",
                "sClass": "center",
                "sTitle": "充值编号"
            },
            {
                "mDataProp": "uid",
                "sClass": "center",
                "bVisible": false
            },
            {
                "mDataProp": "p_name",
                "sClass": "center",
                "sTitle": "渠道"
            },
            {
                "mDataProp": "channel_name",
                "sClass": "center",
                "bVisible": false
            },
            {
                "mDataProp": "gid",
                "sClass": "center",
                "bVisible": false
            },

            {
                "mDataProp": "s_name",
                "sClass": "center",
                "sTitle": "区服"
            },
            {
                "mDataProp": "rid",
                "sClass": "center",
                "sTitle": "角色ID"
            },
            {
                "mDataProp": "r_name",
                "sClass": "center",
                "sTitle": "角色名称"
            },
            {
                "mDataProp": "vip",
                "sClass": "center",
                "sTitle": "VIP等级"
            },
            {
                "mDataProp": "cid",
                'sClass': 'center',
                "sTitle": "充值档"
            },
            {
                "mDataProp": "total",
                'sClass': 'center',
                "sTitle": "充值金额"
            },
            {
                "mDataProp": "result",
                "sClass": "center",
                "sTitle": "状态"
            },
            {
                "mDataProp": "createtime",
                "sClass": "center",
                "sTitle": "创建时间"
            }
        ];
        var fnRowCallback = function (nRow, aData) {
            var str_html2 = aData.gid + "区:" + aData.s_name;
            $('td:eq(2)', nRow).html(str_html2);
            var str_html = "";
            if (aData.result == "yes") {
                str_html = "<span class='badge badge-success'>成功</span>";
                // str_html3 = "<button onclick=\"query_person_recharge(this)\" class=\"btn default btn-xs blue\">详细</button>"
            }
            else {
                str_html = "<span class='badge badge-info'>准备</span>";
            }
            $('td:eq(8)', nRow).html(str_html);
            // $('td:eq(8)', nRow).html(str_html3);
            return nRow;
        };
        var data = {
            select_channel: select_channel, select_game_query: select_game_query, start_date: start_date,
            end_date: end_date, recharge_role_id: recharge_role_id
        };
        dataTablePage($("#recharge_table"), aoColumns, ajax_source, data, false, fnRowCallback);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
rechargeValidation();



var query_person_recharge = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#recharge_table").dataTable().fnGetData(nRoW);
    var id = data["id"];
    var channel_name = data["channel_name"];
    var query_date = $("#query_date").val();
    var select_game_query = $("#select_game_query").val();
    $.ajax({
        type: 'get',
        url: '/queryrechargedetails',
        data: {
            id: id,
            channel_name: channel_name
        },
        dataType: 'JSON',
        success: function (data) {
            var str_title = "";
            var str_html = "<tr>";
            if (data["data"] != null){
                for(var d=0; d<data["name"].length; d++){
                str_title += "<th>" + data["value"][d] + "</th>";
                str_html += "<td>" + data["data"][data["name"][d]] + "</td>";
                }
                str_title += "<th>操作</th>";
                str_html += "<td><button class='btn btn-xs green' onclick=\"recharge_validate(" + id + "," + "'" + channel_name + "')\">"  + "校验</button></td>";
                $("#recharge_title").html(str_title);
                $("#recharge_list").html(str_html);
                $("#recharge_modal").modal("show");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "未查到数据.");
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
};


function recharge_validate(rid, channel_name){
    $.ajax({
        type: 'get',
        url: '/validatechannelrecharge',
        data: {
            order_id: rid,
            channel_name: channel_name
        },
        dataType: 'JSON',
        success: function (data) {
            if (data.status == "success"){
                Common.alert_message($("#validate_modal"), 1, "校验成功.");

            }
            else if (data.status == "fail"){
                Common.alert_message($("#validate_modal"), 0, "校验失败.");
            }
            else if (data.status == "no"){
                Common.alert_message($("#validate_modal"), 0, "渠道未开通查询接口.");
            }
            setTimeout(function(){
                $("#validate_modal").modal("hide");
            }, 2000);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
}



var query_json = function(config){
    for (var i=0; i < config.length; i++){
        if(config[i] in GLOBAL_DATA == false) {
            var success = function (data) {
                GLOBAL_DATA[config[i]] = data[config[i]];
            };
            var data = {
                server_id: server_id,
                type: JSON.stringify([config[i]])
            };

            my_ajax(true, '/queryjsondatabyserver', 'get', data, false, success);
        }
    }
};

var accountValidation = function () {
    var form1 = $('#account_form');
    var rules = {
        account: {
            required: true
        }
    };
    var messages = {
        account: {
            required: "请输入账号名"
        }
    };
    var submitFunc = function () {
        var account = $("#account").val();
        var data = {
            account: account
        };
        var success = function(data){
            var str_html = "";
            if (data.length != 0){
                for(var i=0; i<data.length; i++){
                    str_html += "<tr>";
                    str_html += "<td>" + data[i]["uid"] + "</td>";
                    str_html += "<td>" + data[i]["account"] + "</td>";
                    str_html += "<td>" + data[i]["gid"] + "区:" + data[i]["gamename"] + "</td>";
                    str_html += "<td>" + data[i]["recharge"] + "</td>";
                    str_html += "<td>" + data[i]["rid"] + "</td>";
                    str_html += "<td>" + data[i]["name"] + "</td>";
                    str_html += "<td>" + data[i]["level"] + "</td>";
                    str_html += "<td>" + data[i]["vip"] + "</td>";
                    str_html += "<td>" + data[i]["gold"] + "</td>";
                    str_html += "<td>" + data[i]["coin"] + "</td>";
                    str_html += "<td>" + data[i]["createtime"] + "</td>";
                    str_html += "</tr>";
                }
            }
            else{
                str_html += "<tr>";
                str_html += '<td colspan="10" class="text-center"><span class="label label-danger">无此账号数据</span></td>';
                str_html += '</tr>';
            }
            $("#account_list").html(str_html);
        };
        my_ajax(true, "/queryuid", "get", data, false, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
accountValidation();


var roleValidation = function () {
    var form1 = $('#role_form');
    var rules = {
        role_info: {
            required: true
        }
    };
    var messages = {
        role_info: {
            required: "请输入角色编号或名称"
        }
    };
    var submitFunc = function () {
        var role_info = $("#role_info").val();
        var page_content = $('.page-content');
        var query_type = $role_info_button_txt.text() === '角色编号' ? 'role_id' : 'role_name';
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/queryrole2',
            data: {server_id: server_id, role_info: role_info, query_type: query_type},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                $("#a_role").parent("li").addClass("active");
                $("#tab_role").addClass("active");

                $("#a_role").parent("li").nextAll().each(function(){
                    if ($(this).hasClass("active")) {
                        $(this).removeClass("active");
                        var tab_name = $(this).children("a").attr("id");
                        $("#tab_" + tab_name + "_1").removeClass("active");
                    }
                });
                var str_info = "<tr>";
                if (data['status'] === 'success') {
                    str_info += "<td>" + data["uid"] + "</td>";
                    str_info += "<td>" + data["channel_name"] + "</td>";
                    str_info += "<td>" + data["account"] + "</td>";
                    str_info += "<td>" + data["id"] + "</td>";
                    str_info += "<td>" + data["name"] + "</td>";
                    str_info += "<td>" + data["level"] + "</td>";

                    str_info += "<td>" + data["vip"] + "</td>";
                    str_info += "<td>" + data["recharge"] + "</td>";
                    str_info += "<td>" + data["gold"] + "</td>";
                    str_info += "<td>" + data["coin"] + "</td>";
                    str_info += "<td>" + data["createtime"] + "</td>";
                    str_info += "<td>" + data["lastlogin"] + "</td>";
                    str_info += "</tr>";
                    $("#role_id").val(data["id"]);
                }
                else {
                    str_info += '<td colspan="9" class="text-center"><span class="label label-danger">无此角色编号数据</span></td>';
                    str_info += '</tr>';
                }

                $("#role_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        })
    };
    commonValidation(form1, rules, messages, submitFunc);
};
roleValidation();


var validate_role = function(){
    var role_id = $("#role_id").val();
    var tag = true;
    if (role_id == "" || role_id == null || role_id == undefined)
        tag = false;
    return tag;
};


//主角
$('#role_1').bind("click",function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if (v_str) {
        query_json(["general", "pet2_attr", "pet2_fragment"]);
        $("#role_1").attr("href", "#tab_role_1");
        var GENERAL_JSON = GLOBAL_DATA["general"];
        var PET_JSON = GLOBAL_DATA["pet2_attr"];
        var PET_FRAGMENT_JSON = GLOBAL_DATA["pet2_fragment"];
        $.ajax({
            type: 'get',
            url: '/queryLead',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                var str_g = "";
                var str_p = "";
                var str_pf = "";
                if (data.length != 0) {
                    var cid = data['cid'];
                    var quality = GENERAL_JSON[cid]["quality"];
                    str_g += "<tr>";
                    str_g += "<td>";
                    str_g += "<span class=\"btn default btn-xs " + QUALITY_CSS[quality] + "\">";

                    var name = '';
                    if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'shou') {
                        name = '魔王'
                    } else if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'nan') {
                        name = '男主'
                    } else if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'nv') {
                        name = '女主'
                    }
                    str_g += name + "</span></td>";
                    str_g += "<td>" + GENERAL_QUALITY[quality] + "</td>";
                    str_g += "</tr>";

                    var pet = data['pet'];
                    for (var p in pet){
                        var pet_rank = pet[p]['level2'];
                        var pet_cid = pet[p]['cid'];
                        str_p += "<tr>";
                        str_p += "<td>" + PET_JSON[pet_cid][pet_rank]['name'] + "</td>";
                        str_p += "<td>" + pet[p]['level1'] + "</td>";
                        str_p += "<td>" + pet[p]['level2'] + "</td>";
                        str_p += "</tr>";
                    }

                    var pet_fragment = data['pet_fragment'];
                    for (var pf in pet_fragment){
                        var pet_fragment_cid = PET_FRAGMENT_JSON[pet_fragment[pf]['cid']]['petid'];
                        str_pf += "<tr>";
                        str_pf += "<td>" + PET_JSON[pet_fragment_cid][0]['name'] + "</td>";
                        str_pf += "<td>" + pet_fragment[pf]['num'] + "</td>";
                        str_pf += "</tr>";
                    }
                }
                $('#role2_list').html(str_g);
                $('#devil_list').html(str_p);
                $('#devil_fragment_list').html(str_pf);
            },
            error: function () {
            }
        })
    } else {
        $("#role_1").attr("href", "#");
    }
});

//武将
$('#general').bind("click",function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            query_json(["general", "equip"]);
            $("#general").attr("href", "#tab_general_1");
            var GENERAL_JSON = GLOBAL_DATA["general"];
            var EQUIP_JSON = GLOBAL_DATA["equip"];
            $.ajax({
                    type: 'get',
                    url: '/querygeneral2',
                    data: {server_id: server_id, role_id: role_id},
                    dataType: 'JSON',
                    success: function (data) {
                        var str_g = "";
                        var general_arr = {};
                        if (data.length != 0) {
                            for (var general in data){
                                var g_data = data[general];
                                var cid = g_data['cid'];
                                var quality = GENERAL_JSON[cid]["quality"];
                                var general_name = GENERAL_JSON[cid].hasOwnProperty("name") ? GENERAL_JSON[cid]["name"] : GENERAL_JSON[cid]["name_CN"]
                                str_g += "<tr>";
                                // 名称
                                str_g += "<td>";
                                str_g += "<span class=\"btn default btn-xs " + QUALITY_CSS[quality] + "\">";
                                general_arr[g_data['id']] = {
                                    "name": general_name,
                                    "quality": QUALITY_CSS[quality]
                                };
                                str_g += general_name + "</span></td>";

                                //位置
                                var addr = '';
                                if (g_data['addr'] == 2){
                                    addr = '上阵'
                                }else if (g_data['addr'] == 1){
                                    addr = '助阵'
                                }
                                str_g += "<td>" + addr + "</td>";

                                //等级
                                str_g += "<td>" + g_data['level1'] + "</td>";
                                str_g += "<td>" + g_data['level2'] + "</td>";

                                //碎片数量
                                if(GENERAL_JSON[cid]["name"]=='主角'){
                                    str_g += "<td>" + 0 + "</td>";
                                }else{
                                    str_g += "<td>" + g_data['num'] + "</td>";
                                }

                                //装备
                                var weapon = '';
                                var armor = '';
                                var accessory = '';
                                var head = '';
                                var treasure = '';
                                var horse = '';

                                if(g_data["weapon"]!=null){
                                    weapon = EQUIP_JSON[g_data["weapon"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["weapon"]]['name'] : EQUIP_JSON[g_data["weapon"]]['name_CN']
                                }
                                if(g_data["armor"]!=null){
                                    armor = EQUIP_JSON[g_data["armor"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["armor"]]['name'] : EQUIP_JSON[g_data["armor"]]['name_CN']
                                }
                                if(g_data["accessory"]!=null){
                                    accessory = EQUIP_JSON[g_data["accessory"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["accessory"]]['name'] : EQUIP_JSON[g_data["accessory"]]['name_CN']
                                }
                                if(g_data["head"]!=null){
                                    head = EQUIP_JSON[g_data["head"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["head"]]['name'] : EQUIP_JSON[g_data["head"]]['name_CN']
                                }
                                if(g_data["treasure"]!=null){
                                    treasure = EQUIP_JSON[g_data["treasure"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["treasure"]]['name'] : EQUIP_JSON[g_data["treasure"]]['name_CN']
                                }
                                if(g_data["horse"]!=null){
                                    horse = EQUIP_JSON[g_data["horse"]].hasOwnProperty('name') ? EQUIP_JSON[g_data["horse"]]['name'] : EQUIP_JSON[g_data["horse"]]['name_CN']
                                }
                                str_g += "<td>" + weapon + "</td>";
                                str_g += "<td>" + armor + "</td>";
                                str_g += "<td>" + accessory + "</td>";
                                str_g += "<td>" + head + "</td>";
                                str_g += "<td>" + treasure + "</td>";
                                str_g += "<td>" + horse + "</td>";
                                str_g += "</tr>";
                            }
                            $('#generals_list').html(str_g);
                        }

                    },
                    error : function () {
                    }
            })
        }else{
            $("#general").attr("href", "#");
        }
});

//装备
$('#equip').bind('click', function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str) {
        query_json(["equip"]);
        $("#equip").attr("href", "#tab_equip_1");
        var EQUIP_JSON = GLOBAL_DATA["equip"];
        $.ajax({
            type: 'get',
            url: '/queryequip2',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                var str_e = "";
                if (data.length != 0) {
                    for (var e = 0; e < data.length; e++) {
                        str_e += "<tr>";
                        str_e += "<td>";
                        var quality = EQUIP_JSON[data[e].cid]["quality"];
                        str_e += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                        str_e += EQUIP_JSON[data[e].cid].hasOwnProperty('name') ? EQUIP_JSON[data[e].cid]['name'] : EQUIP_JSON[data[e].cid]['name_CN'] + "</span></td>";
                        str_e += "<td>" + data[e]["level1"] + "</td>";
                        str_e += "<td>" + data[e]["level2"] + "</td>";
                        str_e += "<td>" + data[e]["exp2"] + "</td>";
                        str_e += "</tr>";
                    }
                    $("#equip_list").html(str_e);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    } else {
        $("#equip").attr("href", "#");
    }
});

//道具
$("#props").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        query_json(["props"]);
        $("#props").attr("href", "#tab_props_1");
        var PROPS_JSON = GLOBAL_DATA["props"];
        $.ajax({
            type: 'get',
            url: '/queryprops2',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        console.log(data[p].num);
                        if (data[p].num != 0) {
                            str_p += "<tr>";
                            str_p += "<td>";
                            str_p += PROPS_JSON[data[p].cid].hasOwnProperty('name') ? PROPS_JSON[data[p].cid]['name'] : PROPS_JSON[data[p].cid]['name_CN'] + "</td>";
                            str_p += "<td>" + data[p].num + "</td>";
                            str_p += "</tr>";
                        }

                    }
                    $("#props_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    } else {
        $("#props").attr("href", "#");
    }
});

//命格
$("#soul").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        query_json(["soul"]);
        $("#soul").attr("href", "#tab_soul_1");
        var SOUL_JSON = GLOBAL_DATA["soul"];
        $.ajax({
            type: 'get',
            url: '/querysoul2',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_s = "";
                    for (var s = 0; s < data.length; s++) {
                        str_s += "<tr>";
                        str_s += "<td>";
                        var quality = SOUL_JSON[data[s].cid]["quality"];
                        str_s += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                        str_s += SOUL_JSON[data[s].cid].hasOwnProperty('name') ? SOUL_JSON[data[s].cid]['name'] : SOUL_JSON[data[s].cid]['name_CN'] + "</span></td>";
                        str_s += "<td>" + data[s]["level"] + "</td>";
                        str_s += "<td>" + data[s]["exp"] + "</td>";
                        str_s += "</tr>";
                    }
                    $("#soul_list").html(str_s);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    } else {
        $("#soul").attr("href", "#");
    }
});

//副本
$("#copy").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#copy").attr("href", "#tab_copy_1");
        query_json(["map", "copy"]);
        query_copy(role_id, $("#copy_list"));
    } else {
        $("#copy").attr("href", "#");
    }
});

//精英副本
$("#starcopy").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $(this).attr("href", "#tab_star_copy_1");
        query_json(["star_map", "star_copy"]);
        query_general_copy(role_id, $("#starcopy_list"));
    } else {
        $(this).attr("href", "#");
    }
});



var query_copy = function(role_id, div){
    $.ajax({
        type: 'get',
        url: '/querycopyinfo',
        data: {game_id: server_id, role_id: role_id},
        dataType: 'JSON',
        success: function (data) {
            var str_info = "";
            var copy = GLOBAL_DATA["copy"];
            var map = GLOBAL_DATA["map"];
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + (map[data[i]["map"]].hasOwnProperty('name') ? map[data[i]["map"]]['name'] : map[data[i]["map"]]['name_CN']) + "</td>";

                str_info += "<td>" + (copy[data[i]["map"]][data[i]["point"]].hasOwnProperty('name') ? copy[data[i]["map"]][data[i]["point"]]['name'] : copy[data[i]["map"]][data[i]["point"]]['name_CN']) + "</td>";
                var star = data[i]["star"];
                str_info += "<td>" ;
                for(var j = 0; j < star; j++){
                    str_info += "<i class='fa fa-star'></i>";
                }
                for(var k=3; k > star; k--){
                    str_info += "<i class='fa fa-star-o'></i>";
                }
                str_info += "</td>";
                str_info += "</tr>";
            }
            div.html(str_info);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
};


var query_general_copy = function(role_id, div){
    $.ajax({
        type: 'get',
        url: '/querygeneralcopyinfo',
        data: {game_id: server_id, role_id: role_id},
        dataType: 'JSON',
        success: function (data) {
            var str_info = "";
            var copy = GLOBAL_DATA["star_copy"];
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + (GLOBAL_DATA["star_map"][data[i]["map"]].hasOwnProperty('name') ? GLOBAL_DATA["star_map"][data[i]["map"]]['name'] : GLOBAL_DATA["star_map"][data[i]["map"]]['name_CN']) + "</td>";

                str_info += "<td>" + (copy[data[i]["map"]][data[i]["point"]].hasOwnProperty('name') ? copy[data[i]["map"]][data[i]["point"]]['name'] : copy[data[i]["map"]][data[i]["point"]]['name_CN']) + "</td>";
                str_info += "<td>";
                if (data[i]["star"] == -1){
                    str_info += "失败";
                }
                else{
                    str_info += "成功";
                }
                str_info += "</td>";
                str_info += "</tr>";
            }
            div.html(str_info);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
};

//战斗力
var POWER_TYPE = {
    "equip": "装备",
    "general": "武将",
    "pet": "魔宠",
    "soul": "命格",
    "treasure": "宝物"
};

$("#power").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
            $("#power").attr("href", "#tab_power_1");
            var role_id = $("#role_id").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/getrolepower',
                    data: {server_id: server_id, role_id: role_id},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content);
                        console.log(data);
                        var str_info = "";
                        var data_set = [];
                        for (var p in POWER_TYPE) {
                            str_info += "<tr>";
                            str_info += "<td>" + POWER_TYPE[p] + "</td>";
                            str_info += "<td>" + data[p] + "</td>";
                            str_info += "</tr>";
                            var temp = {
                                label: POWER_TYPE[p],
                                data: data[p] / data["total"] * 100
                            };
                            data_set.push(temp);
                        }
                        str_info += "<tr class=\"success\">";
                        str_info += "<td>总战力</td>";
                        str_info += "<td>" + data["total"] + "</td>";
                        str_info += "</tr>";

                        drawPieChart($("#chart_power"), data_set);
                        $("#power_list").html(str_info);
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        }else{
            $("#power").attr("href", "#");
        }
});

var accountChujianValidation = function () {
    var form1 = $('#chujian_role_form');
    var rules = {
        account: {
            required: true
        }
    };
    var messages = {
        account: {
            required: "请输入角色信息"
        }
    };
    var submitFunc = function () {
        var server_id = $("#select_chujian_gameserver").val();
        var role_info = $("#chujian_role_info").val();
        var data = {
            server_id: server_id,
            role_info: role_info
        };
        var success = function(data){
            var str_html = "";
            if (data.length != 0){
                for(var i=0; i<data.length; i++){
                    str_html += "<tr>";
                    str_html += "<td>" + data[i]["uid"] + "</td>";
                    str_html += "<td>" + data[i]["account"] + "</td>";
                    str_html += "<td>" + data[i]['chujianuser_name'] + "</td>";
                    str_html += "<td>" + data[i]["gid"] + "区:" + data[i]["gamename"] + "</td>";
                    str_html += "<td>" + data[i]["recharge"] + "</td>";
                    str_html += "<td>" + data[i]["rid"] + "</td>";
                    str_html += "<td>" + data[i]["name"] + "</td>";
                    str_html += "<td>" + data[i]["level"] + "</td>";
                    str_html += "<td>" + data[i]["vip"] + "</td>";
                    str_html += "<td>" + data[i]["gold"] + "</td>";
                    str_html += "<td>" + data[i]["coin"] + "</td>";
                    str_html += "<td>" + data[i]["createtime"] + "</td>";
                    str_html += "</tr>";
                }
            }
            else{
                str_html += "<tr>";
                str_html += '<td colspan="10" class="text-center"><span class="label label-danger">无此账号数据</span></td>';
                str_html += '</tr>';
            }
            $("#chujian_account_list").html(str_html);
        };
        my_ajax(true, "/query/chujian/player", "get", data, false, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
accountChujianValidation();


var format_time_range_input = function (e_object) {
    "use strict";
    e_object.daterangepicker({
        "opens": "center",
        "drops": "down",
        "autoUpdateInput": false,
        "locale": {'format': 'YYYY/MM/DD', cancelLabel: 'Clear'},
        "alwaysShowCalendars": true
    });
    e_object.on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY/MM/DD') + ' - ' + picker.endDate.format('YYYY/MM/DD'));
    });
    e_object.on('cancel.daterangepicker', function() {
        $(this).val('');
    });

};
var $recharge_download_modal = $('#recharge_download_modal');
var $down_recharge_time_range = $('#down_recharge_time_range');
var $btn_confirm_down = $('#btn_confirm_down');
format_time_range_input($down_recharge_time_range);
$('#btn_export_recharge_data').click(function () {
    $recharge_download_modal.modal('show')
});

$btn_confirm_down.click(function () {
    var range_date = $down_recharge_time_range.val();
    if (range_date.length>0){
        $btn_confirm_down.attr('disabled', 'disabled');
        $btn_confirm_down.text('执行中');
        range_date = range_date.split('-');
        var time_start = $.trim(range_date[0].replace(/\//g, '-'));
        var time_end = $.trim(range_date[1].replace(/\//g, '-'));

        $.ajax({
            url: '/download/recharge_data',
            type: 'get',
            dataType:'json',
            data: {'start_date': time_start, 'end_date': time_end},
            success: function (result) {
                $btn_confirm_down.removeAttr('disabled');
                $btn_confirm_down.text('确认导出');
                if (result['status'] === 'success'){
                     window.location=result["url"];
                    $recharge_download_modal.modal('hide')
                }else if (result['status'] ==='data_empty'){
                    alert('当前选择时间范围，没有数据')
                }else{
                    alert('处理失败')
                }
            },
            error: function () {
                $btn_confirm_down.removeAttr('disabled');
                $btn_confirm_down.text('确认导出');
                alert('处理失败1')
            }
        })
    }else{
        alert('时间范围不能为空');
    }

});

$recharge_download_modal.on('hide.bs.modal', function () {
  $btn_confirm_down.removeAttr('disabled');
  $btn_confirm_down.text('确认导出');
});
