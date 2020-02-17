/**
 * Created by wangrui on 14-10-14.
 */

create_del_modal($("#task_del_modal"), "是否删除此信息?", "del_task");

handleDatePickers2();
handleTimePickers();
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));

var $hide_common = $("input[name='hide_common']");
var $version_list = $("#version_list");
var $btn_confirm_upload = $("#btn_confirm_upload");

var compare_cid = 0;
var current_version = 0;
var new_section_file = $("#new_section_file");
var upload_table_title = $("#upload_table_title");
var upload_title_data = ["文件名", "状态", "结果", "时间校验", '操作'];

function show_upload_title(){
    show_table_title(upload_title_data, upload_table_title)
}
show_upload_title();

var auth_upload = function (div_modal){
    var user_upload = $.cookie("user_upload");
    if (user_upload == "1"){
        $("#new_upload_modal").modal("show");
    }
    else{
        Common.alert_message($("#error_modal"), 0, "无权限上传文件");
    }
};



$("#new_upload_file").on("click", function(e){
    e.preventDefault();
    auth_upload($("#upload_modal"));
});


//查询分区表
var getSection = function () {
    var success = function(data){
        if (data.length != 0) {
            var str_info = "";
            for (var i in data) {
                str_info += "<option value='" + data[i].id + "'>" + data[i].name + "</option>";
            }
            new_section_file.html(str_info);
            new_section_file.change();
        }
    };
    my_ajax(true, "/querysection", "get", {}, true, success);
};
getSection();



new_section_file.on("change", function (e) {
    e.preventDefault();
    var select_type = $('#new_select_type');
    var effective_type = $("#effective_type");
    var section_id = $(this).val();
    var new_section_file_name = $("option:checked", this).text();
    var success = function (data) {
        var str_info = "<option value='0'>请选择</option>";
        if (data.length != 0) {
            for (var i = 0; i < data.length; i++) {
                str_info += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + ", " + data[i]["alias"] + "</option>";
            }
        }
        select_type.html(str_info);
        select_type.val("0").trigger('change');
        effective_type.html(str_info);
        effective_type.val("0").trigger('change');
    };

    $("#section_name").html(new_section_file_name);
    var data = {
        section_id: section_id
    };
    my_ajax(true, '/querytype2', 'get', data, true, success);
});


$('#new_select_type').on("change", function (e) {
    e.preventDefault();
    get_config_data();
});


$hide_common.on("change", function (e) {
    e.preventDefault();
    if ($(this).prop('checked')){
        $("#excel_data tr[class='default']").hide();
    }
    else{
        $("#excel_data tr[class='default']").show();
    }
});



