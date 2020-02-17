/**
 * Created by wangrui on 16/3/14.
 */
get_section($("#select_section"));
handleDatePickers2();

var activity_time = "activity_time";
var content_time = ["id", "systemid", "icon", "type", "name", "seq", "begin", "end", "generalanimation"];
var grow_plan_json = null;
var month_card_json = null;
var reward_json = null;
var dayday_gift_json = null;
var reward_list = [];
var ctype_reward = {
    "props": "道具",
    "equip": "装备",
    "general": "武将",
    "general_fragment": "武将碎片",
    "coin": "银两",
    "gold": "元宝",
    "pet2_attr": "魔宠",
    "pet3_fragment": "魔宠碎片"
};

//activity_time配置表ID发生变化后，需要修改.
var activity_type = {
    7: {
        "name": "growplan",
        "list": ["id", "level", "gold"]
    },
    6: {
        "name": "recharge",
        "list": []
    },
    8: {
        "name": "monthcardgift",
        "list": ["id", "rmb", "reward"]
    },
    11: {
        "name": "toplevel",
        "list": []
    },
    14: {
        "name": "daydaygift_item",
        "list": ["id", "day", "rmb", "reward"]
    },
    15: "consumegift_reward",
    16: "recharge_gift",
    101: "month_growup",
    24: "treasure_discount"
};
var activity_json_data = {};


function display_ctype_reward(){
    var str_html = "";
    for (var cr in ctype_reward){
        str_html += "<option value='" + cr + "'>" + ctype_reward[cr] + "</option>";
        if (cr == "coin" || cr == "gold") {
            console.log(cr);
        }
        else{
            reward_list.push(cr);
        }
    }
    $("#select_reward_type").html(str_html);
    $("#gift_select_reward_type").html(str_html);
}
display_ctype_reward();


