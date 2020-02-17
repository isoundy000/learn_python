/**
 * Created by wangrui on 16/8/26.
 */

var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $btn_query_data = $('#btn_query_data');
var $server_type = $('#server_type');


handleDatePickers();
$start_date.val(getNowFormatDate(0));
$end_date.val(getNowFormatDate(0));


function query_server_data(){
    var data = {
        'start_date': $start_date.val(),
        'end_date': $end_date.val(),
        'server_type': $server_type.val()
    };

    var success = function(data){
        var str_html = "";
        data.sort(function (a, b) {
            return a['gid'] - b['gid'];
        });
        for(var i=0; i<data.length; i++){
            str_html += "<tr>";
            var status = data[i]["status"];
            if (status == 1){
                str_html += "<td><span class='badge badge-success'>" + data[i]["gid"] + "区:" + data[i]["name"] + "</span></td>";
            }else{
                str_html += "<td>" + data[i]["gid"] + "区:" + data[i]["name"] + "</td>";
            }
            str_html += "<td>" + data[i]["create_time"] + "</td>";
            str_html += "<td>" + data[i]["online"] + "</td>";
            str_html += "<td>" + data[i]["recharge_num"] + "</td>";
            str_html += "<td>" + data[i]["pay_num"] + "</td>";
            str_html += "<td>" + data[i]["role_num"] + "</td>";
            str_html += "<td>" + data[i]["login_num"] + "</td>";
            var arppu = 0;
            if (data[i]["pay_num"] != 0){
                arppu = parseFloat(data[i]["recharge_num"] / data[i]["pay_num"]).toFixed(2);
            }
            var arpu = 0;
            var pay_percent = 0;
            if (data[i]["login_num"] != 0){
                pay_percent = parseFloat(data[i]["pay_num"] / data[i]["login_num"] * 100).toFixed(2);
                arpu = parseFloat(data[i]["recharge_num"] / data[i]["login_num"]).toFixed(2);
            }
            str_html += "<td>" + arppu + "</td>";
            str_html += "<td>" + arpu + "</td>";
            str_html += "<td>" + pay_percent + "%</td>";

            str_html += "</tr>";
        }
        $("#server_data").html(str_html);
    };
    my_ajax(true, "/queryserverdata", 'get', data, true, success);
}
query_server_data();

$btn_query_data.click(function () {
    query_server_data();
});
