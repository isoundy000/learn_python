/**
 * Created by wangrui on 15/10/19.
 */

getGameServerData($("#game_server"), 1);

$("#conditon1").slideUp(200);


var BATTLE_JSON = {
    "name": "test",
    "level": "",
    "data": {
        "slot":[],
        "cheer": []
    }
};

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

var init_cheer_data = function(){
    var str_html = "";
    for(var i=0; i<8; i++){
        var temp_html = "<td><button id='cheer_" + i + "' class='btn default'>助威" + (i + 1) + "</button></td>";
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
            },
            error: function () {
                error_func();
            }
        }
    )
};
init_json_data();

var set_quality_general = function(){
    var blue_html = "<option value='0'>蓝色品质</option>";
    var purple_html = "<option value='0'>紫色品质</option>";
    var yellow_html = "<option value='0'>橙色品质</option>";
    var str_html = "";
    for (var d in JSON_DATA["general"]){
        var general_id = parseInt(d);
        if (JSON_DATA["general"][d]["battle"] == 1){
            var quality = JSON_DATA["general"][d]["quality"];
            if (general_id > 10200) {
                if (quality == 3) {
                    blue_html += "<option value='" + d + "'>" + JSON_DATA["general"][d]["name"] + "</option>";
                }
                else if (quality == 4) {
                    purple_html += "<option value='" + d + "'>" + JSON_DATA["general"][d]["name"] + "</option>";
                }
                else if (quality == 5) {
                    yellow_html += "<option value='" + d + "'>" + JSON_DATA["general"][d]["name"] + "</option>";
                }
                if (!RANDOM_GENERAL.hasOwnProperty(quality)){
                    RANDOM_GENERAL[quality] = [];
                }
                RANDOM_GENERAL[quality].push(JSON_DATA["general"][d]);
            }
            else{
                LEAD_DATA[quality].push(JSON_DATA["general"][d]);
            }
            str_html += "<option value='" + d + "'>" + quality + "星:"  + JSON_DATA["general"][d]["name"] + "</option>";
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

    $("#quality_3").html(blue_html);
    $("#quality_4").html(purple_html);
    $("#quality_5").html(yellow_html);

    $("#general_t").html(str_html);
    $("#horse").html(temp_html + horse_html);
    $("#treasure").html(temp_html + treasure_html);
    $("#weapon").html(temp_html + weapon_html);
    $("#head").html(temp_html + head_html);
    $("#armor").html(temp_html + armor_html);
    $("#accessory").html(temp_html + accessory_html);
};

var quality_css = {
    3: "btn blue",
    4: "btn purple",
    5: "btn yellow"
};

var quality_css2 = {
    2: "badge-success",
    3: "badge-info",
    4: "badge-purple",
    5: "badge-danger"
};

var alert_modal = function(){
    Common.alert_message($("#error_modal"), 0, "请选择武将");
};

$("#quality_ div select").on("change", function(e){
    e.preventDefault();
    var qua_value = $(this).val();
    var selectText = $(this).find("option:selected").text();
    if (qua_value == "0"){
        alert_modal();
    }
    else{
        var quality = JSON_DATA["general"][qua_value]["quality"];
        var html1 = "<button type=\"button\" class='btn " + quality_css[quality]  + "'>" + selectText +  "</button>";
        $("#general_choose").html(html1);
        $("#hidden_id").val(qua_value);
    }
});


var DPS = {

};

var level1 = 0;
var level2 = 1;
var slot_num = 1;
var cheer_num = 0;


$("#random_general").on("click", function(e){
    e.preventDefault();
    BATTLE_JSON["data"]["slot"] = [];

    var corps_level = $("#corps_level").val();
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
    var new_cid_arr = [];
    while (1){
        new_cid_arr = unique(cid_arr);
        if (new_cid_arr.length == slot_num + cheer_num){
            break;
        }
        var s_temp =  RANDOM_GENERAL[choose_general_quality][Math.floor(Math.random() * RANDOM_GENERAL[choose_general_quality].length)]["generalid"];
        cid_arr.push(s_temp);
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
                    set_equip(cid, cond_type3, parseInt(cond_ids_d), level1, level2);
                }
            }
        }
    }

};

var display_general = function(){
    var slot_data = BATTLE_JSON["data"]["slot"];

    for (var s=0; s < slot_data.length; s++){
        var $slot = $("#slot_" + s);
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
        $slot.after("<button id=\"del_" + s +  "\"type=\"button\" class=\"close\"></button>");
        $slot.siblings('div').html("");
        $slot.siblings('div').html(str_html);
    }

    var cheer_data = BATTLE_JSON["data"]["cheer"];
    for (var k = 0; k < cheer_data.length; k++){
        var $cheer = $("#cheer_" + k);
        $cheer.html(JSON_DATA["general"][cheer_data[k]["cid"]]["name"]);
        $cheer.removeClass();
        var quality2 = JSON_DATA["general"][cheer_data[k]["cid"]]["quality"];
        $cheer.addClass(quality_css[quality2]);
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



$("#general_info tr td .btn").on("click", function(e){
    e.preventDefault();
    var slot_id = $(this).attr('id');
    var slot_split = slot_id.split("_");
    var slot_n = parseInt(slot_split[1]);
    if ((slot_n + 1) > slot_num){
        Common.alert_message($("#error_modal"), 0, "上阵个数必须为" + slot_num + "个");
        return;
    }
    var slot_data = BATTLE_JSON["data"]["slot"][slot_n];
    var cid = slot_data["cid"];
    var general_level1 = slot_data["level1"];
    var general_level2 = slot_data["level2"];

    $("#general_t").val(cid);
    $("#general_level1").val(general_level1);
    $("#general_level2").val(general_level2);

    $("#hidden_slot").val(slot_n);
    set_property(slot_data);
    $("#general_modal").modal("show");
});

$("#cheer_list tr td button").on("click", function(e){
    e.preventDefault();
    var cheer_id = $(this).attr('id');
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
    $("#cheer_level1").val(cheer_level1);
    $("#cheer_level2").val(cheer_level2);
    $("#cheer_modal").modal("show");
});


var set_property = function(s_data){
    for (var et in EQUIP_TYPE){
        var e_id = "0";
        var h_level1 = "";
        var h_level2 = "";
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
                }
                $("#" + cond_type3).val(cond_ids_d);
                $("#" + cond_type3 + "_level1").val(level1);
                $("#" + cond_type3 + "_level2").val(level2);
            }
        }
    }
});


$("#btn_confirm").on("click", function(e){
    e.preventDefault();
    var hidden_slot = $("#hidden_slot").val();

});