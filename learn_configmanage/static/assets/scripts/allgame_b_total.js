/**
 * Created by admin on 2018/4/9.
 */
/**
 * Created by wangrui on 15/5/11.
 */

get_left_game_server();

var $total_server_num = $('#total_server_num');
var $total_running_num = $('#total_running_num');
var $total_closed_num = $('#total_closed_num');
var $total_server_online_num = $('#total_server_online_num');
var $total_running_online_num = $('#total_running_online_num');
var $total_closed_online_num = $('#total_closed_online_num');
var $total_online_num = $('#total_online_num');
var $total_machine_num = $('#total_machine_num');
var $total_client_error_num = $('#total_client_error_num');
var $total_python_error_num = $('#total_python_error_num');
var $btn_operate_game = $('#btn_operate_game');

var $server_filter_condition = $('#server_filter_condition');

var $btn_control_filter_display = $('#btn_control_filter_display');
var $server_list_table = $('#server_list_table');

var $filter_time_range = $('#filter_time_range');
var $filter_partition = $('#filter_partition');
var $filter_out_ip = $('#filter_out_ip');
var $filter_inner_ip = $('#filter_inner_ip');
var $single_filter_value = $('#single_filter_value');
var $single_filter_type = $('#single_filter_type');
var $filter_server_range = $('#filter_server_range');
var $filter_server_id = $('#filter_server_id');
var $filter_server_status = $('#filter_server_status');
var $filter_game_status = $('#filter_game_status');

var $multiple_filter_clear = $('#multiple_filter_clear');
var $multiple_filter_search = $('#multiple_filter_search');
var $single_filter_search = $('#single_filter_search');

var $error_modal_title = $('#error_modal_title');
var $server_error_modal = $('#server_error_modal');
var $server_error_table = $('#server_error_table');

var $multi_select_obj = $('#filter_out_ip, #filter_inner_ip, #filter_partition, #filter_server_status, #filter_game_status');

var replace_total_color = function (d_value, div_obj) {
    "use strict";
    if (d_value>0){
        div_obj.parent().parent().attr('class', 'dashboard-stat red');
    }else{
        div_obj.parent().parent().attr('class', 'dashboard-stat green');
    }
};
var get_total_data = function () {
    "use strict";
    $.ajax({
        url: '/new_server/total',
        type: 'get',
        dataType: 'json',
        success: function (result) {
            $total_server_num.text(result['total']);
            $total_server_online_num.text(result['online_total']);
            $total_running_num.text(result['running']);
            $total_running_online_num.text(result['online_running']);
            $total_closed_num.text(result['closed']);
            $total_closed_online_num.text(result['online_closed']);
            replace_total_color(result['online_closed'], $total_closed_online_num);
            $total_online_num.text(result['online']);

            $total_machine_num.text(result['physical']);
            replace_total_color(result['client_error'], $total_client_error_num);
            $total_client_error_num.text(result['client_error']);
            replace_total_color(result['python_error'], $total_python_error_num);
            $total_python_error_num.text(result['python_error']);
        }
    });
};

// 初始化
get_total_data();
var format_time_range_input = function (e_object) {
    "use strict";
    e_object.daterangepicker({
        "opens": "center",
        "drops": "down",
        "autoUpdateInput": false,
        "locale": {'format': 'YYYY/MM/DD', cancelLabel: 'Clear'},
        "alwaysShowCalendars": true
    });
    e_object.on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY/MM/DD') + ' - ' + picker.endDate.format('YYYY/MM/DD'));
    });
    e_object.on('cancel.daterangepicker', function() {
        $(this).val('');
    });

};
var init_multi_select = function (multi_select_obj) {
    "use strict";
    multi_select_obj.multiselect({
        numberDisplayed: 10,
        includeSelectAllOption: true,
        selectAllText: '选择全部',
        enableFiltering: true,
        nonSelectedText: "==请选择==",
        buttonWidth: '100%',
        maxHeight: 250
    });
};

init_multi_select($multi_select_obj);
format_time_range_input($filter_time_range);

