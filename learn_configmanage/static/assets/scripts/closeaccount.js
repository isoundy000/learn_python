/**
 * Created by wangrui on 15/9/7.
 */

var SEAL_TYPE = {
    1: "一天",
    2: "七天",
    3: "一个月",
    4: "永久"
};

var init_seal_type = function(){
    var str_html = "";
    for (var s in SEAL_TYPE) {
        str_html += "<option value='" + s +  "'>" + SEAL_TYPE[s] + "</option>";
    }
    $("#close_type").html(str_html);
}();

getGameServerData($("#select_server"), 1);

$("#select_server").on("change", function(e){
    e.preventDefault();
    $("#nav_div").children().each(function(e){
        if ($(this).hasClass("active")){
            $(this).find("a").click();
        }
    })
});

create_del_modal($("#del_modal"), "是否解封此用户?", "confirm_del");

$("#add_close").on("click", function(e){
    e.preventDefault();
    $("#close_id").val("");
    $("#close_role").val("");
    $("#close_modal").modal("show");
});

$("#add_gag").on("click", function(e){
    e.preventDefault();
    $("#role_id").val("");
    $("#gag_num").val("");
    $("#gag_type").val("");
    $("#gag_modal").modal("show");
});

var gagValidation = function () {
    var rules = {
        role_id: {
            required: true,
            digits: true
        },
        gag_type: {
            required: true
        }
    };
    var messages = {
        role_id: {
            required: "请输入角色编号",
            digits: "请输入整数"
        },
        gag_type: {
            required: "请选择类型"
        }
    };
    var submitHandler1 = function (form) {
        var role_id = $("#role_id").val();
        var gag_type = $("#gag_type").val();
        var gag_num = $("#gag_num").val();
        var server_id = $("#select_server").val();
        $.ajax({
                type: 'get',
                url: '/addgag',
                data: {
                    server_id: server_id,
                    role_id: role_id,
                    gag_type: gag_type,
                    gag_num: gag_num
                },
                dataType: 'JSON',
                success: function (data) {
                    $("#gag_modal").modal("hide");
                    if (data.status == 0) {
                        Common.alert_message($("#error_modal"), 0, "操作失败.");
                    }
                    $("#a_gag").click();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation($("#gag_form"), rules, messages, submitHandler1);
};
gagValidation();

var closeValidation = function () {
    var form1 = $('#close_form');
    var rules = {
        close_role: {
            required: true,
            digits: true
        }
    };
    var messages = {
        close_role: {
            required: "请输入角色",
            digits: "请输入数字"
        }
    };
    var submitFunction = function (form) {
        var close_id = $("#close_id").val();
        var server_id = $("#select_server").val();
        var close_role = $("#close_role").val();
        var close_type = $("#close_type").val();
        $.ajax({
                type: 'get',
                url: '/operateseal',
                data: {
                    close_id: close_id,
                    server_id: server_id,
                    close_role: close_role,
                    close_type: close_type
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data.status == false) {
                        Common.alert_message($("#error_modal"), 0, "操作失败.")
                    }
                    $("#close_modal").modal("hide");
                    $("#a_closeaccount").click();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunction);
};
closeValidation();

$("#a_gag").on("click", function(){
    var server_id = $("#select_server").val();
    var ajax_source = "/querygag";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色"
        },
        {
            "mDataProp": "type",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "server",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "gagnum",
            "sClass": "center",
            "sTitle": "类型"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"enable_gag(this)\" class=\"btn default btn-xs purple\" data-toggle=\"modal\">恢复 <i class=\"fa fa-refresh\"></i></button>"
        }
    ];
    var fnRowCallback = function(nRow, aData){
        var gag_html = "";
        if (aData.type == "hour") {
            gag_html += aData.gagnum + '小时';
        }
        else if (aData.type == "day") {
            gag_html += aData.gagnum + "天";
        }
        else {
            gag_html += "永久";
        }
        $('td:eq(1)', nRow).html(gag_html);
    };
    var data = {
        server_id: server_id
    };
    dataTablePage($("#gag_table"), aoColumns, ajax_source, data, true, fnRowCallback);
});

$("#a_gag").click();

function enable_gag(btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#gag_table").dataTable().fnGetData(nRoW);
    var server_id = data.server;
    var rid = data.rid;
    $.ajax({
            type: 'get',
            url: '/enablechat',
            data: {server_id: server_id, rid: rid},
            dataType: 'JSON',
            success: function (data) {
                $("#a_gag").click();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
}

$("#a_closeaccount").on("click", function(){
    var server_id = $("#select_server").val();
    var ajax_source = "/queryseal";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "server",
            "sClass": "center",
            "bVisible": false,
            "sTitle": "服务器"
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色"
        },
        {
            "mDataProp": "type",
            "sClass": "center",
            "sTitle": "封号类型"
        },
        {
            "mDataProp": "createtime",
            "sClass": "center",
            "sTitle": "创建时间"
        },
        {
            "mDataProp": "endtime",
            "sClass": "center",
            "sTitle": "解封时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_seal(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_seal(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">解封 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function(nRow, aData){
        var seal_type = SEAL_TYPE[aData.type];
        $('td:eq(1)', nRow).html(seal_type);
    };
    var data = {
        server_id: server_id
    };
    dataTablePage($("#seal_table"), aoColumns, ajax_source, data, true, fnRowCallback);
});

var mod_seal = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#seal_table").dataTable().fnGetData(nRoW);

    $("#close_id").val(data["id"]);
    $("#select_game").val(data["server"]);
    $("#close_role").val(data["rid"]);
    $("#close_type").val(data["type"]);
    $("#close_modal").modal("show");
};

var del_seal = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#seal_table").dataTable().fnGetData(nRoW);
    $("#confirm_del").attr('onclick', "confirm_del_close(" + data["id"] + ")");
    $("#del_modal").modal("show");
};

var confirm_del_close = function(nid){
    $.ajax({
            type: 'get',
            url: '/deleteseal',
            data: {
                close_id: nid
            },
            dataType: 'JSON',
            success: function (data) {
                if (data.status == "fail") {
                    Common.alert_message($("#error_modal"), 0, "删除失败.")
                }
                $("#del_modal").modal("hide");
                $("#a_closeaccount").click();
            },
            error: function (XMLHttpRequest){
                error_func(XMLHttpRequest);
            }
        }
    )
};