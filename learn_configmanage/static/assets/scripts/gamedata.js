/**
 * Created by wangrui on 15/5/8.
 */
var $select_type1 = $("#select_type1");
var $select_type2 = $("#select_type2");
var $select_type3 = $("#select_type3");
var $select_gameserver = $("#select_gameserver");
var $select_gameserver2 = $("#select_gameserver2");
var $select_channel = $('#select_channel');
var $multiple_server_select = $('#multiple_server_select');
var $btn_query_level_2 = $('#btn_query_level_2');
var $single_server_select_div = $('#single_server_select_div');
getGameServerData($select_gameserver, 1);
getGameServerData($select_gameserver2, 1);
getPartnerData($select_channel);

$multiple_server_select.multiselect({
    numberDisplayed: 3,
    enableFiltering: true,
    nonSelectedText: "==请选择(最多选择4项)==",
    buttonWidth: '100%',
    maxHeight: 300,
    onChange: function(option) {
        // Get selected options.
        var selectedOptions = $multiple_server_select.find('option:selected');

        if (selectedOptions.length >= 4) {
          // Disable all other checkboxes.
          var nonSelectedOptions = $multiple_server_select.find('option').filter(function() {
            return !$(this).is(':selected');
          });

          // var dropdown = $channel_list_select.siblings('.multiselect-container');
          nonSelectedOptions.each(function() {
            var input = $('input[value="' + $(this).val() + '"]');
            input.prop('disabled', true);
            input.parent('li').addClass('disabled');
          });
        }
        else {
          // Enable all checkboxes.
          // var dropdown = $channel_list_select.siblings('.multiselect-container');
          $multiple_server_select.find('option').each(function() {
            var input = $('input[value="' + $(this).val() + '"]');
            input.prop('disabled', false);
            input.parent('li').addClass('disabled');
          });
        }
    }
}
);

var multi_select_data = [];
var multi_init_value = '';
for (var i in GAME_SERVER_DICT){
    if (multi_init_value.length === 0){
        multi_init_value = i;
    }
    multi_select_data.push({"label":i+'区:'+ GAME_SERVER_DICT[i]["name"],"value":i});
}
$multiple_server_select.multiselect('dataprovider',multi_select_data);
$multiple_server_select.multiselect('select', multi_init_value);

handleDatePickers();
$("#text_liveness_date").val(getNowFormatDate(1));
$("#gamedata_date").val(getNowFormatDate(1));


$select_gameserver.on("change", function(e){
    e.preventDefault();
    $(".tabbable-custom .active a").click();
});


var TYPE1_DATA = {
    "server": "区服",
    "level": "等级",
    "vip": "VIP等级"
};

var TYPE2_DATA = {
    "online": "在线时长",
    "power": "战斗力",
    "coin": "银币",
    "gold": "元宝",
    "props": "道具",
    "equip": "装备",
    "equip_quality": "装备品质",
    "treasure": "宝物",
    "protagonist": "魔王突破",
    "artifact": "法宝洗练",
    "gem": "魔符强化等级",
    "pet": "宠物突破",
    "pet3_passiveskill": "宠物被动技能",
    "general": "武将",
    "magicstone": "神石强化等级",
    "stamina": "体力",
    "athletics": "竞技场消耗",
    "watchstart": "一键观星",
    "passbattle": "过关斩将",
    "trialreset": "冠军试炼充值次数",
    "gold_use": "元宝消耗日区间"
};

var TYPE_18N = {
    "online": "【分钟-人】",
    "power": "【万-人】",
    "coin": "【万-人】",
    "gold": "【个-人】",
    "props": "【个-人】",
    "equip": "【个-人】",
    "equip_quality": "【星-人】",
    "treasure": "【等级-人】",
    "protagonist": "【阶-人】",
    "artifact": "【属性-人】",
    "gem": "【等级-人】",
    "pet": "【阶-人】",
    "pet3_passiveskill": "【星-人】",
    "general": "【等级-人】",
    "magicstone": "【等级-人】",
    "stamina": "【-人】",
    "athletics": "【次数-人】",
    "watchstart": "【次数-人】",
    "passbattle": "【-人】",
    "trialreset": "【-人】",
    "gold_use": "【-人】"
};

