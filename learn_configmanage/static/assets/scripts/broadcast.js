/**
 * Created by wangrui on 15/9/7.
 */

var broadcast_TYPE = {
    "5M": "5分钟",
    "10M": "10分钟",
    "20M": "20分钟",
    "30M": "30分钟",
    "60M": "1小时"
};

var init_broadcast = function(){
    var html = "";
    for(var b in broadcast_TYPE){
        html += "<option value='"  + b + "'>" + broadcast_TYPE[b] + "</option>";
    }
    $("#broadcast_type").html(html);
};
init_broadcast();

getGameServerData($("#select_server"), 2);
getGameServerData($("#select_server_query"), 2);
create_del_modal($("#broadcast_del_modal"), "是否删除此公告?", "confirm_del");

handleDatePickers2();
$("#end_date").val(getNowFormatDate(-7));


$("#add_broadcast").on("click", function(e){
    e.preventDefault();
    $("#broadcast_id").val("");
    $("#broadcast_name").val("系统");
    $("#broadcast_content").val("");
    $("#broadcast_count").val("1");
    $("#broadcast_time").val("");
    $("#broadcast_modal").modal("show");
});

var broadcastValidation = function () {
    var form1 = $('#broadcast_form');
    var rules = {
        broadcast_name: {
            required: true
        },
        broadcast_content: {
            required: true
        },
        broadcast_count: {
            required: true,
            digits: true
        },
        broadcast_time: {
            required: true,
            digits: true
        }
    };
    var messages = {
        broadcast_name: {
            required: "请输入角色"
        },
        broadcast_content: {
            required: "请输入广播内容"
        },
        broadcast_count: {
            required: "请输入次数",
            digits: "请输入数字"
        },
        broadcast_time: {
            required: "请输入广播持续时间",
            digits: "请输入数字"
        }
    };
    var submitFunction = function (form) {
        var broadcast_id = $("#broadcast_id").val();
        var broadcast_name = $("#broadcast_name").val();
        var broadcast_content = $("#broadcast_content").val();
        var broadcast_count = $("#broadcast_count").val();
        var server_id = $("#select_server").val();
        var broadcast_type = $("#broadcast_type").val();
        var end_date = $("#end_date").val();
        $.ajax({
                type: 'get',
                url: '/operatebroadcast',
                data: {
                    broadcast_id: broadcast_id,
                    server_id: server_id,
                    broadcast_name: broadcast_name,
                    broadcast_content: broadcast_content,
                    broadcast_count: broadcast_count,
                    broadcast_type: broadcast_type,
                    end_date: end_date
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data.status == false) {
                        Common.alert_message($("#error_modal"), 0, "操作失败.")
                    }
                    $("#broadcast_modal").modal("hide");
                    $("#select_server_query").change();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunction);
};

broadcastValidation();

$("#select_server_query").on("change", function(e){
    e.preventDefault();
    var ajax_source = "/querybroadcast";
    var server_id = $("#select_server_query").val();
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "server",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "person",
            "sClass": "center",
            "sTitle": "角色"
        },
        {
            "mDataProp": "content",
            "sClass": "center",
            "sTitle": "广播内容"
        },
        {
            "mDataProp": "type",
            "sClass": "center",
            "sTitle": "广播频率"
        },
        {
            "mDataProp": "count",
            "sClass": "center",
            "sTitle": "次数"
        },
        {
            "mDataProp": "createtime",
            "sClass": "center",
            "sTitle": "创建时间"
        },
        {
            "mDataProp": "durationtime",
            "sClass": "center",
            "sTitle": "结束时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_broadcast(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_broadcast(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function(nRow, aData){
//        var str_server = "";
//        if (aData.server == "0"){
//            str_server += "全服";
//        }
//        else{
//            str_server = aData.server + "区:" + GAME_SERVER_DICT[aData.server]["name"];
//        }
//        $('td:eq(0)', nRow).html(str_server);
        var str_html = broadcast_TYPE[aData.type];
        $('td:eq(2)', nRow).html(str_html);
    };
    var data = {
        server_id: server_id
    };

    dataTablePage($("#broadcast_table"), aoColumns, ajax_source, data, false, fnRowCallback);
});
$("#select_server_query").change();


var mod_broadcast = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#broadcast_table").dataTable().fnGetData(nRoW);
    $("#broadcast_id").val(data["id"]);
    $("#select_server").val(data["server"]);
    $("#broadcast_name").val(data["person"]);
    $("#broadcast_content").val(data["content"]);
    $("#broadcast_type").val(data["type"]);
    $("#broadcast_count").val(data["count"]);
    $("#broadcast_time").val(data["duration"]);
    $("#broadcast_modal").modal("show");
};

var del_broadcast = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#broadcast_table").dataTable().fnGetData(nRoW);
    $("#confirm_del").attr('onclick', "confirm_del_broadcast(" + data["id"] + ")");
    $("#broadcast_del_modal").modal("show");
};

var confirm_del_broadcast = function(nid){
    $.ajax({
            type: 'get',
            url: '/deletebroadcast2',
            data: {
                notice_id: nid
            },
            dataType: 'JSON',
            success: function (data) {
                if (data.status == false) {
                    Common.alert_message($("#error_modal"), 0, "删除失败.")
                }
                $("#broadcast_del_modal").modal("hide");
                $("#select_server_query").change();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};