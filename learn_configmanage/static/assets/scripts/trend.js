/**
 * Created by wangrui on 15/11/23.
 */

handleDatePickers();
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

$("#start_date_2").val(getNowFormatDate(7));
$("#end_date_2").val(getNowFormatDate(0));


var G_DATA = null;
var G_DATA2 = null;

// function get_total_online(){
//     var success = function(data){
//          $("#online_total").html(data["online_total"]);
//     };
//     my_ajax(true, "/gettotalonline", 'get', {}, true, success);
// }


!function getTotal(){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querytrendtotal',
        data: {},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var total_user = data["total_user"];
            $("#total_user").html(total_user);
            $("#seven_active_user").html(data["seven_active"]);
            $("#third_active_user").html(data["thirty_active"]);
            var total_pay_user =  data["total_pay_user"];
            $("#total_pay_user").html(data["total_pay_user"]);
            var total_pay = 0;
            if (data["total_pay"] != null){
                total_pay = data["total_pay"];
            }
            $("#total_pay_num").html(total_pay);
            var pay_percent = 0;
            var arpu = 0;
            var arppu = 0;
            if (total_user != 0){
                pay_percent = commonPercent(data["total_pay_user"], total_user);
                arpu = parseFloat(data["total_pay"] / total_user).toFixed(2);
            }
            if (total_pay_user != 0){
                arppu = parseFloat(data["total_pay"] / total_pay_user).toFixed(2);
            }

            $("#pay_percent").html(pay_percent + "%");
            $("#arpu").html(arpu);
            $("#arppu").html(arppu);
            $("#online_total").html(parseInt(data["total_online"]));
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
}();


function tick_format(v){
    var temp = G_DATA[v][0].split("-");
    return temp[1] + "-" + temp[2];
}

function tick_format2(v){
    var temp = G_DATA2["pay"][v][0].split("-");
    return temp[1] + "-" + temp[2];
}


var $btn_active = $("#btn_active_user");
var $btn_new = $("#btn_new_user");
var $btn_active_of = $("#btn_active_user_of");

var $btn_second_day = $("#btn_second_day");
var $btn_seven_day = $("#btn_seven_day");
var $btn_thirty_day = $("#btn_thirty_day");
var $btn_pay_user = $("#btn_pay_user");
var $btn_pay_num = $("#btn_pay_num");
var $btn_new_pay_user = $("#btn_new_pay_user");
var $btn_pay_percent = $("#btn_pay_percent");

var $chart_user = $("#chart_user");
var $chart_2 = $("#chart_2");

var LABEL_NAME = {
    4: "付费用户",
    5: "付费金额",
    6: "新增付费用户",
    7: "付费率"
};


function hover(x, y){
    return G_DATA[x][0] + ":" + y;
}

function hover2(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "新用户:" + G_DATA[x][2] + "</br>";
    var old_user = G_DATA[x][1] - G_DATA[x][2];
    str_html += "老用户:" + old_user + "</br>";
    str_html += "活跃用户:" + G_DATA[x][1];
    return str_html;
}

function query_active(){
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var tag = parseInt($("#whole_type").val());
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryactiveuser',
        data: {
            user_channel: 0,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var draw_data = [];
            var draw_data_2 = [];

            var new_draw_data = [];
            var old_draw_data = [];
            var ticks = [];
            var str_info = "";
            G_DATA = data;
            for (var i in data){
                str_info += "<tr>";
                str_info += "<td>" + data[i][0] + "</td>";
                str_info += "<td>" + data[i][3] + "</td>";
                str_info += "<td>" + data[i][1] + "</td>";
                str_info += "</tr>";
                var old_user = parseInt(data[i][1] - data[i][2]);
                draw_data.push([i, data[i][1]]);
                draw_data_2.push([i, data[i][3]]);
                new_draw_data.push([i, data[i][1]]);
                old_draw_data.push([i, old_user]);
                var date_split = data[i][0].split("-");
                var date_time = date_split[1] + "-" + date_split[2];
                ticks.push([i, date_time]);
            }
            var data_set = [
                {
                    label: "活跃用户",
                    data: draw_data
                }
            ];

            var data_set_2 = [
                {
                    label: "新增用户",
                    data: draw_data_2
                }
            ];

            var bar_data_set = [
                {
                    label: "新增用户",
                    data: new_draw_data
                },
                {
                    label: "老用户",
                    data: old_draw_data
                }
            ];
            if (tag == 1){
                DrawLineChart(data_set_2, $chart_user, tick_format);
            }
            else if (tag == 2){
                DrawLineChart(data_set, $chart_user, tick_format);
            }
            else{
                drawBarsChart(bar_data_set, ticks, "center", 0.2, $chart_user);
            }
            $("#user_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}

$("#a_data_details").on("click", function(e){
    e.preventDefault();
    $("#data_details_modal").modal("show");
});


$("#div_whole_start").on("changeDate", function(e){
    e.preventDefault();
    query_active();
});

$("#div_whole_end").on("changeDate", function(e){
    e.preventDefault();
    query_active();
});


$btn_new.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#whole_type").val("1");
    query_active();
    chart_hover_display($chart_user, hover);
});

$btn_new.click();

$btn_active.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#whole_type").val("2");
    query_active();
    chart_hover_display($chart_user, hover);
});


