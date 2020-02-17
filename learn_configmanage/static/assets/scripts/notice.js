/**
 * Created by wangrui on 15/9/18.
 */

handleDatePickers2();
handleTimePickers();

$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));
create_del_modal($("#login_del_modal"), "是否删除此公告", "confirm_del");

if (PLATFORM_NAME==='hot_yuenan'){
    $('#a_system_notice').show()
}

$("#add_login_notice").on("click", function (e) {
    e.preventDefault();
    $("#login_notice_id").val("");
    $("#login_title").val("");
    $("#login_content").val("");
    $("#start_time").val("");
    $("#end_time").val("");
    $("#login_notice_modal").modal("show");
});


var loginNoticeValidation = function () {
    var form1 = $('#login_notice_form');
    var rules = {
        login_title: {
            required: true
        },
        login_content: {
            required: true
        }
    };
    var messages = {
        login_title: {
            required: "请输入公告标题"
        },
        login_content: {
            required: "请输入公告简介"
        }
    };
    var submitFunction = function (form) {
        var login_notice_id = $("#login_notice_id").val();
        var login_title = $("#login_title").val();
        var login_content = $("#login_content").val();
        var start_date = $("#start_date").val();
        var start_time = $("#start_time").val();
        var end_date = $("#end_date").val();
        var end_time = $("#end_time").val();
        var select_opt = $("#select_opt").val();
        var select_status = $("#select_status").val();
        $.ajax({
                type: 'get',
                url: '/operateloginnotice',
                data: {
                    login_notice_id: login_notice_id,
                    login_title: login_title,
                    login_content: login_content,
                    start_date: start_date,
                    start_time: start_time,
                    end_date: end_date,
                    end_time: end_time,
                    select_opt: select_opt,
                    select_status: select_status
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败.")
                    }
                    $("#login_notice_modal").modal("hide");
                    get_login_notice();
                },
                error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunction);
};
loginNoticeValidation();

var get_login_notice = function () {
    var ajax_source = '/queryloginnotice';
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "title",
            'sClass': 'center',
            "sTitle": "标题"
        },
        {
            "mDataProp": "start",
            'sClass': 'center',
            "sTitle": "开始时间"
        },
        {
            "mDataProp": "end",
            'sClass': 'center',
            "sTitle": "结束时间"
        },
        {
            "mDataProp": "opt",
            'sClass': 'center',
            "sTitle": "操作"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "createtime",
            'sClass': 'center',
            "sTitle": "创建时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_login_notice(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_login_notice(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html = "";
        if (aData.opt == 'yes') {
            str_html += "<span class='badge badge-success'>允许进入游戏</span>";
        }
        else {
            str_html += "<span class='badge badge-danger'>禁止进入游戏</span>";
        }
        $('td:eq(3)', nRow).html(str_html);
        console.log(aData.start, aData.end);
        var str_html1 = "";
        if (aData.status == "prepare") {
            str_html1 += "<span class='badge badge-info'>准备</span>";
        }
        else if (aData.status == "execute") {
            str_html1 += "<span class=\"badge badge-success\">执行</span>";
        }
        else {
            str_html1 += "<span class=\"badge badge-danger\">错误</span>";
        }
        $('td:eq(4)', nRow).html(str_html1);
    };
    dataTablePage($("#login_notice_table"), aoColumns, ajax_source, {}, false, fnRowCallback);
};

get_login_notice();

var mod_login_notice = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#login_notice_table").dataTable().fnGetData(nRoW);
    $("#login_notice_id").val(data["id"]);
    $("#login_title").val(data["title"]);
    $("#login_content").val(data["content"]);
    var start_s = data["start"].split(" ");
    var end_s = data["end"].split(" ");
    $("#start_date").val(start_s[0]);
    $("#start_time").val(start_s[1]);

    $("#end_date").val(end_s[0]);
    $("#end_time").val(end_s[1]);
    $("#select_opt").val(data["opt"]);
    $("#select_status").val(data["status"]);
    $("#login_notice_modal").modal("show");
};

var del_login_notice = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#login_notice_table").dataTable().fnGetData(nRoW);

    $('#login_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_login_notice(" + data["id"] + ")");
};

