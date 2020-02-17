var $push_files_table = $('#push_files_table');
var $confirm_push_file = $('#confirm_push_file');
var $push_file = $('#push_file');
var $error_modal = $('#error_modal');
var $add_file_modal = $('#add_file_modal');
var $game_server_list = $('#game_server_list');
var $send_file_modal = $('#send_file_modal');
var $send_describe = $('#send_describe');
var $confirm_send_file = $('#confirm_send_file');
var $push_file_prompt = $('#push_file_prompt');
var $push_records_modal = $('#push_records_modal');
var $push_records_table = $('#push_records_table');
var $file_content = $('#file_content');
var $btn_sync_all_files = $('#btn_sync_all_files');
var $send_file_row_2 = $('#send_file_row_2');
var $sync_all_prompt = $('#sync_all_prompt');


$game_server_list.multiselect({
    numberDisplayed: 10,
    // includeSelectAllOption: true,
    // selectAllText: '选择全部',
    enableFiltering: true,
    nonSelectedText: "==请选择==",
    buttonWidth: '100%',
    maxHeight: 300,
     onChange: function(option, checked) {
        if (option.val() === '0' && checked){
            var SelectedOptions = $('#game_server_list option').filter(function() {
                return $(this).is(':selected');
              });
            SelectedOptions.each(function(a, b) {
                var s_data = $(b).val();
                if ( s_data !== '0'){
                    $game_server_list.multiselect('deselect', s_data);
                }
            });

        }else {
          $game_server_list.multiselect('deselect', '0');
        }

        var channel_list = $game_server_list.val();
       if (channel_list !== null && channel_list.length > 0){
           $push_file_prompt.hide();
       }


    }
}
);

$btn_sync_all_files.click(function () {
    "use strict";
    $send_file_row_2.hide();
    $sync_all_prompt.show();
    $confirm_send_file.val(0);
    $('#send_file_modal').modal('show');

});

my_ajax(true, '/server/getgameserver', 'get', {}, false, function (result) {
    var server_list = [];
    server_list.push({"label": '所有区服（id小于1000）',"value": '0'});
    for (var rec in result){
        if (result[rec]['gameid'] < 1000){
            server_list.push({"label":result[rec]['gameid']+ ' '+ result[rec]['name'], "value": result[rec]['gameid']})
        }

    }
    $game_server_list.multiselect('dataprovider',server_list);
    $game_server_list.multiselect('select', '0');

});


var table_data;
var update_file_record = function () {
    "use strict";
    var ajax_data = {
        "url": "/get/push_files",
        "type": "get",
        "data":{},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result.status === 'success' ) {
                return result.data;
            }else {
                return [];
            }
        }
    };
    var columns = [{"title": "序号",'data':'id'}, {"title": "类型",'data':'type'},{"title":"文件名",'data':'name'},
        {"title":"路径",'data':'location'}, {"title":"时间",'data':'update_time'},{"title":"描述",'data':'file_describe'},
        {"title":"状态",'data':'status'}, {"title":"操作",'data':'status'}];
    var columnDefs = [
        {
            "targets": 1,
            "render": function (data) {
                if (data === 1){
                    return 'sql文件';
                }else if (data === 2){
                    return '源码包';
                }else if (data === 3) {
                    return '合服脚本';
                }
                else if (data === 4) {
                        return '源码路径';
                }else{
                    return data;
                }

            }
        },
        {
            "targets": -2,
            "render": function (data, type, row) {
                var check = $.inArray(row['type'], [1, 4])>=0;
                if (data === '0' && check ) {
                    return '<span class="badge badge-primary">未派发</span>&nbsp<button class="btn btn-xs red-intense" ' +
                        'onclick="show_file_content(\''+row['location']+'\')"> <i class="fa fa-file-text"></i></button>';
                } else if (data === '1' && check) {
                    return '<span class="badge badge-success">已派发</span>&nbsp<button class="btn btn-xs red-intense" ' +
                        'onclick="show_file_content(\''+row['location']+'\')"> <i class="fa fa-file-text"></i></button>';
                } else{
                    return '';
                }
            }
        },
        {
            "targets": -1,
            "render": function (data, type ,row) {
                if (data === '0'){
                    return '<button   class="btn btn-xs  red-intense" onclick="delete_send_file('+row['id']+')"> <i class="fa fa-trash-o"></i></button>' +
                        '&nbsp<button  class="btn btn-xs  blue" onclick="send_game_file('+row['id']+','+row['file_describe']+')"> <i class="fa fa-mail-forward"></i></button>';
                }else{
                    return '<button   class="btn btn-xs  yellow" onclick="btn_push_detail('+row['id']+',\''+row['name']+'\')"> <i class="fa fa-info-circle"></i></button>';
                }
            }
        }
    ];
    table_data = back_page_table($push_files_table, ajax_data,columns,columnDefs,false);
};

