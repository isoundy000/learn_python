/**
 * Created by wangrui on 14/11/10.
 */

var battle_data = {
    "battle": {
        "action": [

        ],
        "init": {
            "attack": {

            },
            "defense": {

            }
        }
    },
    "meta": {
        "attack": {
            "generals": {},
            "name": "",
            "pet": {
                "0": {

                }
            }
        },

        "defense": {
            "generals": {},
            "name": ""
        }
    },
    "result": null,
    "type": "battle"
};

var PET_JSON = {
    "9001": "炽炎犬",
    "9002": "太极熊",
    "9003": "紫极魔",
    "9004": "青光妖龙",
    "9005": "炽炎朱雀"
};

//武将json数据
var general_json = {};
var combskill_json = {};
var temp_defense_arr = [];
var temp_change_data = [];
var temp_general = {"attack":{}, "defense": {}};
var dead_general = {"attack":{}, "defense": {}};

var attack_id = 1000000000;
var defense_id = 1100000000;

//var init_pet = function(){
//    var pet_str = "<option value='0'>请选择</option>";
//    for(var p in PET_JSON){
//        pet_str += "<option value='" + p + "'>" + PET_JSON[p] + "</option>";
//    }
//    $("#pet_name").html(pet_str);
//};
//init_pet();
//
//$("#pet_name").on("change", function(e){
//    e.preventDefault();
//    var pet_name = $(this).val();
//    if (pet_name != "0"){
//
//        battle_data["battle"]["init"]["attack"]["0"] = {
//            "id": 0,
//            "pet": true
//        };
//        battle_data["meta"]["attack"]["pet"]["0"] = {
//            "ap": 0,
//            "cid": pet_name,
//            "level2": 10
//        };
//    }
//});

var get_battle_json = function(){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/getbattlefile',
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data.length != 0){
                    for (var i=0; i < data.length; i++) {
                        str_info += "<tr>";
                        str_info += "<td><span class='badge badge-success'>" + (i + 1) + "</span></td>";
                        str_info += "<td>" + data[i]["filename"] + "</td>";
                        var url = "./static/" + data[i]["url"];
                        str_info += "<td>";
                        str_info += '&nbsp; <a onclick="open_json(\'' + data[i]["filename"] + '\')"' + ' class="btn default btn-xs purple">打开 <i class="fa fa-edit"></i></a>';
                        str_info += '&nbsp; <a onclick="window.open(\'' + url + '\')"' + ' class="btn default btn-xs green">下载 <i class="fa fa-edit"></i></a>';
                        str_info += '&nbsp; <a onclick="delete_json(\'' + data[i]["filename"] + '\')"' + ' class="btn default btn-xs red">删除 <i class="fa fa-edit"></i></a>';
                        str_info += "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#json_list").html(str_info);
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
};
get_battle_json();

function delete_json(file_name){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/deletejsonfile',
            data: {file_name: file_name},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                get_battle_json();
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
}

function open_json(file_name){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/openjsonfile',
            data: {file_name: file_name},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                battle_data = data;
                for(var k in battle_data["battle"]["init"]["attack"]){
                    var iid1 = battle_data["battle"]["init"]["attack"][k]["id"];
                    var is_boos1 = battle_data["battle"]["init"]["attack"][k]["boss"];
                    var hp = battle_data["meta"]["attack"]["generals"][iid1]["hp"];
                    var general_name1 = battle_data["meta"]["attack"]["generals"][iid1]["name"];
                    temp_general["attack"][k] = {"id": iid1, "hp": hp, "boss": is_boos1, "damage": 0};
                    display_hp_init($("#attack_" + k), general_name1, is_boos1, hp, 0);
                }

                for(var s in battle_data["battle"]["init"]["defense"]){
                    var iid2 = battle_data["battle"]["init"]["defense"][s]["id"];
                    var is_boos2 = battle_data["battle"]["init"]["defense"][s]["boss"];
                    var hp1 =  battle_data["meta"]["defense"]["generals"][iid2]["hp"];
                    var general_name2 = battle_data["meta"]["defense"]["generals"][iid2]["name"];
                    temp_general["defense"][s] = {"id": iid2, "hp": hp1, "boss": is_boos2, "damage": 0};
                    display_hp_init($("#defense_" + s), general_name2, is_boos2, hp1, 0);
                }

                var battleaction = battle_data["battle"]["action"];
                attack_id += 1000000000;
                defense_id += 1000000000;

                for(var i in battleaction){
                    var battleactioni = battleaction[i];
                    if (battleactioni["type"] == "pos"){
                        var changes = battleactioni["changes"];
                        for(var c in changes){
                            var change = changes[c];
                            var c_value = "";
                            if (change["direct"] == true){
                                c_value = "attack";
                            }
                            else{
                                c_value = "defense";
                            }
                            if (change.opt == "appear"){
                                var pos1 = changes[c]["pos"];
                                var isboos_1 = changes[c]["direct"];
                                var hp2 = battle_data["meta"][c_value]["generals"][change.general]["hp"];
                                temp_general[c_value][pos1] = {"id": change.general, "hp": hp2, "boss": isboos_1, "damage": 1};
                            }
                        }
                    }
                    else if (battle_data["battle"]["action"][i]["type"] == "battle"){
                        for(var d in battle_data["battle"]["action"][i]["dest"]){
                            var direct = battle_data["battle"]["action"][i]["dest"][d]["direct"];
                            var d_value = "";
                            if (direct == true){
                                d_value = "attack";
                            }
                            else{
                                d_value = "defense";
                            }
                            var pos = battle_data["battle"]["action"][i]["dest"][d]["pos"];
                            if ("damage" in battle_data["battle"]["action"][i]["dest"][d]){
                                var status = battle_data["battle"]["action"][i]["dest"][d]["damage"]["status"];
                                if (status == "dead"){
                                    dead_general[d_value][pos] = {"id": temp_general[d_value][pos]["id"]};
    //                                delete temp_general[d_value][pos];
                                }
                            }
                        }
                    }
                }
                display_battle();
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
}


