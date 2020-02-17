/**
 * Created by wangrui on 15/10/19.
 */

getGameServerData($("#game_server"), 1);

var BATTLE_JSON = {
    "name": "test",
    "level": "",
    "data": {
        "slot":[],
        "cheer": []
    }
};

var quality_css = {
    2: "btn green",
    3: "btn blue",
    4: "btn purple",
    5: "btn yellow"
};

var quality_css2 = {
    2: "badge-success",
    3: "badge-info",
    4: "badge-purple",
    5: "badge-warning"
};

var level1 = 1;
var level2 = 0;
var slot_num = 1;
var cheer_num = 0;
var corps_level = 2;

$("#corps_level").val(corps_level);
create_del_modal($("#battle_modal"), "是否删除此记录", "confirm_del");

var html_general = $("#general_table").html();

var getbattle = function () {
    var sAjaxSource = "/getbattledata";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "编号"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "名称"
        },
        {
            "mDataProp": "level",
            'sClass': 'center',
            "sTitle": "战队等级"
        },
        {
            "mDataProp": "power",
            'sClass': 'center',
            "sTitle": "战斗力"
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "sTitle": "描述"
        },
        {
            "mDataProp": "json",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_battle(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button><button onclick=\"del_battle(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    dataTablePage($("#battle_table"), aoColumns, sAjaxSource, {}, false, null);
};
getbattle();


var init_cheer_data = function(){
    var str_html = "";
    for(var i=0; i<8; i++){
        var temp_html = "<td><button onclick='cheer_btn(this)' id='cheer_" + i + "' class='btn default'>助威" + (i + 1) + "</button><div></div></td>";
        if ((i+1) % 2 != 0){
            str_html += "<tr>";
            str_html += temp_html;
        }
        else{
            str_html += temp_html;
            str_html += "<tr>";
        }
    }
    $("#cheer_list").html(str_html);
};
init_cheer_data();

var JSON_DATA = {};
var CONFIG = ["general", "equip", "role_exp", "suit", "combskill"];
var LEAD_DATA = {
    2: [],
    3: [],
    4: [],
    5: []
};
var RANDOM_GENERAL = {};
var EQUIP_TYPE = ["horse", "treasure", "weapon", "head", "armor", "accessory"];
var quality_3 = {};
var quality_4 = {};
var quality_5 = {};

var str_quality = {
   3: "蓝色品质",
   4: "紫色品质",
   5: "橙色品质"
};

function init_quality(){
    var str_html = "";
    for (var i in str_quality){
        str_html += "<option value=\"" + i + "\">" + str_quality[i] + "</option>";
    }
    $("#quality_type").html(str_html);
    $("#quality_type").change();
}


var set_quality_general = function(){

    for (var d in JSON_DATA["general"]){
        var general_id = parseInt(d);
        var temp_data = JSON_DATA["general"][d];
        if (temp_data["battle"] == 1){
            var quality = temp_data["quality"];
            if (general_id > 10200) {
                if (quality == 3) {
                    quality_3[general_id] = JSON_DATA["general"][d];
                }
                else if (quality == 4) {
                    quality_4[general_id] = JSON_DATA["general"][d];
                }
                else if (quality == 5) {
                    quality_5[general_id] = JSON_DATA["general"][d];
                }
                if (!RANDOM_GENERAL.hasOwnProperty(quality)){
                    RANDOM_GENERAL[quality] = [];
                }
                RANDOM_GENERAL[quality].push(JSON_DATA["general"][d]);
            }
            else{
                LEAD_DATA[quality].push(JSON_DATA["general"][d]);
            }
        }
    }

    var suit_html = "";
    for(var s in JSON_DATA["suit"]){
        suit_html += "<option value='" + s + "'>" + JSON_DATA["suit"][s]["name"] + "</option>"
    }
    //设置宝物、装备
    var horse_html = "";
    var treasure_html = "";
    var weapon_html = "";
    var head_html = "";
    var armor_html = "";
    var accessory_html = "";
    var temp_html = "<option value='0'>无装备</option>";
    for(var e in JSON_DATA["equip"]){
        var equip_type = JSON_DATA["equip"][e]["type"];
        var equip_quality = JSON_DATA["equip"][e]["quality"];
        var s_temp_html = "<option value='" + e + "'>" + equip_quality + "星:" + JSON_DATA["equip"][e]["name"] + "</option>";

        if (equip_type == "horse"){
            horse_html += s_temp_html;
        }
        else if (equip_type == "treasure"){
            treasure_html += s_temp_html;
        }
        else if (equip_type == "weapon"){
            weapon_html +=  s_temp_html;
        }
        else if (equip_type == "head"){
            head_html +=  s_temp_html;
        }
        else if (equip_type == "armor"){
            armor_html += s_temp_html;
        }
        else if (equip_type == "accessory"){
            accessory_html += s_temp_html;
        }
    }
    var str_html = MakeOptionList2(JSON_DATA["general"], MyGetDataFunc);
    $("#general_t").html(str_html);
    $("#general_cheer").html(str_html);

    $("#horse").html(temp_html + horse_html);
    $("#treasure").html(temp_html + treasure_html);
    $("#weapon").html(temp_html + weapon_html);
    $("#head").html(temp_html + head_html);
    $("#armor").html(temp_html + armor_html);
    $("#accessory").html(temp_html + accessory_html);
};


var init_json_data = function(){
    var server_id = $("#game_server").val();
    $.ajax({
            type: 'get',
            url: "/queryjsondatabyserver",
            data: {
                server_id: server_id,
                type: JSON.stringify(CONFIG)
            },
            dataType: 'JSON',
            success: function (data) {
                JSON_DATA = data;
                set_quality_general();
                init_quality();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};
init_json_data();


$("#quality_type").change(function(){
    var quality_a = $(this).val();
    var temp_data = null;
    if (quality_a == "3"){
        temp_data = quality_3;
    }
    else if (quality_a == "4"){
        temp_data = quality_4;
    }
    else if (quality_a == "5"){
        temp_data = quality_5;
    }
    var str_html = MakeOptionList(temp_data, MyGetDataFunc);
    var $quality_general = $("#quality_general");
    $quality_general.html(str_html);
    $quality_general.change();
});

$("#quality_general").on("change", function(e){
    e.preventDefault();
    var qua_value = $(this).val();
    var selectText = $(this).find("option:selected").text();
    var quality = $("#quality_type").val();
    var html1 = "<span class='badge " + quality_css2[quality] + "'>" + selectText + "</span>";
    $("#general_choose").html(html1);
    $("#hidden_id").val(qua_value);
});

function isEmptyObject(o){
    for(var n in o){

        return false;
    }
    return true;
}

var display_general = function(){
    var slot_data = BATTLE_JSON["data"]["slot"];
    for (var s=0; s < slot_data.length; s++){
        var $slot = $("#slot_" + s);
        if (isEmptyObject(slot_data[s]) == false){
            $slot.html(JSON_DATA["general"][slot_data[s]["cid"]]["name"]);
            $slot.removeClass();
            var quality = JSON_DATA["general"][slot_data[s]["cid"]]["quality"];
            $slot.addClass(quality_css[quality]);

            var str_html = "";
            str_html += "<span class='label label-default'> LV:" + slot_data[s]["level1"] + "</span>";
            str_html += "<span class='label label-default'> +" + slot_data[s]["level2"] + "</span>";
            for(var c in EQUIP_TYPE){
                if (slot_data[s].hasOwnProperty(EQUIP_TYPE[c])){
                    var e_cid = slot_data[s][EQUIP_TYPE[c]]["cid"];
                    var e_quality = JSON_DATA["equip"][e_cid]["quality"];
                    var equip_name = JSON_DATA["equip"][e_cid]["name"];
                    str_html += "<span class='badge " + quality_css2[e_quality] + "'>" + equip_name + "</span>";
                }
            }
            if($slot.siblings('button').length == 0){
                $slot.after("<button onclick=\"del_slot(" + s +  ")\"type=\"button\" class=\"close\"></button>");
            }
            $slot.siblings('div').html("");
            $slot.siblings('div').html(str_html);
        }
        else{
            $slot.html("槽" + (s + 1));
            $slot.removeClass();
            $slot.addClass("btn default");
            $slot.parent().html($slot);
            $slot.parent().append("<div></div>");
            $slot.attr("onclick", "click_btn(this)");
        }
    }

    var cheer_data = BATTLE_JSON["data"]["cheer"];
    for (var k = 0; k < cheer_data.length; k++){
        var $cheer = $("#cheer_" + k);
        if (isEmptyObject(cheer_data[k]) == false){
            var str_html1 = "";
            str_html1 += "<span class='label label-default'> LV:" + cheer_data[k]["level1"] + "</span>";
            str_html1 += "<span class='label label-default'> +" + cheer_data[k]["level2"] + "</span>";

            $cheer.html(JSON_DATA["general"][cheer_data[k]["cid"]]["name"]);
            $cheer.removeClass();
            var quality2 = JSON_DATA["general"][cheer_data[k]["cid"]]["quality"];
            $cheer.addClass(quality_css[quality2]);

            if ($cheer.siblings('button').length == 0) {
                $cheer.after("<button onclick=\"del_cheer(" + k + ")\"type=\"button\" class=\"close\"></button>");
            }
            $cheer.siblings('div').html("");
            $cheer.siblings('div').html(str_html1);
        }
        else{
            $cheer.html("助威" + (k + 1));
            $cheer.removeClass();
            $cheer.addClass("btn default");
            $cheer.parent().html($cheer);
            $slot.parent().append("<div></div>");
        }
    }
};





$("#random_general").on("click", function(e){
    e.preventDefault();
    BATTLE_JSON["data"]["slot"] = [];

    corps_level = $("#corps_level").val();

    var $alert = $(".alert-danger");
    var $condition_form = $("#condition_form");
    if (corps_level == "" || corps_level == undefined || corps_level == "1"){
        $(".alert span").html("战队等级不能为空和1级");
        $($alert, $condition_form).show();
        return;
    }

    var general_id = $("#hidden_id").val();
    if (general_id == "" || general_id == undefined){
        $(".alert span").html("请选择武将");
        $($alert, $condition_form).show();
        return;
    }
    //隐藏错误信息
    $($alert, $condition_form).hide();

    //设置战队等级
    BATTLE_JSON["level"] = parseInt(corps_level);

    //武将个数
    slot_num = JSON_DATA["role_exp"][corps_level]["slotnum"];
    // 助威个数
    cheer_num = JSON_DATA["role_exp"][corps_level]["cheernum"];
    var choose_general_quality = JSON_DATA["general"][general_id]["quality"];

    //设置主角
    var lead_general = LEAD_DATA[choose_general_quality][Math.floor(Math.random() * LEAD_DATA[choose_general_quality].length)];
    level1 = parseInt(corps_level) * 2;

    var cid_arr = [lead_general["generalid"], parseInt(general_id)];
    var cheer_arr = [];

    //添加合体技
    var commonskill = JSON_DATA["general"][general_id]["combskillid"];
    if (commonskill != 0) {
        for (var k = 1; k <= 3; k++) {
            var ids = JSON_DATA["combskill"][commonskill]["cid" + k];
            if (cid_arr.length < slot_num) {
                if (ids != "")
                    cid_arr.push(parseInt(ids));
            }
        }
    }
    //选择武将缘
    for (var m = 1; m < 19; m++) {
        var cond_type2 = JSON_DATA["general"][general_id]["cond" + m + "type"];
        var cond_ids_t = JSON_DATA["general"][general_id]["cond" + m + "ids"];
        if (cond_type2 == "person") {
            var cond_ids2 = cond_ids_t.split(";");
            for (var c in cond_ids2) {
                if (cid_arr.length < slot_num) {
                    cid_arr.push(parseInt(cond_ids2[c]));
                }
                else {
                    if (cheer_arr.length < cheer_num){
                        cheer_arr.push(parseInt(cond_ids2[c]));
                    }
                }
            }
        }
    }
    console.log(choose_general_quality);
    //武将如果不够， 随机
    var new_cid_arr = [];
    if (new_cid_arr.length != slot_num + cheer_num){
        while (1){
            new_cid_arr = unique(cid_arr);
            if (new_cid_arr.length == slot_num + cheer_num){
                break;
            }
            var s_temp =  RANDOM_GENERAL[choose_general_quality][Math.floor(Math.random() * RANDOM_GENERAL[choose_general_quality].length)]["generalid"];
            cid_arr.push(s_temp);
        }
    }
    else{
        new_cid_arr = cid_arr;
    }


    var slot_arr = new_cid_arr.splice(0, slot_num);
    if (cheer_num != 0){
        set_cheer_general(new_cid_arr);
    }
    set_slot_general(slot_arr);
    display_general();
});

var set_cheer_general = function(cheer_arr){
    for (var c in cheer_arr){
        set_cheer(c, cheer_arr[c], level1, level2);
    }
};

var set_cheer = function(num, cid, lv1, lv2){
    BATTLE_JSON["data"]["cheer"][num] = {
        "cid": cid,
        "level1": lv1,
        "level2": lv2
    };
};


function unique(arr) {
    var result = [], hash = {};
    for (var i = 0, elem; (elem = arr[i]) != null; i++) {
        if (!hash[elem]) {
            result.push(elem);
            hash[elem] = true;
        }
    }
    return result;
}


var set_slot_general = function(cid_arr){
    for(var cid in cid_arr){
        set_general(cid, cid_arr[cid], level1, level2);
        for (var n = 1; n < 19; n++) {
            var cond_type3 = JSON_DATA["general"][cid_arr[cid]]["cond" + n + "type"];
            var cond_ids_d = JSON_DATA["general"][cid_arr[cid]]["cond" + n + "ids"];
            if (cond_type3 != ""){
                if (cond_type3 != "person"){
                    if (cond_type3 == "equip"){
                        var equip_type = JSON_DATA["equip"][cond_ids_d]["type"];
                        set_equip(cid, equip_type, parseInt(cond_ids_d), level1, level2);
                    }
                    else{
                        set_equip(cid, cond_type3, parseInt(cond_ids_d), level1, level2);
                    }
                }
            }
        }
    }

};


var set_equip = function(num, c_type, cid, level1, level2){
   BATTLE_JSON["data"]["slot"][num][c_type] = {
       "cid": cid,
        "level1": level1,
        "level2": level2
   }
};

var set_general = function(num, cid, level1, level2){
    BATTLE_JSON["data"]["slot"][num] = {
        "cid": cid,
        "level1": level1,
        "level2": level2
    };
};

var click_btn = function(s_this){

    var slot_id = $(s_this).attr('id');
    var slot_split = slot_id.split("_");
    var slot_n = parseInt(slot_split[1]);
    if ((slot_n + 1) > slot_num){
        Common.alert_message($("#error_modal"), 0, "上阵个数必须为" + slot_num + "个");
        return;
    }
    var slot_data = BATTLE_JSON["data"]["slot"][slot_n];
    var cid = "0";
    if(slot_data.hasOwnProperty("cid")){
        cid = slot_data["cid"];
    }
    var general_level1 = level1;
    if(slot_data.hasOwnProperty("level1")){
        general_level1 = slot_data["level1"];
    }
    var general_level2 = 0;
    if (slot_data.hasOwnProperty("level2")){
        general_level2 = slot_data["level2"];
    }

    $("#general_t").val(cid);
    $("#general_level1").val(general_level1);
    $("#general_level2").val(general_level2);

    $("#hidden_slot").val(slot_n);
    set_property(slot_data);
    $("#general_modal").modal("show");
};


//$("#general_info tr td .btn").on("click", function(e){
//    e.preventDefault();
//    click_btn($(this));
//});

var cheer_btn = function(btn){
    var cheer_id = $(btn).attr('id');
    var cheer_split = cheer_id.split("_");
    var cheer_n = parseInt(cheer_split[1]);
    if ((cheer_n + 1) > cheer_num){
        Common.alert_message($("#error_modal"), 0, "助阵个数必须为" + cheer_num + "个");
        return;
    }
    var cheer_data = BATTLE_JSON["data"]["cheer"][cheer_n];
    var cid = cheer_data["cid"];
    var cheer_level1 = cheer_data["level1"];
    var cheer_level2 = cheer_data["level2"];

    $("#general_cheer").val(cid);
    $("#hidden_cheer").val(cheer_n);
    $("#cheer_level1").val(cheer_level1);
    $("#cheer_level2").val(cheer_level2);
    $("#cheer_modal").modal("show");
};


var set_property = function(s_data){
    for (var et in EQUIP_TYPE){
        var e_id = "0";
        var h_level1 = "1";
        var h_level2 = "0";
        if(s_data.hasOwnProperty(EQUIP_TYPE[et])){
            e_id = s_data[EQUIP_TYPE[et]]["cid"];
            h_level1 = s_data[EQUIP_TYPE[et]]["level1"];
            h_level2 = s_data[EQUIP_TYPE[et]]["level2"];

        }
        $("#" + EQUIP_TYPE[et]).val(e_id);
        $("#" + EQUIP_TYPE[et] + "_" + "level1").val(h_level1);
        $("#" + EQUIP_TYPE[et] + "_" + "level2").val(h_level2);
    }
};


$("#general_t").on("change", function(e){
    var change_general = $("#general_t").val();
    var general_data = JSON_DATA["general"][change_general];
    for(var et in EQUIP_TYPE){
        $("#" + EQUIP_TYPE[et]).val("0");
    }
    for (var n = 1; n < 19; n++) {
        var cond_type3 = general_data["cond" + n + "type"];
        var cond_ids_d = general_data["cond" + n + "ids"];
        if (cond_type3 != "") {
            if (cond_type3 != "person") {
                if (cond_type3 == "equip") {
                    var equip_type = JSON_DATA["equip"][cond_ids_d]["type"];
                    $("#" + equip_type).val(cond_ids_d);
                    $("#" + equip_type + "_level1").val(level1);
                    $("#" + equip_type + "_level2").val(level2);
                }
                $("#" + cond_type3).val(cond_ids_d);
                $("#" + cond_type3 + "_level1").val(level1);
                $("#" + cond_type3 + "_level2").val(level2);
            }
        }
    }
});


var check_common_general1 = function(slot, general_id){
    for(var s in BATTLE_JSON["data"]["slot"]){
        if (slot != s && BATTLE_JSON["data"]["slot"][s]["cid"] == general_id){
            return true;
        }
    }
    for(var c in BATTLE_JSON["data"]["cheer"]){
        if (BATTLE_JSON["data"]["cheer"][c]["cid"] == general_id){
            return true;
        }
    }
    return false;
};
var check_common_general2 = function(slot, general_id){
    for(var s in BATTLE_JSON["data"]["slot"]){
        if (BATTLE_JSON["data"]["slot"][s]["cid"] == general_id){
            return true;
        }
    }
    for(var c in BATTLE_JSON["data"]["cheer"]){
        if (slot != s && BATTLE_JSON["data"]["cheer"][c]["cid"] == general_id){
            return true;
        }
    }
    return false;
};

$("#btn_confirm").on("click", function(e){
    e.preventDefault();
    var hidden_slot = $("#hidden_slot").val();
    var general_t = parseInt($("#general_t").val());
    var tag = check_common_general1(parseInt(hidden_slot), general_t);
    if (tag){
        $("#general_modal").modal("hide");
        Common.alert_message($("#error_modal"), 0, "武将重复,请重选武将");
        return;
    }
    var general_level1 = parseInt($("#general_level1").val());
    var general_level2 = parseInt($("#general_level2").val());

    BATTLE_JSON["data"]["slot"][hidden_slot]["cid"] = general_t;
    BATTLE_JSON["data"]["slot"][hidden_slot]["level1"] = general_level1;
    BATTLE_JSON["data"]["slot"][hidden_slot]["level2"] = general_level2;

    for(var s in EQUIP_TYPE){
        var equip_t = parseInt($("#" + EQUIP_TYPE[s]).val());
        if(equip_t != 0){
            var equip_level1 = 1;
            equip_level1 = parseInt($("#" + EQUIP_TYPE[s] + "_level1").val());
            var equip_level2 = 1;
            equip_level2 = parseInt($("#" + EQUIP_TYPE[s] + "_level2").val());
            if (!BATTLE_JSON["data"]["slot"][hidden_slot].hasOwnProperty(EQUIP_TYPE[s])){
                BATTLE_JSON["data"]["slot"][hidden_slot][EQUIP_TYPE[s]] = {};
            }
            BATTLE_JSON["data"]["slot"][hidden_slot][EQUIP_TYPE[s]]["cid"] = equip_t;
            BATTLE_JSON["data"]["slot"][hidden_slot][EQUIP_TYPE[s]]["level1"] = equip_level1;
            BATTLE_JSON["data"]["slot"][hidden_slot][EQUIP_TYPE[s]]["level2"] = equip_level2;
        }
        else{
            if (BATTLE_JSON["data"]["slot"][hidden_slot].hasOwnProperty(EQUIP_TYPE[s])){
                delete BATTLE_JSON["data"]["slot"][hidden_slot][EQUIP_TYPE[s]];
            }
        }
    }
    $("#general_modal").modal("hide");
    display_general();
});

var del_slot = function(s){
    BATTLE_JSON["data"]["slot"][s] = {};
    display_general();
};

var del_cheer = function(s){
    BATTLE_JSON["data"]["cheer"][s]["cid"] = {};
    display_general();
};

$("#btn_confirm_cheer").on("click", function(e){
    e.preventDefault();
    var hidden_cheer = $("#hidden_cheer").val();
    var general_cheer = parseInt($("#general_cheer").val());
    var tag = check_common_general2(parseInt(hidden_cheer), general_cheer);
    if (tag){
        $("#cheer_modal").modal("hide");
        Common.alert_message($("#error_modal"), 0, "武将重复,请重选武将");
        return;
    }

    var cheer_level1 = parseInt($("#cheer_level1").val());
    var cheer_level2 = parseInt($("#cheer_level2").val());
    BATTLE_JSON["data"]["cheer"][hidden_cheer]["cid"] = general_cheer;
    BATTLE_JSON["data"]["cheer"][hidden_cheer]["level1"] = cheer_level1;
    BATTLE_JSON["data"]["cheer"][hidden_cheer]["level2"] = cheer_level2;
    $("#cheer_modal").modal("hide");
    display_general();
});


$("#get_power").on("click", function(e){
    e.preventDefault();
    var server_id = $("#game_server").val();
    $.ajax({
            type: 'post',
            url: '/getbattlepower',
            data: {
                server_id: server_id,
                data: JSON.stringify(BATTLE_JSON)
            },
            dataType: 'JSON',
            success: function (data) {
                if(data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else{
                    $("#power_number").html(data["power"]);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

$("#save_battle").on("click", function(e){
    e.preventDefault();
    $("#save_modal").modal("show");
});


$("#btn_save").on("click", function(e){
    e.preventDefault();
    var h_id = $("#h_id").val();
    var server_id = $("#game_server").val();
    var battle_name = $("#battle_name").val();
    var battle_dec = $("#battle_desc").val();
    var hidden_id = $("#hidden_id").val();
    var s_level = $("#corps_level").val();
    $.ajax({
            type: 'post',
            url: '/savebattle',
            data: {
                h_id: h_id,
                server_id: server_id,
                battle_name: battle_name,
                battle_dec: battle_dec,
                cid: hidden_id,
                s_level: s_level,
                json_data: JSON.stringify(BATTLE_JSON)
            },
            dataType: 'JSON',
            success: function (data) {
                if(data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                $("#save_modal").modal("hide");

                $("#li_input").removeClass("active");
                $("#tab_battle_input").removeClass("active");

                $("#li_data").addClass("active");
                $("#tab_battle_data").addClass("active");
                getbattle();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

$("#test_drag").easydrag();

//data

var mod_battle = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#battle_table").dataTable().fnGetData(nRoW);
    BATTLE_JSON = $.parseJSON(data["json"]);
    $("#corps_level").val(data["level"]);
    var cid = data["cid"];
    var quality = JSON_DATA["general"][cid]["quality"];
    var html1 = "<span class='badge " + quality_css2[quality] + "'>" + JSON_DATA["general"][cid]["name"] + "</span>";
    $("#general_choose").html(html1);
    $("#hidden_id").val(cid);
    $("#h_id").val(data["id"]);
    $("#battle_name").val(data["name"]);
    $("#battle_desc").val(data["desc"]);
    $("#power_number").html(data["power"]);

    slot_num = JSON_DATA["role_exp"][data["level"]]["slotnum"];
    cheer_num = JSON_DATA["role_exp"][data["level"]]["cheernum"];
    level1 = data["level"] * 2;
    level2 = 0;

    $("#li_data").removeClass("active");
    $("#tab_battle_data").removeClass("active");

    $("#li_input").addClass("active");
    $("#tab_battle_input").addClass("active");
    display_general();
};

var del_battle = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#battle_table").dataTable().fnGetData(nRoW);
    $('#battle_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_battle(" + data["id"] + ")");
};

var confirm_battle = function(bid){
    $.ajax({
        type: 'get',
        url: '/deletebattle',
        data: {bid: bid},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 0) {
                Common.alert_message($("#error_modal"), 0, "删除失败");
            }
            $('#battle_modal').modal("hide");
            getbattle();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


$("#add_new_battle").on("click", function(e){
    e.preventDefault();

    BATTLE_JSON = {
        "name": "test",
        "level": "",
        "data": {
            "slot":[],
            "cheer": []
        }
    };
    $("#li_data").removeClass("active");
    $("#tab_battle_data").removeClass("active");

    $("#li_input").addClass("active");
    $("#tab_battle_input").addClass("active");

    $("#corps_level").val("2");
    $("#hidden_id").val("");
    $("#battle_name").val("");
    $("#battle_desc").val("");
    $("#power_number").html("0");
    $("#h_id").val("0");
    $("#general_choose").html("");
    $("#general_table").html(html_general);
    init_cheer_data();
});