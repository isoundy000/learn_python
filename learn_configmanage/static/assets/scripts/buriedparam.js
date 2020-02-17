/**
 * Created by wangrui on 15/5/8.
 */

create_del_modal($("#param_del_modal"), "是否删除此埋点?", "del_param_btn");
create_del_modal($("#param_data_del_modal"), "是否删除此数据配置?", "del_param_data_btn");

var get_param_data = function(){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryparam',
            data: {},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                var str_info1 = "";
                if (data.length != 0){
                    for(var i=0; i<data.length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["name"] + "</td>";
                        str_info += "<td>";
                        str_info += '&nbsp; <a onclick="mod_param(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                        str_info += '&nbsp; <a onclick="del_param(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                        str_info += "</td>";
                        str_info += "</tr>";
                        str_info1 += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + "</option>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#param_list").html(str_info);
                $("#select_param").html(str_info1);
                $("#login_param").html(str_info1);
                $("#online_param").html(str_info1);
                $("#strengthen_param").html(str_info1);
                $("#select_param").change();
            },
            error: function(){
                App.unblockUI(page_content);
            }
    })
};
get_param_data();

$("#select_param").on("change", function(e){
    var select_param = $("#select_param").val();
    var page_content = $('.page-content');
    if (select_param !== null && select_param.length != 0){
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/queryparamdata',
            data: {select_param: select_param},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data.length != 0) {
                    for (var i = 0; i < data.length; i++) {
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["id"] + "</td>";
                        str_info += "<td>" + data[i]["start"] + "</td>";
                        str_info += "<td>" + data[i]["end"] + "</td>";
                        str_info += "<td>";
                        str_info += '&nbsp; <a onclick="mod_param_data(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                        str_info += '&nbsp; <a onclick="del_param_data(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                        str_info += "</td>";
                        str_info += "</tr>";
                    }
                }
                else {
                    str_info += "<tr>";
                    str_info += '<td colspan="4" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#param_data_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        })
    }
});

var mod_param_data = function(id){
   $("#param_data_modal").modal("show");
   $.ajax({
        type: 'get',
        url: '/queryoneparamdata',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            $("#param_data_id").val(id);
            $("#param_start").val(data["start"]);
            $("#param_end").val(data["end"]);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

var del_param_data = function(id){
    $('#param_data_del_modal').modal("show");
    $("#del_param_data_btn").attr('onclick', 'fun_del_param_data(' + id + ');');
};

var fun_del_param_data = function(id){
    $.ajax({
        type: 'get',
        url: '/deleteparamdata',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if(data["status"] == "fail"){
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#param_data_del_modal').modal("hide");
            get_param_data();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


var mod_param = function(id){
    $("#param_modal").modal("show");
    $.ajax({
        type: 'get',
        url: '/queryoneparam',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            $("#param_id").val(id);
            $("#param_name").val(data["name"]);
            $("#param_desc").val(data["desc"]);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

var del_param = function(id){
    $('#param_del_modal').modal("show");
    $("#del_param_btn").attr('onclick', 'fun_del_param(' + id + ');');
};

var fun_del_param = function(id){
   $.ajax({
        type: 'get',
        url: '/deleteparam',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if(data["status"] == "fail"){
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

$("#add_param").on("click", function(){
    $("#param_id").val("");
    $("#param_name").val("");
    $("#param_desc").val("");
    $("#param_modal").modal("show");
});

$("#add_param_data").on("click", function(){
    $("#param_start").val("");
    $("#param_end").val("");
    $("#param_data_id").val("");
    $("#param_data_modal").modal("show");
});


var paramValidate = function(){
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
        var param_desc = $("#param_desc").val();
        $.ajax({
                type: 'get',
                url: '/operateparam',
                data: {
                    param_id: param_id,
                    param_name: param_name,
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

var paramDataValidate = function(){
    var form = $("#param_data_form");
    var rules = {
        param_start: {
            required: true,
            digits: true
        },
        param_end: {
            required: true,
            digits: true
        }
    };
    var messages = {
        param_start: {
            required: "请输入开始数字.",
            digits: "请输入数字"
        },
        param_end: {
            required: "请输入结束数字",
            digits: "请输入数字"
        }

    };
    var submitFunc = function () {
        var param_data_id = $("#param_data_id").val();
        var select_param = $("#select_param").val();
        var param_start = $('#param_start').val();
        var param_end = $("#param_end").val();
        $.ajax({
                type: 'get',
                url: '/operateparamdata1',
                data: {
                    select_param: select_param,
                    param_data_id: param_data_id,
                    param_start: param_start,
                    param_end: param_end
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#param_data_modal").modal("hide");
                    $("#select_param").change();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form, rules, messages, submitFunc);
};
paramDataValidate();