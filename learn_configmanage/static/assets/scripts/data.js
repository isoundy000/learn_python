/**
 * Created by wangrui on 16/2/1.
 */
/**
 * Created by wangrui on 14-10-16.
 */

get_left_game_server();
setLeftStyle();

var server_id = $("#server_id").val();
handleDatePickers();
$("#create_date").val(getNowFormatDate(0));
$("#login_date").val(getNowFormatDate(0));
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));

$("#s_date").val(getNowFormatDate(0));
$("#e_date").val(getNowFormatDate(0));

if (server_id === '999999'){
    $('#all_copy').show();
}else{
    $('#all_copy').hide();
}


var QUALITY_CSS = {
    2: "green",
    3: "blue",
    4: "purple",
    5: "yellow"
};

var DATA = {};

var CONFIG = ["general", "equip", "props", "map", "copy", "star_copy", "star_map", "soul", "pet3_attr", "expedition_map"];

var init_data = function(){
    $.ajax({
            type: 'get',
            url: "/queryjsondatabyserver",
            data: {
                server_id: server_id,
                type: JSON.stringify(CONFIG)
            },
            dataType: 'JSON',
            success: function (data) {
                DATA = data;
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};
 setTimeout("init_data()", 2000);

var Data = function(){
    var roleidValidation = function () {
        var rules = {
            role_search: {
                required: true
            }
        };
        var messages = {
            role_search: {
                required: "请输入角色编号."
            }
        };
        var submitHandler = function (form) {
            var role_search = $("#role_search").val();
            var page_content = $('.page-content');

            var r = /^\+?[1-9][0-9]*$/;
            var role_type = '';
            (r.test(role_search)) ? role_type = 'role_id' : role_type = 'role_name';
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: "/getroleinfo",
                    data: {role_search: role_search, server_id: server_id, role_type: role_type},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content);
                        var str_info = "<tr>";
                        if (data != null) {
                            $("#role_id").val(data["id"]);
                            str_info += "<td>" + data["uid"] + "</td>";
                            str_info += "<td>" + data["id"] + "</td>";
                            str_info += "<td><div id='role_name'>" + data["name"] + "</div></td>";
                            str_info += "<td><div id='role_vip'>" + data["vip"] + "</div></td>";
                            str_info += "<td><div id='role_level'>" + data.level + "</div></td>";
                            str_info += "<td><div id='role_exp'>" + data["exp"] + "</div></td>";
                            str_info += "<td><div id='role_coin'>" + data["coin"] + "</div></td>";
                            str_info += "<td><div id='role_gold'>" + data["gold"] + "</div></td>";
                            str_info += "<td><div id='role_stamina'>" + data["stamina"] + "</div></td>";
                            str_info += "<td>" + data["maxstamina"] + "</td>";
                            str_info += "<td><div id='role_energy'>" + data["energy"] + "</div></td>";
                            str_info += "<td>" + data["maxenergy"] + "</td>";
                            str_info += "<td><div id='role_prestige'>" + data["prestige"] + "</div></td>";
                            str_info += "<td><div id='role_athletics'>" + data["athletics"] + "</div></td>";
                            if (data["channel"] == null) {
                                str_info += "<td>IOS官方</td>";
                            }
                            else {
                                str_info += "<td>" + data["channel"] + "</td>";
                            }
                            str_info += "<td><div id='role_power'>" + data["power"] + "</div></td>";
                            str_info += "<td>" + data["createtime"] + "</td>";
                            str_info += "<td>" + data["lastlogin"] + "</td>";
                            str_info += "<td>";
                            str_info += '&nbsp; <button class="btn default btn-xs green" onclick="save_role()">保存<i class="fa fa-check"></i></button>';
                            str_info += "</td>";
                            str_info += "</tr>";
                        }
                        else {
                            str_info += '<td colspan="17" class="text-center"><span class="label label-danger">无此角色编号数据</span></td>';
                            str_info += '</tr>';
                        }
                        $("#role_list").html(str_info);
                        var tdNods = $("td div");
                        tdNods.dblclick(tdClick);

                    },
                    error: function (XMLHttpRequest) {
                        error_func(XMLHttpRequest);
                    }
                }
            );
        };
        commonValidation($("#roleid_form"), rules, messages, submitHandler);
    };

    var equipValidation = function () {
        var rules = {
            equip_num: {
                required: true,
                digits: true
            }
        };

        var messages = {
            equip_num: {
                required: "请输入装备数量",
                digits: "请输入整数"
            }
        };

        var submitHandler = function (form) {
            var role_id = $("#role_id").val();
            var equip_cid = $("#equip_cid").val();
            var equip_num = $("input[name='equip_num']").val();
            var equip_name = $("#equip_cid").find("option:selected").text();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/addequip',
                    data: {server_id: server_id, role_id: role_id, equip_cid: equip_cid, equip_num: equip_num, equip_name: equip_name},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content, true);
                        $("#equip_modal").modal("hide");
                        if (data.status == "fail") {
                            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                        }
                        else {
                            Common.alert_message($("#error_modal"), 1, "装备添加成功");
                        }
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content, true);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        };
        commonValidation($("#equip_form"), rules, messages, submitHandler);
    };

    var propsValidation = function () {
        var rules = {
            props_num: {
                required: true,
                digits: true
            }
        };

        var messages = {
            props_num: {
                required: "请输入道具数量",
                digits: "请输入整数"
            }
        };

        var submitHandler = function (form) {
            var role_id = $("#role_id").val();
            var props_cid = $("#props_cid").val();
            var props_name = $("#props_cid").find("option:selected").text();
            var props_num = $("input[name='props_num']").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/addprops',
                    data: {server_id: server_id, role_id: role_id,props_name: props_name,
                        props_cid: props_cid, props_num: props_num},
                    dataType: 'JSON',
                    success: function (data) {
                        $("#props_modal").modal("hide");
                        App.unblockUI(page_content, true);
                        if (data.status == "fail") {
                            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                        }
                        else {
                            Common.alert_message($("#error_modal"), 1, "道具添加成功");
                        }
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content, true);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        };
        commonValidation($("#props_form"), rules, messages, submitHandler);
    };


    var soulValidation = function () {
        var rules = {
            soul_num: {
                required: true,
                digits: true
            }
        };
        var messages = {
            soul_num: {
                required: "请输入命格数量",
                digits: "请输入数字"
            }
        };
        var submitHandler = function (form) {
            var role_id = $("#role_id").val();
            var soul_cid = $("#soul_cid").val();
            var soul_name = $("#soul_cid").find('option:selected').text();
            var soul_num = $("input[name='soul_num']").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/addsoul',
                    data: {server_id: server_id, soul_name: soul_name, role_id: role_id, soul_cid: soul_cid, soul_num: soul_num},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content, true);
                        $("#soul_modal").modal("hide");
                        if (data.status == "fail") {
                            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                        }
                        else {
                            Common.alert_message($("#error_modal"), 1, "武魂添加成功");
                        }
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content, true);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        };
        commonValidation($("#soul_form"), rules, messages, submitHandler);
    };

    var guideValidation = function(){
        var form1 = $("#guide_form");
        var rules = {
            step: {
                required: true,
                digits: true
            },
            status: {
                required: true
            }
        };
        var messages = {
            step: {
                required: "请输入步骤.",
                digits: "请输入数字."
            },
            status: {
                required: "请选择状态."
            }
        };
        var submitFunc = function(){
            var role_id = $("#role_id").val();
            var section = $("#section").val();
            var step = $("#step").val();
            var status = $("#status").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/updateguide',
                    data: {server_id: server_id, role_id: role_id, section: section, step: step, status: status},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content, true);
                        $("#guide_modal").modal("hide");
                        if (data["status"] == "fail") {
                            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                        }
                        else {
                            Common.alert_message($("#error_modal"), 1, "新手引导修改成功");
                        }
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content, true);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        };
        commonValidation(form1, rules, messages, submitFunc);
    };
    guideValidation();
    equipValidation();
    roleidValidation();
    propsValidation();
    soulValidation();
}();