var multi_select = ['filter_out_ip', 'filter_inner_ip', 'filter_partition', 'filter_server_status', 'filter_game_status'];
//获取分区信息
$.ajax({
   url: '/server/get_partition',
    type:'get',
    dataType: 'json',
    success: function (result) {
       var partition_data = [];
       for (var i=0;i<result.length;i++){
           partition_data.push({"label":result[i]["name"],"value":result[i]["id"]});
       }
       $filter_partition.multiselect('dataprovider',partition_data);
    },
    error: function () {
    }
});
//获取IP信息
$.ajax({
   url: '/new_server/ip',
    type:'get',
    dataType: 'json',
    data: {ip_type: 'all'},
    success: function (result) {
       var out_ip_data = [];
       var inner_ip_data = [];
       for (var i=0;i<result.length;i++){
           out_ip_data.push({"label":result[i]["extranet_ip"],"value":result[i]["extranet_ip"]});
           inner_ip_data.push({"label":result[i]["ip"],"value":result[i]["ip"]});
       }
       $filter_out_ip.multiselect('dataprovider',out_ip_data);
        $filter_inner_ip.multiselect('dataprovider',inner_ip_data);

        var replace_html = $filter_server_id.prop('outerHTML');
        replace_html = replace_html.replace($single_filter_type.val(), 'single_search_value');
        $single_filter_value.html(replace_html);
        // $single_filter_search.click();
    },
    error: function () {
       "use strict";
        var replace_html = $filter_server_id.prop('outerHTML');
        replace_html = replace_html.replace($single_filter_type.val(), 'single_search_value');
        $single_filter_value.html(replace_html);
        // $single_filter_search.click();
    }
});

$single_filter_type.change(function () {
    "use strict";
    var e_value = $(this).val();

    var replace_html = e_value === 'filter_server_range' ? eval('$' + e_value).html() : eval('$' + e_value).prop('outerHTML');


    $single_filter_value.html(replace_html.replace(e_value, 'single_search_value'));
    if (e_value === 'filter_time_range'){
        format_time_range_input($('#single_search_value'));
    }else if ($.inArray(e_value, multi_select)>=0){
        init_multi_select($('#single_search_value'));
    }


});

var operate_game_data = [];
var total_click_search = function (o_type) {
    "use strict";
    var send_data =   {
        "extranet_ip": [],
        "ip": [],
        "gameid": '',
        "server_range": {
            "start": '',
            "end": ''
        },
        "section": [],
        "open_time": {
            "start": '',
            "end": ''
        },
        "status": [],
        "running": 0,
        "closed": 0,
        "client_error":0,
        "python_error": 0
    };
    send_data[o_type] = 1;
    send_data['status'] = ["online"];
    operate_game_data = send_data;
    get_server_list(send_data);

};


$multiple_filter_clear.click(function () {
    'use strict';
    $filter_server_id.val('');
    $filter_server_range.find("input[name=from]").val('');
    $filter_server_range.find('input[name=to]').val('');
    $filter_game_status.val('0');
    $filter_time_range.val('');
    $multi_select_obj.multiselect('clearSelection');
    $multi_select_obj.multiselect('refresh');
});

$btn_control_filter_display.click(function () {
    "use strict";
    var select_type = $single_filter_type.val();
    var o_single_search_value = $('#single_search_value');
    if ($(this).hasClass("filter_show")) {
        $(this).removeClass("filter_show").addClass("filter_hide");
        $server_filter_condition.slideUp(200);
        $single_filter_type.removeAttr('disabled');
        $single_filter_search.removeAttr('disabled');
        if ($.inArray(select_type, multi_select)>=0){
            o_single_search_value.multiselect('enable');
        }else if(select_type === 'filter_server_range'){
            $single_filter_value.find("input[name=from]").removeAttr('disabled');
            $single_filter_value.find('input[name=to]').removeAttr('disabled');
        }else{
            o_single_search_value.removeAttr('disabled');
        }
        $multiple_filter_clear.click();

    } else {
        $(this).removeClass("filter_hide").addClass("filter_show");
        $server_filter_condition.slideDown(200);
        $single_filter_type.attr('disabled', 'disabled');
        $single_filter_search.attr('disabled', 'disabled');

        if ($.inArray(select_type, multi_select)>=0){
            o_single_search_value.multiselect('disable');
        }else if (select_type === 'filter_server_range'){
            $single_filter_value.find("input[name=from]").attr('disabled', 'disabled');
            $single_filter_value.find('input[name=to]').attr('disabled', 'disabled');
        } else{
            o_single_search_value.attr('disabled', 'disabled');
        }
    }
});

