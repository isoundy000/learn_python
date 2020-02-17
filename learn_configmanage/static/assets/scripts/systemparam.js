/**
 * Created by wangrui on 15/5/28.
 */

get_left_game_server();
create_del_modal($("#param_del_modal"), "是否删除此系统及系统下的所有函数?", "del_param_btn");
create_del_modal($("#func_del_modal"), "是否删除此函数?", "del_func_btn");

handleDatePickers();
$("#q_date").val(getNowFormatDate(1));
$("#guide_date").val(getNowFormatDate(1));

getGameServerData($("#select_gameserver"), 1);
getGameServerData($("#select_gameserver1"), 1);

var get_param_data = function () {
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querysystemparam',
        data: {},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);

            var str_info = "";
            var str_info1 = "";
            if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                    str_info += "<tr>";
                    str_info += "<td>" + data[i]["name"] + "</td>";
                    str_info += "<td>" + data[i]["param"] + "</td>";
                    str_info += "<td>";
                    str_info += '&nbsp; <a onclick="set_param(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs blue" data-toggle="modal">配置 <i class="fa fa-gear"></i></a>';
                    str_info += '&nbsp; <a onclick="mod_param(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                    str_info += '&nbsp; <a onclick="del_param(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                    str_info += "</td>";
                    str_info += "</tr>";
                    str_info1 += '<option value="' + data[i]["id"] + '">' + data[i]["name"] + '</option>';
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#param_list").html(str_info);
            $("#select_system").html(str_info1);
        },
        error: function () {
            App.unblockUI(page_content);
        }
    })
};
get_param_data();


var get_param_data1 = function () {
    $.ajax({
        type: 'get',
        url: '/queryparam',
        data: {},
        dataType: 'JSON',
        success: function (data) {
            var str_info1 = "";
            if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                    str_info1 += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + "</option>";
                }
            }
            $("#select_param1").html(str_info1);
        },
        error: function () {
        }
    })
};
get_param_data1();


var set_param = function (id) {
    $("#param_set_id").val(id);
    query_func(id);
    $("#param_set_modal").modal("show");
};

var query_func = function (id) {

    var ajax_source = "/queryfuncbysystem";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "函数"
        },
        {
            "mDataProp": "stay_time",
            "sClass": "center",
            "sTitle": "停留时间"
        },
        {
            "mDataProp": "out_time",
            "sClass": "center",
            "sTitle": "超时时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_func(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_func(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        system_id: id
    };
    dataTablePage($("#func_list"), aoColumns, ajax_source, data, false);
};

var mod_func = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#func_list").dataTable().fnGetData(nRoW);
    $("#func_id").val(data["id"]);
    $("#func_name").val(data["name"]);
    $("#stay_time").val(data["stay_time"]);
    $("#out_time").val(data["out_time"]);
    $("#func_modal").modal("show");
};

var del_func = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#func_list").dataTable().fnGetData(nRoW);
    $('#func_del_modal').modal("show");
    $("#del_func_btn").attr('onclick', 'fun_del_func(' + data["id"] + ');');
};

