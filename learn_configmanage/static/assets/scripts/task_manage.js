//全局变量
$start_date = $('.page-container input.start_date');
$end_date = $('.page-container input.end_date');

//初始化时间
handleDatePickers();
$start_date.val(getNowFormatDate(1));
$end_date.val(getNowFormatDate(0));

//生成任务记录函数
var show_task_record = function () {
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var task_id = $('#task_id').val();

    var ajax_data = {
        "url": "/task_manage/task_record",
        "type": "POST",
        "data": {"task_id": task_id, "start_date":start_date, "end_date": end_date},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'success'){
                return result['data']
            } else {
                return []
            }
        }
    };
    var columns = [{"title": "任务ID"}, {"title": "操作用户"},{"title":"任务描述"},{"title":"任务数"},{"title":"执行时间"},
      {"title":"完成时间"}, {"title":"进度"}, {"title":"操作"}];
    var columnDefs = [
        {
            "targets": -2,
            "render": function (data) {
                if (data === '100'){
                    return '已完成'
                } else {
                    return data + '%'
                }

            }
        },
        {
            "targets": -1,
            "render": function (data, type, row) {
                var schedule = parseInt(row[6]);
                if (isNaN(schedule)){
                    return '进度异常'
                }else{
                    var btn_html = '<button type="button" onclick="btn_task_detail(this)" ' +
                        'class="btn btn-xs btn-primary">详情</button>';
                    return (schedule <= 100) ? btn_html : ''

                }
            }
        }
    ];
    return back_page_table($("#task_table"), ajax_data,columns,columnDefs,false);
};

//生成表格
var task_table_ins = show_task_record();

//查询按钮事件
$('#btn_query_task').click(function () {
    task_table_ins = show_task_record()
});

//任务详情
//生成任务记录函数
var show_task_detail = function (task_id, table_object) {
    var ajax_data = {
        "url": "/task_manage/task_sub_record",
        "type": "POST",
        "data": {"task_id": task_id},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'success'){
                return result['data']
            } else {
                return []
            }
        }
    };
    var columns = [{"title": "子任务ID"}, {"title":"任务描述"},{"title":"执行时间"},
      {"title":"完成时间"}, {"title":"状态"}];
    var columnDefs = [
        {
            "targets": -1,
            "render": function (data) {
                if (data === '01'){
                    return "<span class='badge badge-primary'>发送中</span>"
                } else if(data === '03') {
                    return "<span class='badge badge-warning'>执行失败</span>"
                } else if(data === '02') {
                    return"<span class='badge badge-success'>执行成功</span>"
                }
            }
        }
    ];
    return back_page_table(table_object, ajax_data,columns,columnDefs,false);
};


var btn_task_detail = function (row_data) {
    var $task_detail_head = $('#task_detail_head');
    var row_task_data = task_table_ins.row($(row_data).parent()).data();
    $task_detail_head.html('');
    $task_detail_head.append('<p class="text-left">任务ID：'+ row_task_data[0] +'</p>');
    $task_detail_head.append('<p class="text-left">操作人：'+ row_task_data[1] +'</p>');
    $task_detail_head.append('<p class="text-left">进度： '+ row_task_data[6] +'%</p>');
    $('#task_detail_modal').modal('show');
    show_task_detail(row_task_data[0], $('#task_detail_table'));
};
