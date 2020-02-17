/**
 * Created by wangrui on 15/6/1.
 */
get_left_game_server();
handleDatePickers();
$("#acc_date").val(getNowFormatDate(1));

$("#btn_acc").on("click", function(e){
    e.preventDefault();
    var ajax_source = "/queryacclog";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "函数名称"
        },
        {
            "mDataProp": "min",
            "sClass": "center",
            "sTitle": "最小回调时间(秒)"
        },
        {
            "mDataProp": "max",
            "sClass": "center",
            "sTitle": "最大回调时间(秒)"
        },
        {
            "mDataProp": "pro",
            'sClass': 'center',
            "sTitle": "回调次数所占比例 %"
        },
        {
            "mDataProp": "num",
            "sTitle": "回调次数",
            "sClass": "center"
        },
        {
            "mDataProp": "ave",
            "sTitle": "平均回调时间(秒)",
            "sClass": "center"
        },
        {
            "mDataProp": "acount",
            "sTitle": "错误次数",
            "sClass": "center"
        }
    ];
    var acc_date = $("#acc_date").val();
    var data = {
            q_date: acc_date
    };
    dataTablePage($("#table_acc_log"), aoColumns, ajax_source, data, true, null);
});

$("#btn_acc").click();