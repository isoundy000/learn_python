//全局变量
var $cut_partition_tab = $('#cut_partition_tab');
var $tab_task_record = $('#tab_task_record');
var $start_date = $tab_task_record.find('input.start_date');
var $end_date = $tab_task_record.find('input.end_date');
var $tab1_game_server = $('#tab1_game_server');
var $btn_tab2_query = $('#btn_tab2_query');
var $tab1_partition = $('#tab1_partition');
var $tab1_start_day = $('#tab1_start_day');
var $tab1_end_day = $('#tab1_end_day');
var $btn_tab1_1 = $('#btn_tab1_1');
var $btn_tab1_2 = $('#btn_tab1_2');
var $btn_tab1_3 = $('#btn_tab1_3');
var $btn_tab1_4 = $('#btn_tab1_4');
var $tab1_table_head = $('#tab1_table_head');
var $btn_exe = $('#btn_exe');
var $btn_no_exe = $('#btn_no_exe');
var $start_exe_date = $('#start_exe_date');
var $start_exe_time = $('#start_exe_time');


var $cut_partition_record_tab = $('#cut_partition_record_tab');
//初始化
handleDatePickers();
$start_date.val(getNowFormatDate(1));
$end_date.val(getNowFormatDate(0));

$start_exe_time.val('23:00:00');
$start_exe_date.datepicker({
    format: 'yyyy-mm-dd',

    autoclose: true,
    startDate: new Date()
});


getGameServerData($tab1_game_server, 1);
getPartitionData($tab1_partition);



var op_com_conf = function (data, success_func) {
    $.ajax({
        url: '/operate/common_conf',
        type: 'get',
        data: data,
        success: success_func
    })
};
var field_1 = '';
var field_2 = '';
var field_3 = '';
$btn_tab1_1.click(function () {
    if ($(this).text() === '修改'){
        $tab1_start_day.removeAttr('disabled');
        $tab1_end_day.removeAttr('disabled');
        $tab1_partition.removeAttr('disabled');
        $start_exe_date.removeAttr('disabled');
        $start_exe_date.attr('readonly','readonly');
        field_1 = $tab1_start_day.val();
        field_2 = $tab1_end_day.val();
        field_3 = $tab1_partition.val();
        $btn_tab1_3.hide();
        $btn_tab1_4.show();
        $btn_tab1_1.text('确定');

        $('.desc_partition_edit').show();
    }else if ($(this).text() === '确定'){
        var field_tmp_1 = $tab1_start_day.val();
        var field_tmp_2 = $tab1_end_day.val();
        var field_tmp_3 = $tab1_partition.val();
        var field_tmp_4 = $start_exe_date.val();
        var field_tmp_5 = $start_exe_time.val();

        if ( (/^[1-9]+[0-9]*]*$/.test(field_tmp_1)) && (/^[1-9]+[0-9]*]*$/.test(field_tmp_2)) &&
            Number(field_tmp_2) > Number(field_tmp_1) && Number(field_tmp_1) >= 9 &&
            field_tmp_3 !== '' && field_tmp_4 !== '' && field_tmp_5 !== '')
        {
            var data = {conf_name: 'auto_cut_partition',op_type:'update',field_1: field_tmp_1,
                field_2: field_tmp_2, field_3: field_tmp_3, field_4: field_tmp_4+' '+field_tmp_5};
            op_com_conf(data, function () {
                Pending_exe_task('query_exe', btn_html_1);
            });
            $tab1_start_day.attr("disabled",'disabled');
            $tab1_end_day.attr("disabled",'disabled');
            $tab1_partition.attr("disabled",'disabled');
            $start_exe_date.removeAttr('readonly');
            $start_exe_date.attr('disabled','disabled');
            $('.desc_partition_edit').hide();
            $('.editable-click').removeClass('editable-click');
            $btn_tab1_1.text('修改');
            $btn_tab1_4.hide();
        }else {
            alert('配置错误，请查看！！！')
        }

    }
});

$btn_tab1_2.click(function () {
    $.ajax({
        url: '/auto_cut_partition/control',
        data: {'op_type': 'stop'},
        type: 'get',
        dataType: 'json',
        success: function(result){
            if (result.status === 'ok'){
                $btn_tab1_2.hide();
                $btn_tab1_1.show();
                $btn_tab1_3.show();
                $btn_exe.click();
            }
        }
    })
});

