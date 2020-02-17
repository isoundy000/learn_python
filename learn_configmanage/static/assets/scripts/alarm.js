/**
 * Created by wangrui on 17/6/3.
 */


handleDatePickers();
$("#start_date").val(getNowFormatDate(1));
$("#end_date").val(getNowFormatDate(0));


var $select_server = $("#select_server");

getGameServerData($select_server, 1);

var user_data = {};
create_del_modal($("#alarm_config_del_modal"), "是否删除此记录?", "del_confirm");


function get_user() {
    var success = function(data){
        for(var s =0; s<data.length; s++){
            user_data[data[s]["id"]] = data[s];
        }

    };
    if ($.isEmptyObject(user_data)){
        my_ajax(true, '/getalluser', 'get', {}, false, success);
    }
    var str_info = "";
    for (var i in user_data) {
        if (user_data[i]["mail"] || user_data[i]["phone"]){
            str_info += "<label> <input type=\"checkbox\" name=\"user_data\" value=\"" +
            i  + "\">" + user_data[i]["name"] + "</label>";
        }

    }
    $("#alarm_user").html(str_info);
}
get_user();


var alarmConfigValidation = function () {
    var form1 = $('#alarm_config_form');
    var rules = {
        alarm_name: {
            required: true
        },
        alarm_module_name: {
            required: true
        },
        alarm_config_time: {
            required: true
        }

    };
    var messages = {
        alarm_name: {
            required: "请输入用户名."
        },
        alarm_module_name: {
            required: "密码输入不一致."
        },
        alarm_config_time: {
            required: "请输入采集时频"
        }
    };

    var submitHandler = function (form) {
        var alarm_config_id = $("#alarm_config_id").val();
        var alarm_name = $("#alarm_name").val();
        var alarm_module_name = $("#alarm_module_name").val();
        var alarm_config_time = $("#alarm_config_time").val();
        var user_data = [];
        $("input[name='user_data']:checked").each(function () {
            user_data.push($(this).val());
        });
        var email = 0;
        var phone = 0;
        $("input[name='send_type']:checked").each(function () {
            var send_value = $(this).val();
            if (send_value == "1"){
                email = 1;
            }
            if (send_value == "2"){
                phone = 1;
            }
        });

        var success = function (data) {
            if (data.status == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            $("#alarm_config_modal").modal("hide");
            get_alarm_config();
        };
        var data = {
            alarm_config_id: alarm_config_id,
            alarm_name: alarm_name,
            alarm_module_name: alarm_module_name,
            alarm_config_time: alarm_config_time,
            user_data: JSON.stringify(user_data),
            email: email,
            phone: phone
        };
        my_ajax(true, '/alarm/operateconfig', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
alarmConfigValidation();


var get_alarm_config = function () {
    var ajax_source = "/alarm/getalarmconfig";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "报警名称"
        },
        {
            "mDataProp": "module_name",
            "sClass": "center",
            "sTitle": "模块程序"
        },
        {
            "mDataProp": "p_time",
            "sClass": "center",
            "sTitle": "处理时频"
        },
        {
            "mDataProp": "send",
            "sClass": "center",
            "sTitle": "推送人"
        },
        {
            "mDataProp": "email",
            "sClass": "center",
            "sTitle": "报警方式"
        },
        {
            "mDataProp": "phone",
            "sClass": "center",
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_alarm_config(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>" +
                "&nbsp;&nbsp;<button onclick=\"del_alarm_config(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        $('td:eq(2)', nRow).html(aData.p_time + "分钟");
        var send_split = aData.send.split(",");
        var str_html = "";
        for(var s=0; s<send_split.length; s++){
            str_html += user_data[send_split[s]]["name"] + "、";
        }
        $('td:eq(3)', nRow).html(str_html);

        var str_html2 = "";
        var email = aData.email;
        var phone = aData.phone;
        if (email == 1){
            str_html2 += "邮件";
        }
        if (phone == 1){
            str_html2 += "手机";
        }
        $('td:eq(4)', nRow).html(str_html2);

        return nRow;
    };
    dataTablePage($("#alarm_config_table"), aoColumns, ajax_source, {}, false, fnRowCallback);
};
get_alarm_config();


$("#add_alarm_config").on("click", function (e) {
    e.preventDefault();
    $("#alarm_name").val("");
    $("#alarm_module_name").val("");
    $("#alarm_config_time").val("");
    $("input[name='user_data']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    $("input[name='send_type']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    $("#alarm_config_modal").modal("show");
});

var mod_alarm_config = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#alarm_config_table").dataTable().fnGetData(nRoW);
    $("#alarm_config_id").val(data["id"]);
    $("#alarm_name").val(data["name"]);
    $("#alarm_module_name").val(data["module_name"]);
    $("#alarm_config_time").val(data["p_time"]);
    var custom = data["send"];
    var split_arr = custom.split("|");
    for (var i = 0; i < split_arr.length; i++) {
        if (split_arr[i] != "") {
            var operate_d = $("input[name='send'][value='" + split_arr[i] + "']");
            operate_d.prop("checked", true);
            operate_d.parent("span").addClass("checked");
        }
    }
    var email = data["email"];
    if (email == 1){
        var send_type = $("input[name='send_type'][value='1']");
        send_type.prop("checked", true);
        send_type.parent("span").addClass("checked");
    }
    var phone = data["phone"];
    if (phone == 1){
        var send_type2 = $("input[name='send_type'][value='2']");
        send_type2.prop("checked", true);
        send_type2.parent("span").addClass("checked");
    }
    $("#alarm_config_modal").modal("show");
};

var del_alarm_config = function (s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#alarm_config_table").dataTable().fnGetData(nRoW);
    $('#alarm_config_del_modal').modal("show");
    $("#del_confirm").attr('onclick', "confirm_del_alarm_config(" + data["id"] + ")");
};

function confirm_del_alarm_config(alarm_config_id) {
    var success = function () {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败");
        }
        get_alarm_config();
    };
    var data = {
        alarm_config_id: alarm_config_id
    };
    my_ajax(true, '/alarm/delete', 'get', data, true, success);
}


function get_alarm_info(){
    var server_id = $select_server.val();
    var start = $("#start_date").val();
    var end = $("#end_date").val();
    var alarm_type = $("#alarm_type").val();
    var ajax_source = "/alarm/getalarminfo";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "gid",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "区服"
        },
        {
            "mDataProp": "type",
            "sClass": "center",
            "sTitle": "报警类型"
        },
        {
            "mDataProp": "status",
            "sClass": "center",
            "sTitle": "是否发送"
        },
        {
            "mDataProp": "mess1",
            "sClass": "center",
            "sTitle": "信息"
        },
        {
            "mDataProp": "otime",
            "sClass": "center",
            "sTitle": "时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = aData.gid + "区:" + aData.name;
        $('td:eq(1)', nRow).html(str_html1);

        var str_html2 = alarm_type[aData.type];
        $('td:eq(2)', nRow).html(str_html2);

        var str_html3 = "";
        if (aData.status == 1){
            str_html3 = "<span class='badge badge-success'>Y</span>";
        }
        else{
            str_html3 = "<span class='badge badge-danger'>N</span>";
        }
        $('td:eq(3)', nRow).html(str_html3);

        var str_html4 = "";
        if (aData.status2 == 1){
            str_html4 = "<button onclick=\"process_alarm(this)\" class=\"btn default btn-xs purple\" data-toggle=\"modal\">处理 <i class=\"fa fa-edit\"></i></button>";
        }
        else{
            str_html4 = "<button onclick=\"display_process(this)\" class=\"btn default btn-xs blue\" data-toggle=\"modal\">查看 <i class=\"fa fa-edit\"></i></button>";
        }
        $('td:eq(4)', nRow).html(str_html4);

        return nRow;
    };
    var data = {
        server_id: server_id, alarm_type: alarm_type, start: start, end: end
    };
    dataTablePage($("#alarm_table"), aoColumns, ajax_source, data, false, fnRowCallback);
}


$("#btn_query_alarm").on("click", function (e) {
    e.preventDefault();
    get_alarm_info();
});


var process_alarm = function (p_alarm) {
    var nRoW = $(p_alarm).parents('tr')[0];
    var data = $("#alarm_table").dataTable().fnGetData(nRoW);
    $("#alarm_id").val(data["id"]);
    $("#process_alarm_modal").modal("show");
};


var display_porcess = function(p_alarm){
    var nRoW = $(p_alarm).parents('tr')[0];
    var data = $("#alarm_table").dataTable().fnGetData(nRoW);
    var aid = data["id"];
    var success = function(data){
        var str_html = "";
        str_html += "<td>" + data["id"] + "</td>";
        str_html += "<td>" + data["username"] + "</td>";
        str_html += "<td>" + data["opttime"] + "</td>";
        str_html += "<td>" + data["desc"] + "</td>";
        $("#process_alarm_list").html(str_html);
    };
    var req_data = {
        aid: aid
    };
    my_ajax(true, "/alarm/display", 'get', req_data, true, success);
};


$("#btn_confirm_desc").on("click", function (e) {
    var success = function (data) {
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "修改失败.");
        }
        $("#process_alarm_modal").modal("hide");
        get_alarm_info();
    };
    var req_data = {
        "aid": $("#alarm_id").val(),
        "process_desc": $("#process_desc_info").val()
    };
    my_ajax(true, "/alarm/process", "get", req_data, true, success);
});