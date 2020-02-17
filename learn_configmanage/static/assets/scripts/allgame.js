/**
 * Created by wangrui on 15/5/11.
 */
get_left_game_server();

var $gameserver_list = $("#gameserver_list");
var $operate_game_modal = $("#operate_game_modal");
var $add_command = $('#add_command');
var $command_modal = $('#command_modal');
var $command_list_tab = $('#command_list_tab');
var $confirm_modal = $('#confirm_modal');
var $confirm_modal_title = $('#confirm_modal_title');
var $confirm_modal_content = $('#confirm_modal_content');
var $btn_confirm_modal = $('#btn_confirm_modal');
var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $command_record_table = $('#command_record_table');
var $command_list_head = $('#command_list_head');

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
              ["14:00:00", "14:02:00"],
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
    var str_info = [];
    $("input[name='check_game']").each(function(e){
        if($(this).is(":checked")){
            str_info.push($(this).next().text());
        }
    });
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

    var s_name = get_service_name(ss_tag);
    str_html += s_name + ";区服如下:<br/>";
    for(var s=0; s<str_info.length; s++){
        str_html += str_info[s] + "<br/>";
    }
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


var getGlobalStatus = function(){
    var success = function (data) {
        var html = "<tr>";
        if (data["port"] == "on") {
            html +=  "<td> <span class='badge badge-success'>运行</td>";;
        }
        else {
            html += "<td><span class='font-red-intense'>关闭</td>";
        }
        html += "</tr>";
        $("#globalserver_list").html(html);
    };
    my_ajax(true, "/global/status", "get", {}, true, success);
};

getGlobalStatus();

var get_acc_status = function () {
    var success = function (data) {
        var html = "<tr>";
        if (data["acc_port"] == "on") {
            html += "<td> <span class='badge badge-success'>运行</td>";
        }
        else {
            html += "<td><span class='font-red-intense'>关闭</td>";
        }
        if (data["pay_port"] == "on") {
            html += "<td> <span class='badge badge-success'>运行</td>";
        }
        else {
            html += "<td><span class='font-red-intense'>关闭</td>";
        }
        html += "<td></td>";
        get_game_error_total(0, 0, 2, 2);
        $("#accserver_list").html(html);
    };
    var req_data = {
        method: 2
    };
    my_ajax(true, "/account/status", 'get', req_data, true, success);
};
get_acc_status();