var init_general = function () {
    var general_select = $("#general_select");
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/initgeneral',
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "<option value=''>请选择</option>";
                for (var key in data["general"]) {
                    str_info += "<option value='" + key + "'>" + data["general"][key]["name"] + "</option>";
                }
                $("#general_select").html(str_info);
                $("#pos_general").html(str_info);
                $("#talk_generals_new").html(str_info);
                general_json = data["general"];
                combskill_json = data["comb"];
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
    var str_head = '<div class="row">';
    var str_end = '</div>';

    var attackBattle = $("#attack_battle");
    var html = "";
    var s = 1;
    var t = 8;
    for (var i = 1; i <= 14; i++) {
        var str_info = "";
        str_info += '<div class="col-md-6">';
        if (i % 2 != 0) {
            str_info += '<a id="attack_' + t + '" onclick="choose_general(' + '\'attack_' + t + '\',' + t + ')"' + ' class="battle">';
            str_info += '<span class="badge badge-info">' + t + '</span>';
            t += 1;
        } else {
            str_info += '<a id="attack_' + s + '" onclick="choose_general(' + '\'attack_' + s + '\',' + s + ')"' + ' class="battle">';
            str_info += '<span class="badge badge-info">' + s + '</span>';
            s += 1;
        }
        str_info += '</a></div>';
        if (i % 2 != 0) {
            html += str_head;
        }
        html += str_info;
        if (i % 2 == 0) {
            html += str_end;
        }
    }
    attackBattle.append(html);

    var defenseBattle = $("#defense_battle");
    var html2 = "";
    var m = 1;
    var n = 8;
    for (var k = 1; k <= 14; k++) {
        var str_right = "";
        str_right += '<div class="col-md-6">';
        if (k % 2 != 0) {
            str_right += '<a id="defense_' + m + '" onclick="choose_general(' + '\'defense_' + m + "\'," + m + ')"' + ' class="battle">';
            str_right += '<span class="badge badge-info">' + m + '</span>';
            m += 1;
        } else {
            str_right += '<a id="defense_' + n + '" onclick="choose_general(' + '\'defense_' + n + "\'," + n + ')"' + ' class="battle">';
            str_right += '<span class="badge badge-info">' + n + '</span>';
            n += 1;
        }

        str_right += '</a></div>';
        if (k % 2 != 0) {
            html2 += str_head;
        }
        html2 += str_right;
        if (k % 2 == 0) {
            html2 += str_end;
        }
    }
    defenseBattle.append(html2)
};
init_general();

$("#set_attack_name").bind("click", function(e){
    e.preventDefault();
    var attack_name = $("#attack_name").val();
    battle_data["meta"]["attack"]["name"] = attack_name;
    $("#set_attack_name").attr("disabled", true);
});

$("#set_defense_name").bind("click", function(e){
    e.preventDefault();
    var defense_name = $("#defense_name").val();
    battle_data["meta"]["defense"]["name"] = defense_name;
    $("#set_defense_name").attr("disabled", true);
});

function choose_general(choose_id, pos) {
    $("#general_modal").modal("show");
    $("#confirm_general").attr("onclick", "confirm('" + choose_id + '\',' + pos + ")");
}

function confirm(choose_id, pos) {
    var c_id = Number($("#general_select").val());
    var general_hp = Number($("#general_hp").val());
    var general_hp2 = Number($("#general_hp2").val());
    var general_level = Number($("#general_level").val());
    var is_boss = $("#isboss").is(":checked");
    var general_name = general_json[c_id]["name"];
    var init_ap = $("#init_ap").val();
    var choose = $("#" + choose_id);

    $("#general_modal").modal("hide");
    var split_choose = choose_id.split("_");
    var g_iid = 0;
    if (split_choose[0] == "attack"){
        g_iid = attack_id;
        attack_id += 1;
    }
    else{
        g_iid = defense_id;
        defense_id += 1;
    }
    var init_json = {"id": g_iid,
        "boss": is_boss
    };
    var skillid = null;
    if (general_json[c_id]["skillid"] != 0){
        skillid = {"id": general_json[c_id]["skillid"]};
    }
    var meta_json = {"cid": c_id,
        "ap": Number(init_ap),
        "defaultskill": skillid,
        "hp": general_hp,
        "hp2": general_hp2,
        "id": g_iid,
        "level": general_level,
        "name": general_name,
        "pos": pos
    };
    battle_data["battle"]["init"][split_choose[0]][pos] = init_json;
    battle_data["meta"][split_choose[0]]["generals"][g_iid] = meta_json;
    temp_general[split_choose[0]][pos] = {"hid": choose_id, "cid":c_id, "id": g_iid, "boss": is_boss, "hp": general_hp, "damage": 0};

    display_hp_init(choose, general_name, is_boss, general_hp, 0);
}