var show_battle = function(id){
    $.ajax({
        type: 'get',
        url: '/showbattlereport',
        data: {server_id: server_id, r_id: id},
        dataType: 'JSON',
        success: function (data) {
            $("#battle_report_detail").val(data["report"]);
            $("#battle_modal").modal("show");
        },
        error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
    })
};

var play_battle = function(id){
    var mode = 1;
    window.open("/htmlbattle?mode=" + mode + "&id=" + id + "&server_id=" + server_id);
};

var mod_guide = function(rid, section){
    $.ajax({
            type: 'get',
            url: '/queryoneguide',
            data: {server_id: server_id, role_id: rid, section: section},
            dataType: 'JSON',
            success: function (data) {
                $("#section").val(section);
                $("#section").attr("diabled", true);
                $("#step").val(data["step"]);
                $("#status").val(data["status"]);
                $("#guide_modal").modal("show");
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};

function update_general(rid, gid){
    var general_exp = $("#general_exp" + gid).text();
    var game_id = $("input[name='server_id']").val();
    $.ajax({
            type: 'get',
            url: '/updategeneral',
            data: {game_id: game_id, rid: rid, gid: gid, general_exp: general_exp},
            dataType: 'JSON',
            success: function (data) {
                if (data.status == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else{
                    Common.alert_message($("#error_modal"), 0, "修改角色武将成功.");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
}


var query_generl = function (general_id){
    $("#soul_info").empty();
    var game_id = $("input[name='server_id']").val();
    var role_id = $("#role_id").val();
    $.ajax({
            type: 'get',
            url: '/querygeneral',
            data: {
                general_id: general_id,
                game_id: game_id,
                role_id: role_id
            },
            dataType: 'JSON',
            success: function (data) {
                var g_cid = data["cid"];
                var g_quality = DATA["general"][g_cid]["quality"];
                var g_css = QUALITY_CSS[g_quality];
                var EQUIP_JSON = DATA["equip"];
                var SOUL_JSON = DATA["soul"];
                $("#general_cid").html("<span class='btn " + g_css + "'>" + (DATA["general"][g_cid].hasOwnProperty("name") ? DATA["general"][g_cid]["name"] : DATA["general"][g_cid]["name_CN"]) + "<span>");
                $("#general_level1").html("<span class='badge badge-success '>" + data["level1"] + "</span>");
                $("#general_level2").html("<span class='badge badge-success'>" + data["level2"] + "</span>");
                $("#skill_level").html("<span class='badge badge-success'>" + data["skilllevel"] + "</span>");
                $("#general_power").html("<span class='badge badge-danger'>" + data["power"] + "</span>");
                // 血量、 攻击、防御、速度属性
                $("#hp_value").html("生命 +" +  data["attr"]["hp"]["value"] );
                $("#atk_value").html("攻击 +"  + data["attr"]["atk"]["value"] );
                $("#def_value").html("防御 +"  + data["attr"]["def"]["value"] );
                $("#speed_value").html("速度 +"  + data["attr"]["speed"]["value"] );

                if (data["equip"]["horse"] != null) {
                    var horse_cid = data["equip"]["horse"]["cid"];
                    var horse_quality = EQUIP_JSON[horse_cid]["quality"];
                    var horse_css = QUALITY_CSS[horse_quality];
                    var str_horse = "<span class='btn " + horse_css + "'>" + (EQUIP_JSON[horse_cid].hasOwnProperty("name") ? EQUIP_JSON[horse_cid]["name"] : EQUIP_JSON[horse_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["horse"]["level1"];
                    if (parseInt(data["equip"]["horse"]["speed"]) != 0){
                        str_horse += "</br>" + "速度 +" + parseInt(data["equip"]["horse"]["speed"]);
                    }
                    if (parseInt(data["equip"]["horse"]["atk"]) != 0){
                        str_horse += "</br>" + "攻击 +" + parseInt(data["equip"]["horse"]["atk"]);
                    }
                    if (parseInt(data["equip"]["horse"]["hp"]) != 0){
                        str_horse += "</br>" + "血量 +" + parseInt(data["equip"]["horse"]["hp"]);
                    }
                    if (parseInt(data["equip"]["horse"]["def_"]) != 0){
                        str_horse += "</br>" + "防御 +" + parseInt(data["equip"]["horse"]["def_"]);
                    }
                    $("#cid_horse").html(str_horse);

                    $("#horse_level2").html("+" + data["equip"]["horse"]["level2"]);
                }
                else {
                    $("#cid_horse").html("<span class='label label-danger'>" + "未装备</span>");
                }

                if (data["equip"]["weapon"] != null){
                    var weapon_cid = data["equip"]["weapon"]["cid"];
                    var weapon_quality = EQUIP_JSON[weapon_cid]["quality"];

                    var weapon_css = QUALITY_CSS[weapon_quality];
                    var str_weapon = "<span class='btn " + weapon_css + "'>" + (EQUIP_JSON[weapon_cid].hasOwnProperty("name") ? EQUIP_JSON[weapon_cid]["name"] : EQUIP_JSON[weapon_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["weapon"]["level1"];
                    str_weapon += "</br>" + "攻击 +" + parseInt(data["equip"]["weapon"]["atk"]);
                    $("#cid_weapon").html(str_weapon);
                    $("#weapon_level2").html("+" + data["equip"]["weapon"]["level2"]);
                }
                else{
                    $("#cid_weapon").html("<span class='label label-danger'>" + "未装备</span>");
                }

                if (data["equip"]["treasure"] != null){
                    var treasure_cid = data["equip"]["treasure"]["cid"];
                    var treasure_quality = EQUIP_JSON[treasure_cid]["quality"];

                    var treasure_css = QUALITY_CSS[treasure_quality];
                    var str_treasure = "<span class='btn " + treasure_css + "'>" + (EQUIP_JSON[treasure_cid].hasOwnProperty("name") ? EQUIP_JSON[treasure_cid]["name"] : EQUIP_JSON[treasure_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["treasure"]["level1"];
                    if (parseInt(data["equip"]["treasure"]["speed"]) != 0){
                        str_treasure += "</br>" + "速度 +" + parseInt(data["equip"]["treasure"]["speed"]);
                    }
                    if (parseInt(data["equip"]["treasure"]["atk"]) != 0){
                        str_treasure += "</br>" + "攻击 +" + parseInt(data["equip"]["treasure"]["atk"]);
                    }
                    if (parseInt(data["equip"]["treasure"]["hp"]) != 0){
                        str_treasure += "</br>" + "血量 +" + parseInt(data["equip"]["treasure"]["hp"]);
                    }
                    if (parseInt(data["equip"]["treasure"]["def_"]) != 0){
                        str_treasure += "</br>" + "防御 +" + parseInt(data["equip"]["treasure"]["def_"]);
                    }

                    $("#cid_treasure").html(str_treasure);
                    $("#treasure_level2").html("+" + data["equip"]["treasure"]["level2"]);
                }
                else{
                    $("#cid_treasure").html("<span class='label label-danger'>" + "未装备</span>");
                }

                if (data["equip"]["head"] != null){
                    var head_cid = data["equip"]["head"]["cid"];
                    var head_quality = EQUIP_JSON[head_cid]["quality"];

                    var head_css = QUALITY_CSS[head_quality];
                    var str_head = "<span class='btn " + head_css + "'>" + (EQUIP_JSON[head_cid].hasOwnProperty("name") ? EQUIP_JSON[head_cid]["name"] : EQUIP_JSON[head_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["head"]["level1"];
                    str_head += "</br>" + "血量 +" + parseInt(data["equip"]["head"]["hp"]);
                    $("#cid_head").html(str_head);
                    $("#head_level2").html("+" + data["equip"]["head"]["level2"]);
                }
                else{
                    $("#cid_head").html("<span class='label label-danger'>" + "未装备</span>");
                }

                if (data["equip"]["armor"] != null){
                    var armor_cid = data["equip"]["armor"]["cid"];
                    var armor_quality = EQUIP_JSON[armor_cid]["quality"];

                    var armor_css = QUALITY_CSS[armor_quality];
                    var str_armor = "<span class='btn " + armor_css + "'>" + (EQUIP_JSON[armor_cid].hasOwnProperty("name") ? EQUIP_JSON[armor_cid]["name"] : EQUIP_JSON[armor_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["armor"]["level1"];
                    str_armor += "</br>" + "防御 +" + parseInt(data["equip"]["armor"]["def_"]);
                    $("#cid_armor").html(str_armor);
                    $("#armor_level2").html("+" + data["equip"]["armor"]["level2"]);
                }
                else{
                    $("#cid_armor").html("<span class='label label-danger'>" + "未装备</span>");
                }

                if (data["equip"]["accessory"] != null){
                    var accessory_cid = data["equip"]["accessory"]["cid"];
                    var accessory_quality = EQUIP_JSON[accessory_cid]["quality"];

                    var accessory_css = QUALITY_CSS[accessory_quality];
                    var str_accessory = "<span class='btn " + accessory_css + "'>" + (EQUIP_JSON[accessory_cid].hasOwnProperty("name") ? EQUIP_JSON[accessory_cid]["name"] : EQUIP_JSON[accessory_cid]["name_CN"]) + "</span>" + "LV:" + data["equip"]["accessory"]["level1"];
                    str_accessory += "</br>" + "攻击 +" + parseInt(data["equip"]["accessory"]["atk"]);
                    $("#cid_accessory").html(str_accessory);
                    $("#accessory_level2").html("+" + data["equip"]["accessory"]["level2"]);
                }
                else{
                    $("#cid_accessory").html("<span class='label label-danger'>" + "未装备</span>");
                }

                var str_real = "";
                for(var i =1; i <=6; i++){
                    var str_s = "";
                    if(data["relation"][i] == true){
                        str_s = "green";
                    }
                    else{
                        str_s = "default";
                    }
                    var cond_name =  "cond" + i + "name";
                    if (cond_name in DATA["general"][g_cid]){
                        str_real += '<a class="icon-btn">';
                        str_real += "<div>" + "<span class='btn " + str_s + "'>" + DATA["general"][g_cid][cond_name] + "</span></div>";
                        str_real += '</a>';
                    }
                }
                $("#relation_info").html(str_real);

                var str_soul = "";
                for(var k =1; k <= 8; k++){
                    str_soul += '<a class="icon-btn">';
                    if(data["soul"]["s" + k] != null){
                        var soul_cid =  data["soul"]["s"+k].cid;
                        var soul_quality = SOUL_JSON[soul_cid]["quality"];
                        var soul_css = QUALITY_CSS[soul_quality];
                        str_soul += "<div>" + "<span class='btn " + soul_css + "'>" + (SOUL_JSON[soul_cid].hasOwnProperty("name") ? SOUL_JSON[soul_cid]["name"] : SOUL_JSON[soul_cid]["name_CN"]) + "</span></div>";
                        str_soul += '<span class="badge badge-important">' + data["soul"]["s"+k].level + '级</span></a>';
                    }
                    else{
                        str_soul += "<div><span class='btn red'>未装备</span></div>";
                    }
                }
                $("#soul_info").html(str_soul);
                $("#general_modal").modal("show");
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};

function save_role(){
    var game_id = $("input[name='server_id']").val();
    var role_id = $("#role_id").val();
    var role_name = $("#role_name").text();
    var role_vip= $("#role_vip").text();
    var role_level = $("#role_level").text();
    var role_exp = $("#role_exp").text();
    var role_coin = $("#role_coin").text();
    var role_gold = $("#role_gold").text();
    var role_stamina = $("#role_stamina").text();
    var role_energy = $("#role_energy").text();
    var role_prestige = $("#role_prestige").text();
    var role_athletics = $("#role_athletics").text();
    var role_power = $("#role_power").text();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/updaterole',
            data: {game_id: game_id, role_id: role_id, role_name: role_name, role_vip: role_vip,
                   role_level: role_level, role_exp: role_exp, role_coin: role_coin, role_gold: role_gold,
                   role_stamina: role_stamina, role_energy: role_energy, role_prestige: role_prestige,
                   role_athletics: role_athletics, role_power: role_power
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"])
                }
                else{
                    Common.alert_message($("#error_modal"), 1, "修改角色成功.")
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
}

function tdClick(){
    var tdText = $(this).text();
    $(this).empty();

    var input = $("<input type='text'>");
    input.val(tdText);
    $(this).append(input);
    input.blur(function () {
        var input = $(this);
        var inputText = input.val();
        var div = input.parent("div");
        div.html(inputText);
        div.css("color", "red");
        div.dblclick(tdClick);
    });
}

function general_Click(){
    var tdText = $(this).text();
    $(this).empty();
    var input = $("<input type='text'>");
    input.val(tdText);
    $(this).append(input);
    input.blur(function () {
        var input = $(this);
        var inputText = input.val();

        var div = input.parent("div");

        div.html(inputText);
        div.css("color", "red");
        div.dblclick(general_Click);
    });
}

var validate_role = function(){
    var role_id = $("#role_id").val();

    var tag = true;
    if (role_id == "" || role_id == null || role_id == undefined || role_level.length == 0)
        tag = false;
    return tag;
};



$("#general").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#general").attr("href", "#tab_general");
        $.ajax({
                type: 'get',
                url: '/querygeneralinfo',
                data: {game_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    var str_g = "";
                    var general_arr = {};
                    var GENERAL_JSON = DATA["general"];
                    if (data["general"].length != 0) {
                        for (var k = 0; k < data["general"].length; k++) {

                            str_g += "<tr>";
                            str_g += "<td>" + data["general"][k].id + "</td>";
                            var cid = data["general"][k].cid;
                            var quality = GENERAL_JSON[cid]["quality"];
                            var general_name = GENERAL_JSON[cid].hasOwnProperty("name") ? GENERAL_JSON[cid]["name"] : GENERAL_JSON[cid]["name_CN"]
                            str_g += "<td>";
                            str_g += "<span class=\"btn default btn-xs " + QUALITY_CSS[quality] + "\">";
                            general_arr[data["general"][k].id] = {
                                "name": general_name,
                                "quality": QUALITY_CSS[quality]
                            };
                            str_g += general_name + "</span></td>";
                            str_g += "<td>" + data["general"][k]["level1"] + "</td>";
                            str_g += "<td>" + data["general"][k]["level2"] + "</td>";
                            str_g += "<td>" +  data["general"][k]["exp"] + "</td>";
                            str_g += "<td>" + data["general"][k]["hp_foster"] + "</td>";
                            str_g += "<td>" + data["general"][k]["atk_foster"] + "</td>";
                            str_g += "<td>" + data["general"][k]["def_foster"] + "</td>";
                            str_g += "<td>" + data["general"][k]["potential"] + "</td>";
                            str_g += "<td>" + data["general"][k]["skillexp"] + "</td>";
                            str_g += "<td>" + data["general"][k]["skilllevel"] + "</td>";
                            str_g += "<td>" + data["general"][k]["weapon"] + "</td>";
                            str_g += "<td>" + data["general"][k]["armor"] + "</td>";
                            str_g += "<td>" + data["general"][k]["accessory"] + "</td>";
                            str_g += "<td>" + data["general"][k]["head"] + "</td>";
                            str_g += "<td>" + data["general"][k]["treasure"] + "</td>";
                            str_g += "<td>" + data["general"][k]["horse"] + "</td>";
//                            str_g += "<td>";
//                            str_g += '&nbsp; <a onclick="update_general(' + data["general"][k].rid + ',' + data["general"][k].id + ')"' + 'class="btn default btn-xs green">保存 <i class="fa fa-check"></i></a>';
//                            str_g += "</td>";
                            str_g += "</tr>";
                        }
                        $('#general_list').html(str_g);
                    }

                    var str_slot = '<div class="clearfix">';
                    str_slot += '<h4 class="block">上阵武将</h4><div class="btn-group">';
                    for (var i = 1; i < 8; i++) {
                        if (data["slot"]["s" + i] != null) {
                            var iid = data["slot"]["s" + i];
                            var quality1 = general_arr[iid]["quality"];
                            str_slot += '<button type="button" onclick="query_generl(' + data["slot"]["s" + i] + ')" class="btn ' + quality1 + "\">" + "<span class='badge badge-default'>" + i + "</span>" + general_arr[iid]["name"] + '</button>';
                        }
                        else {
                            str_slot += '<button type="button" class="btn default red-stripe"><span class="badge badge-success">' + i + '</span>无</button>';
                        }
                    }
                    str_slot += '</div></div>';

                    str_slot += '<div class="clearfix">';
                    str_slot += '<h4 class="block">助威武将</h4>';
                    for (var j = 1; j < 9; j++) {
                        if (data["slot"]["c" + j] != null) {
                            var iid1 = data["slot"]["c" + j];
                            var quality2 = general_arr[iid1]["quality"];
                            str_slot += '<button type="button" onclick="query_generl(' + data["slot"]["c" + j] + ')" class="btn ' + quality2 + "\">" + "<span class='badge badge-default'>" + j + "</span>" + general_arr[iid1]["name"] + '</button>';
                        }
                        else {
                            str_slot += '<button type="button" class="btn default red-stripe"><span class="badge badge-success">' + j + '</span>无</button>';
                        }
                    }
                    str_slot += '</div>';

                    $("#slot_list").html(str_slot);

                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    }
});

$("#equip").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#equip").attr("href", "#tab_equip");

        var EQUIP_JSON = DATA["equip"];
        var equip_str = "";
        for (var e in EQUIP_JSON){
            equip_str += "<option value='" + e + "'>" + EQUIP_JSON[e]["quality"] + "星:" + (EQUIP_JSON[e].hasOwnProperty("name") ? EQUIP_JSON[e]["name"] : EQUIP_JSON[e]["name_CN"]) + "</option>";
        }
        $("#equip_cid").html(equip_str);

        $.ajax({
            type: 'get',
            url: '/queryequipinfo',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                var str_e = "";
                if (data.length != 0) {
                    for (var e = 0; e < data.length; e++) {
                        str_e += "<tr>";
                        str_e += "<td>" + data[e].id + "</td>";
                        str_e += "<td>";
                        var quality = EQUIP_JSON[data[e].cid]["quality"];
                        str_e += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                        str_e += (EQUIP_JSON[data[e].cid].hasOwnProperty("name") ? EQUIP_JSON[data[e].cid]["name"] : EQUIP_JSON[data[e].cid]["name_CN"]) + "</span></td>";
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
    }
});

$("#props").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#props").attr("href", "#tab_props");

        var PROPS_JSON = DATA["props"];
        var props_str = "";
        for (var p in PROPS_JSON){
            props_str += "<option value='" + p + "'>" + p + "-" + (PROPS_JSON[p].hasOwnProperty("name") ? PROPS_JSON[p]["name"] : PROPS_JSON[p]["name_CN"]) + "</option>";
        }
        $("#props_cid").html(props_str);
        $('#props_cid').change();

        $.ajax({
            type: 'get',
            url: '/querypropsinfo',
            data: {game_id: server_id, role_id: role_id},
            async: false,
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>";
                        str_p += '<span data-cid='+data[p]['cid']+' data-rid='+data[p]['rid']+'>'+ (PROPS_JSON[data[p].cid].hasOwnProperty("name") ? PROPS_JSON[data[p].cid]["name"] : PROPS_JSON[data[p].cid]["name_CN"]) + "</span></td>";
                        str_p += "<td><span class='prop_num' data-pk='1' style='text-decoration: underline;cursor: pointer'>" + data[p].num + "</span></td>";
                        str_p += "</tr>";
                    }
                    $("#props_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
        $('.prop_num').editable({
            type: "text",
            url: '/post/role/prop',
            ajaxOptions:{
              dataType: 'json'
            },
            params: function (params) {
                var $pre_div = $(this).parent().siblings().children();

                var data = {};
                data['id'] = params.pk;
                data['cid'] = $pre_div.attr('data-cid');
                data['cid_name'] = $pre_div.text();
                data['rid'] = $pre_div.attr('data-rid');
                data['new_num'] = params.value;
                data['server_id'] = server_id;
                return data
            },
            validate: function (value) {
                if (!$.trim(value)) {
                    return '不能为空';
                }
            },
            success: function(response) {
                if(response.status === 'fail'){
                    return response.errmsg
                }
            }
        })
    }
});


$("#soul").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#soul").attr("href", "#tab_soul");

        var SOUL_JSON = DATA["soul"];
        var soul_str = "";
        for(var s in SOUL_JSON){
            soul_str += "<option value='" + s + "'>" + SOUL_JSON[s]["quality"] + "星" + (SOUL_JSON[s].hasOwnProperty("name") ? SOUL_JSON[s]["name"] : SOUL_JSON[s]["name_CN"]) + "</option>";
        }
        $("#soul_cid").html(soul_str);

        $.ajax({
            type: 'get',
            url: '/querysoulinfo',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_s = "";
                    for (var s = 0; s < data.length; s++) {
                        str_s += "<tr>";
                        str_s += "<td>" + data[s].id + "</td>";
                        str_s += "<td>";
                        var quality = SOUL_JSON[data[s].cid]["quality"];
                        str_s += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                        str_s += (SOUL_JSON[data[s].cid].hasOwnProperty("name") ? SOUL_JSON[data[s].cid]["name"] : SOUL_JSON[data[s].cid]["name_CN"]) + "</span></td>";
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
    }
});

$("#guide").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#guide").attr("href", "#tab_guide");

        $.ajax({
            type: 'get',
            url: '/queryguideinfo',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_d = "";
                    for (var d = 0; d < data.length; d++) {
                        str_d += "<tr>";
                        str_d += "<td>" + data[d]["section"] + "</td>";
                        str_d += "<td>" + data[d]["step"] + "</td>";
                        str_d += "<td>" + data[d]["status"] + "</td>";
                        str_d += "<td>";
                        str_d += '&nbsp; <a onclick="mod_guide(' + data[d]["rid"] + ',' + data[d]["section"] + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                        str_d += "</td>";
                        str_d += "</tr>";
                    }
                    $("#guide_list").html(str_d);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
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
            var copy = DATA["copy"];
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + (DATA["map"][data[i]["map"]].hasOwnProperty("name") ? DATA["map"][data[i]["map"]]["name"] : DATA["map"][data[i]["map"]]["name_CN"]) + "</td>";

                str_info += "<td>" + (copy[data[i]["map"]][data[i]["point"]].hasOwnProperty("name") ? copy[data[i]["map"]][data[i]["point"]]["name"] : copy[data[i]["map"]][data[i]["point"]]["name_CN"]) + "</td>";
                str_info += "<td>" + data[i]["move"] + "</td>";
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
            var copy = DATA["star_copy"];
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + (DATA["star_map"][data[i]["map"]].hasOwnProperty("name") ? DATA["star_map"][data[i]["map"]]["name"] : DATA["star_map"][data[i]["map"]]["name_CN"]) + "</td>";

                str_info += "<td>" + (copy[data[i]["map"]][data[i]["point"]].hasOwnProperty("name") ? copy[data[i]["map"]][data[i]["point"]]["name"] : copy[data[i]["map"]][data[i]["point"]]["name_CN"]) + "</td>";
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


$("#copy").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#copy").attr("href", "#tab_copy");
        query_copy(role_id, $("#copy_list"));
    }
});

$("#general_copy").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#general_copy").attr("href", "#tab_general_copy");
        query_general_copy(role_id, $("#general_copy_list"));
    }
});

$("#error_battle").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#error_battle").attr("href", "#tab_battle");
        $.ajax({
                type: 'get',
                url: '/queryerrorbattleinfo',
                data: {game_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    if (data.length != 0) {
                        var str_b = "";
                        for (var b = 0; b < data.length; b++) {
                            str_b += "<tr>";
//                            str_b += "<td>" + data[b]["system"] + "</td>";
                            str_b += "<td>" + data[b]["time"] + "</td>";
                            str_b += "<td>";
                            str_b += '&nbsp; <a onclick="show_battle(' + data[b]["id"] + ')"' + 'class="btn default btn-xs blue" data-toggle="modal">查看 <i class="fa fa-edit"></i></a>';
                            str_b += '&nbsp; <a onclick="play_battle(' + data[b]["id"] + ')"' + 'class="btn default btn-xs green" data-toggle="modal">播放<i class="fa fa-play"></i></a>';

                            str_b += "</td>";
                            str_b += "</tr>";
                        }
                        $("#battle_report_list").html(str_b);
                    }
                },
                error: function(){
                }
        });
    }
});

$("#monthcard").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
        $("#monthcard").attr("href", "#tab_monthcard");
        $.ajax({
                type: 'get',
                url: '/querymonthcardinfo',
                data: {game_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    if (data.length != 0) {
                        $("#monthday1").val(data["day1"]);
                        $("#monthday2").val(data["day2"]);
                    }
                },
                error: function(){
                }
        });
    }
});

$("#get_battle").on("click", function(e){
    e.preventDefault();
    var role_id = $("#role_id").val();
    $.ajax({
            type: 'get',
            url: '/getbattle',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else{
                    $("#battle_report_detail").val(data["battle"]["report"]);
                    $("#battle_modal").modal("show");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});


$("#battle_put").on("click", function(e){
    e.preventDefault();
    var role_id = $("#role_id").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/setbattle',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else{
                    Common.alert_message($("#error_modal"), 1, "战报入库成功.");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

function update_month(tag, days){
    var role_id = $("#role_id").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/updatemonthcard',
            data: {server_id: server_id, role_id: role_id, month_type: tag, month_day: days},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else{
                    Common.alert_message($("#error_modal"), 1, "月卡充值成功.");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
}

$("#update_month1").bind("click", function(e){
    e.preventDefault();
    var days = $("#monthday1").val();
    update_month(1, days);
});

$("#update_month2").bind("click", function(e){
    e.preventDefault();
    var days = $("#monthday2").val();
    update_month(2, days);
});


$("#delete_guide").bind("click", function(e){
    e.preventDefault();
    var role_id = $("#role_id").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/deleteguide',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, "删除新手引导失败.");
                }
                else{
                    Common.alert_message($("#error_modal"), 1, "删除新手引导成功.");
                }
                $("#guide_list").html("");
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});


$("#query_role").bind("click", function(e){
    e.preventDefault();
    var start_date = $("#create_date").val();
    var end_date = $("#login_date").val();
    var channel = $("#user_channel").val();

    var new_guide = $("#new_guide").is(":checked");
    var online_time = $("#online_time").is(":checked");
    var last_time = $("#last_time").is(":checked");
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/querychannelrole2',
            data: {server_id: server_id, start_date: start_date, end_date: end_date, channel: channel},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (new_guide == true) {
                    $("#title_guide").removeClass("hide");
                }
                else{
                    $("#title_guide").addClass("hide");
                }
                if (last_time == true) {
                    $("#title_last").removeClass("hide");
                }
                else{
                    $("#title_last").addClass("hide");
                }
                if (online_time == true){
                    $("#title_online").removeClass("hide");
                }
                else{
                    $("#title_online").addClass("hide");
                }
                if(data.length != 0){
                    $("#total_num").html("总人数:" + data.length);
                    for(var i=0; i < data.length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["id"] + "</td>";
                        str_info += "<td>" + data[i]["name"] + "</td>";
                        str_info += "<td>" + data[i]["vip"] + "</td>";
                        str_info += "<td>" + data[i]["level"] + "</td>";
                        str_info += "<td>" + data[i]["exp"] + "</td>";
                        str_info += "<td>" + data[i]["coin"] + "</td>";
                        str_info += "<td>" + data[i]["gold"] + "</td>";
                        str_info += "<td>" + data[i]["stamina"] + "</td>";
//                        str_info += "<td>" + data[i]["maxstamina"] + "</td>";
                        str_info += "<td>" + data[i]["energy"] + "</td>";
//                        str_info += "<td>" + data[i]["maxenergy"] + "</td>";
                        str_info += "<td>" + data[i]["prestige"] + "</td>";
                        str_info += "<td>" + data[i]["athletics"] + "</td>";
                        str_info += "<td>" + data[i]["power"] + "</td>";
                        str_info += "<td>" + data[i]["channel"] + "</td>";
                        str_info += "<td>" + data[i]["createtime"] + "</td>";
                        if (new_guide == true){
                            if (data[i].step == 0){
                                str_info += "<td>新手引导完成</td>";
                            }
                            else if (data[i].step == -1){
                                str_info += "<td><span class='label label-danger'>未进入新手引导</span></td>";
                            }
                            else{
                                if (data[i]["step"] == 87)
                                {
                                    str_info += "<td>新手引导完成</td>";
                                }
                                else{
                                    str_info += "<td>步骤:" + data[i]["step"] + ";";
                                    str_info += data[i]["step_name"];
                                    if (data[i]["guide"] == "excute") {
                                        str_info += "<span class='label label-info'>执行</span></td>";
                                    }
                                    else if(data[i]["guide"] == "complete"){
                                        str_info += "<span class='label label-success'>完成</span></td>";
                                    }
                                }
                            }
                        }
                        if (online_time == true){
                            str_info += "<td>" + data[i]["online"] + "分钟</td>";
                        }
                        if(last_time == true){
                            str_info += "<td>" + data[i]["last_time"] + "</td>";
                        }
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="15" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#role_count_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

var POWER_TYPE = {
    "equip": "装备",
    "general": "武将",
    "pet": "魔宠",
    "soul": "命格",
    "treasure": "宝物"
};

$("#power").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str){
        $("#power").attr("href", "#tab_power");
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
                    var str_info = "";
                    var data_set = [];
                    for(var p in POWER_TYPE){
                        str_info += "<tr>";
                        str_info += "<td>" + POWER_TYPE[p] + "</td>";
                        str_info += "<td>" + data[p] + "</td>";
                        str_info += "</tr>";
                        var temp = {label: POWER_TYPE[p],
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
                error_func(XMLHttpRequest);
            }
            }
        )
    }
});

$("#recharge").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#recharge").attr("href", "#tab_recharge");
    }
});

$("#all_copy").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#all_copy").attr("href", "#tab_all_copy");
    }
});

$("#athletics").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#athletics").attr("href", "#tab_athletics");
        var role_id = $("#role_id").val();
        $.ajax({
            type: 'get',
            url: '/queryathleticsinfo',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data) {
                    var str_p = "";
                    str_p += "<tr>";
                    str_p += "<td>";
                    str_p += data["rank"] + "</td>";
                    str_p += "<td>" + data["status"] + "</td>";
                    str_p += "</tr>";
                    $("#athletics_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#pet_3").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#pet_3").attr("href", "#tab_pet_3");
        var role_id = $("#role_id").val();
        var PET_JSON = DATA["pet3_attr"];
        $.ajax({
            type: 'get',
            url: '/querypet3info',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>";
                        str_p += (PET_JSON[data[p].cid][0].hasOwnProperty("name") ? PET_JSON[data[p].cid][0]["name"] : PET_JSON[data[p].cid][0]["name_CN"]) + "</td>";
                        str_p += "<td>" + data[p].level + "</td>";
                        str_p += "</tr>";
                    }
                    $("#pet3_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#mieshendian").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#mieshendian").attr("href", "#tab_mieshendian");
        var role_id = $("#role_id").val();
        $.ajax({
            type: 'get',
            url: '/querymieshendianinfo',
            data: {game_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data) {
                    var str_p = "";
                    str_p += "<tr>";
                    str_p += "<td>";
                    str_p += data["level_max"] + "</td>";
                    //str_p += "<td>" + data["level_max_today"] + "</td>";
                    //str_p += "<td>" + data["count"] + "</td>";
                    //str_p += "<td>" + data["fail"] + "</td>";
                    //str_p += "<td>" + data["level"] + "</td>";
                    //str_p += "<td>" + data["point"] + "</td>";
                    //str_p += "<td>" + data["modupend"] + "</td>";
                    //str_p += "<td>" + data["point_get"] + "</td>";
                    //str_p += "<td>" + data["point_max"] + "</td>";
                    //str_p += "<td>" + data["integral"] + "</td>";
                    str_p += "</tr>";
                    $("#mieshendian_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#friendcopy").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#friendcopy").attr("href", "#tab_friendcopy");
        var role_id = $("#role_id").val();
        var EXPEDITION_JSON = DATA["expedition_map"];
        $.ajax({
            type: 'get',
            url: '/queryfriendcopyinfo',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>";
                        str_p += (EXPEDITION_JSON[data[p]["cid"]].hasOwnProperty("name") ? EXPEDITION_JSON[data[p]["cid"]]["name"] : EXPEDITION_JSON[data[p]["cid"]]["name_CN"]) + "</td>";
                        if (data[p]["kill"] == "-1") {
                            var status = "成功";
                        } else {
                            var status = "失败";
                        }
                        str_p += "<td>" + status + "</td>";
                        str_p += "</tr>";
                    }
                    $("#friendcopy_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#magicstone").on("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#magicstone").attr("href", "#tab_magicstone");
        var role_id = $("#role_id").val();
        $.ajax({
            type: 'get',
            url: '/querymagicstoneinfo',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>";
                        str_p += data[p]["slot"] + "</td>";
                        str_p += "<td>" + data[p]["g1"] + "</td>";
                        str_p += "<td>" + data[p]["g2"] + "</td>";
                        str_p += "<td>" + data[p]["g3"] + "</td>";
                        str_p += "<td>" + data[p]["g4"] + "</td>";
                        str_p += "<td>" + data[p]["g5"] + "</td>";
                        str_p += "<td>" + data[p]["g6"] + "</td>";
                        str_p += "<td>" + data[p]["g7"] + "</td>";
                        str_p += "<td>" + data[p]["g8"] + "</td>";
                        str_p += "</tr>";
                    }
                    $("#magicstone_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#gang").on("click", function(e) {
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#gang").attr("href", "#tab_gang");
        var role_id = $("#role_id").val();
        $.ajax({
            type: 'get',
            url: '/queryganginfo',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>" + data[p]["name"] + "</td>";
                        str_p += "<td>" + data[p]["exp"] + "</td>";
                        str_p += "<td>" + data[p]["level"] + "</td>";
                        str_p += "<td>" + data[p]["power"] + "</td>";
                        str_p += "<td>" + data[p]["time"] + "</td>";
                        str_p += "<td>" + data[p]["contribute_week"] + "</td>";
                        str_p += "</tr>";
                    }
                    $("#gang_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#gang_activity").on("click", function(e) {
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
        $("#gang_activity").attr("href", "#tab_gang_activity");
        var role_id = $("#role_id").val();
        $.ajax({
            type: 'get',
            url: '/querygangactivityinfo',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                console.log(data);
                if (data.length != 0) {
                    var str_p = "";
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>" + data[p]["pointtoday"] + "</td>";
                        str_p += "<td>" + data[p]["pointtotal"] + "</td>";
                        str_p += "<td>" + data[p]["time"] + "</td>";
                        str_p += "<td>" + data[p]["c1"] + "</td>";
                        str_p += "<td>" + data[p]["c2"] + "</td>";
                        str_p += "<td>" + data[p]["c3"] + "</td>";
                        str_p += "<td>" + data[p]["c6"] + "</td>";
                        str_p += "<td>" + data[p]["c7"] + "</td>";
                        str_p += "<td>" + data[p]["c8"] + "</td>";
                        str_p += "</tr>";
                    }
                    $("#gang_activity_list").html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
});

$("#confirm_recharge").on("click", function(e){
    var role_id = $("#role_id").val();
    var recharge_type = $("#recharge_type").val();
    var user_name = $.cookie("user_game");
    var user_recharge = $.cookie("user_recharge");
    var user_name_split = user_name.split("|");
    var user_recharge_split = user_recharge.split("|");
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var is_recharge = null;
    for(var i=0; i < user_name_split.length; i ++){
        if(user_name_split[i] == server_id){
            is_recharge = user_recharge_split[i]
        }
    }
    if (is_recharge != null && is_recharge == "1"){
        $.ajax({
            type: 'get',
            url: '/rolerecharge',
            data: {
                server_id: server_id,
                role_id: role_id,
                recharge_type: recharge_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                Common.alert_message($("#error_modal"), 1, "充值成功.");
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        })
    }
    else{
        no_auth_func();
    }
});

var SOURCE_TYPE = {
     AccCDKeyExchange: "兑换码",
     UserActivityStartGift: "累计30天奖励",
     UserAthleticsAttack: "竞技场",
     UserAthleticsBoss: "竞技场Boss",
     UserAthleticsRewardsExchange2: "竞技场兑换",
     UserBegin7DaysReward: "7天活动",
     UserConsumeGiftReward: "消费有礼",
     UserContinue7Reward: "连续7天奖励",
     UserCopyAttack: "普通副本",
     UserCopyPrestigeReward: "副本通关奖励",
     UserCupBattleReward: "杯赛奖励",
     UserDayDayGiftReward: "天天有礼",
     UserEncounterUse: "奇遇",
     UserEquipFragmentCompound: "碎片合成",
     UserEquipResolve: "装备分解",
     UserExpeditionAttack: "",
     UserFirstRechargeReward: "首冲奖励",
     UserGeneralInheritConfirm: "武将继承确认",
     UserLimitTimeShopBuy: "限时商店",
     UserLivenessReward: "活跃度奖励",
     UserMailRead: "邮件",
     UserMonthCardRewardGet: "月卡奖励",
     UserMysticalConfirm: "观星台",
     UserMysticalReward: "观星台奖励",
     UserOnlineReward: "在线奖励",
     UserSignIn: "登录",
     UserSoulResolve: "命格分解",
     UserTaskComplete: "成就",
     UserTreasureFragmentRob: "宝物合成",
     UserUseProps: "箱子",
     UserWorldBoss1Attack: "世界Boss",
     UserZhusendaiBattle: "灭神殿战斗",
     UserZhusendaiExchange: "灭神殿兑换",
     UserZhusendaiModup: "灭神殿扫荡"
};

$("#a_props_c").on("click", function(e){
    e.preventDefault();
    var str_info = "";
    str_info += "<th>道具编号</th>";
    str_info += "<th>道具名称</th>";
    str_info += "<th>数量</th>";
    for(var s in SOURCE_TYPE){
        str_info += "<th>" + SOURCE_TYPE[s] + "</th>";
    }
    $("#props_title").html(str_info);
});


$("#query_props").on("click", function(e){
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var s_date = $("#s_date").val();
    var e_date = $("#e_date").val();
    $.ajax({
        type: 'get',
        url: '/queryprops',
        data: {
            server_id: server_id,
            s_date: s_date,
            e_date: e_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            for(var d in data){
                str_info += "<tr>";
                str_info += "<td><a onclick='props_details(" + d + ")'>" + d + "</a></td>";
                str_info += "<td>";
                if (d > 20000 && d < 21000){
                    str_info += (PROPS_JSON[d].hasOwnProperty("name") ? PROPS_JSON[d]["name"] : PROPS_JSON[d]["name_CN"]);
                }
                else if (d > 21100 && d < 27000){
                    str_info += (EQUIP_JSON[d].hasOwnProperty("name") ? EQUIP_JSON[d]["name"] : EQUIP_JSON[d]["name_CN"]);
                }
                else{
                    str_info += (SOUL_JSON[d].hasOwnProperty("name") ? SOUL_JSON[d]["name"] : SOUL_JSON[d]["name_CN"]);
                }
                str_info += "</td>";
                str_info += "<td>" + data[d]["total"] + "</td>";

                for (var s in SOURCE_TYPE) {
                    if (s in data[d]["data"]) {
                        str_info += "<td class=\"success\">" + data[d]["data"][s] + "</td>";
                    }
                    else {
                        str_info += "<td>0</td>";
                    }
                }
                str_info += "</tr>";
            }
            $("#props_count_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});

function props_details(cid){
    var s_date = $("#s_date").val();
    var e_date = $("#e_date").val();
    $.ajax({
        type: 'get',
        url: '/querypropsrole',
        data: {
            server_id: server_id,
            cid: cid,
            s_date: s_date,
            e_date: e_date
        },
        dataType: 'JSON',
        success: function (data) {
            var str_info = "";
            for (var s in data){
                str_info += "<tr>";
                str_info += "<td>" + data[s]["role"]["id"] + "</td>";
                str_info += "<td>" + data[s]["role"]["name"] + "</td>";
                str_info += "<td>";
                for (var d in data[s]["data"]){
                    str_info += SOURCE_TYPE[d] + ",";
                }
                str_info += "<td>" + data[s]["rob"] + "</td>";
                str_info += "</td>";
                if ("UserUseProps" in data[s]["data"]){
                    str_info += "<td>" + data[s]["data"]["UserUseProps"] + "</td>";
                }
                else{
                    str_info += "<td>0</td>";
                }
                str_info += "<td>" + data[s]["role"]["recharge"] + "</td>";

                str_info += "<td>" + data[s]["role"]["power"] + "</td>";
                str_info += "<td>" + data[s]["usegold"] + "</td>";
                str_info += "</tr>";
            }
            $("#props_details_list").html(str_info);
            $("#props_role_modal").modal("show");
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
}

$("#open_all_copy").on("click", function(e){
    e.preventDefault();
    var role_id = $("#role_id").val();
    $.ajax({
        type: 'get',
        url: '/openallcopy',
        data: {
            server_id: server_id,
            rid: role_id
        },
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "success"){
                Common.alert_message($("#error_modal"), 1, "操作成功");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "操作失败:" + data["errmsg"]);
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
});

