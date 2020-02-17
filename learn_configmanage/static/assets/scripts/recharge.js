/**
 * Created by wangrui on 14/12/3.
 */


var default_date = function () {
    var now_time = getNowFormatDate(0);
    $("#text_date").val(now_time);
    $("#text_date_week").val(now_time);
    $("#text_date_month").val(now_time);
    handleDatePickers();
};
default_date();
getGameServerData($("#select_game"), 2);

setPartnerData($("#user_channel").val(), $("#partner_list"));

$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
});

var dayOfWeek = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];


var get_total_recharge = function () {
    var user_channel = $("#user_channel").val();
//    recharge_list_draw(0, {user_channel: user_channel}, '/getrechargetotal', $("#total_recharge_list"), $("#chart_total"));
    var game_id = $("#select_game").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/getrechargetotal",
            data: {user_channel: user_channel, game_id: game_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                $("#total_recharge").html(data["total"]);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
};
get_total_recharge();

$("#select_game").bind("change", function(e){
    e.preventDefault();
    get_total_recharge();
});

var drawRechargeDayChart = function(draw_data, div_flot){
    var dataset = [
        {
            label: "充值",
            data: draw_data
        }
    ];
    var options = {
        series:{
            lines: {
                show: true,
                lineWidth: 2,
//                fill: true,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.1
                        },
                        {
                            opacity: 1
                        }
                    ]
                }
            },
            points: {
                show: false
            },
            shadowSize: 5
        },
        xaxis:{
            mode: "time",
            tickSize: [1, "hour"],
            tickFormatter: function(v, axis){
                var date = new Date(v);
                return date.getHours() + "点";
            },
            axisLabel: "Time"
        },
        colors: ["#d12610"],
        yaxis: {
            color: "black",
            min:0,
            tickDecimals: 0,
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 12,
            axisLabelPadding: 3,
            tickFormatter: function(v, axies){
                return v.toFixed(axies.tickDecimals);
            }
        }
    };

    $.plot(div_flot, dataset, options);
};

var drawRechargeWeekChart = function(draw_data, div_flot){
    var dataset = [
        {
            label: "充值",
            data: draw_data
        }
    ];
    var options = {
        series:{
            lines: {
                show: true,
                lineWidth: 2,
//                fill: true,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.1
                        },
                        {
                            opacity: 0.1
                        }
                    ]
                }
            },
            points: {
                show: false
            },
            shadowSize: 5
        },
        xaxis:{
//            min:1,
//            tickSize:1
            mode: "time",
            tickSize: [1, "day"],
//            timeformat: "%m/%d",
            tickFormatter: function(v, axis){
//                console.log("test", new Date(v).getDay());
//                return dayOfWeek[new Date(v).getDay()];
                return new Date(v).getDay();
            },
            axisLabel: "Time"
        },
        colors: ["#d12610"],
        yaxis: {
            color: "black",
            min:0,
            tickDecimals: 0,
            axisLabelUseCanvas: true,
            axisLabelFontSizePixels: 12,
            axisLabelPadding: 3,
            tickFormatter: function(v, axies){
                return v.toFixed(axies.tickDecimals);
            }
        }
    };

    $.plot(div_flot, dataset, options);
};


$("#query_button").bind("click", function(e){
    e.preventDefault();
    var text_date = $("#text_date").val();
    var user_channel = $("#user_channel").val();

    var game_id = $("#select_game").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/getrechargeday",
            data: {user_channel: user_channel,
                   q_date: text_date,
                   game_id: game_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var draw_data = [];
                var ticks = [];
                var d_data = {};
                var x = 1;
                var amount = 0;
                for (var s in data["data"]){
                    var hour = parseInt(data["data"][s]["time"].split(" ")[1].split(":")[0]);
                    if (hour in d_data == false){
                        x = 1;
                        amount = 0
                    }
                    amount += data["data"][s]["amount"];
                    d_data[hour] = amount;
                    x += 1;
                }
                for (var i = 0; i <= 23; i++) {
                    var temp_data = [i - 1, 0];
                    if (i in d_data){

                        temp_data = [i - 1, d_data[i]];
                    }
                    var temp_ticks = [i, (i + 1) + "点"];
                    draw_data.push(temp_data);
                    ticks.push(temp_ticks);
                }
                var dataset = [
                    {
                        label: "充值日统计",
                        data: draw_data
                    }
                ];
                drawBarsChart(dataset, ticks, "center", 0.5, $("#chart_day"));
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});

$("#week_query_button").bind("click", function(e){
    e.preventDefault();
    var text_date_week = $("#text_date_week").val();
    var user_channel = $("#user_channel").val();

    var game_id = $("#select_game").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: "/getrechargeweek",
            data: {user_channel: user_channel,
                   q_date: text_date_week,
                   game_id: game_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var draw_data = [];
                var ticks = [];
                for (var i = 0; i <= data.length; i++) {
                    var temp_data = [i + 1, data[i]];
                    var temp_ticks = [i + 1, dayOfWeek[i]];
                    draw_data.push(temp_data);
                    ticks.push(temp_ticks);
                }
                var dataset = [
                    {
                        label: "充值周统计",
                        data: draw_data
                    }
                ];
                drawBarsChart(dataset, ticks, "center", 0.5, $("#chart_week"));
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});


$("#month_query_button").bind("click", function(e){
    e.preventDefault();
    var text_date_month = $("#text_date_month").val();
    var user_channel = $("#user_channel").val();
    var game_id = $("#select_game").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: "/getrechargemonth",
            data: {
                q_date: text_date_month,
                user_channel: user_channel,
                game_id: game_id
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var draw_data = [];
                var ticks = [];
                for (var i = 0; i <= data.length; i++) {
                    var temp_data = [i + 1, data[i]];
                    var temp_ticks = [i + 1, i + 1];
                    draw_data.push(temp_data);
                    ticks.push(temp_ticks);
                }
                var dataset = [
                    {
                        label: "充值月统计",
                        data: draw_data
                    }
                ];
                drawBarsChart(dataset, ticks, "center", 0.5, $("#chart_month"));
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});

$("#a_day").on("click", function(e){
    e.preventDefault();
    $("#query_button").click();
});

$("#a_week").on("click", function(e){
    e.preventDefault();
    $("#week_query_button").click();
});

$("#a_month").on("click", function(e){
    e.preventDefault();
    $("#month_query_button").click();
});