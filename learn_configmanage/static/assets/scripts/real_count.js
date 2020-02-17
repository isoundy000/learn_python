/**
 * Created by wangrui on 14/12/25.
 */

var $partner = $("#partner_list");
setPartnerData($("#user_channel").val(), $partner);
var Interval = 1000 * 60 * 15;
handleDatePickers();

$("#query_date").val(getNowFormatDate(0));

var DrawLineChartReal = function (dataset, div_flot) {
    var options = {
        series: {
            lines: {
                show: true,
                lineWidth: 2,
                fill: false,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.05
                        },
                        {
                            opacity: 0.01
                        }
                    ]
                }
            },
            points: {
                show: true,
                radius: 2
            },
            shadowSize: 2
        },
        grid: {
            hoverable: true,
            clickable: true,
            tickColor: "#eee",
            borderWidth: 0
        },
        // colors: [],
        xaxis: {
            mode: "time",
            tickSize: [15, "minute"],
            tickFormatter: function(v, axis){
                var date = new Date(v);
                var hour = date.getHours();
                var minute = date.getMinutes();
                if (minute == 0){
                    return hour + ":" + minute + "0";
                }
                else{
                    return "";
                }
            }
        },
        yaxis: {
            ticks: 11,
            tickDecimals: 0
        }
    };

    $.plot(div_flot, dataset, options);
};



var query_real_count = function () {
    var success = function (data) {
        var draw_data_2 = [];
        var draw_data = [];
        $("#reg_total").html(data["total_reg"]);
        $("#pay_user").html(data["recharge_user"]);
        $("#pay_num").html(data["recharge_num"]);
        $("#new_pay_user").html(data["new_pay_user"]);
        var chart_day = $("#chart_day");
        var start_time = query_date.replace(/-/g, "/");
        var s_time = new Date(start_time).getTime();
        var s_time2 = new Date(start_time).getTime();
        draw_data.push([s_time, 0]);
        draw_data_2.push([s_time, 0]);
        for (var i = 0; i <= 24 * 4 - 1; i++) {
            var temp = s_time;
            s_time += Interval;
            var x = 0;
            var tt = 0;
            for (var s in data["data"]) {
                var create_time = data["data"][s]["createtime"];
                var now_date_s = create_time.replace(/-/g, "/");
                now_date_s = new Date(now_date_s).getTime();
                if (now_date_s >= temp && now_date_s <= s_time) {
                    x += 1;
                    delete data["data"][s];
                }
            }
            for (var dd in data["recharge_data"]) {
               
                var create_time2 = data["recharge_data"][dd]["recvtime"];
                var now_date_s2 = create_time2.replace(/-/g, "/");
                now_date_s2 = new Date(now_date_s2).getTime();
                if (now_date_s2 >= temp && now_date_s2 <= s_time) {
                    tt += 1;
                    delete data["recharge_data"][dd];
                }
            }
            draw_data.push([s_time, x]);
            draw_data_2.push([s_time, tt]);
        }
        var dataset = [
            {
                label: "新增用户",
                data: draw_data
            },
            {
                label: "付费用户",
                data: draw_data_2
            }
        ];
        DrawLineChartReal(dataset, chart_day);
    };
    var query_date = $("#query_date").val();
    var user_channel = $("#user_channel").val();
    
    var data = {
        query_date: query_date, user_channel: user_channel
    };
    
    my_ajax(true, "/queryrealcount", 'get', data, true, success);
};
query_real_count();

$("#div_date").on("changeDate", function(e){
    e.preventDefault();
    query_real_count();
});

$("#partner_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    query_real_count();
});

function hover(x, y){
    var dd = new Date(x);
    var hour = dd.getHours() >= 10 ? dd.getHours() : "0" + dd.getHours();
    var minute = dd.getMinutes() >= 10 ? dd.getMinutes() : "0" + dd.getMinutes();
    return hour + ":" + minute + "[" + y + "]";
}

chart_hover_display($("#chart_day"), hover);


$("#export_excel").on("click", function(e){
    e.preventDefault();
    var query_date = $("#query_date").val();
    $.ajax({
        type: 'get',
        url: '/exportnewuserrealexcel',
        data: {
            query_date: query_date,
            excel_data: JSON.stringify(draw_data_2)
        },
        dataType: 'JSON',
        success: function (data) {
            var message = "";
            if (data["status"] == true){
                message = "任务已提交,请到<a href='/downcenter'>下载中心</a>下载.";
            }
            else{
                message = "任务下载失败.请重新下载.";
            }
            Common.alert_message($("#error_modal"), 1, message);
        },
        error: function(XMLHttpResponse) {
            error_func(XMLHttpResponse);
        }
    })
});



