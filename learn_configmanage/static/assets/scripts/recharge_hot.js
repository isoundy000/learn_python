/**
 * Created by wangrui on 14/12/18.
 */
var common_url = "http://182.92.240.247:3010";

var folder = {
    "": "",
    "battle": "battle",
    "common_lua": "common_lua",
    "config": "config",
    "pb": "pb",
    "scripts": "scripts",
    "spine": "spine",
    "UI": "UI",
    "music": "music"
};
init_select_html(false, folder, $("#select_folder"));

var PLAT_FORM = {
    "ios": "苹果",
    "android": "安卓",
    "all": "所有"
};

var tag = true;
var down_status = null;

create_del_modal($("#res_channel_del_modal"), "是否删除此渠道?", "confirm_del");


// function get_start_end_version(){
//     var return_data = null;
//     var success = function (data){
//         return_data = data;
//     };
//
//     my_ajax(true, "/resource/getstartend", "get", {}, false, success);
//     return return_data;
// }
//
// var resource_log_data = null;
var end_version = 1;
function get_resource_log(){
    var success = function (data){
        resource_log_data = data;

        if (resource_log_data.length > 0){
            end_version = resource_log_data[0];
        }
    };
    my_ajax(true, "/resource/getresourcelog", "get", {}, false, success);
}
get_resource_log();



function insert_resource_log(){

}



var get_resource = function () {
    var success = function(data){
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
    };
    my_ajax(true, "/resource/getresourceversion2", 'get', {}, true, success);
};
get_resource();


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


var get_version_list = function () {
    var ajaxSource = "/resource/getresourceversion";
    var aoColumns = [
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
    ];
    var fnRowCallback = function(nRow, aData, iDisplayIndex){
        if (aData.needrestart == "yes") {
            $('td:eq(3)', nRow).html('<span class="badge badge-success">是</span>');
        } else {
            $('td:eq(3)', nRow).html('<span class="badge badge-danger">否</span>');
        }
        if (aData.status == "excute") {
            $('td:eq(2)', nRow).html('<span class="badge badge-success">执行</span>');
        } else if (aData.status == "prepare") {
            $('td:eq(2)', nRow).html('<span class="badge badge-info">准备</span>');
        } else if (aData.status == "error") {
            $('td:eq(2)', nRow).html('<span class="badge badge-danger">错误</span>');
        }
        var str_html = "";
        if (aData.id > end_version) {
            str_html = "<button onclick=\"mod(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>"
        }
        $('td:eq(4)', nRow).html(str_html);
        return nRow;
    };
    dataTablePage($("#version_table"), aoColumns, ajaxSource, {}, false, fnRowCallback);
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

    var success = function(data){
        $("#version_modal").modal("hide");
        if (data["status"] == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.")
        }
        get_version_list();
        get_resource();
        get_resource_log();
    };
    var resource_version = $("#resource_version").val();
    var select_status = $("#select_status").val();
    var version_desc = $("#version_desc").val();
    var select_restart = $("#select_restart").val();
    var data = {
        resource_version: resource_version,
        status: select_status,
        select_restart: select_restart,
        version_desc: version_desc
    };
    my_ajax(true, "/resource/addresourceversion", 'get', data, true, success);
});