function confirm_del_login_notice(nid) {
    $.ajax({
        type: 'get',
        url: '/deleteloginnotice',
        data: {nid: nid},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 0) {
                Common.alert_message($("#error_modal"), 0, "操作失败.");
            }
            $('#login_del_modal').modal("hide");
            get_login_notice();
        },
        error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
    });
}


handleDatePickers();
$("#param1_date").val(getNowFormatDate(0));
$("#param2_date").val(getNowFormatDate(0));
getGameServerDataCheck($("select_server"));
create_del_modal($("#system_notice_del_modal"), "是否删除此系统公告", "confirm_system_del");

var SECTION_JSON_DATA = {};

get_section($("#select_section"));

$("#a_system_notice").on("click", function (e) {
    get_notice_data();
});

var recharge_gift = 0;
//var pic_name_list = new Array();

var config_id = '';
var get_notice_data = function () {
    var str_html = "";
    var section = $("#select_section").val();
    $.ajax({
        type: 'get',
        url: '/queryjsondatabysection',
        data: {
            section: section,
            type: JSON.stringify(["notice_3", "build"])
        },
        dataType: 'JSON',
        success: function (data) {
            SECTION_JSON_DATA[section] = data;
            if (SECTION_JSON_DATA[section]["notice_3"] != null) {
                config_id = data.notice_3_id;
                for (var i in SECTION_JSON_DATA[section]["notice_3"]) {

//                    pic_name_list.push(SECTION_JSON_DATA[section]["notice_3"][i]['pic']);
                    if (parseInt(i) >= recharge_gift) {
                        recharge_gift = parseInt(i);
                    }

                    str_html += "<tr>";
                    str_html += "<td>" + i + "</td>";
                    str_html += "<td>" + SECTION_JSON_DATA[section]["notice_3"][i]["title"] + "</td>";
                    str_html += "<td>" + SECTION_JSON_DATA[section]["notice_3"][i]["display"] + "</td>";
                    var type = SECTION_JSON_DATA[section]["notice_3"][i]["type"];
                    var param2 = SECTION_JSON_DATA[section]["notice_3"][i]["param2"];

                    if (type == 1) {
                        str_html += "<td><span class='badge badge-success'>有效</span></td>";
                    }
                    else {
                        var now_date = getNowFormatDate2();
                        if (now_date > param2) {
                            str_html += "<td><span class='badge badge-danger'>无效</span></td>";
                        }
                        else {
                            str_html += "<td><span class='badge badge-success'>有效</span></td>";
                        }
                    }
                    var server = SECTION_JSON_DATA[section]["notice_3"][i]["server"];
                    str_html += "<td>";
                    if (server.length != 0) {
                        if (server == "0") {
                            str_html += "全服";
                        }
                        else {
                            if (server.substring(0, 1) == "[") {
                                var server_d = server.split(";");
                                for (var k = 0; k < server_d.length; k++) {
                                    var server_arr = eval(server_d[k]);
                                    str_html += GAME_SERVER_DICT[server_arr[0]]["name"] + "~" + GAME_SERVER_DICT[server_arr[1]]["name"];

                                }
                            }
                            else {
                                var server_j = server.split(",");
                                str_html += server_j[0] + "区:" + GAME_SERVER_DICT[server_j[0]]["name"];
                                if (server_j.length > 1) {
                                    str_html += "," + server_j[1] + "区:" + GAME_SERVER_DICT[server_j[1]]["name"];
                                }
                            }
                        }
                    }
                    str_html += "</td>";
                    str_html += "<td>";
                    str_html += '&nbsp; <a onclick="mod_notice(' + "'" + i + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                    str_html += '&nbsp; <a onclick="del_notice(' + "'" + i + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                    str_html += "</td>";
                    str_html += "</tr>";
                }
            }
            else {
                str_html += "<tr>";
                str_html += '<td colspan="12" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_html += '</tr>';
            }
            var str_html1 = "";
                console.log(SECTION_JSON_DATA)
            str_html1 += "<option value='0'>空</option>";
            for (var s in SECTION_JSON_DATA[section]["build"]) {
                str_html1 += "<option value='" + s + "'>" + SECTION_JSON_DATA[section]["build"][s]["name_CN"] + "</option>";
            }
            console.log(recharge_gift);
            $("#buttonid").html(str_html1);

            $("#notice_list").html(str_html);
        },
        error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
    });
};