var get_single_mult_value = function (c_type, t_div) {
    "use strict";
    var return_data;
    if ($single_filter_type.val() === c_type && t_div.val() !== null){
        return_data = t_div.val();
    }else{
        return_data = [];
    }
    return return_data;
};


$single_filter_search.click(function () {
    "use strict";
    var filter_type = $single_filter_type.val();
    var $single_search_value = $('#single_search_value');
    var server_start='';
    var server_end='';
    if (filter_type === 'filter_server_range'){
        server_start = $single_filter_value.find("input[name='from']").val();
        server_end = $single_filter_value.find("input[name='to']").val();
    }

    var time_start = '';
    var time_end = '';
    var running = 0;
    var closed = 0;
    var client_error = 0;
    var python_error =0;
    if (filter_type === 'filter_time_range'){
        var time_value = $single_search_value.val();
        time_value = time_value.split('-');
        time_start = $.trim(time_value[0].replace(/\//g, '-'));
        time_end = $.trim(time_value[1].replace(/\//g, '-'));
    }else if (filter_type === 'filter_game_status'){
        var game_status = $single_search_value.val();
        for (var i=0;i<game_status.length;i++){
            if (game_status[i] === 'running'){
                running=1;
            }else if(game_status[i] === 'closed'){
                closed=1;
            }else if(game_status[i] === 'client_error'){
                client_error=1;
            }else if(game_status[i] === 'python_error'){
                python_error=1;
            }
        }
    }
    var send_data = {
        "extranet_ip": get_single_mult_value('filter_out_ip', $single_search_value),
        "ip": get_single_mult_value('filter_inner_ip', $single_search_value),
        "gameid": filter_type === 'filter_server_id' ? $single_search_value.val() : '',
        "server_range": {
            "start": server_start,
            "end": server_end
        },
        "section": get_single_mult_value('filter_partition', $single_search_value),
        "open_time": {
            "start": time_start,
            "end": time_end
        },
        "status": get_single_mult_value('filter_server_status', $single_search_value),
        "running": running,
        "closed": closed,
        "client_error":client_error,
        "python_error": python_error
    };
    get_server_list(send_data);
});

$multiple_filter_search.click(function () {
    var extranet_ip = $filter_out_ip.val() === null ? [] : $filter_out_ip.val();
    var ip = $filter_inner_ip.val() === null ? [] : $filter_inner_ip.val();
    var section = $filter_partition.val() === null ? [] : $filter_partition.val();
    var game_status = $filter_game_status.val() === null ? [] : $filter_game_status.val();
    var running =0;
    var closed =0;
    var client_error =0;
    var python_error =0;
    for (var i=0;i<game_status.length;i++){
        if (game_status[i] === 'running'){
            running=1;
        }else if(game_status[i] === 'closed'){
            closed=1;
        }else if(game_status[i] === 'client_error'){
            client_error=1;
        }else if(game_status[i] === 'python_error'){
            python_error=1;
        }

    }

    var time_start = '';
    var time_end = '';
    var time_value = $filter_time_range.val();
    if (time_value.length>0){
        time_value = time_value.split('-');
        time_start = $.trim(time_value[0].replace(/\//g, '-'));
        time_end = $.trim(time_value[1].replace(/\//g, '-'));
    }
    var send_data =   {
        "extranet_ip": extranet_ip,
        "ip": ip,
        "gameid": $filter_server_id.val(),
        "server_range": {
            "start": $filter_server_range.find("input[name=from]").val(),
            "end": $filter_server_range.find("input[name=to]").val()
        },
        "section": section,
        "open_time": {
            "start": time_start,
            "end": time_end
        },
        "status": $filter_server_status.val() === null ? [] : $filter_server_status.val(),
        "running": running,
        "closed": closed,
        "client_error":client_error,
        "python_error": python_error
    };
    get_server_list(send_data);

});


var add0 = function (m){return m<10?'0'+m:m };
var format = function (timestamp)
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
};
var server_error_table_div;
var query_error = function (game_id, error_type) {
    "use strict";
    var columns;
    var columnDefs;
    if (error_type === 'python_error'){
        $error_modal_title.html(game_id + '区，后端错误');
        columns = [{"title":"时间",'data':'otime'}, {"title":"错误类型",'data':'tag'}
        ,{"title":"错误信息",'data':'message'}];
        columnDefs = [];
    }else if (error_type === 'client_error'){
        $error_modal_title.html(game_id + '区，前端错误');
        columns = [{"title":"时间",'data':'created_time'}, {"title":"渠道",'data':'channel'}, {"title":"账号ID",'data':'uid'}
        , {"title":"角色编号",'data':'rid'}, {"title":"类型",'data':'type'}, {"title":"错误信息",'data':'msg'}
        , {"title":"设备编号",'data':'device_id'}, {"title":"设备类型",'data':'device_model'}, {"title":"CPU",'data':'cpu'}
        , {"title":"内存",'data':'memory'}, {"title":"系统版本",'data':'sys_version'}, {"title":"手机号",'data':'mobile'}
        ,{"title":"ip地址",'data':'ip'}];
        columnDefs = [{
            "targets": 0,
            "render": function (data) {
                return  format(data);
            }
        }];
    }

    $server_error_modal.modal('show');
    var send_data = {
        server_id: game_id,
        error_type: error_type
    };
    var ajax_data = {
        "url": "/new_server/error",
        "type": "post",
        "dataType": 'json',
        "data": function ( d ) {
            return JSON.stringify( $.extend(d, send_data));
          },
        contentType: 'application/json; charset=UTF-8',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#server_error_table_processing').hide();
        },
        "dataSrc": function (result) {
            $btn_operate_game.show();
            if (result['status'] === 'success'){
                return result.data;
            }else{
                 result.recordsTotal = 0;
                 result.recordsFiltered = 0;
                return [];
            }
        }
    };


   server_error_table_div = back_page_table($server_error_table, ajax_data, columns,columnDefs,false);
};

$server_error_modal.on('hide.bs.modal', function () {
    "use strict";
  server_error_table_div.destroy();
  $server_error_table.html('');
});

var get_server_list = function (data) {
    "use strict";
    operate_game_data = data;
    var ajax_data = {
        "url": "/new_server/search",
        "type": "POST",
        "dataType": 'json',
        "data": function ( d ) {
            return JSON.stringify( $.extend(d, data));
          },
        contentType: 'application/json; charset=UTF-8',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            $btn_operate_game.show();
            if (result['status'] === 'success'){
                return result.data;
            }else{
                 result.recordsTotal = 0;
                 result.recordsFiltered = 0;
                return [];
            }
        }
    };
    var columns = [{"title": "区服ID",'data':'gameid'}, {"title":"区服名称",'data':'name'}
        ,{"title":"开服时间",'data':'createtime'},{"title":"区服状态",'data':'status'}, {"title":"分区",'data':'section'},
        {"title":"总人数",'data':'total'}, {"title":"在线人数",'data':'online'}, {"title":"启动模式",'data':'mode'},
        {"title":"前端错误", 'data': 'client_error'}, {"title":"后端错误", 'data': 'python_error'},
        {"title":"内网IP",'data':'ip'}, {"title":"外网IP", 'data': 'extranet_ip'},  {"title":"路由状态", 'data': 'gates'},
        {"title":"游戏状态", 'data': 'game'},
        {"title":"扩展状态", 'data': 'ext'},
        {"title":"运行状态",'data':'g_status'}, {"title":"跳转",'data':'gameid'}];
    var columnDefs = [
        {
            "visible": false,
            "targets": 0
        },
        {
            "targets": 1,
            "render": function (data, type, row) {
                return  row['gameid'] + '区，' + data;
            }
        },
        {
            "targets": 3,
            "render": function (data) {
               if (data === 'online'){
                    data = '在线';
                }else if(data === 'offline'){
                    data = '停机';
                }else if (data === 'maintain'){
                    data = '维护';
                }else if (data === 'inner'){
                    data = '内部';
                }else if (data === 'fault'){
                    data = '缺陷';
                }else{
                    data = '异常';
                }
               return data;
            }
        },
        {
            "targets": 7,
            "render": function (data) {
               if (data === 6){
                    data = '性能模式';
                }else if(data === 5){
                    data = '标准模式';
                }else{
                    data = '异常';
                }
               return data;
            }
        },
        {
            "targets": 8,
            "render": function (data, type, row) {
               if (data > 0){
                    data = '<span class="badge badge-danger" style="cursor: pointer" ' +
                        'onclick="query_error('+row['gameid']+', \'client_error\')">'+data+'</span>';
                }else{
                    data = '<span class="badge badge-success">'+data+'</span>';
                }
               return data;
            }
        },
        {
            "targets": 9,
            "render": function (data, type ,row) {
               if (data > 0){
                    data = '<span class="badge badge-danger" style="cursor: pointer" ' +
                        'onclick="query_error('+row['gameid']+', \'python_error\')">'+data+'</span>';
                }else{
                    data = '<span class="badge badge-success">'+data+'</span>';
                }
               return data;
            }
        },

        {
            "targets": -5,
            "render": function (data,type,row) {
                if (row['mode'] === 6){
                    if (data === 1){
                        return '<span class="badge badge-success">运行</span>';
                    }else{
                        return '<span class="badge badge-danger">关闭</span>';
                    }
                }else{
                    return '';
                }

            }
        },
        {
            "targets": [-3,-4],
            "render": function (data) {
               if (data === 1){
                    return '<span class="badge badge-success">运行</span>';
                }else{
                    return '<span class="badge badge-danger">关闭</span>';
                }
            }
        },
        {
            "targets": -2,
            "render": function (data) {
               if (data === 1){
                    data = '运作中';
                    return '<span class="badge badge-success">'+data+'</span>';
                }else if(data === 0){
                    data = '关闭';
                    return '<span class="badge badge-danger">'+data+'</span>';
                } else{
                    data = '状态异常';
                    return '<span class="badge badge-warning">'+data+'</span>';
                }
            }
        },
        {
            "targets": -1,
            "render": function (data) {
                return '<a class="badge badge-info " href="/game_manage?server_id='+data+'">游戏管理</a>&nbsp;' +
                    '<a class="badge badge-important" href="/data_manage?server_id='+data+'">数据管理</a>';

            }
        }
    ];
    $server_list_table.DataTable({
        "destroy" : true,
        'serverSide': true,
        "autoWidth" : true,
        "processing" : true,
        "ajax": ajax_data,
        "searching": false,    //去掉搜索框方法三：这种方法可以
        "lengthChange": true,
        "paging": true,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage,
        fixedColumns: {
            leftColumns: 2,
            rightColumns: 2
        },
        "scrollCollapse": false,
        "scrollX": true

   });
   // back_page_table($server_list_table, ajax_data, columns,columnDefs,false);
};

$btn_operate_game.click(function (e) {
    e.preventDefault();


    var action = "/allgame_b/operate";
    var form = $("<form></form>");
    form.attr('action',action);
    form.attr('method','post');
    var input1 = $("<input type='hidden' name='data' />");
    input1.attr('value', JSON.stringify(operate_game_data));
    form.append(input1);
    form.appendTo("body");
    form.css('display','none');
    form.submit();
});