var TYPE3_DATA = {
    "props": {
        "20222": "洗练石",
        "20017": "突破丹",
        "20196": "初级经验丹",
        "20197": "中级经验丹",
        "20198": "高级经验丹",
        "20199": "神奇经验丹",
        "20200": "魂蛋",
        "20256": "精炼石",
        "20270": "锻造石",
        "20164": "泥威雅",
        "20163": "香奶儿",
        "20165": "Sixgod",
        "20128": "洞天护符",
        "20099": "灵元",
        "20166": "灵魂石",
        "20262": "遥控器",
        "20010": "传音符",
        "20009": "培养丹",
        "20278": "觉醒丹",
        "20276": "铜矿石",
        "20277": "铁矿石",
        "20275": "秘银石",
        "20274": "金刚石",
        "20282": "低级升星石",
        "20283": "高级升星石",
        "20281": "能量精华",
        "20285": "游戏币",
        "20286": "魔王纪念币"
    },
    "equip": {
        "level": "强化",
        "break": "进阶",
        "baptize": "洗练"
    },
    "treasure": {
        "level": "强化",
        "break": "精炼"
    },
    "general": {
        "level": "等级",
        "break": "突破"
    },
    "equip_quality": {
        2: "2星",
        3: "3星",
        4: "4星",
        5: "5星",
        6: "5星套装"
    },
    "pet3_passiveskill":{
        2: "2星",
        3: "3星",
        4: "4星",
        5: "5星"
    },
    "magicstone": {
        1: "攻击神石",
        2: "防御神石",
        3: "生命神石",
        4: "命中神石",
        5: "闪避神石",
        6: "反击神石",
        7: "抗暴神石",
        8: "抗反神石"
    }
};


init_select_html(false, TYPE1_DATA, $select_type1);
init_select_html(false, TYPE2_DATA, $select_type2);

$select_type1.on("change", function(e){
    e.preventDefault();
    if($(this).val() == "server"){
        $select_gameserver2.attr("disabled", "disabled");
    }
    else{
        $select_gameserver2.removeAttr("disabled");
    }
});

$select_type2.on("change", function(e){
    e.preventDefault();
    var type2 = $(this).val();
    if (TYPE3_DATA.hasOwnProperty(type2)){
        init_select_html(false, TYPE3_DATA[type2], $select_type3);
        $("#div_type3").removeClass("hidden");
    }
    else{
        $("#div_type3").addClass("hidden");
    }
});

$("#query_gamedata").on("click", function(e){
    e.preventDefault();
    var type1 = $select_type1.val();
    var type2 = $select_type2.val();
    var type3 = $select_type3.val();
    var server = $select_gameserver2.val();
    var query_date = $("#gamedata_date").val();
    if(!TYPE3_DATA.hasOwnProperty(type2)){
        type3 = ''
    }
    var data = {
        type1: type1,
        type2: type2,
        type3: type3,
        server: server,
        query_date: query_date
    };
    var type1_name = $select_type1.children("option:selected").text();
    var success = function(data){
        var str_html = "";
        var str_title = "<th>" + type1_name + "</th>";
        if (data){
            if (type1 == "server"){
                var tag1 = true;
                for(var sd in data){
                    str_html += "<tr>";
                    str_html += "<td>" + sd + "区:" + data[sd]["name"] + "</td>";
                    for(var di in data[sd]["data"]){
                        if (tag1){
                            str_title += "<th>" + di + TYPE_18N[type2] + "</th>";
                        }
                        str_html += "<td>" + data[sd]["data"][di] + "</td>";
                    }
                    tag1 = false;
                    str_html += "</tr>";
                }
            }
            else{
                var s_data = JSON.parse(data["data"]);
                var tag = true;
                for(var d in s_data){
                    str_html += "<tr>";
                    str_html += "<td>" + d + "</td>";
                    for(var i in s_data[d]){
                        if (tag){
                            str_title += "<th>" + i + "</th>";
                        }
                        str_html += "<td>" + s_data[d][i] + "</td>";

                    }
                    tag = false;
                    str_html += "</tr>";
                }
            }

        }
        $("#gamedata_list").html(str_html);
        $("#gamedata_title").html(str_title);
    };
    my_ajax(true, "/querygamedata", "get", data, true, success);
});


