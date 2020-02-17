/**
 * Created by wangrui on 15/1/30.
 */

handleDatePickers();
getGameServerData($("#select_gameserver"), 2);
// getGameServerData($("#select_gameserver1"), 1);
var Interval = 1000 * 300;
var WEEKIntToChinese = {
    1:"一",
    2:"二",
    3:"三",
    4:"四",
    5:"五",
    6:"六",
    7:"日"
};

var QUEUE_TYPE = {
    "game": "游戏人数",
    "valid": "空余人数",
    "queue": "排队人数",
    "gametime": "游戏超时人数",
    "queuetime": "排队超时人数",
    "in_": "进入人数"
};
var now_time = getNowFormatDate(2);
$("#text_date").val(now_time);
// $("#queue_date").val(now_time);


function button_click_func(){
    var $type_ul = $("#type_ul");
    $type_ul.children().each(function(e){
        if ($(this).hasClass("active")){
            $(this).children("a").click();
        }
    })
}


$("#div_date").bind("changeDate", function(e){
    e.preventDefault();
    button_click_func();
});


$("#select_gameserver").on("change", function(e){
    e.preventDefault();
    button_click_func();
});


$("#a_day").on("click", function(e){
    e.preventDefault();
    var text_date = $("#text_date").val();
    var server_id = $("#select_gameserver").val();
    $.ajax({
            type: 'get',
            url: '/getonline',
            data: {server_id: server_id, q_date: text_date},
            dataType: 'JSON',
            success: function (data) {
                var chart_day = $("#chart_day");
                var draw_data_high_yes = [];
                var draw_data_high_tod = [];
                var draw_data_high_qd = [];
                if (data != null){
                    var start_time = data[0][0]["otime"].replace(/-/g, "/");
                    var s_time = new Date(start_time).getTime();
                    for (var i = 0; i < data[0].length; i++) {
                        var high_data = [];
                        s_time += Interval;
                        high_data = [s_time, data[0][i]["high"]];
                        draw_data_high_qd.push(high_data);
                    }
                    var start_time2 = data[0][0]["otime"].replace(/-/g, "/");
                    var s_time2 = new Date(start_time2).getTime();
                    for (var k = 0; k < data[1].length; k++) {
                        var high_data2 = [];
                        s_time2 += Interval;
                        high_data2 = [s_time2, data[1][k]["high"]];
                        draw_data_high_yes.push(high_data2);
                    }
                    var start_time3 = data[0][0]["otime"].replace(/-/g, "/");
                    var s_time3 = new Date(start_time3).getTime();
                    for (var s = 0; s < data[2].length; s++) {
                        var high_data3 = [];
                        s_time3 += Interval;
                        high_data3 = [s_time3, data[2][s]["high"]];
                        draw_data_high_tod.push(high_data3);
                    }
                    var data_set = [
                        {
                            label: text_date + "在线人数",
                            data: draw_data_high_qd
                        },
                        {
                            label: "昨日在线人数",
                            data: draw_data_high_yes
                        },
                        {
                            label: "今日在线人数",
                            data: draw_data_high_tod
                        }
                        
                    ];
                    drawLineChartTime(data_set, chart_day);
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});
$("#a_day").click();

function hover(x, y){
    var dd = new Date(x);
    var hour = dd.getHours() >= 10 ? dd.getHours() : "0" + dd.getHours();
    var minute = dd.getMinutes() >= 10 ? dd.getMinutes() : "0" + dd.getMinutes();
    return hour + ":" + minute + "[" + y + "]";
}

chart_hover_display($("#chart_day"), hover);

$("#query_button").click();


$("#a_week").on("click", function(e){
    e.preventDefault();
    var q_date = $("#text_date").val();
    var page_content = $('.page-content');
    var server_id = $("#select_gameserver").val();
    App.blockUI(page_content, false);
    var success = function (data) {

    };
    $.ajax({
            type: 'get',
            url: '/getonlinebyweek',
            data: {server_id: server_id, q_date: q_date},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var high_data = [];
                var chart_week = $("#chart_week");
                var ticks = [];
                var m = 0;
                for (var i = 0; i < data.length; i++) {
                    for (var k = 0; k < 24; k++) {
                        if (k == 0) {
                            ticks.push([i * 24 + k, WEEKIntToChinese[(i + 1)]])
                        }
                        else {
                            if (k % 6 == 0) {
                                if (k != 24) {
                                    ticks.push([i * 24 + k, k])
                                }
                                else {
                                    ticks.push([i * 24 + k, ""])
                                }
                            }
                            else {
                                ticks.push([i * 24 + k, ""])
                            }
                        }
                        var a_count = 0;
                        var high = 0;
                        if (data[i][k] == null) {
                            high = 0;
                            a_count = 0;
                        }
                        else {
                            if (data[i][k]["high"] == null) {
                                high = 0;
                            } else {
                                high = data[i][k]["high"];
                            }
                        }
                        var temp_data1 = [m, high];
                        m += 1;
                        high_data.push(temp_data1);
                    }
                }
                var dataset = [
                    {
                        label: "最高在线人数",
                        data: high_data
                    }
                ];
                drawBarsChart(dataset, ticks, "center", 0.5, chart_week);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});

var G_DATA = null;

$("#a_month").on("click", function(e){
    e.preventDefault();
    var q_date = $("#text_date").val();
    var page_content = $('.page-content');
    var server_id = $("#select_gameserver").val();
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/getonlinebymonth',
        data: {server_id: server_id, q_date: q_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            G_DATA = data;
            console.log(data);
            var high_data = [];
            var chart_month = $("#chart_month");
            var ticks = [];
            for (var i = 0; i < data.length; i++) {
                var a_count = 0;
                var high = 0;
                if (data[i] != null){
                    a_count = data[i]["a_count"];
                    high = data[i]["high"];
                }
                var temp_data1 = [i, high];
                high_data.push(temp_data1);
                ticks.push([i, data[i]["date"]]);
            }
            var dataset = [
                {
                    label: "最高在线人数",
                    data: high_data
                }
            ];
            drawBarsChart(dataset, ticks, "center", 0.2, chart_month);
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});


function hover3(x, y){
    var str_html = "<strong>" + G_DATA[x]["date"] + "</strong></br>";
    str_html += "最高在线人数:" + G_DATA[x]["high"] + "</br>";
    str_html += "平均在线人数:" + G_DATA[x]["a_count"];
    return str_html;
}


chart_hover_display($("#chart_month"), hover3);

$("#a_queue").on("click", function(e){
    e.preventDefault();
    var str_info = "";
    var i = 0;
    for (var q in QUEUE_TYPE) {
        if (i == 0){
            str_info += "<label class=\"checkbox-inline\"><input checked type=\"checkbox\" name=\"q_type\" value=\"" +
                    q + "\">" + QUEUE_TYPE[q] + "</label>";
        }
        else{
            str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"q_type\" value=\"" +
                    q + "\">" + QUEUE_TYPE[q] + "</label>";
        }
        i += 1;
    }
//    $("input[name='q_type']:first").prop("checked", true);
//    $("input[name='q_type']").parent("span").addClass("checked");
    $("#queue_type").html(str_info);
    $("#queue_btn").click();
});

$("#select_gameserver1").on("change", function(e){
    e.preventDefault();
    $("#queue_btn").click();
});

$("#queue_btn").on("click", function(e){
    e.preventDefault();
    var queue_date = $("#queue_date").val();
    var server = $("#select_gameserver1").val();
    var queue_type = "";

    $("input[name='q_type']:checked").each(function(){
        queue_type += $(this).val() + ",";
    });
    var queue_type_arr = queue_type.split(",");
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryqueue',
            data: {
                server_id: server,
                q_date: queue_date,
                queue_type: queue_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var chart_queue = $("#chart_queue");
                var start_time = data[0]["time"].replace(/-/g, "/");
                var s_time = new Date(start_time).getTime();
                var data_set = [];
                for (var j = 0; j<queue_type_arr.length; j++){
                    var temp = [];
                    temp.push([s_time, 0]);
                    for (var i = 0; i < data.length; i++) {
                        s_time += Interval;
                        var find_s = "m_" + queue_type_arr[j];
                        temp.push([s_time, data[i][find_s]]);
                    }
                    s_time = new Date(start_time).getTime();
                    if (queue_type_arr[j].length != 0){
                        data_set.push({
                            label: QUEUE_TYPE[queue_type_arr[j]],
                            data: temp
                        });
                    }
                }
                drawLineChartTime(data_set, chart_queue);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});

function hover2(x, y){
    var dd = new Date(x);
    var hour = dd.getHours() >= 10 ? dd.getHours() : "0" + dd.getHours();
    var minute = dd.getMinutes() >= 10 ? dd.getMinutes() : "0" + dd.getMinutes();
    return hour + ":" + minute + "[" + y + "]";
}

chart_hover_display($("#chart_queue"), hover2);