$("#select_section").on("change", function (e) {
    e.preventDefault();
    get_notice_data();
});


$("#select_server").on("change", function (e) {
    e.preventDefault();
    var server_val = $("#select_server").val();
    if (server_val == "other") {
        $("#input_server").show();
    }
    else {
        $("#input_server").hide();
    }
});

$("#add_system_notice").on("click", function (e) {
    e.preventDefault();
//    var section = $("#select_section").val();
//    getGameServerDataCheck3($("#select_server"), section);

    var $notice_id = $("#notice_id");
    $notice_id.val(parseInt(recharge_gift) + 1);
//    $notice_id.attr("disabled", true);
    $("#start_server").val("");
    $("#end_server").val("");
    $("#notice_title").val("");

//    var pic_name_text = "";
//    pic_name_text += "<option value=''>" + "请选择" + "</option>";

//    for (var i in pic_name_list){
//        pic_name_text += "<option value='" + pic_name_list[i] + "'>" + pic_name_list[i] + "</option>";
//    }
//    $("#pic_name1").html(pic_name_text);

    $("#display").val("");
    $("#title_content").val("");
    $("#title_time").val("【活动时间】:");
    $("#content").val("【活动内容】:");
    $("#reward").val("【活动奖励】:");
    $("#picture_select").val("");
    $("#select_type").change();
    $("#end_day").val("");
    $("#system_notice_modal").modal("show");
});

$("#picture_select").on("change", function (e) {
    var picture_select = $("#picture_select").val();
    if (picture_select == "") {
        $("#div_platform").show();
        $("#div_pic").show();
    }
    else {
        $("#div_platform").hide();
        $("#div_pic").hide();
    }
});


$("#select_type").on("change", function (e) {
    var select_type = $("#select_type").val();
    if (select_type == "1") {
        $("#param1").show();
        $("#param1_1").hide();

        $("#param2_1").show();
        $("#param2").hide();
    }
    else {
        $("#param1").hide();
        $("#param1_1").show();

        $("#param2_1").hide();
        $("#param2").show();
    }
});