var fun_del_func = function (id) {
    var param_set_id = $("#param_set_id").val();
    $.ajax({
        type: 'get',
        url: '/deletefunc',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#func_del_modal').modal("hide");
            query_func(param_set_id);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


$("#add_func").on("click", function (e) {
    e.preventDefault();
    $("#func_name").val("");
    $("#stay_time").val("");
    $("#out_time").val("");
    $("#func_modal").modal("show");
});

var mod_param = function (id) {
    $.ajax({
        type: 'get',
        url: '/queryonesystemparam',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            $("#param_id").val(id);
            $("#select_param1").val(data["param"]);
            $("#param_name").val(data["name"]);
            if (data["tag"] == 1) {
                $("#system_tag").prop("checked", true);
                $("#system_tag").parent("span").addClass("checked");
            }
            else {
                $("#system_tag").prop("checked", false);
                $("#system_tag").parent("span").removeClass("checked");
            }
            $("#param_desc").val(data["desc"]);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
    $("#param_modal").modal("show");
};

var del_param = function (id) {
    $('#param_del_modal').modal("show");
    $("#del_param_btn").attr('onclick', 'fun_del_param(' + id + ');');
};

var fun_del_param = function (id) {
    $.ajax({
        type: 'get',
        url: '/deletesystemparam',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#param_del_modal').modal("hide");
            get_param_data();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

$("#add_param").on("click", function () {
    $("#param_id").val("");
    $("#param_name").val("");
    $("#param_desc").val("");
    $("#param_modal").modal("show");
});

var paramValidate = function () {
    var form1 = $('#param_form');
    var rules = {
        param_name: {
            required: true
        }
    };
    var messages = {
        param_name: {
            required: "请输入参数名."
        }
    };
    var submitFunc = function () {
        var param_id = $("#param_id").val();
        var param_name = $('#param_name').val();
        var param = $("#select_param1").val();
        var param_desc = $("#param_desc").val();
        var system_tag = 0;
        if ($("#system_tag").is(":checked")) {
            system_tag = 1;
        }
        $.ajax({
                type: 'get',
                url: '/operatesystemparam',
                data: {
                    param_id: param_id,
                    param: param,
                    param_name: param_name,
                    system_tag: system_tag,
                    param_desc: param_desc
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#param_modal").modal("hide");
                    get_param_data();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunc);
};
paramValidate();


$("#btn_func").on("click", function (e) {
    e.preventDefault();
    var func_id = $("#func_id").val();
    var param_set_id = $("#param_set_id").val();
    var func_name = $("#func_name").val();
    var stay_time = $("#stay_time").val();
    var out_time = $("#out_time").val();
    $.ajax({
            type: 'get',
            url: '/operatefunction',
            data: {
                func_id: func_id,
                param_set_id: param_set_id,
                func_name: func_name,
                stay_time: stay_time,
                out_time: out_time
            },
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "fail") {
                    Common.alert_message($("#error_modal"), 0, "操作失败");
                }
                $("#func_modal").modal("hide");
                query_func(param_set_id);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
});


$("#stay_time").on("input propertychange", function (e) {
    e.preventDefault();
    $("#out_time").val($("#stay_time").val());
});


$("#select_type").on("change", function (e) {
    e.preventDefault();
    var select_type = $("#select_type").val();
    if (select_type == "count") {
        $("#div_role").addClass("hide");
    }
    else {
        $("#div_role").removeClass("hide");
    }

});

$("#btn_process").on("click", function (e) {
    e.preventDefault();
    var select_gameserver = $("#select_gameserver").val();
    var q_date = $("#q_date").val();
    var select_system = $("#select_system").val();
    var select_type = $("#select_type").val();
    var role_id = $("#role_id").val();
    if (select_type == "count") {
    }
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/process_gamelog',
        data: {
            select_gameserver: select_gameserver,
            q_date: q_date,
            role_id: role_id,
            select_system: select_system,
            select_type: select_type
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_title = "";
            var str_info = "";
            if (data["status"]) {
                if (select_type == "count") {
                    str_title += "<tr>";
                    str_title += "<th>漏斗数据</th>";
                    str_title += "<th>人数</th>";
                    str_title += "</tr>";
                    var total_value = 0;
                    for (var d in data["data"]["funnel_data"]) {
                        str_info += "<tr>";
                        str_info += "<td>" + data["data"]["funnel_data"][d]["start"] + "~" + data["data"]["funnel_data"][d]["end"] + "次数</td>";
                        str_info += "<td>" + data["data"]["funnel_data"][d]["value"] + "</td>";
                        str_info += "</tr>";
                        total_value += data["data"]["funnel_data"][d]["value"];
                    }
                    str_info += "<tr>";
                    str_info += "<td>总计</td>";
                    str_info += "<td>" + total_value + "</td>";
                    str_info += "</tr>";
                }
                else {
                    str_title += "<tr>";
                    str_title += "<th>平均时间</th>";
                    str_title += "<th>人数</th>";
                    str_title += "</tr>";
                    str_info += "<tr>";
                    str_info += "<td>" + data["data"]["ave_time"] + "秒</td>";
                    str_info += "<td>" + data["data"]["person"] + "</td>";
                    str_info += "</tr>";
                }
            }
            $("#process_title").html(str_title);
            $("#process_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


$("#btn_guide_process").on("click", function (e) {
    e.preventDefault();
    var select_gameserver = $("#select_gameserver1").val();
    var guide_date = $("#guide_date").val();
    var guide_role = $("#guide_role").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/process_guidelog',
        data: {
            select_gameserver: select_gameserver,
            guide_date: guide_date,
            guide_role: guide_role
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var str_title = "";
            str_title += "<tr>";
            str_title += "<th>步骤</th>";
            if (data["guide_data"]["status"]) {
                if (guide_role.length == 0) {
                    str_title += "<th>平均时间(秒)</th>";
                    str_title += "<th>人数</th>";
                }
                else {
                    str_title += "<th>用时时间</th>";
                }
                str_title += "</tr>";
                for (var i = 0; i < data["guide_data"]["data"].length; i++) {
                    str_info += "<tr>";
                    var s = data["guide_data"]["data"][i][0] + 1;
                    str_info += "<td>" + data["guide_json"][1][s]["_param2"] + "</td>";
                    str_info += "<td>" + data["guide_data"]["data"][i][1] + "</td>";
                    if (guide_role.length == 0) {
                        str_info += "<td>" + data["guide_data"]["data"][i][2] + "</td>";
                    }
                    str_info += "</tr>";
                }
            }
            $("#guide_title").html(str_title);
            if (str_info != ""){
                $("#guide_list").html(str_info);
            }else{
                var str_info2 = "";
                str_info2 += "<tr>";
                if (guide_role.length == 0) {
                    str_info2 += '<td colspan="3" class="text-center"><span class="label label-danger">无新手引导数据</span></td>';
                }else{
                    str_info2 += '<td colspan="2" class="text-center"><span class="label label-danger">无新手引导数据</span></td>';
                }
                str_info2 += '</tr>';
                $("#guide_list").html(str_info2);
            }

        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});