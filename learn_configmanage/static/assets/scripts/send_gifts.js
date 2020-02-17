var $op_record_table = $('#op_record_table');
var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $file_info = $('#file_info');
var $uid = $('#uid');
var $myModal = $('#myModal');
var $modal_prompt = $('#modal_prompt');
var $btn_confirm = $('#btn_confirm');

//初始化
handleDatePickers();
$start_date.val(getNowFormatDate(6));
$end_date.val(getNowFormatDate(0));

$myModal.on('hidden.bs.modal',function () {
    $btn_confirm.removeAttr('disabled');
    $btn_confirm.text('确认发送礼包');
    $modal_prompt.hide();
});

var check_file = function () {
    //上传自定义文件
    $btn_confirm.text('发送中');
    $btn_confirm.attr('disabled','disabled');

    var fromdata = new FormData();
    var name = $file_info.val();
    fromdata.append("file",$file_info[0].files[0]);
    fromdata.append("name",name);
    $.ajax({
        url:"/post/gifts/uid",
        type:"post",
        data: fromdata,
        // async: false,
        contentType:false,
        processData: false,
        success: function (result) {
            if (result['status'] === 'success'){
                $myModal.modal('hide');
                op_record();

            }else{
                $modal_prompt.show()
            }
        },
        error: function () {
          alert('服务器异常')
        }
    });




};

//操作记录
var op_record = function () {
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var uid = $uid.val();
    var ajax_data = {
        "url": "/send/gifts/records",
        "type": "GET",
        "data":{start_date:start_date, end_date: end_date, uid: uid},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {
            if (result.status === 'success' ) {
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
    var columns = [{"title": "记录ID", 'data': 'record_id'},{"title": "uid", 'data': 'uid'},{"title": '操作用户', 'data': 'op_user'},
        {"title": "创建时间", 'data': 'create_time'},{"title":"备注", 'data': 'remark'}];
    var columnDefs = [];
    return new_front_page_table($op_record_table, ajax_data,columns,columnDefs,false);
};

op_record();