$("#a_role").on("click", function (e){
    e.preventDefault();
    $single_server_select_div.show();
    var success = function(data){
        var str_html = "";
        for(var d = 0; d<data["data"].length; d++){
            str_html += "<tr>";
            str_html += "<td>" + data["data"][d]["name"] + "/" + data["data"][d]["server"] + "</td>";
            str_html += "<td>" + data["data"][d]["create_time"] + "</td>";
            str_html += "<td>" + data["data"][d]["days"] + "</td>";
            var total = data["data"][d]["total"];
            str_html += "<td>" + total + "</td>";
            str_html += "<td>" + data["data"][d]["active"] + "</td>";
            str_html += "<td>" + data["data"][d]["recharge"] + "</td>";
            for (var n = 0; n < data["data"][d]["data"].length; n++) {
                var role_num = data["data"][d]["data"][n];
                var percent = 0.0;
                if (total != 0) {
                    percent = parseFloat(role_num / total * 100).toFixed(2);
                }
                str_html += "<td>" + role_num + "/" + percent + "%</td>";
            }
            var all_total = 0.0;
            if (data["total"] != 0) {
                all_total = parseFloat(total / data["total"] * 100).toFixed(2);
            }
            str_html += "<td>" + all_total + "%</td>";
            str_html += "</tr>";
        }
        $("#level_list").html(str_html);
    };
    my_ajax(true, "/querylevel2", "get", {}, true, success);
});

$("#a_role").click();

