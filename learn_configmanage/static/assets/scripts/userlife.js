/**
 * Created by wangrui on 15/1/20.
 */


handleDatePickers();
getGameServerData($("#select_game"), 1);
$("#appoint_date").val(getNowFormatDate(0));
$("#count_date").val(getNowFormatDate(0));

$("#query_button").bind("click", function (e) {
    e.preventDefault();
    var count_type = $("#query_type").val();
    var server = $("#select_game").val();
    var s_date = $("#appoint_date").val();
    var e_date = $("#count_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryuserlife',
        data: {count_type: count_type, server: server, s_date: s_date, e_date: e_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            str_info += "<tr>";
            str_info += "<td>" + data["login"] + "</td>";
            str_info += "<td>" + data["t_recharge"] + "</td>";
            str_info += "<td>" + data["recharge_num"] + "</td>";
            str_info += "<td>" + data["total_recharge_num"] + "</td>";
            str_info += "<td>" + data["total_recharge"] + "</td>";
            str_info += "<td>" + (data["total_recharge_num"] / data["total_login"] * 100.0).toFixed(2) + "%</td>";
            str_info += "</tr>";
            $("#life_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});





