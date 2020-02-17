/**
 * Created by wangrui on 16/1/6.
 */



handleDatePickers();
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));

$("#start_date2").val(getNowFormatDate(0));
$("#end_date2").val(getNowFormatDate(0));

setPartnerData($("#user_channel").val(), $("#partner_list"));
setPartnerData($("#user_channel").val(), $("#partner_list2"));

$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $("#query_button").click();
});

$("#partner_list2").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $("#query_button2").click();
});

var device_name = {
    "Xiaomi": "小米",
    "nubia": "努比亚",
    "QiKU": "奇酷",
    "Meizu": "魅族",
    "Huawei": "华为"
};

$("#query_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querydevice',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            for (var d=0; d < data.length; d++){
                str_info += "<tr>";
                str_info += "<td>" + data[d][0] + "</td>";
//                var device_num = getPropertyCount(data[d]["device_num"]);
//                var account_num = getPropertyCount(data[d]["account_num"]);
                str_info += "<td>" + data[d][1] + "</td>";
                str_info += "<td>" + data[d][2] + "</td>";
                str_info += "<td>" + (parseInt(data[d][2]) - parseInt(data[d][1])) + "</td>";
                str_info += "</tr>";
            }
            $("#device_list").html(str_info);
        },
        error: function(XMLHttpRequest){
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});

$("#query_button").click();

function getProperty(obj){
    var count = 0;
    for(var o in obj){
        count ++;
    }
    return count;
}

$("#export_device").on("click", function(e){
    e.preventDefault();
    var export_title = "";
    $("#export_title").children().each(function(e){
        export_title += $(this).html() + ",";
    });

    var str_s = "";
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    $("#device_list").children().each(function(e){
        var str_data = "";
        $(this).children().each(function (e) {
            str_data += $(this).html() + ","
        });
        str_s += str_data;
        str_s += "|";
    });

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/exportdeviceexcel',
        data: {
            export_title: export_title,
            start_date: start_date,
            end_date: end_date,
            query_data: str_s
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            window.open(data["url"]);
        },
        error: function() {
            App.unblockUI(page_content);
            error_func();
        }
    })
});


$("#a_device_info").on("click", function(e){
    e.preventDefault();
    $("#query_button2").click();
});

$("#query_button2").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#user_channel").val();
    var start_date = $("#start_date2").val();
    var end_date = $("#end_date2").val();
    var device_type = $("#device_type").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    console.log(user_channel);
    $.ajax({
        type: 'get',
        url: '/querydeviceinfo',
        data: {
            device_type: device_type,
            user_channel: user_channel,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var title = "";
            var device_num = 0;
            var account_num = 0;
            if (device_type == "1"){
                title += "<th>账号</th>";
                title += "<th>设备</th>";
                title += "<th>设备个数</th>";
                var str_info = "";
                for (var d in data){
                    str_info += "<tr>";
                    str_info += "<td>" + d + "</td>";
                    var temp = "";
                    var c1 = 0;
                    for (var i in data[d]["data"]){
                        temp += "(" + i + "," + data[d]["data"][i] + ")" + ";";
                        c1 ++;
                    }
                    str_info += "<td>" + temp + "</td>";
                    str_info += "<td>" + c1 + "</td>";
                    str_info += "</tr>";
                    device_num += getProperty(data[d]["data"]);
                    account_num += 1;
                }
                $("#device_list2").html(str_info);
            }
            else{
                title += "<th>设备编号</th>";
                title += "<th>设备型号</th>";
                title += "<th>账号</th>";
                title += "<th>账号个数</th>";
                var str_info1 = "";
                for (var d1 in data){
                    str_info1 += "<tr>";
                    str_info1 += "<td>" + d1 + "</td>";
                    str_info1 += "<td>" + data[d1]["name"] + "</td>";
                    var temp2 = "";
                    var cc = 0;
                    for (var dd in data[d1]["data"]){
                        temp2 += "(" + dd + ")" + ";";
                        cc ++;
                    }
                    str_info1 += "<td>" + temp2 + "</td>";
                    str_info1 += "<td>" + cc + "</td>";
                    str_info1 += "</tr>";
                    device_num += 1;
                    account_num += getProperty(data[d1]["data"]);
                }
                $("#device_list2").html(str_info1);
            }
            $("#device_title").html(title);
            $("#count_info").html("设备总数:" +  "<span class='badge badge-success'>" + device_num + "</span>," + "账号总数:"
               + "<span class='badge badge-success'>" + account_num + "</span>");
        },
        error: function(XMLHttpRequest){
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});