function common_compare_excel(cid, last_version){

    var success = function(data){
        var str_html = "";
        var title_cn = data["title_cn"];
        var title = data["title"];
        var str_title = "";
        str_title += "<tr>";
        for(var i=0; i<title_cn.length; i++){
            str_title += "<th>" + title_cn[i] + "</th>";
        }
        str_title += "</tr>";
        str_title += "<tr>";
        for(var h=0; h<title.length; h++){
            str_title += "<th>" + title[h] + "</th>";
        }
        str_title += "</tr>";
        $("#excel_title").html(str_title);

        var excel_data = data["data"];
        $("#excel_data").html("");
        for(var k=0; k<excel_data.length; k++){
            var temp_html = "";
            var s_tag = false;
            for (var m=0; m<excel_data[k].length; m++){
                var tag = excel_data[k][m][1];
                var td_class = "";
                if (tag == 1){
                    td_class = "active";
                }
                else if (tag == 2){
                    td_class = "warning";
                    s_tag = true;
                }
                else if (tag == 3){
                    td_class = "success";
                    s_tag = true;
                }
                else if (tag == 4){
                    td_class = "danger";
                    s_tag = true;
                }
                temp_html += "<td class='" + td_class +  "'>" + excel_data[k][m][0] + "</td>";
            }
            var str_html2 = "";
            if (s_tag){
                str_html2 += "<tr>";
            }
            else{
                str_html2 += "<tr class='default'>";
            }
            str_html2 += temp_html;
            str_html2 += "</tr>";
            $("#excel_data").append(str_html2);
        }
        var version_html = '当前版本:' + current_version + '</span>';
        $("#current_version_label").html(version_html);
        var diff_html = "";
        if (data["change"]["row_add"] != 0){
            diff_html += "<span style='color:green'>行新增:<span style='font-size:32px'>"+ data["change"]["row_add"] + "</span></span>";
        }
        else{
            diff_html += "<span style='color:green'>行新增:</span>"+ data["change"]["row_add"] ;
        }
        if (data["change"]["row_del"] != 0){
            diff_html += "<span style='color:red'>行删除:<span style='font-size:32px'>"+ data["change"]["row_del"] + "</span></span>";
        }
        else{
            diff_html += "<span style='color:red'>行删除:</span>"+ data["change"]["row_del"] ;
        }
        if (data["change"]["mod"] != 0){
            diff_html += "<span style='color:#ffb848'>修改:<span style='font-size:32px'>"+ data["change"]["mod"] + "</span></span>";
        }
        else{
            diff_html += "修改:"+ data["change"]["mod"] ;
        }
        if (data["change"]["col_add"] != 0){
            diff_html += "<span style='color:green'>列新增:<span style='font-size:32px'>"+ data["change"]["col_add"] + "</span></span>";
        }
        else{
            diff_html += "<span style='color:green'>列新增:</span>"+ data["change"]["col_add"] ;
        }
        if (data["change"]["col_del"] != 0){
            diff_html += "<span style='color:red'>列删除:<span style='font-size:32px'>"+ data["change"]["col_del"] + "</span></span>";
        }
        else{
            diff_html += "<span style='color:red'>列删除:</span>"+ data["change"]["col_del"] ;
        }
        $("#diff_excel").html(diff_html);
        $("#compare_modal").modal("show");
        $hide_common.change();
    };
    var req_data = {
        cid: cid,
        version: last_version
    };
    my_ajax(true, "/config/compare", 'get', req_data, true, success);
}

$btn_confirm_upload.on("click", function (e) {
    e.preventDefault();
    $("#compare_modal").modal("hide");
    set_effective(compare_cid);
});


$("#close_compare").on("click", function (e) {
    e.preventDefault();
    $("#compare_modal").modal("hide");
    get_config_data();
});



function get_version_list(cid){
    var success = function(data){
        var str_html = "";
        var s_ver = 1;
        if (data.length != 0){
            for (var i = 0; i < data.length; i++) {
                if (data[i]["status"] == "online") {
                    str_html += "<option value='" + data[i]["version"] + "'>线上版本:" + data[i]["version"] + "</option>";
                    s_ver = data[i]["version"];
                }
                else {
                    str_html += "<option value='" + data[i]["version"] + "'>版本:" + data[i]["version"] + "</option>";
                }
            }
        }
        $version_list.html(str_html);
        $version_list.val(s_ver).trigger("change");
    };
    var data = {
        cid: cid
    };
    my_ajax(true, '/config/queryversion', 'get', data, false, success);
}

function compare_excel(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#new_file_table").dataTable().fnGetData(nRoW);

    var s_type = data["s_type"];
    var s_type_alias = data["alias"];
    var str_com_html = "配置表:" + s_type + "(" + s_type_alias + ")";
    current_version = data["version"];
    $("#compare_name").html(str_com_html);

    compare_cid = data["id"];
    get_version_list(compare_cid);
}

$version_list.on("change", function (e) {
    e.preventDefault();
    var choose_version = $(this).val();
    common_compare_excel(compare_cid, choose_version);
});


