/**
 * Created by wangrui on 14/12/18.
 */

var folder = {
    "battle": "battle",
    "common_lua": "common_lua",
    "config": "config",
    "pb": "pb",
    "scripts": "scripts",
    "spine": "spine",
    "UI": "UI",
    "music": "music"
};

var PLAT_FORM = {
    "ios": "苹果",
    "android": "安卓",
    "all": "所有"
};

var tag = true;
var lan = "qingyuan";

var get_resource = function () {
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: "/getresourceversion2",
            data: {
                language: lan
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                for (var i = 0; i < data.length; i++) {
                    str_info += "<option value='" + data[i]["id"] + "'>" + data[i]["id"] + "</option>";
                }
                var $version1 = $("#select_version");
                var $version2 = $("#select_version1");
                var $version3 = $("#select_version_zip");
                $version1.html(str_info);
                $version2.html(str_info);
                $version3.html(str_info);
//                $version1.searchableSelect().hide();
//                $version1.searchableSelect().show();
//                if (tag){
//                    $version2.searchableSelect();
//                    $version3.searchableSelect();
//                    tag = false;
//                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
};
get_resource();

var create_folder_html = function () {
    var htmlstr = [];
    var select_folder = $("#select_folder");
    for (var f in folder) {
        htmlstr.push("<option value='" + folder[f] + "'>" + folder[f] + "</option>");
    }
    select_folder.html(htmlstr.join(""));
};
create_folder_html();

$("#resource_file").bind("click", function (e) {
    e.preventDefault();

    $("#select_version").change();
});

$("#version_add").bind("click", function (e) {
    e.preventDefault();
    $("#resource_version").val("");
    $("#select_status").html("<option value='prepare'>准备</option>");

    $("#version_desc").val("");
    $("#version_modal").modal("show");
});

var Start = 0;
var End = 10;

var get_version_list = function () {
    $('#version_table').dataTable({
        "oLanguage": oLanguage,
        "aoColumns": [
            {
                "mDataProp": "id",
                'sClass': 'center',
                "sTitle": "版本"
            },
            {
                "mDataProp": "updatetime",
                'sClass': 'center',
                "sTitle": "时间"
            },
            {
                "mDataProp": "status",
                'sClass': 'center',
                "sTitle": "状态"
            },
            {
                "mDataProp": "needrestart",
                'sClass': 'center',
                "sTitle": "是否重启"
            },
            {
                "mDataProp": "desc",
                'sClass': 'center',
                "sTitle": "描述",
                "bVisible": false
            },
            {
                "sTitle": "操作",
                "sClass": "center",
                "sDefaultContent": "<button onclick=\"mod(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>"
            }
        ],
        "fnRowCallback": function (nRow, aData, iDisplayIndex) {
            if (aData.needrestart == "yes"){
                $('td:eq(3)', nRow).html('<span class="badge badge-success">是</span>');
            }
            else{
                $('td:eq(3)', nRow).html('<span class="badge badge-danger">否</span>');
            }
            if (aData.status == "excute") {
                $('td:eq(2)', nRow).html('<span class="badge badge-success">执行</span>');
            }
            else if (aData.status == "prepare") {
                $('td:eq(2)', nRow).html('<span class="badge badge-info">准备</span>');
            }
            else if (aData.status == "error") {
                $('td:eq(2)', nRow).html('<span class="badge badge-danger">错误</span>');
            }
            return nRow;
        },
        "bPaginate": true,
        "bFilter": false,
        "bDestroy": true,
        "bLengthChange": true,
        "bWidth": true,
        "iDisplayStart": Start,
        "iDisplayLength": End,
        "bSort": false,
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": true,
        "bStateSave": false,
        "sAjaxSource": "/getresourceversion",
        "fnServerData": function (sSource, aoData, fnCallback) {
            $.ajax({
                    type: 'get',
                    url: sSource,
                    data: {language: lan, aoData: JSON.stringify(aoData)},
                    dataType: 'JSON',
                    success: function (resp) {
                        fnCallback(resp);
                    },
                    error: function (XMLHttpRequest) {
                        error_func(XMLHttpRequest);
                    }
                }
            )
        }
    });
};
get_version_list();

var mod = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#version_table").dataTable().fnGetData(nRoW);
    var select_status = $("#select_status");
    select_status.empty();
    var ready_data = "<option value='prepare'>准备</option>";
    ready_data += "<option value='excute'>执行</option>";
    ready_data += "<option value='error'>错误</option>";
    select_status.html(ready_data);
    $("#resource_version").val(data["id"]);
    select_status.val(data["status"]);
    $("#select_restart").val(data["needrestart"]);
    $("#version_desc").val(data["desc"]);
    $("#version_modal").modal("show");
};


