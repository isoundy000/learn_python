/**
 * Created by wangrui on 14-10-15.
 */
var server_id = $("#server_id").val();

handleDatePickers();
$("#text_liveness_date").val(getNowFormatDate(1));
$("#login_date").val(getNowFormatDate(1));
$("#online_date").val(getNowFormatDate(1));
$("#guide_date").val(getNowFormatDate(1));
$("#copy_count_date").val(getNowFormatDate(1));
$("#copy_date").val(getNowFormatDate(1));
$("#brave_copy_count_date").val(getNowFormatDate(1));
$("#brave_copy_date").val(getNowFormatDate(1));

create_del_modal($("#param_del_modal"), "是否删除此参数?", "del_param_btn");
create_del_modal($("param_data_del_modal"), "是否删除此埋点漏斗数据?", "del_param_data_btn");


var LOGIN_TYPE = {
    "1": "正常",
    "2": "重连",
    "3": "断网",
    "4": "超时重连",
    "11": "首冲",
    "12": "商城",
    "13": "领奖",
    "14": "副本",
    "15": "体力"
};


var GUIDE_JSON = null;
var COPY_JSON = null;
var BRAVE_COPY_JSON = null;
var MAP_JSON = {};


var init_data = function(){
    var str_info = "";
    for(var u in LOGIN_TYPE){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"login_type\" value=\"" +
                    u + "\">" + LOGIN_TYPE[u] + "</label>";
    }
    $("#login_type").html(str_info);

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/getburieddata",
            data: {},
            async: false,
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                GUIDE_JSON = data["guide"];
                COPY_JSON = data["copy"];
                BRAVE_COPY_JSON = data["brave_copy"];
                MAP_JSON = data["map"];
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    )

};
init_data();

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
    App.blockUI(page_content, false);
    if (select_param.length != 0){
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
            error: function () {
                App.unblockUI(page_content);
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
        error: function () {
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
        error: function () {
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
        error: function () {
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
        error: function () {
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
                error: function () {
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
                error: function () {
                }
            }
        )
    };
    commonValidation(form, rules, messages, submitFunc);
};
paramDataValidate();

//$("#coin_type").change(function(e){
//    e.preventDefault();
//    var coin_type = $("#coin_type").val();
//    if(coin_type != "hour"){
//        $("#hour_select").addClass("hide");
//    }else{
//        $("#hour_select").removeClass("hide");
//    }
//});

//$("#gold_type").change(function(e){
//    e.preventDefault();
//    var coin_type = $("#gold_type").val();
//    if(coin_type != "hour"){
//        $("#gold_hour_select").addClass("hide");
//    }else{
//        $("#gold_hour_select").removeClass("hide");
//    }
//});

//$("#query_button_coin").click(function(e){
//    e.preventDefault();
//    var q_date = $("#text_date_coin").val();
//    var coin_type = $("#coin_type").val();
//    var hour_num = $("#coin_time_num").val();
//    var coin_opttype = "";
//    $("input[name='coin_opttype']:checked").each(function(){
//        if($(this).val() != "" || $(this).val() != null){
//            coin_opttype += $(this).val() + ",";
//        }
//    });
//    $.ajax({
//        type: 'get',
//        url: '/getconsumecoin',
//        data: {server_id: server_id, q_date: q_date, coin_type: coin_type, hour_num: hour_num, coin_opttype:coin_opttype},
//        dataType: 'JSON',
//        success: function (data) {
//            var dataset = [];
//            var chart_coin = $("#chart_coin");
//            chart_coin.empty();
//            var current = 0.0;
//            if(data["status"] == "success"){
//                for(var i=0; i<data["data"].length; i++){
//                    var temp = {label: Coin_Type[data["data"][i]["opt"]],
//                                data: data["data"][i]["per"]
//                                };
//                    current += data["data"][i]["per"];
//                    dataset.push(temp);
//                }
//                if(current < 100){
//                    dataset.push({label: "其他", data: 100.0 - current});
//                }
//                drawPieChart(chart_coin, dataset);
//            }else{
//                chart_coin.html("<span class='label label-danger'>无数据</span>");
//            }
//
//        },
//        error: function () {
//        }
//    })
//});

//$("#query_button_gold").click(function(e){
//    e.preventDefault();
//    var q_date = $("#text_date_gold").val();
//    var gold_type = $("#gold_type").val();
//    var hour_num = $("#gold_time_num").val();
//    var gold_opttype = "";
//    $("input[name='gold_opttype']:checked").each(function(){
//        if($(this).val() != "" || $(this).val() != null){
//            gold_opttype += $(this).val() + ",";
//        }
//    });
//    $.ajax({
//        type: 'get',
//        url: '/getconsumegold',
//        data: {server_id: server_id, q_date: q_date, gold_type: gold_type, hour_num: hour_num, gold_opttype:gold_opttype},
//        dataType: 'JSON',
//        success: function (data) {
//            var dataset = [];
//            var chart_gold = $("#chart_gold");
//            chart_gold.empty();
//            var current = 0.0;
//            if(data["status"] == "success"){
//                for(var i=0; i<data["data"].length; i++){
//                    var temp = {label: Gold_Type[data["data"][i]["opt"]],
//                                data: data["data"][i]["per"]
//                                };
//                    current += data["data"][i]["per"];
//                    dataset.push(temp);
//                }
//                if(current < 100){
//                    dataset.push({label: "其他", data: 100.0 - current});
//                }
//                drawPieChart(chart_gold, dataset);
//            }else{
//                chart_gold.html("<span class='label label-danger'>无数据</span>");
//            }
//
//        },
//        error: function () {
//        }
//    })
//});

//$("#a_recharge").bind("click", function(e){
//    e.preventDefault();
//    recharge_list_draw(0, {server_id: server_id}, '/getservertotal', $("#total_recharge_list"), $("#chart_server_total"));
//});
//
//$("#recharge_day_button").bind("click", function(e){
//    e.preventDefault();
//    var recharge_day_date = $("#recharge_day_date").val();
//    recharge_list_draw(1, {server_id: server_id, q_date: recharge_day_date}, '/getserverday', $("#day_recharge_list"), $("#chart_recharge_day"));
//});
//
//$("#recharge_week_button").bind("click", function(e){
//    e.preventDefault();
//    var recharge_date_week = $("#recharge_date_week").val();
//    recharge_list_draw(0, {server_id: server_id, q_date: recharge_date_week}, '/getserverweek', $("#week_recharge_list"), $("#chart_recharge_week"));
//});
//
//$("#recharge_month_button").bind("click", function(e){
//    e.preventDefault();
//    var recharge_date_month = $("#recharge_date_month").val();
//    $.ajax({
//            type: 'get',
//            url: "/getservermonth",
//            data: {server_id: server_id, q_date: recharge_date_month},
//            dataType: 'JSON',
//            success: function (data) {
//                var dataset = [];
//                for(var d in data){
//                    var t_empty = {};
//                    var t_data = [];
//                    for(var i=0; i < data[d].length; i++){
//                        var temp_data = [(i+1), data[d][i]];
//                        t_data.push(temp_data);
//                    }
//                    t_empty["label"] = d;
//                    t_empty["data"] = t_data;
//                    dataset.push(t_empty);
//                }
//                drawManyLineChart(dataset, $("#chart_recharge_month"))
//            },
//            error: function () {
//            }
//        }
//    )
//});

var getRoleLevel = function (){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/querylevel",
            data: {server_id: server_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data["data"].length != 0){
                    for(var i=0; i<data["data"].length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data["data"][i]["level"] + "</td>";
                        str_info += "<td>" + data["data"][i]["num"] + "</td>";
                        str_info += "<td>" + (data["data"][i]["num"]/data["total"] * 100).toFixed(2) + "%</td>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#level_count_list").html(str_info);
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    )
};
getRoleLevel();


$("#a_vip").bind("click", function(e){
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/queryvip",
            data: {server_id: server_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data["data"].length != 0){
                    for(var i=0; i<data["data"].length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data["data"][i]["level"] + "</td>";
                        str_info += "<td>" + data["data"][i]["num"] + "</td>";
                        str_info += "<td>" + (data["data"][i]["num"]/data["total"] * 100).toFixed(2) + "%</td>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#vip_count_list").html(str_info);
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    )
});

$("#euqip_btn").on("click", function(e){
    e.preventDefault();
    var equip_star = $("#equip_star").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryequip',
        data: {
            server_id: server_id,
            equip_star: equip_star
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != "") {
                for (var s in data) {
                    str_info += "<tr>";
                    str_info += "<td>";
                    if (equip_star == "2") {
                        str_info += "<a class='btn btn-xs green'>" + data[s]["name"] + "</a>";
                    }
                    else if (equip_star == "3") {
                        str_info += "<a class='btn btn-xs blue'>" + data[s]["name"] + "</a>";
                    }
                    else if (equip_star == "4") {
                        str_info += "<a class='btn btn-xs purple'>" + data[s]["name"] + "</a>";
                    }
                    else {
                        str_info += "<a class='btn btn-xs yellow'>" + data[s]["name"] + "</a>";
                    }
                    str_info += "</td>";
                    str_info += "<td>" + data[s]["num"] + "</td>";
                    str_info += "<td>" + (data[s]["users"] / data[s]["total"] * 100).toFixed(2) + "%</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#equip_list").html(str_info);
        },
        error: function () {
            App.unblockUI(page_content);
            error_func();
        }
    })
});

$("#general_btn").on("click", function(){
    var general_star = $("#general_star").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querygeneralbyid',
        data: {server_id: server_id, general_star: general_star},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != "") {
                for (var s in data) {
                    str_info += "<tr>";
                    str_info += "<td>";
                    if (general_star == "2") {
                        str_info += "<a class='btn btn-xs green'>" + data[s]["name"] + "</a>";
                    }
                    else if (general_star == "3") {
                        str_info += "<a class='btn btn-xs blue'>" + data[s]["name"] + "</a>";
                    }
                    else if (general_star == "4") {
                        str_info += "<a class='btn btn-xs purple'>" + data[s]["name"] + "</a>";
                    }
                    else {
                        str_info += "<a class='btn btn-xs yellow'>" + data[s]["name"] + "</a>";
                    }
                    str_info += "</td>";
                    str_info += "<td>" + data[s]["num"] + "</td>";
                    str_info += "<td>" + (data[s]["users"] / data[s]["total"] * 100).toFixed(2) + "%</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#general_list").html(str_info);
        },
        error: function () {
            App.unblockUI(page_content);
            error_func();
        }
    })
});