$btn_query_level_2.click(function () {

    if ($multiple_server_select.val() === null){
        alert('游戏服不能为空');
    }else{
        $("#a_role_2").click();
    }
});
$("#a_role_2").on("click", function (e){
    e.preventDefault();
    $single_server_select_div.hide();
    var page_content = $('.page-content');
    var channel_id = $select_channel.val();
    var server_id = $multiple_server_select.val();
    if (server_id === null){
        server_id = multi_init_value;
    }else{
        server_id = server_id.join(',');
    }
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/querylevel",
            data: {server_id: server_id, channel_id: channel_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";

                var chart_rate1 = 0;
                var chart_rate2 = 0;
                var chart_rate3 = 0;
                var chart_rate4 = 0;
                var chart_rate5 = 0;
                var chart_rate6 = 0;
                if (data["data"].length != 0){

                    for(var i=0; i<data["data"].length; i++){
                        str_info += "<tr>";
                        var level = data["data"][i]["level"];
                        str_info += "<td>" + data["data"][i]["level"] + "</td>";
                        str_info += "<td>" + data["data"][i]["num"] + "</td>";
                        var level_rate = commonPercent(data["data"][i]["num"], data["total"]);
                        str_info += "<td>" + level_rate + "%</td>";
                        level_rate = parseFloat(level_rate);
                        if (level >= 1 && level <= 10){
                            chart_rate1 += level_rate;
                        }
                        else if (level >= 11 && level <= 20){
                            chart_rate2 += level_rate;
                        }
                        else if (level >= 21 && level <= 30){
                            chart_rate3 += level_rate;
                        }
                        else if (level >= 31 && level <= 40){
                            chart_rate4 += level_rate;
                        }
                        else if (level >= 41 && level <= 50){
                            chart_rate5 += level_rate;
                        }
                        else{
                            chart_rate6 += level_rate;
                        }
                    }
                    var data_set = [
                        {
                            label: "1~10级",
                            data: chart_rate1
                        },
                        {
                            label: "11~20级",
                            data: chart_rate2
                        },
                        {
                            label: "21~30级",
                            data: chart_rate3
                        },
                        {
                            label: "31~40级",
                            data: chart_rate4
                        },
                        {
                            label: "41~50级",
                            data: chart_rate5
                        },
                        {
                            label: "51~60级",
                            data: chart_rate6
                        }
                    ];
                    drawPieChart($("#chart_level"), data_set);
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#level_count_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});




$("#a_vip").bind("click", function(e){
    e.preventDefault();
    $single_server_select_div.show();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var server_id = $("#select_gameserver").val();
    $.ajax({
            type: 'get',
            url: "/queryvip",
            data: {server_id: server_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data["data"].length != 0){
                    for(var i=0; i<data["data"].length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data["data"][i]["level"] + "</td>";
                        str_info += "<td>" + data["data"][i]["num"] + "</td>";
                        var level_rate = commonPercent(data["data"][i]["num"], data["total"]);
                        str_info += "<td>" + level_rate + "%</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#vip_count_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});


var equip_query = function(){
    var equip_star = $("#equip_star").val();
    var server_id = $("#select_gameserver").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryequip',
        data: {
            server_id: server_id,
            equip_star: equip_star
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != "") {
                for (var s in data) {
                    str_info += "<tr>";
                    str_info += "<td>";
                    if (equip_star == "2") {
                        str_info += "<a class='btn btn-xs green'>" + data[s]["name"] + "</a>";
                    }
                    else if (equip_star == "3") {
                        str_info += "<a class='btn btn-xs blue'>" + data[s]["name"] + "</a>";
                    }
                    else if (equip_star == "4") {
                        str_info += "<a class='btn btn-xs purple'>" + data[s]["name"] + "</a>";
                    }
                    else if (equip_star == "5"){
                        str_info += "<a class='btn btn-xs yellow'>" + data[s]["name"] + "</a>";
                    }
                    else{
                        str_info += "<a class='btn btn-xs red'>" + data[s]["name"] + "</a>";
                    }
                    str_info += "</td>";
                    str_info += "<td>" + data[s]["num"] + "</td>";
                    str_info += "<td>" + (data[s]["users"] / data[s]["total"] * 100).toFixed(2) + "%</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#equip_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
};

$("#a_equip").on("click", function(e){
    $single_server_select_div.show();
    equip_query();
});

$("#equip_star").on("change", function(e){
    e.preventDefault();
    equip_query();
});


var general_query = function(){
    var server_id = $("#select_gameserver").val();
    var general_star = $("#general_star").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querygeneralbyid',
        data: {server_id: server_id, general_star: general_star},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != "") {
                for (var s in data) {
                    str_info += "<tr>";
                    str_info += "<td>";
                    if (general_star == "2") {
                        str_info += "<a class='btn btn-xs green'>" + data[s]["name"] + "</a>";
                    }
                    else if (general_star == "3") {
                        str_info += "<a class='btn btn-xs blue'>" + data[s]["name"] + "</a>";
                    }
                    else if (general_star == "4") {
                        str_info += "<a class='btn btn-xs purple'>" + data[s]["name"] + "</a>";
                    }
                    else if (general_star == "5"){
                        str_info += "<a class='btn btn-xs yellow'>" + data[s]["name"] + "</a>";
                    }
                    else{
                        str_info += "<a class='btn btn-xs red'>" + data[s]["name"] + "</a>";
                    }
                    str_info += "</td>";
                    str_info += "<td>" + data[s]["num"] + "</td>";
                    str_info += "<td>" + (data[s]["users"] / data[s]["total"] * 100).toFixed(2) + "%</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#general_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
};

$("#a_general").on("click", function(e){
    $single_server_select_div.show();
    general_query();
});

$("#general_star").on("change", function(e){
    e.preventDefault();
    general_query();
});
$('#a_liveness,#a_gamedata').click(function () {
    $single_server_select_div.show();
});

$("#liveness_query").on("click", function(e){
    e.preventDefault();
    var server_id = $("#select_gameserver").val();
    var text_liveness_date = $("#text_liveness_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryliveness',
            data: {server_id: server_id, q_date: text_liveness_date},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                var total = 0;
                for (var k=0;  k<data.length; k++){
                    total += data[k]["c_count"];
                }
                if(data.length != 0){
                    for (var i=0; i <data.length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["point"] + "积分</td>";
                        str_info += "<td>" + data[i]["c_count"] + "</td>";
                        str_info += "<td>" + (data[i]["c_count"] / total * 100).toFixed(2) + "%</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#liveness_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
                error_func();
            }
    })
});