var display_hp_init = function(div, general_name, is_boss, hp, damage_hp){
    var spare_hp = hp - damage_hp;
    var spare_hp_percent = (spare_hp / hp * 100).toFixed(0);
    var damage_hp_percent = (damage_hp / hp * 100).toFixed(0);
    div.children().remove('div');
    var str_html =  "<div>" + general_name + hp ;
    if (is_boss == true) {
         str_html += "<span class='badge badge-danger'>Boss</span>";
    }
    str_html += "</div>";
    str_html += "<div class=\"progress\">";
    str_html += "<div class=\"progress-bar progress-bar-success\" style=\"width: " +
                    spare_hp_percent +  "%\"><span>" + spare_hp + "</span></div>" +
                    "<div class=\"progress-bar progress-bar-danger\" style=\"width: " +
                    damage_hp_percent + "%\"><span>" + damage_hp + "</span></div></div>";
    div.append(str_html);
};

$("#add_change").on("click", function(e){
    e.preventDefault();
    $("#change_battle").val("");
    $("#pos_general").val("");
    var str_info = "";
    for (var i = 1; i < 15; i++) {
        str_info += "<option value='" + i + "'>" + i + "号位</option>";
    }
    $("#change_general").html(str_info);
    $("#change_g_hp").val("");
    $("#change_g_hp2").val("");
    $("#change_g_level").val("");
    $("#change_modal").modal("show");
});

$("#add_def").click(function (e) {
    e.preventDefault();
    $("#input[name='add_blood']").attr("checked", false);
    $("#defense_modal").modal("show");
});

function change_str(crit_is) {
    if (crit_is) {
        return "critical";
    }
    else {
        return "normal";
    }
}

$("#confirm_def").click(function (e) {
    e.preventDefault();
    var attack_value = $("#select_attack").val();
    var atk_pos = Number($("#select_general_list").val());
    var def_general = Number($("#def_general_select").val());
    var harm_text_hp = Number($("#harm_text_hp").val());
    var crit_is = $("#crit_is").is(":checked");
    var effect = $('input[name="effect"]:checked').val();
    var buffer = $('input[name="buffer"]:checked').val();
    var crit_num = Number($("#crit_num").val());
    var add_blood = $("#add_blood").is(":checked");
    var w_ap = Number($("#w_ap").val());

    var direct = null;
    var direct1 = null;
    if (attack_value == "attack") {
        direct = false;
        direct1 = true;
    } else {
        direct = true;
        direct1 = false;
    }
    if (add_blood == false){
        var num = 0;
        if (crit_is == true){
            num = crit_num
        }
        var temp_one = {
            "damage": {
                "damage": harm_text_hp,
                "status": change_str(crit_is),
                "num": num
            },
            "pos": def_general,
            "direct": direct
        };

        if (effect != "null"){
            temp_one["status"] = {
                "status": effect,
                "switch": true
            };
        }

        var pro_buff = {};
        if (buffer != "null"){
            var buffer_s = buffer.split("_");
            if (buffer_s[0] == "w"){
                temp_one["buffer"] = {
                    "attr": buffer_s[1],
                    "status": "weaken",
                    "switch": true
                };
            }
            else{

                pro_buff["pos"] = atk_pos;
                pro_buff["buffer"] = {
                    "attr": buffer_s[1],
                    "status": "promote",
                    "switch": true
                };
                pro_buff["direct"] = direct1;
            }
        }
        temp_defense_arr.push(temp_one);
        if (!pro_buff){
            temp_defense_arr.push(pro_buff);
        }
        var ap_json = {
            "ap": w_ap,
            "direct": false,
            "pos": def_general
        };
        if (w_ap != 0){
            temp_defense_arr.push(ap_json);
        }
    }
    else{
        for(var key_ in temp_general[attack_value]){
            var temp_one1 = {
                "pos": Number(key_),
                "damage": {
                    "damage": -harm_text_hp,
                    "status": change_str(crit_is)
                },
                "direct": direct1
            };
            temp_defense_arr.push(temp_one1);
        }
    }

    $("#defense_modal").modal("hide");

    display_battle_info();
});

var display_battle_info = function(){
    var def_list = $("#def_list");
    var html = "";
    for (var k = 0; k < temp_defense_arr.length; k++) {
        html += '<div class="form-group">';
        if ( "damage" in temp_defense_arr[k]) {
            html += '<div class="col-md-2"><p>位置:' + temp_defense_arr[k]["pos"] + '</p></div>';
            html += '<div class="col-md-4"><p>伤害:' + temp_defense_arr[k]["damage"]["damage"] + '</p></div>';
            if (temp_defense_arr[k]["damage"]["status"] == "critical") {
                html += '<div class="col-md-2"><p class="label label-danger">暴击</p></div>';
            }
            else {
                html += '<div class="col-md-2"><p class="label label-success">无暴击</p></div>';
            }
            if ("status" in temp_defense_arr[k]) {
                console.log(temp_defense_arr[k]["status"]);
                if (temp_defense_arr[k]["status"] == "dizzy")
                    html += '<div class="col-md-2"><p class="label label-danger">晕眩</p></div>';
                else
                    html += '<div class="col-md-2"><p class="label label-danger">中毒</p></div>';
            }
        }
        else{

        }
//        html += '<div class="col-md-2"><button class="btn green" onclick="mod_battle(' + k +  ')">修改</button></div>';
        html += '<div class="col-md-2"><button class="btn btn-xs red" onclick="del_battle(' + k +  ')">删除</button></div>';
        html += '</div>';
    }
    def_list.html(html);
};