$btn_tab1_3.click(function () {

    $.ajax({
        url: '/auto_cut_partition/control',
        data: {'op_type': 'start', 'exe_time': $start_exe_date.val()+' '+$start_exe_time.val()},
        type: 'get',
        dataType: 'json',
        success: function(result){
            if (result.status === 'ok'){
                $btn_tab1_1.hide();
                $btn_tab1_3.hide();
                $btn_tab1_2.show();
                $btn_exe.click();
            }
        }
    })
});

$btn_tab1_4.click(function () {
    $btn_exe.click();
    $tab1_start_day.attr("disabled",'disabled');
    $tab1_end_day.attr("disabled",'disabled');
    $tab1_partition.attr("disabled",'disabled');
    $btn_tab1_1.text('修改');
    $btn_tab1_4.hide();
    $btn_tab1_3.show();

    $tab1_start_day.val(field_1);
    $tab1_end_day.val(field_2);
    $tab1_partition.val(field_3).trigger('change');

    $('.desc_partition_edit').hide();
    $('.editable-click').removeClass('editable-click');
});



var btn_html_1 = '<button  onclick="tab1_data_del(this)" class="btn btn-xs  red-intense"> ' +
                    '<i class="fa fa-trash-o"></i></button>';
var btn_html_2 = '<button  onclick="tab1_data_recovery(this)" class="btn btn-xs  blue"> ' +
                    '<i class="fa fa-reply"></i></button>';

var tab1_data_del = function (this_div) {
    var game_id = $(this_div).parent().siblings().eq(0).text().split('区')[0];
    var data = {conf_name: 'auto_cut_partition',op_type: 'concat_add',field_6: game_id};
    op_com_conf(data, function () {
        cut_partition_table.ajax.reload();
    });
};

var tab1_data_recovery = function (this_div) {
    var game_id = $(this_div).parent().siblings().eq(0).text().split('区')[0];
    var data = {conf_name: 'auto_cut_partition',op_type: 'replace_del',field_6: game_id};
    op_com_conf(data, function () {
        cut_partition_table.ajax.reload();
    });
};

//待执行任务
var cut_partition_table;
var Pending_exe_task = function (op_type, btn_html) {
    var ajax_data = {
        "url": "/plan/auto_cut_partition/handler",
        "type": "POST",
        "data":{op_type: op_type},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_tab_processing').hide();
        },
        dataSrc: function(result){
            if (result.status ==='stop' || result.status ==='start'){
                $tab1_start_day.val(result.field_1);
                $tab1_end_day.val(result.field_2);
                $tab1_partition.val(result.field_3).select2();
                var exe_date = result.field_4.split(' ')[0].replace(/-/g,"/");
                if (exe_date.length === 10 ){
                    $start_exe_date.datepicker('setDate', new Date(exe_date));
                }


                if (result.status ==='start'){
                    $btn_tab1_3.hide();
                    $btn_tab1_1.hide();
                    $btn_tab1_2.show();
                    $tab1_table_head.html('<h4><p class="text-center" style="margin-bottom: 0px">以下任务将执行</p></h4>');
                }else{
                    $btn_tab1_2.hide();
                    $btn_tab1_1.show();
                    $btn_tab1_3.show();
                    $tab1_table_head.html('<h4><p class="text-center" style="margin-bottom: 0px">任务已停止</p></h4>')
                }

                                if (result.data === null){
                    return []
                }else{
                    return result.data
                }

                        } else{
                            return []
            }
        }
    };
    var columns = [{"title": "游戏服",'data':'gameid'},{"title": "游戏服名",'data':'name'},
        {"title": "已开服天数",'data':'up_day'}, {"title":"当前分区",'data':'section'},{"title":"目标分区",'data':'target'},
        {"title":"开服时间",'data':'createtime'}, {"title":"操作"}];
    var columnDefs = [
        {
            "targets": 0,
            "render": function (data, type, row) {
                return data + '区:' + row['name']

            }
        },
        {
            "visible": false,
            "targets": 1
        },
        {
            "targets": 2,
            "render": function (data) {
                return data + '天'

            }
        },
        {
            "targets": 3,
            "render": function (data) {
                return $tab1_partition.find("option[value="+data+"]").text()
                // return '<span class="badge badge-info">' + $tab1_partition.find("option[value="+data+"]").text() + '</span>';
            }
        },
        {
            "targets": 4,
            "render": function (data, type, row) {
                return '<div><span  data-type="select2" data-pk="'+row['gameid']+'" data-partitionid="'+row['section']+'" ' +
                    'data-value="'+data+'"  data-title="目标分区">'+$tab1_partition.find("option[value="+data+"]").text()
                    +'</span><span class="pull-right fa fa-edit desc_partition_edit" style="cursor: pointer;display: none" onclick="partition_edit_func(event, this)"></span> '

                // return '<span class="badge badge-info">' + $tab1_partition.find("option[value="+data+"]").text() + '</span>';
            }

        },
        {
            "targets": -1,
            "render": function () {
                return btn_html

            }
        }

    ];
    cut_partition_table = new_front_page_table($cut_partition_tab, ajax_data,columns,columnDefs,false);
};

