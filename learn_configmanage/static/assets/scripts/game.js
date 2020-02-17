/**
 * Created by wangrui on 14-10-17.
 */


get_left_game_server();
setLeftStyle();

var server_id = $("input[name='server_id']").val();
var server_name = $("input[name='server_name']").val();
var game_tag = null;
var url = "";
var exturl = "";

var BROAD_TYPE = {
    "5S": "5秒",
    "1M": "1分钟",
    "5M": "5分钟",
    "10M": "10分钟",
    "1H": "1小时"
};
handleDatePickers2();
handleTimePickers();
$("#lua_start_date").val(getNowFormatDate(1));
$("#lua_end_date").val(getNowFormatDate(0));
$("#system_date").val(getNowFormatDate(0));

var $operate_game_modal = $("#operate_game_modal");

var ext_time = {
      "cup": {
          "name": "杯赛",
          "week": [0, 1, 2, 3, 4, 5, 6],
          "data": [
              ["08:40:00", "08:45:00"],
              ["09:00:00", "09:02:00"],
              ["09:20:00", "09:22:00"],
              ["09:40:00", "09:42:00"],
              ["10:00:00", "10:02:00"],
              ["10:20:00", "10:21:00"],
              ["10:40:00", "10:41:00"],
              ["11:00:00", "11:01:00"],
              ["11:20:00", "11:21:00"],
              ["11:40:00", "11:41:00"],
              ["12:00:00", "12:01:00"],
              ["14:00:00", "14:01:00"],
              ["16:00:00", "16:01:00"],
              ["18:55:00", "19:59:00"]
          ]
      }
};


var game_time = {
      "boss": {
          "name": "群仙屠龙",
          "week": [0, 1, 2, 3, 4, 5, 6],
          "data": [
              ["12:00:00", "12:30:00"],
              ["21:00:00", "21:30:00"]
          ]
      },
    "wudaohui":{
          "name": "武道会",
          "week": [1, 3, 5],
          "data": [
              ["20:30:00", "21:00:00"]
          ]
      }
};



function get_time_format(){
    var day = new Date();
    var hours = day.getHours();
    var minutes = day.getMinutes();
    var seconds = day.getSeconds();
    var CurrentDate = "";
    if (hours >= 10){
        CurrentDate += hours;
    }
    else{
        CurrentDate += "0" + hours;
    }
    CurrentDate += ":";
    if (minutes >= 10){
        CurrentDate += minutes;
    }
    else{
        CurrentDate += "0" + minutes;
    }
    CurrentDate += ":";
    if (seconds >= 10){
        CurrentDate += seconds;
    }
    else{
        CurrentDate += "0" + seconds;
    }

    return CurrentDate;
}


function reboot_or_close_notice(array_list, array_list2, tag2, ss_tag){
    var current_time = get_time_format();
    var week = new Date().getDay();
    var str_html = "";
    var str_html2 = "";
    for (var i in array_list){
        if (array_list[i]["week"].indexOf(week) > -1){
            var name = array_list[i]["name"];
            var tag = false;
            for(var s=0; s<array_list[i]["data"].length; s++){
                if (array_list[i]["data"][s][0] < current_time && current_time < array_list[i]["data"][s][1]){
                    tag = true;
                    break;
                }
            }
            if (tag){
                str_html2 += name;
            }
        }
    }
    for (var al in array_list2){
        if (array_list2[al]["week"].indexOf(week) > -1){
            var name2 = array_list2[al]["name"];
            var tag3 = false;
            for(var s2=0; s2<array_list2[al]["data"].length; s2++){
                if (array_list2[al]["data"][s2][0] < current_time && current_time < array_list2[al]["data"][s2][1]){
                    tag3 = true;
                    break;
                }
            }
            if (tag3){
                str_html2 += name2;
            }
        }
    }
    if (str_html2.length != 0){
        str_html += "现在是:[" + str_html2 + "]时间<br/>";
    }
    str_html += "是否";
    if (tag2 == true) {
        str_html += "关闭"
    }
    else {
        str_html += "重启"
    }
    str_html += "[" + server_id + "区:" + server_name + "]";
    var s_name = get_service_name(ss_tag);
    str_html += s_name + ";";
    return str_html;
}