function get_game_error(server){
    var sAjaxSource = "/getgameerror";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "platform",
            'sClass': 'center',
            "sTitle": "平台"
        },
        {
            "mDataProp": "server",
            'sClass': 'center',
            "sTitle": "游戏服"
        },
        {
            "mDataProp": "tag",
            'sClass': 'center',
            "sTitle": "错误类型"
        },
        {
            "mDataProp": "message",
            'sClass': 'center',
            "sTitle": "错误信息"
        },
        {
            "mDataProp": "otime",
            'sClass': 'center',
            "sTitle": "时间"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html = "";
        if (aData.tag == "game"){
            str_html = "游戏";
        }
        else if (aData.tag == "ext"){
            str_html = "扩展";
        }
        else if (aData.tag == "acc"){
            str_html = "账号";
        }
        $('td:eq(2)', nRow).html(str_html);
        return nRow;
    };
    var data = {
        server_id: server
    };
    dataTablePage($("#game_error_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
    $("#gameerror_modal").modal("show");
}


var get_game_status = function(server_id, h, mode){
    var data = {
        server_id: server_id
    };
    var success = function(data){
        var run_html = "<span class='badge badge-success'>运行</span>";
        var stop_html = "<span class='badge badge-danger'>关闭</span>";
        var set_div = $gameserver_list.children('tr').eq(h).children('td');
        if (server_id != 0){
            if (mode == 6){
                if (data["gate"] == "on") {
                    set_div.eq(1).html(run_html);
                }
                else {
                    set_div.eq(1).html(stop_html);
                }
            }

            if (data["game"] == "on") {
                set_div.eq(2).html(run_html);
            }
            else {
                set_div.eq(2).html(stop_html);
            }
            if (data["ext"] == "on") {
                set_div.eq(3).html(run_html);
            }
            else {
                set_div.eq(3).html(stop_html);
            }
        }
    };
    my_ajax(true, "/server/getgamestatus", "get", data, true, success);
};

var get_one_line = function(server_id, m){
    var data = {
        server_id: server_id
    };
    var success = function(data){
        var set_div = $gameserver_list.children('tr').eq(m).children('td');
        if (data["online"]["status"] == "success") {
            set_div.eq(6).html("<span class='badge badge-info'>" + data["online"]["total"] + "</span>");
            set_div.eq(7).html("<span class='badge badge-success'>" + data["online"]["online"] + "</span>");
        }
        set_div.eq(9).html(data["servertime"]["value"]);
    };
    my_ajax(true, "/server/getoneonline", "get", data, true, success);
};


var get_game_error_total = function (server_id, m, tag, s_tag) {
    var str_html = "";
    var success = function(data){
        var set_div = $gameserver_list.children('tr').eq(m).children('td');
        if (tag == 1){
            set_div = $gameserver_list.children('tr').eq(m).children('td');
        }
        else{
            set_div = $("#accserver_list").children('tr').eq(m).children('td');
        }
        if (data["error"] == 0) {
            str_html += "<span class='badge badge-success'>0</span>"
        }
        else {
            str_html += "<a onclick='get_game_error(" + server_id + ")'>" + "<span class='badge badge-danger'>" + data["error"] + "</span></a>";
        }


        var success2 = function(data){
            if (data["status1"] == 0) {
                str_html += "<span class='badge badge-danger'>异常</span>";
            }
            else{
                str_html += "<span class='badge badge-success'>正常</span>";
            }
            if (data["status2"]["game"] == "off" && data["status2"]["ext"] == "off") {
                str_html += "<span class='badge badge-danger'>异常</span>";
            }
            else{
                str_html += "<span class='badge badge-success'>正常</span>";
            }
            set_div.eq(s_tag).html(str_html);
        };
        if (server_id != 0){
            var req_data2 = {
                server_id: server_id
            };
            my_ajax(false, "/gamelog/getstatus", "get", req_data2, true, success2);
        }
        else{
            set_div.eq(s_tag).html(str_html);
        }

    };
    var req_data = {
        server_id: server_id
    };
    my_ajax(true, "/server/geterror", "get", req_data, true, success);
};


var get_client_error = function (server_id, m, eq_num) {
    var success = function(data){
        var set_div = $gameserver_list.children('tr').eq(m).children('td');
        var str_html = "";
        if (data["error"] == 0) {
            str_html += "<span class='badge badge-success'>0</span>"
        }
        else {
            str_html +=  "<span class='badge badge-danger'>" + data["error"] + "</span>";
        }
        set_div.eq(eq_num).html(str_html);
    };
    var req_data = {
        server_id: server_id
    };
    my_ajax(true, "/sensor/getcount", "get", req_data, true, success);
};



var getAllGame = function (api, data) {
    var success = function(data){
        var str_info = "";
        if (data.length != 0) {
            var k = 0;
            for (var i in data) {
                var mode = data[i]["mode"];
                str_info += "<tr>";
                str_info += "<td>" + "<div class='checkbox-list'>";
                str_info += "<label> <input type=\"checkbox\" name=\"check_game\" value=\"" +
                    data[i]["gameid"] + "\"><span>" + data[i]["gameid"] + "区:" + data[i]["name"] + "</span></label></div></td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
                str_info += "<td>"+data[i]['section_name']+"</td>";
                str_info += "<td></td>";
                if (mode == 5){
                    str_info += "<td><span class='badge badge-success'>标准模式</span></td>";
                }
                else{
                    str_info += "<td><span class='badge badge-info'>性能模式</span></td>";
                }
                str_info += "<td><a class='badge badge-success' onclick='flush_online(" + data[i]["gameid"] + "," + k + "," + mode + ")'>" + "刷新"  + "</a>";
                str_info += "&nbsp;<a class='badge badge-info ' href='/game_manage?server_id=" + data[i]["gameid"] + "'>游戏管理" + "</a>";
                str_info += "&nbsp; <a class='badge badge-important' href='/data_manage?server_id=" + data[i]["gameid"] + "'>数据管理" + "</td>";
                str_info += "</tr>";
                k += 1;
            }

            var h = 0;
            for (var s in data){
                get_game_status(data[s]["gameid"], h, data[s]["mode"]);
                get_client_error(data[s]["gameid"], h, 4);
                get_game_error_total(data[s]["gameid"], h, 1, 5);
                get_one_line(data[s]["gameid"], h);
                h += 1;
            }
        }
        else {
            str_info += "<tr>";
            str_info += '<td colspan="7" class="text-center"><span class="label label-danger">无数据</span></td>';
            str_info += '</tr>';
        }
        $gameserver_list.html(str_info);

    };

    my_ajax(true, api, "get", data, true, success);


};

$add_command.click(function () {
    $command_modal.modal("show");
});
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
            $command_modal.modal("hide");
            $command_list_head.click();
        };
        var data = {
            command_name: command_name,
            command_value: command_value,
            command_param: command_param,
            server_id: '-1'
        };
        my_ajax(true, '/addcommand', 'get', data, true, success);
    };
    commonValidation($("#command_form"), rules, messages, submitHandler);
};

