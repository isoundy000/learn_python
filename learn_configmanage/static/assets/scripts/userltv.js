/**
 * Created by wangrui on 16/4/28.
 */
/**
 * Created by wangrui on 15/11/24.
 */

handleDatePickers();
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

setPartnerData($("#user_channel").val(), $("#partner_list"));

$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    get_ltv_table_data();
});


$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    get_ltv_table_data();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    get_ltv_table_data();
});

$("#query_type").on("change", function (e) {
    e.preventDefault();
    get_ltv_table_data();
});


function query_retain_user(){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var user_channel = $("#user_channel").val();
    var query_type = $("#query_type").val();
    var success = function (data) {
        var str_info = "";
        var total_list = ['总数',0];
        var row_total_num = [0, 0];
        for (var i in data) {
            str_info += "<tr>";
            str_info += "<td>" + data[i][0] + "</td>";
            var reg_users = data[i][1];
            str_info += "<td>" + reg_users + "</td>";
            for (var x = 2; x < data[i].length; x++) {
                if (total_list.length <= x){
                    total_list.push(0);
                    row_total_num.push(0);
                }
                if (data[i][x] == 0) {
                    str_info += "<td>-</td>";
                }
                else {
                    total_list[x] += data[i][x];
                    row_total_num[x] += data[i][1];
                    str_info += "<td>" + parseFloat(data[i][x] / data[i][1]).toFixed(2) + "</td>";
                }
            }
            str_info += "</tr>";
            total_list[1] += reg_users;
        }
        str_info += "<tr class='success'>";
        str_info += "<td>" + total_list[0] + "</td>" +"<td>" + total_list[1] + "</td>";
        for (i=2;i<total_list.length;i++){
            if (total_list[i] === 0) {
                str_info += "<td>-</td>";
            }
            else {
                str_info += "<td>" + parseFloat(total_list[i] / row_total_num[i]).toFixed(2) + "</td>";
            }
        }
        str_info += "</tr>";
        $("#user_ltv_list").html(str_info);
    };
    var data = {
        query_type: query_type,
        channel: user_channel,
        start_date: start_date,
        end_date: end_date
    };
    my_ajax(true, '/queryuserltv', 'get', data, false, success);
}
var ltv_table_obj;
var get_ltv_table_data = function () {

    var ajax_data = {
        "url": "/queryuserltv",
        "type": "GET",
        "data": {
            query_type: $("#query_type").val(),
            channel: $("#user_channel").val(),
            start_date: $("#start_date").val(),
            end_date: $("#end_date").val()
        },
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#ltv_table_processing').hide();
        },
        "dataSrc": function (result) {
            var total_list = ['总数',0];
            var row_total_num = [0, 0];
            for (var i = 0; i < result.length; i++) {
                for(var x=2; x<result[i].length; x++){
                    if (total_list.length <= x){
                        total_list.push(0);
                        row_total_num.push(0);
                    }
                    if (result[i][x] === 0) {
                        result[i][x] = '-';
                    }
                    else {
                        total_list[x] += result[i][x];
                        row_total_num[x] += result[i][1];
                        result[i][x] = parseFloat(result[i][x] / result[i][1]).toFixed(2);
                    }

                }
                total_list[1] += result[i][1];
            }
            for (i=2;i<total_list.length;i++){
                if (total_list[i] === 0) {
                    total_list[i] = '-';
                }
                else {
                    total_list[i] = parseFloat(total_list[i] / row_total_num[i]).toFixed(2);
                }
            }
            result.push(total_list);
            return result;
        }
    };
    var columns = [{'title': '时间','width': '50px'},{"title": "新增用户"}, {"title": "当天"},{"title":"2天"},{"title":"3天"},{"title":"4天"},{"title":"5天"}
   ,{"title":"6天"},{"title":"7天"},{"title":"8天"},{"title":"9天"},{"title":"10天"},{"title":"11天"},{"title":"12天"},{"title":"13天"}
    ,{"title":"14天"},{"title":"15天"},{"title":"16天"},{"title":"17天"},{"title":"18天"},{"title":"19天"},{"title":"20天"},{"title":"21天"}
    ,{"title":"22天"},{"title":"23天"},{"title":"24天"},{"title":"25天"},{"title":"26天"},{"title":"27天"},{"title":"28天"},{"title":"29天"}
    ,{"title":"30天"},{"title":"45天"},{"title":"60天"},{"title":"90天"},{"title":"180天"},{"title":"360天"},{"title":"720天"}];
    var columnDefs = [];
    ltv_table_obj = $("#ltv_table").DataTable({
        "destroy" : true,
        "autoWidth" : false,
        "processing" : true,
        "ajax": ajax_data,
        "searching": false,    //去掉搜索框方法三：这种方法可以
        "lengthChange": false,
        "paging": false,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage,
        "createdRow": function( row, data ) {
            if ( data[0] === "总数" ) {
              $(row).css("background-color","#dff0d8");
            }
          },
        "scrollX": true,
        fixedColumns: { //固定列的配置项
            // rightColumns:2, //固定右边第一列
            leftColumns: 1
        }
   });
};
get_ltv_table_data();


$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#export_title"), $("#user_ltv_list"), "用户LTV");
});
