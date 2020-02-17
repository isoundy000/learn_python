/**
 *  * Created by wangrui on 15/1/17.
 *   */

var G_DATA = null;
handleDatePickers();
display_left_count();
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

setPartnerData($("#user_channel").val(), $("#partner_list"));


var $active_type = $('#active_type');
var $btn_active = $("#btn_active_user");
var $btn_active_of = $("#btn_active_user_of");
var $chart_active_user = $("#chart_active_user");
var $btn_open_game_num = $('#btn_open_game_num');
var $btn_single_use_time = $('#btn_single_use_time');
var $btn_avg_user_time = $('#btn_avg_user_time');
var $btn_avg_open_num = $('#btn_avg_open_num');


$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $btn_active.click();
});

$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    $btn_active.click();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    $btn_active.click();
});

function tick_format(v){
    var temp = G_DATA[v][0].split("-");
    return temp[1] + "-" + temp[2];
}

function query_active (){
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var active_type = $active_type.val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryactiveuser',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            active_type: active_type,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var str_info = "";
            var draw_data = [];

            var new_draw_data = [];
            var old_draw_data = [];
            var ticks = [];
            G_DATA = data;
            for (var i in data){
                str_info += "<tr>";
                str_info += "<td>" + data[i][0] + "</td>";
                str_info += "<td>" + data[i][1] + "</td>";
                str_info += "<td>" + data[i][2] + "</td>";
                var new_user_pre = data[i][1] === 0 ?'0.00%' : ((data[i][2]/data[i][1])*100).toFixed(2) + '%';
                str_info += "<td>" + new_user_pre + "</td>";
                var old_user = parseInt(data[i][1] - data[i][2]);
                str_info += "<td>" + old_user + "</td>";
                var old_user_pre = data[i][1] === 0 ?'0.00%' : ((old_user/data[i][1])*100).toFixed(2) + '%';
                str_info += "<td>" + old_user_pre + "</td>";
                str_info += "</tr>";
                draw_data.push([i, data[i][1]]);

                new_draw_data.push([i, data[i][1]]);
                old_draw_data.push([i, old_user]);
                var date_split = data[i][0].split("-");
                var date_time = date_split[1] + "-" + date_split[2];
                ticks.push([i, date_time]);
            }
            $("#active_user_list").html(str_info);
            if (active_type == "1"){
                var data_set = [
                    {
                        label: "活跃用户",
                        data: draw_data
                    }
                ];
                DrawLineChart(data_set, $chart_active_user, tick_format);
            }
            else if (active_type == "2"){
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
                console.log(bar_data_set);
                drawBarsChart(bar_data_set, ticks, "center", 0.5, $chart_active_user);
            }
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}

function query_login_num (){
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var active_type = $active_type.val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryactiveuser',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            active_type: active_type,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var draw_data = [];
            var i;
            var data_set;
            G_DATA = data;

            if (active_type === "3"){
                for (i in data){
                    draw_data.push([i, data[i][1]]);
                }
                data_set = [
                    {
                        label: "活跃用户启动次数",
                        data: draw_data
                    }
                ];
                DrawLineChart(data_set, $chart_active_user, tick_format);
            }else if (active_type === "6"){
                for (i in data){
                    draw_data.push([i, data[i][2]]);
                }
                data_set = [
                    {
                        label: "平均日启动次数",
                        data: draw_data
                    }
                ];
                DrawLineChart(data_set, $chart_active_user, tick_format);
            }else if (active_type === "4"){
                for (i in data){
                    draw_data.push([i, data[i][2]]);
                }
                data_set = [
                    {
                        label: "平均单次使用时长(时间单位：分钟)",
                        data: draw_data
                    }
                ];
                DrawLineChart(data_set, $chart_active_user, tick_format);
            }else if (active_type === "5"){
                for (i in data){
                    draw_data.push([i, data[i][2]]);
                }
                data_set = [
                    {
                        label: "平均日使用时长(时间单位：分钟)",
                        data: draw_data
                    }
                ];
                DrawLineChart(data_set, $chart_active_user, tick_format);
            }


        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}

$btn_active.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("1");
    query_active();
    chart_hover_display($chart_active_user, hover);
});
$btn_active.click();


$btn_active_of.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("2");
    query_active();
    chart_hover_display($chart_active_user, hover2);
});

$btn_open_game_num.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("3");
    query_login_num();
    chart_hover_display($chart_active_user, hover3);
});

$btn_single_use_time.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("4");
    query_login_num();
    chart_hover_display($chart_active_user, hover4);
});

$btn_avg_user_time.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("5");
    query_login_num();
    chart_hover_display($chart_active_user, hover5);
});

$btn_avg_open_num.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $active_type.val("6");
    query_login_num();
    chart_hover_display($chart_active_user, hover6);
});


function hover(x, y){
    return G_DATA[x][0] + ":" + y;
}

function hover2(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "新用户:" + G_DATA[x][2] + "</br>";
    var old_user = 0;
    if (G_DATA[x][1] > G_DATA[x][2]){
        old_user = G_DATA[x][1] - G_DATA[x][2];
    }
    str_html += "老用户:" + old_user + "</br>";
    str_html += "活跃用户:" + G_DATA[x][1];
    return str_html;
}

function hover3(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "总启动次数:" + G_DATA[x][1] + "</br>";
    return str_html;
}

function hover4(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "平均单次使用时长:" + G_DATA[x][1] + "</br>";
    return str_html;
}

function hover5(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "平均日使用时长:" + G_DATA[x][2] + "</br>";
    return str_html;
}

function hover6(x, y){
    var str_html = "<strong>" + G_DATA[x][0] + "</strong></br>";
    str_html += "平均值:" + G_DATA[x][2] + "</br>";
    return str_html;
}

$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#export_title"), $("#active_user_list"), "活跃用户");
});