$confirm_modal.on('hide.bs.modal', function () {
  $btn_confirm_modal.text('确认操作');
  $btn_confirm_modal.removeAttr('disabled');
});

function deleteruncommand(command_id){
    var success = function(data){
        if (data["status"] === "success"){
            $confirm_modal.modal('hide');
            $command_list_head.click();
        }
        else{
            $confirm_modal.modal('hide');
            Common.alert_message($("#error_modal"), 0, "删除失败");
        }
    };
    var data = {
        command_id: command_id
    };
    my_ajax(true, "/deletecommand", 'get', data, false, success);
}
function runcommand(command, param, name){
    $btn_confirm_modal.text('执行中');
    $btn_confirm_modal.attr('disabled', 'disabled');
    var success = function(data){
        if (data["status"] === "success"){
            $confirm_modal.modal('hide');
            Common.alert_message($("#error_modal"), 1, "已执行，可在记录里查看执行结果");
        }
        else{
            $confirm_modal.modal('hide');
            Common.alert_message($("#error_modal"), 0, "执行失败");
        }
    };
    var data = {
        api: command,
        param: param,
        type: 'all',
        name: name
    };
    my_ajax(true, "/run/command", 'get', data, true, success);
}
var send_command_type = '';
var send_command_api = '';
var send_command_param = '';
var send_command_id = '';
var send_command_name = '';
function operate_confirm(type,command,param,name){
    send_command_api = command;
    send_command_param = param;
    send_command_name = name;
    if (type === 0){
        $confirm_modal_title.html('删除操作');
        $confirm_modal_content.html('<h4><span style="color: red">删除命令：</span>'+name+'</h4>');
        send_command_type = 'delete';
        $confirm_modal.modal('show')
    }else if(type === 1){
        $confirm_modal_title.html('执行操作');
        $confirm_modal_content.html('<h4><span style="color: red">执行命令：</span>'+name+'</h4>');
        send_command_type = 'send';
        $confirm_modal.modal('show')
    }
}

$btn_confirm_modal.click(function () {
    if (send_command_type === 'delete'){
        deleteruncommand(send_command_id)
    }else if (send_command_type === 'send'){
        runcommand(send_command_api, send_command_param, send_command_name)
    }

});


function get_command_data() {
    var ajax_data = {
        "url": "/getcommand",
        "type": "GET",
        "data": {"server_id": '-1'},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            var a = {'data': result};
            return a.data;
        }
    };
    var columns = [{"title": "名称", 'data': 'name'}, {"title":"命令", 'data': 'command'},{"title":"参数", 'data': 'param'},
      {"title":"操作", 'data': 'id'}];
    var columnDefs = [
        {
            "targets": -1,
            "render": function (data, type, row) {
                send_command_id = data;
                var str = "'"+row.command + "','" + row.param + "','" + row.name+"'";
                return '<button onclick="operate_confirm(1,'+str+')" class="btn btn-xs blue">执行</button><button onclick="operate_confirm(0,'+str+')" class="btn btn-xs red">删除</button>';
            }
        }
    ];
    return new_front_page_table($command_list_tab, ajax_data,columns,columnDefs,false);
}

function send_command_record() {
    var ajax_data = {
        "url": "/get/commands/records",
        "type": "GET",
        "data": {"game_id": '-1', 'start_date': $start_date.val(), 'end_date': $end_date.val()},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'ok' ){
                return result.data
            }else{
                return []
            }
        }
    };
    var columns = [{"title": "操作人", 'data': 'op_user'}, {"title":"区服", 'data': 'server_id'}, {"title":"名称", 'data': 'name'},{"title":"命令", 'data': 'command'},
      {"title":"参数", 'data': 'param'}, {"title":"状态", 'data': 'status'}, {'title': "备注", 'data': 'response'}];
    var columnDefs = [];
    return new_front_page_table($command_record_table, ajax_data,columns,columnDefs,false);
}



if (server_ip === ''){
    //初始化
    handleDatePickers();
    $start_date.val(getNowFormatDate(6));
    $end_date.val(getNowFormatDate(0));
    commandValidation();
    get_command_data()
} else if (server_ip !== "all" && server_ip.indexOf('-')>0){
    getAllGame("/server/queryallgame/filter", {tag:1, filter_info: server_ip})
} else if (server_ip === 'all'){
    getAllGame('/server/queryallgame', {tag:1});
}else{
    getAllGame('/server/queryallgame/server_ip', {extranet_ip:server_ip,tag:1});
}

function flush_online(server, col, mode){
    get_game_status(server, col, mode);
    get_one_line(server, col);
    get_game_error_total(server, col, 1, 5);
}