$("#liveness_query").on("click", function(e){
    e.preventDefault();
    var text_liveness_date = $("#text_liveness_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryliveness',
            data: {server_id: server_id, q_date: text_liveness_date},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                var total = 0;
                for (var k=0;  k<data.length; k++){
                    total += data[k]["c_count"];
                }
                if(data.length != 0){
                    for (var i=0; i <data.length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["point"] + "积分</td>";
                        str_info += "<td>" + data[i]["c_count"] + "</td>";
                        str_info += "<td>" + (data[i]["c_count"] / total * 100).toFixed(2) + "%</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#liveness_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
                error_func();
            }
    })
});



//$("#a_gold").bind("click", function(e){
//    e.preventDefault();
//    $("#gold_start_date").val(getNowFormatDate(7));
//    $("#gold_end_date").val(getNowFormatDate(0));
//});
//
//$("#gold_query").bind("click", function(e){
//    e.preventDefault();
//    var gold_start_date = $("#gold_start_date").val();
//    var gold_end_date = $("#gold_end_date").val();
//    var page_content = $('.page-content');
//    App.blockUI(page_content, false);
//    $.ajax({
//        type: 'get',
//        url: '/querygold',
//        data: {server_id: server_id, start_date: gold_start_date, end_date: gold_end_date},
//        dataType: 'JSON',
//        success: function (data) {
//            App.unblockUI(page_content);
//            var str_info = "";
//            var recharge = parseInt(data["recharge"]);
//            var system = parseInt(data["system"]);
//            var hand = parseInt(data["hand"]);
//            var total = recharge + system + hand;
//            str_info += "<tr>";
//            str_info += "<td>" + recharge + "</td>";
//            str_info += "<td>" + system + "</td>";
//            str_info += "<td>" + hand + "</td>";
//            str_info += "<td>" + total + "</td>";
//            if (recharge == 0){
//                str_info += "<td>0%</td>";
//            }
//            else{
//                str_info += "<td>" + ((hand + system) / data["recharge"] * 100).toFixed(2) + "%</td>";
//            }
//            str_info += "<td>" + parseInt(data["usegold"]["num"]) + "</td>";
//            str_info += "<td>" + data["usegold"]["count"] + "</td>";
//            str_info += "<td>" + (total - data["usegold"]["num"])  + "</td>";
//            if (data["usegold"]["count"] == 0){
//                str_info += "<td>0%</td>";
//            }
//            else{
//                str_info += "<td>" + parseInt(data["usegold"]["num"]) / parseInt(data["usegold"]["count"]) + "</td>";
//            }
//            str_info += "<td>" + data["havegold"] + "</td>";
//            str_info += "</tr>";
//            $("#gold_list").html(str_info);
//        },
//        error: function () {
//            App.unblockUI(page_content);
//            error_func();
//        }
//    })
//});