function get_service_name(tag3){
    var str_html = "";
    if (tag3 == 1){
        str_html += "路由";
    }
    else if (tag3 == 2){
        str_html += "游戏";
    }
    else if (tag3 == 3){
        str_html += "扩展";
    }
    else{
        str_html += "路由、游戏、扩展";   
    }
    str_html += "服务";
    return str_html;
}

function start_game(method, tag3){
    var service_name = get_service_name(tag3);
    create_del_modal($operate_game_modal, "是否启动" + service_name +  "服务.", "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_game_service(1," + method + ")");
    $operate_game_modal.modal("show");
}


function close_game(method, tag3){
    var str_html = reboot_or_close_notice(ext_time, game_time, true, tag3);
    create_del_modal($operate_game_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_game_service(2," + method + ")");
    $operate_game_modal.modal("show");
}


function reboot(method){
    set_game_service(3, method);
}


$("#gate_reboot_game").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(game_time, {}, false, 1);
    create_del_modal($operate_game_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(2)");
    $operate_game_modal.modal("show");
});

$("#gate_start_game").on("click", function (e) {
    e.preventDefault();
    start_game(2, 1);
});

$("#close_gate").on("click", function (e) {
    e.preventDefault();
    close_game(2, 1);
});


//网关模式game控制
$("#gate_game_reboot_game").on("click", function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(game_time, {}, false, 2);
    create_del_modal($operate_game_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(3)");
    $operate_game_modal.modal("show");
});

$("#gate_game_start_game").on("click", function (e) {
    e.preventDefault();
    start_game(3, 2);
});

$("#close_gate_game").on("click", function (e) {
    e.preventDefault();
    close_game(3, 2);
});

//网关模式ext控制
$("#reboot_ext2").on("click", function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(ext_time, {}, false, 3);
    create_del_modal($operate_game_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(4)");
    $operate_game_modal.modal("show");
});

$("#start_ext2").on("click", function (e) {
    e.preventDefault();
    start_game(4, 3);
});

$("#close_ext2").on("click", function (e) {
    e.preventDefault();
    close_game(4, 3);
});

//网关模式总控制
$("#reboot_all").on("click", function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(game_time, ext_time, false, 4);
    create_del_modal($operate_game_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(6)");
    $operate_game_modal.modal("show");
});

$("#start_all").on("click", function (e) {
    e.preventDefault();
    start_game(6, 4);
});

$("#close_all").on("click", function (e) {
    e.preventDefault();
    close_game(6, 4);
});


