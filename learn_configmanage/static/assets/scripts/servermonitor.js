

handleDatePickers2();
handleTimePickers();
var now_date = getNowFormatDate(0);
$("#create_date").val(now_date);
$("#open_date").val(now_date);
$("#restart_date").val(now_date);


create_del_modal($("#server_del_modal"), "是否删除此区服?", "confirm_del");
create_del_modal($("#base_del_modal"), "是否删除此数据库?", "confirm_del_base");


create_del_modal($("#del_openserver_modal"), "是否删除此记录?", "del_open_confirm");
create_del_modal($("#del_restartserver_modal"), "是否删除此记录?", "del_restart_confirm");
create_del_modal($("#del_servermonitor_modal"), "是否删除此记录?", "del_servermonitor_confirm");
create_del_modal($("#close_error_servermonitor_modal"), "是否关闭所有报错的服务探测?", "confirm_close_error_servermonitor");
create_del_modal($("#open_servermonitor_modal"), "是否开启所有的探测服务?", "confirm_open_servermonitor");


getGameServerDataCheck($("#restartserver_check"));

var GAME_SERVER_DICT2 = null;
var getAllGameServerData = function (div_select, tag) {
    if (GAME_SERVER_DICT2 == null) {
        var success = function (data) {
            GAME_SERVER_DICT2 = data;
        };
        my_ajax(true, '/server/getgameserver', 'get', {"tag": "1"}, false, success);
    }
    var str_html = "";
    if (tag == 2) {
        str_html += "<option value='0'>全服</option>";
    }
    for (var i in GAME_SERVER_DICT2) {
        str_html += '<option value="' + i + '">' + i + "区:" + GAME_SERVER_DICT2[i]["name"] + '</option>';
    }
    div_select.html(str_html);
};

getAllGameServerData($("#select_server"), 1);
getAllGameServerData($("#select_openserver"), 1);
getAllGameServerData($("#select_mid"), 1);

var server_data = {};
var START_MODE_DICT = {
    "5": "标准模式",
    "6": "性能模式"
};

var SERVER_STATUS = {
    "online": "在线",
    "offline": "停机",
    "maintain": "维护",
    "inner": "内部",
    "fault": "缺陷"
};
init_select_html(false, START_MODE_DICT, $("#start_mode"));
init_select_html(false, SERVER_STATUS, $("#server_status"));


var handleDatePickers = function () {

    if (jQuery().datepicker) {
        $('.date-picker').datepicker({
            rtl: App.isRTL(),
            autoclose: true,
            endDate: new Date()
        });
    }
};


var handleDatePickers2 = function () {
    if (jQuery().datepicker) {
        $('.date-picker').datepicker({
            rtl: App.isRTL(),
            autoclose: true
        });
    }
};

var handleTimePickers = function () {

    if (jQuery().timepicker) {
        $('.timepicker-24').timepicker({
            showInputs: false,
            minuteStep: 1,
            secondStep: 1,
            showSeconds: true,
            showMeridian: false
        });
    }
};


var getNowFormatDate = function (d) {
    var day = new Date();
    var CurrentDate = "";
    day.setDate(day.getDate() - d);
    var Year = day.getFullYear();
    var Month = day.getMonth() + 1;
    var Day = day.getDate();
    CurrentDate += Year + "-";
    if (Month >= 10) {
        CurrentDate += Month + "-";
    }
    else {
        CurrentDate += "0" + Month + "-";
    }
    if (Day >= 10) {
        CurrentDate += Day;
    }
    else {
        CurrentDate += "0" + Day;
    }
    return CurrentDate;
};

get_section($("#section_select"));