$btn_active_of.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#whole_type").val("3");
    query_active();
    chart_hover_display($chart_user, hover2);
});


function query_trend(){
    var start_date = $("#start_date_2").val();
    var end_date = $("#end_date_2").val();
    var tag = parseInt($("#details_type").val());
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querytrend',
        data: {
            channel: 0,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var draw_data = [];
            var draw_data_2 = [];
            var ticks = [];
            var str_info = "";
            G_DATA2 = data;

            for(var i in data["pay"]){
                str_info += "<tr>";
                str_info += "<td>" + data["pay"][i][0] + "</td>";
                str_info += "<td>" + data["pay"][i][2] + "</td>";
                str_info += "<td>" + data["pay"][i][4] + "</td>";
                str_info += "<td>" + data["pay"][i][1] + "</td>";
                var pay_percent = commonPercent(data["pay"][i][2], data["pay"][i][3]);
                str_info += "<td>" + commonPercent(data["pay"][i][2], data["pay"][i][3]) + "%</td>";
                var reg_count = data["retain"][i][1];
                var second_per = data["retain"][i][2];
                var second = 0;
                var seven = 0;
                var thirty = 0;
                if (second_per == 0)
                    str_info += "<td>-</td>";
                else{
                    second = commonPercent(second_per, reg_count);
                    str_info += "<td>" + second + "%</td>";
                }

                var seven_per = data["retain"][i][8];
                if (seven_per == 0)
                    str_info += "<td>-</td>";
                else{
                    seven =  commonPercent(seven_per, reg_count);
                    str_info += "<td>" + seven + "%</td>";
                }
                var thirty_per = data["retain"][i][10];
                if (thirty_per == 0)
                    str_info += "<td>-</td>";
                else{
                    thirty = commonPercent(thirty_per, reg_count);
                    str_info += "<td>" + thirty + "%</td>";
                }

                draw_data.push([i, reg_count]);
                if (tag == 1){
                    draw_data_2.push([i, second]);
                }
                else if (tag == 2){
                    draw_data_2.push([i, seven]);
                }
                else if (tag == 3){
                    draw_data_2.push([i, thirty]);
                }
                else if (tag == 4){
                    draw_data_2.push([i, data["pay"][i][2]]);
                }
                else if (tag == 5){
                    draw_data_2.push([i, data["pay"][i][4]]);
                }
                else if (tag == 6){
                    draw_data_2.push([i, data["pay"][i][1]]);
                }
                else if (tag == 7){
                    draw_data_2.push([i, pay_percent]);
                }

                var date_split = data["retain"][i][0].split("-");
                var date_time = date_split[1] + "-" + date_split[2];
                ticks.push([i, date_time]);
            }
            if (tag == 0){
                $("#pay_retain_list").html(str_info);
            }
            else if (tag > 0 && tag <= 3){
                DrawLineChartAndBarChart(draw_data, draw_data_2, $chart_2, ticks);
            }
            else{
                var data_set = [
                    {
                        label: LABEL_NAME[tag],
                        data: draw_data_2
                    }
                ];
                DrawLineChart(data_set, $chart_2, tick_format2);
            }
         },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}


$("#div_details_start").on("changeDate", function(e){
    e.preventDefault();
    query_trend();
});

$("#div_details_end").on("changeDate", function(e){
    e.preventDefault();
    query_trend();
});

function hover3(x, y){
    var str_html = "<strong>" + G_DATA2["retain"][x][0] + "</strong></br>";
    str_html += "新增用户:" + G_DATA2["retain"][x][1] + "</br>";
    str_html += "留存率:" + y + "%</br>";
    return str_html;
}

function hover4(x, y){
    return G_DATA2["pay"][x][0] + ":" + y;
}


var $details_type = $("#details_type");
$btn_second_day.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("1");
    query_trend();
    chart_hover_display($chart_2, hover3);
});

$btn_seven_day.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("2");
    query_trend();
    chart_hover_display($chart_2, hover3);
});

$btn_thirty_day.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("3");
    query_trend();
    chart_hover_display($chart_2, hover3);
});

$btn_pay_user.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("4");
    query_trend();
    chart_hover_display($chart_2, hover4);
});

$btn_pay_num.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("5");
    query_trend();
    chart_hover_display($chart_2, hover4);
});

$btn_new_pay_user.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("6");
    query_trend();
    chart_hover_display($chart_2, hover4);
});

$btn_pay_percent.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $details_type.val("7");
    query_trend();
    chart_hover_display($chart_2, hover4);
});

$btn_second_day.click();

$("#a_data_details_2").on("click", function(e){
    e.preventDefault();
    $details_type.val("0");
    query_trend();
    $("#data_details_modal_2").modal("show");
});