/**
 * Created by wangrui on 16/7/4.
 */

var $acc_modal = $("#acc_modal");
var acc_url = "";
var global_url = "";

var getlog = function () {
    var success = function (data) {
        acc_url = data["acc_url"];
        global_url = data["global_url"];

    }; 
    var data = {
        server_id: 0
    };
    my_ajax(true, "/getlog", 'get', data, true, success);
};
getlog();

function reboot_or_close_notice(tag, tag2){
    var str_notice = "是否";
    if (tag == 1){
        str_notice += '重启';
    }
    else{
        str_notice += '关闭';
    }
    if (tag2 == 1){
        str_notice += "账号";
    }
    else if (tag2 == 2){
        str_notice += "充值";
    }
    else if(tag2 == 3){
        str_notice += "账号、充值";
    }
    else{
        str_notice += "全局";
    }
    str_notice += '服务';
    return str_notice;
}


function getGlobalStatus(){
    var success = function (data) {
        var html = "";
        var run_html = "<span class='label label-success'><i class='fa fa-play'></i></span>";
        var stop_html = "<span class='label label-danger'><i class='fa fa-stop'></i></span>";
        if (data["port"] == "on") {
            html += run_html;
        }
        else {
            html += stop_html;
        }
        $("#global_status").html(html);
    };
    my_ajax(true, "/getglobalstatus", "get", {}, true, success);
}

$("#global_service").on("click", function(e){
    e.preventDefault();
    getGlobalStatus();
});



function set_global_service(method) {
    var success = function(data){
        if (method == 1) {
            setTimeout("getGlobalStatus()", 2000);
        }
        else {
            setTimeout("getGlobalStatus()", 2000);
        }
    };
    var data = {
        method: method
    };
    my_ajax(true, "/setglobalservice", "get", data, true, success);
}


$("#close_global").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 4);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_global_service(0, 1)");
    $acc_modal.modal("show");
});

$("#start_global").click(function (e) {
    e.preventDefault();
    set_global_service(1, 1);
});

function reboot_global(tag){
    set_global_service(0, tag);
    set_global_service(1, tag);
}

$("#reboot_global").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(1, 4);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot_global(1)");
    $acc_modal.modal("show");
});


$("#global_log").on("click", function(e){
    e.preventDefault();
    var param = $("#global_param").val();
    window.open(global_url + "?param=" + param);
});



function getAccStatus(method, div){
    var success = function (data) {
        var html = "";
        var total = 0;
        var run_html = "<span class='label label-success'> <i class='fa fa-play'></i></span>";
        var stop_html = "<span class='label label-danger'><i class='fa fa-stop'></i></span>";
        if (data["acc_port"] == "on") {
            html += run_html;
            total += 1;
        }
        else {
            html += stop_html;
        }
        if (method == 2) {
            var html2 = "";
            if (data["pay_port"] == "on") {
                html2 += run_html;
                total += 1;
            }
            else {
                html2 += stop_html;
            }
            $("#pay_status").html(html2);
        }
        div.html(html);
        var html3 = "";
        if (total == 2) {
            html3 = run_html;
        }
        else {
            html3 = stop_html;
        }
        $("#acc_status_total").html(html3);
    };
    var data = {
        method: method
    };
    my_ajax(true, "/getaccstatus", "get", data, true, success);
}


$("#accservice").click(function (e) {
    e.preventDefault();
    var acc_status = $("#acc_status");
    getAccStatus(1, acc_status);
});

$("#accservice2").click(function(e){
    e.preventDefault();
    var acc_status = $("#acc_status2");
    getAccStatus(2, acc_status);
});
$("#accservice2").click();

$("#acc_log").bind("click", function (e) {
    e.preventDefault();
    var param = $("#acc_param").val();
    window.open(acc_url + "?tag=1&param=" + param);
});

$("#recharge_acc_log").bind("click", function (e) {
    e.preventDefault();
    var param = $("#acc_recharge_param").val();
    window.open(acc_url + "?tag=2&param=" + param);
});

//标准模式
$("#close_acc").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 1);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 1)");
    $acc_modal.modal("show");
});

$("#start_acc").click(function (e) {
    e.preventDefault();
    set_acc_service(1, 1);
});

function reboot(tag){
    set_acc_service(0, tag);
    set_acc_service(1, tag);
}

$("#reboot_acc").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(1, 3);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(1)");
    $acc_modal.modal("show");
});

//总控制
$("#close_acc_total").on("click", function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 3);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 4)");
    $acc_modal.modal("show");
});

$("#start_acc_total").on("click", function(e){
    e.preventDefault();
    set_acc_service(1, 4);
});

