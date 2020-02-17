/**
 * Created by wangrui on 14-10-13.
 */

var $open_datetime = $('#open_datetime');
var $sync_create_time = $('#sync_create_time');
// display_left_filter();

handleDatePickers2();
handleTimePickers();
var now_date = getNowFormatDate(0);
$("#create_date").val(now_date);
$("#restart_date").val(now_date);

$open_datetime.datetimepicker({
    format: 'yyyy-mm-dd hh:ii',
    startDate: new Date(),    autoclose:true
});

create_del_modal($("#server_del_modal"), "是否删除此区服?", "confirm_del");
create_del_modal($("#base_del_modal"), "是否删除此数据库?", "confirm_del_base");


create_del_modal($("#del_openserver_modal"), "是否删除此记录?", "del_open_confirm");
create_del_modal($("#del_restartserver_modal"), "是否删除此记录?", "del_restart_confirm");
getGameServerDataCheck($("#restartserver_check"));

var GAME_SERVER_DICT2 = null;
var getAllGameServerData = function(div_select, tag){
    if (GAME_SERVER_DICT2 == null){
        var success = function(data){
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



get_section($("#section_select"));
var game_server_table;
function get_gameserver () {
    var ajaxSource = "/server/getgameserverpage";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "sTitle": "区服名称"
        },
        {
            "mDataProp": "m_status",
            'sClass': 'center',
            "sTitle": "合服"
        },
        {
            "mDataProp": "gameid",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "extranet_ip",
            'sClass': 'center',
            "sTitle": "IP地址"
        },
        {
            "mDataProp": "ip",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },

        {
            "mDataProp": "extport",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "tag1",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "tag2",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "gmport",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "extgmport",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "path",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "extpath",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "log_path",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "config_path",
            'sClass': 'center',
            "bVisible": false
        },

        {
            "mDataProp": "section",
            'sClass': 'center',
            "sTitle": "分区"
        },
        {
            "mDataProp": "createtime",
            'sClass': 'center',
            "sTitle": "开服时间"
        },
        {
            "mDataProp": "mode",
            'sClass': 'center',
            "sTitle": "启动模式"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_server(this)\" class=\"btn btn-xs default\" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>" +
                "&nbsp;&nbsp;&nbsp;<button onclick=\"del_server(this)\" class=\"btn btn-xs  red-intense\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = '<span class="badge badge-danger">' + aData.gameid + "</span>" + "区:" + aData.name;
        $('td:eq(0)', nRow).html(str_html1);
        var str_temp = "";
        if (aData.m_status == 1){
            str_temp += '<span class="font-green-haze">主</span>';
        }
        else if (aData.m_status == 2){
            str_temp += '<span class="font-blue-madison">副</span>';
        }
        $('td:eq(1)', nRow).html(str_temp);

        var str_html4 = "";
        if (aData.status == "online") {
            str_html4 = '<span class="font-green-haze">在线</span>';
        }
        else if (aData.status == "offline") {
            str_html4 = '<span class="font-red-intense">停机</span>';
        }
        else if (aData.status == "maintain") {
            str_html4 = '<span class="font-red-intense">维护</span>';
        }
        else if (aData.status == "inner"){
            str_html4 = '<span class="font-red-intense">内部</span>';
        }
        else if (aData.status == "fault"){
            str_html4 = '<span class="font-red-intense">缺陷</span>';
        }
        $('td:eq(3)', nRow).html(str_html4);
        var str_html5 = SECTION_DATA[aData.section]["name"] ;
        $('td:eq(4)', nRow).html(str_html5);
        var str_html6 = "";
        if (aData.mode == 5){
            str_html6 = '<span class="font-blue-madison">标准模式</span>';
        }
        else{
            str_html6 = '<span class="font-green-haze">性能模式</span>';
        }
        $('td:eq(6)', nRow).html(str_html6);
        return nRow;
    };
    var data = {
        "status": g_status
    };
    game_server_table = dataTablePage($("#table_game_server"), aoColumns, ajaxSource, data, false, fnRowCallback);
}


var g_status = "";

$("#btn_online").on("click", function(e){
    e.preventDefault();
    g_status = "online";
    change_class($(this));
    get_gameserver();
});
$("#btn_online").click();


$("#btn_offline").on("click", function(e){
    e.preventDefault();
    g_status = "offline";
    change_class($(this));
    get_gameserver();
});


$("#cancel_confirm").on("click", function(e){
    e.preventDefault();
    $("#confirm_modal").modal("hide");
    server_data = {};
});

function confirm_server(){
    var server_id = $("#server_id").val();
    var server_name = $("#server_name").val();
    var server_ip = $("#server_ip").val();
    var intranet_ip = $("#intranet_ip").val();
    var server_port = $("#server_port").val();
    var server_extport = $("#server_extport").val();
    var server_gmport = $("#server_gmport").val();
    var server_extgmport = $("#server_extgmport").val();
    var server_tag1 = $("#server_tag1").val();
    var server_tag2 = $("#server_tag2").val();
    var server_status = $("#server_status").val();
    var server_path = $("#server_path").val();
    var server_extpath = $("#server_extpath").val();
    var log_path = $("#log_path").val();
    var config_path = $("#config_path").val();
    var section = $("#section_select").val();
    var server_desc = $("#server_desc").val();
    var create_date = $("#create_date").val();
    var create_time = $("#create_time").val();
    var createdate = create_date + " " + create_time;
    var start_mode = $("#start_mode").val();
    var is_restart_now = $('#is_restart_now').val();
    var send_data = {
        server_id: server_id, server_name: server_name, server_ip: server_ip,
                intranet_ip: intranet_ip, server_port: server_port, server_extport: server_extport,
                server_gmport: server_gmport, server_extgmport: server_extgmport, server_tag1: server_tag1,
                server_tag2: server_tag2, server_status: server_status, server_path: server_path,
                server_extpath: server_extpath, log_path: log_path, config_path: config_path,
                section: section, createdate: createdate, server_desc: server_desc, start_mode: start_mode,
                is_restart_now: is_restart_now
    };
    if (server_id.length == 0) {
        $("#server_modal").modal("hide");
    }
    else {
        $("#confirm_modal").modal("hide");
    }
    var success = function(data){
        if (data.status == 0) {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        game_server_table.ajax.reload(null, false);
        getGameServerData($("#select_server"), 1);

    };
    my_ajax(true, "/server/operategame", "get", send_data, true, success);
}

$("#button_confirm").on("click", function(e){
    e.preventDefault();
    confirm_server();
    server_data = {};
});

var Server = function () {
    jQuery.validator.addMethod("ip", function (value, element) {
        var ip = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return this.optional(element) || (ip.test(value) && (RegExp.$1 < 256 && RegExp.$2 < 256 && RegExp.$3 < 256 && RegExp.$4 < 256));
    }, "IP地址格式错误");

    var serverValidation = function () {
        var form1 = $('#server_form');
        var rules = {
            server_name: {
                required: true
            },
            server_ip: {
                required: true
            },
            intranet_ip: {
                ip: true,
                required: true
            },
            server_port: {
                required: true,
                digits: true
            },
            server_extport: {
                required: true,
                digits: true
            },
            server_gmport: {
                required: true,
                digits: true
            },
            server_extgmport: {
                required: true,
                digits: true
            },
            server_tag1: {
                required: true
            },
            server_tag2: {
                required: true
            },
            server_status: {
                required: true
            },
            server_path: {
                required: true
            },
            server_extpath: {
                required: true
            },
            section_select: {
                required: true
            },
            log_path: {
                required: true
            }
        };
        var messages = {
            server_name: {
                required: "请输入区服名称."
            },
            server_ip: {
                required: "请输入IP或者域名."
            },
            intranet_ip: {
                required: "请输入IP地址.",
                ip: "请输入正确的IP地址"
            },
            server_port: {
                required: "请输入端口",
                digits: "请输入数字"
            },
            server_extport: {
                required: "请输入端口",
                digits: "请输入数字"
            },
            server_gmport: {
                required: "请输入端口",
                digits: "请输入数字"
            },
            server_extgmport: {
                required: "请输入端口",
                digits: "请输入数字"
            },
            server_tag1: {
                required: "请选择类型1."
            },
            server_tag2: {
                required: "请选择类型2"
            },
            server_status: {
                required: "请选择状态"
            },
            server_path: {
                required: "请输入代码路径"
            },
            server_extpath: {
                required: "请输入扩展代码路径"
            },
            section_select: {
                required: "请选择分区"
            },
            log_path: {
                required: "请输入日志路径"
            }
        };

        var submitFunc = function () {
            var server_id = $("#server_id").val();
            if (server_id.length != 0){
                $("#server_modal").modal("hide");
                var str_html = "";
                var server_name = $("#server_name").val();
                var server_ip = $("#server_ip").val();
                var intranet_ip = $("#intranet_ip").val();
                var server_port = $("#server_port").val();
                var server_extport = $("#server_extport").val();
                var server_gmport = $("#server_gmport").val();
                var server_extgmport = $("#server_extgmport").val();
                var server_tag2 = $("#server_tag2").val();
                var server_status = $("#server_status").val();
                var section_select = $("#section_select").val();
                var create_date = $("#create_date").val();
                var create_time = $("#create_time").val();
                var createdate = create_date + " " + create_time;
                var start_mode = $("#start_mode").val();
                var is_restart_now = $("#is_restart_now").val();
                if (server_name != server_data["name"]){
                    str_html += "<p>" + server_id + "区服名称:" + server_data["name"] + "=>" + "<span class='font-red-intense'>" + server_name + "</span><p/>";
                }
                if (server_ip != server_data["ip"]){
                    str_html += "<p>" + "外网IP:" + server_data["ip"] + "=>" + "<span class='font-red-intense'>" + server_ip + "</span><p/>";
                }
                if (intranet_ip != server_data["intranet_ip"]){
                    str_html += "<p>" + "内网IP:" + server_data["intranet_ip"] + "=>" + "<span class='font-red-intense'>" + intranet_ip  + "</span><p/>";
                }
                if (server_port != server_data["port"]){
                    str_html += "<p>" + "游戏端口:" + server_data["port"] + "=>" + "<span class='font-red-intense'>" + server_port  + "</span><p/>";
                }
                if (server_extport != server_data["extport"]){
                    str_html += "<p>" + "扩展端口:" + server_data["extport"] + "=>" + "<span class='font-red-intense'>" + server_extport  + "</span><p/>";
                }
                if (server_gmport != server_data["gmport"]){
                    str_html += "<p>" + "游戏GM端口:" + server_data["gmport"] + "=>" + "<span class='font-red-intense'>" + server_port  + "</span><p/>";
                }
                if (server_extgmport != server_data["extgmport"]){
                    str_html += "<p>" + "扩展GM端口:" + server_data["extgmport"] + "=>" + "<span class='font-red-intense'>" + server_extgmport  + "</span><p/>";
                }
                if (server_tag2 != server_data["tag2"]){
                    str_html += "<p>" + "类型2:" + server_data["tag2"] + "=>" + "<span class='font-red-intense'>" + server_tag2 + "</span><p/>";
                }
                if (server_status != server_data["status"]){
                    str_html += "<p>" + "状态:" + server_data["status"] + "=>" + "<span class='font-red-intense'>" + server_status + "</span><p/>";
                }
                if (section_select != server_data["section"]){
                    str_html += "<p>" + "分区:" + SECTION_DATA[server_data["section"]]["name"] + "=>" + "<span class='font-red-intense'>" + SECTION_DATA[section_select]["name"] + "</span><p/>";
                }
                if (createdate != server_data["createtime"]){
                    str_html += "<p>" + "开服时间:" + server_data["createtime"] + "=>" + "<span class='font-red-intense'>" + createdate + "</span><p/>";
                }
                if (start_mode != server_data["mode"]){
                    str_html += "<p>" + "启动模式:" + START_MODE_DICT[server_data["mode"]] + "=>" + "<span class='font-red-intense'>" + START_MODE_DICT[start_mode] + "</span><p/>";
                }
                $("#update_info").html(str_html);
                $("#confirm_modal").modal("show");
            }
            else{
                confirm_server();
            }
        };
        commonValidation(form1, rules, messages, submitFunc);
    };

    var databaseValidation = function () {
        var form1 = $('#database_form');
        var rules = {
            database_name: {
                required: true
            },
            database_user: {
                required: true
            }
        };
        var messages = {
            database_name: {
                required: "请输入数据库名."
            },
            database_user: {
                required: "请输入数据库用户名."
            }
        };

        var submitFunction = function (form) {
            var server_id = $("#select_server").val();
            var base_port = $("#base_port").val();
            var database = $("#database_name").val();
            var user = $("#database_user").val();
            var password = $("#database_password").val();
            var desc = $("#database_desc").val();
            var success = function (data) {
                if (data.status == "fail") {
                    Common.alert_message($("#error_modal"), 0, "添加失败.");
                }
                else if (data.status == "fail2"){
                    Common.alert_message($("#error_modal"), 0, "无法连接数据库.");
                }
                $("#database_modal").modal("hide");
                databases_table.ajax.reload( null, false );
            };
            
            var data = {
                        server_id: server_id, base_port: base_port,
                        database: database, user: user, password: password, desc: desc
            };
            my_ajax(true, "/database/operatebase", 'get', data, true, success);
        };
        commonValidation(form1, rules, messages, submitFunction);
    };
    
    serverValidation();
    databaseValidation();
}();

var databases_table;
$("#a_gamebase").on("click", function () {
    var ajax_source = '/database/getgamebase';
    var aoColumns = [
        {
            "mDataProp": "server",
            'sClass': 'center',
            "sTitle": "所属区服"
        },
        {
            "mDataProp": "database",
            'sClass': 'center',
            "sTitle": "数据库名"
        },
        {
            "mDataProp": "user",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "password",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_gamebase(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_gamebase(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_info = aData.server + "区:" + aData.name;
        $('td:eq(0)', nRow).html(str_info);
        return nRow;
    };
    databases_table = dataTablePage($("#table_database"), aoColumns, ajax_source, {}, false, fnRowCallback);
});


$("#server_add").bind("click", function (e) {
    e.preventDefault();
    $sync_create_time.attr('disabled', 'disabled');
    $("#server_id").val("");
    $("#server_title").html("");
    $("#server_name").val("");
    $("#server_ip").val("");
    $("#intranet_ip").val("");
    $('#server_port').val("");
    $('#server_extport').val("");
    $('#server_gmport').val("");
    $("#server_extgmport").val("");
    $("#server_desc").val("");
    $("#server_path").val("");
    $("#server_extpath").val("");
    $("#log_path").val("");
    $("#config_path").val("");
    $("#section_select").val("0");
    $("#server_modal").modal("show");
});

$("#database_add").bind("click", function (e) {
    e.preventDefault();
    $('#base_port').val("");
    $("#database_name").val("");
    $("#database_desc").val("");
    $("#database_modal").modal("show");
});

var mod_gamebase = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_database").dataTable().fnGetData(nRoW);
    $("#select_server").val(data["server"]);
    $('#base_port').val(data["port"]);
    $("#database_name").val(data["database"]);
    $("#database_user").val(data["user"]);
    $("#database_password").val(data["password"]);
    $("#database_desc").val(data["desc"]);
    $("#database_modal").modal("show");
};


var del_gamebase = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_database").dataTable().fnGetData(nRoW);
    $("#confirm_del_base").attr('onclick', "confirm_del_gamebase(" + data["server"] + ")");
    $("#base_del_modal").modal("show");
};

function confirm_del_gamebase(base_id) {
    var success = function(data){
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $("#base_del_modal").modal("hide");
        databases_table.ajax.reload(null, false);
    };
    var req_data = {
        base_id: base_id
    };
    my_ajax(true, "/database/deletebase", 'get', req_data, true, success);
}


var del_server = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_game_server").dataTable().fnGetData(nRoW);
    $('#server_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_server(" + data["gameid"] + ")");
};

var confirm_del_server = function (server_id) {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#server_del_modal').modal("hide");
        game_server_table.ajax.reload(null, false);
    };
    var data = {
        server_id: server_id
    };
    my_ajax(true, "/server/deleteserver", 'get', data, true, success);
};

function mod_server(btn) {
    $sync_create_time.attr('disabled', 'disabled');
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_game_server").dataTable().fnGetData(nRoW);
    $("#server_id").val(data["gameid"]);
    $("#server_name").val(data["name"]);
    server_data["name"] = data["name"];
    $("#server_title").html(data["gameid"] + "区:" + data["name"]);
    $("#server_ip").val(data["extranet_ip"]);
    server_data["ip"] = data["extranet_ip"];
    $("#intranet_ip").val(data["ip"]);
    server_data["intranet_ip"] = data["ip"];
    $("#server_port").val(data["port"]);
    server_data["port"] = data["port"].toString();
    $("#server_extport").val(data["extport"]);
    server_data["extport"] = data["extport"].toString();
    $("#server_gmport").val(data["gmport"]);
    server_data["gmport"] = data["gmport"].toString();
    $("#server_extgmport").val(data["extgmport"]);
    server_data["extgmport"] = data["extgmport"].toString();
    $("#server_path").val(data["path"]);
    $("#server_extpath").val(data["extpath"]);
    $("#log_path").val(data["log_path"]);
    $("#config_path").val(data["config_path"]);
    $("#section_select").val(data["section"]);
    server_data["section"] = data["section"];
    $("#server_desc").val(data["description"]);
    $("#server_tag1").val(data["tag1"]);
    $("#server_tag2").val(data["tag2"]);
    server_data["tag2"] = data["tag2"];
    $("#server_status").val(data["status"]);
    server_data["status"] = data["status"];
    var createtime = data["createtime"];
    var create_split = createtime.split(" ");
    $("#create_date").val(create_split[0]);
    $("#create_time").val(create_split[1]);
    server_data["createtime"] = data["createtime"];
    $("#start_mode").val(data["mode"]);
    server_data["mode"] = data["mode"];
    $("#server_modal").modal("show");

    $.ajax({
        url: '/put/games/time',
        type: 'GET',
        dataType: 'json',
        data: {'server_id': $("#server_id").val()},
        success: function (result) {
            if (result['status'] === 'success' &&  result['value'] !== createtime){
                 $sync_create_time.removeAttr('disabled');
            }

        }

    })

}



// var commandValidation = function () {
//     var rules = {
//         command_name: {
//             required: true
//         },
//         command_value: {
//             required: true
//         }
//     };
//
//     var messages = {
//         command_name: {
//             required: "请输入命令名称"
//         },
//         command_value: {
//             required: "请输入命令行"
//         }
//     };
//
//     var submitHandler = function (form) {
//         var command_name = $("#command_name").val();
//         var command_value = $("#command_value").val();
//         var command_param = $("#command_param").val();
//         $.ajax({
//                 type: 'get',
//                 url: '/addcommand',
//                 data: {
//                     server_id: 0,
//                     command_name: command_name,
//                     command_value: command_value,
//                     command_param: command_param
//                 },
//                 dataType: 'JSON',
//                 success: function (data) {
//                     if (data["status"] == false) {
//                         Common.alert_message($("#error_modal"), 0, "操作失败.");
//                     }
//                     $("#command_modal").modal("hide");
//                     $("#a_command").click();
//                 },
//                 error: function (XMLHttpRequest) {
//                     error_func(XMLHttpRequest);
//                 }
//             }
//         )
//     };
//     commonValidation($("#command_form"), rules, messages, submitHandler);
// };
//
// commandValidation();


// $("#a_command").on("click", function (e) {
//     e.preventDefault();
//     var page_content = $('.page-content');
//     App.blockUI(page_content, false);
//     $.ajax({
//             type: 'get',
//             url: '/getcommand',
//             data: {
//                 server_id: 0
//             },
//             dataType: 'JSON',
//             success: function (data) {
//                 App.unblockUI(page_content);
//                 var str_info = "";
//                 for (var i = 0; i < data.length; i++) {
//                     str_info += "<tr>";
//                     str_info += "<td>" + data[i]["name"] + "</td>";
//                     str_info += "<td>" + data[i]["command"] + "</div></td>";
//                     str_info += "<td ondblclick='tdClick(" + data[i]["id"] + ");'><div id='div_param_" + data[i]["id"] + "'>" + data[i]["param"] + "</div></td>";
//                     str_info += "<td><button  onclick=\"runcommand('" + data[i]["id"] + "')\" class=\"btn btn-xs blue\">执行</button></td>";
//                     str_info += "</tr>";
//                 }
//                 $("#command_list").html(str_info);
//             },
//             error: function (XMLHttpRequest) {
//                 App.unblockUI(page_content);
//                 error_func(XMLHttpRequest);
//             }
//         }
//     )
// });

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
    var success = function(data){
        Common.alert_message($("#error_modal"), 1, JSON.stringify(data));
    };
    var data = {
        cid: cid,
        param: param,
        tag: 0
    };
    my_ajax(true, "/runcommand", 'get', data, true, success);
}

function runcommand2(param, param2){
    var success = function(data){
        Common.alert_message($("#error_modal"), 1, JSON.stringify(data));
    };
    var data = {
        server_id: 0,
                param: param,
                param2: param2
    };
    my_ajax(true, "/runcommand2", 'get', data, true, success);
}

create_del_modal($("#refreshserver_modal"), "是否刷新服务器列表?", "confirm_refresh");


$("#btn_refreshserver").on("click", function(e){
    e.preventDefault();
    $("#refreshserver_modal").modal("show");
    $("#confirm_refresh").attr("onclick", "runcommand2('gm/refreshserver', '')");
});

$("#btn_refreshserver2").on("click", function(e){
    e.preventDefault();
    $("#refreshserver_modal").modal("show");
    $("#confirm_refresh").attr("onclick", "runcommand2('gm/refreshserver', '')");
});

$("#btn_updatesection").on("click", function(e){
    e.preventDefault();
    $("#updatesection_modal").modal("show");
});

var updateSectionValidation = function () {
    var rules = {
        section_id: {
            required: true,
            digits: true
        }
    };

    var messages = {
        section_id: {
            required: "请输入分区编号",
            digits: "请输入数字."
        }
    };

    var submitHandler = function (form) {
        var section_id = $("#section_id").val();
        var section_str = "section=" + section_id;
        runcommand2("config/updateSection", section_str);
        $("#updatesection_modal").modal("hide");
    };
    commonValidation($("#updatesection_form"), rules, messages, submitHandler);
};

updateSectionValidation();


var mergeValidation = function () {
    var rules = {
    };

    var messages = {
    };

    var submitHandler = function (form) {
        var select_mid = $("#select_mid").val();
        var merge_tag = $("#merge_tag").val();
        var oid_list = [];
        $("input[name='oid_list']").each(function(e){
            var oid_value = $(this).val();
            if (oid_value.length > 0 && !isNaN(oid_value)){
                oid_list.push($(this).val());
            }
        });
        var data = {
            merge_tag: merge_tag,
            "mid": select_mid,
            "oid_list": JSON.stringify(oid_list)
        };
        var success = function(data){
            if (data["status"] == "fail"){
                Common.alert_message($("error_modal"), 0, "处理错误");
            }
            $("#merge_modal").modal("hide");
            $("#a_merge_server").click();
        };
        my_ajax(true, "/operatemergeserver", 'get', data, true, success);
    };
    commonValidation($("#merge_form"), rules, messages, submitHandler);
};

mergeValidation();

var i = 1;
$("#btn_add").on("click", function (e) {
    e.preventDefault();
    var str_id = "merge_oid_" + i;
    var s = $("#" + str_id);
    var html_str = "";
    html_str += "<label class='control-label col-md-3'>副区服" + (i+1) + "<span class='required'> </span></label>";
    html_str += "<div class='col-md-3'>";
    html_str += "<div class='input-icon'>";
    html_str += "<i class='fa fa-user'></i>";
    html_str += "<input class='form-control' name='oid_list' placeholder='' type='text'/>";
    html_str += "</div>";
    html_str += "</div>";
    i += 1;
    var next_str_id = "merge_oid_" + i;
    s.after("<div class=\"form-group\" id=" + next_str_id + "></div>");
    $("#" + next_str_id).html(html_str);
});

$("#add_merge").on("click", function(e){
    e.preventDefault();
    var str_id = "merge_oid_" + 1;
    var s = $("#" + str_id);
    $("input[name='oid_list']").val("");
    s.nextAll().remove();
    i = 1;
    $("#merge_tag").val("0");
    $("#merge_modal").modal("show");
});

$("#a_merge_server").on("click", function(e){
    e.preventDefault();
    var success = function(data){
        var html_title = "";
        var html = "";
        var len = 0;
        for(var s=0; s < data.length; s++){
            var data_length = data[s].length;
            if (data_length > len){
                len = data_length;
            }
        }

        for(var m=0; m < data.length; m++){
            html += "<tr>";
            for(var n=0; n<data[m].length; n++){
                html += "<td>" + data[m][n] + "区:"
                if (GAME_SERVER_DICT2.hasOwnProperty(data[m][n])){
                    html += GAME_SERVER_DICT2[data[m][n]]["name"]
                }
                html += "</td>";
            }
            var s_length = len - data[m].length;

            for(var u=0; u < s_length; u++){
                html += "<td>";
                html += "</td>";
            }
            html += "<td>";
            html += '&nbsp; <a onclick="mod_merge(' + "'" + data[m] + "'" + ')"' + 'class="btn default btn-xs " data-toggle="modal"> <i class="fa fa-edit"></i></a>';
            html += "</td>";
            html += "</tr>";
        }

        for(var j=0; j<len; j++){
            if (j == 0){
                html_title += "<th>主区服</th>";
            }
            else{
                html_title += "<th>" + "副区服" + j + "</th>";
            }
        }
        html_title += "<th>操作</th>";

        $("#merge_title").html(html_title);
        $("#merge_list").html(html);
    };
    my_ajax(true, "/getmergeserver", 'get', {}, true, success);
});


function mod_merge(merge_str){
    $("#merge_tag").val("1");
    var merge_list = merge_str.split(",");
    i = 1;
    var str_id1 = "merge_oid_" + 1;
    var st1 = $("#" + str_id1);
    st1.nextAll().remove();
    for(var s=0; s<merge_list.length; s++){
        if (s == 0){
            $("#select_mid").val(merge_list[s]);
        }
        else{
            var str_id = "merge_oid_" + i;
            var st = $("#" + str_id);
            if (s == 1){
                $("input[name='oid_list']").val(merge_list[s]);
            }
            else{
                var html_str = "";
                html_str += "<label class='control-label col-md-3'>副区服" + (i + 1) + "<span class='required'> </span></label>";
                html_str += "<div class='col-md-3'>";
                html_str += "<div class='input-icon'>";
                html_str += "<i class='fa fa-user'></i>";
                html_str += "<input class='form-control' name='oid_list' placeholder='' value='"  + merge_list[s] + "' type='text'/>";
                html_str += "</div>";
                html_str += "</div>";
                i += 1;
                var next_str_id = "merge_oid_" + i;
                st.after("<div class=\"form-group\" id=" + next_str_id + "></div>");
                $("#" + next_str_id).html(html_str);
            }
        }
    }
    $("#merge_modal").modal("show");
}


$("#open_add").on("click", function (e) {
    e.preventDefault();
    $("#openserver_modal").modal("show");
});


var open_server_table;
function get_openserver () {
    var ajaxSource = "/openserver/getopenserver";
    var aoColumns = [
        {
            "mDataProp": "gid",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "opentime",
            'sClass': 'center',
            "sTitle": "开服时间"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "result",
            'sClass': 'center',
            "sTitle": "结果"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_openserver(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_openserver(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 =  aData.gid + "区:" + aData.name;
        $('td:eq(0)', nRow).html(str_html1);

        var str_html2 = "";
        if (aData.status == "prepare") {
            str_html2 = '<span class="badge badge-success">准备</span>';
        }
        else{
            str_html2 = '<span class="badge badge-info">执行</span>';
        }
        $('td:eq(2)', nRow).html(str_html2);

        var str_html3 = "";
        if (aData.result == "success") {
            str_html3 = '<span class="badge badge-success">成功</span>';
        }
        else if (aData.result == "fail"){
            str_html3 = '<span class="badge badge-danger">失败</span>';
        }
        else{
            str_html3 = '<span class="badge badge-danger">未执行</span>';
        }
        $('td:eq(3)', nRow).html(str_html3);
        return nRow;
    };
    open_server_table = dataTablePage($("#table_openserver"), aoColumns, ajaxSource, {}, false, fnRowCallback);
}


$("#a_openserver").on("click", function(e){
    e.preventDefault();
    get_openserver();
});


var mod_openserver = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_openserver").dataTable().fnGetData(nRoW);
    $("#select_openserver").val(data["gid"]);
    $("#open_status").val(data["status"]);
    var opentime = data["opentime"];
    $open_datetime.val(opentime);
    // var opentime_split = opentime.split(" ");
    // $("#open_date").val(opentime_split[0]);
    // $("#open_time").val(opentime_split[1]);
    $("#openserver_modal").modal("show");
};

var del_openserver = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_openserver").dataTable().fnGetData(nRoW);
    $('#del_openserver_modal').modal("show");
    $("#del_open_confirm").attr('onclick', "confirm_del_openserver(" + data["gid"] + ")");
};

var confirm_del_openserver = function (gid) {
    var success = function(data){
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#del_openserver_modal').modal("hide");
        open_server_table.ajax.reload(null, false);
    };
    var data = {
        gid: gid
    };
    my_ajax(true, '/openserver/delete', 'get', data, true, success);
};


var openserverValidation = function () {
    var form1 = $('#openserver_form');
    var rules = {
    };
    var messages = {
    };

    var submitFunction = function (form) {
        var gid = $("#select_openserver").val();
        // var open_date = $("#open_date").val();
        // var open_time = $("#open_time").val();
        var open_time2 = $open_datetime.val();
        var open_status = $("#open_status").val();
        var success = function (data) {
            if (data.status == 'fail') {
                Common.alert_message($("#error_modal"), 0, "操作失败.")
            }
            $("#openserver_modal").modal("hide");
            open_server_table.ajax.reload( null, false );
        };
        var data = {
            gid: gid,
            open_time: open_time2,
            status: open_status
        };
        my_ajax(true, '/openserver/operate', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};
openserverValidation();


//定时重启服务

$("#select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='restartserver_check']").prop("checked", true);
    $("input[name='restartserver_check']").parent("span").addClass("checked");
});


$("#no_select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='restartserver_check']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});


function get_restart_server(){
    var ajaxSource = "/restart/getrestartserver";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "gid_list",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "restarttime",
            'sClass': 'center',
            "sTitle": "重启时间"
        },
        {
            "mDataProp": "game",
            'sClass': 'center',
            "sTitle": "服务"
        },
        {
            "mDataProp": "ext",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "result",
            'sClass': 'center',
            "sTitle": "结果"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_restartserver(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_restartserver(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var gid_list = aData["gid_list"].split(",");
        var str_html1 = "";
        for(var i=0; i<gid_list.length; i++){
            str_html1 +=  gid_list[i] + "区:" + GAME_SERVER_DICT2[gid_list[i]]["name"];
        }
        $('td:eq(0)', nRow).html(str_html1);

        var str_html2 = "";
        if (aData.game == 1) {
            str_html2 += '<span class="font-green-haze">游戏服务、</span>';
        }
        if (aData.ext == 1){
            str_html2 += '<span class="font-green-haze">扩展服务</span>';
        }
        $('td:eq(2)', nRow).html(str_html2);

        var str_html3 = "";
        if (aData.status == "prepare") {
            str_html3 = '<span class="font-blue-madison">准备</span>';
        }
        else{
            str_html3 = '<span class="font-green-haze">执行</span>';
        }
        $('td:eq(3)', nRow).html(str_html3);

        var str_html4 = "";
        if (aData.result == "success") {
            str_html4 = '<span class="font-green-haze">成功</span>';
        }
        else if (aData.result == "fail"){
            str_html4 = '<span class="font-red-intense">失败</span>';
        }
        else{
            str_html4 = '<span class="font-red-intense">未执行</span>';
        }
        $('td:eq(4)', nRow).html(str_html4);
        return nRow;
    };
    dataTablePage($("#table_restartserver"), aoColumns, ajaxSource, {}, false, fnRowCallback);
}

$("#a_restartserver").on("click", function(e){
    e.preventDefault();
    get_restart_server();
});


$("#restart_add").on("click", function (e) {
    e.preventDefault();
    $("#restart_id").val("");
    $("#restartserver_modal").modal("show");
});



var restartserverValidation = function () {
    var form1 = $('#restartserver_form');
    var rules = {
    };
    var messages = {
    };

    var submitFunction = function (form) {
        var restart_id = $("#restart_id").val();
        var gid_list = [];

        $("input[name='game_server']:checked").each(function(){
            gid_list.push($(this).val());
        });
        var restart_date = $("#restart_date").val();
        var restart_time = $("#restart_time").val();
        var restart_time2 = restart_date + " " + restart_time;
        var restart_status = $("#restart_status").val();

        var game = 0;
        var ext = 0;
        $("input[name='service_type']:checked").each(function(){
            var st = $(this).val();
            if (st == "1"){
                game = 1;
            }
            else if(st == "2"){
                ext = 1;
            }
        });
        var success = function (data) {
            if (data.status == 'fail') {
                Common.alert_message($("#error_modal"), 0, "操作失败.")
            }
            $("#restartserver_modal").modal("hide");
            $("#a_restartserver").click();
        };
        var data = {
            restart_id: restart_id,
            gid_list: JSON.stringify(gid_list),
            restart_time: restart_time2,
            game: game,
            ext: ext,
            status: restart_status
        };
        my_ajax(true, '/restart/operate', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};
restartserverValidation();


var mod_restartserver = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_restartserver").dataTable().fnGetData(nRoW);
    $("#restart_status").val(data["status"]);
    var restarttime = data["restarttime"];
    var opentime_split = restarttime.split(" ");
    $("#restart_id").val(data["id"]);
    $("#restart_date").val(opentime_split[0]);
    $("#restart_time").val(opentime_split[1]);
    var gid_list = data["gid_list"];
    var split_arr = gid_list.split(",");
    for (var i = 0; i < split_arr.length; i++) {
        if (split_arr[i] != "") {
            var operate_d = $("input[name='game_server'][value='" + split_arr[i] + "']");
            operate_d.prop("checked", true);
            operate_d.parent("span").addClass("checked");
        }
    }
    var game = data["game"];
    var ext = data["ext"];
    if (game == 1){
        var st = $("input[name='service_type'][value='1']");
        st.prop("checked", true);
        st.parent("span").addClass("checked");
    }
    if (ext == 1){
        var st = $("input[name='service_type'][value='2']");
        st.prop("checked", true);
        st.parent("span").addClass("checked");
    }

    $("#restartserver_modal").modal("show");
};

var del_restartserver = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_restartserver").dataTable().fnGetData(nRoW);
    $('#del_restartserver_modal').modal("show");
    $("#del_restart_confirm").attr('onclick', "confirm_del_restartserver(" + data["id"] + ")");
};

var confirm_del_restartserver = function (restart_id) {
    var success = function(data){
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#del_restartserver_modal').modal("hide");
        get_restart_server();
    };
    var data = {
        restart_id: restart_id
    };
    my_ajax(true, '/restart/delete', 'get', data, true, success);
};


var $batch_modal = $('#batch_modal');
var $batch_type = $('#batch_type');
var $batch_target = $('#batch_target');
var $batch_game = $('#batch_game');
var $batch_modal_commit = $('#batch_modal_commit');
var $batch_modal_cue = $('#batch_modal_cue');

var init_batch_target_modal = function () {
    var batch_type_value = $batch_type.val();
    if ( batch_type_value=== '1'){
        init_select_html(false, SERVER_STATUS, $batch_target);
      }else if (batch_type_value === '2'){
        getPartitionData($batch_target);
      }
};

$batch_modal.on('show.bs.modal', function () {
    init_batch_target_modal();
    var batch_game_html = '';
    for (var game in GAME_SERVER_DICT){
        batch_game_html += '<div class="checkbox"><lable><input style="margin-left: 5px;margin-right: 4px" type="checkbox" value="'+game+'">'+game + '区：' + GAME_SERVER_DICT[game]['name']+'</lable></div>'
    }
    $batch_game.html(batch_game_html)

});
$batch_modal.on('hide.bs.modal', function () {
    $batch_modal_commit.show();
  $batch_modal_cue.hide()
});

$batch_type.change(function () {
    init_batch_target_modal()
});

$batch_modal_commit.click(function () {
    var batch_type_value = $batch_type.val();
    var batch_target_value = $batch_target.val();
    var batch_game_list = [];
    $batch_game.find('input:checkbox:checked').each(function () {
        batch_game_list.push($(this).val())
    });

    if (batch_game_list.length === 0 ){
        $batch_modal_cue.text('错误：游戏区服选择不能为空');
        $batch_modal_cue.show()
    }else{
        $batch_modal_commit.hide();
        $batch_modal_cue.show();
        $batch_modal_cue.text('处理中，请稍后。。。');
        $.ajax({
            url: '/post/batch/games',
            type: 'post',
            dataType: 'json',
            data: {type: batch_type_value, target: batch_target_value, game_list: JSON.stringify(batch_game_list)},
            success: function (result) {
                $batch_modal_commit.show();
                if (result.status === 'success'){
                    $batch_modal.modal('hide')
                }else{
                    $batch_modal_cue.text(result.msg);
                }
            },
            error: function () {
                $batch_modal_cue.text('服务器错误');
                $batch_modal_cue.show()
            }

        })
    }
});

var $error_modal = $('#error_modal');
$sync_create_time.click(function () {
    var create_date = $("#create_date").val();
    var create_time = $("#create_time").val();
    var create_time = create_date + " " + create_time;
    my_ajax(true, '/put/games/time', 'post', {'server_id': $("#server_id").val(), 'create_time': create_time}, false, function (result) {
        $("#server_modal").modal("hide");
        if (result['status'] === 'success'){
            Common.alert_message($error_modal, 1, "同步成功");
        }else{
            Common.alert_message($error_modal, 0, "同步失败");
        }
    }, function () {
        $("#server_modal").modal("hide");
    });
});

$("#export_test_sql").on("click", function (e) {
    e.preventDefault();
    var success = function (data) {
        // $(this).attr("href", data["url"]);
        window.location=data["url"]
    };
    my_ajax(true, '/database/exportsql', 'get', {}, true, success, null);
});


$("#server_port").on("blur", function (e) {
    e.preventDefault();
    var server_port = parseInt($(this).val());
    $("#server_extport").val(server_port + 2);
    $("#server_gmport").val(server_port + 1);
    $("#server_extgmport").val(server_port + 3);
});
