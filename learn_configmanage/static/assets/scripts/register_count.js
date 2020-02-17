/**
 * Created by wangrui on 14/12/25.
 */

handleDatePickers();
//var Interval = 1000 * 3600;
setPartnerData($("#user_channel").val(), $("#partner_list"));


$("#partner_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    get_registers();
});

$("#query_date").val(getNowFormatDate(0));


var get_registers = function () {
    var user_channel = $("#user_channel").val();
    var page_content = $('.page-content');
    var query_date = $("#query_date").val();
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/getdayregist',
        data: {user_channel: user_channel, query_date: query_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            $("#reg_total").html(data["total_reg"]);
            $("#pay_user").html(data["recharge_user"]);
            $("#pay_num").html(data["recharge_num"]);
            $("#new_pay_user").html(data["new_pay_user"]);
            var chart_day = $("#chart_day");
            var draw_data = [];
            var ticks = [];
            var d_data = {};
            var x = 1;
            for (var s in data["data"]) {
                var hour = parseInt(data["data"][s]["createtime"].split(" ")[1].split(":")[0]);
                if (hour in d_data == false) {
                    x = 1;
                }
                d_data[hour] = x;
                x += 1;
            }
            for (var i = 0; i <= 23; i++) {
                var temp_data = [i, 0];
                if (i in d_data) {

                    temp_data = [i, d_data[i]];
                }
                var temp_ticks = [i, i + "点"];
                draw_data.push(temp_data);
                ticks.push(temp_ticks);
            }
            var dataset = [
                {
                    label: "新增用户",
                    data: draw_data
                }
            ];
            drawBarsChart(dataset, ticks, "center", 0.5, chart_day);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
};
get_registers();


$("#flush_current").bind("click", function (e) {
    e.preventDefault();
    get_registers();
});