$("#reboot_acc_total").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(1, 3);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(4)");
    $acc_modal.modal("show");
});


//账号服务
$("#close_acc2").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 1);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 2)");
    $acc_modal.modal("show");
});

$("#start_acc2").on("click", function(e){
    e.preventDefault();
    set_acc_service(1, 2);
});

$("#reboot_acc2").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(1, 1);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(2)");
    $acc_modal.modal("show");
});


//充值服务
$("#close_pay").click(function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 2);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 3)");
    $acc_modal.modal("show");
});

$("#reboot_pay").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(1, 2);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(3)");
    $acc_modal.modal("show");
});


$("#start_pay").on("click", function(e){
    e.preventDefault();
    set_acc_service(1, 3);
});



function set_acc_service(acc_tag, method) {
    var success = function(data){
        if (method == 1) {
            setTimeout("$('#accservice').click()", 5000);
        }
        else {
            setTimeout("$('#accservice2').click()", 5000);
        }
    };
    var data = {
        acc_tag: acc_tag,
        method: method
    };
    my_ajax(true, "/setaccservice", "get", data, true, success);
}


var source_flush = function (tag, method) {
    var success = function (data) {
        if (data["status"] == "success") {
            Common.alert_message($("#error_modal"), 1, data["module"]);
        }
        else {
            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
        }
    };
    var data = {
        tag: tag,
        method: method
    };
    console.log(data);
    my_ajax(true, "/flushaccsource", 'get', data, true, success);
};

//一个进程的模式
$("#source_flush").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 2);
});
//一个进程的模式
$("#back_flush").bind("click", function (e) {
    e.preventDefault();
    source_flush(2, 2);
});


$("#source_flush2").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 1);
});

$("#back_flush2").bind("click", function (e) {
    e.preventDefault();
    source_flush(2, 1);
});


$("#source_flush_pay").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 2);
});


$("#back_flush_pay").bind("click", function(e){
    e.preventDefault();
    source_flush(2, 2);
});


$("#command").on("click", function (e) {
    e.preventDefault();
    $("#command_name").val("");
    $("#command_value").val("");
    $("#command_modal").modal("show");
});

var PARAM_DATA = {
    "review_version_lst": "评审版本序列",
    "WhiteTestResourceVersion": "名单测试热更",
    "InvalidClientVersion": "热更关闭"
};

display_left_filter();


//添加
$("#sys_add").on("click", function () {
    $("#sys_name").attr("disabled", false);
    $("#sys_name").val("");
    $("#sys_value").val("");
    $("#sys_modal").modal("show");
});



var system_param_Validate = function () {
    var form1 = $('#sysparam_form');
    var rules = {
        sys_name: {
            required: true
        }
    };
    var messages = {
        sys_name: {
            required: "请输入参数名."
        }
    };
    var submitFunc = function () {
        var sys_name = $('#sys_name').val();
        var sys_value = $("#sys_value").val();
        var select_language = $("#select_language").val();
        var data = {
            sys_name: sys_name,
            sys_value: sys_value,
            language: select_language
        };

        var success = function(data){
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            $("#sys_modal").modal("hide");
            get_system_param();
        };
        my_ajax(true, "/operatesysparam", "get", data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
system_param_Validate();


function get_system_param() {
    var success = function (data){
        var str_info = "";
        for(var i=0; i < data.length; i++){
            str_info += "<tr>";
            str_info += "<td>" + data[i]["key"] + "</td>";
            str_info += "<td>" + PARAM_DATA[data[i]["key"]] + "</td>";
            str_info += "<td>" + data[i]["value"] + "</td>";
            str_info += "<td>";
            str_info += '&nbsp; <a onclick="mod_sys_params(this,' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs " data-toggle="modal"> <i class="fa fa-edit"></i></a>';
            str_info += "</td>";
            str_info += "</tr>";
        }
        $("#table_sys").html(str_info);
    };
    var select_language = $("#select_language").val();
    var data = {
        "language": select_language
    };
    my_ajax(true, "/getaccsysparam", "get", data, true, success);
}

$("#sysparam").on("click", function(e){
    e.preventDefault();
    get_system_param();
});

$("#select_language").on("change", function(e){
    e.preventDefault();
    get_system_param();
});


var mod_sys_params = function (div, sid) {
    var sys_name = $(div).parents('tr').children('td').eq(0).html();
    var sys_value = $(div).parents('tr').children('td').eq(2).html();
    $("#sys_name").val(sys_name);
    $("#sys_name").attr("disabled", true);
    $("#sys_value").val(sys_value);
    $("#sys_modal").modal("show");
};