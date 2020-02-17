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

function reboot_or_close_notice(tag, s_type){
    var str_notice = "是否";
    var operate_type = {
        "reboot": '重启',
        "close": "关闭",
        "start": "启动"
    };
    str_notice += operate_type[tag];
    var service_type = {
        "resource": "资源",
        "account": "账号",
        "recharge": "充值",
        "all": "资源、账号、充值",
        "global": "全局"
    };
    str_notice += service_type[s_type];
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
    my_ajax(true, "/global/status", "get", {}, true, success);
}

$("#global_service").on("click", function(e){
    e.preventDefault();
    getGlobalStatus();
});



function set_global_service(method) {
    var success = function(data){
        setTimeout("getGlobalStatus()", 2000);
    };
    var data = {
        method: method
    };

    my_ajax(true, "/global/service", "get", data, true, success);
}


$("#close_global").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice("close", "global");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_global_service(0)");

    $acc_modal.modal("show");
});

$("#start_global").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice("start", "global");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_global_service(1)");
    $acc_modal.modal("show");
});

function reboot_global(){
    set_global_service(0);
    set_global_service(1);
}

$("#reboot_global").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice("reboot", "global");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot_global()");
    $acc_modal.modal("show");
});


$("#global_log").on("click", function(e){
    e.preventDefault();
    var param = $("#global_param").val();
    window.open(global_url + "?param=" + param);
});



function getAccStatus(){
    var success = function (data) {
        var html = "";
        var html2 = "";
        var html3 = "";
        var total = 0;
        var run_html = "<span class='label label-success'><i class='fa fa-play'></i></span>";
        var stop_html = "<span class='label label-danger'><i class='fa fa-stop'></i></span>";
        if (data["acc_port"] === "on") {
            html += run_html;
            total += 1;
        }
        else {
            html += stop_html;
        }
        $("#acc_status2").html(html);
        if (accmode === 1){
            $("#div_res").hide();
            $("#div_pay").hide();
            $("#div_all").hide();
        }

        else if(accmode === 2 || accmode === 3){
            if (data["pay_port"] === "on") {
                html2 += run_html;
                total += 1;
            }
            else {
                html2 += stop_html;
            }
            $("#pay_status").html(html2);
            if (accmode === 2){
                $("#div_res").hide();
            }
            else{
                if (data["res_port"] === "on") {
                    html3 = run_html;
                    total += 1;
                }
                else {
                    html3 += stop_html;
                }
                $("#res_status").html(html3);
                $("#div_res").show();
            }
            var html4 = "";
            if (total === accmode) {
                html4 = run_html;
            }
            else {
                html4 = stop_html;
            }
            $("#acc_status_total").html(html4);
        }
    };
    my_ajax(true, "/account/status", "get", {}, true, success);
}


var add_input_validate = function (modal) {
    var html = "<div class='form-group'><input type='text' value='' id='validate_code'/></div>";
    modal.children("modal-body").append(html);
};


// $("#accservice").click(function (e) {
//     e.preventDefault();
//     var acc_status = $("#acc_status");
//     getAccStatus(acc_status);
// });
// $("#accservice").click();

$("#accservice2").click(function(e){
    e.preventDefault();
    getAccStatus();
});
$("#accservice2").click();


$("#res_log").bind("click", function (e) {
    e.preventDefault();
    var param = $("#res_param").val();
    window.open(acc_url + "?tag=1&param=" + param);
});

$("#acc_log").bind("click", function (e) {
    e.preventDefault();
    var param = $("#acc_param").val();
    window.open(acc_url + "?tag=2&param=" + param);
});

$("#recharge_acc_log").bind("click", function (e) {
    e.preventDefault();
    var param = $("#acc_recharge_param").val();
    window.open(acc_url + "?tag=3&param=" + param);
});

function reboot(method){
    set_acc_service(0, method);
    set_acc_service(1, method);
}


// //标准模式
// $("#close_acc").click(function (e) {
//     e.preventDefault();
//     var str_html = reboot_or_close_notice(2, 1);
//     create_del_modal($acc_modal, str_html, "btn_confirm");
//
//     $("#btn_confirm").attr("onclick", "set_acc_service(0, 1)");
//     $acc_modal.modal("show");
// });
//
// $("#start_acc").click(function (e) {
//     e.preventDefault();
//     set_acc_service(1, 1);
// });
//
//
// $("#reboot_acc").click(function (e) {
//     e.preventDefault();
//     var str_html = reboot_or_close_notice(1, 3);
//     create_del_modal($acc_modal, str_html, "btn_confirm");
//     $("#btn_confirm").attr("onclick", "reboot(1)");
//     $acc_modal.modal("show");
// });

//总控制
$("#close_acc_total").on("click", function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice('close', 'all');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "set_acc_service(0, 1)");
    else
        $("#btn_confirm").attr("onclick", "set_acc_service(0, 5)");
    $acc_modal.modal("show");
});

$("#start_acc_total").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice('start', 'all');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "set_acc_service(1, 1)");
    else
        $("#btn_confirm").attr("onclick", "set_acc_service(1, 5)");
    $acc_modal.modal("show");
});

