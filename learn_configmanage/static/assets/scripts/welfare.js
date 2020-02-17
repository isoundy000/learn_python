/**
 * Created by wangrui on 16/5/12.
 */

display_left_filter();
create_del_modal($("#welfare_delete_modal"), "是否删除此角色?", "confirm_del");
getGameServerData($("#select_server"), 1);

$("#add_welfare").on("click", function(e){
    e.preventDefault();
    $("#role_id").val("");
    $("#welfare_modal").modal("show");
});


var welfareValidation = function () {
    var form1 = $('#welfare_form');
    var rules = {
        role_id: {
            required: true,
            digits: true
        }
    };
    var messages = {
        role_id: {
            required: "请输入角色ID",
            digits: "请输入数字"
        }
    };

    var submitHandler = function (form) {
        var gid = $("#select_server").val();
        var rid = $("#role_id").val();
        var data = {
            gid: gid,
            rid: rid
        };
        var success = function(data){
            if (data.status == "fail") {
                show_error_modal(0, "操作失败");
            }
            $("#welfare_modal").modal("hide");
            getWelfare();
        };
        my_ajax(true, '/addwelfareuser', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
welfareValidation();


var getWelfare = function () {
    var aoColumns = [
        {
            "mDataProp": "gid",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "data",
            'sClass': 'center',
            "sTitle": "数据"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent":
                "<button onclick=\"del_welfare(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var data = $.parseJSON(aData.data)["data"];
        var str_html1 = "元宝:" + data["gold"] + ",战斗力:" + data["power"] + ",等级:" + data["level"] +
                        ",VIP等级:" + data["vip"] + ",战斗力排行:" + data["powerrank"];
        $('td:eq(2)', nRow).html(str_html1);
    };
    var gid = $("#select_server").val();
    var data = {
        gid: gid
    };
    dataTablePage($("#welfare_table"), aoColumns, "/getwelfareuser", data, false, fnRowCallback);

};
getWelfare();


function del_welfare(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#welfare_table").dataTable().fnGetData(nRoW);
    $('#welfare_delete_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_welfare(" + data["gid"] + "," + data["rid"] + ")");
}

function confirm_del_welfare(gid, rid) {
    var data = {
        gid: gid,
        rid: rid
    };
    var success = function(data){
        if (data.status == "fail") {
            show_error_modal(0, "设置失败");
        }
        getWelfare();
    };
    my_ajax(true, "/deletewelfare", "get", data, true, success);
}