var operate_notice = function (div_modal) {
    var section = $("#select_section").val();
    $.ajax(
        {
            url: "/operatesystemnotice",
            type: "post",
            data: {
                section: section,
                notice_data: JSON.stringify(SECTION_JSON_DATA[section]["notice_3"])
            },
            dataType: 'json',
            success: function (data, status) {
                if (data["status"] == "fail") {
                    Common.alert_message($("#error_modal"), 0, "处理失败.");
                }
                div_modal.modal("hide");
                get_notice_data();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
};


$("#btn_notice").on("click", function (e) {
    e.preventDefault();
    var section = $("#select_section").val();
    var $alert_span = $(".alert-danger span");
    var $alert_show = $('.alert-danger', $('#system_notice_form'));

    var notice_id = $("#notice_id").val();
    if (notice_id == "" || !isNaN(notice_id) == false) {
        $alert_span.html("编号不能为空且为数字");
        $alert_show.show();
        return;
    }
    else {
        $alert_show.hide();
    }
    //判断编号是否重复
    if (SECTION_JSON_DATA[section].hasOwnProperty(notice_id)) {
        $alert_span.html("编号冲突");
        $alert_show.show();
        return;
    }
    else {
        $alert_show.hide();
    }

    var server = "";
//    $("#game_server").on("each", function (e) {
//        server += $(this).val() + ",";
//    });

    var notice_title = $("#notice_title").val();
    if (notice_title == "") {
        $alert_span.html("");
        $alert_show.show();
        return;
    } else {
        $alert_show.hide();
    }

    var display = $("#display").val();
    if (display == "" || !isNaN(display) == false) {
        $alert_span.html("排序不能为空且为数字");
        $alert_show.show();
        return;
    } else {
        $alert_show.hide();
    }


    var title_time = $("#title_time").val();

    var content = $("#content").val();
    var reward = $("#reward").val();
    var buttonid = parseInt($("#buttonid").val());
    var select_type = $("#select_type").val();

    var pic_name = $("#pic_name").val();

    var param1 = "";
    var param2 = "";
    if (select_type == "1") {
        param1 = $("#select_param1").val();
        param2 = $("#end_day").val();
    }
    else {
        var param1_date = $("#param1_date").val().split("-");
        var param2_date = $("#param2_date").val().split("-");
        param1 = param1_date[0] + param1_date[1] + param1_date[2] + "000000";
        param2 = param2_date[0] + param2_date[1] + param2_date[2] + "000000";
    }

    SECTION_JSON_DATA[section]["notice_3"][notice_id] = {
        id: parseInt(notice_id),
        title: notice_title,
        display: parseInt(display),
        pic: pic_name,
        title_content_CN: $('#title_content_cn').val(),
        title_content_VI: $('#title_content_vi').val(),
        title_time:   title_time,
        content:  content,
        reward: reward,
        button: buttonid,
        type: parseInt(select_type),
        param1: param1,
        param2: param2,
        server: server,
        ishot: 1,
        notice_type: 2
    };
    operate_notice($("#system_notice_modal"));
});


var mod_notice = function (nid) {
    var section = $("#select_section").val();
   // getGameServerDataCheck3($("#select_server"), section);
    $("#notice_id").attr("disabled", false);
    $("#notice_id").val(nid);
//    var server = SECTION_JSON_DATA[section]["notice_3"][nid]["server"];
//    var server_list = server.split(",");
//    for (var s = 0; s < server_list.length; s++) {
//        if (server_list[s] != "") {
//            var in_game = $("input[name='game_server'][value='" + server_list[s] + "']");
//            in_game.prop("checked", true);
//            in_game.parent("span").addClass("checked");
//        }
//    }
    $("#notice_title").val(SECTION_JSON_DATA[section]["notice_3"][nid]["title"]);
    $("#display").val(SECTION_JSON_DATA[section]["notice_3"][nid]["display"]);
    $("#pic_name").val(SECTION_JSON_DATA[section]["notice_3"][nid]["pic"]);

//    var pic_name_text = '';
//    for (var i in pic_name_list){
//        pic_name_text += "<option value='" + pic_name_list[i] + "'>" + pic_name_list[i] + "</option>";
//    }
//    $("#pic_name1").html(pic_name_text);

    $("#title_content").val(SECTION_JSON_DATA[section]["notice_3"][nid]["title_content"]);
    $("#title_time").val(SECTION_JSON_DATA[section]["notice_3"][nid]["title_time"]);
    $("#content").val(SECTION_JSON_DATA[section]["notice_3"][nid]["content"]);
    $("#reward").val(SECTION_JSON_DATA[section]["notice_3"][nid]["reward"]);
    $("#buttonid").val(SECTION_JSON_DATA[section]["notice_3"][nid]["button"]);
    var notice_type = SECTION_JSON_DATA[section]["notice_3"][nid]["type"];
    var param1 = SECTION_JSON_DATA[section]["notice_3"][nid]["param1"];
    var param2 = SECTION_JSON_DATA[section]["notice_3"][nid]["param2"];
    $("#select_type").val(notice_type);
    $("#select_type").change();
    if (notice_type == "1") {
        $("#select_param1").val(param1);
        $("#end_day").val(param2);
    }
    else {
        var p1 = param1.substring(0, 4) + "-" + param1.substring(4, 6) + "-" + param1.substring(6, 8);
        var p2 = param2.substring(0, 4) + "-" + param2.substring(4, 6) + "-" + param2.substring(6, 8);
        $("#param1_date").val(p1);
        $("#param2_date").val(p2);
    }
    $("#system_notice_modal").modal("show");
};

var del_notice = function (nid) {
    $("#system_notice_del_modal").modal("show");

    $("#confirm_system_del").attr('onclick', "confirm_del_system_notice(" + nid + ")");
};

function confirm_del_system_notice(nid) {
    var section = $("#select_section").val();
    delete SECTION_JSON_DATA[section]["notice_3"][nid];
    operate_notice($("#system_notice_del_modal"));
}


$("#reload_config").on("click", function(e){
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/reloadconfig',
            dataType: 'JSON',
            data: {'section':  $("#select_section").val(),'config_id': config_id},
            success: function (data) {
                App.unblockUI(page_content);
                //console.log(data);
                if (data["status"] == "success") {
                    Common.alert_message($("#error_modal"), 1, "配置加载成功.");
                }
                else {
                    Common.alert_message($("#error_modal"), 0, "配置加载失败.")
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});
