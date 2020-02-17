/**
 * Created by wangrui on 16/11/24.
 */

handleDatePickers();
var now_time = getNowFormatDate(0);
$("#text_date").val(now_time);

function getOnline() {
    var success = function (data) {
        var str_title = "";
        var str_html = "";
        var online_data = [];
        var ticks = [];
        for (var i = 0; i < data["title"].length; i++) {
            str_title += "<th>" + data["title"][i] + "</th>";
        }
        for (var m = 0; m < data["data"].length; m++) {
            str_html += '<tr>';
            ticks.push([m, m+1]);
            online_data.push([m, data["data"][m][1]]);
            for (var k = 0; k < data["data"][m].length; k++) {
                str_html += '<td>' + data["data"][m][k] + '</td>';
            }
            str_html += '</tr>';
        }
        var bar_data_set = [
            {
                label: "最高在线人数",
                data: online_data
            }
        ];
        drawBarsChart(bar_data_set, ticks, "center", 0.2, $("#online_chart"));
        $("#online_title").html(str_title);
        $("#online_list").html(str_html);
    };
    var text_data = $("#text_date").val();
    var req = {
        name: "online",
        date: text_data
    };
    my_ajax(true, "/queryaudit", "get", req, true, success);
}

getOnline();

$("#div_date").bind("changeDate", function(e){
    e.preventDefault();
    getOnline();
});