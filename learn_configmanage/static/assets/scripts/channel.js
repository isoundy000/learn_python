/**
 * Created by wangrui on 15/11/26.
 */

handleDatePickers();
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

var $btn_active = $("#btn_active_user");
var $btn_new = $("#btn_new_user");

var $btn_pay_user = $("#btn_pay_user");
var $btn_pay_num = $("#btn_pay_num");
var $btn_second_retain = $("#btn_second_retain");

var $chart_channel = $("#chart_channel");
var G_DATA = null;

function chart_type(data){
    var draw_data = [];
    var i = 1;
    for(var d in data["data"]){
        var temp = [];
        if (i > 10){
            break;
        }
        for (var s in data["data"][d]["data"]){
            temp.push([s, data["data"][d]['data'][s]]);
        }
        draw_data.push({
            label: data["data"][d]["name"],
            data: temp
        });
        i += 1;
    }
    return draw_data;
}


function tick_format(v){
    var temp = G_DATA[v].split("-");
    return temp[1] + "-" + temp[2];
}

function query_channel(channel_type){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querychannelinfo',
        data: {
            channel_type: channel_type,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var draw_data = chart_type(data);
            G_DATA = data["dates"];
            DrawLineChart(draw_data, $chart_channel, tick_format);
         },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });

    chart_hover_display($chart_channel, hover);
}

function query_channel_table(day_type){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querychanneltable',
        data: {
            day_type: day_type
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var str_info = "";
            for (var d in data["data"]){
                str_info += "<tr>";
                str_info += "<td>" + data["data"][d]["channel_name"] + "</td>";
                str_info += "<td>" + data["data"][d]["new_user"] + "</td>";
                str_info += "<td>" + data["data"][d]["active_user"] + "</td>";
                str_info += "<td>" + data["data"][d]["pay_user"] + "</td>";
                str_info += "<td>" + data["data"][d]["pay_num"] + "</td>";
                str_info += "<td>" + data["data"][d]["total_user"] + "(" + data["data"][d]["total_user_rate"] + "%)" + "</td>";
                str_info += "</tr>";
            }
            $("#table_channel").html(str_info);
         },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}

$("#today").on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel_table("today");
});
$("#today").click();


$("#yesterday").on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel_table("yesterday");
});

function hover(x, y){
    return G_DATA[x] + ":" + y;
}


$btn_new.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel("new");
});

$btn_active.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel("active");
});

$btn_pay_user.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel("pay_user");
});

$btn_pay_num.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel("pay_num");
});

$btn_second_retain.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    query_channel("second_login");
});

$btn_new.click();