$("#select_version").bind("change", function () {
    var select_version = $("#select_version").val();
    var file_list = $("#file_list");
    $("#select_version1").val(select_version);

    var success = function(data){
        var str_info = "";
        if (data.length != 0) {
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + data[i]["filepath"] + "</td>";
                str_info += "<td>" + data[i]["length"] + "</td>";
                str_info += "<td>" + PLAT_FORM[data[i]["platform"]] + "</td>";
                str_info += "<td>" + data[i]["updatetime"] + "</td>";
                str_info += '<td><a target="_blank" class="btn btn-xs default blue" href="';
                str_info += data[i]["url"] + '">下载<i class="fa fa-download"></i></a></td>';
                str_info += "</tr>";
            }
        } else {
            str_info += "<tr>";
            str_info += '<td colspan="5" class="text-center"><span class="label label-danger">无数据</span></td>';
            str_info += '</tr>';
        }
        file_list.html(str_info);
    };
    var data = {
        version: select_version
    };

    my_ajax(true, '/resource/getresourcefile', 'get', data, true, success);
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
            url: "/resource/uploadresourcefile",
            secureuri: false,
            type: "post",
            fileElementId: 'resource_file_b',
            data: {
                select_version1: select_version1,
                select_folder: select_folder,
                second_dir: second_dir,
                platform: select_platform,
                file_desc: file_desc
            },
            dataType: 'json',
            success: function (data, status)
            {
                App.unblockUI(page_content);
                $("#choose_div").empty();
                $("#choose_div").html(choose_div);
                $("#upload_modal").modal("hide");
                $("#select_version").change();
            },
            error: function (data, status, e)
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
            url: "/resource/uploadresourcezipfile",
            secureuri: false,
            type: "post",
            fileElementId: 'resource_file_zip',
            data: {
                select_version: select_version
            },
            dataType: 'json',
            success: function (data, status)
            {
                App.unblockUI(page_content);
                $("#choose_div_zip").empty();
                $("#choose_div_zip").html(choose_div_zip);
                if (data["status"] == "success") {
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


// var get_res_down_status = function(){
//     var url = common_url + "/compress_status.php";
//     var success = function(data){
//         if (data["success"] == "true"){
//             $("#down_status").html(data["message"] + ", 下载进度:" + data["percent"] + "%");
//             if (data["percent"] == 100){
//                 clearInterval(down_status);
//             }
//             $("#progress_num").html(data["percent"]);
//         }
//     };
//     my_ajax(true, url, "get", {}, true, success);
// };


function add0(m){return m<10?'0'+m:m }
function format(timestamp)
{
  //timestamp是整数，否则要parseInt转换,不会出现少个0的情况
        var time = new Date(timestamp * 1000);
        var year = time.getFullYear();
        var month = time.getMonth()+1;
        var date = time.getDate();
        var hours = time.getHours();
        var minutes = time.getMinutes();
        var seconds = time.getSeconds();
        return year+'-'+add0(month)+'-'+add0(date)+' '+add0(hours)+':'+add0(minutes)+':'+add0(seconds);
}

var resource_timer = null;
var get_res_down_status = function(){
    var success = function(data){
        var timestamp = Date.parse(new Date());
        if (data != null){
            var upload_time = data["updated_time"];
            var five_minutes = 5 * 60 * 1000;
            if (data["status"] == 1 && resource_timer != null){
                clearInterval(resource_timer);
            }
            else if (data["status"] == 0 && timestamp - upload_time * 1000 <= five_minutes){
                if (resource_timer == null)
                    resource_timer = setInterval("get_res_down_status()",5000);
            }
            else if(data["status"] == 1){
                insert_resource_log();
            }
            var time_str = format(upload_time);
            $("#down_status").html("<p>" + time_str + ":" + data["message"] + "</p>");
        }

    };
    my_ajax(false, '/resource/getcompress', "get", {}, true, success);
};
get_res_down_status();


$("#btn_res_down").on("click", function(e){
    e.preventDefault();
    var success = function (data) {
        if (data["status"] == "success"){
            Common.alert_message($("#error_modal"), 1, "处理成功.");
        }
        else if(data["status"] == "already"){
            Common.alert_message($("#error_modal"), 0, "已处理该版本.");
        }
        else if(data["status"] == "lock"){
            Common.alert_message($("#error_modal"), 0, "处理异常，请联系相关人员.");
        }
        else{
            Common.alert_message($("#error_modal"), 0, "处理失败.");
        }
    };
    my_ajax(true, '/resource/compress', "get", {}, true, success);
    get_res_down_status();
});

var execute_str = "";
var execute_command = function(){
    var success = function (data) {
        $("#command_modal").modal("hide");
        if (data["status"] == "success"){
            Common.alert_message($("#error_modal"), 1, "处理成功.");
        }
        else{
            Common.alert_message($("#error_modal"), 0, "处理失败.");
        }
    };
    var data = {
        ctype: execute_str
    };
    my_ajax(true, "/resource/execommand", "get", data, true, success);
};

var commandValidation = function () {
    var form1 = $('#command_form');
    var rules = {
        opt_password: {
            required: true
        }
    };
    var messages = {
        opt_password: {
            required: "请输入密码."
        }
    };
    var submitFunc = function () {
        var opt_password = $("#opt_password").val();
        if (opt_password == "wozhendeyaozhemezuo"){
            execute_command();
        }
        else{
            $('.alert-danger span').html("密码错误");
            $('.alert-danger', $('#command_form')).show();
        }
    };
    commonValidation(form1, rules, messages, submitFunc);
};
commandValidation();


$("#btn_effective").on("click", function(e){
    e.preventDefault();
    execute_str = "effective_compress.php";
    $("#command_modal").modal("show");
});

$("#btn_rollback").on("click", function(e){
    e.preventDefault();
    execute_str = "onestep.php";
    $("#command_modal").modal("show");
});


var $btn_online = $("#btn_online");
var $btn_offline = $("#btn_offline");

var query_compress = function(tag){
    var ajaxSource = "/resource/querycompress";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "sTitle": "版本"
        },
        {
            "mDataProp": "platform",
            'sClass': 'center',
            "sTitle": "平台"
        },
        {
            "mDataProp": "size",
            'sClass': 'center',
            "sTitle": "文件大小"
        },
        {
            "mDataProp": "needrestart",
            'sClass': 'center',
            "sTitle": "是否重启"
        },
        {
            "mDataProp": "url",
            'sClass': 'center',
            "sTitle": "操作"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = "<span class='badge badge-success'>" + aData.id;
        $('td:eq(0)', nRow).html(str_html1);
        var str_html2 = "";
        if (aData.needrestart == 'yes'){
            str_html2 += "<span class='badge badge-success'>是</span>";
        }
        else{
            str_html2 += "<span class='badge badge-danger'>否</span>";
        }
        $('td:eq(3)', nRow).html(str_html2);
        var str_html3 = "";
        str_html3 += '&nbsp; <a target="_blank" class="btn default btn-xs blue" href="';
        str_html3 += aData.url + '">下载<i class="fa fa-download"></i></a>';
        $('td:eq(4)', nRow).html(str_html3);
        return nRow;
    };
    var data = {
        tag: tag
    };
    dataTablePage($("#compress_table"), aoColumns, ajaxSource, data, false, fnRowCallback);
};


$("#a_download_zip").on("click", function(e){
    e.preventDefault();
    $btn_online.click();
});

$btn_online.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_compress(1);
});

