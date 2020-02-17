/**
 * Created by wangrui on 15/5/18.
 */
get_left_game_server();
getGameServerData($("#select_gameserver"), 1);
getGameServerData($("#select_gameserver1"), 1);
getGameServerData($("#gameserver_file"), 1);
getGameServerData($("#select_gameserver2"), 1);
getGameServerData($("#select_gameserver3"), 1);

create_del_modal($("#gamelog_del_modal"), "是否删除此游戏日志", "btn_confirm");

handleDatePickers();
handleTimePickers();
$("#q_date").val(getNowFormatDate(1));
$("#error_date").val(getNowFormatDate(1));
$("#error_num_date").val(getNowFormatDate(1));
$("#process_date").val(getNowFormatDate(1));

$("#query_log").on("click", function(e){
    e.preventDefault();
    var ajax_source = "/querygamelog";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "函数名称"
        },
        {
            "mDataProp": "min",
            "sClass": "center",
            "sTitle": "最小回调时间(秒)"
        },
        {
            "mDataProp": "max",
            "sClass": "center",
            "sTitle": "最大回调时间(秒)"
        },
        {
            "mDataProp": "pro",
            'sClass': 'center',
            "sTitle": "回调次数所占比例 %"
        },
        {
            "mDataProp": "num",
            "sTitle": "回调次数",
            "sClass": "center"
        },
        {
            "mDataProp": "ave",
            "sTitle": "平均回调时间(秒)",
            "sClass": "center"
        },
        {
            "mDataProp": "acount",
            "sTitle": "错误次数",
            "sClass": "center"
        }
    ];
    var game_id = $("#select_gameserver").val();
    var q_date = $("#q_date").val();
    var data = {
            game_id: game_id,
            q_date: q_date
    };
    dataTablePage($("#game_log"), aoColumns, ajax_source, data, true);
});


$("#query_error").on("click", function(e){
    e.preventDefault();
    var ajax_source = "/queryerrorgamelog";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色名称"
        },
        {
            "mDataProp": "func",
            "sClass": "center",
            "sTitle": "函数名称"
        },
        {
            "mDataProp": "count",
            'sClass': 'center',
            "sTitle": "次数"
        },
        {
            "mDataProp": "error",
            "sClass": "center",
            "sTitle": "错误信息"
        }
    ];
    var game_id = $("#select_gameserver1").val();
    var q_date = $("#error_date").val();
    var data = {
            game_id: game_id,
            q_date: q_date
    };
    dataTablePage($("#error_log"), aoColumns, ajax_source, data, false);
});


$("#query_error_num").on("click", function(e){
    e.preventDefault();
    var ajax_source = "/queryerrornumgamelog";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色名称"
        },
        {
            "mDataProp": "Error_num",
            "sClass": "center",
            "sTitle": "报错次数"
        },
        {
            "mDataProp": "Abnormal_num",
            'sClass': 'center',
            "sTitle": "异常次数"
        },
        {
            "mDataProp": "total_num",
            "sClass": "center",
            "sTitle": "总出错次数"
        }
    ];
    var game_id = $("#select_gameserver3").val();
    var q_date = $("#error_num_date").val();
    var data = {
            game_id: game_id,
            q_date: q_date
    };
    dataTablePage($("#error_num_log"), aoColumns, ajax_source, data, false);
});



$("#btn_gamefile").on("click", function(e){
    e.preventDefault();
    var gameserver_file = $("#gameserver_file").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querygamelogfile',
        data: {
            server_id: gameserver_file
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0) {
                for (var i=0; i <data.length; i ++) {
                    str_info += "<tr>";
                    str_info += "<td>" + data[i][0] + "</td>";
                    var tag = data[i][1];
                    if (tag == 1){
                        str_info += "<td><span class='badge badge-success'>全服</span></td>";
                    }
                    else if (tag == 2){
                        str_info += "<td><span class='badge badge-success'>角色</span></td>";
                    }
                    else{
                        str_info += "<td><span class='badge badge-danger'>未处理</span></td>";
                    }
                    str_info += "<td>";
                    str_info += '&nbsp; <a onclick="del_gamelog(\'' + data[i][0] + '\')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                    str_info += '&nbsp; <a onclick="process_game(\'' + data[i][0] + '\')"' + 'class="btn default btn-xs blue" data-toggle="modal">处理 <i class="fa fa-arrow-right"></i></a>';
                    str_info += "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#gamefile_log").html(str_info);
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

var process_game = function(file_name){
    $("#role_id").val("");
    $("#btn_process").attr('onclick', "process_game_log('" + file_name + "')");
    $("#gamelog_process_modal").modal("show");
};

$("#select_type").on("change", function(e){
    e.preventDefault();
    var select_type = $("#select_type").val();
    if (select_type == "1"){
        $("#div_role").removeClass("hide");
    }
    else{
        $("#div_role").addClass("hide");
    }
});

var process_game_log = function(file_name){
    var gameserver_file = $("#gameserver_file").val();
    var role_id = 0;
    var select_type = $("#select_type").val();
    if (select_type == "1"){
        var role = $("#role_id").val();
        if (role.length == 0){
            Common.alert_message($("#error_modal"), 0, "角色ID不能为空.");
            return;
        }
        role_id = role;
    }
    else{
        role_id = select_type;
    }
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $("#gamelog_process_modal").modal("hide");
    $.ajax({
        type: 'get',
        url: '/processgamelogfile',
        data: {
            server_id: gameserver_file,
            file_name: file_name,
            role_id: role_id
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            if (data["status"] == true){
                Common.alert_message($("#error_modal"), 1, "处理成功");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "处理失败");
            }

            $("#a_gamefile").click();
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
};

var del_gamelog = function(file){
    $("#gamelog_del_modal").modal("show");
    $("#btn_confirm").attr('onclick', "confirm_del_gamelog(\"" + file + "\")");
};

var confirm_del_gamelog = function(file_name){
    var gameserver_file = $("#gameserver_file").val();
    $.ajax({
        type: 'get',
        url: '/deletegamelogfile',
        data: {
            server_id: gameserver_file,
            file_name: file_name
        },
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == 1){
                $("#gamelog_del_modal").modal("hide");
                $("#btn_gamefile").click();
            }
        },
        error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
    })
};

$("#btn_process_query").on("click", function(e){
    e.preventDefault();
    var ajax_source = "/queryprocessgamelog";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "func",
            "sClass": "center",
            "sTitle": "函数名称"
        },
        {
            "mDataProp": "otime",
            "sClass": "center",
            "sTitle": "时间"
        },
        {
            "mDataProp": "time_count",
            'sClass': 'center',
            "sTitle": "回调时间"
        }
    ];
    var process_date = $("#process_date").val();
    var server_id = $("#select_gameserver2").val();
    var role_id = $("#process_role_id").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    var process_func = $("#process_func").val();
    var data = {
            q_date: process_date,
            server_id: server_id,
            start_time: start_time,
            end_time: end_time,
            process_func: process_func,
            role_id: role_id
    };
    dataTablePage($("#process_log"), aoColumns, ajax_source, data, true);
});

$("#query_log").click();

$("#a_error_gamelog").on("click", function(e){
    e.preventDefault();
    $("#query_error").click();
});

$("#a_error_num_gamelog").on("click", function(e){
    e.preventDefault();
    $("#query_error_num").click();
});

$("#a_gamefile").on("click", function(e){
    e.preventDefault();
    $("#btn_gamefile").click();
});

//$("#a_gamefile_process").on("click", function(e){
//    e.preventDefault();
//    $("#btn_process_query").click();
//});