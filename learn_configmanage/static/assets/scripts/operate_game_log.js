
get_left_game_server();
setLeftStyle();

var $game_operate_record_table = $('#game_operate_record_table');
var $detail_record_modal = $('#detail_record_modal');
var $btn_all_retry = $('#btn_all_retry');
var $detail_record_table = $('#detail_record_table');
var $start_date = $('#start_date');
var $end_date = $('#end_date');


var all_table_data;
var detail_table_data;


    // 任务记录
var get_operate_game_record = function () {
    var ajax_data = {
        "url": "/setgame/query",
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
        {"title":"区服区间",'data':'info'}, {"title":"操作类型",'data':'opt'}, {"title":"操作服务",'data':'method'},
        {"title":"总数",'data':'total'}, {"title":"成功",'data':'success'},
        {"title":"执行",'data':'running'}, {"title":"失败",'data':'fail'}, {"title":"状态",'data':'success'},
        {"title":"操作", 'data': 'fail'}];
    var columnDefs = [
        {
            "targets": 4,
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
            "targets": 5,
            "render": function (data) {
                if (data === 1){
                    data = '游戏';
                }else if(data === 2){
                    data = '路由';
                }else if (data === 3){
                    data = '游戏';
                }else if (data === 4){
                    data = '扩展';
                }else if (data === 5){
                    data = '游戏、扩展';
                }else if (data === 6){
                    data = '路由、游戏、扩展';
                }else{
                    data = '异常';
                }
               return data;
            }
        },
        {
            "targets": -3,
            "render": function (data) {
                if (data > 0){
                    return '<span class="badge badge-danger">'+data+'</span>';
                }else{
                    return data;
                }

            }
        },
        {
            "targets": -2,
            "render": function (data,type,row) {
                if (data === row['total']){
                    return '<span class="badge badge-success">成功</span>';
                }else{
                    return '<span class="badge badge-warning">异常</span>';
                }

            }
        },
        {
            "targets": -1,
            "render": function (data,type,row) {
                if (data > 0 || row['running']>0){
                    return '<button type="button" class="btn-danger margin-right-10" onclick="show_detail_modal('+row['id']+',1)">错误处理</button>' +
                        '<button type="button" class="btn-primary" onclick="refresh_single_row(this)">刷新</button>';
                }else{
                    return '<button type="button" class="btn-primary" onclick="show_detail_modal('+row['id']+',2)">详情</button>';
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
        url: '/setgame/get',
        data: {'cid': row_data['id']},
        type: 'post',
        dataType: 'json',
        success: function (result) {
            all_table_data.row(row_div).data(result);
        }
    });
};
var retry_data = {'all_server': [], 'cid': '', 'method': '', 'tag': '', 'logid_list': []};
var get_detail_record = function (cid, tag) {
    $btn_all_retry.hide();
    retry_data['all_server'] = [];
    retry_data['logid_list'] = [];
    var ajax_data = {
        "url": "/setgame/details",
        "type": "GET",
        "data": {cid: cid, t_type: tag},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result.length > 0){
                $btn_all_retry.show();
            }
            for (var i=0;i<result.length;i++){
                if (i === 0){
                    retry_data['cid'] = result[i]['cid'];
                    retry_data['method'] = result[i]['method'];
                    retry_data['tag'] = result[i]['opt'];
                }
                retry_data['all_server'].push(result[i]['gid']);
                retry_data['logid_list'].push(result[i]['id']);
            }

            return result;

        }
    };
    var columns = [{"title": "IP",'data':'ip'}, {"title": "区服",'data':'gid'}, {"title":"操作时间",'data':'otime'}
        ,{"title":"操作类型",'data':'opt'},{"title":"状态",'data':'status'}, {"title":"重试次数",'data':'retry_num'},
        {"title":"错误信息",'data':'err_info'}, {"title":"操作", 'data': 'gid'}];
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
            "targets": -3,
            "render": function (data) {
               return '<span class="badge badge-info">'+data+'</span>';
            }
        },
        {
            "targets": -1,
            "render": function (data,type,row) {
               return '<div class="btn-group"><a class="badge green" ' +
                   'onclick="retry_game_operate('+data+','+row['id']+')">重试<i class="fa fa-wrench"></i></a></div>';
            }
        }
    ];
    if (tag !== 1){
        columnDefs.push({
            "targets": [-1, -2],
            "visible": false
        });
    }
    detail_table_data = new_front_page_table($detail_record_table, ajax_data, columns,columnDefs,false);
};


$detail_record_modal.on('hide.bs.modal', function () {
  all_table_data.ajax.reload(null, false);
});

var show_detail_modal = function (cid,tag) {
    $detail_record_modal.modal('show');
    get_detail_record(cid,tag);


};


var retry_game_operate = function (r_server, r_cid) {
    var send_data;
    var error_fun = function () {
        $detail_record_modal.modal('hide');
    };
    if (r_server === 'all'){
        send_data = {
            server_list: JSON.stringify(retry_data['all_server']),
            tag: retry_data['tag'],
            method: retry_data['method'],
            cid: retry_data['cid'],
            logid_list: JSON.stringify(retry_data['logid_list'])
        };
        my_ajax(true, "/server/setallgameservice", "get", send_data, false, function () {

        }, error_fun);
    }else{
        send_data = {
            server_list: JSON.stringify([r_server]),
            tag: retry_data['tag'],
            method: retry_data['method'],
            cid: retry_data['cid'],
            logid_list: JSON.stringify([r_cid])
        };
        my_ajax(true, "/server/setallgameservice", "get", send_data, false, function () {

        }, error_fun);
    }

    detail_table_data.ajax.reload(null, false);
};