$btn_offline.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_compress(2);
});


var $cid = $("#cid");
var $channel_id = $("#channel_id");
var $channel_name = $("#channel_name");
var $channel_status = $("#channel_status");

var query_channel_status = function () {
    var ajaxSource = "/resource/channel";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "channel_id",
            'sClass': 'center',
            "sTitle": "渠道编号"
        },
        {
            "mDataProp": "channel_name",
            'sClass': 'center',
            "sTitle": "渠道名称"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_channel(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_channel(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html = "";
        if (aData.status == 1){
            str_html = "<span class='badge badge-success'>有效</span>"
        }
        else{
            str_html = "<span class='badge badge-danger'>无效</span>"
        }
        $('td:eq(2)', nRow).html(str_html);
        return nRow;
    };
    dataTablePage($("#channel_status_table"), aoColumns, ajaxSource, {}, false, fnRowCallback);
};

var mod_channel = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#channel_status_table").dataTable().fnGetData(nRoW);
    $cid.val(data["id"]);
    $channel_id.val(data["channel_id"]);
    $channel_name.val(data["channel_name"]);
    $channel_status.val(data["status"]);
    $("#res_channel_modal").modal("show");
};


var confirm_del_channel = function (cid) {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }
        $('#res_channel_modal').modal("hide");
        query_channel_status();
    };
    var req_data = {
        cid: cid
    };
    my_ajax(true, "/resource/deletechannel", "get", req_data, true, success);
};


var del_channel = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#channel_status_table").dataTable().fnGetData(nRoW);
    $('#res_channel_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_channel(" + data["id"] + ")");
};



$("#a_res_channel").on("click", function (e) {
    e.preventDefault();
    query_channel_status();
});



$("#add_channel").on("click", function (e) {
    e.preventDefault();
    $cid.val("0");
    $channel_id.val("");
    $channel_name.val("");
    $("#res_channel_modal").modal("show");
});



var channelStatusValidation = function () {
    var form1 = $('#channel_status_form');
    var rules = {
        channel_id: {
            required: true,
            digits: true
        },
        channel_name: {
            required: true
        }
    };
    var messages = {
        channel_id: {
            required: "请输入渠道编号.",
            digits: "请输入数字"
        },
        channel_name: {
            required: "请输入渠道名称."
        }
    };
    var submitFunc = function () {
        var success = function(data){
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败.")
            }
            $("#res_channel_modal").modal("hide");
            query_channel_status();
        };
        var req_data = {
            cid: $cid.val(),
            channel_id: $channel_id.val(),
            channel_name: $channel_name.val(),
            status: $channel_status.val()
        };
        my_ajax(true, "/resource/operatechannel", 'get', req_data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
channelStatusValidation();