function display_excel(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#new_file_table").dataTable().fnGetData(nRoW);

    var s_type = data["s_type"];
    var s_type_alias = data["alias"];
    current_version = data["version"];
    compare_cid = data["id"];

    $("#excel_name").html(s_type + s_type_alias);

    var cid = data["id"];
    var success = function (data) {
        var display_data = data;
        var title_cn = display_data["title_cn"];
        var title = display_data["title"];
        var str_title = "";
        str_title += "<tr>";
        for (var i = 0; i < title_cn.length; i++) {
            str_title += "<th>" + title_cn[i] + "</th>";
        }
        str_title += "</tr>";
        str_title += "<tr>";
        for (var h = 0; h < title.length; h++) {
            str_title += "<th>" + title[h] + "</th>";
        }
        str_title += "</tr>";
        $("#dis_excel_title").html(str_title);

        var str_html = "";
        var excel_data = display_data["data"];
        for (var k = 0; k < excel_data.length; k++) {
            str_html += "<tr>";
            for (var m = 0; m < excel_data[k].length; m++) {
                str_html += "<td class='active'>" + excel_data[k][m] + "</td>";
            }
            str_html += "</tr>";
        }
        $("#dis_excel_data").html(str_html);
        $("#display_excel_modal").modal("show");
        };
    var req_data = {cid: cid};
    my_ajax(true, "/config/displayexcel", 'get', req_data, true, success);
}



function get_config_data(){
    var sAjaxSource = "/config/queryexcel";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "excelurl",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "s_type",
            'sClass': 'center',
            "sTitle": "配置类型"
        },
        {
            "mDataProp": "alias",
            'sClass': 'center',
            "sTitle": "中文名称"
        },
        {
            "mDataProp": "version",
            'sClass': 'center',
            "sTitle": "版本"
        },
        {
            "mDataProp": "who",
            'sClass': 'center',
            "sTitle": "上传者"
        },
        {
            "mDataProp": "upload_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "sTitle": "描述"
        },
        {
            "sTitle": "操作1",
            "sClass": "center",
            "sDefaultContent": ""
        },
        {
            "sTitle": "操作2",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html1 = '';
        var str_html2 = "";
        var str_html3 = "";

        str_html3 += "&nbsp;<button type='button' onclick=\"display_excel(this)\" class=\"btn default btn-xs grey-gallery\">查看</button>";
        str_html3 += "&nbsp;<button type='button' onclick=\"compare_excel(this)\" class=\"btn default btn-xs blue-madison\">对比</button>";
        if (aData.status == 'invalid'){
            str_html1 = '<span class="badge badge-danger">无效</span>';
            str_html2 += "<button type='button' onclick=\"mod_config(this)\" class=\"btn default btn-xs\">修改</button>";
            str_html2 += "<button type='button' onclick=\"effective(this)\" class=\"btn default btn-xs blue\">有效</button>";

        }
        else if (aData.status == 'effective'){
            str_html1 = '<span class="badge badge-info">有效</span>';
            str_html2 += "<button type='button' onclick=\"mod_config(this)\" class=\"btn default btn-xs\">修改</button>";
            str_html2 += '&nbsp;<a download target="_blank" class="btn btn-xs blue-madison" href="';
            str_html2 += aData.excelurl + '">下载</a>';
        }
        else{
            str_html1 = '<span class="badge badge-success">上线</span>';
            str_html2 += "<button type='button' onclick=\"mod_config(this)\" class=\"btn default btn-xs\">修改</button>";
            str_html2 += '&nbsp;<a download target="_blank" class="btn btn-xs blue-madison" href="';
            str_html2 += aData.excelurl + '">下载</a>';
        }

        $('td:eq(1)', nRow).html(aData.alias + str_html1);
        $('td:eq(2)', nRow).html("<span class='badge badge-success'>" + aData.version + "</span>");
        $('td:eq(6)', nRow).html(str_html2);
        $('td:eq(7)', nRow).html(str_html3);

        return nRow;
    };

    var data = {
        section_id: new_section_file.val(),
        section_type: $("#new_select_type").val()
    };
    dataTablePage($("#new_file_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
}


var mod_config = function (cid){
    var nRow = $(cid).parents('tr')[0];
    var data = $("#new_file_table").dataTable().fnGetData(nRow);
    $("#config_cid").val(data["id"]);
    $("#config_desc_info").html(data["desc"]);
    $("#config_modal").modal("show");
};


$("#btn_confirm_desc").on("click", function (e) {
    e.preventDefault();
    var success = function (data) {
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "修改失败.");
        }
        $("#config_modal").modal("hide");
        get_config_data();
    };
    var req_data = {
        "cid": $("#config_cid").val(),
        "config_desc": $("#config_desc_info").val()
    };
    my_ajax(true, "/config/updatedesc", "get", req_data, true, success);
});


