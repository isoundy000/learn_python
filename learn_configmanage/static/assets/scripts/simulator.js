/**
 * Created by wangrui on 16/2/2.
 */

var GLOBAL_JSON_DATA = null;

//getGameServerData($("#game_server"), 1);

var quality_css = {
    2: "btn green",
    3: "btn blue",
    4: "btn purple",
    5: "btn yellow"
};


var quality_css3 = {
    2: "label label-success",
    3: "label label-info",
    4: "label label-purple",
    5: "label label-warning"
};

var g_data = null;
var GENERAL_DATA = null;
var EQUIP_TYPE = ["weapon", "head", "armor", "accessory",  "treasure", "horse"];
var EQUIP_TYPE_NAME = ["武器", "头盔", "盔甲", "佩饰", "宝物", "坐骑"];
var EQUIP_DATA = null;
var MAGIC_STONE = null;
var GENERAL_UPGRADE_PROPS = [20196,20197,20198,20199];
var GENERAL_PROPS_EXP = [100, 1000, 5000, 20000];
var peiyangdan_cid = 20009;
var MAX_GENERAL_LEVEL = 0;
var SERVER_ID = 1;
var LOG_ARRAY = [];
var PRODUCT_ARRAY = [];


function formate_time(){
    var currentDT = new Date();
    var y, m, date, hs, ms, ss, theDateStr;
    y = currentDT.getFullYear(); //四位整数表示的年份
    m = currentDT.getMonth() + 1; //月
    date = currentDT.getDate(); //日
    hs = currentDT.getHours(); //时
    ms = currentDT.getMinutes(); //分
    ms = ms < 10? "0" + ms: ms;
    ss = currentDT.getSeconds(); //秒
    ss = ss < 10? "0" + ss: ss;
    theDateStr = y + "-" + m + "-" + date  + hs + ":" + ms + ":" + ss;
    return theDateStr;
}

function insert_log(message){
    var temp_date = formate_time();
    LOG_ARRAY.push(temp_date + "[" + message + "]");
}


function insert_product(message){
    PRODUCT_ARRAY.push(message);
}


function display_log(){
    var str_html = "";
    for(var la=0; la<LOG_ARRAY.length; la++){
        str_html += "<p>" + LOG_ARRAY[la]  + "</p>";
    }
    $("#log_list").html(str_html);
}


function display_product(){
    var str_html = "";
    for(var la=0; la<PRODUCT_ARRAY.length; la++){
        str_html += "<p>" + PRODUCT_ARRAY[la]  + "</p>";
    }
    $("#product_props_list").html(str_html);
}

