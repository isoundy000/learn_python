var $game_id = $('#game_id');
var $operate_game_modal =$('#operate_game_modal');
var $btn_dayclear = $('#btn_dayclear');
var $game_opentime = $('#game_opentime');

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
var server_id = $game_id.find('option:selected').val();
var server_name = $game_id.find('option:selected').text();

my_ajax(true, "/put/games/time", "get", {'server_id': server_id}, false, function (result) {
    $game_opentime.text(result['value']);
});


$game_opentime.editable({
    type: "datetime",
    url: '/put/games/time',
    placement: 'bottom',
    ajaxOptions:{
      dataType: 'json'
    },
     params: function (params) {
        var data = {};
        data['server_id'] = server_id;
        data['create_time'] = params.value;
         return data;
    },
    format: 'yyyy-mm-dd hh:ii:ss',
    viewformat: 'yyyy-mm-dd hh:ii:ss',
    datetimepicker: { weekStart: 1 , pickerPosition: 'bottom-right'},
    validate: function (value) {
        if (!$.trim(value)) {
            return '不能为空';
        }
    },
    success:function (response) {
         if(response.status === 'fail'){
            return response.errmsg
        }
    },
    error: function (response) {
        return '保存异常，请联系管理员';
    }

});


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


create_del_modal($("#closegame_modal"), "是否关闭游戏?", "confirm_closegame");
create_del_modal($("#dayclear_modal"), "是否执行每日清零?", "confirm_dayclear");

function set_game_service(tag, method) {
    var game_list = [];
    game_list.push(server_id);
    var success = function(data){
        setTimeout("getServerStatus()", 5000);
    };
    var req_data = {
        server_list: JSON.stringify(game_list), tag: tag, method: method
    };
    my_ajax(true, "/server/setallgameservice", "get", req_data, true, success);
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



$btn_dayclear.on("click", function(e){
    e.preventDefault();
    $("#dayclear_modal").modal("show");
    $("#confirm_dayclear").attr("onclick", "runcommand2('gm/dayclear')");
});


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

getServerStatus();