$("#reboot_acc_total").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice('reboot', 'all');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "reboot(1)");
    else
        $("#btn_confirm").attr("onclick", "reboot(5)");
    $acc_modal.modal("show");
});

//资源服务
$("#close_res").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice('close', "resource");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 2)");
    $acc_modal.modal("show");
});

$("#start_res").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice('start', "resource");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(1, 2)");
    $acc_modal.modal("show");
});

$("#reboot_res").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice('reboot', "resource");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(2)");
    $acc_modal.modal("show");
});


//账号服务
$("#close_acc2").click(function (e) {
    e.preventDefault();
    var str_html = reboot_or_close_notice("close", 'account');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "set_acc_service(0, 1)");
    else
        $("#btn_confirm").attr("onclick", "set_acc_service(0, 3)");
    $acc_modal.modal("show");
});

$("#start_acc2").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice("start", 'account');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "set_acc_service(1, 1)");
    else
        $("#btn_confirm").attr("onclick", "set_acc_service(1, 3)");
    $acc_modal.modal("show");
});

$("#reboot_acc2").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice("reboot", 'account');
    create_del_modal($acc_modal, str_html, "btn_confirm");
    if (accmode === 1)
        $("#btn_confirm").attr("onclick", "reboot(1)");
    else
        $("#btn_confirm").attr("onclick", "reboot(3)");
    $acc_modal.modal("show");
});


//充值服务
$("#close_pay").click(function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice(2, 2);
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(0, 4)");
    $acc_modal.modal("show");
});

$("#reboot_pay").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice("reboot", "recharge");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "reboot(4)");
    $acc_modal.modal("show");
});


$("#start_pay").on("click", function(e){
    e.preventDefault();
    var str_html = reboot_or_close_notice("start", "recharge");
    create_del_modal($acc_modal, str_html, "btn_confirm");
    $("#btn_confirm").attr("onclick", "set_acc_service(1, 4)");
    $acc_modal.modal("show");
});



function set_acc_service(acc_tag, method) {
    var data = {
        acc_tag: acc_tag,
        method: method
    };
    $.ajax({
            type: 'get',
            url: '/account/service',
            data: data,
            dataType: 'JSON',
            cache: false,
            headers: {"cache-control": "no-cache"},
            async: true,
            success: function (data) {
                if (method == 1) {
                    setTimeout("$('#accservice').click()", 5000);
                }
                else {
                    setTimeout("$('#accservice2').click()", 5000);
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
    // my_ajax(true, "/account/service", "get", data, true, success);
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
    my_ajax(true, "/account/flushaccsource", 'get', data, true, success);
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


$("#res_source_flush").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 1);
});

$("#res_back_flush").bind("click", function (e) {
    e.preventDefault();
    source_flush(2, 1);
});


$("#source_flush2").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 2);
});

$("#back_flush2").bind("click", function (e) {
    e.preventDefault();
    source_flush(2, 2);
});


$("#source_flush_pay").bind("click", function (e) {
    e.preventDefault();
    source_flush(1, 3);
});


$("#back_flush_pay").bind("click", function(e){
    e.preventDefault();
    source_flush(2, 3);
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
        var sys_value = $("#sys_value").val().replace(/\n/g, ',');
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
            system_param_table_data.ajax.reload(null, false);
        };
        my_ajax(true, "/operatesysparam", "get", data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
system_param_Validate();


var system_param_table_data;
var get_system_param = function () {
    var ajax_data = {
        "url": "/getaccsysparam",
        "type": "GET",
        "data": {"language": $("#select_language").val()},
        "error": function (jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            var data = [];
            var param_prompt;
            var params;
            for (var i = 0; i < result.length; i++) {
                param_prompt = result[i]["key"] in PARAM_DATA ? result[i]["key"] : '';
                params = result[i]["value"] === null ? '' : result[i]["value"];
                data.push([result[i]["key"], param_prompt, params]);
            }
            return data
        }
    };
    var columns = [{"title": "参数名称"}, {"title": "参数说明"}, {"title": "参数数值"}, {"title": "操作"}];
    var columnDefs = [
        {
            "targets": -1,
            "render": function () {
                return '<button onclick="mod_sys_params(this)" class="btn btn-xs default"> <i class="fa fa-edit"></i></button>'
            }
        }
    ];
    system_param_table_data = $("#table_sys").DataTable({
        "destroy" : true,
        "autoWidth" : true,
        "processing" : true,
        "ajax": ajax_data,
        "searching": false,    //去掉搜索框方法三：这种方法可以
        "lengthChange": true,
        "lengthMenu":[10,20,50,100],
        "paging": false,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage,
        "scrollX": true,
        fixedColumns: { //固定列的配置项
            rightColumns:1, //固定右边第一列
            leftColumns: 1
        }
   });
};

$("#sysparam").on("click", function(e){
    e.preventDefault();
    get_system_param();
});


var mod_sys_params = function (div, sid) {
    var table_data = system_param_table_data.row(div).data();
    var sys_name = table_data[0];
    var sys_value = table_data[2];
    $("#sys_name").val(sys_name);
    $("#sys_name").attr("disabled", true);
    sys_value = sys_value.replace(/,/g, '\n');
    $("#sys_value").val(sys_value);
    $("#sys_modal").modal("show");
};