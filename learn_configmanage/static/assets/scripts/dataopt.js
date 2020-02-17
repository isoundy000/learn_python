
display_left_filter();
handleDatePickers();
handleTimePickers();
var now_date = getNowFormatDate(0);
$("#start_date").val(getNowFormatDate(1));
$("#end_date").val(now_date);
$("#q_date").val(now_date);

getPartnerData($("#select_channel"));
var $select_game_query = $("#select_game_query");
var $select_game = $("#select_game");

getGameServerData($select_game_query, 2);
getGameServerData($select_game, 2);

create_del_modal($("#recharge_del_modal"), "是否删除此记录", "confirm_del");

$("#add_recharge").on("click", function (e) {
    e.preventDefault();
    $("#role_id").val("");
    $("#recharge_modal").modal("show");
});

var delete_recharge = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#recharge_table").dataTable().fnGetData(nRoW);
    $('#recharge_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_recharge(" + data["id"] + ")");
};

var confirm_del_recharge = function (r_id) {
    var success = function (data) {
        if (data.status == 0) {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#recharge_del_modal').modal("hide");
    };
    var data = {
        r_id: r_id
    };
    my_ajax(true, "/deleterechargerecord", "get", data, true, success);
    query_recharge();
};


function query_recharge() {
    var select_game_query = $("#select_game_query").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var recharge_role_id = $("#recharge_role_id").val();
    var select_channel = $("#select_channel").val();
    var ajax_source = "/queryrechargerepo";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "uid",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "channel",
            "sClass": "center",
            "sTitle": "渠道"
        },
        {
            "mDataProp": "gid",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "s_name",
            "sClass": "center",
            "sTitle": "区服"
        },
        {
            "mDataProp": "total",
            'sClass': 'center',
            "sTitle": "充值金额"
        },
        {
            "mDataProp": "createtime",
            "sClass": "center",
             "sTitle": "创建时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html = aData.channel_name;
        $('td:eq(0)', nRow).html(str_html);
        var str_html2 = aData.gid + "区:" + aData.s_name;
        $('td:eq(1)', nRow).html(str_html2);
        var str_html3 = "<button onclick=\"delete_recharge(this)\" class=\"btn default btn-xs red\">删除</button>";
        $('td:eq(4)', nRow).html(str_html3);
        return nRow;
    };
    var data = {
        select_channel: select_channel, select_game_query: select_game_query, start_date: start_date,
        end_date: end_date, recharge_role_id: recharge_role_id
    };
    dataTablePage($("#recharge_table"), aoColumns, ajax_source, data, false, fnRowCallback);
}


$("#btn_recharge").on("click", function (e) {
    e.preventDefault();
    query_recharge();
});

var rechargeValidation = function () {
    var form1 = $('#recharge_form');
    var rules = {
        select_game: {
            required: true
        },
        role_id: {
            required: true
        },
        recharge_cid: {
            required: true
        }
    };
    var messages = {
        select_game: {
            required: "请选择区服."
        },
        role_id: {
            required: "请输入角色编号."
        },
        recharge_cid: {
            required: "请选择充值档."
        }
    };

    var submitFunction = function (form) {
        var select_game = $("#select_game").val();
        var role_id = $("#role_id").val();
        var recharge_cid = $("#recharge_cid").val();
        var q_date = $("#q_date").val();
        var q_time = $("#q_time").val();
        var q_datetime = q_date + " " + q_time;
        var success = function (data) {
            if (data.status == 1) {
                Common.alert_message($("#error_modal"), 0, "操作失败.");
            }
            else if (data.status == 2){
                Common.alert_message($("#error_modal"), 0, "角色不存在.");
            }
            $("#recharge_modal").modal("hide");
        };
        var data = {
            select_game: select_game, role_id: role_id, recharge_cid: recharge_cid, q_datetime:q_datetime
        };
        my_ajax(true, "/addrechargerecord", 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};
rechargeValidation();