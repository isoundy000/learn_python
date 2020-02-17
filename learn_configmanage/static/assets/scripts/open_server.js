/**
 * Created by admin on 2018/4/9.
 */

var $server_list_table = $('#server_list_table');
var $hand_open_server_id = $('#hand_open_server_id');
var $hand_open_server_time = $('#hand_open_server_time');
var $btn_confirm_open_server = $('#btn_confirm_open_server');
var $open_server_modal = $('#open_server_modal');


var server_table_obj;
var get_server_list = function () {
    "use strict";
    var ajax_data = {
        "url": "/openserver/hand/open_info",
        "type": "get",
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#server_list_table_processing').hide();
        },
        "dataSrc": function (result) {
            return result;
        }
    };
    var columns = [{"title": "序号",'data':'id'}, {"title":"区服编号",'data':'gameid'}
        ,{"title":"区服名称",'data':'name'},
        {"title":"操作"}];
    var columnDefs = [
        {
            "visible": false,
            "targets": 0
        },
        {
            "targets": -1,
            "render": function () {
                return '<button type="button" class="btn btn-primary btn-sm" onclick="open_server_confirm(this)">开服</button>';

            }
        }
    ];
   server_table_obj = new_front_page_table($server_list_table, ajax_data, columns,columnDefs,false);
};

var click_game_id;
var click_open_time;
var open_server_confirm = function (this_div) {
    "use strict";
    var row_div = $(this_div).closest('tr');
    var row_data = server_table_obj.row( row_div ).data();

    $hand_open_server_id.html(row_data['gameid'] + '区:' + row_data['name']);

    var now_date = new Date();
    var now_date_str = now_date.getFullYear() +'-'+
    ((now_date.getMonth()+1)<10?"0"+(now_date.getMonth()+1):(now_date.getMonth()+1))+'-' +
     (now_date.getDate()<10?"0"+now_date.getDate():now_date.getDate()) + ' ' +
        (now_date.getHours()<10?"0"+now_date.getHours():now_date.getHours())  + ':' +
        (now_date.getMinutes()<10?"0"+now_date.getMinutes():now_date.getMinutes()) + ':00';

    click_game_id = row_data['gameid'];
    click_open_time = now_date_str;

    $hand_open_server_time.html(now_date_str);
    $open_server_modal.modal('show');
};

get_server_list();

var $error_modal = $("#error_modal");
$btn_confirm_open_server.click(function () {
    "use strict";
    $btn_confirm_open_server.attr('disabled', 'disabled');
    $btn_confirm_open_server.text('操作执行中');
    $.ajax({
        url: '/openserver/hand/operate',
        type: 'get',
        data: {'game_id': click_game_id, 'open_time': click_open_time},
        success: function (result) {
            $open_server_modal.modal('hide');
            if (result['status'] === 'success'){
                Common.alert_message($error_modal, 1, "操作成功");
            }else if (result['status'] === 'warning'){
                Common.alert_message($error_modal, 0, "操作失败，区服状态异常");
            }else{
                Common.alert_message($error_modal, 0, "操作失败");
            }
            server_table_obj.ajax.reload( null, false );
        },
        error: function () {
            $open_server_modal.modal('hide');
            Common.alert_message($error_modal, 0, "操作失败");
        }
    });

});


$open_server_modal.on('show.bs.modal', function () {
    "use strict";
    $btn_confirm_open_server.text('确认开服');
    $btn_confirm_open_server.removeAttr('disabled');

});