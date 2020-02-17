/**
 * Created by wangrui on 16/7/4.
 */

var PARAM_DATA = {
    "review_version_lst": "评审版本序列",
    "WhiteTestResourceVersion": "名单测试热更",
    "InvalidClientVersion": "热更关闭"
};

display_left_filter();


//添加
$("#sys_add").on("click", function () {
    $("#sys_name").attr("disabled", false);
    $("#sys_name").val("");
    $("#sys_value").val("");
    $("#sys_modal").modal("show");
});



var system_param_Validate = function () {
    var form1 = $('#sysparam_form');
    var rules = {
        sys_name: {
            required: true
        }
    };
    var messages = {
        sys_name: {
            required: "请输入参数名."
        }
    };
    var submitFunc = function () {
        var sys_name = $('#sys_name').val();
        var sys_value = $("#sys_value").val();
        var select_language = $("#select_language").val();
        var data = {
            sys_name: sys_name,
            sys_value: sys_value,
            language: select_language
        };

        var success = function(data){
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            $("#sys_modal").modal("hide");
            get_system_param();
        };
        my_ajax(true, "/operatesysparam", "get", data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunc);
};
system_param_Validate();


function get_system_param() {
    var success = function (data){
        var str_info = "";
        for(var i=0; i < data.length; i++){
            str_info += "<tr>";
            str_info += "<td>" + data[i]["key"] + "</td>";
            str_info += "<td>" + PARAM_DATA[data[i]["key"]] + "</td>";
            str_info += "<td>" + data[i]["value"] + "</td>";
            str_info += "<td>";
            str_info += '&nbsp; <a onclick="mod_sys_params(this,' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs " data-toggle="modal"> <i class="fa fa-edit"></i></a>';
            str_info += "</td>";
            str_info += "</tr>";
        }
        $("#table_sys").html(str_info);
    };
    var select_language = $("#select_language").val();
    var data = {
        "language": select_language
    };
    my_ajax(true, "/getaccsysparam", "get", data, true, success);
}
get_system_param();

$("#select_language").on("change", function(e){
    e.preventDefault();
    get_system_param();
});


var mod_sys_params = function (div, sid) {
    var sys_name = $(div).parents('tr').children('td').eq(0).html();
    var sys_value = $(div).parents('tr').children('td').eq(2).html();
    $("#sys_name").val(sys_name);
    $("#sys_name").attr("disabled", true);
    $("#sys_value").val(sys_value);
    $("#sys_modal").modal("show");
};