function getrolename(){
    $.ajax({
        type: 'get',
        url: '/simulator/getrolename',
        data: {server_id: SERVER_ID},
        dataType: 'JSON',
        async:false,
        success: function (data) {
            var str_html = "";
            str_html += "<option value=\"0\">创建新角色</option>";
            var last_id = data[0]["id"];
            for (var i = 0; i < data.length; i++) {
                str_html += "<option value='" + data[i]["id"] + "'>" + data[i]["id"] + "_" + data[i]["level"] + "级-" +
                    data[i]["name"] + "</option>";

            }
            var $select_role = $("#select_role");
            $select_role.html(str_html);
            $select_role.val(last_id);
            $select_role.change();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
}


function display_choose_modal(){
    $.ajax({
        type: 'get',
        url: '/simulator/getroleid',
        dataType: 'JSON',
        success: function (data) {
            getrolename();
            if (data["role_id"] == 0) {
                $("#choose_role_modal").modal("show");
            }
            else{
                $("#select_role").val(data["role_id"]);
                console.log($("#select_role").val());
                $("#game_in").click();
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
}
display_choose_modal();


$("#create_new").on("click", function(e){
    e.preventDefault();
    var role_name = $("#new_role").val();
    if(role_name.length !=0){
        $.ajax({
            type: 'get',
            url: '/simulator/createnew',
            data: {
                server_id: SERVER_ID,
                role_name: role_name
            },
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "success"){
                    getrolename();
                }
                else if (data["status"] == "fail"){
                    alert_error_modal("角色名称重复.");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }else{
        Common.alert_message($("#error_modal"), 0, "角色名称不能为空.");
    }

});



$("#select_role").on("change", function(e){
    e.preventDefault();
    var select_role = $(this).val();
    var $new_div = $("#new_role_div");
    var div_game_in = $("#div_game_in");
    console.log(select_role);
    if (select_role == "0"){
        $new_div.removeClass("hidden");
        div_game_in.addClass("hidden");
    }
    else{
        $new_div.addClass("hidden");
        div_game_in.removeClass("hidden");
    }
});



var EQUIP_BAPTIZE = {
    "atk": "攻击",
    "def": "防御",
    "hp": "生命",
    "adddmg": "增伤值",
    "subdmg": "减伤值"
};

var getequipinfo = function(other, equip_id, type, tag){
    //获取装备属性
    var role_id = $("#select_role").val();
    if (equip_id != 0){
        $.ajax({
            type: 'get',
            url: '/simulator/getequipproperty',
            data: {
                server_id: SERVER_ID,
                role_id: role_id,
                equip_id: equip_id
            },
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "success") {
                    var data1 = data["data"];
                    console.log("equip_info", data["data"]);
                    var equip_cid = data1[1];
                    var equip_level = data1[2];
                    var equip_level2 = g_data["equip"][equip_id]["level2"];
                    var equip_name = GLOBAL_JSON_DATA["equip"][equip_cid]["name"];
                    var equip_qua = GLOBAL_JSON_DATA["equip"][equip_cid]["quality"];
                    var equip_type = GLOBAL_JSON_DATA["equip"][equip_cid]["type"];
                    var limit_xilian_qua = GLOBAL_JSON_DATA["global_kv"]["baptize_equip_quality"]["value"];
                    $("#equip_id").val(equip_id);
                    $("#equip_type").val(equip_type);
                    if (type == 1) {
                        var $equip_name = $("#equip_name");
                        $equip_name.html(equip_name + "+" + equip_level2);
                        $equip_name.removeClass();
                        $equip_name.addClass("label " + quality_css3[equip_qua]);
                        $("#equip_level").html(equip_level);
                        $("#equip_atk").html(data1[5]);
                        $("#equip_def").html(data1[6]);
                        $("#equip_hp").html(data1[7]);
                        $("#adddmg").html(data1[8]);
                        $("#subdmg").html(data1[9]);
                        if (equip_qua >= limit_xilian_qua) {
                            for (var i = 1; i <= 4; i++) {
                                var baptize_attr = GLOBAL_JSON_DATA["equip"][equip_cid]["baptize_attr" + i];
                                var attr_limit = GLOBAL_JSON_DATA["equip"][equip_cid]["attrlimit" + i];
                                var attr_limitup = GLOBAL_JSON_DATA["equip"][equip_cid]["attrlimitup_" + i];
                                var attr_equip = 0;
                                var max_limit = (equip_level - 1) * attr_limitup + attr_limit;
                                if (baptize_attr == "atk") {
                                    attr_equip = data1[5]
                                }
                                else if (baptize_attr == "def") {
                                    attr_equip = data1[6]
                                }
                                else if (baptize_attr == "hp") {
                                    attr_equip = data1[7]
                                }
                                else if (baptize_attr == "adddmg") {
                                    attr_equip = data1[8]
                                }
                                else if (baptize_attr == "subdmg") {
                                    attr_equip = data1[9]
                                }
                                $("#xilian_" + i).html(EQUIP_BAPTIZE[baptize_attr] + ":" + attr_equip);
                                $("#max_xilian_" + i).html("最大:" + max_limit);
                            }
                        }
                        if (tag == 1) {
                            $("#equip_info_modal").modal("show");
                        }
                        else{
                            $("#horse_info_modal").modal("show");
                        }
                    }
                    else {
                        var $horse_name = $("#horse_name");
                        $horse_name.html(equip_name + "+" + equip_level2);
                        $("#horse_level1").html(equip_level);
                        $("#horse_level").html(equip_level);
                        var role_level = g_data["role"]["level"];
                        $("#horse_max_level").html(role_level);
                        var attr1 = GLOBAL_JSON_DATA["equip"][equip_cid]["attr1"];
                        $("#horse_att1").html(EQUIP_BAPTIZE[attr1] + ":");
                        $("#horse_strengthen_attr").html(EQUIP_BAPTIZE[attr1] + ":");
                        var init1 = GLOBAL_JSON_DATA["equip"][equip_cid]["init1"];
                        var grow_1 = GLOBAL_JSON_DATA["equip"][equip_cid]["grow_1"];
                        var attr1_value = (equip_level-1) * grow_1 + init1;
                        var two_exp = GLOBAL_JSON_DATA["treasure2_strengthen"][equip_level + 1]["quality" + equip_qua];
                        $("#horse_exp1").html(g_data["equip"][equip_id]["exp2"]);
                        $("#horse_exp2").html(two_exp);
                        $("#horse_att1_value").html(attr1_value);
                        $("#horse_strengthen_value").html(attr1_value);
                        $("#horse_info_modal").modal("show");

                    }
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
    else{
        console.log("other", other);
        $("#equip_type").val(other);
        $("#change_equip").click();
    }

};


$("#strength_horse").on("click", function(e){
    e.preventDefault();
    $("#horse_info_modal").modal("hide");
    $("#horse_strengthen_id").val($("#equip_id").val());
    $("#strength_horse_modal").modal("show");
});

var consume_horse_strengthen = [];

$("#auto_add_horse").on("click", function(e){
    e.preventDefault();
    var i= 1;
    var str_html = "";
    var treasure_strength = GLOBAL_JSON_DATA["treasure2_strengthen"];
    var horse_id = $("#horse_strengthen_id").val();
    var horse_level = parseInt($("#horse_level").html());
    var horse_max_level = parseInt($("#horse_max_level").html());
    var horse_cid = g_data["equip"][horse_id]["cid"];
    var horse_quality = GLOBAL_JSON_DATA["equip"][horse_cid]["quality"];
    var horse_limit_exp = GLOBAL_JSON_DATA["equip"][horse_cid]["exp"];
    var horse_exp1 = parseInt($("#horse_exp1").html());
    var horse_exp2 = parseInt($("#horse_exp2").html());
    var strengthen_value = parseInt($("#horse_strengthen_value").html());
    for(var n=1; n<horse_max_level.length; n++){
        horse_limit_exp += treasure_strength[n]["quality" + horse_quality];
    }
    var up_level = 0;
    for(var eq in g_data["equip"]){
        if (i > 5){
            break;
        }
        var equip_cid = g_data["equip"][eq]["cid"];
        var equip_level1 = g_data["equip"][eq]["level1"];
        var equip_t = GLOBAL_JSON_DATA["equip"][equip_cid]["type"];
        var equip_name = GLOBAL_JSON_DATA["equip"][equip_cid]["name"];
        var equip_qua = GLOBAL_JSON_DATA["equip"][equip_cid]["quality"];
        var exp2 = g_data["equip"][eq]["exp2"];
        if (horse_id != eq){
            if (equip_t == "horse" || equip_t == "treasure") {
                if (!g_data["equip"][eq].hasOwnProperty("g_cid")) {
                    var total = GLOBAL_JSON_DATA["equip"][equip_cid]["exp"];
                    for (var t =1; t<equip_level1+1; t++){
                        total +=  treasure_strength[t]["quality" + equip_qua];
                    }
                    str_html += "<label>" + equip_name + "[LV:" + equip_level1 + "]" + "</label>";
                    if (total > horse_limit_exp){
                        break;
                    }
                    else{
                        var s_total = total + horse_exp1;
                        while(s_total > horse_exp2){
                            up_level += 1;
                            s_total = s_total - horse_exp2;
                            horse_exp2 = treasure_strength[(horse_level + up_level + 1)]["quality" + horse_quality];
                            horse_exp1 = s_total;
                        }
                        horse_exp1 = s_total;
                    }
                    consume_horse_strengthen.push(parseInt(eq));
                    i += 1;
                }
            }
        }
    }
    if (up_level > 0){
        $("#horse_add_level").html("+" + up_level);
    }
    $("#horse_exp1").html(horse_exp1);
    $("#horse_exp2").html(horse_exp2);
    var s_value = (horse_level + up_level - 1) * GLOBAL_JSON_DATA["equip"][horse_cid]["grow_1"] + GLOBAL_JSON_DATA["equip"][horse_cid]["init1"];

    $("#horse_strengthen_add_value").html("+" + (s_value - strengthen_value));
    $("#horse_consume_props").html(str_html);
});

$("#horse_strengthen_confirm").on("click", function(e){
    e.preventDefault();
    var equip_id = $("#equip_id").val();
    var req_data = {
        "iid": equip_id,
        "ids": consume_horse_strengthen
    };
    var data = common_request(req_data, 1118);
    console.log("baowu_strengthen", data);
    if (data["status"] == "status"){
        consume_horse_strengthen = [];
        setTimeout("load_role_info()", 1000);
    }
});

var TEMP_CONSUME_REFINE = [];

$("#horse_jinglian").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(137);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{
        var horse_id = $("#equip_id").val();
        var horse_cid = g_data["equip"][horse_id]["cid"];
        var horse_level2 = g_data["equip"][horse_id]["level2"];
        var horse_name = GLOBAL_JSON_DATA["equip"][horse_cid]["name"];
        var horse_quality = GLOBAL_JSON_DATA["equip"][horse_cid]["quality"];
        var refine = GLOBAL_JSON_DATA["equip"][horse_cid]["refine"];
        var refine_grow = GLOBAL_JSON_DATA["equip"][horse_cid]["refine-grow"];
        var jinglian_name1 = horse_name;
        var jinglian_name2 = horse_name;
        if (horse_level2 > 0){
            jinglian_name1 += "+" + horse_level2;
        }
        var new_level = horse_level2 + 1;
        jinglian_name2 += "+" + new_level;

        $("#horse_jinglian_name").html(jinglian_name1);
        $("#horse_jinglian_name2").html(jinglian_name2);
        $("#horse_jinglian_attr1").html(EQUIP_BAPTIZE[refine] + ":");
        $("#horse_jinglian_attr2").html(EQUIP_BAPTIZE[refine] + ":");
        $("#horse_jinglian_attr3").html(horse_level2 * refine_grow);
        $("#horse_jinglian_attr4").html(new_level * refine_grow);

        for(var i=1; i<=4; i++){
            var refine_level = GLOBAL_JSON_DATA["equip"][horse_cid]["refine-level" + i];
            var refine_attr = GLOBAL_JSON_DATA["equip"][horse_cid]["refine-attr" + i];
            var temp_html = "";
            if (refine_level != 0){
                var temp = refine_attr.split(";");
                var label_html = "";
                if (horse_level2 > refine_level){
                    label_html = "<label class='label label-success'>"
                }
                else{
                    label_html = "<label>";
                }
                temp_html = label_html + EQUIP_BAPTIZE[temp[0]] + "+" + parseInt(temp[1]) * 100 + "%" + "(宝物+" + refine_level + "解锁)" + "</label>";
                $("#horse_jinglian_value" + i).html(temp_html);
                $("#horse_jinglian_value" + i + "_" + i).html(temp_html);
            }
        }
        var needself = GLOBAL_JSON_DATA["treasure2_refine"][new_level]["oneself" + horse_quality];
        var num = GLOBAL_JSON_DATA["treasure2_refine"][new_level]["num" + horse_quality];
        var jinglian_num = num.split(";")[1].split(",")[1];
        var consume_cid = num.split(";")[1].split(",")[0];
        var consume_coin = num.split(";")[0].split(",")[1];
        var have = 0;
        if (g_data["props"].hasOwnProperty(consume_cid)){
            have = g_data["props"][consume_cid]["num"];
        }
        if (needself != 0){
            $("#jinglian_self_name").html(horse_name);
            var self1 = 0;
            for(var eq in g_data["equip"]){
                if (g_data["equip"][eq]["cid"] == horse_cid){
                    self1 += 1;
                    TEMP_CONSUME_REFINE.push(eq);
                }
            }
            $("#jinglian_self1").html(self1 + "/");
            $("#jinglian_self2").html(needself);
        }
        $("#jinglian_consume1").html(have);
        $("#jinglian_consume2").html(jinglian_num);
        $("#jinglian_consume_coin").html(consume_coin);
        $("#horse_info_modal").modal("hide");
        $("#jinglian_horse_modal").modal("show");
    }
});


$("#horse_jinglian_confirm").on("click", function(e){
    e.preventDefault();
    var consume1 = parseInt($("#jinglian_consume1").html());
    var consume2 = parseInt($("#jinglian_consume2").html());
    var consume_coin = parseInt($("#jinglian_consume_coin").html());
    if (consume1 < consume2){
        alert_error_modal("精炼石不足");
    }
    else if (consume_coin < g_data["role"]["coin"]){
        alert_error_modal("银币不足");
    }
    else{
        var horse_id = $("#equip_id").val();
        var req_data = [horse_id];
        for (var i = 0; i < TEMP_CONSUME_REFINE.length; i++) {
            req_data.push(TEMP_CONSUME_REFINE[i]);
        }
        var data = common_request(req_data, 1119);
        console.log("jinglian", data);
        if (data["status"] == "success") {
            $("#jinglian_horse_modal").modal("hide");
            setTimeout("load_role_info()", 1000);
        }
    }
});


function xilian_zhuangbei(equip_id){
    $("#xilian_id").val(equip_id);
    getequipinfo("", equip_id, 1, 2);
    $("#xilian_modal").modal("show");
}

$("#xilian_equip").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(53);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{
        $("#equip_info_modal").modal("hide");
        $("#xilian_id").val($("#equip_id").val());
        $("#xilian_modal").modal("show");
    }
});


function equip_xilian_preview(count){
    var eid = parseInt($('#xilian_id').val());
    var xilian_type = parseInt($("input[name='xilian_type']:checked").val());
    var req_data = [
        eid, xilian_type, count
    ];
    var data = common_request(req_data, 1120);
    console.log(data);
    if (data["status"] == "success"){
        var xilian_data = $.parseJSON(data["data"]);
        var e_cid = xilian_data[1];
        var atk = xilian_data[5];
        var def = xilian_data[6];
        var hp = xilian_data[7];
        var adddmg = xilian_data[8];
        var subdmg = xilian_data[9];
        for(var i=1; i<4; i++){
            var baptize_attr = GLOBAL_JSON_DATA["equip"][e_cid]["baptize_attr" + i];
            var xilian_init = parseInt($("#xilian_" + i).html().split(":")[1]);
            var sub_num = 0;
            if (baptize_attr == "atk"){
                sub_num = atk - xilian_init;
            }
            else if (baptize_attr == "def"){
                sub_num = def - xilian_init;
            }
            else if (baptize_attr == "hp"){
                sub_num = hp - xilian_init;
            }
            else if (baptize_attr == "adddmg"){
                sub_num = adddmg - xilian_init;
            }else if (baptize_attr == "subdmg"){
                sub_num = subdmg - xilian_init;
            }
            if (sub_num != 0){
                var tmp = "";
                if (sub_num > 0){
                    tmp = "<span class='badge badge-success'>" + "+" + sub_num + "</span>";
                }
                else{
                    tmp = "<span class='badge badge-important'>" + sub_num + "</span>";
                }
                $("#xilian_change_" + i).html(tmp);
            }
        }
        $("#xilian_opr_group").removeClass("hidden");
    }
}

function clear_xilian_data(){
    for(var i=1; i<=4; i++){
        $("#xilian_change_" + i).html("");
    }
}

function xilian_pre(tag){
    equip_xilian_preview(tag);
    $("#xilian_opr_group").removeClass("hidden");
    $("#xilian_preview_group").addClass("hidden");
}


$("#xilian_preview1").on("click", function(e){
    e.preventDefault();
    xilian_pre(1);
});

$("#xilian_preview5").on("click", function(e){
    e.preventDefault();
    xilian_pre(5);
});

$("#xilian_preview10").on("click", function(e){
    e.preventDefault();
    xilian_pre(10);
});

function xilian_operation(tag){
    var data = common_request([tag], 1121);
    console.log("xilian", data);
    if (data["status"] == "success"){
        clear_xilian_data();
        $("#xilian_opr_group").addClass("hidden");
        $("#xilian_preview_group").removeClass("hidden");
        var xilian_id = $("#xilian_id").val();
        getequipinfo("", xilian_id, 1, 0);
    }
}

$("#xilian_confrim").on("click", function(e){
    e.preventDefault();
    xilian_operation(1);
});

$("#xilian_cancle").on("click", function(e){
    e.preventDefault();
    xilian_operation(0);
});


function get_level_max_exp(quality, g_cid, level){
    var general_exp_json = GLOBAL_JSON_DATA["general_exp"][level];
    var max_exp = 0;
    if (g_cid >= 10101 && g_cid <= 10115){
        max_exp = general_exp_json["exp"];
    }
    else{
        max_exp = general_exp_json[quality + "exp"];
    }
    return max_exp;
}

var load_general_info = function(i, general_id){
    //去掉槽位的样式
    for(var t=1; t<=7; t++){
        var $sl = $("#slot_" + t);
        if (t != i && $sl.hasClass("btn dark")){
            $sl.removeClass();
            $sl.addClass("btn btn-default");
        }
    }
    var rid = $("#select_role").val();
    var general_cid = GENERAL_DATA[general_id]["cid"];
    var general_level1 = GENERAL_DATA[general_id]["level1"];
    var general_level2 = GENERAL_DATA[general_id]["level2"];
    var exp = GENERAL_DATA[general_id]["exp"];
    var general_power = GENERAL_DATA[general_id]["power"];
    var general_json = GLOBAL_JSON_DATA["general"][general_cid];
    var general_quality = GLOBAL_JSON_DATA["general"][general_cid]["quality"];
    var $general_name = $("#general_name");
    var general_name = GLOBAL_JSON_DATA["general"][general_cid]["name"];

    $general_name.html(general_name + "+" + general_level2);
    var $slot = $("#slot_" + i);
    $slot.html(general_name);
    $slot.removeClass();
    $slot.addClass("btn dark");

    $general_name.removeClass();
    $general_name.addClass(quality_css3[general_quality]);
    $("#general_level").html(general_level1);
    $("#shengji_level1").html(general_level1);

    var max_exp = get_level_max_exp(general_quality, general_cid, general_level1);
    $("#shengji_exp").html(exp);
    $("#shengji_max_exp").html(max_exp);
    $("#general_exp").html(exp);
    $("#general_max_exp").html(max_exp);
    $("#general_power").html(general_power);
    $("#general_id").val(general_id);
    $("#general_cid").val(general_cid);
    $("#slot_id").val(i);
    //获取武将属性
    $.ajax({
        type: 'get',
        url: '/simulator/getgeneralproperty',
        data: {
            server_id: SERVER_ID,
            role_id: rid,
            general_id: general_id
        },
        dataType: 'JSON',
        success: function (data){
            if(data["status"] == "success"){
                var data1 = data["data"];
                $("#atk").html(data1["atk"]);
                $("#py_atk").html( data1["atk"]);
                $("#shengji_atk").html(data1["atk"]);

                $("#hp").html(data1["hp"]);
                $("#py_hp").html( data1["hp"]);
                $("#shengji_hp").html(data1["hp"]);

                $("#defense").html(data1["defense"]);
                $("#py_def").html(data1["defense"]);
                $("#shengji_def").html(data1["defense"]);

                $("#speed").html(data1["speed"]);
                $("#py_speed").html(data1["speed"]);
                $("#shengji_speed").html(data1["speed"]);

                $("#critical").html(data1["critical"]);
                $("#dodge").html(data1["dodge"]);
                $("#parry").html(data1["parry"]);
                $("#hit").html(data1["hit"]);
                $("#arp").html(data1["arp"]);
                $("#resilience").html(data1["resilience"]);
                $("#criticaldmg").html(data1["criticaldmg"]);
                $("#potential").html(data1["potential"]);
                $("#py_potential").html(data1["potential"]);
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });

    //缘分
    $.ajax({
        type: 'get',
        url: '/simulator/getslotrelation',
        data: {
            server_id: SERVER_ID,
            role_id: rid,
            slot_id: i
        },
        dataType: 'JSON',
        success: function (data){
            var relation_arr = null;
            if(data["status"] == "success"){
                relation_arr = data["data"]["slots"][0]["relation"];
            }
            var temp_html = "";
            for(var r=0; r<relation_arr.length; r ++){
                if(r>5){
                    break;
                }
                var cond_desc = general_json["cond" + (r + 1) + "desc"];
                temp_html += "<tr>";
                if (relation_arr[r]["activate"] == 2){
                    temp_html += "<td class='success'>";
                }
                else{
                    temp_html += "<td>";
                }
                temp_html += cond_desc + "</label></td></tr>";
            }
            $("#cond_list").html(temp_html);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });

    //装备信息
    for(var e=0; e < EQUIP_TYPE.length; e++){
        var equip_id = GENERAL_DATA[general_id][EQUIP_TYPE[e]];
        var type = 0;
        if (EQUIP_TYPE[e] == "treasure" || EQUIP_TYPE[e] == "horse") {
            type = 2;
        }
        else {
            type = 1;
        }
        var $equip = $("#" + EQUIP_TYPE[e]);
        if (equip_id != null){
            var equip_cid = g_data["equip"][equip_id]["cid"];
            var equip_level1 = g_data["equip"][equip_id]["level1"];
            var equip_level2 = g_data["equip"][equip_id]["level2"];
            var equip_json = GLOBAL_JSON_DATA["equip"][equip_cid];
            var equip_name = equip_json["name"];
            var quality = equip_json["quality"];
            var temp = "<label class='label " + quality_css3[quality] + "'>" + equip_name + "+" + equip_level2 + "</label>";
            $equip.children("div").html(temp);
            $equip.children("span").html(equip_level1);
            $equip.attr("onclick", "getequipinfo('" + EQUIP_TYPE[e] + "'," + equip_id + "," + type + "," + 1 + ")")
        }
        else{
            $equip.children("div").html(EQUIP_TYPE_NAME[e]);
            $equip.children("span").html("");
            $equip.attr("onclick", "getequipinfo('" + EQUIP_TYPE[e] + "'," + 0 + "," + type + "," + 2 + ")")
        }
    }
    //神石信息
    for(var s=1; s<=8; s++){
        var $stone = $("#stone_" + s);
        var t_html = "";
        var temp_1 = MAGIC_STONE[i-1]["g" + s];
        $stone.children("span").removeClass();
        if (temp_1 == 0){
            $stone.children("span").addClass("badge badge-info");
        }
        else{
            t_html = temp_1;
            $stone.children("span").addClass("badge badge-info");
        }
        $stone.children("span").html(t_html);
    }
};

var open_level = {
    3: 3,
    7: 4,
    13: 5,
    20: 6,
    24: 7
};

function load_role_data(){
    var data = g_data["role"];
    if (data.length != 0) {
        $("#role_level").html(data["level"]);
        $("#role_name").html(data["name"]);
        $("#role_stamina").html(data["stamina"] + "/" + data["maxstamina"]);
        $("#role_energy").html(data["energy"] + "/" + data["maxenergy"]);
        $("#role_coin").html(data["coin"]);
        $("#role_gold").html(data["gold"]);
        $("#role_power").html(data["power"]);
        $("#a_power").html(data["power"]);
        $("#b_power").html(data["power"]);
        MAX_GENERAL_LEVEL = data["level"] * parseInt(GLOBAL_JSON_DATA["global_kv"]["general_level"]);
    }
}

function load_role_info(){
    console.log("in load_role_info()");
    var role_id = $("#select_role").val();
    var slot_id = parseInt($("#slot_id").val());
    $.ajax({
        type: 'get',
        url: '/simulator/getroleinfo',
        data: {
            server_id: SERVER_ID,
            role_id: role_id
        },
        dataType: 'JSON',
        success: function (data){
            g_data = data;
            var slot = 0;
            load_role_data();

            for (var ol in open_level) {
                if (data["role"]["level"] >= ol) {
                    slot = open_level[ol];
                }
            }
            if(data["slot"].length != 0){
                GENERAL_DATA = data["general"];
                EQUIP_DATA = data["equip"];
                MAGIC_STONE = data["godstone"];
                for(var i=1; i<=7; i++){
                    var temp_slot = data["slot"]["s" + i];
                    var $slot = $("#slot_" + i);
                    var $a_slot = $("#a_slot_" + i);
                    var $b_a_slot = $("#b_a_slot_" + i);
                    $slot.html("未开启");
                    $a_slot.html("未开启");
                    $a_slot.removeClass();
                    if(temp_slot != null){
                        g_data["general"][temp_slot]["slot"] = 1;
                        var general_cid = GENERAL_DATA[temp_slot]["cid"];
                        var general_name = GLOBAL_JSON_DATA["general"][general_cid]["name"];
                        var general_qua = GLOBAL_JSON_DATA["general"][general_cid]["quality"];
                        $slot.html(general_name);
                        $a_slot.html(general_name);
                        $a_slot.addClass(quality_css[general_qua]);
                        $b_a_slot.html(general_name);
                        if (slot_id == 0){
                            if (i == 1)
                                load_general_info(i, temp_slot)
                        }
                        else if (slot_id == i){
                            load_general_info(slot_id, temp_slot)
                        }
                        $slot.attr("onclick", "load_general_info(" + i + "," + temp_slot + ")");
                        for(var e=0; e<EQUIP_TYPE.length; e++){
                            var equip_id = GENERAL_DATA[temp_slot][EQUIP_TYPE[e]];
                            if (equip_id != null){
                                g_data["equip"][equip_id]["g_cid"] = general_cid;
                            }
                        }
                    }
                    else{
                        if (i <= slot){
                            $slot.html("+");
                            $slot.removeClass();
                            $slot.addClass("btn green");
                            $slot.attr("onclick", "on_slot(" + i + ")");
                        }
                    }
                }
            }
            display_general();
            display_props();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
}

function on_slot(slot_num){
    $("#slot_id").val(slot_num);
    $("#change_general_modal").modal("show");
}

$("#game_in").on("click", function(e){
    e.preventDefault();
    $("#choose_role_modal").modal("hide");
    var load_modal = $("#loading_json_modal");
    var select_role = $("#select_role").val();
    console.log("select_role", select_role);
    $.ajax({
        type: 'get',
        url: '/simulator/updateusersimulator',
        data: {
            role_id: select_role
        },
        dataType: 'JSON',
        success: function (data) {

        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });

    if (GLOBAL_JSON_DATA == null){
        load_modal.modal("show");
        var page_content = $('.page-content');
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/simulator/loadjsondata',
            data: {server_id: SERVER_ID},
            dataType: 'JSON',
            success: function (data){
                App.unblockUI(page_content);
                GLOBAL_JSON_DATA = data;
                load_modal.modal("hide");
                load_role_info();
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        });
    }
    else{
        load_role_info();
    }

});

var COPY_EXT = {
    "copy": {},
    "brave_copy": {}
};

function isEmptyObject(o){
    for(var n in o){

        return false;
    }
    return true;
}

function MakeOptionListMap(copy, tag, json, json2){
    var str_html = "";
    var temp_s = 0;
    if (isEmptyObject(copy) == false){
        for(var c=0; c<copy.length; c++){
            var map = copy[c]["map"];
            var point = copy[c]["point"];
            var next_point = parseInt(point) + 1;
            if (COPY_EXT[tag].hasOwnProperty(map)){
                if (!json[map].hasOwnProperty(next_point)){
                    map += 1;
                }
                if (temp_s != map){
                    str_html += "<option value='" + map + "'>" + map + "_" + json2[map]["name"] + "</option>";
                    temp_s = map;
                }
            }
        }
    }
    else{
        var map2 = 42101;
        str_html += "<option value='" + map2 + "'>" + map2 + "_" + json2[map2]["name"] + "</option>";
    }
    return str_html;
}


$("#change_equip").on("click", function(e){
    e.preventDefault();
    $("#equip_info_modal").modal("hide");
    var equip_type = $("#equip_type").val();
    var str_html = "";
    for(var eq in g_data["equip"]){
        var equip_cid = g_data["equip"][eq]["cid"];
        var equip_t = GLOBAL_JSON_DATA["equip"][equip_cid]["type"];
        var equip_name = GLOBAL_JSON_DATA["equip"][equip_cid]["name"];
        if (equip_t == equip_type){
            var g_name = "";
            if (g_data["equip"][eq].hasOwnProperty("g_cid")){
                g_name = GLOBAL_JSON_DATA["general"][g_data["equip"][eq]["g_cid"]]["name"];
            }
            if (g_name == ""){
                str_html += "<option value='" + eq + "'>" + equip_name + "</option>";
            }
            else{
                str_html += "<option value='" + eq + "'>" + equip_name + "-装备与" + g_name + "</option>";
            }
        }
    }
    $("#select_change_equip").html(str_html);
    $("#change_equip_modal").modal("show");
});

$("#change_horse").on("click", function(e){
    $("#change_equip").click();
});


$("#btn_change_equip_confirm").on("click", function(e){
    e.preventDefault();
    var slot_id = parseInt($("#slot_id").val());
    var equip_id = parseInt($("#select_change_equip").val());
    var reg_data = {
        "slot": slot_id,
        "equipeid": equip_id
    };
    var data = common_request(reg_data, 1005);
    console.log("change_equip", data);
    if (data["status"] == "success"){
        $("#change_equip_modal").modal("hide");
        setTimeout("load_role_info()", 1000);
    }
});

function MakeOptionListPoint(map, tag, json){
    var str_html = "";
    console.log("COPY_EXT", COPY_EXT);
    if (COPY_EXT[tag].hasOwnProperty(map)){
        var point_array = COPY_EXT[tag][map]["data"];
        var point_array_len = point_array.length;
        var next_point = point_array[0] + 1;
        if(json[map].hasOwnProperty(next_point)){
            str_html += "<option value='" + next_point + "'>" + next_point + "_" + json[map][next_point]["name"] + "</option>";
        }
        for(var p =0; p<point_array_len; p++){
            var point = point_array[p];
            str_html += "<option value='" + point + "'>" + point + "_" + json[map][point]["name"] + "</option>";
        }
    }
    else{
        str_html += "<option value='1'>" + "1_" + json[map]["1"]["name"] + "</option>";
    }
    return str_html;
}


function MakeCopyExt(copy, tag){
    for(var c in copy){
        var map = copy[c]["map"];
        var point = copy[c]["point"];
        if (!COPY_EXT[tag].hasOwnProperty(map)){
            COPY_EXT[tag][map] = {};
            COPY_EXT[tag][map]["data"] = [];
        }
        COPY_EXT[tag][map][point] = copy[c];
        COPY_EXT[tag][map]["data"].push(point);
    }
}


$("#li_copy").on("click", function(e){
    e.preventDefault();
    console.log("li_copy click");
    COPY_EXT["copy"] = {};
    MakeCopyExt(g_data["copy"], "copy");
    var str_html = MakeOptionListMap(g_data["copy"], "copy", GLOBAL_JSON_DATA["copy"], GLOBAL_JSON_DATA["map"]);
    var $copy_section = $("#copy_section");
    $copy_section.html(str_html);
    $copy_section.change();
});

$("#li_bravecopy").on("click", function(e){
    e.preventDefault();
    MakeCopyExt(g_data["brave_copy"], "brave_copy");
    var str_html = MakeOptionListMap(g_data["brave_copy"], "brave_copy", GLOBAL_JSON_DATA["brave_copy"], GLOBAL_JSON_DATA["brave_map"]);
    var $bcopy_section = $("#brave_copy_section");
    $bcopy_section.html(str_html);
    $bcopy_section.change();
});

$("#copy_section").on("change", function(e){
    e.preventDefault();
    var map = $(this).val();
    var str_html = MakeOptionListPoint(map, "copy", GLOBAL_JSON_DATA["copy"]);
    var $copy_point = $("#copy_point");
    $copy_point.html(str_html);
    $copy_point.change();
});

function display_star_count(tag, map, point, battle_r){
    var str_html = "";
    var star = 0;
    if(COPY_EXT[tag].hasOwnProperty(map)){
        if (COPY_EXT[tag][map].hasOwnProperty(point))
            star = COPY_EXT[tag][map][point]["star"];
    }
    for(var s=1; s<=3; s++){
        if (star >= s){
            str_html += "<i class='fa fa-star'></i>"
        }
        else{
            str_html += "<i class='fa fa-star-o'></i>"
        }
    }
    battle_r.html(str_html);
}

var display_npc = function(tag){
    var maps = "";
    var point = "";
    var power = 0;
    var temp = "";
    var slot = "";
    if (tag == 1){
        maps = $("#copy_section").val();
        point = $("#copy_point").val();
        power = GLOBAL_JSON_DATA["copy"][maps][point]["power"];
        $("#npc_power").html(power);
        temp = "copy";
        slot = "d_slot_";
    }
    else{
        maps = $("#brave_copy_section").val();
        point = $("#brave_copy_point").val();
        power = GLOBAL_JSON_DATA["brave_copy"][maps][point]["power"];
        temp = "brave_copy";
        slot = "b_d_slot_";
        $("#brave_npc_power").html(power);
    }
    for(var i = 1; i <= 7; i ++){
        var p_str = GLOBAL_JSON_DATA[temp][maps][point]["p" + i];
        var p_type = GLOBAL_JSON_DATA[temp][maps][point]["p" + i + "-type"];
        var p_type_str = "";
        if (p_type == 1){
            p_type_str = "(普通)";
        }
        else{
            p_type_str = "(Boss)";
        }
        if(p_str != 0){
            var quality = GLOBAL_JSON_DATA["copy_monster"][p_str]["quality"];
            var general_name = GLOBAL_JSON_DATA["copy_monster"][p_str]["name"];
            var $d_slot = $("#" + slot + i);
            $d_slot.html(general_name + p_type_str);
            $d_slot.removeClass();
            $d_slot.addClass(quality_css[quality]);
            if (p_type == 1){
                $d_slot.addClass("btn-xs");
            }
        }
    }
};

$("#copy_point").on("change", function(e){
    e.preventDefault();
    display_npc(1);
    var map = $("#copy_section").val();
    var point = $(this).val();
    display_star_count("copy", map, point, $("#battle_result"));
});

$("#brave_copy_section").on("change", function(e){
    e.preventDefault();
    var map = $(this).val();
    var str_html = MakeOptionListPoint(map, "brave_copy", GLOBAL_JSON_DATA["brave_copy"]);
    var $copy_point = $("#brave_copy_point");
    $copy_point.html(str_html);
    $copy_point.change();
});

$("#brave_copy_point").on("change", function(e){
    e.preventDefault();
    var map = $("#brave_copy_section").val();
    var point = $(this).val();
    display_star_count("brave_copy", map, point, $("#brave_battle_result"));
    display_npc(2);
});

var REWARD = {
    "coin": "银币",
    "gold": "元宝",
    "equips": "武器",
    "props": "道具"
};

var enter_str = "&#13;&#10;";
var space_str = "&nbsp;";

function get_attack_type(str_type) {
    if (str_type == "skill") {
        return "【技能】";
    }
    else if (str_type == "normal") {
        return "【普攻】";
    }
    else {
        return "【合体技】";
    }
}

function display_battle(battle_json){
    var str_html = "";
    str_html += "【战斗结果】";
    var result = battle_json["result"];
    console.log(battle_json);
    if (result == 1){
        var star = battle_json["result"];
        str_html += star + "星" + enter_str;
    }
    else{
        str_html += "失败" + enter_str;
    }
    str_html += "【战斗获得】" + enter_str;
    var reward_data = battle_json["reward"];
    for (var r in REWARD){
        str_html += space_str + space_str + space_str + space_str;
        str_html += REWARD[r] + ":";
        if (r == "equips"){
            for(var e=0; e< reward_data[r].length; e++){
                var cid = reward_data[r][e][1];
                var equip_name = GLOBAL_JSON_DATA["equip"][cid]["name"];
                PRODUCT_ARRAY.push("[副本掉落装备:]" + equip_name + "*1");
                str_html += equip_name + "*1";
            }
        }
        else if (r == "props"){
            for(var p=0; p< reward_data[r].length; p++){
                var props_name = "";
                if (reward_data[r][p][0] in GLOBAL_JSON_DATA["props"])
                     props_name = GLOBAL_JSON_DATA["props"][reward_data[r][p][0]]["name"];
                else{
                    props_name = reward_data[r][p][0];
                }
                PRODUCT_ARRAY.push("[副本掉落道具:]" + props_name + "*1");
                str_html += props_name + "*" + reward_data[r][p][1];
            }
        }
        else{
            str_html += reward_data[r];
        }
        str_html += enter_str;
    }
    var battle_data = $.parseJSON(battle_json["battlereport"]);
    str_html += "【战报】" + enter_str;
    for (var k = 0; k < battle_data["battle"]["action"].length; k++) {
        var action_source = battle_data["battle"]["action"][k]["type"];
        str_html += (k+1) + ":";
        if (action_source == "battle") {
            var source = battle_data["battle"]["action"][k]["source"];
            console.log(source);
            if (isEmptyObject(source) == false){
                var source_direct = battle_data["battle"]["action"][k]["source"]["direct"];
                var source_pos_array = battle_data["battle"]["action"][k]["source"]["pos"];
                var source_type = battle_data["battle"]["action"][k]["source"]["type"];
                var name = "";
                var zhenrong = "";
                if (source_direct == true){
                    name = "attack";
                    zhenrong = "左阵容";
                }
                else{
                    name = "defense";
                    zhenrong = "右阵容";
                }
                var generals = battle_data["meta"][name]["generals"];
                var init_data = battle_data["battle"]["init"][name];
                if(source_pos_array)
                for (var s = 0; s < source_pos_array.length; s++) {
                    var spas = source_pos_array[s];
                    if (spas != 0){
                        var ge_iid = init_data[spas]["id"];
                        var general_name = generals[ge_iid]["name"];
                        str_html += zhenrong + "[" + general_name + "]";
                    }

                }
                str_html += "使用";
                str_html += get_attack_type(source_type);
                str_html += "攻击";
                var dest_arrray = battle_data["battle"]["action"][k]["dest"];
                for (var d = 0; d < dest_arrray.length; d++) {
                    var dest_pos = dest_arrray[d]["pos"];
                    var dest_direct = dest_arrray[d]["direct"];
                    var dest_name = "";
                    var zhenrong2 = "";
                    if (dest_direct == true){
                        dest_name = "attack";
                        zhenrong2 = "左阵容";
                    }else{
                        dest_name = "defense";
                        zhenrong2 = "右阵容";
                    }
                    var dest_g_iid = 0;
                    var damage_status = "";
                    if ("damage" in dest_arrray[d]){
                        var damage_status1 = dest_arrray[d]["damage"]["status"];
                        if (damage_status1 == "normal") {
                            damage_status = "正常";
                        }
                        else if (damage_status1 == "critical") {
                            damage_status = "暴击";
                        }
                        else if(damage_status1 == "dead"){
                            damage_status = "死亡";
                        }
                        else{
                            damage_status = damage_status1;
                        }
                        dest_g_iid = battle_data["battle"]["init"][dest_name][dest_pos]["id"];
                        var dest_g_name = battle_data["meta"][dest_name]["generals"][dest_g_iid]["name"];
                        str_html += zhenrong2  + "[" + dest_g_name + "]";
                        str_html += "造成:" + dest_arrray[d]["damage"]["damage"] + "伤害" + "[" + damage_status + "]";
                        if ("status" in dest_arrray[d]){
                            if (dest_arrray[d]["status"] == "dizzy")
                                str_html += "【晕眩】";
                            else if (dest_arrray[d]["status"] == "dot")
                                str_html += "【中毒】";
                            else
                                str_html += dest_arrray[d]["status"];
                        }
                    }
                    else if ("ap" in dest_arrray[d]){
                        var ap_g_iid = battle_data["battle"]["init"][dest_name][dest_pos]["id"];
                        var ap_g_name = "";
                        if (dest_pos == 0){
                            ap_g_name = "魔宠";
                        }
                        else{
                            ap_g_name = battle_data["meta"][dest_name]["generals"][ap_g_iid]["name"];
                        }
                        str_html += ap_g_name + "怒气值:【" + dest_arrray[d]["ap"] + "】";
                    }
                }
            }
        }
        else if(action_source == "talk"){
            var general_cid = battle_data["battle"]["action"][k]["general"];
            str_html += "[" + general_json[general_cid]["name"] + "]";
            str_html += "对话:";
            str_html += "【" + battle_data["battle"]["action"][k]["content"] + "】";
        }
        else if (action_source == "pos"){
            var changes_arr = battle_data["battle"]["action"][k]["changes"];
            for (var i =0; i < changes_arr.length; i ++){
                var direct = changes_arr[i]["direct"];
                var g_iid = changes_arr[i]["general"];
                var g_name = "";
                if (direct == true){
                    str_html += "左阵容";
                    g_name = battle_data["meta"]["attack"]["generals"][g_iid]["name"];
                }
                else{
                    str_html += "右阵容";
                    g_name = battle_data["meta"]["defense"]["generals"][g_iid]["name"];
                }
                var pos = changes_arr[i]["pos"];
                var opt = changes_arr[i]["opt"];
                var str_opt = "";
                if (opt == "appear"){
                    str_opt = "上场";
                }
                else{
                    str_opt = "下场";
                }
                str_html += "【" + pos + "】" + "号位" + g_name + str_opt + ";";
            }
        }
        str_html += enter_str;
    }
    $("#battle_info").html(str_html);
    display_product();
}


function physical_no(tag, map, point){
    var role_stamina = parseInt($("#role_stamina").html().split("/")[0]);
    var physical = GLOBAL_JSON_DATA[tag][map][point]["physical"];
    if (role_stamina < physical){
        Common.alert_message($("#error_modal"), 0, "体力不足.");
    }
}

$("#copy_fight").on("click", function(e){
    e.preventDefault();
    var map = parseInt($("#copy_section").val());
    var point = parseInt($("#copy_point").val());
    physical_no("copy", map, point);
    var req_data = [
          map, point
    ];
    var data = common_request(req_data, 1306);
    if(data["status"] == "success"){
        var json_data = $.parseJSON(data["data"]);
        display_battle(json_data);
        setTimeout("load_role_info()", 2000);
        setTimeout("$(\"#li_copy\").click()", 2000);
    }
});

$("#b_copy_fight").on("click", function(e){
    e.preventDefault();
    var map = parseInt($("#brave_copy_section").val());
    var point = parseInt($("#brave_copy_point").val());
    physical_no("brave_copy", map, point);
    var req_data = [
          map, point
    ];
    var data = common_request(req_data, 1337);
    if(data["status"] == "success"){
        var json_data = $.parseJSON(data["data"]);
        display_battle(json_data);
    }
});

$("#li_bag").on("click", function(e){
    e.preventDefault();
    console.log("li_bag click");
    $("input[name='equip_type']").click();
});

$("#a_horse").on("click", function(e){
    e.preventDefault();
    $("input[name='baowu_type']").change();
});


$("#a_fragment").on("click", function(e){
    e.preventDefault();
    $("input[name='suipian_equip']").change();
});

var fragment_compound = function(other, num, e_cid){
    var data = common_request([e_cid], 1108);
    console.log("fragment_compound", data);
    if (data["status"] == "success"){
        g_data["equip_fragment"][other]["num"] = g_data["equip_fragment"][other]["num"] - num;
        $("input[name='suipian_equip']").change();
        alert_error_modal("合成成功.");
    }
};


$("input[name='suipian_equip']").on("change", function(e){
    e.preventDefault();
    var fragment_array = g_data["equip_fragment"];
    var fragment_type = $("input[name='suipian_equip']:checked").val();
    var str_html = "";
    for(var fa=0; fa<fragment_array.length; fa++){
        var fragment_cid = fragment_array[fa]["cid"];
        var equip_frag_config = null;
        if (fragment_cid in GLOBAL_JSON_DATA["equip_fragment"]){
            equip_frag_config = GLOBAL_JSON_DATA["equip_fragment"][fragment_cid];
        }
        else{
            equip_frag_config = GLOBAL_JSON_DATA["treasure2_fragment"][fragment_cid];
        }
        var fragment_num = fragment_array[fa]["num"];
        var fragment_equip = equip_frag_config["equip"];
        var equip_config = GLOBAL_JSON_DATA["equip"][fragment_equip];
        var equip_type2 = equip_config["type"];
        var fragment_num2 = equip_frag_config["num"];
        var fragment_name = equip_frag_config["name"];
        if (fragment_num > 0){
            if (fragment_type == "1") {
                if (equip_type2 == "weapon" || equip_type2 == "armor" || equip_type2 == "accessory" || equip_type2 == "head") {
                    str_html += "<tr>";
                    str_html += "<td>" + fragment_name + "</td>";
                    str_html += "<td>" + fragment_num + "/" + fragment_num2 + "</td>";
                    str_html += "<td>";
                    if (fragment_num >= fragment_num2) {
                        str_html += "<button class='btn blue' onclick='fragment_compound(" + fa + "," + fragment_num2 + "," + fragment_equip + ")'>合成</button>";
                    }
                    str_html += "</td>";
                    str_html += "</tr>";
                }
            }
            else {
                if (equip_type2 == "horse" || equip_type2 == "treasure") {
                    str_html += "<tr>";
                    str_html += "<td>" + fragment_name + "</td>";
                    str_html += "<td>" + fragment_num + "/" + fragment_num2 + "</td>";
                    str_html += "<td>";
                    if (fragment_num >= fragment_num2) {
                        str_html += "<button class='btn yellow' onclick='fragment_compound(" + fragment_equip + ")'>合成</button>";
                    }
                    str_html += "</td>";
                    str_html += "</tr>";
                }
            }
        }
    }
    $("#fragment_list").html(str_html);
});

function use_props(props_cid){
    var data = common_request([props_cid, 1], 1201);
    console.log("use_props", data);
    if(data["status"] == "success"){
        g_data["props"][props_cid]["num"] -=1;
        var some_data = $.parseJSON(data["data"]);
        g_data["role"]["coin"] += some_data["coin"];
        g_data["role"]["energy"] += some_data["energy"];
        g_data["role"]["stamina"] += some_data["stamina"];
        setTimeout("load_role_info()", 1000);
    }
}


function display_props(){
    var props_array = g_data["props"];
    var str_html = "";
    var str_html1 = "";
    str_html1 += "<p>[银币] *" +  g_data["role"]["coin"] + "</p>";
    str_html1 += "<p>[元宝] *" +  g_data["role"]["gold"] + "</p>";
    for(var pa in props_array){
        str_html += "<tr>";
        var props_name = GLOBAL_JSON_DATA["props"][pa]["name"];
        var props_type = GLOBAL_JSON_DATA["props"][pa]["type"];
        var props_num = props_array[pa]["num"];
        str_html1 += "<p>[" + props_name + "] *" +  props_num + "</p>";
        str_html += "<td>" + props_name + "</td>";
        str_html += "<td>" + props_num + "</td>";
        str_html += "<td>";
        if (props_type == "value") {
            str_html += "<button class='btn blue' onclick='use_props(" + pa + ")'>" + "使用" + "</button>";
        }
        else if (props_type == "box") {
            str_html += "<button class='btn blue' onclick='use_props(" + pa + ")'>" + "打开" + "</button>";
        }
        str_html += "</td>";
        str_html += "</tr>";
    }
    $("#consume_props_list").html(str_html1);
    $("#props_list").html(str_html);
}


$("#a_props").on("click", function(e){
    e.preventDefault();
    display_props();
});

$("input[name='baowu_type']").on("change", function(e){
    e.preventDefault();
    var equip_array = g_data["equip"];
    var temp_str = $("input[name='baowu_type']:checked").val();
    var str_html = "";
    for (var ea in equip_array) {
        var equip_cid = equip_array[ea]["cid"];
        var equip_name = GLOBAL_JSON_DATA["equip"][equip_cid]["name"];
        var level1 = equip_array[ea]["level1"];
        var level2 = equip_array[ea]["level2"];

        var equip_type = GLOBAL_JSON_DATA["equip"][equip_cid]["type"];
        if (equip_type == "treasure" || equip_type == "horse") {
            if (temp_str != "all") {
                if (temp_str == equip_type) {
                    str_html += "<tr>";
                    str_html += "<td>" + equip_name + "+" + level2 + "</td>";
                    str_html += "<td>" + level1 + "</td>";
                    var g_name = "";
                    if (equip_array[ea].hasOwnProperty("g_cid")) {
                        g_name = GLOBAL_JSON_DATA["general"][equip_array[ea]["g_cid"]]["name"];
                    }
                    str_html += "<td>" + g_name + "</td>";
                    str_html += "<td><a class=\"btn blue btn-xs\" onclick='jinglian_common(" + ea + ")'>精炼</a>" +
                        "<a class=\"btn yellow btn-xs\" onclick='qianghua_common(" + ea + ")'>强化</a></td>";
                }
            }
            else {
                str_html += "<tr>";
                str_html += "<td>" + equip_name + "+" + level2 + "</td>";
                str_html += "<td>" + level1 + "</td>";
                var g_name1 = "";
                if (equip_array[ea].hasOwnProperty("g_cid")) {
                    g_name1 = GLOBAL_JSON_DATA["general"][equip_array[ea]["g_cid"]]["name"];
                }
                str_html += "<td>" + g_name1 + "</td>";
                str_html += "<td><a class=\"btn blue btn-xs\" onclick='jinglian_common(" + ea + ")'>精炼</a>" +
                        "<a class=\"btn yellow btn-xs\" onclick='qianghua_common(" + ea + ")'>强化</a></td>";
                str_html += "</tr>";
            }
        }
    }
    $("#horse_list").html(str_html);
});

function jinglian_common(e_id){
    $("#equip_id").val(e_id);
    $("#horse_jinglian").click();
}

function qianghua_common(e_id){
    $("#equip_id").val(e_id);
    $("#strength_horse").click();
}

function equip_strengthen(eid, method){
    var req_data = {
        "iid": eid,
        "method": method
    };
    console.log(req_data);
    var data = common_request(req_data, 1101);
    console.log("equipStrengthen", data);

    if (data["status"] == "success"){
        load_role_info();
        $("input[name='equip_type']").click();
    }
}

$("input[name='equip_type']").on("click", function(e){
    e.preventDefault();
    var equip_array = g_data["equip"];
    var temp_str = $("input[name='equip_type']:checked").val();
    console.log("temp_str", temp_str);
    var str_html = "";
    var baptize_equip_quality = GLOBAL_JSON_DATA["global_kv"]["baptize_equip_quality"]["value"];
    for (var ea in equip_array) {
        var equip_cid = equip_array[ea]["cid"];
        var equip_name = GLOBAL_JSON_DATA["equip"][equip_cid]["name"];
        var level1 = equip_array[ea]["level1"];
        var level2 = equip_array[ea]["level2"];
        var equip_qua = GLOBAL_JSON_DATA["equip"][equip_cid]["quality"];
        var equip_type = GLOBAL_JSON_DATA["equip"][equip_cid]["type"];
        if (equip_type == "weapon" || equip_type == "armor" || equip_type == "accessory" || equip_type == "head") {
            if (temp_str != "all") {
                if (temp_str == equip_type) {
                    str_html += "<tr>";
                    str_html += "<td><label class='" + quality_css3[equip_qua] +  "'>" + equip_name + "+" + level2 + "</label></td>";
                    str_html += "<td>" + level1 + "</td>";
                    var g_name = "";
                    if (equip_array[ea].hasOwnProperty("g_cid")) {
                        g_name = GLOBAL_JSON_DATA["general"][equip_array[ea]["g_cid"]]["name"];
                    }
                    str_html += "<td>" + g_name + "</td>";
                    str_html += "<td><button class=\"btn blue btn-xs\" onclick='equip_strengthen(" + ea + "," + 1 + ")'>一键强化</button>" +
                        "&nbsp;&nbsp;<button class=\"btn blue btn-xs\" onclick='equip_strengthen(" + ea + "," + 0 + ")'>强化</button>";
                    if (equip_qua >= baptize_equip_quality)
                        str_html += "&nbsp;&nbsp;<button class=\"btn yellow btn-xs\" onclick='xilian_zhuangbei(" + ea + ")'>洗练</button></td>";
                    str_html += "</tr>";
                }
            }
            else {
                str_html += "<tr>";
                str_html += "<td><label class='" + quality_css3[equip_qua] +  "'>" + equip_name + "+" + level2 + "</label></td>";
                str_html += "<td>" + level1 + "</td>";
                var g_name1 = "";
                if (equip_array[ea].hasOwnProperty("g_cid")) {
                    g_name1 = GLOBAL_JSON_DATA["general"][equip_array[ea]["g_cid"]]["name"];
                }
                str_html += "<td>" + g_name1 + "</td>";
                str_html += "<td><button class=\"btn blue btn-xs\" onclick='equip_strengthen(" + ea + "," + 1 + ")'>一键强化</button>" +
                        "&nbsp;&nbsp;<button class=\"btn blue btn-xs\" onclick='equip_strengthen(" + ea + "," + 0 + ")'>强化</button>";
                if (equip_qua >= baptize_equip_quality)
                        str_html += "&nbsp;&nbsp;<button class=\"btn yellow btn-xs\" onclick='xilian_zhuangbei(" + ea + ")'>洗练</button></td>";
                str_html += "</tr>";
            }
        }
    }

    $("#equip_list").html(str_html);
});

function common_request(data, type){
    var role_id = $("#select_role").val();
    var return_data = null;
    $.ajax({
        type: 'get',
        url: '/simulator/common',
        data: {
            server_id: SERVER_ID,
            role_id: role_id,
            type: type,
            data: JSON.stringify(data)
        },
        dataType: 'JSON',
        async: false,
        success: function (data){
            return_data = data;
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
    return return_data;
}

function alert_error_modal(message){
    Common.alert_message($("#error_modal"), 1, message);
    setTimeout('$("#error_modal").modal("hide")', 1000);
}

//一键装备
$("#btn_yijianzb").on("click", function(e){
    e.preventDefault();
    var slot =parseInt($("#slot_id").val());
    var data = common_request([slot, 2], 1007);
    console.log("yijianzhuangbei", data);
    if(data["status"] == "success"){
        alert_error_modal("一键装备成功");
        setTimeout("load_role_info()", 1000);
        insert_log("一键装备");
        display_log();
    }
});


//一键强化
$("#btn_yijianstrength").on("click", function(e){
    e.preventDefault();
    var general_id = parseInt($("#general_id").val());
    var data = common_request([general_id], 1109);
    console.log("btn_yijianstrength", data);
    if(data["status"] == "success"){
        alert_error_modal("一键强化成功");
        setTimeout("load_role_info()", 1000);
        insert_log("一键强化");
        display_log();
    }
});

$("#btn_yijianjihuo").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(3);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{

    }
});

function display_general(){
    var str_html = "";
    for(var g in g_data["general"]){
        if (!g_data["general"][g].hasOwnProperty("slot")){
            var general_cid = g_data["general"][g]["cid"];
            var level1 = g_data["general"][g]["level1"];
            var general_name = GLOBAL_JSON_DATA["general"][general_cid]["name"];
            str_html += "<option value='" + g + "'>" + level1 + "级" + general_name + "</option>";
        }
    }
    $("#select_change_general").html(str_html);
}


$("#btn_change").on("click", function(e){
    e.preventDefault();
    $("#change_general_modal").modal("show");
});


$("#btn_change_confirm").on("click", function(e){
    e.preventDefault();
    var iid = parseInt($("#select_change_general").val());
    var pos1 = parseInt($("#slot_id").val());
    var req_data = {
        "pos1": pos1,
        "iid": iid,
        "pos2": 0
    };
    var data = common_request(req_data, 1003);
    if (data["status"] == "success"){
        $("#change_general_modal").modal("hide");
        setTimeout("load_role_info()", 1000);
    }
});

function return_number_html(a){
    var temp1 = "";
    if (a > 0) {
        temp1 = "<span class='badge badge-success'>" + "+" + a + "</span>"
    }
    else {
        temp1 = "<span class='badge badge-important'>" + a + "</span>"
    }
    return temp1;
}


function peiyang(t){
    var gid = parseInt($("#general_id").val());
    var temp_type = $("input[name='peiyang_type']:checked").val();
    var method = 0;
    var peiyang_jian = 0;
    if (temp_type == "1"){
        if (t == 1){
            peiyang_jian = 1;
            method = 1;
        }
        else{
            peiyang_jian = 10;
            method = 2;
        }
    }
    else{
        if (t == 1){
            peiyang_jian = 1;
            method = 3;
        }
        else{
            peiyang_jian = 10;
            method = 4;
        }
    }
    var req_data = {
        "id": gid,
        "method": method
    };
    var data = common_request(req_data, 1013);
    console.log("peiyang_data", data);
    if (data["status"] == "success"){
        var c_data = $.parseJSON(data["data"]);
        var temp_data = c_data["generals"][0];
        var atk = temp_data["atk"];
        var hp = temp_data["hp"];
        var defense = temp_data["defense"];
        var speed = temp_data["speed"];
        var potential = temp_data["potential"];

        var py_atk = parseInt($("#py_atk").html());
        var py_hp = parseInt($("#py_hp").html());
        var py_def = parseInt($("#py_def").html());
        var py_speed = parseInt($("#py_speed").html());
        var py_potential = parseInt($("#py_potential").html());

        var add_atk = atk - py_atk;
        var add_hp = hp - py_hp;
        var add_def = defense - py_def;
        var add_speed = speed - py_speed;
        var add_potential = potential - py_potential;
        if (add_atk != 0){
            $("#py_add_atk").html(return_number_html(add_atk));
        }
        if (add_hp != 0){
            $("#py_add_hp").html(return_number_html(add_hp));
        }
        if (add_def != 0){
            $("#py_add_def").html(return_number_html(add_def));
        }
        if (add_speed != 0){
            $("#py_add_speed").html(return_number_html(add_speed));
        }
        if (add_potential != 0){
            $("#py_add_potential").html(return_number_html(add_potential));
        }
        $("#peiyang_button").removeClass("hidden");
        $("#btn_peiyang_group").addClass("hidden");
        $("#peiyangdan_jian").html("-" + peiyang_jian);
    }
}

function clear_add_data(){
    $("#py_add_atk").html("");
    $("#py_add_hp").html("");
    $("#py_add_def").html("");
    $("#py_add_speed").html("");
    $("#py_add_potential").html("");
    $("#peiyangdan_jian").html("");
}

$("#peiyang_cancle").on("click", function(e){
    e.preventDefault();
    $("#peiyang_button").addClass("hidden");
    $("#btn_peiyang_group").removeClass("hidden");
    clear_add_data();
});

$("#peiyang_confirm").on("click", function(e){
    e.preventDefault();
    var general_id = parseInt($("#general_id").val());
    var req_data = {"opt": 1, "id": general_id};
    var data = common_request(req_data, 1014);
    $("#peiyang_button").addClass("hidden");
    clear_add_data();
    if (data["status"] == "success"){
        $("#btn_peiyang_group").removeClass("hidden");
        load_role_info();
    }
});

$("#peiyang_one").on("click", function(e){
    e.preventDefault();
    peiyang(1);
});

$("#peiyang_ten").on("click", function(e){
    e.preventDefault();
    peiyang(2);
});

$("#btn_tupo").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(52);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{
        var general_cid = parseInt($("#general_cid").val());
        var data = common_request([general_cid], 1017);
        console.log(data);
        if (data["status"] == "success"){
            load_role_info();
        }
    }
});

function check_level_open(build_id){
    var role_level = g_data["role"]["level"];
    var limit_level = GLOBAL_JSON_DATA["build"][build_id]["level"];
    if (role_level <= limit_level){
        return limit_level;
    }
    else{
        return 0;
    }
}

$("#btn_shengji").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(135);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{
        for (var i = 0; i < GENERAL_UPGRADE_PROPS.length; i++) {
            if (g_data["props"].hasOwnProperty(GENERAL_UPGRADE_PROPS[i])) {
                var props_name = GLOBAL_JSON_DATA["props"][GENERAL_UPGRADE_PROPS[i]]["name"];
                var num = g_data["props"][GENERAL_UPGRADE_PROPS[i]]["num"];
                var $jingyandan = $("#jingyandan_" + i);
                $jingyandan.html(props_name + "*" + num);
            }
        }
        $("#shengji_up").html("");
        $("#shengji_general_modal").modal("show");
    }
});


var shengji_jingyan_temp = [0, 0, 0, 0];
var temp_level = 0;
var shengji_up = 0;
var shengji_max_exp = 0;


$("#btn_yijianadd").on("click", function(e){
    e.preventDefault();

});

$("#btn_shengji_confirm").on("click", function(e){
    e.preventDefault();
    var general_id = parseInt($("#general_id").val());
    var req_data = {
        "iid": general_id,
        "props": shengji_jingyan_temp
    };
    var slot_id = $("#slot_id").val();
    var data = common_request(req_data, 1038);
    if (data["status"] == "success"){
        var all_data = $.parseJSON(data["data"]);
        var level1 = all_data["generals"][0]["level1"];
        temp_level = 0;
        shengji_up = 0;
        shengji_max_exp = 0;
        $("#shengji_level1").html(level1);
        $("#shengji_up").html("");
        load_general_info(slot_id, $("#general_id").val());
    }
});


$("#strength_equip").on("click", function(e){
    e.preventDefault();
    var equip_id = parseInt($("#equip_id").val());
    equip_strengthen(equip_id, 1);
});



$("#shengji_general_modal .form-group .btn-default").on("click", function(e){
    e.preventDefault();
    var btn_id = $(this).attr("id");
    var btn_num = btn_id.split("_")[1];
    shengji_jingyan_temp[btn_num] += 1;
    var shengji_num_str = $(this).html();
    var cailiao_name = shengji_num_str.split("*")[0];
    var shengji_num = parseInt(shengji_num_str.split("*")[1]);
    $(this).html(cailiao_name + "*" + (shengji_num - 1));

    var exp_num = GENERAL_PROPS_EXP[btn_num];
    var $shengji_exp = $("#shengji_exp");
    var shengji_exp = parseInt($shengji_exp.html());
    var $shengji_max_exp = $("#shengji_max_exp");
    if (shengji_max_exp == 0){
        shengji_max_exp = parseInt($shengji_max_exp.html());
    }
    var all_exp = exp_num + shengji_exp;
    if  (temp_level == 0){
        temp_level = parseInt($("#shengji_level1").html());
    }
    var general_cid = parseInt($("#general_cid").val());
    var quality = GLOBAL_JSON_DATA["general"][general_cid]["quality"];
    var temp_exp = 0;
    while (all_exp > shengji_max_exp){
        temp_exp = all_exp - shengji_max_exp;
        all_exp = temp_exp;
        temp_level += 1;
        shengji_max_exp = get_level_max_exp(quality, general_cid, temp_level);
        shengji_up += 1;
    }
    if (shengji_up > 0){
        $("#shengji_up").html("+" + shengji_up);
    }
    $shengji_exp.html(all_exp);
    $shengji_max_exp.html(shengji_max_exp);
});

$("#btn_peiyang").on("click", function(e){
    e.preventDefault();
    var check_level = check_level_open(51);
    if (check_level != 0){
        alert_error_modal(check_level + "级开启");
    }
    else{
        if (g_data["props"].hasOwnProperty(peiyangdan_cid)) {
            var peiyangdan_num = g_data["props"][peiyangdan_cid]["num"];
            $("#peiyangdan_num").html(peiyangdan_num);
        }
        $("#peiyang_general_modal").modal("show");
    }

});


$("#exit_game").on("click", function(e){
    e.preventDefault();
    $("#choose_role_modal").modal("show");
});