var del_battle = function (id){
    temp_defense_arr.splice(id, 1);
    display_battle_info();
};

function create_select(str_f, select_general) {
    var str_info = "";
    for (var data in battle_data["meta"][str_f]["generals"]) {
        var general_cid = battle_data["meta"][str_f]["generals"][data]["cid"];
        if (general_cid != 0){
            var general_name = general_json[general_cid]["name"];
            var pos = "";
            for (var s in temp_general[str_f]) {
                if (temp_general[str_f][s]["id"] == data) {
                    pos = s;
                }
            }

            str_info += '<option value="' + pos + '">';
            if (pos == ""){
                str_info += "【已死亡】"
            }
            else{
                str_info += pos + "号位:";
            }
            str_info += general_name + "</option>";
        }
    }
    select_general.html(str_info);
}

$("#select_attack").change(function () {
    var attack_value = $("#select_attack").val();
    var s_general = $("#select_general_list");
    var def_general_select = $("#def_general_select");
    if (attack_value != ""){
        create_select(attack_value, s_general);
        if (attack_value == "attack"){
            create_select("defense", def_general_select);
        }
        else{
            create_select("attack", def_general_select);
        }
        $("#select_general_list").change();
    }
});

$("#select_general_list").on("change", function(){

    var attack_value = $("#select_attack").val();
    var select_general_list = $("#select_general_list").val();
    if (select_general_list != ""){
        var iid = temp_general[attack_value][select_general_list]["id"];
        var cid = battle_data["meta"][attack_value]["generals"][iid]["cid"];
        var comb_skill_id = general_json[cid]["combskillid"];

        var html = "";
        html += "<option value=\"normal\">普攻</option>";
        html += "<option value=\"skill\">技能</option>";
        if (comb_skill_id != 0) {
            var cid_arr = [];
            for (var s in battle_data["meta"][attack_value]["generals"]) {
                cid_arr.push(battle_data["meta"][attack_value]["generals"][s]["cid"])
            }
            var cid1 = combskill_json[comb_skill_id]["cid1"];
            var cid2 = combskill_json[comb_skill_id]["cid2"];
            var cid3 = combskill_json[comb_skill_id]["cid3"];

            if (cid_arr.indexOf(cid1) >= 0 && cid_arr.indexOf(cid2) >= 0) {
                var comb_pos = "";
                for (var i in battle_data["meta"][attack_value]["generals"]) {
                    if (battle_data["meta"][attack_value]["generals"][i]["cid"] == cid1) {
                        comb_pos += battle_data["meta"][attack_value]["generals"][i]["pos"] + ",";
                    }
                    if (battle_data["meta"][attack_value]["generals"][i]["cid"] == cid2) {
                        comb_pos += battle_data["meta"][attack_value]["generals"][i]["pos"] + ",";
                    }
                    if (cid3 != 0 && cid_arr.indexOf(cid3) >= 0) {
                        if (battle_data["meta"][attack_value]["generals"][i]["cid"] == cid3) {
                            comb_pos += battle_data["meta"][attack_value]["generals"][i]["pos"] + ",";
                        }
                    }
                }

                $("#comb_pos").val(comb_pos);
                html += "<option value=\"comb\">合体技</option>";
            }
        }
        $("#attack_type").html(html);
    }
});


$("#attack_type").change(function (e) {
    e.preventDefault();
    var attack_type = $("#attack_type").val();
    var comb_general = $("#comb_general");
    if (attack_type == "comb") {
        comb_general.removeClass("hide");
    }
    else {
        if (comb_general.hasClass("hide") == false) {
            comb_general.addClass("hide");
        }
    }
});