var set_effective = function(cid){
    var success = function(data){
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "设置失败");
        }
        get_config_data();
    };
    var req_data = {
        "cid": cid
    };
    my_ajax(true, "/config/seteffective", 'get', req_data, true, success);

};



var effective = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#new_file_table").dataTable().fnGetData(nRoW);
    var cid = data["id"];

    set_effective(cid)
};

var online_data = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#new_file_table").dataTable().fnGetData(nRoW);
    var cid = data["id"];
    set_online(cid)
};

$("#add_effective").on("click", function (e) {
    e.preventDefault();
    $("#effective_modal").modal("show");
});


// $("#btn_query").on("click", function (e) {
//     e.preventDefault();
//     get_config_data();
// });



$("#close_upload_btn").on("click", function (e) {
    e.preventDefault();
    $("#upload_modal").modal("hide");
    get_config_data();
});

//新配置文件点击上传
$("#btn_upload_excel").on("click", function (e) {
    e.preventDefault();
    $("#new_upload_modal").modal("hide");
    App.blockUI($page_content, false);
    $.ajaxFileUpload(
        {
            url: "/config/uploadexcel",
            secureuri: false,
            type: "post",
            fileElementId: 'new_excel_file',
            data: {
                section: new_section_file.val(),
                excel_status: $("#excel_status").val(),
                file_desc: $("#new_file_desc").val()
            },
            dataType: 'json',
            success: function (data, status){
                App.unblockUI($page_content);
                var str_html1 = "";
                for(var i=0; i<data.length; i++){
                    str_html1 += "<tr>";
                    str_html1 += "<td>" + data[i]["filename"] + "</td>";
                    var status1 = data[i]["status"];
                    if (status1 == "success"){
                        str_html1 += "<td><span class='badge badge-success'>成功</span></td>";
                        str_html1 += "<td>" + "行新增:<span class='badge badge-success'>" + data[i]["change"]["row_add"] + "</span>"
                                + "行删除:<span class='badge badge-danger'>" + data[i]["change"]["row_del"] + "</span>"
                            + "修改:<span class='badge badge-warning'>" + data[i]["change"]["mod"] + "</span>"
                            + "列新增:<span class='badge badge-success'>" + data[i]["change"]["col_add"] + "</span>"
                            + "列删除:<span class='badge badge-danger'>" + data[i]["change"]["col_del"] + "</span>" + "</td>";

                        if (data[i]["error"] == 5){
                            str_html1 += "<td>开启的活动时间发生改变,活动编号:" + data[i]["msg"] + "</td>";
                        }
                        else{
                            str_html1 += "<td></td>";
                        }
                        str_html1 += "<td><button onclick=\"commpare_this(" + data[i]["data"]["id"] + "," + data[i]["data"]["version"] + ")\" class=\"btn default btn-xs blue\">比较</button></td>";
                    }
                    else{
                        str_html1 += "<td><span class='badge badge-danger'>失败</span></td>";
                        var error = data[i]["error"];
                        var str_html = "";
                        if (data[i]["error"] == 1) {
                            str_html = "文件名不符合规则";
                        }
                        else if (data[i]["error"] == 2) {
                            str_html = "缺少配置表类型主键";
                        }
                        else if (data[i]["error"] == 3) {
                            str_html = "文件内容错误";
                        }
                        else if (data[i]["error"] == 4){
                            str_html = "时间格式错误,活动编号:" + data[i]["msg"];
                        }
                        else if (data[i]["error"] == 5){
                            str_html = "活动时间发生变化,活动编号:" + data[i]["msg"];
                        }
                        else if (data[i]["error"] == 6){
                            str_html = "生成json出错,错误列:" + data[i]["msg"];
                        }
                        str_html1 += "<td>" + str_html + "</td>";
                        str_html1 += "<td></td>";
                        str_html1 += "<td></td>";
                    }
                    str_html1 += "<tr>";
                }
                $("#upload_list").html(str_html1);
                $("#upload_modal").modal("show");
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
});

var commpare_this = function(compare_id, version){
    current_version = version;
    compare_cid = compare_id;
    $("#upload_modal").modal("hide");
    get_version_list(compare_id);
};




var query_config_log = function () {
    var sAjaxSource = "/config/querylog";
    var aoColumns = [
        {
            "mDataProp": "username",
            'sClass': 'center',
            "sTitle": "用户"
        },
        {
            "mDataProp": "opt",
            "sClass": "center",
            "sTitle": "操作1"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "配置类型"
        },
        {
            "mDataProp": "alias",
            'sClass': 'center',
            "sTitle": "配置名称"
        },
        {
            "mDataProp": "version",
            'sClass': 'center',
            "sTitle": "版本"
        },
        {
            "mDataProp": "opt_time",
            'sClass': 'center',
            "sTitle": "时间"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html1 = '';
        var opt = aData["opt"];
        if (opt === "upload"){
            str_html1 = "上传";
        }
        else if (opt == "effective"){
            str_html1 = "生效";
        }
        else{
            str_html1 = "上线";
        }

        $('td:eq(1)', nRow).html(str_html1);

        return nRow;
    };

    dataTablePage($("#config_log_table"), aoColumns, sAjaxSource, {}, false, fnRowCallback);
};


$("#a_config_log").on("click", function(e){
    e.preventDefault();
    query_config_log();
});


var query_task_info = function () {
    var sAjaxSource = "/task/querytask";
    var aoColumns = [
        {
            "mDataProp": "username",
            'sClass': 'center',
            "sTitle": "用户"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "任务名称"
        },
        {
            "mDataProp": "auto_time",
            "sClass": "center",
            "sTitle": "执行时间"
        },
        {
            "mDataProp": "restart_game",
            'sClass': 'center',
            "sTitle": "是否重启游戏"
        },
        {
            "mDataProp": "restart_ext",
            'sClass': 'center',
            "sTitle": "是否重启扩展"
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "sTitle": "描述信息"
        },
        {
            "mDataProp": "opt_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_task(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_task(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {

        return nRow;
    };
    var data = {
        tag: 1
    };
    dataTablePage($("#task_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
};


$("#a_config_auto").on("click", function (e) {
    e.preventDefault();
    query_task_info();
});


$("#add_task").on("click", function (e) {
    e.preventDefault();
    $("#task_id").val("");
    $("#task_modal").modal("show");
});


var mod_task = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#task_table").dataTable().fnGetData(nRoW);
    $("#task_id").val(data["id"]);
    var opentime = data["auto_time"];
    var opentime_split = opentime.split(" ");
    $("#task_date").val(opentime_split[0]);
    $("#task_time").val(opentime_split[1]);
    $("#task_desc").val(data["desc"]);
    $("#task_modal").modal("show");
};


var del_task = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#task_table").dataTable().fnGetData(nRoW);
    $('#task_del_modal').modal("show");
    $("#del_task").attr('onclick', "confirm_del_task(" + data["id"] + ")");
};

var confirm_del_task = function (task_id) {
    var success = function(data){
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#del_openserver_modal').modal("hide");
        get_openserver();
    };
    var data = {
        task_id: task_id
    };
    my_ajax(true, '/task/delete', 'get', data, true, success);
};

var cancel_choose = function(name){
    var radio_name = $("input[name="+ name + "]");
    radio_name.removeAttr("checked");
};


var delete_effective = function(cid){
    var success = function (data) {
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "移除失败.");
        }
        get_effective_list(2);
    };

    var data = {
        cid: cid
    };
    my_ajax(true, "/config/removeconfig", 'get', data, true, success);
};

function get_effective_list(tag) {
    var success = function (data) {
        var str_html = "";
        for(var i in data){
            str_html += "<tr>";
            var len_data = data[i].length;

            for (var s = 0; s<len_data; s++){
                if (s == 0){
                    str_html += "<td rowspan='" + len_data + "' style='vertical-align: middle;text-align: center;'>" + data[i][0]["name"] + "</td>";
                    str_html += "<td rowspan='" + len_data + "' style='vertical-align: middle;text-align: center;'>" + data[i][0]["ctype"] + "</td>";
                }
                str_html += "<td><input checked type='radio'" + "name='" + data[i][s]["name"] + "'" + "value='" + data[i][s]["id"] + "'>"
                    + data[i][s]["version"] + "</td>";
                str_html += "<td>"+ data[i][s]["desc"] + "</td>";
                str_html += "<td><a class='badge badge-info' onclick=\"cancel_choose('" + data[i][s]["name"] + "')\">" + "取消"  + "</a>";
                str_html += "<a class='badge badge-danger' onclick=\"delete_effective(" + data[i][s]["id"] + ")\">" + "移除"  + "</a></td>";
                str_html += "</tr>";
            }
        }
        $("#effective_table").html(str_html);
        if (tag == 1){
            $("#effective_modal").modal("show");
        }

    };
    console.log($("#task_id").val());
    var req_data = {
        section: new_section_file.val(),
        task_id: $("#task_id").val()
    };
    my_ajax(true, "/config/geteffectivelist", "get", req_data, true, success);
}

$("#btn_online").on("click", function (e) {
    e.preventDefault();
    query_task();
    get_effective_list(1);
});



$("#btn_confirm_choose").on("click", function (e) {
    e.preventDefault();
    var effective_type =  $("#effective_type").val();
    if (effective_type != "0") {
        var success = function (data) {
        var str_html = "";
        for(var i in data){
                str_html += "<tr>";
                var len_data = data[i].length;

                for (var s = 0; s<len_data; s++){
                    if (s == 0){
                        str_html += "<td rowspan='" + len_data + "' style='vertical-align: middle;text-align: center;'>" + data[i][0]["name"] + "</td>";
                        str_html += "<td rowspan='" + len_data + "' style='vertical-align: middle;text-align: center;'>" + data[i][0]["ctype"] + "</td>";
                        str_html += "<td><input checked type='radio'" + "name='" + data[i][s]["name"] + "'" + "value='" + data[i][s]["id"] + "'>"
                                    + data[i][s]["version"] + "</td>";
                        str_html += "<td>"+ data[i][s]["desc"] + "</td>";
                        str_html += "<td rowspan='" + len_data + "'><a class='badge badge-info' onclick=\"cancel_choose('" + data[i][s]["name"] + "')\">" + "取消"  + "</a>";
                    }
                    else{
                        str_html += "<td><input type='radio'" + "name='" + data[i][s]["name"] + "'" + "value='" + data[i][s]["id"] + "'>"
                        + data[i][s]["version"] + "</td>";
                        str_html += "<td>"+ data[i][s]["desc"] + "</td>";
                    }
                    str_html += "</tr>";
                }
            }
            $("#effective_table").append(str_html);
            $("#effective_choose_modal").modal("hide");
        };
        var req_data = {
            section: new_section_file.val(),
            effective_type: $("#effective_type").val()
        };
        my_ajax(true, "/config/geteffectivelist2", "get", req_data, true, success);
    }
    else{
        Common.alert_message($("#error_modal"), 0, "请选择类型");
    }

});

$("#btn_confirm_online").on("click", function (e) {
    e.preventDefault();
    var tag = false;
    var check_type_list = [];
    $("input:radio").each(function (e) {
        if ($(this).is(":checked")){
            check_type_list.push($(this).val());
            tag = true;
        }
    });
    $("#effective_modal").modal("hide");
    if (tag == false){
        $("#effective_modal").modal("hide");
        Common.alert_message($("#error_modal"), 0, "请至少选择一个版本.");
    }
    else{
        var success = function(data){
            if (data["status"] == "success"){
                Common.alert_message($("#error_modal"), 1, "上线成功.");
            }
            else if (data["status"] == "busy"){
                Common.alert_message($("#error_modal"), 0, "正在处理其他任务,请稍后重试.");
            }
            else if (data["status"] == "error"){
                Common.alert_message($("#error_modal"), 0, "上线错误,请联系相关人员.");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "上线失败.");
            }
            get_config_data();
        };
        var restart_game = 0;
        var restart_ext = 0;
        $("input[name='online_type']").each(function(e){
             if ($(this).is(":checked")){
                 var v_p = $(this).val();
                 if (v_p == "1"){
                     restart_game = 1
                 }
                 else if (v_p == "2"){
                     restart_ext = 1
                 }

             }
        });
        var task_date = $("#task_date").val();
        var task_time = $("#task_time").val();
        var task_datetime = task_date + " " + task_time;
        var req_data = {
            "section": new_section_file.val(),
            "type_list": JSON.stringify(check_type_list),
            "online_model": $("#online_model").val(),
            "task_id": $("#task_id").val(),
            "task_name": $("#task_name").val(),
            "task_datetime": task_datetime,
            "restart_game": restart_game,
            "restart_ext": restart_ext,
            "task_desc": $("#task_desc").val()
        };
        my_ajax(true, "/config/setallonline", 'post', req_data, true, success);
        get_config_data();
    }
});

var taskValidation = function () {
    var form1 = $('#task_form');
    var rules = {
    };
    var messages = {
    };

    var submitFunction = function (form) {
        var task_id = $("#task_id").val();
        var task_date = $("#task_date").val();
        var task_time = $("#task_time").val();
        var task_time2 = task_date + " " + task_time;
        var restart_game = $("input[name='restart_game']:checked").val();
        if (typeof(restart_game) == "undefined"){
            restart_game = 0;
        }
        var restart_ext = $("input[name='restart_ext']:checked").val();
        if (typeof(restart_ext) == 'undefined'){
            restart_ext = 0;
        }
        var task_desc = $("#task_desc").val();
        var success = function (data) {
            if (data.status == 'fail') {
                Common.alert_message($("#error_modal"), 0, "操作失败.")
            }
            $("#task_modal").modal("hide");
            $("#a_config_auto").click();
        };
        var data = {
            task_id: task_id,
            auto_time: task_time2,
            restart_game: restart_game,
            restart_ext: restart_ext,
            task_desc: task_desc
        };
        my_ajax(true, '/task/operate', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};
taskValidation();

var task_data = {};

var query_task = function (){
    var success = function (data) {
        var str_html = "<option value='0'>新任务</option>";
        for (var d = 0; d < data.length; d++) {
            str_html += "<option value='" + data[d]["id"] + "'>" + data[d]["name"] + "</option>";
            task_data[data[d]["id"]] = data[d];
        }
        $("#task_id").html(str_html);
        $("#task_id").val("0").trigger('change');
    };
    var data = {
        tag: 2
    };

    my_ajax(true, "/task/querytask", 'get', data, false, success);

};


$("#online_model").on("change", function (e) {
    e.preventDefault();
    var online_model = $(this).val();
    if (online_model == "1"){
        $("#auto_task_name").addClass("hidden");
        $("#auto_task").addClass("hidden");
        $("#auto_desc").addClass("hidden");
        $("#auto_date").addClass("hidden");
        $("#auto_time").addClass("hidden");
        $("#auto_game").addClass("hidden");
    }
    else{
        $("#auto_task_name").removeClass("hidden");
        $("#auto_task").removeClass("hidden");
        $("#auto_desc").removeClass("hidden");
        $("#auto_date").removeClass("hidden");
        $("#auto_time").removeClass("hidden");
        $("#auto_game").removeClass("hidden");
    }
    $("#task_id").change();
});


$("#task_id").on("change", function (e) {
    e.preventDefault();
    get_effective_list(2);
    var task_id = $(this).val();
    if (task_id != "0"){
        $("#task_name").val(task_data[task_id]["name"]);
        var t_date = task_data[task_id]["auto_time"];
        var restart_game = task_data[task_id]["restart_game"];
        var auto_desc = task_data[task_id]["auto_desc"];
        var s_date_arr = t_date.split(" ");
        var s_date = s_date_arr[0];
        var s_time = s_date_arr[1];
        $("#task_date").val(s_date);
        $("#task_time").val(s_time);
        $("#auto_desc").val(auto_desc);
    }
    else{
        $("#task_name").val("");
        $("#task_date").val("");
        $("#task_time").val("");
        $("#auto_desc").val("");
    }
});