var partition_edit_func = function (event, this_div) {
    var select_data = [];
    for(var i=0;i<PARTITION_DATA.length;i++){
        select_data.push({id:PARTITION_DATA[i]['id'],text:PARTITION_DATA[i]['name']})
    }
    var $pre_div = $(this_div).prev();
    var game_id = Number($pre_div.attr('data-pk'));
    var sour_partition = Number($pre_div.attr('data-partitionid'));
    if (! $pre_div.hasClass('editable-click')){
        $pre_div.editable({
            source: select_data,
            url: function (params) {
                $.ajax({
                    type: 'get',
                    url: '/auto_cut_partition/game_partition/rel',
                    data: {game_id: game_id, sour_partition: sour_partition, desc_partition: params.value},
                    dataType: 'json' //assuming json response
                })
            },
            validate: function (value) {
                if (!$.trim(value)) {
                    return '不能为空';
                }
            }
            // success: function(response, newValue) {
            //     total_table_data[total_key_1][total_key_2][row_data+'-'+col_data] = newValue.Format("yyyyMMddhhmmss");
            //
            //     if (!$modify_flag.hasClass('active')){
            //         $modify_flag.addClass('active');
            //         $modify_flag.show()
            //     }
            //     console.log(total_table_data)
            // }
        });
    }
    event.stopPropagation();
    $(this_div).prev().click()

};

Pending_exe_task('query_exe', btn_html_1);

$btn_exe.click(function () {
    change_class($(this));
    Pending_exe_task('query_exe', btn_html_1);
});
$btn_no_exe.click(function () {
    change_class($(this));
    Pending_exe_task('query_no_exe', btn_html_2);
});



//任务记录
var Pending_exe_record = function () {
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var ajax_data = {
        "url": "/plan/auto_cut_partition/handler",
        "type": "POST",
        "data":{op_type:'record', start_date:start_date, end_date: end_date},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result.status === 'ok' ) {
                if (result.data === null){
                    return []
                }else{
                    return result.data
                }
            }else {
                return []
            }
        }
    };
    var columns = [{"title": "任务ID",'data':'id'}, {"title": "游戏服",'data':'server_name'},{"title":"开服天数",'data':'up_day'},
        {"title":"源分区",'data':'sour_partition'}, {"title":"目标分区",'data':'desc_partition'},
        {"title":"执行时间",'data':'create_time'}, {"title":"完成时间",'data':'update_time'},
        {"title":"执行结果","data":"status"}, {"title":"结果信息",'data':'info'}];
    var columnDefs = [
        {
            "targets": 2,
            "render": function (data) {
                return data + '天'
            }
        },
        {
            "targets": -2,
            "render": function (data) {
                if (data === 'fail') {
                    return '<span class="badge badge-warning">失败</span>'
                } else if (data === 'ok') {
                    return '<span class="badge badge-success">执行成功</span>'
                } else if (data === 'wait') {
                    return '<span class="badge badge-primary">处理中</span>'
                } else{
                    return '<span class="badge badge-danger">异常</span>'
                }
            }
        }
    ];
    return back_page_table($cut_partition_record_tab, ajax_data,columns,columnDefs,false);
};

Pending_exe_record();

$btn_tab2_query.click(function () {
    Pending_exe_record();
});