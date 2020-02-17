/**
 * Created by wangrui on 16/6/17.
 */

display_left_filter();
create_del_modal($("#batch_delete_modal"), "是否删除此角色?", "confirm_del");
getGameServerData($("#select_server"), 1);


$("#add_recharge").on("click", function(e){
    e.preventDefault();
    $("#select_server").val("1");
    $("#role_id").val("");
    $("#role_stag").val("1");
    $("#batch_modal").modal("show");
});

var batchValidation = function () {
    var form1 = $('#batch_form');
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
        var role_stag = $("#role_stag").val();
        var data = {
            gid: gid,
            rid: rid,
            tag: role_stag
        };
        var success = function(data){
            if (data.status == "fail") {
                show_error_modal(0, "操作失败");
            }
            else if(data.status == "exists"){
                show_error_modal(0, "角色已存在");
            }
            else if (data.status == "no"){
                show_error_modal(0, "角色不存在");
            }
            $("#batch_modal").modal("hide");
            getBatchRecharge();
        };
        my_ajax(true, '/operatebatchrecharge', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
batchValidation();


var getBatchRecharge = function () {
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
            "mDataProp": "tag",
            'sClass': 'center',
            "sTitle": "标识"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_batch(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_batch(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html = "";
        if (aData.tag == 0){
            str_html = "<span class='badge badge-danger'>非活跃</span>";
        }
        else{
            str_html = "<span class='badge badge-success'>活跃</span>";
        }
        $('td:eq(2)', nRow).html(str_html);
    };
    dataTablePage($("#batch_table"), aoColumns, "/getbatchrecharge", {}, false, fnRowCallback);
};
getBatchRecharge();



function mod_batch(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#batch_table").dataTable().fnGetData(nRoW);
    $("#select_server").val(data["gid"]);
    $("#role_id").val(data["rid"]);
    $("#role_stag").val(data["tag"]);
    $("#batch_modal").modal("show");
}


function del_batch(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#batch_table").dataTable().fnGetData(nRoW);
    $('#batch_delete_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_batch(" + data["gid"] + "," + data["rid"] + ")");
}

function confirm_del_batch(gid, rid) {
    var data = {
        gid: gid,
        rid: rid
    };
    var success = function(data){
        if (data.status == "fail") {
            show_error_modal(0, "删除失败");
        }
        getBatchRecharge();
    };
    my_ajax(true, "/deletebatchrecharge", "get", data, true, success);
}


$("#recharge").on("click", function(e){
    e.preventDefault();
    var success = function(data){
        if (data.status == "success") {
            show_error_modal(1, "充值成功.");
        }
        else{
            show_error_modal(0, "充值失败.");
        }
    };
    var recharge_type = $("#recharge_type").val();
    var data = {
        type: recharge_type
    };
    my_ajax(true, "/batchrecharge", "get", data, true, success);
});