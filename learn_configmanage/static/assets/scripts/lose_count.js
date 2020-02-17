/**
 * Created by wangrui on 14/12/29.
 */
handleDatePickers();

$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(1));

setPartnerData($("#user_channel").val(), $("#partner_list"));

$("#partner_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    query_lose();
});

var G_DATA = null;

function tick_format(v){
    var temp = G_DATA[v].split("-");
    return temp[1] + "-" + temp[2];
}

$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_lose();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_lose();
});

function query_lose(){
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var export_type = $("#export_type").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querylose',
        data: {
            channel: user_channel,
            start_date: start_date,
            end_date: end_date,
            tag: export_type
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var draw_data = [];
            G_DATA = data["dates"];
            for (var i in data["data"]){
                str_info += "<tr>";
                str_info += "<td>" + data["dates"][i] + "</td>";
                str_info += "<td>" + parseInt(data["data"][i][0]) + "</td>";
                var active_user = data["data"][i][1];
                var lose_percent = 0;
                if (active_user != 0){
                    lose_percent = commonPercent(data["data"][i][0], active_user);
                }
                str_info += "<td>" + lose_percent + "%</td>";
                str_info += "</tr>";
                draw_data.push([i, data["data"][i][0]]);
            }
            $("#lose_list").html(str_info);
            var data_set = [
                {
                    label: "流失用户",
                    data: draw_data
                }
            ];
            DrawLineChart(data_set, $("#chart_lose"), tick_format);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
}
var $btn_seven = $("#btn_seven");
var $btn_fourteen = $("#btn_fourteen");
var $btn_thirty = $("#btn_thirty");

$btn_seven.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#export_type").val("7");
    query_lose();
});
$btn_seven.click();

$btn_fourteen.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#export_type").val("14");
    query_lose();
});

$btn_thirty.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    $("#export_type").val("30");
    query_lose();
});


$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#export_title"), $("#lose_list"), "流失用户");
});