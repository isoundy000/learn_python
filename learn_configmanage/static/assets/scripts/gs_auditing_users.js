/**
 * Created by wangrui on 15/12/8.
 */

var $gs_users_table = $('#gs_users_table');
var $user_success_modal = $('#user_success_modal');
var $user_fail_modal = $('#user_fail_modal');


create_del_modal($user_success_modal, "是否通过此用户?", "btn_confirm");
create_del_modal($user_fail_modal, "是否拒绝此用户?", "btn_refuse");





var get_gs_users = function () {

};

var confirm_operate_user = function (uid, type) {

    $.ajax({
        'url': '/gs_recharge/update_user',
        'data': {'uid': uid, 'op_type': type},
        'type': 'post',
        'dataType': 'json',
        'success': function (result) {
            $user_success_modal.modal("hide");
            $user_fail_modal.modal("hide");
            if (result['status'] === 'success'){
                Common.alert_message($("#error_modal"), 1, "操作成功.");
            }else{
                Common.alert_message($("#error_modal"), 0, "操作失败.");
            }
            show_user_table_obj.ajax.reload(null, false);
        },
        'error': function () {
            $user_success_modal.modal("hide");
            $user_fail_modal.modal("hide");
            Common.alert_message($("#error_modal"), 0, "操作失败, 服务器错误.");
        }


    });
};

var success_gs_user = function (uid) {
    $user_success_modal.modal("show");
    $("#btn_confirm").attr('onclick', "confirm_operate_user(" + uid + ",'via')");
};
var fail_gs_user = function (uid) {
    $user_fail_modal.modal("show");
    $("#btn_refuse").attr('onclick', "confirm_operate_user(" + uid + ",'refuse')");
};


var show_user_table_obj;
var show_recharge_user = function (uid_status) {
    "use strict";

    var ajax_data = {
        "url": "/gs_recharge/show_user",
        "type": "get",
        "data": {'uid_status': uid_status},
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#user_table_processing').hide();
        },
        "dataSrc": function (result) {
            return result;
        }
    };

    var columns = [{"title": "用户标识", 'data': 'uid'}, {"title":"创建用户", 'data': 'c_user'},
        {"title":"创建时间", 'data': 'create_time'},{"title":"审核时间", 'data': 'checked_time'},
        {"title":"审核人", 'data': 'u_user'},{"title":"操作", 'data': 'uid'}];


    var columnDefs;
    if (uid_status === 'no_checked'){
        columnDefs = [
            {
                "targets": [-1],
                "render": function (data) {
                    return '<button onclick="success_gs_user('+data+')" class="btn default btn-xs green" data-toggle="modal">通过' +
                        '</button><button onclick="fail_gs_user('+data+')" class="btn default btn-xs red" data-toggle="modal">拒绝 ' +
                        '</button>';
                }
            },
            {
                "visible": false,
                "targets": [3, 4]
            }
        ];
    }else{
        columnDefs = [
            {
                "visible": false,
                "targets": -1
            }
        ];
    }

   show_user_table_obj = new_front_page_table($gs_users_table, ajax_data,columns,columnDefs,false);
};




var $btn_approve = $("#btn_approve");
var $btn_success = $("#btn_success");
var $btn_fail = $("#btn_fail");

$btn_approve.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    show_recharge_user('no_checked');
});

$btn_success.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    show_recharge_user('checked');
});

$btn_fail.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    show_recharge_user("refuse");
});

$btn_approve.click();



