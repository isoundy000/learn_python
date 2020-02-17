/**
 * Created by wangrui on 15/1/31.
 */
handleDatePickers();
//getPartnerData($("#select_channel"));

getGameServerData2($("#select_gameserver"));

$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));


$("#query_button").on("click", function(e){
    e.preventDefault();
    var partner = $("#user_channel").val();
    var game = $("#select_gameserver").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: "/querylevelconsume",
        data: {partner: partner, game: game, start_date: start_date, end_date: end_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            for(var s in data){
                str_info += "<tr>";
                str_info += "<td>" + data[s]["level"] + "</td>";
                str_info += "<td>" + data[s]["users"] + "</td>";
                str_info += "<td>" + data[s]["usegold"] + "</td>";
                str_info += "<td>" + data[s]["usegold_person"] + "</td>";
                if (data[s]["usegold"] == 0 || data[s]["usegold_person"] == 0){
                    str_info += "<td>0</td>";
                }
                else{
                    str_info += "<td>" + (data[s]["usegold"] / data[s]["usegold_person"]).toFixed(0) + "</td>";
                }
                str_info += "<td>" + data[s]["recharge_person"] + "</td>";
                str_info += "<td>" + data[s]["recharge_num"] + "</td>";
                str_info += "<td>" + data[s]["getgold"] + "</td>";
                str_info += "</tr>";
            }
            $("#consume_list").html(str_info);
        },
        error: function () {
            App.unblockUI(page_content);
            error_func();
        }
    })
});