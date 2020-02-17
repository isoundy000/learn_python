/**
 * Created by admin on 2018/4/9.
 */
/**
 * Created by wangrui on 15/5/11.
 */

get_left_game_server();

var $start_server = $('#start_server');
var $stop_server = $('#stop_server');
var $restart_server = $('#restart_server');
var $operate_type = $('#operate_type');
var $confirm_operate_modal = $('#confirm_operate_modal');
var $btn_confirm_operate = $('#btn_confirm_operate');
var $confirm_operate_title_modal = $('#confirm_operate_title_modal');
var $confirm_operate_modal_content = $('#confirm_operate_modal_content');

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

var $multi_select_obj = $('#filter_out_ip, #filter_inner_ip, #filter_partition, #filter_server_status, #filter_game_status');

var OPERATE_GAME_DATA = {'server_list': []};
var SERVER_DATA = [];


// 初始化
init_data = $.parseJSON(init_data);
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
    async: false,
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
    async: false,
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
        // init_multi_select($('#single_search_value'));
        // $single_filter_search.click();
    },
    error: function () {
       "use strict";
       var replace_html = $filter_server_id.prop('outerHTML');
        replace_html = replace_html.replace($single_filter_type.val(), 'single_search_value');
        $single_filter_value.html(replace_html);
       //  init_multi_select($('#single_search_value'));
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
    "use strict";
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


var get_server_list = function (data) {
    "use strict";
    var ajax_data = {
        "url": "/new_server/search",
        "type": "POST",
        "dataType": 'json',
        "data": function ( d ) {
            return JSON.stringify( data);
          },
        contentType: 'application/json; charset=UTF-8',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'success'){
                return result.data;
            }else{
                 result.recordsTotal = 0;
                 result.recordsFiltered = 0;
                return [];
            }
        }
    };
    var columns = [{"title": '<input type="checkbox" name="i-check-all" checked>', 'data':'gameid'},
        {"title": "区服ID",'data':'gameid'}, {"title":"区服名称",'data':'name'}
        ,{"title":"开服时间",'data':'createtime'},{"title":"区服状态",'data':'status'}, {"title":"分区",'data':'section'},
        {"title":"总人数",'data':'total'}, {"title":"在线人数",'data':'online'}, {"title":"启动模式",'data':'mode'},
        {"title":"内网IP",'data':'ip'}, {"title":"外网IP", 'data': 'extranet_ip'}, {"title":"路由状态", 'data': 'gates'},
        {"title":"游戏状态", 'data': 'game'}, {"title":"扩展状态", 'data': 'ext'}, {"title":"运行状态",'data':'g_status'}];
    var columnDefs = [
        {
            "targets": 0,
            "class": 'td-check-child',
            "render": function (data,type,row) {
               return '<input type="checkbox" name="i-check-child" value="'+data+','+row['name']+'," checked>';
            }
        },
        {
            "visible": false,
            "targets": 1
        },
        {
            "targets": 2,
            "render": function (data, type, row) {
                return  row['gameid'] + '区，' + data;
            }
        },
        {
            "targets": 4,
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
            "targets": -7,
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
            "targets": [-4],
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
            "targets": [-2,-3],
            "render": function (data) {
               if (data === 1){
                    return '<span class="badge badge-success">运行</span>';
                }else{
                    return '<span class="badge badge-danger">关闭</span>';
                }
            }
        },
        {
            "targets": -1,
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
        }
    ];
     $server_list_table.DataTable({
        "destroy" : true,
        "autoWidth" : false,
        "processing" : true,
        "ajax": ajax_data,
        "searching": false,    //去掉搜索框方法三：这种方法可以
        "lengthChange": true,
        "lengthMenu": [ [-1, 10, 25, 50, 100], ["所有", 10, 25, 50, 100 ] ],
        "paging": true,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage
   });
   // new_front_page_table($server_list_table, ajax_data, columns,columnDefs,false);
};

if (!$.isEmptyObject(init_data)){
    get_server_list(init_data);
}

$server_list_table.on("change",":checkbox",function() {
    if ($(this).is("[name='i-check-all']")) {
        //全选
        $(":checkbox", $server_list_table).prop("checked", $(this).prop("checked"));
    }else{
        //一般复选
        var checkbox = $("tbody :checkbox",$server_list_table);
        $(":checkbox[name='i-check-all']",$server_list_table).prop('checked', checkbox.length === checkbox.filter(':checked').length);
    }
});

