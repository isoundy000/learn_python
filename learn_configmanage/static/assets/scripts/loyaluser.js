/**
 * Created by wangrui on 15/1/22.
 */

handleDatePickers();
getGameServerData2($("#select_gameserver"));
$("#q_date").val(getNowFormatDate(1));

$("#query_button").bind("click", function(e){
    e.preventDefault();
    var q_date = $("#q_date").val();
    var server_id = $("#select_gameserver").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryloyaluser',
        data: {q_date: q_date, server_id: server_id},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            str_info += "<tr>";
            str_info += "<td>" + data["total"] + "</td>";
            str_info += "<td>" + data["two_count"]  + "/" + commonPercent(data["two_count"], data["total"]) + "%</td>";
            str_info += "<td>" + data["three_count"]  + "/" + commonPercent(data["three_count"], data["total"]) + "%</td>";
            str_info += "<td>" + data["seven_count"]  + "/" + commonPercent(data["seven_count"], data["total"]) + "%</td>";
            str_info += "<td>" + data["thirty_count"]  + "/" + commonPercent(data["thirty_count"], data["total"]) + "%</td>";
            str_info += "</tr>";
            $("#lose_list").html(str_info);
        },
        error: function(){
            App.unblockUI(page_content);
            error_func();
        }
    })
});