$("#confirm_add").bind("click", function (e) {
    e.preventDefault();
    var resource_version = $("#resource_version").val();
    var select_status = $("#select_status").val();
    var version_desc = $("#version_desc").val();
    var select_restart = $("#select_restart").val();
    $.ajax({
            type: 'get',
            url: '/addresourceversion',
            data: {language: lan,
                resource_version: resource_version, status: select_status,
                select_restart: select_restart, version_desc: version_desc},
            dataType: 'JSON',
            success: function (data) {
                $("#version_modal").modal("hide");
                if (data["status"] < 0) {
                    Common.alert_message($("#error_modal"), 0, "操作失败.")
                }
                get_version_list();
                get_resource();
//                get_prepare_resource();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});


$("#select_version").bind("change", function () {
    var select_version = $("#select_version").val();
    var file_list = $("#file_list");
    $("#select_version1").val(select_version);
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/getresourcefile',
            data: {language: lan, version: select_version},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "<tr>";
                if (data.length != 0) {
                    for (var i = 0; i < data.length; i++) {
                        str_info += "<td>" + data[i]["filepath"] + "</td>";
                        str_info += "<td>" + data[i]["length"] + "</td>";
                        str_info += "<td>" + PLAT_FORM[data[i]["platform"]] + "</td>";
                        str_info += "<td>" + data[i]["updatetime"] + "</td>";
                        str_info += '<td><a target="_blank" class="btn btn-xs default blue" href="';
                        str_info += data[i]["url"] + '">下载<i class="fa fa-download"></i></a></td>';
                        str_info += "</tr>";
                    }
                }
                else {
                    str_info += '<td colspan="5" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                file_list.html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});


var choose_div = $("#choose_div").html();
$("#btn_upload").bind("click", function (e) {
    e.preventDefault();
    var select_version1 = $("#select_version1").val();
    var select_folder = $("#select_folder").val();
    var second_dir = $("#second_dir").val();
    var select_platform = $("#select_platform").val();
    var file_desc = $("#file_desc").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajaxFileUpload(
        {
            url: "/uploadresourcefile",
            secureuri: false,
            type: "post",
            fileElementId: 'resource_file_b',
            data: {
                language: lan,
                select_version1: select_version1,
                select_folder: select_folder,
                second_dir: second_dir,
                platform: select_platform,
                file_desc: file_desc
            },
            dataType: 'json',
            success: function (data, status)  //服务器成功响应处理函数
            {
                App.unblockUI(page_content);
//                $("#del_file").click();
                $("#choose_div").empty();
                $("#choose_div").html(choose_div);
                $("#upload_modal").modal("hide");
                $("#select_version").change();
            },
            error: function (data, status, e)//服务器响应失败处理函数
            {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
});


var choose_div_zip = $("#choose_div_zip").html();
$("#confirm_upload").on("click", function (e) {
    e.preventDefault();
    var select_version = $("#select_version_zip").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajaxFileUpload(
        {
            url: "/uploadresourcezipfile",
            secureuri: false,
            type: "post",
            fileElementId: 'resource_file_zip',
            data: {
                language: lan,
                select_version: select_version
            },
            dataType: 'json',
            success: function (data, status)  //服务器成功响应处理函数
            {
                App.unblockUI(page_content);
//                $("#del_file").click();
                $("#choose_div_zip").empty();
                $("#choose_div_zip").html(choose_div_zip);
                if (data["status"] == true) {
                    Common.alert_message($("#error_modal"), 1, "处理成功");
                }
                else {
                    Common.alert_message($("#error_modal"), 0, "处理失败");
                }
            },
            error: function (data, status, e)//服务器响应失败处理函数
            {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
});

function init_easy_pie_chart(){
    $('.easy-pie-chart .number.visits').easyPieChart({
        animate: 1000,
        size: 75,
        lineWidth: 5,
        barColor: App.getLayoutColorCode('green')
    });
}
init_easy_pie_chart();

var get_res_down_status = function(){
    var url = "http://182.92.161.59:3010/compress_status.php";
    var success = function(data){
        console.log(data);
        if (data["success"] == "true"){
//            $('.easy-pie-chart .number.progress').data('easyPieChart').update(data["percent"]);
            $("#progress_num").html(data["percent"]);
        }
    };
    my_ajax(true, url, "get", {}, true, success);
};


var resource_down_Validation = function () {
    var form1 = $('#resource_down_form');
    var rules = {
        start_version: {
            required: true,
            digits: true
        },
        end_version: {
            digits: true,
            required: true
        }
    };
    var messages = {
        start_version: {
            required: "请输入版本.",
            digits: "请输入数字"
        },
        end_version: {
            required: "请输入版本.",
            digits: "请输入数字"
        }
    };

    var submitFunc = function () {
        var start_version = $("#start_version").val();
        var end_version = $("#end_version").val();
        var url = "http://182.92.161.59:3010/compress.php";
        var success = function(data){
            if (data["success"] == "true"){
                get_res_down_status();
                setInterval("get_res_down_status()", 5000);
            }
        };
        var data = {
            start: start_version,
            end: end_version
        };
        my_ajax(true, url, "get", data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};

resource_down_Validation();