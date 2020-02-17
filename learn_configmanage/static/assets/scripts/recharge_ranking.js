
handleDatePickers();
display_left_count();
getGameServerData($("#select_gameserver_top"), 2);

setPartnerData($("#user_channel").val(), $("#partner1_list"));



$("#partner1_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($("#partner1_list").val());
    $("#top_query_btn").click();
});


$("#recharge_start_date").val(getNowFormatDate(1));
$("#recharge_end_date").val(getNowFormatDate(0));


$("#top_query_btn").on("click", function (e) {
    e.preventDefault();
    var start_date = $("#recharge_start_date").val();
    var end_date = $("#recharge_end_date").val();
    var top_select = $("#top_select").val();
    var user_channel = $("#user_channel").val();
    var game_id = $("#select_gameserver_top").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querytoprecharge',
        data: {start_date: start_date,
            end_date: end_date,
            user_channel: user_channel,
            game_id: game_id,
            top_select: top_select},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0) {
                for (var d = 0; d < data.length; d++) {
                    str_info += "<tr>";
                    str_info += "<td>" + data[d]["game"] + "</td>";
                    str_info += "<td>" + data[d]["name"] + "</td>";
                    str_info += "<td>" + data[d]["recharge"] + "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#role_recharge_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});