var Game = function () {
    var broadcastOneValidation = function () {
        var form1 = $("#broad_one_form");
        var rules = {
            one_broad_name: {
                required: true
            },
            one_broad_content: {
                required: true
            }
        };
        var messages = {
            one_broad_name: {
                required: "请输入角色"
            },
            one_broad_content: {
                required: "请输入广播内容"
            }
        };
        var submitFunc = function () {
            var one_broad_name = $("#one_broad_name").val();
            var one_broad_content = $("#one_broad_content").val();
            var success = function(data){
                if (data["status"] == "success") {
                    Common.alert_message($("#error_modal"), 1, "发送成功.");
                }
                else {
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                $("#one_broad_name").val("");
                $("#one_broad_content").val("");
            };
            var data = {
                server_id: server_id,
                broadcast_name: one_broad_name,
                broadcast_content: one_broad_content
            };
            my_ajax(true, "/sendonebroad", 'get', data, true, success);
        };
        commonValidation(form1, rules, messages, submitFunc);
    };
    broadcastOneValidation();

    var PushContentValidation = function () {
        var form1 = $("#push_form");
        var rules = {
            push_content: {
                required: true
            }
        };
        var messages = {
            push_content: {
                required: "请输入推送内容"
            }
        };
        var submitFunc = function () {
            var push_content = $("#push_content").val();
            var success = function(data){
                if (data["status"] === "success") {
                    Common.alert_message($("#error_modal"), 1, "发送成功.");
                }
                else {
                    Common.alert_message($("#error_modal"), 0, '发送失败');
                }
                $("#push_content").val("");
            };
            var data = {
                server_id: server_id,
                push_content: push_content
            };
            my_ajax(true, "/push/game/content", 'get', data, true, success);
        };
        commonValidation(form1, rules, messages, submitFunc);
    };
    PushContentValidation();




    var mailValidation = function () {
        var rules = {
            mail_content: {
                required: true
            }
        };

        var messages = {
            mail_content: {
                required: "请输入邮件内容"
            }
        };

        var submitHandler = function (form) {
            var sys_mail_id = $("#sys_mail_id").val();
            var mail_all = 0;
            if ($("#mail_all").is(":checked")) {
                mail_all = 1;
            }
            var reply_user = $("#reply_user").val();
            var mail_title = $("#mail_title").val();
            var mail_content = $("#mail_content").val();
            var mail_attachment = $("#mail_attachment").val();
            var success = function(data){
                if (data["status"] == "fail") {
                    Common.alert_message($("#error_modal"), 0, data["errmsg"]);
                }
                else {
                    Common.alert_message($("#error_modal"), 1, "邮件发送成功");
                }
                $("#mail_modal").modal("hide");
                $("#a_mail").click();
            };
            var data = {
                server_id: server_id, mail_all: mail_all, sys_mail_id: sys_mail_id,
                reply_user: reply_user, mail_title: mail_title, mail_content: mail_content, mail_attachment: mail_attachment
            };
            my_ajax(true, '/mail/sendmail', 'get', data, true, success);
        };
        commonValidation($("#mail_form"), rules, messages, submitHandler);
    };

    var commandValidation = function () {
        var rules = {
            command_name: {
                required: true
            },
            command_value: {
                required: true
            }
        };

        var messages = {
            command_name: {
                required: "请输入命令名称"
            },
            command_value: {
                required: "请输入命令行"
            }
        };

        var submitHandler = function (form) {
            var command_name = $("#command_name").val();
            var command_value = $("#command_value").val();
            var command_param = $("#command_param").val();
            var success = function (data) {
                if (data["status"] == false) {
                    Common.alert_message($("#error_modal"), 0, "操作失败.");
                }
                $("#command_modal").modal("hide");
                $("#a_command").click();
            };
            var data = {
                command_name: command_name,
                command_value: command_value,
                command_param: command_param,
                server_id: server_id
            };
            my_ajax(true, '/addcommand', 'get', data, true, success);
        };
        commonValidation($("#command_form"), rules, messages, submitHandler);
    };


    var getServerStatus = function () {
        var gate_status = $("#gate_status");
        var gate_game_status = $("#gate_game_status");
        var ext_game_status2 = $("#ext_game_status2");

        var total_status = $("#total_status");
        var success = function(data){
            var html = "";
            var html2 = "";
            var html3 = "";
            var run_html = "<span class='badge badge-success'>运行</span>";
            var close_html = "<span class='badge badge-danger'>关闭</span>";
            var server_mode = data["mode"];
            if (server_mode == 5){
                $("#server_mode").html("标准模式");
                $("#div_gate_status").hide();
                $("#div_gates").hide();
            }
            else{
                $("#server_mode").html("性能模式");
                if (data["gate"] == "on") {
                    html3 += run_html;
                }
                else {
                    html3 += close_html;
                }
                gate_status.html(html3);
                $("#div_gate_status").show();
                $("#div_gates").show();
            }
            
            if (data["game"] == "on") {
                html += run_html;
            }
            else {
                html += close_html;
            }
            if (data["ext"] == "on") {
                html2 += run_html;
            }
            else {
                html2 += close_html;
            }

            gate_game_status.html(html);
            ext_game_status2.html(html2);

            if (data["game"] == "on" && data["ext"] == "on" && data["gate"] == "on") {
                total_status.html(run_html);
            }
            else {
                total_status.html(close_html);
            }

        };
        var data = {
            server_id: server_id
        };
        my_ajax(true, "/server/getgamestatus", "get", data, true, success);
    };

    var getlog = function () {
        var success = function (data) {
            url = data["url"];
            exturl = data["exturl"];
        };
        var data = {
            server_id: server_id
        };
        my_ajax(true, "/getlog", 'get', data, true, success);
    };

    mailValidation();
    commandValidation();
    getServerStatus();
    getlog();
    return{
        get_server_status: function () {
            getServerStatus();
        }
    }
}();


$("#gates_server_log").on("click", function(e){
    e.preventDefault();
    var log_param = $("#gates_log_param").val();
    window.open(url + "?server_id=" + server_id + "&tag=1" + "&param=" + log_param);
});


$("#server_log").on("click", function(e){
    e.preventDefault();
    var log_param = $("#log_param").val();
    window.open(url + "?server_id=" + server_id + "&tag=2" + "&param=" + log_param);
});

$("#ext_log").on("click", function(e){
    e.preventDefault();
    var log_param = $("#ext_log_param").val();
    window.open(url + "?server_id=" + server_id + "&tag=3" + "&param=" + log_param);
});



function set_game_service(tag, method) {
    var game_list = [];
    game_list.push(server_id);
    var req_data = {
        server_list: JSON.stringify(game_list), tag: tag, method: method
    };
    $.ajax({
            type: 'get',
            url: '/server/setallgameservice',
            data: req_data,
            dataType: 'JSON',
            cache: false,
            headers: {"cache-control": "no-cache"},
            async: true,
            success: function (data) {
                setTimeout("Game.get_server_status()", 5000);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
}

$("#a_monitor_log").on("click", function(e){
    e.preventDefault();
    var success = function(data){
        var html = "";
        var b_class = "";
        var str_s = "";

        var html2 = "";
        var b_class2 = "";
        var str_s2 = "";
        if (data["status2"]["game"] == "on") {
            html += "<span class='badge badge-success'>开启</span>";
            b_class = "red-intense";
            str_s = "关闭";
        }
        else {
            html += "<span class='badge badge-danger'>关闭</span>";
            b_class = "green-haze";
            str_s = "开启";
        }
        if (data["status2"]["ext"] == "on") {
            html2 += "<span class='badge badge-success'>开启</span>";
            b_class2 = "red-intense";
            str_s2 = "关闭";
        }
        else {
            html2 += "<span class='badge badge-danger'>关闭</span>";
            b_class2 = "green-haze";
            str_s2 = "开启";
        }

        $("#monitor_game_status").html(html);
        $("#set_game_log").removeClass();
        $("#set_game_log").addClass("btn " + b_class);
        $("#set_game_log").html(str_s);

        $("#monitor_ext_status").html(html2);
        $("#set_ext_log").removeClass();
        $("#set_ext_log").addClass("btn " + b_class2);
        $("#set_ext_log").html(str_s2);
    };
    var data = {
        server_id: server_id
    };
    my_ajax(true, '/gamelog/getstatus', 'get', data, true, success);
});


var setmonitorlog = function(game_tag, tag){
    var success = function (data) {
        $("#a_monitor_log").click();
    };
    var data = {
        server_id: server_id,
        game_tag: game_tag,
        tag: tag
    };
    my_ajax(true, "/gamelog/setmonitorlog", 'get', data, true, success);
};


$("#set_game_log").on("click", function (e) {
    e.preventDefault();
    if ($(this).html() == "开启") {
        setmonitorlog("game", 1);
    }
    else {
        setmonitorlog("game", 2);
    }
});

$("#set_ext_log").on("click", function (e) {
    e.preventDefault();
    if ($(this).html() == "开启") {
        setmonitorlog("ext", 1);
    }
    else {
        setmonitorlog("ext", 2);
    }
});

var source_flush = function (tag) {
    var success = function(data){
        if (data["status"] == "success") {
            Common.alert_message($("#error_modal"), 1, data["module"]);
        }
        else {
            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
        }
    };
    var data = {server_id: server_id, tag: tag};
    my_ajax(true, '/flushsource', 'get', data, true, success);
};

$("#source_flush").on("click", function (e) {
    e.preventDefault();
    source_flush(1);
});

$("#source_flush2").on("click", function (e) {
    e.preventDefault();
    source_flush(1);
});

$("#back_flush").on("click", function (e) {
    e.preventDefault();
    source_flush(2);
});

$("#back_flush2").on("click", function (e) {
    e.preventDefault();
    source_flush(2);
});



$("#broad_add").on("click", function (e) {
    e.preventDefault();
    var htmlstr = [];
    var select_folder = $("#broad_type");
    for (var b in BROAD_TYPE) {
        htmlstr.push("<option value='" + b + "'>" + BROAD_TYPE[b] + "</option>");
    }
    select_folder.html(htmlstr.join(""));
});

$("#a_notice").click(function (e) {
    e.preventDefault();
    $("#notice_person").val("");
    $("#notice_value").val("");
});


var get_system_mail = function (){
    var sAjaxSource = "/mail/getsystemmail";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "ask",
            'sClass': 'center',
            "sTitle": "邮件内容"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "time1",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">回复 <i class=\"fa fa-edit\"></i></button>"
        }
    ];
    var data = {
        server_id: server_id
    };
    dataTablePage($("#system_mail_table"), aoColumns, sAjaxSource, data, false, null);
};



$("#a_mail").on("click", function (e) {
    e.preventDefault();
    get_system_mail();
});
//回复系统邮件
var mod = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#system_mail_table").dataTable().fnGetData(nRoW);
    $("#sys_mail_id").val(data["id"]);
    $("#reply_user").val(data["rid"]);
    $("#reply_user").attr("disabled", true);
    $("#mail_all").prop("checked", false);
    $("#mail_all").parent("span").removeClass("checked");
    $("#mail_title").val("");
    $("#mail_content").val("");
    $("#mail_attachment").val("");
    $("#mail_modal").modal("show");
};


$("#write_mail").on("click", function (e) {
    e.preventDefault();
    $("#sys_mail_id").val("");
    $("#reply_user").val("");
    $("#reply_user").attr("disabled", false);
    $("#mail_all").prop("checked", false);
    $("#mail_all").parent("span").removeClass("checked");
    $("#mail_title").val("");
    $("#mail_content").val("");
    $("#mail_attachment").val("");
    $("#mail_modal").modal("show");
});



$("#a_cup").on("click", function (e) {
    e.preventDefault();
    var cup_status = $("#cup_status");
    var success = function (data) {
        var html = "";
        if (data["status"] == 'success') {
            html += "<span class='badge badge-success'>" + data["round"] + "</span>";
        }
        else {
            html += "<span class='badge badge-danger'>0</span>";
        }
        cup_status.html(html);
    };
    var data = {
        server_id: server_id
    };

    my_ajax(true, '/getcupstatus', 'get', data, true, success);
});

$("#confirm_round").on("click", function (e) {
    e.preventDefault();
    var cup_num = $("input[name='cup_num']").val();
    var success = function(data){
        if (data["status"] == 'success') {
            Common.alert_message($("#error_modal"), 1, "处理成功")
        }
        else {
            Common.alert_message($("#error_modal"), 0, data["errmsg"])
        }
    };
    var data = {
        server_id: server_id, cup_num: cup_num
    };

    my_ajax(true, '/cupround', 'get', data, true, success);
});

$("#confirm_test").on("click", function (e) {
    e.preventDefault();
    var cup_start = $("input[name='cup_start']").val();
    var cup_end = $("input[name='cup_end']").val();
    var suc = function(data){
        if (data["status"] == 'success') {
            Common.alert_message($("#error_modal"), 1, "处理成功")
        }
        else {
            Common.alert_message($("#error_modal"), 0, data["errmsg"])
        }
    };
    var data = {
        server_id: server_id, cup_start: cup_start, cup_end: cup_end
    };
    my_ajax(true, '/cuptest', 'get', data, true, suc);
});

$("#a_boss").on("click", function (e) {
    e.preventDefault();
    var suc = function (data) {
        var html = "";
        var b_class = "";
        var str_s = "";

        var html2 = "";
        var b_class2 = "";
        var str_s2 = "";
        if (data[1]["status"] == "success" && data[1]["switch"] == "true") {
            html += "<span class='badge badge-success'>开启</span>";
            b_class = "red-intense";
            str_s = "关闭";
        }
        else {
            html += "<span class='badge badge-danger'>关闭</span>";
            b_class = "green-haze";
            str_s = "开启";
        }
        if (data[2]["status"] == "success" && data[2]["switch"] == "true") {
            html2 += "<span class='badge badge-success'>开启</span>";
            b_class2 = "red-intense";
            str_s2 = "关闭";
        }
        else {
            html2 += "<span class='badge badge-danger'>关闭</span>";
            b_class2 = "green-haze";
            str_s2 = "开启";
        }

        $("#boss_status").html(html);
        $("#set_boss").removeClass();
        $("#set_boss").addClass("btn " + b_class);
        $("#set_boss").html(str_s);

        $("#boss_status2").html(html2);
        $("#set_boss2").removeClass();
        $("#set_boss2").addClass("btn " + b_class2);
        $("#set_boss2").html(str_s2);
    };
    var data = {
        server_id: server_id
    };
    my_ajax(true, '/getbossstatus', 'get', data, true, suc);
});

$("#set_boss").on("click", function (e) {
    e.preventDefault();
    if ($(this).html() == "开启") {
        switch_boss(1, 1);
    }
    else {
        switch_boss(0, 1);
    }

    setTimeout("$('#a_boss').click()", 2000);
});

$("#set_boss2").on("click", function (e) {
    e.preventDefault();
    if ($(this).html() == "开启") {
        switch_boss(1, 2);
    }
    else {
        switch_boss(0, 2);
    }

    setTimeout("$('#a_boss').click()", 2000);
});

var switch_boss = function (tag, boss) {
    var data = {
        server_id: server_id,
        tag: tag,
        boss: boss
    };
    var suc = function (data) {

    };
    my_ajax(true, '/switchboss', 'get', data, true, suc);
};

var query_lua_error = function () {
    var sAjaxSource = "/queryluaerror";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色"
        },
        {
            "mDataProp": "time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "frm",
            'sClass': 'center',
            "sTitle": "类型"
        },
        {
            'sClass': 'center',
            "sTitle": "错误信息",
            "sDefaultContent": "<button onclick=\"display_lua(this)\" class=\"btn btn-xs blue\" data-toggle=\"modal\">详细</button>"
        },

        {
            "mDataProp": "tag",
            'sClass': 'center',
            "sTitle": "操作"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html2 = "";
        if (aData.tag == 0) {
            str_html2 += "<button onclick=\"process_lua(" + aData.id + ")\" class=\"btn btn-xs red\">未处理</button>";
        }
        else {
            str_html2 += "<button class=\"btn default btn-xs green\">处理</button>";
        }

        var str_html = "";
        if (aData.frm == "net") {
            str_html = "网络"
        }
        else {
            str_html = "界面"
        }
        $('td:eq(2)', nRow).html(str_html);
        $('td:eq(4)', nRow).html(str_html2);
        return nRow;
    };

    var data = {
        server_id: server_id,
        lua_roleid: $("#lua_roleid").val(),
        start_date: $("#lua_start_date").val(),
        end_date: $("#lua_end_date").val()
    };
    dataTablePage($("#lua_client_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
};


$("#lua_search").on("click", function (e) {
    e.preventDefault();
    query_lua_error();
});

function display_lua(btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#lua_client_table").dataTable().fnGetData(nRoW);
    Common.alert_message($("#error_modal"), 0, data["msg"]);
}

function process_lua(lua_id) {
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    var success = function (data) {
        if (data["status"] == true) {
            Common.alert_message($("#error_modal"), 1, "处理成功.");
        }
        else {
            Common.alert_message($("#error_modal"), 0, "处理失败.");
        }
        $("#lua_search").click();
    };
    var data = {
        server_id: server_id,
        lua_id: lua_id
    };

    my_ajax(true, '/processlua', 'get', data, true, success);
}



$("#command").on("click", function (e) {
    e.preventDefault();
    $("#command_name").val("");
    $("#command_value").val("");
    $("#command_modal").modal("show");
});


function deleteruncommand(command_id){
    var success = function(data){
        if (data["status"] == "success"){
            $("#a_command").click();
        }
        else{
            Common.alert_message($("#error_modal"), 0, "删除失败");
        }
    };
    var data = {
        command_id: command_id
    };
    my_ajax(true, "/deletecommand", 'get', data, false, success);
}


$("#a_command").on("click", function (e) {
    e.preventDefault();
    var success = function(data){
        var str_info = "";
        for (var i = 0; i < data.length; i++) {
            str_info += "<tr>";
            str_info += "<td>" + data[i]["name"] + "</td>";
            str_info += "<td>" + data[i]["command"] + "</div></td>";
            str_info += "<td ondblclick='tdClick(" + data[i]["id"] + ");'><div id='div_param_" + data[i]["id"] + "'>" + data[i]["param"] + "</div></td>";
            str_info += "<td><button  onclick=\"runcommand('" + data[i]["id"] + "')\" class=\"btn btn-xs blue\">执行</button>" +
                "<button  onclick=\"deleteruncommand('" + data[i]["id"] + "')\" class=\"btn btn-xs red\">删除</button>" + "</td>";
            str_info += "</tr>";
        }
        $("#command_list").html(str_info);
    };
    var data = {server_id: server_id};

    my_ajax(true, '/getcommand', 'get', data, true, success);
});

function tdClick(cid) {
    var s = $("#div_param_" + cid);
    var tdText = s.text();
    s.empty();

    var input = $("<input type='text'>");
    input.val(tdText);
    s.append(input);
    input.blur(function () {
        var inputText = input.val();
        s.html(inputText);
        s.css("color", "red");
    });
}

function runcommand(cid) {
    var param = $("#div_param_" + cid).text();
    var success = function (data) {
        Common.alert_message($("#error_modal"), 1, JSON.stringify(data));
    };
    var data = {
        cid: cid,
        param: param,
        tag: 1
    };
    my_ajax(true, '/runcommand', 'get', data, true, success);
}

function runcommand2(param){
    var success = function (data) {
        Common.alert_message($("#error_modal"), 1, JSON.stringify(data));
    };
    var data = {
        server_id: server_id,
        param: param,
        param2: ""
    };
    my_ajax(true, '/runcommand2', 'get', data, true, success);
}

function runcommand3(param, name, value){
    var response = null;
    var success = function (data) {
        response = data;
    };
    var data = {
        server_id: server_id,
                param: param,
                name: name,
                value: value
    };
    my_ajax(true, '/getsysparam', 'get', data, false, success);
    return response;
}

create_del_modal($("#forcedb_modal"), "是否重写数据?", "confirm_forcedb");
create_del_modal($("#closegame_modal"), "是否关闭游戏?", "confirm_closegame");
create_del_modal($("#dayclear_modal"), "是否执行每日清零?", "confirm_dayclear");


$("#btn_forcedb").on("click", function(e){
    e.preventDefault();
    $("#forcedb_modal").modal("show");
    $("#confirm_forcedb").attr("onclick", "runcommand2('gm/forcedb')");
});


$("#btn_closegame").on("click", function(e){
    e.preventDefault();
    $("#closegame_modal").modal("show");
    $("#confirm_closegame").attr("onclick", "runcommand2('gm/gameexit')");
});

$("#btn_dayclear").on("click", function(e){
    e.preventDefault();
    $("#dayclear_modal").modal("show");
    $("#confirm_dayclear").attr("onclick", "runcommand2('gm/dayclear')");
});


$("#a_servertime").on("click", function(e){
    e.preventDefault();
    var name = "servertime";
    var data = runcommand3('gm/getsysparam', name, "");
    if (data["status"] == "success"){
        $("#servertime").html(data["value"]);
    }
});


$("#btn_setservertime").on("click", function(e){
    e.preventDefault();
    var name = "servertime";
    var system_date = $("#system_date").val();
    var system_time = $("#system_time").val();
    var date_list = system_date.split("-");
    var value = date_list[0] + date_list[1] + date_list[2];
    var time_list = system_time.split(":");
    value += time_list[0] + time_list[1] + time_list[2];
    var data = runcommand3('gm/setsysparam', name, value);
    if (data["status"] == "success"){
        Common.alert_message($("#error_modal"), 1, "设置成功.");
        $("#a_servertime").click();
    }
    else{
        Common.alert_message($("#error_modal"), 0, data["errmsg"]);
    }
});


$("#a_maxonline").on("click", function(e){
    e.preventDefault();
    var name = "onlinemax";
    var data = runcommand3('gm/getsysparam', name, "");
    if (data["status"] == "success"){
        $("#max_online_num").val(data["value"]);
    }
});

var maxOnlineValidation = function () {
    var rules = {
        max_online_num: {
            required: true,
            digits: true
        }
    };

    var messages = {
        max_online_num: {
            required: "请输入最大在线人数",
            digits: "请输入数字"
        }
    };

    var submitHandler = function (form) {
        var max_online_num = $("#max_online_num").val();
        var name = "onlinemax";
        var data = runcommand3('gm/setsysparam', name, max_online_num);
        if (data["status"] == "success"){
            Common.alert_message($("#error_modal"), 1, "设置成功.");
            $("#a_maxonline").click();
        }
        else{
            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
        }
    };
    commonValidation($("#max_online_form"), rules, messages, submitHandler);
};
maxOnlineValidation();