$("#a_guide").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var select_area = $("#select_area");
    for (var s in GUIDE_JSON){
        str_info1 += "<option value='" + s + "'>" + s + "</option>";
    }
    select_area.html(str_info1);
    select_area.change();
});

$("#select_all").bind("click", function(e){
    var guide_step_type = $("input[name='guide_step_type']");
    if ($("#select_all").is(":checked")){
        guide_step_type.prop("checked", true);
        guide_step_type.parent("span").addClass("checked");
    }
    else{
        guide_step_type.prop("checked", false);
        guide_step_type.parent("span").removeClass("checked");
    }
});

$("#no_select_all").bind("click", function(e){
    $("input[name='guide_step_type']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});

$("#copy_select_all").bind("click", function(e){
    var copy_map_type = $("input[name='copy_map_type']");
    if ($("#copy_select_all").is(":checked")){
        copy_map_type.prop("checked", true);
        copy_map_type.parent("span").addClass("checked");
    }
    else{
        copy_map_type.prop("checked", false);
        copy_map_type.parent("span").removeClass("checked");
    }
});

$("#copy_no_select_all").bind("click", function(e){
    $("input[name='copy_map_type']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});


$("#select_area").on("change", function(e){
    e.preventDefault();
    var area = $("#select_area").val();
    var str_info = "";
    var area_array = GUIDE_JSON[area];
    for (var i in area_array) {
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"guide_step_type\" value=\"" +
                    area_array[i]["step"] + "\">" + area_array[i]["_param2"] + "</label>";
    }
    $("#guide_step").html(str_info);
});

var get_temp_json = function(div_type){
    var tag = div_type.val();
    var temp_json = null;
    if (tag == "1"){
        temp_json = COPY_JSON;
    }
    else{
        temp_json = BRAVE_COPY_JSON;
    }
    return temp_json;
};


$("#a_copy_count").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var temp_json = get_temp_json($("#select_copy_type"));

    var select_section = $("#select_section");
    for (var s in temp_json){
        str_info1 += "<option value='" + s + "'>" + s + "_" + MAP_JSON[s]["name"] + "</option>";
    }
    select_section.html(str_info1);
    select_section.change();
});

$("#select_section").on("change", function(e){
    e.preventDefault();
    var temp_json = get_temp_json($("#select_copy_type"));
    var select_section = $("#select_section").val();
    var str_info = "";
    var section_array = temp_json[select_section];
    for(var i in section_array){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"copy_map_type\" value=\"" +
                    section_array[i]["point"] + "\">" + section_array[i]["point"] + "_" + section_array[i]["name"] + "</label>";
    }
    $("#select_map").html(str_info);
});

$("#a_brave_copy_count").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var select_brave_section = $("#select_brave_section");
    for (var s in BRAVE_COPY_JSON){
        str_info1 += "<option value='" + s + "'>" + s + "</option>";
    }
    select_brave_section.html(str_info1);
    select_brave_section.change();
});

$("#select_brave_section").on("change", function(e){
    e.preventDefault();
    var select_brave_section = $("#select_brave_section").val();
    var str_info = "";
    var section_array = COPY_JSON[select_brave_section];
    for(var i in section_array){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"brave_copy_type\" value=\"" +
                    section_array[i]["point"] + "\">" + section_array[i]["name"] + "</label>";
    }
    $("#select_brave_map").html(str_info);
});


//新手引导时间查询
$("#btn_guide").on("click", function(e){
    e.preventDefault();
    var guide_date = $("#guide_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryguidebytime',
            data: {server_id: server_id, guide_date: guide_date},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                $("#enter_guide").html(data["enter"]);
                $("#choose_profile").html(data["choose_profile"]);
            },
            error: function(){
                App.unblockUI(page_content);
            }
    })
});

