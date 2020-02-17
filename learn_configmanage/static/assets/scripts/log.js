/**
 * Created by wangrui on 14-10-13.
 */
/**
 * Created by wangrui on 14-10-13.
 */

handleDatePickers();
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));


!function get_user() {
    var success = function(data){
        var str_info = "";
        str_info += "<option value=''>所有人</option>";
        for (var i in data) {
            str_info += "<option value='" + data[i].username + "'>" + data[i].username + "</option>";
        }
        $("#user_select").html(str_info);
    };

    my_ajax(true, '/getalluser', 'get', {}, true, success);
}();

var query_log = function () {
    var ajax_url = "/querylog";
    var aoColumns = [
        {
            "mDataProp": "type",
            'sClass': 'center',
            "sTitle": "类型"
        },
        {
            "mDataProp": "user",
            'sClass': 'center',
            "sTitle": "用户"
        },
        {
            "mDataProp": "ip",
            'sClass': 'center',
            "sTitle": "IP地址"
        },
        {
            "mDataProp": "op_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "content",
            'sClass': 'center',
            "sTitle": "内容"
        }
    ];
    var data = {
        user: $("#user_select").val(),
        start_time: $("#start_date").val(),
        end_time: $("#end_date").val()
    };
    dataTablePage($("#datatable_log"), aoColumns, ajax_url, data, false, null);
};


var $query_log = $("#query_log");

$query_log.on("click", function (e) {
    e.preventDefault();
    query_log();
});

$query_log.click();






