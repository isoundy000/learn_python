
get_left_game_server();
setLeftStyle();

var $game_operate_record_table = $('#game_operate_record_table');
var $detail_record_modal = $('#detail_record_modal');
var $btn_all_retry = $('#btn_all_retry');
var $abnormal_record_table = $('#abnormal_record_table');
var $success_record_table = $('#success_record_table');
var $retry_record_table = $('#retry_record_table');
var $abnormal_record = $('#abnormal_record');
var $success_record = $('#success_record');
var $retry_record = $('#retry_record');
var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $retry_refresh_time = $('#retry_refresh_time');


var all_table_data;
var detail_table_data;


    // 任务记录
var row_running_tag;
var get_operate_game_record = function () {
    "use strict";
    var ajax_data = {
        "url": "/new_server/result",
        "type": "POST",
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'success'){
                return result['data'];
            }else{
                return [];
            }

        }
    };
    var columns = [{"title": "序号",'data':'id'}, {"title": "操作人",'data':'username'},{"title":"操作时间",'data':'otime'},
        {"title":"操作类型",'data':'opt'}, {"title":"操作服务",'data':'method'},
        {"title":"总数",'data':'total'}, {"title":"成功",'data':'success'},
        {"title":"执行",'data':'running'}, {"title":"失败",'data':'fail'}, {"title":"状态",'data':'success'}, {"title":"重试次数",'data':'retry_num'}, {"title":"操作"}];
    var columnDefs = [
        {
            "targets": 3,
            "render": function (data) {
                if (data === 1){
                    data = '<span class="badge" style="background-color: #44b6ae">启动</span>';
                }else if(data === 2){
                    data = '<span class="badge badge-danger">关闭</span>';
                }else if (data === 3){
                    data = '<span class="badge badge-primary">重启</span>';
                }else{
                    data = '<span class="badge badge-warning">异常</span>';
                }
               return data;
            }
        },
        {
            "targets": 4,
            "render": function (data) {
                if(data === 2){
                    data = '路由';
                }else if (data === 3){
                    data = '游戏';
                }else if (data === 4){
                    data = '扩展';
                }else if (data === 5){
                    data = '游戏、路由、扩展';
                } else{
                    data = '异常';
                }
               return data;
            }
        },
        {
            "targets": -4,
            "render": function (data) {
                if (data > 0){
                    return '<span class="badge badge-danger">'+data+'</span>';
                }else{
                    return data;
                }

            }
        },
        {
            "targets": -3,
            "render": function (data,type,row) {
                var r_str = '';
                if (data === row['total']){
                    r_str = '<span class="badge badge-success">成功</span>';
                }else{
                    r_str = '<span class="badge badge-warning">异常</span>';
                }
                if (row['retry_num']>0){
                    r_str += '<span class="badge badge-danger">'+row['retry_num']+'</span>';
                }
                return r_str;

            }
        },
        {
            "targets": -2,
            "visible": false
        },
        {
            "targets": -1,
            "render": function (data,type,row) {
                if (row['running']>0 || row['fail']>0){
                    return '<button type="button" class="btn btn-danger btn-sm" onclick="show_detail_modal('+row['id']+','+row['running']+',\'error\',this)">错误处理</button>&nbsp&nbsp' +
                        '<button type="button"  onclick="refresh_single_row(this)">刷新</button>';
                }else{
                    return '<button type="button" class="btn-primary" onclick="show_detail_modal('+row['id']+','+row['running']+', \'success\')">详情</button>';
                }

            }
        }
    ];
    all_table_data = back_page_table($game_operate_record_table, ajax_data, columns,columnDefs,false);
};

get_operate_game_record();

var refresh_single_row = function (this_div) {
    "use strict";
     var row_div = $(this_div).closest('tr');
    var row_data = all_table_data.row( row_div ).data();
    $.ajax({
        url: '/new_server/refresh',
        data: {'cid': row_data['id']},
        type: 'post',
        dataType: 'json',
        success: function (result) {
            all_table_data.row(row_div).data(result);
        }
    });
};
var refresh_detail_record = function () {
    "use strict";

    detail_table_data.ajax.reload(null, false);

    // get_detail_record(cid, detail_type);
};
var all_logid_list = [];
var detail_row_div;
var reccord_modal_cid;