//新手引导类型查询
$("#btn_type_guide").on("click", function(e){
    e.preventDefault();
    var select_area = $("#select_area").val();
    var guide_date = $("#guide_date").val();
    var guide_step_type = "";
    $("input[name='guide_step_type']:checked").each(function(){
        guide_step_type += $(this).val() + ",";
    });
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryguidebytype',
            data: {
                    server_id: server_id,
                    guide_date: guide_date,
                    select_area: select_area,
                    guide_step_type: guide_step_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){
                    for(var i in data){
                        str_info += "<tr>";
                        str_info += "<td>" + GUIDE_JSON[select_area][i]["_param2"] + "</td>";
                        str_info += "<td>" + data[i] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#guide_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
            }
    })
});


$("#btn_copy_count").on("click", function(e){
    e.preventDefault();
    var select_copy_type = $("#select_copy_type").val();
    var select_section = $("#select_section").val();
    var select_map = "";
    $("input[name='copy_map_type']:checked").each(function(){
        select_map += $(this).val() + ",";
    });
    var copy_count_date = $("#copy_count_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var temp_json = null;
    if (select_copy_type == "1") {
        temp_json = COPY_JSON;
    }
    else {
        temp_json = BRAVE_COPY_JSON
    }
    $("#copy_count_list").empty();
    $.ajax({
            type: 'get',
            url: '/querycopycount',
            data: {
                    server_id: server_id,
                    select_copy_type: select_copy_type,
                    copy_count_date: copy_count_date,
                    select_section: select_section,
                    select_map: select_map
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){

                    for(var i = 0; i < data.length; i++){
                        str_info += "<tr>";

                        str_info += "<td>" + temp_json[data[i]["map"]][data[i]["point"]]["name"] + "</td>";
                        str_info += "<td>" + data[i]["c1"] + "</td>";
                        str_info += "<td>" + data[i]["c2"] + "</td>";
                        str_info += "<td>" + data[i]["c3"] + "</td>";
                        str_info += "<td>" + data[i]["c4"] + "</td>";
                        str_info += "<td>" + data[i]["c5"] + "</td>";
                        str_info += "<td>" + data[i]["c6"] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="8" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#copy_count_list").html(str_info);

            },
            error: function(){
                App.unblockUI(page_content);
            }
    })
});

$("#btn_copy").on("click", function(e){
    e.preventDefault();
    var s_type = $("#s_type").val();
    var copy_date = $("#copy_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $("#copy_list").empty();
    $.ajax({
            type: 'get',
            url: '/querycopylimit',
            data: {
                s_type: s_type,
                server_id: server_id,
                copy_date: copy_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){

                    for(var i = 0; i < data.length; i++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["map"] + "_" + MAP_JSON[data[i]["map"]]["name"] + "</td>";
                        str_info += "<td>" + data[i]["point"] + "_" + COPY_JSON[data[i]["map"]][data[i]["point"]]["name"] + "</td>";
                        str_info += "<td>" + data[i]["c"] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#copy_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
            }
    })
});


$("#btn_online").on("click", function(e){
    e.preventDefault();
    var online_param = $("#online_param").val();
    var online_date = $("#online_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/queryonlinedata',
            data: {
                server_id: server_id,
                online_param: online_param,
                online_date: online_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){

                    for(var s in data){
                        str_info += "<tr>";
                        str_info += "<td>" + s + "</td>";
                        str_info += "<td>" + data[s] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#online_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
                error_func();
            }
    })
});

$("#btn_login").on("click", function(e){
    e.preventDefault();
    var login_date = $("#login_date").val();
    var login_param = $("#login_param").val();
    var login_type = "";
    $("input[name='login_type']:checked").each(function(){
        login_type += $(this).val() + ",";
    });
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/queryrolecount',
            data: {
                server_id: server_id,
                login_param: login_param,
                login_date: login_date,
                login_type: login_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){
                    for(var s=0; s<data.length; s++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[s][0] + "</td>";
                        str_info += "<td>";
                        for (var i in data[s][1]){
                            str_info += "<span class='label label-success'>" + LOGIN_TYPE[i] + "</span>:" + data[s][1][i]
                            + "&nbsp;";
                        }
                        str_info += "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#buried_list").html(str_info);
            },
            error: function(){
                App.unblockUI(page_content);
                error_func();
            }
    })
});