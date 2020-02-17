/**
 * Created by wangrui on 14-10-11.
 */
display_left_filter();

getPartnerData($("#select_channel"));
//getGameServerDataCheck($("#game_server"));


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
        var user_name = $("#user_name").val();
        var user_pass = $("#user_pass").val();
        var user_role_type = "";
        var user_game = "";
        var is_start = "";
        var is_recharge = "";
        var upload_is = 0;
        $("input[name='user_role_type']:checked").each(function () {
            user_role_type += $(this).val() + ",";
            if ($(this).val() == "2") {
                if ($("#upload_is").is(":checked")) {
                    upload_is = 1;
                }
            }
            if ($(this).val() == "4") {
                $("input[name='user_game']:checked").each(function () {
                    var user_ = $(this).val();
                    user_game += user_ + "|";
                    if ($("input[name='is_start'][value='" + user_ + "']").is(":checked")) {
                        is_start += "1|";
                    }
                    else {
                        is_start += "0|";
                    }

                    if ($("input[name='is_recharge'][value='" + user_ + "']").is(":checked")) {
                        is_recharge += "1|";
                    }
                    else {
                        is_recharge += "0|";
                    }
                });
            }
        });

        var select_channel = $("#select_channel").val();
        $.ajax({
                type: 'get',
                url: '/operateuser',
                data: {
                    user_id: user_id,
                    user_name: user_name,
                    user_pass: user_pass,
                    user_type: user_role_type,
                    user_game: user_game,
                    upload_is: upload_is,
                    is_start: is_start,
                    is_recharge: is_recharge,
                    select_channel: select_channel
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data.status == 0) {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#user_modal").modal("hide");
                    getUsers();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitHandler);
};
userValidation();

$("input[name='is_start']").on("change", function (e) {
    e.preventDefault();
    var s_v = $(this).val();
    var s = $("input[name='user_game'][value='" + s_v + "']");
    if ($(this).is(":checked")) {
        s.prop("checked", true);
        s.parent("span").addClass("checked");
    }
    else {
        s.prop("checked", false);
        s.parent("span").removeClass("checked");
    }
});


$("input[name='is_recharge']").on("change", function (e) {
    e.preventDefault();
    var s_v = $(this).val();
    var s = $("input[name='user_game'][value='" + s_v + "']");
    if ($(this).is(":checked")) {
        s.prop("checked", true);
        s.parent("span").addClass("checked");
    }
    else {
        s.prop("checked", false);
        s.parent("span").removeClass("checked");
    }
});

$("input[name='user_game']").on("change", function (e) {
    e.preventDefault();
    var s_str = $(this).val();
    var is_start = $("input[name='is_start'][value='" + s_str + "']");
    var is_recharge = $("input[name='is_recharge'][value='" + s_str + "']");
    if ($(this).is(":checked") == false) {
        is_start.prop("checked", false);
        is_start.parent("span").removeClass("checked");
        is_recharge.prop("checked", false);
        is_recharge.parent("span").removeClass("checked");
    }
});


$("input[name='user_role_type']").on("change", function (e) {
    e.preventDefault();
    var role_t = $(this).val();
    if (role_t == "2") {
        if ($(this).is(":checked")) {
            $("#div_upload").removeClass("hide");
        }
        else {
            $("#div_upload").addClass("hide");
        }
    }
    if (role_t == "4") {
        if ($(this).is(":checked")) {
            $("#div_game").removeClass("hide");
        }
        else {
            $("#div_game").addClass("hide");
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
            "mDataProp": "role1",
            'sClass': 'center',
            "sTitle": "管理系统"
        },
        {
            "mDataProp": "role2",
            'sClass': 'center',
            "sTitle": "策划系统"
        },
        {
            "mDataProp": "role3",
            'sClass': 'center',
            "sTitle": "统计系统"
        },
        {
            "mDataProp": "role4",
            'sClass': 'center',
            "sTitle": "运维系统"
        },
        {
            "mDataProp": "role5",
            'sClass': 'center',
            "sTitle": "运营系统"
        },
        {
            "mDataProp": "channel",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "game",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "upload",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "start",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "recharge",
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
        var str_html1 = '<span class="badge badge-success">Y</span>';
        var str_html2 = '<span class="badge badge-danger">N</span>';
        if (aData.role1 == '1')
            $('td:eq(1)', nRow).html(str_html1);
        else
            $('td:eq(1)', nRow).html(str_html2);

        if (aData.role2 == '1')
            $('td:eq(2)', nRow).html(str_html1);
        else
            $('td:eq(2)', nRow).html(str_html2);

        if (aData.role3 == '1')
            $('td:eq(3)', nRow).html(str_html1);
        else
            $('td:eq(3)', nRow).html(str_html2);

        if (aData.role4 == '1')
            $('td:eq(4)', nRow).html(str_html1);
        else
            $('td:eq(4)', nRow).html(str_html2);

        if (aData.role5 == '1')
            $('td:eq(5)', nRow).html(str_html1);
        else
            $('td:eq(5)', nRow).html(str_html2);
        return nRow;
    };

    dataTablePage($("#user_table"), aoColumns, sAjaxSource, {}, false, fnRowCallback);
};
getUsers();

$("#add_user").click(function (e) {
    e.preventDefault();
    $("#user_id").val("");
    $("#user_name").val("");
    $("#user_name").attr("disabled", false);
    $("#user_pass").val("");
    $("#user_configm_pass").val("");
    //$("#user_type").val("");
    $("input[name='user_role_type']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });
    $("#div_upload").addClass("hide");
    $("#div_game").addClass("hide");
    $('#upload_switch').bootstrapSwitch('setState', false);
    $("input[name='user_game']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });

    $("input[name='is_start']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });

    $("input[name='is_recharge']").each(function (e) {
        $(this).prop("checked", false);
        $(this).parent("span").removeClass("checked");
    });

    $("#user_modal").modal("show");
});

function del_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#user_table").dataTable().fnGetData(nRoW);
    $('#user_del_modal').modal("show");
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
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            getUsers();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
}

function mod_user(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#user_table").dataTable().fnGetData(nRoW);
    $("#user_id").val(data["id"]);
    var $user_name = $("#user_name");
    $user_name.val(data["username"]);
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
//        if (data["game"] != "") {
//            var split_arr = data["game"].split("|");
//            var split_start = data["start"].split("|");
//            var split_recharge = data["recharge"].split("|");
//            $("#div_game").removeClass("hide");
//            for (var i = 0; i < split_arr.length; i++) {
//                if (split_arr[i] != "") {
//                    var in_game = $("input[name='user_game'][value='" + split_arr[i] + "']");
//                    in_game.prop("checked", true);
//                    in_game.parent("span").addClass("checked");
//
//                    var is_start = $("input[name='is_start'][value='" + split_arr[i] + "']");
//                    if (split_start[i] == "1") {
//                        is_start.prop("checked", true);
//                        is_start.parent("span").addClass("checked");
//                    }
//                    else {
//                        is_start.prop("checked", false);
//                        is_start.parent("span").removeClass("checked");
//                    }
//
//                    var is_recharge = $("input[name='is_recharge'][value='" + split_arr[i] + "']");
//                    if (split_recharge[i] == "1") {
//                        is_recharge.prop("checked", true);
//                        is_recharge.parent("span").addClass("checked");
//                    }
//                    else {
//                        is_recharge.prop("checked", false);
//                        is_recharge.parent("span").removeClass("checked");
//                    }
//                }
//            }
//        }
//        else {
//            $("#div_game").addClass("hide");
//        }
    }
    else {
        $("#user_role_type4").prop("checked", false);
        $("#user_role_type4").parent("span").removeClass("checked");
    }


    if (data["role5"] == '1') {
        $("#user_role_type5").prop("checked", true);
        $("#user_role_type5").parent("span").addClass("checked");
    }
    else {
        $("#user_role_type5").prop("checked", false);
        $("#user_role_type5").parent("span").removeClass("checked");
    }

    $user_name.attr("disabled", true);
    $("#select_channel").val(data["channel"]);
    $("#user_modal").modal("show");
}