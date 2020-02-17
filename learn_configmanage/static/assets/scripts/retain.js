/**
 * Created by wangrui on 15/11/24.
 */
display_left_count();
handleDatePickers();
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

setPartnerData($("#user_channel").val(), $("#partner_list"));

$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    query_retain_user();
});


$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_retain_user();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_retain_user();
});
$('.typeRadio').change(function () {
    query_retain_user();
});

function query_retain_user(){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var user_channel = $("#user_channel").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryretainuser',
        data: {
            channel: user_channel,
            start_date: start_date,
            end_date: end_date,
            query_type: $('#query_user_type input[name="typeRadio"]:checked').val()
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            for (var i in data){
                str_info += "<tr>";
                str_info += "<td>" + data[i][0] + "</td>";
                var reg_users = data[i][1];
                str_info += "<td>" + reg_users + "</td>";
                for (var x = 2; x < data[i].length; x++){
                    var percent_num = commonPercent(data[i][x], reg_users);
                    if (data[i][x] == 0){
                        str_info += "<td>-</td>";
                    }
                    else{
                        str_info += "<td class='success'>" + percent_num + "%</td>";
                    }
                }
                str_info += "</tr>";
            }
            $("#retain_user_list").html(str_info);
        },
        error: function(XMLHttpRequest){
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
}
query_retain_user();


$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#export_title"), $("#retain_user_list"), "留存用户");
});