var wb_status = false;
var ws;
$confirm_operate_modal.on('hide.bs.modal', function () {
    "use strict";
    if (wb_status){
        ws.close();
    }
    $btn_confirm_operate.removeAttr('disabled');
    $btn_confirm_operate.text('确认操作');
});
var operate_server = function (o_name, control_type, o_type) {
    "use strict";
    var temp_server_data;
    SERVER_DATA = [];
    OPERATE_GAME_DATA['server_list'] = [];
    $(":checkbox[name='i-check-child']:checked",$server_list_table).each(function () {
        temp_server_data = $(this).val().split(',');
        OPERATE_GAME_DATA['server_list'].push(temp_server_data[0]);
        SERVER_DATA.push(temp_server_data);
    });
    if (SERVER_DATA.length>0){
        var server_name;
        var server_html = '<ul>';

        if (o_type === '5'){
            server_name = '游戏、路由、扩展';

        }else if(o_type === '2'){
            server_name = '路由';
        }else if(o_type === '3'){
            server_name = '游戏';
        }else if(o_type === '4'){
            server_name = '扩展';
        }

        $.extend(OPERATE_GAME_DATA, {'control_type': parseInt(control_type), 'method': parseInt(o_type)});
        $confirm_operate_title_modal.html(o_name +': ' + server_name);
        $confirm_operate_modal_content.html('');
        for(var i=0;i<SERVER_DATA.length;i++){
            server_html += '<li style="margin-bottom: 10px"><div class="col-md-6">'+SERVER_DATA[i][0]+'区：'+SERVER_DATA[i][1]+'</div><div id="operate_server_id_'+SERVER_DATA[i][0]+'" class="col-md-4" ' +
                'style="color: blue;"><span class="fa fa-circle-o"></span>待执行</div></li>';
        }
        server_html += '</ul>';
        $confirm_operate_modal_content.html(server_html);
        $confirm_operate_modal.modal('show');

    }else{
        alert('没有要操作的区服');
    }
};


// $(".td-check-child",$server_list_table).click(function () {
//     console.log($(":checkbox[name='i-check-child']", $(this)));
// });

$start_server.click(function () {
    "use strict";
    operate_server('启动', '1', $operate_type.val());
});

$stop_server.click(function () {
    "use strict";
    operate_server('关闭', '2', $operate_type.val());
});

$restart_server.click(function () {
    "use strict";
    operate_server('重启', '3', $operate_type.val());
});

$btn_confirm_operate.click(function () {
    "use strict";
    var server_obj;
    $(this).attr('disabled', 'disabled');
    $(this).text('操作执行中');
    for(var i=0;i<SERVER_DATA.length;i++) {
        server_obj = $('#operate_server_id_' + SERVER_DATA[i][0]);
        server_obj.css('color', 'black');
        server_obj.html('&nbsp&nbsp执行中').addClass('loading');
    }
    $.ajax({
       url: '/new_server/control',
        type: 'post',
        dataType: 'json',
        data: JSON.stringify(OPERATE_GAME_DATA),
        contentType: 'application/json; charset=UTF-8',

        success: function (result) {

           if (result['status'] === 'success'){
               var finish_num = 0;
               ws = new WebSocket("ws://"+window.location.host+"/new_server/message"); // 新建一个ws连接
               wb_status = true;
                ws.onopen = function() {  // 连接建立好后的回调
                   ws.send(result['command_id']);  // 向建立的连接发送消息
                };
                ws.onmessage = function (evt) {  // 收到服务器发送的消息后执行的回调
                    var wb_data = eval(evt.data);
                    console.log(wb_data);
                    for (i=0;i<wb_data.length;i++){

                        if (wb_data[i]['status'] === 2){
                            server_obj = $('#operate_server_id_' + wb_data[i]['gid']);
                            server_obj.removeClass('loading');
                            server_obj.css('color', '#45b6af');
                            server_obj.html('<span class="fa fa-check"></span>执行成功');
                            finish_num ++;
                        }else if(wb_data[i]['status'] === 3){
                            server_obj = $('#operate_server_id_' + wb_data[i]['gid']);
                            server_obj.removeClass('loading');
                            server_obj.css('color', 'red');
                            server_obj.html('<span class="fa fa-bolt"></span>执行失败,'+wb_data[i]['err_info']);
                            finish_num ++;
                        }
                    }
                    if (finish_num === SERVER_DATA.length){
                        $btn_confirm_operate.text('操作完成');
                        ws.close();
                        wb_status = false;
                    }
                };

           }else{
               alert('执行异常');
           }

        },
        error: function () {
            alert('执行异常');
        }
    });
});

