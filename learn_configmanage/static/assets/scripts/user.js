/**
 * Created by wangrui on 14-10-11.
 */
// display_left_filter();

getPartnerData($("#select_channel"));

var userValidation = function () {
    var form1 = $('#user_form');
    var rules = {
        user_name: {
            required: true
        },
        user_confirm_pass: {
            equalTo: "#user_pass"
        },
        user_type: {
            required: true
        }

    };
    var messages = {
        user_name: {
            required: "请输入用户名."
        },
        user_confirm_pass: {
            equalTo: "密码输入不一致."
        },
        user_type: {
            required: "请选择类型"
        }
    };

    var submitHandler = function (form) {
        var user_id = $("#user_id").val();
        var name = $("#name").val();
        var user_name = $("#user_name").val();
        var user_pass = $("#user_pass").val();
        var email = $("#email").val();
        var phone = $("#phone").val();
        var user_role_type = [];
        var user_game = "";
        var is_start = "";
        var is_recharge = "";
        var upload_is = 0;
        var mail_approve = 0;
        var operate_type = [];
        $("input[name='user_role_type']:checked").each(function () {
            user_role_type.push($(this).val());
            if ($(this).val() == "2") {
                if ($("#upload_is").is(":checked")) {
                    upload_is = 1;
                }
            }
            if ($(this).val() == "5"){
                if ($("input[name='mail_approve']").prop("checked")){
                    mail_approve = 1;
                }
                $("input[name='operate_type']:checked").each(function () {
                    operate_type.push($(this).val());
                });
            }

        });

        var select_channel = $("#select_channel").val();

        var success = function (data) {
            if (data.status == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            $("#user_modal").modal("hide");
            getUsers();
        };
        var data = {
            user_id: user_id,
            name: name,
            user_name: user_name,
            user_pass: user_pass,
            user_type: JSON.stringify(user_role_type),
            user_game: user_game,
            upload_is: upload_is,
            is_start: is_start,
            is_recharge: is_recharge,
            select_channel: select_channel,
            mail_approve: mail_approve,
            operate_type: JSON.stringify(operate_type),
            email: email,
            phone: phone
        };
        my_ajax(true, '/operateuser', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
userValidation();



$("input[name='user_role_type']").on("change", function (e) {
    e.preventDefault();
    var role_t = $(this).val();
    var check_t = $(this).is(":checked");
    if (role_t == "2") {
        if (check_t) {
            $("#div_upload").show();
        }
        else {
            $("#div_upload").hide();
        }
    }
    if (role_t == "5") {
        if (check_t) {
            $("#div_operation_auth").show();
        } else {
            $("#div_operation_auth").hide();
        }
    }
});

var getUsers = function () {
    var sAjaxSource = "/getotheruser";
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
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "姓名"
        },
        {
            "mDataProp": "role1",
            'sClass': 'center',
            "sTitle": "系统权限"
        },
        {
            "mDataProp": "email",
            'sClass': 'center',
            "sTitle": "邮箱"
        },
        {
            "mDataProp": "phone",
            'sClass': 'center',
            "sTitle": "手机号"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_user(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button><button onclick=\"del_user(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html1 = '';
        if (aData.role1 == '1')
            str_html1 += '<span class="badge badge-success">管理系统</span>';

        if (aData.role2 == '1')
            str_html1 += '<span class="badge badge-success">策划系统</span>';

        if (aData.role3 == '1')
            str_html1 += '<span class="badge badge-success">统计系统</span>';

        if (aData.role4 == '1')
            str_html1 += '<span class="badge badge-success">运维系统</span>';

        if (aData.role5 == '1')
            str_html1 += '<span class="badge badge-success">运营系统</span>';
        $('td:eq(2)', nRow).html(str_html1);
        return nRow;
    };

    dataTablePage($("#user_table"), aoColumns, sAjaxSource, {}, false, fnRowCallback);
};
getUsers();

$("#add_user").click(function (e) {
    e.preventDefault();
    $("#user_id").val("");
    $("#user_name").val("");
    $("#name").val();
    $("#user_name").attr("disabled", false);
    $("#user_pass").val("");
    $("#user_configm_pass").val("");
    $("input[name='user_role_type']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    $("#div_upload").addClass("hide");
    $("#div_game").addClass("hide");
    $('#upload_switch').bootstrapSwitch('setState', false);
    $("input[name='div_operation_auth']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    $("#email").val("");
    $("#phone").val("");
    $("#user_modal").modal("show");
});

function del_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#user_table").dataTable().fnGetData(nRoW);
    $('#user_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_user(" + data["id"] + ")");
}

function confirm_del_user(user_id) {
    var success = function () {
        if (data.status == 0) {
            Common.alert_message($("#error_modal"), 0, "操作失败");
        }
        getUsers();
    };
    var data = {
        user_id: user_id
    };
    my_ajax(true, 'deleteuser', 'get', data, true, success);
}

function mod_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#user_table").dataTable().fnGetData(nRoW);
    $("#user_id").val(data["id"]);
    $("#name").val(data["name"]);
    $("#user_name").val(data["username"]);

    if (data["role1"] == '1') {
        $("#user_role_type1").prop("checked", true);
        $("#user_role_type1").parent("span").addClass("checked");
    }
    else {
        $("#user_role_type1").prop("checked", false);
        $("#user_role_type1").parent("span").removeClass("checked");
    }

    if (data["role2"] == '1') {
        $("#user_role_type2").prop("checked", true);
        $("#user_role_type2").parent("span").addClass("checked");
        $("#div_upload").removeClass("hide");
        if (data["upload"] == "1") {
            $('#upload_switch').bootstrapSwitch('setState', true);
        }
        else {
            $('#upload_switch').bootstrapSwitch('setState', false);
        }
    }
    else {
        $("#div_upload").addClass("hide");
        $("#user_role_type2").prop("checked", false);
        $("#user_role_type2").parent("span").removeClass("checked");
    }

    if (data["role3"] == '1') {
        $("#user_role_type3").prop("checked", true);
        $("#user_role_type3").parent("span").addClass("checked");
    }
    else {
        $("#user_role_type3").prop("checked", false);
        $("#user_role_type3").parent("span").removeClass("checked");
    }

    if (data["role4"] == '1') {
        $("#user_role_type4").prop("checked", true);
        $("#user_role_type4").parent("span").addClass("checked");
    }
    else {
        $("#user_role_type4").prop("checked", false);
        $("#user_role_type4").parent("span").removeClass("checked");
    }

    if (data["role5"] === 1) {
        $("#user_role_type5").prop("checked", true);
        $("#user_role_type5").parent("span").addClass("checked");
        $("#div_operation_auth").show();
        var custom = data["custom"];
        $("input[name='operate_type']").parent("span").removeClass('checked');
        var split_arr = custom.split("|");
        for (var i = 0; i < split_arr.length; i++) {
            if (split_arr[i] !== "") {
                var operate_d = $("input[name='operate_type'][value='" + split_arr[i] + "']");
                operate_d.prop("checked", true);
                operate_d.parent("span").addClass("checked");
            }
        }
    }
    else {
        $("#div_operation_auth").hide();
        $("#user_role_type5").prop("checked", false);
        $("#user_role_type5").parent("span").removeClass("checked");
    }

    $("#user_name").attr("disabled", true);
    $("#select_channel").val(data["channel"]);
    $("#email").val(data["email"]);
    $("#phone").val(data["phone"]);
    $("#user_modal").modal("show");
}