$('#btn_confirm_jump_log').click(function () {
    window.location.href = "/operate_game/log";

});
function set_game_service(tag, method) {
    var game_list = [];
    $("input[name='check_game']").each(function(e){
        if ($(this).is(":checked")){
            game_list.push($(this).val());
        }
    });
    var success = function(data){
        $('#jump_log_modal').modal('show');
    };
    var req_data = {
        server_list: JSON.stringify(game_list), tag: tag, method: method
    };
    my_ajax(true, "/server/setallgameservice", "get", req_data, true, success);
}

function check_game(){
    var str_game = "";
    var str_list = [];

    $("input[name='check_game']").each(function(e){
        str_game += $(this).val() + ",";
        if($(this).is(":checked")){
            str_list.push($(this).val());
        }
    });
    if(str_list.length == 0){
        show_error_modal(0, "请选择区服.");
        return false;
    }
    return true;
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
    if (check_game()) {
        var str_html = reboot_or_close_notice(game_time, {}, false, 1);
        create_del_modal($operate_game_modal, str_html, "btn_confirm");
        $("#btn_confirm").attr("onclick", "reboot(2)");
        $operate_game_modal.modal("show");
    }
});

$("#gate_start_game").on("click", function(e){
    e.preventDefault();
    if (check_game())
        start_game(2, 1);
});

$("#close_gate").on("click", function(e){
    e.preventDefault();
    if (check_game())
        close_game(2, 1);
});



//网关模式game控制
$("#gate_game_reboot_game").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        var str_html = reboot_or_close_notice(game_time, {}, false, 2);
        create_del_modal($operate_game_modal, str_html, "btn_confirm");
        $("#btn_confirm").attr("onclick", "reboot(3)");
        $operate_game_modal.modal("show");
    }
});

$("#gate_game_start_game").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        start_game(3, 2);
    }
});

$("#close_gate_game").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        close_game(3, 2);
    }
});

//网关模式ext控制
$("#reboot_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        var str_html = reboot_or_close_notice(ext_time, {}, false, 3);
        create_del_modal($operate_game_modal, str_html, "btn_confirm");
        $("#btn_confirm").attr("onclick", "reboot(4)");
        $operate_game_modal.modal("show");
    }
});

$("#start_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        start_game(4, 3);
    }
});

$("#close_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        close_game(4, 3);
    }
});

//网关模式总控制
$("#reboot_all").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        var str_html = reboot_or_close_notice(game_time, ext_time, false, 4);
        create_del_modal($operate_game_modal, str_html, "btn_confirm");
        $("#btn_confirm").attr("onclick", "reboot(6)");
        $operate_game_modal.modal("show");
    }
});

$("#start_all").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        start_game(6, 4);
    }
});

$("#close_all").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        close_game(6, 4);
    }
});


$("#all_check").on("change", function (e) {
    e.preventDefault();
    var $check_game = $("input[name='check_game']");

    if ($(this).is(":checked")) {
        $check_game.prop("checked", true);
        $check_game.parent("span").addClass("checked");
    }
    else{
        $check_game.prop("checked", false);
        $check_game.parent("span").removeClass("checked");
    }
});

$("#flush_current").bind("click", function(e){
    e.preventDefault();
    getGlobalStatus();
    get_acc_status();
    if (server_ip === 'all'){
        setTimeout(getAllGame('/server/queryallgame', {tag:1}), 5000);
    }else{
        setTimeout(getAllGame('/server/queryallgame/server_ip', {extranet_ip:server_ip,tag:1}), 5000);
    }

});

var $check_game_start_id = $('#check_game_start_id');
var $check_game_end_id = $('#check_game_end_id');
var $select_game_prompt = $('#select_game_prompt');
function isRealNum(val){
    // isNaN()函数 把空串 空格 以及NUll 按照0来处理 所以先去除
    if(val === "" || val === null){
        return false;
    }
    return !isNaN(val)
}
$('#btn_confirm_select_game').click(function () {
    var start_id = $check_game_start_id.val();
    var end_id = $check_game_end_id.val();
    var game_id;
    if (isRealNum(start_id) && isRealNum(end_id)){
        var $check_game = $("input[name='check_game']");

        $check_game.each(function (a, b) {
            game_id = $(b);
            if ( parseInt(end_id) >= parseInt(game_id.val()) && parseInt(game_id.val()) >= parseInt(start_id)){
                game_id.prop("checked", true);
            }else{
                game_id.prop("checked", false);
            }

        });

        $('#select_game_modal').modal('hide')

    }else{
        $select_game_prompt.show()
    }

});

$('#select_game_modal').on('hide.bs.modal', function () {
  $select_game_prompt.hide()
});
