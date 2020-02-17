/**
 * Created by wangrui on 17/6/13.
 */
get_left_game_server();
handleDatePickers2();
handleTimePickers();
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));
var $select_server = $("#select_server");


var getGameServerData = function(div_select, tag){
    if (GAME_SERVER_DICT == null){
        var success = function(data){
            GAME_SERVER_DICT = data;
        };
        my_ajax(true, '/server/getgameserver', 'get', {}, false, success);
    }
    var str_html = "";
    if (tag == 2) {
        str_html += "<option value='0'>登录</option>";

    }
    for (var i in GAME_SERVER_DICT) {
        str_html += '<option value="' + i + '">' + i + "区:" + GAME_SERVER_DICT[i]["name"] + '</option>';
    }
    div_select.html(str_html);
};

getGameServerData($select_server, 2);


function add0(m){return m<10?'0'+m:m }
function format(timestamp)
{
  //timestamp是整数，否则要parseInt转换,不会出现少个0的情况
        var time = new Date(timestamp * 1000);
        var year = time.getFullYear();
        var month = time.getMonth()+1;
        var date = time.getDate();
        var hours = time.getHours();
        var minutes = time.getMinutes();
        var seconds = time.getSeconds();
        return year+'-'+add0(month)+'-'+add0(date)+' '+add0(hours)+':'+add0(minutes)+':'+add0(seconds);
}

function query_client_error(){
    var server_id = $select_server.val();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var role_id = $("#role_id").val();
    var ajax_source = "/sensor/query";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "created_time",
            "sClass": "center",
            "sTitle": "时间"
        },
        {
            "mDataProp": "channel",
            "sClass": "center",
            "sTitle": "渠道"
        },
        {
            "mDataProp": "uid",
            "sClass": "center",
            "sTitle": "账号ID"
        },
        {
            "mDataProp": "server",
            "sClass": "center",
            "sTitle": "区服"
        },
        {
            "mDataProp": "rid",
            "sClass": "center",
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "platform",
            "sClass": "center",
            "sTitle": "平台"
        },
        {
            "mDataProp": "type",
            "sClass": "center",
            "sTitle": "类型"
        },
        {
            "mDataProp": "msg",
            "sClass": "center",
            "sTitle": "错误信息"
        },
        {
            "mDataProp": "device_id",
            "sClass": "center",
            "sTitle": "设备编号"
        },
        {
            "mDataProp": "device_model",
            "sClass": "center",
            "sTitle": "设备类型"
        },
        {
            "mDataProp": "cpu",
            "sClass": "center",
            "sTitle": "CPU"
        },
        {
            "mDataProp": "memory",
            "sClass": "center",
            "sTitle": "内存"
        },
        {
            "mDataProp": "sys_version",
            "sClass": "center",
            "sTitle": "系统版本"
        },
        {
            "mDataProp": "mobile",
            "sClass": "center",
            "sTitle": "手机号"
        },
        {
            "mDataProp": "ip",
            "sClass": "center",
            "sTitle": "IP地址"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var created_time = format(aData.created_time);
        $('td:eq(0)', nRow).html(created_time);
        return nRow;
    };
    var data = {
        server_id: server_id, start_date: start_date, end_date: end_date, role_id: role_id
    };
    dataTablePage($("#client_error_table"), aoColumns, ajax_source, data, false, fnRowCallback);
}


$("#btn_query").on("click", function (e) {
    e.preventDefault();
    query_client_error();
});
