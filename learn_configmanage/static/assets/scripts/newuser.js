/**
 * Created by wangrui on 15/11/18.
 */

display_left_count();
handleDatePickers();

var $partner = $("#partner_list");
setPartnerData($("#user_channel").val(), $partner);

$partner.on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    query_new_user();
});

$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));


var G_DATA = null;

$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_new_user();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_new_user();
});


function tick_format(v){
    var temp = G_DATA[v][0].split("-");
    return temp[1] + "-" + temp[2];
}

function query_new_user(){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var user_channel = $("#user_channel").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryregistuser',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var str_info = "";
            var draw_data = [];
            G_DATA = data;

            for(var i in data){
                str_info += "<tr>";
                str_info += "<td>" + data[i][0] + "</td>";
                str_info += "<td>" + data[i][1] + "</td>";
                str_info += "</tr>";
                draw_data.push([i, data[i][1]]);
            }
            var data_set = [
                {
                    label: "新增用户",
                    data: draw_data
                }
            ];
            DrawLineChart(data_set, $("#chart_new_user"), tick_format);
            $("#new_user_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}

query_new_user();

function hover(x, y){
    return G_DATA[x][0] + ":" + y;
}
chart_hover_display($("#chart_new_user"), hover);


$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#new_user_title"), $("#new_user_list"), "新增用户");
});