$("#confirm_result").click(function (e) {
    e.preventDefault();
    var select_attack = $("#select_attack").val();
    var attack_type = $("#attack_type").val();
    var source_pos = Number($("#select_general_list").val());
    var fight_tag = $("#fight_tag").val();
    var attack_ap = Number($("#attack_ap").val());

    var temp_id = "";
    var general_cid = "0";
    for (var t in battle_data["meta"][select_attack]["generals"]) {
        var pos = battle_data["meta"][select_attack]["generals"][t]["pos"];
        if (pos == source_pos) {
            general_cid = battle_data["meta"][select_attack]["generals"][t]["cid"];
            if (pos in dead_general[select_attack]){
                temp_id = dead_general[select_attack][pos]["id"];
                if (temp_id == t){
                    continue;
                }
            }
            temp_id = t;
        }
    }
    var skill_id = battle_data["meta"][select_attack]["generals"][temp_id]["defaultskill"]["id"];
    var temp_round = {
        "dest": [],
        "source": {
            "type": attack_type,
            "pos": [source_pos],
            "skillid": skill_id
        },
        "type": "battle"
    };

    if (attack_type == "comb") {
        var comb_pos = $("#comb_pos").val();
        var comb_pos_arr = comb_pos.split(",");
        temp_round["source"]["pos"] = [];
        for(var c in comb_pos_arr){
            if (comb_pos_arr[c] != ""){
                temp_round["source"]["pos"].push(Number(comb_pos_arr[c]));
            }
        }
        temp_round["source"]["skillid"] = general_json[general_cid]["combskillid"];
    }

    var s = "";
    var temp_tag = null;
    if (select_attack == "attack") {
        temp_tag = true;
        s = "defense";
    }
    else {
        temp_tag = false;
        s = "attack";
    }
    temp_round["source"]["direct"] = temp_tag;

    for (var i = 0; i < temp_defense_arr.length; i++) {
        var direct = temp_defense_arr[i]["direct"];
        if ("damage" in temp_defense_arr[i]) {
            var damage_value = temp_defense_arr[i]["damage"]["damage"];
            var iid = null;
            var def_hp = null;

            if (damage_value < 0) {
                iid = temp_general[select_attack][temp_defense_arr[i]["pos"]]["id"];
                def_hp = battle_data["meta"][select_attack]["generals"][iid]["hp"];
            }
            else {
                iid = temp_general[s][temp_defense_arr[i]["pos"]]["id"];
                def_hp = temp_general[s][temp_defense_arr[i]["pos"]]["hp"];
                if (damage_value >= def_hp) {
                    temp_defense_arr[i]["damage"]["status"] = "dead";
                    dead_general[s][temp_defense_arr[i]["pos"]] = temp_general[s][temp_defense_arr[i]["pos"]];
                    delete temp_general[s][temp_defense_arr[i]["pos"]];
                }
                else {
                    temp_general[s][temp_defense_arr[i]["pos"]]["hp"] = def_hp - damage_value;
                }
            }
        }
        temp_round["dest"].push(temp_defense_arr[i]);
    }
    var ap_data = {
        "ap": attack_ap,
        "direct": temp_tag,
        "effect": false,
        "pos": source_pos
    };
    temp_round["dest"].push(ap_data);

    if (fight_tag == ""){
        battle_data["battle"]["action"].push(temp_round);
    }
    else{
        battle_data["battle"]["action"][Number(fight_tag)] = temp_round
    }
    display_battle();
    temp_defense_arr = [];
    $("#def_list").html("");
});

//function dis_details(k){
//    var action_data = battle_data["battle"]["action"][k];
//    var pos = action_data["source"]["pos"];
//
//    var attack_data = {};
//    var def_data_array = [];
//    for (var i = 0; i < action_data["dest"].length; i++) {
//        var def_pos = action_data["dest"][i]["pos"];
//        def_data_array.push(def_pos);
//    }
//    if(tag){
//        attack_data = temp_general["attack"][pos];
//        for(var n=0; n<def_data_array.length; n++){
//            var temp_d = temp_general["defense"][def_data_array[n]];
//            $("#" + temp_d["hid"]).append(temp_d["hp"] + "," + temp_d["damage"] + ',' + temp_d["spare"]);
//            $("#" + temp_d["hid"]).css("border-color", "#e23e29");
//        }
//    }
//    else{
//        attack_data = temp_general["defense"][pos];
//        for(var m=0; m<def_data_array.length; m++){
//            var temp_da = temp_general["defense"][def_data_array[m]];
//            $("#" + temp_da["hid"]).append(temp_da["hp"] + "," + temp_da["damage"] + ',' + temp_da["spare"]);
//            $("#" + temp_da["hid"]).css("border-color", "#e23e29");
//        }
//    }
//    $("#" + attack_data["hid"]).append(attack_data["hp"]);
//    $("#" + attack_data["hid"]).css("border-color", "#66ee66");
//}

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

$("#talk_battle").change(function(e){
    e.preventDefault();
    var talk_battle = $("#talk_battle").val();
    var talk_generals = $("#talk_generals");
    if(talk_battle != ""){
         create_talk_select(talk_battle, talk_generals);
    }
});

function create_talk_select(tag, select_talk){
    var str_info = "";
    for (var data in battle_data["meta"][tag]["generals"]) {
        var general_cid = battle_data["meta"][tag]["generals"][data]["cid"];

        var general_name = battle_data["meta"][tag]["generals"][data]["name"];
        str_info += "<option value='" + general_cid + "'>" + general_name + "</option>";
    }
    select_talk.html(str_info);
}

$("#add_talk_general").on("click", function(e){
    e.preventDefault();
    $("#talk_battle_new").val("");
    $("#talk_generals_new").val("");
    $("#talk_general_hp").val("");
    $("#talk_general_hp2").val("");
    $("#talk_general_level").val("");
    $("#talk_modal").modal("show");
});

$("#confirm_talk_1").on("click", function(e){
    e.preventDefault();
    var talk_battle_new = $("#talk_battle_new").val();
    var talk_generals_new = $("#talk_generals_new").val();
    var talk_general_hp = Number($("#talk_general_hp").val());
    var talk_general_hp2 = Number($("#talk_general_hp2").val());
    var talk_general_level = Number($("#talk_general_level").val());
    var isboss_talk = $("#isboss_talk").is(":checked");

    var g_iid = 0;
    if(talk_battle_new == "attack"){
        g_iid = attack_id;
        attack_id += 1;
    }else{
        g_iid = defense_id;
        defense_id += 1;
    }
    var skill_id = null;
    if (general_json[talk_generals_new]["skillid"] != 0){
        skill_id = {"id": general_json[talk_generals_new]["skillid"]}
    }

    var meta_json = {"cid": Number(talk_generals_new),
        "defaultskill": skill_id,
        "hp": talk_general_hp,
        "hp2": talk_general_hp2,
        "id": g_iid,
        "level": talk_general_level,
        "name": general_json[Number(talk_generals_new)]["name"]
    };
    battle_data["meta"][talk_battle_new]["generals"][g_iid] = meta_json;
    $("#talk_modal").modal("hide");
});