var servermonitorValidation = function () {
    var form1 = $('#servermonitor_form');
    var rules = {
        servermonitor_ip: {
            required: true
        },
        servermonitor_port: {
            required: true
        },
        servermonitor_protocol: {
            required: true
        }
    };
    var messages = {
        servermonitor_ip: {
            required: "请输入ip."
        },
        servermonitor_port: {
            required: "请输入port."
        },
        servermonitor_protocol: {
            required: "请选择传输协议."
        }
    };

    var submitFunction = function (form) {
        var ip_info = $("#servermonitor_ip").val();
        var port_info = $("#servermonitor_port").val();
        var protocol = $("#servermonitor_protocol").val();
        var req_path = $("#servermonitor_path").val();
        var req_way = $("#req_way").val();
        var req_param = $("#servermonitor_param").val();
        var success = function (data) {
            if (data.status == "fail") {
                Common.alert_message($("#error_modal"), 0, "添加失败.");
            }
            else if (data.status == "fail2") {
                Common.alert_message($("#error_modal"), 0, "无法连接数据库.");
            }
            $("#servermonitor_modal").modal("hide");
            get_servermonitor()
        };

        var data = {
            ip_info: ip_info, port_info: port_info,
            protocol: protocol, req_path: req_path, req_way: req_way, req_param: req_param
        };
        my_ajax(true, "/add/servermonitor/info", 'post', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};

servermonitorValidation();

function get_servermonitor() {
    var ajaxSource = "/query/servermonitor/info";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "sTitle": "id"
        },
        {
            "mDataProp": "ip",
            'sClass': 'center',
            "sTitle": "url"
        },
        {
            "mDataProp": "req_param",
            'sClass': 'center',
            "sTitle": "请求参数"
        },
        {
            "mDataProp": "protocol",
            'sClass': 'center',
            "sTitle": "协议"
        },
        {
            "mDataProp": "req_way",
            "sClass": "center",
            "sTitle": "请求方式"
        },

        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent":
                "<button onclick=\"del_servermonitor(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = aData.id;
        $('td:eq(0)', nRow).html(str_html1);
        var str_html2 = aData.ip + ":" + aData.port + aData.req_path;
        $('td:eq(1)', nRow).html(str_html2);
        var str_html3 = aData.req_param;
        $('td:eq(2)', nRow).html(str_html3);
        var str_html4 = aData.protocol;
        $('td:eq(3)', nRow).html(str_html4);
        var str_html5 = aData.req_way;
        $('td:eq(4)', nRow).html(str_html5);
        return nRow;
    };
    dataTablePage($("#table_servermonitor"), aoColumns, ajaxSource, {}, false, fnRowCallback);
}
get_servermonitor();
// $("#tab_servermonitor").ready(function (e) {
//     e.preventDefault();
//     get_servermonitor();
// });
jQuery(document).ready(function (e) {
    // e.preventDefault();
    get_servermonitor();
});

var del_servermonitor = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_servermonitor").dataTable().fnGetData(nRoW);
    $('#del_servermonitor_modal').modal("show");
    $("#del_servermonitor_confirm").attr('onclick', "confirm_del_servermonitor(" + data["id"] + ")");
};

var confirm_del_servermonitor = function (gid) {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#del_servermonitor_modal').modal("hide");
        get_servermonitor();
    };
    var data = {
        info_id: gid
    };
    my_ajax(true, '/delete/servermonitor/info', 'post', data, true, success);
};



$("#servermonitor_protocol").on("click", function (e)  {

    var protocol = $("#servermonitor_protocol").val();
    if (protocol == "HTTP") {
        // $("#show_http_columns").css("style", "");
        $("#show_http_columns").show()
    }
    else if (protocol == "TCP") {
        $("#show_http_columns").hide()
    }
});
$("#servermonitor_protocol").click();

var close_error_servermonitor = function () {
    $('#close_error_servermonitor_modal').modal("show");
    $("#confirm_close_error_servermonitor").attr('onclick', "confirm_close_error_servermonitor()");
};

var confirm_close_error_servermonitor = function () {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#close_error_servermonitor_modal').modal("hide");
    };
    my_ajax(true, '/close/error/servermonitor', 'post', true, success);
};


var open_servermonitor = function () {
    $('#open_servermonitor_modal').modal("show");
    $("#confirm_open_servermonitor").attr('onclick', "confirm_open_servermonitor()");
};

var confirm_open_servermonitor = function () {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#open_servermonitor_modal').modal("hide");
    };
    my_ajax(true, '/open/error/servermonitor', 'post', true, success);
};