var get_detail_record = function (cid, record_type) {
    "use strict";
    $btn_all_retry.hide();

    var ajax_data = {
        "url": "/new_server/details",
        "type": "GET",
        "data": {cid: cid, details_type: record_type},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            all_logid_list = [];
            var fail_num = 0;
            var running_num = 0;
            for (var i=0;i<result.length;i++){
                all_logid_list.push(result[i]['id']);
                if (result[i]['status'] === 3){
                    fail_num ++;
                }else if (result[i]['status'] === 1){
                    running_num ++;
                }
            }
            if (retry_tag && running_num === 0){
                window.clearInterval(retry_refresh_time_obj);
                window.clearInterval(retry_refresh_time_1_obj);
                retry_refresh_time_status = false;
                $retry_refresh_time.hide();
                // retry_tag = false;
            }
            if (fail_num > 0){
                $btn_all_retry.html('<button type="button" class="btn btn-primary  btn-sm retry_operate" ' +
                    'onclick="refresh_detail_record()">刷新</button> <button id="open_add" style="margin-left: 20px" type="button" \
                    class="btn btn-success btn-sm retry_operate"' +'onclick="retry_game_operate(\'all\',\'\')"> 重试所有失败 <i class="fa fa-wrench"></i> </button>');
                $btn_all_retry.show();
            }else{
                $btn_all_retry.html('<button type="button" class="btn btn-primary  btn-sm" ' +
                    'onclick="refresh_detail_record()">刷新</button>');
                $btn_all_retry.show();
            }
            return result;

        }
    };
    var columns = [{"title": "IP",'data':'ip'}, {"title": "区服",'data':'gid'}, {"title":"操作时间",'data':'otime'}
        ,{"title":"操作类型",'data':'opt'},{"title":"状态",'data':'status'},{"title":"错误信息",'data':'err_info'},{"title":"操作",'data':'status'}];
    var columnDefs = [
        {
            "targets": 3,
            "render": function (data) {
               if (data === 1){
                    data = '启动';
                }else if(data === 2){
                    data = '关闭';
                }else if (data === 3){
                    data = '重启';
                }else{
                    data = '异常';
                }
               return '<span class="badge badge-primary">'+data+'</span>';
            }
        },
        {
            "targets": 4,
            "render": function (data) {
                if (data === 1){
                    data = '执行中';
                    return '<span class="badge badge-info">'+data+'</span>';
                }else if(data === 2){
                    data = '成功';
                    return '<span class="badge badge-success">'+data+'</span>';
                }else if (data === 3){
                    data = '失败';
                    return '<span class="badge badge-danger">'+data+'</span>';
                }else{
                    data = '异常';
                    return '<span class="badge badge-warning">'+data+'</span>';
                }

            }
        },
        {
            "targets": -4,
            "render": function (data) {
               return '<span class="badge badge-info">'+data+'</span>';
            }
        },
        {
            "targets": -1,
            "render": function (data, type, row) {
                if (data === 3){
                    return '<div class="btn-group"><button class="badge green retry_operate" ' +
                   'onclick="retry_game_operate(\'single\','+row['id']+')">重试<i class="fa fa-wrench"></i></button></div>';
                }else{
                    return '';
                }

            }
        }
    ];
    var record_table_obj;
    if (record_type === 'success'){
        columnDefs.push({
            "targets": [-1, -2],
            "visible": false
        });
        record_table_obj = $success_record_table;
    }else if (record_type === 'retry'){
        columnDefs.push({
            "targets": [-1],
            "visible": false
        });
        record_table_obj = $retry_record_table;
    }else{
        record_table_obj = $abnormal_record_table;
    }
    detail_table_data = new_front_page_table(record_table_obj, ajax_data, columns,columnDefs,false);
};

var show_detail_modal = function (cid, running_num, detail_type, this_div) {
    "use strict";
    detail_row_div  = this_div;
    reccord_modal_cid = cid;
    $detail_record_modal.modal('show');
    if (detail_type === 'success'){
        $success_record.click();
        $abnormal_record.hide();
        row_running_tag = false;
    }else{
        $abnormal_record.show();
        $abnormal_record.click();
        row_running_tag = running_num>0;
    }

};

$abnormal_record.click(function () {
    get_detail_record(reccord_modal_cid, 'error');
});
$success_record.click(function () {
    get_detail_record(reccord_modal_cid, 'success');
});
$retry_record.click(function () {
    get_detail_record(reccord_modal_cid, 'retry');

});

var set_refresh_time = function () {
    if (refresh_time === 1){
        refresh_time = 5;
    }else{
        refresh_time --;
    }
    $retry_refresh_time.html(refresh_time + '秒后，刷新状态');
};
var retry_tag = false;
var retry_refresh_time_obj;
var retry_refresh_time_1_obj;
var retry_refresh_time_status = false;
var refresh_time = 5;
var retry_game_operate = function (r_type, r_cid) {
    "use strict";
    $('.retry_operate').attr('disabled', 'disabled');
    retry_tag = true;
    var logid_list;
    if (r_type === 'all'){
        logid_list = all_logid_list;
    }else{
        logid_list = [r_cid];
    }

    $.ajax({
        url: '/new_server/control',
        type: 'post',
        dataType: 'json',
        data: JSON.stringify({log_list: logid_list}),
        contentType: 'application/json; charset=UTF-8',
        success: function (result) {
            if (result['status'] === 'success'){
                if (!retry_refresh_time_status){
                    retry_refresh_time_obj = window.setInterval(refresh_detail_record,5000);
                    $retry_refresh_time.html('5秒后，刷新状态');
                    $retry_refresh_time.show();
                    retry_refresh_time_1_obj = window.setInterval(set_refresh_time,1000);
                    retry_refresh_time_status = true;
                }
                detail_table_data.ajax.reload(null, false);
            }else{
                alert('执行失败');
            }

        },
        error: function () {
            alert('执行失败');
        }
    });
};

$detail_record_modal.on('hide.bs.modal', function () {
    "use strict";
  if (row_running_tag || retry_tag){
      refresh_single_row(detail_row_div);
  }
  if (retry_tag){
      window.clearInterval(retry_refresh_time_obj);
      window.clearInterval(retry_refresh_time_1_obj);
      retry_refresh_time_status = false;
      $retry_refresh_time.hide();
      retry_tag = false;

  }

});