$("#confirm_talk").click(function(){
    var talk_battle = $("#talk_battle").val();
    var talk_general = $("#talk_generals").val();
    var talk_content = $("#talk_content").val();
    var talk_tag = $("#talk_tag").val();
    var direct = null;
    if (talk_battle == "attack"){
        direct = true;
    }
    else{
        direct = false;
    }
    var talk_data = {
        "type": "talk",
        "general": Number(talk_general),
        "content": talk_content,
        "direct": direct
    };
    if (talk_tag == ""){
        battle_data["battle"]["action"].push(talk_data);
    }
    else{
        battle_data["battle"]["action"][Number(talk_tag)] = talk_data;
    }
    $("#talk_tag").val("");
    display_battle();
    $("#talk_battle").val("");
    $("#talk_generals").val("");
    $("#talk_content").val("");
});


var n_change_iid = {};
$("#confirm_change1").on("click", function(e){
    e.preventDefault();
    var change_battle = $("#change_battle").val();
    var change_general = Number($("#change_general").val());
    var change_tag = $("#change_tag").val();
    var pos_general = $("#pos_general").val();
    var change_g_hp = Number($("#change_g_hp").val());
    var change_g_hp2 = Number($("#change_g_hp2").val());
    var change_g_level = Number($("#change_g_level").val());
    var is_boss = $("#isboss_change").is(":checked");
    var change_ap = Number($("#change_ap").val());
    var tag = null;
    var g_iid = 0;
    if (change_battle == "attack") {
        tag = true;
        g_iid = attack_id;
        attack_id += 1;
    }
    else{
        tag = false;
        g_iid = defense_id;
        defense_id += 1;
    }
    n_change_iid["generalid"] = g_iid;

    if (temp_general[change_battle][change_general] != null && temp_general[change_battle][change_general] != undefined) {
        var temp_data1 = {
            "direct": tag,
            "pos": change_general,
            "opt": "disappear",
            "general": Number(temp_general[change_battle][change_general]["id"])
        };
        temp_change_data.push(temp_data1);
    }
    else {
        temp_general[change_battle][change_general] = {"id": g_iid, "cid": Number(pos_general), "hp": change_g_hp, "boss": is_boss, "damage": 0};
    }

    if (pos_general != ""){
        var meta_json1 = {"cid": Number(pos_general),
            "ap": change_ap,
            "defaultskill": {
                "id": general_json[Number(pos_general)]["skillid"]
            },
            "hp": change_g_hp,
            "hp2": change_g_hp2,
            "id": g_iid,
            "level": change_g_level,
            "name": general_json[Number(pos_general)]["name"],
            "pos": change_general
        };
        if (battle_data["meta"][change_battle]["generals"][g_iid] == null) {
            battle_data["meta"][change_battle]["generals"][g_iid] = meta_json1;
        }
        var temp_data = {
            "direct": tag,
            "pos": change_general,
            "opt": "appear",
            "general": Number(g_iid),
            "boss": is_boss
        };
        temp_change_data.push(temp_data);
    }

    $("#change_modal").modal("hide");
    display_appear();
});

function display_appear(){

    var html = "";
    for (var k = 0; k < temp_change_data.length; k++) {
        html += '<div class="form-group">';
        var direct = temp_change_data[k]["direct"];
        var str_s = "";
        var str_t = "";
        if (direct == true){
            str_s = "attack";
            str_t =  "<p>左阵容</p>";
        }
        else{
            str_s = "defense";
            str_t = "<p>右阵容</p>";
        }
        html += '<div class="col-md-2">' + str_t + '</div>';
        html += '<div class="col-md-2"><p>' + temp_change_data[k]["pos"]  +'号位:' + '</p></div>';
        var opt = "";
        if(temp_change_data[k]["opt"] == "appear"){
            opt = "上场";
        }
        else{
            opt = "下场";
        }
        html += '<div class="col-md-2"><p>' + battle_data["meta"][str_s]["generals"][temp_change_data[k]["general"]]["name"] + '</p></div>';
        html += '<div class="col-md-2"><p>' + opt + '</p></div>';
        html += '<div class="col-md-2"><button class="btn btn-xs red" onclick="del_appear(' + k +  ')">删除</button></div>';
        html += '</div>';
    }
    $("#change_list").html(html);
}

var g_change_iid = {};
function del_appear(id){
    var direct = temp_change_data[id]["direct"];
    var change_tag = $("#change_tag").val();
    var str_t = "";
    if (direct == true){
        str_t = "attack";

    }
    else{
        str_t = "defense";
    }
    g_change_iid["direct"] = direct;
    g_change_iid["general"] = temp_change_data[id]["general"];
    g_change_iid["pos"] = temp_change_data[id]["pos"];
    delete battle_data["meta"][str_t]["generals"][temp_change_data[id]["general"]];
    delete temp_general[str_t][temp_change_data[id]["pos"]];
    temp_change_data.splice(id, 1);
    display_appear();
}

$("#talk_general_hp").on("input propertychange", function(e){
    e.preventDefault();
    $("#talk_general_hp2").val($("#talk_general_hp").val());
});

$("#change_g_hp").on("input propertychange", function(e){
    e.preventDefault();
    $("#change_g_hp2").val($("#change_g_hp").val());
});

$("#general_hp").on("input propertychange", function(e){
    e.preventDefault();
    $("#general_hp2").val($("#general_hp").val());
});