update_file_record();
var show_file_content = function (location) {
    console.log(location)
    var f_location = location.split('/static/');
    $file_content.html('');
    $('#show_file_modal').modal('show');
    $file_content.load('/static/'+ f_location.pop());

};

var delete_send_file = function (id) {
    my_ajax(true, '/delete/push_file', 'post', {id: id}, true, function (result) {
        table_data.ajax.reload(null, false)
    });

};
var btn_push_detail = function (id, name) {
    "use strict";
    var ajax_data = {
        "url": "/get/push_records",
        "type": "get",
        "data":{id: id},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            $('#push_records_title').text(name+' 推送记录');
            $push_records_modal.modal('show');
            return result;
        }
    };
    var columns = [{"title": "序号",'data':'id'}, {"title": "操作人",'data':'op_user'},{"title":"时间",'data':'create_time'},
        {"title":"ip地址",'data':'ip'}, {"title":"区服",'data':'game_id'},{"title":"路径",'data':'desc_path'},
        {"title":"状态",'data':'status'}];
    var columnDefs = [
        {
            "targets": -1,
            "render": function (data) {
                if (data === '0') {
                    return '<span class="badge badge-warning">失败</span>';
                } else if (data === '1') {
                    return '<span class="badge badge-success">成功</span>';
                } else{
                    return '<span class="badge badge-danger">异常</span>';
                }
            }
        }
    ];
    new_front_page_table($push_records_table, ajax_data,columns,columnDefs,false);
};

$confirm_push_file.click(function () {
    $confirm_push_file.attr('disabled', 'disabled');
    $confirm_push_file.text('上传中');
    var fromdata = new FormData();
    var name = $push_file.val();
    fromdata.append("file",$push_file[0].files[0]);
    fromdata.append("name",name);
    fromdata.append("file_describe",$('#file_describe').val());
    $.ajax({
        url:"/post/upload_files",
        type:"post",
        data: fromdata,
        contentType:false,
        processData: false,
        success: function (result) {
            if (result['status'] === 'success'){
                $add_file_modal.modal('hide');
                Common.alert_message($error_modal, 1, "操作成功");
                table_data.ajax.reload(null, false)
            }else{
                $add_file_modal.modal('hide');
                Common.alert_message($error_modal, 0, "操作失败："+ result['msg']);
            }
        },
        error: function () {
          alert('服务器异常')
        }
    });

});


$add_file_modal.on('show.bs.modal', function () {
    $confirm_push_file.text('确认上传');
    $confirm_push_file.removeAttr('disabled');

});

var send_game_file = function (id, file_describe) {
    $send_describe.val(file_describe);
    $send_file_row_2.show();
    $sync_all_prompt.hide();
    $confirm_send_file.val(id);
    $send_file_modal.modal('show');
};

$confirm_send_file.click(function () {
    var channel_list = $game_server_list.val();
    if (channel_list !== null){
        $confirm_send_file.attr('disabled', 'disabled');
        $confirm_send_file.text('执行中');

        var send_data = {'file_id': $confirm_send_file.val(), 'push_game': $game_server_list.val().join(',')};
        my_ajax(true, '/post/push_files', 'get', send_data, true, function (result) {
            if (result['status'] === 'success'){
                table_data.ajax.reload(null, false);
                $send_file_modal.modal('hide');
                Common.alert_message($error_modal, 1, "操作成功");
            }else{
                $send_file_modal.modal('hide');
                Common.alert_message($error_modal, 0, "操作失败："+ result['msg']);
            }
        });
    }else{
        $push_file_prompt.show()
    }


});

// $game_server_list.change(function () {
//    var channel_list = $game_server_list.val();
//    if (channel_list !== null && channel_list.length > 0){
//        $push_file_prompt.hide()
//    }
// });

$send_file_modal.on('show.bs.modal', function () {
    $push_file_prompt.hide();
    $confirm_send_file.text('确认派发');
    $confirm_send_file.removeAttr('disabled');

});