var query_json_data = function(str_name){
    var temp_data = null;
    var section = $("#select_section").val();
    $.ajax({
        type: 'get',
        url: '/queryjsondatabysection',
        data: {
            section: section,
            type: JSON.stringify([str_name])
        },
        dataType: 'JSON',
        async:false,
        success: function (data) {
            temp_data = data[str_name];
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
    return temp_data;
};


var query_activity_time_data = function(tag){
    if (tag == 0){
        activity_json_data = query_json_data(activity_time);
    }
    var str_info = "";
    for (var d in activity_type) {
        str_info += "<tr>";
        str_info += "<td>" + activity_json_data[d]["id"] + "</td>";
        str_info += "<td>" + activity_json_data[d]["name"] + "</td>";
        str_info += "<td>" + activity_json_data[d]["begin"] + "</td>";
        str_info += "<td>" + activity_json_data[d]["end"] + "</td>";
        str_info += "<td>";
        str_info += '&nbsp; <a onclick="config_activity(' + "'" + activity_json_data[d]["id"] + "'" + ')"' + 'class="btn default btn-xs blue" data-toggle="modal">配置 <i class="fa fa-gear"></i></a>';
        str_info += '&nbsp; <a onclick="mod_activity(' + "'" + d + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
        str_info += "</td>";
        str_info += "</tr>";
    }
    $("#activity_time_list").html(str_info);
};
query_activity_time_data(0);


function save_activity(tag, name, param, json_data){
    var section = $("#select_section").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'post',
        url: '/saveactivity',
        data: {
            section: section,
            name: name,
            param: JSON.stringify(param),
            data: JSON.stringify(json_data)
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            if (tag == 1){
                query_activity_time_data();
            }

        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
}

function display_grow_plan(){
    var str_html = "";
    for (var q in grow_plan_json) {
        str_html += "<tr>";
        str_html += "<td>" + q + "</td>";
        str_html += "<td>" + grow_plan_json[q]["level"] + "</td>";
        str_html += "<td>" + grow_plan_json[q]["gold"] + "</td>";
        str_html += "<td>";
        str_html += '&nbsp; <a onclick="mod_grow_plan(' + "'" + q + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
        str_html += "</td>";
        str_html += "</tr>";
    }
    $("#grow_plan_list").html(str_html);
}


function read_json(){
    if (reward_json == null){
        console.log("reward_list", reward_list);
        var section = $("#select_section").val();
        $.ajax({
            type: 'get',
            url: '/queryjsondatabysection',
            data: {
                section: section,
                type: JSON.stringify(reward_list)
            },
            dataType: 'JSON',
            async:false,
            success: function (data) {
                reward_json = data;
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
}

setTimeout("read_json()", 2000);


function validate_type_str(t_int){
    var temp = "";
    if (t_int >= 10001 && t_int <= 10701) {
        temp = "general";
    } else if (t_int == 30001) {
        temp = "general";
    }
    else if(t_int >= 11201 && t_int <=11701) {
        temp = "general_fragment";
    }
    else if (t_int >= 20001 && t_int <= 21000) {
        temp = "props";
    }
    else if (t_int >= 21001 && t_int <= 30000) {
        temp = "equip";
    }
    else if (t_int >= 91001 && t_int <= 91005) {
        temp = "pet3_fragment";
    }
    else if (t_int >= 90001 && t_int <= 90005) {
        temp = "pet2_attr";
    }
    else if (t_int == 1000) {
        temp = "coin";
    }
    else if (t_int == 1001) {
        temp = "gold";
    }
    return temp;
}


function split_reward(str_reward){
    var temp_split = str_reward.split(";");
    return temp_split[0].split(",");
}


function split_reward_second(str_reward) {
    var temp_split = str_reward.split(";");
    return temp_split[1].split(",");
}


function display_select_reward(ctype, div){
    var str_html = "";
    if (ctype == "coin"){
        str_html += "<option value='1000'>" + ctype_reward["coin"] + "</option>";
    }
    else if (ctype == "gold"){
        str_html += "<option value='1001'>" + ctype_reward["gold"] + "</option>";
    }
    else{
        for(var s in reward_json[ctype]){
            var name = "";
            console.log("ctype", ctype, "s", s);
            //console.log(reward_json[ctype][s]["name"]);reward_json[ctype][s]["name"]
            console.log(reward_json);
            name = configtable_judge_name(ctype, s);
            str_html += "<option value='" + s + "'>" + name + "</option>";
        }
    }

    div.html(str_html);
}

function return_coin_gold(t_int){
    if (t_int == "1000")
        return ctype_reward["coin"];
    else if (t_int == "1001")
        return ctype_reward["gold"];
    else
        return ""
}


$("#select_reward_type").on("change", function(e){
    e.preventDefault();
    var s_type = $(this).val();
    console.log("s_type", s_type);
    display_select_reward(s_type, $("#select_reward"));
});


$("#gift_select_reward_type").on("change", function(e){
    e.preventDefault();
    var s_type = $(this).val();
    console.log("s_type", s_type);
    display_select_reward(s_type, $("#gitf_select_reward"));
});


function display_month_card(){
    var str_html = "";
    for (var q in month_card_json) {
        str_html += "<tr>";
        str_html += "<td>" + q + "</td>";
        str_html += "<td>" + month_card_json[q]["rmb"] + "</td>";
        var reward = month_card_json[q]["reward"];
        var temp_str = split_reward(reward);
        var cid = temp_str[0];
        var num = temp_str[1];
        var name = return_coin_gold(cid);
        if (name.length == 0){
            var str_temp = validate_type_str(parseInt(cid));
            name = reward_json[str_temp][cid]["name"];
        }
        str_html += "<td>" + ctype_reward[str_temp] + "</td>";
        str_html += "<td>" + name + "</td>";
        str_html += "<td>" + num + "</td>";
        str_html += "<td>";
        str_html += '&nbsp; <a onclick="mod_month_card(' + "'" + q + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
        str_html += "</td>";
        str_html += "</tr>";
    }
    $("#month_card_list").html(str_html);
}


function configtable_judge_name(str_temp, cid) {
    var name = ""
    if (str_temp == "general_fragment") {
        var general_id = reward_json[str_temp][cid]["general"];
        name = reward_json["general"][general_id]["name"];
        name = name + "碎片";
    }
    else if (str_temp == "pet3_fragment") {
        var pet_id = reward_json[str_temp][cid]["petid"];
        name = reward_json["pet2_attr"][pet_id]["0"]["name"];
        name = name + "碎片";
    }
    else if (str_temp == "pet2_attr") {
        name = reward_json[str_temp][cid]["0"]["name"];
    }
    else {
        name = reward_json[str_temp][cid]["name"];
    }
    return name
}


function display_dayday_gift() {
    var str_html = "";
    for (var q in dayday_gift_json) {
        str_html += "<tr>";
        str_html += "<td>" + q + "</td>";
        str_html += "<td>" + dayday_gift_json[q]["day"] + "</td>";
        str_html += "<td>" + dayday_gift_json[q]["rmb"] + "</td>";
        var reward = dayday_gift_json[q]["reward"];
        var temp_str = split_reward(reward);
        var cid = temp_str[0];
        var num = temp_str[1];
        var name = return_coin_gold(cid);
        var reward_type = name;
        if (name.length == 0){
            var str_temp = validate_type_str(parseInt(cid));
            name = configtable_judge_name(str_temp, cid);
            var reward_type = ctype_reward[str_temp];
        }
        str_html += "<td>" + reward_type + "</td>";
        str_html += "<td>" + name + "</td>";
        str_html += "<td>" + num + "</td>";
        var second_temp_str = split_reward_second(reward);
        //console.log("00000000000000", second_temp_str);
        var second_cid = second_temp_str[0];
        var second_num = second_temp_str[1];
        var second_name = return_coin_gold(second_cid);
        var second_reward_type = second_name;
        if (second_name.length == 0){
            var str_temp = validate_type_str(parseInt(second_cid));
            //console.log("00000000000000", str_temp);
            second_name = configtable_judge_name(str_temp, second_cid);
            var second_reward_type = ctype_reward[str_temp];
        }
        //console.log("second_reward_type", second_reward_type);
        //console.log("second_name", second_name);
        str_html += "<td>" + second_reward_type + "</td>";
        str_html += "<td>" + second_name + "</td>";
        str_html += "<td>" + second_num + "</td>";
        str_html += "<td>";
        str_html += '&nbsp; <a onclick="mod_dayday_gift(' + "'" + q + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
        str_html += "</td>";
        str_html += "</tr>";
    }
    $("#dayday_gift_list").html(str_html);
}


var config_activity = function(tag){
    var str_activity = activity_type[tag]["name"];
    if (tag == 6){
        Common.alert_message($("#error_modal"), 0, "双倍充值活动不可配置。");
    }
    else if(tag == 7){
        grow_plan_json = query_json_data(str_activity);
        display_grow_plan();
        $("#grow_plan_modal").modal("show");
    }
    else if(tag == 8){
        month_card_json = query_json_data(str_activity);
        display_month_card();
        $("#month_card_modal").modal("show");
    }
    //else if(tag == 11) {
    //    query_json_data(str_activity);
    //}
    else if(tag == 14) {
        dayday_gift_json = query_json_data(str_activity);
        display_dayday_gift();
        $("#dayday_gift_modal").modal("show");
    }
};


var mod_grow_plan = function(q){
    var level = grow_plan_json[q]["level"];
    var gold = grow_plan_json[q]["gold"];
    $("#grow_plan_id").val(q);
    $("#grow_plan_level").val(level);
    $("#grow_plan_gold").val(gold);
    $("#grow_plan_info_modal").modal("show");
};


$("#btn_grow_plan_confirm").on("click", function(e){
    e.preventDefault();
    var grow_plan_id = $("#grow_plan_id").val();
    grow_plan_json[grow_plan_id]["level"] = $("#grow_plan_level").val();
    grow_plan_json[grow_plan_id]["gold"] = $("#grow_plan_gold").val();
    display_grow_plan();
    $("#grow_plan_info_modal").modal("hide");
});

$("#btn_grow_plan").on("click", function(e){
    e.preventDefault();
    save_activity(2, activity_type[7]["name"], activity_type[7]["list"], grow_plan_json);
    $("#grow_plan_modal").modal("hide");
});

$("#btn_grow_cancel").on("click", function(e){
    e.preventDefault();
    $("#grow_plan_info_modal").modal("hide");
});


$("#add_month_card").on("click", function(e){
    e.preventDefault();
    $("#month_card_id").val("");
    $("#month_card_rmb").val("");
    $("#select_reward_type").change();
    $("#month_card_info_modal").modal("show");
});


var mod_month_card = function(q){
    $("#month_card_id").val(month_card_json[q]["id"]);
    $("#month_card_rmb").val(month_card_json[q]["rmb"]);
    var reward = month_card_json[q]["reward"];
    var temp_str = split_reward(reward);
    var cid = temp_str[0];
    var num = temp_str[1];
    var str_temp = validate_type_str(parseInt(cid));
    var select_reward_type = $("#select_reward_type");
    select_reward_type.change();
    select_reward_type.val(str_temp);
    $("#select_reward").val(cid);
    $("#month_card_num").val(num);
    $("#month_card_info_modal").modal("show");
};


var mod_dayday_gift = function(q) {
    $("#dayday_gift_id").val(dayday_gift_json[q]["id"]);
    //console.log(dayday_gift_json[q]["id"]);
    $("#dayday_gift_rmb").val(dayday_gift_json[q]["rmb"]);
    var reward = dayday_gift_json[q]["reward"];
    var temp_str = split_reward(reward);
    var cid = temp_str[0];
    var num = temp_str[1];
    var str_temp = validate_type_str(parseInt(cid));
    var select_reward_type = $("#gift_select_reward_type");
    select_reward_type.change();
    //console.log("str_temp", str_temp);
    select_reward_type.val(str_temp);
    $("#gitf_select_reward").val(cid);
    $("#dayday_gitf_num").val(num);
    $("#dayday_gift_info_modal").modal("show");
}


$("#btn_month_card_cancel").on("click", function(e){
    e.preventDefault();
    $("#month_card_info_modal").modal("hide");
});


$("#btn_month_card_confirm").on("click", function(e){
    e.preventDefault();
    var month_card_id = $("#month_card_id").val();
    var month_card_rmb = $("#month_card_rmb").val();
    var select_reward = $("#select_reward").val();
    var month_card_num = $("#month_card_num").val();
    month_card_json[month_card_id]["rmb"] = month_card_rmb;
    month_card_json[month_card_id]["reward"] = select_reward + "," + month_card_num + ";";
    $("#month_card_modal").modal("hide");
    display_month_card();
});


$("#btn_month_card").on("click", function(e){
    e.preventDefault();
    save_activity(2, activity_type[8]["name"], activity_type[8]["list"], month_card_json);
    $("#month_card_modal").modal("hide");
});


$("#btn_dayday_gift_cancel").on("click", function(e){
    e.preventDefault();
    $("#dayday_gift_info_modal").modal("hide");
});


$("#add_dayday_gift").on("click", function(e){
    e.preventDefault();
    $("#dayday_gift_id").val("");
    $("#dayday_gift_rmb").val("");
    $("#gitf_select_reward").change();
    $("#dayday_gift_info_modal").modal("show");
});


$("#btn_dayday_gift_confirm").on("click", function(e){
    e.preventDefault();
    var dayday_gift_id = $("#dayday_gift_id").val();
    var dayday_gift_rmb = $("#dayday_gift_rmb").val();
    var gitf_select_reward = $("#gitf_select_reward").val();
    var dayday_gitf_num = $("#dayday_gitf_num").val();
    month_card_json[dayday_gift_id]["rmb"] = dayday_gift_rmb;
    month_card_json[dayday_gift_id]["reward"] = gitf_select_reward + "," + dayday_gitf_num + ";";
    $("#dayday_gift_modal").modal("hide");
    display_dayday_gift();
});


var mod_activity = function(a_id){
    var start = activity_json_data[a_id]["begin"];
    var end = activity_json_data[a_id]["end"];
    $("#activity_id").val(a_id);
    $("#activity_name").html(activity_json_data[a_id]["name"]);
    $("#start_date").val(start.substring(0, 8));
    $("#end_date").val(end.substring(0, 8));
    $("#activity_time_modal").modal("show");
};


$("#btn_set_time").on("click", function(e){
    e.preventDefault();
    var activity_id = $("#activity_id").val();
    var start_date = $("#start_date").val() + "000000";
    var end_date = $("#end_date").val() + "000000";
    activity_json_data[activity_id]["begin"] = start_date;
    activity_json_data[activity_id]["end"] = end_date;
    $("#activity_time_modal").modal("hide");
    query_activity_time_data(1);
});


$("#save_activity").on("click", function(e){
    e.preventDefault();
    save_activity(1, activity_time, content_time, activity_json_data);
});


$("#reload_config").on("click", function(){
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/reloadconfig',
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                console.log(data);
                if (data["status"] == "success") {
                    setTimeout("Common.alert_message($(\"#error_modal\"), 1, \"配置加载成功.\")", 1000);
                }
                else {
                    setTimeout("Common.alert_message($(\"#error_moda\"), 0, \"配置加载失败.\")", 1000);
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});