$("#confirm_change").click(function(e){
    e.preventDefault();
    var t_data = {
        "type": "pos",
        "changes": temp_change_data
    };
    var change_tag = $("#change_tag").val();
    if (change_tag == ""){
        battle_data["battle"]["action"].push(t_data);
    }
    else{
        battle_data["battle"]["action"][Number(change_tag)] = t_data;
        for (var i in battle_data["battle"]["action"]){
            var c_type = battle_data["battle"]["action"][i]["type"];
            if (c_type == "talk"){
                if (battle_data["battle"]["action"][i]["general"] == g_change_iid["general"]){
                    battle_data["battle"]["action"][i]["general"] = n_change_iid
                }
            }
            else if (c_type == "pos"){
                var changes = battle_data["battle"]["action"][i]["changes"];
                for (var c in changes){
                    if (changes[c]["pos"] == g_change_iid){

                    }
                }
            }
        }
    }
    $("#change_list").empty();
    display_battle();
    $("#change_tag").val("");
    temp_change_data = [];
    g_change_iid = {};
    n_change_iid = {};
});

$("#create_json").click(function(e){
    e.preventDefault();
    var attack_name = $("#attack_name").val();
    battle_data["meta"]["attack"]["name"] = attack_name;
    var defense_name = $("#defense_name").val();
    battle_data["meta"]["defense"]["name"] = defense_name;
    var result = null;
    for (var s = battle_data["battle"]["action"].length-1; s >= 0; s--){
        if (battle_data["battle"]["action"][s]["type"] == "battle"){
            result = battle_data["battle"]["action"][s]["source"]["direct"];
            break;
        }
    }
    battle_data["result"] = result;
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'post',
            url: '/createbattle',
            data: {battle_data: JSON.stringify(battle_data)},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] = true){
                    get_battle_json();
                }
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    )
});

var display_hp = function(k){
    var battle_info = battle_data["battle"]["action"][k];
    if (battle_info["type"] == "pos"){
        var changes_info = battle_info["changes"];
        for (var c in changes_info){
            var pos = changes_info[c]["pos"];
            var direct = changes_info[c]["direct"];
            var general_id = changes_info[c]["general"];
            var is_boss = changes_info[c]["boss"];
            var str_c = "";
            if (changes_info[c]["opt"] == "appear"){
                if (direct == true)
                {
                    str_c = "attack";
                }
                else{
                    str_c = "defense";
                }
                var general_name = battle_data["meta"][str_c]["generals"][general_id]["name"];
                var hp = battle_data["meta"][str_c]["generals"][general_id]["hp"];
                display_hp_init($("#" + str_c + "_" + pos), general_name, is_boss, hp, 0);
            }
        }
    }
    else if (battle_info["type"] == "battle"){
        var battle_dest = battle_info["dest"];
        for (var b in battle_dest){
            var pos1 = battle_dest[b]["pos"];
            var direct1 = battle_dest[b]["direct"];
            var str_d = "";
            if (direct1 == true){
                str_d = "attack";
            }
            else{
                str_d = "defense";
            }
            var damage = battle_dest[b]["damage"]["damage"];
            var general_name1 = battle_data["meta"][str_d]["generals"][temp_general[str_d][pos1]["id"]]["name"];
            var hp1 = temp_general[str_d][pos1]["hp"];
            var boss = temp_general[str_d][pos1]["boss"];
            display_hp_init($("#" + str_d + "_" + pos1), general_name1, boss, hp1, damage)
        }
    }
};

