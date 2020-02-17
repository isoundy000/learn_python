/**
 * Created by wangrui on 15/12/7.
 */


create_del_modal($("#custom_del_modal"), "是否删除此客服用户?", "confirm_del");


function userValidation() {
    var form1 = $('#custom_user_form');
    var rules = {
        user_name: {
            required: true
        },
        user_confirm_pass: {
            equalTo: "#user_pass"
        }
    };
    var messages = {
        user_name: {
            required: "请输入用户名."
        },
        user_confirm_pass: {
            equalTo: "密码输入不一致."
        }
    };

    var submitHandler = function (form) {
        var user_id = $("#user_id").val();
        var user_name = $("#user_name").val();
        var user_pass = $("#user_pass").val();
        var user_role_type = "";
        var mail_approve = 0;
        if ($("input[name='mail_approve']").prop("checked")){
            mail_approve = 1;
        }
        $("input[name='user_role_type']:checked").each(function () {
            var role_value = $(this).val();
            user_role_type += role_value + "|";
        });
        $.ajax({
                type: 'get',
                url: '/operatecustomuser',
                data: {
                    user_id: user_id,
                    user_name: user_name,
                    user_pass: user_pass,
                    user_type: user_role_type,
                    mail_approve: mail_approve
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data.status == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    else if (data.status == "repeat"){
                        Common.alert_message($("#error_modal"), 0, "用户名已存在");
                    }
                    $("#custom_user_modal").modal("hide");
                    getCustomUsers();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitHandler);
}
userValidation();


var getCustomUsers = function () {
    var sAjaxSource = "/getcustomuser";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "username",
            'sClass': 'center',
            "sTitle": "用户名"
        },
        {
            "mDataProp": "custom",
            'sClass': 'center',
            "sTitle": "客服权限"
        },
        {
            "mDataProp": "approve",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_user(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button><button onclick=\"del_user(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html = '';

        var str_split = aData.custom.split("|");
        for(var s in str_split){
            if (str_split[s] != ""){
                str_html += "<span class='badge badge-success'>" + custom_left_type[str_split[s]]["name"];
                if (aData.approve == 1 && str_split[s] == "2"){
                    str_html += "(审核)";
                }
                str_html += "</span>";
            }

        }
        $('td:eq(1)', nRow).html(str_html);
        return nRow;
    };

    dataTablePage($("#custom_table"), aoColumns, sAjaxSource, {}, false, fnRowCallback);
};
getCustomUsers();

$("#add_custom_user").click(function (e) {
    e.preventDefault();
    $("#user_id").val("");
    $("#user_name").val("");
    $("#user_name").attr("disabled", false);
    $("#user_pass").val("");
    $("#user_configm_pass").val("");
    $("input[name='user_role_type']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    var mail_approve = $("input[name='mail_approve']");
    mail_approve.prop("checked", false);
    mail_approve.parent("span").removeClass("checked");
    $("#custom_user_modal").modal("show");
});

function del_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#custom_table").dataTable().fnGetData(nRoW);
    $('#custom_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_user(" + data["id"] + ")");
}

function confirm_del_user(user_id) {
    $.ajax({
        type: 'get',
        url: '/deleteuser',
        data: {user_id: user_id},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 0) {
                Common.alert_message($("#error_modal"), 0, "删除失败");
            }
            $('#custom_del_modal').modal("hide");
            getCustomUsers();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
}


function mod_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#custom_table").dataTable().fnGetData(nRoW);
    $("#user_id").val(data["id"]);
    var $user_name = $("#user_name");
    $user_name.val(data["username"]);
    var split_arr = data["custom"].split("|");
    for (var i = 0; i < split_arr.length; i++) {
        var role_type = $("input[name='user_role_type'][value='" + split_arr[i] + "']");
        role_type.prop("checked", true);
        role_type.parent("span").addClass("checked");
    }

    $user_name.attr("disabled", true);
    $("#custom_user_modal").modal("show");
}