//战报情况显示
function display_battle(){
    var battle_situation = $("#battle_situation");
    var html = "";
    for (var k = 0; k < battle_data["battle"]["action"].length; k++) {
        html += '<div class="note note-info"><h6 class="block" onclick="display_hp(\'' + k + '\')">';
        var action_source = battle_data["battle"]["action"][k]["type"];
        html += (k + 1) + ":";
        if (action_source == "battle") {
            var source_direct = battle_data["battle"]["action"][k]["source"]["direct"];
            var source_pos_array = battle_data["battle"]["action"][k]["source"]["pos"];
            var source_type = battle_data["battle"]["action"][k]["source"]["type"];
            var name = "";
            if (source_direct == true){
                name = "attack";
            }
            else{
                name = "defense";
            }
            for (var s = 0; s < source_pos_array.length; s++) {
                var ge_iid = 0;
                var spas = source_pos_array[s];
                if (spas in temp_general[name]){
                    ge_iid = temp_general[name][spas]["id"];
                }
                else{
                    ge_iid = dead_general[name][spas]["id"];
                }
                var general_name = battle_data["meta"][name]["generals"][ge_iid]["name"];
                html += "<span class='badge badge-info'>" + spas + "</span>号位:" + "【" + general_name + "】";
            }
            html += "使用";
            html += get_attack_type(source_type);
            html += "攻击";
            var dest_arrray = battle_data["battle"]["action"][k]["dest"];
            for (var d = 0; d < dest_arrray.length; d++) {
                var dest_pos = dest_arrray[d]["pos"];
                var dest_direct = dest_arrray[d]["direct"];
                var dest_name = "";
                if (dest_direct == true){
                    dest_name = "attack";
                }else{
                    dest_name = "defense";
                }
                var dest_g_iid = 0;
                var damage_status = "";
                if ("damage" in dest_arrray[d]){
                    if (dest_arrray[d]["damage"]["status"] == "normal") {
                        damage_status = "正常";
                    }
                    else if (dest_arrray[d]["damage"]["status"] == "critical") {
                        damage_status = "暴击";
                    }
                    else {
                        damage_status = "死亡";
                    }
                    if (dest_pos in dead_general[dest_name]){
                        dest_g_iid = dead_general[dest_name][dest_pos]["id"];
                    }
                    else{
                        dest_g_iid = temp_general[dest_name][dest_pos]["id"];
                    }

                    var dest_g_name = battle_data["meta"][dest_name]["generals"][dest_g_iid]["name"];
                    html += "<span class='badge badge-info'>" + dest_pos + "</span>号位:" + "【" + dest_g_name + "】";
                    html += "造成:" + dest_arrray[d]["damage"]["damage"] + "伤害" + "【" + damage_status + "】";
                    if ("status" in dest_arrray[d]){
                        if (dest_arrray[d]["status"] == "dizzy")
                            html += "【晕眩】";
                        else
                            html += "【中毒】";
                    }
                }
                else if ("ap" in dest_arrray[d]){
                    html += "减少怒气:【" + dest_arrray[d]["ap"] + "】";
                }
            }
        }
        else if(action_source == "talk"){
            var general_cid = battle_data["battle"]["action"][k]["general"];
            if (general_cid == 0){
                html += "【主角】";
            }
            else{
                html += "【" + general_json[general_cid]["name"] + "】";
            }
            html += "对话:";
            html += "【" + battle_data["battle"]["action"][k]["content"] + "】";
        }
        else if (action_source == "pos"){
            var changes_arr = battle_data["battle"]["action"][k]["changes"];
            for (var i =0; i < changes_arr.length; i ++){
                var direct = changes_arr[i]["direct"];
                var g_iid = changes_arr[i]["general"];
                var g_name = "";
                if (direct == true){
                    html += "左阵容";
                    g_name = battle_data["meta"]["attack"]["generals"][g_iid]["name"];
                }
                else{
                    html += "右阵容";
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
                html += "【" + pos + "】" + "号位" + g_name + str_opt + ";";
            }
        }

        html += "</h6>";
        html += '<a onclick="mod_current(' + k + ')">修改</a>';
        html += '<a onclick="del_current(' + k + ')">删除</a>';
        html += "</div>";
    }
    battle_situation.html(html);
}

function mod_current(k){
    if (battle_data["battle"]["action"][k]["type"] == "pos"){
        temp_change_data = battle_data["battle"]["action"][k]["changes"];
        $("#li_fight").removeClass("active");
        $("#li_talk").removeClass("active");
        $("#li_change").addClass("active");

        $("#tab_fight").removeClass("active");
        $("#tab_talk").removeClass("active");
        $("#tab_change").addClass("active");
        $("#change_tag").val(k);
        attack_id = 2000000000;
        defense_id = 2100000000;
        display_appear();
    }
    else if (battle_data["battle"]["action"][k]["type"] == "talk"){
        var direct = battle_data["battle"]["action"][k]["direct"];
        var general_id = battle_data["battle"]["action"][k]["general"];
        var str_s = "";
        if (direct == true){
            str_s = "attack";
        }
        else{
            str_s = "defense";
        }
        $("#li_fight").removeClass("active");
        $("#li_talk").addClass("active");
        $("#li_change").removeClass("active");

        $("#tab_fight").removeClass("active");
        $("#tab_talk").addClass("active");
        $("#tab_change").removeClass("active");

        $("#talk_battle").val(str_s);
        $("#talk_battle").change();
        $("#talk_generals").val(general_id);
        $("#talk_content").val(battle_data["battle"]["action"][k]["content"]);
        $("#talk_tag").val(k);
    }
    else if (battle_data["battle"]["action"][k]["type"] == "battle"){
        var source_direct = battle_data["battle"]["action"][k]["source"]["direct"];
        var source_pos = battle_data["battle"]["action"][k]["source"]["pos"];
        var attack_type = battle_data["battle"]["action"][k]["source"]["type"];
        var str_t = "";
        if (source_direct == true){
            str_t = "attack";
        }
        else{
            str_t = "defense";
        }
        $("#li_fight").addClass("active");
        $("#li_talk").removeClass("active");
        $("#li_change").removeClass("active");

        $("#tab_fight").addClass("active");
        $("#tab_talk").removeClass("active");
        $("#tab_change").removeClass("active");

        $("#select_attack").val(str_t);
        $("#select_attack").change();
        $("#select_general_list").val(source_pos[0]);
        if (attack_type == "comb"){
            var str_c = "";
            for(var i in source_pos){
                str_c += source_pos[i] + ",";
            }
            $("#comb_pos").val(str_c);
        }
        $("#attack_type").val(attack_type);
        temp_defense_arr = battle_data["battle"]["action"][k]["dest"];
        $("#fight_tag").val("");
        display_battle_info();
    }
}

function del_current(k){
    if (battle_data["battle"]["action"][k]["type"] == "pos"){
        var changes = battle_data["battle"]["action"][k]["changes"];
        for(var i in changes){
            var direct = changes[i]["direct"];
            var pos = changes[i]["pos"];
            var value = "";
            if (direct == true){
                value = "attack";
            }
            else{
                value = "defense";
            }
            delete temp_general[value][pos];
        }
    }
    else if (battle_data["battle"]["action"][k]["type"] == "battle"){

    }
    battle_data["battle"]["action"].splice(k, 1);
    display_battle();
}