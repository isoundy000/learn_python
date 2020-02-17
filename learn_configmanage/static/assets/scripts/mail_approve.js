/**
 * Created by wangrui on 15/12/8.
 */


create_del_modal($("#mail_success_modal"), "是否通过此邮件?", "btn_confirm");
create_del_modal($("#mail_fail_modal"), "是否拒绝此邮件?", "btn_refuse");

var $mail_table = $('#mail_table');
var $btn_batch_operate = $('#btn_batch_operate');
var $batch_operate_modal = $('#batch_operate_modal');
var $batch_mail_text = $('#batch_mail_text');
var $btn_confirm_operate = $('#btn_confirm_operate');
var $batch_select = $('#batch_select');

var auditing_mail_table_obj;
var get_mail_approve = function (mail_status) {
    "use strict";
     var columns = [{"title": '<input type="checkbox" name="i-check-all">', 'data':'id'},
         {"title": "邮件类型",'data':'send_mail_way'},{"title": "游戏服",'data':'server'},
        {"title": "渠道",'data':'channel_list'},{"title":"vip等级",'data':'vip_grade'},{"title":"角色ID",'data':'rid'},
         {"title":"充值金额",'data':'role_recharge'},{"title": "邮件内容",'data':'content'}, {"title": "附件",'data':'reward_alias'},
         {"title": "操作时间",'data':'itime'}, {"title": "操作用户",'data':'user'},
         {"title":"审核用户",'data':'user2'}, {"title":"操作",'data':'id'}

    ];
    var fix_right_value = 1;
    var columnDefs = [
        {
            "targets": 0,
            "class": 'td-check-child',
            "render": function (data) {
               return '<input type="checkbox" name="i-check-child" value="'+data+'" >';
            }
        },
        {
            "targets": [1],
            "render": function (data) {
                var add_msg = data;
                if (data === "01"){
                    add_msg = "单服";
                } else if ( data === "02" ){
                    add_msg = "单服全体";
                } else if ( data === "03" ){
                    add_msg = "全服";
                } else if ( data === "04" ){
                    add_msg = "单服渠道";
                } else if ( data === "05" ){
                    add_msg = "全服渠道";
                } else if ( data === "06" ){
                    add_msg = "自定义邮件";
                } else if ( data === "07" ){
                    add_msg = "单服VIP邮件";
                }else if ( data === "08" ){
                    add_msg = "全服VIP邮件";
                }
                return add_msg;
            }
        },
        {
            "targets": [2,3,4,5],
            "render": function (data) {
                return data === 0 || data === '0' ? '-' : data;
            }
        },
        {
            "targets": [-1],
            "render": function () {
                return "<button onclick=\"success_mail(this)\" class=\"btn default btn-xs green\" data-toggle=\"modal\">" +
                    "通过</button><button onclick=\"fail_mail(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">拒绝 </button>";

            }
        }
    ];
    if (mail_status === 'no'){
        columnDefs.push({
            "targets": [-2],
            "visible": false
        });
    }else {
        fix_right_value = 2;
        columnDefs.push({
            "targets": [0, -1],
            "visible": false
        });
    }

    var ajax_data = {
        "url": "/getmailapprove",
        "type": "post",
        'data': function (d) {
            var send_data = {};
            send_data['start'] = d['start'];
            send_data['length'] = d['length'];
            send_data['draw'] = d['draw'];
            send_data['mail_status'] = mail_status;
            return send_data;
        },
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#mail_table_processing').hide();
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

    auditing_mail_table_obj = $mail_table.DataTable({
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
            rightColumns: fix_right_value
        },
        "scrollCollapse": false,
        "scrollX": true

   });



};

var select_check_mail;
$btn_batch_operate.click(function () {
    "use strict";
    select_check_mail = [];
    $(".DTFC_LeftBodyLiner :checkbox").each(function () {
        if ($(this).is(':checked')){
            select_check_mail.push($(this).val());
        }
    });
    var check_len = select_check_mail.length;
    if (check_len > 0){
        $batch_mail_text.html(check_len + '封邮件');
        $batch_operate_modal.modal('show');
    }else{
        alert('请勾选操作项');
    }


});

$btn_confirm_operate.click(function () {
    "use strict";
    var send_data = {'m_id': select_check_mail.join(','), 'status': $batch_select.val()};

    my_ajax(true, "/operatemail", 'get', send_data, true, function (data) {
        $batch_operate_modal.modal('hide');
        if (data['status'] === 'success'){
            auditing_mail_table_obj.ajax.reload(null, false);
            Common.alert_message($("#error_modal"), 1, "操作成功.");
        }else{
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        }

        
    });

});

$('.portlet-body').on('click', '.DTFC_LeftHeadWrapper',function () {
    "use strict";
    var $all_box_div = $(":checkbox", $(this));
   $(".DTFC_LeftBodyLiner :checkbox").prop("checked", $all_box_div.prop("checked"));
});
$mail_table.on("change",":checkbox",function() {
    "use strict";
      //一般复选
    var checkbox = $(".DTFC_LeftBodyLiner :checkbox");
    $(".DTFC_LeftHeadWrapper :checkbox").prop('checked', checkbox.length === checkbox.filter(':checked').length);
});


function operate_mail(m_id, status, tag){
    $.ajax({
        type: 'get',
        url: '/operatemail',
        data: {
            m_id: m_id,
            status: status
        },
        dataType: 'JSON',
        success: function (data) {
            if (tag === 1){
                $('#mail_success_modal').modal("hide");
            }
            else{
                $('#mail_fail_modal').modal("hide");
            }
            if (data["status"] === "fail"){
                Common.alert_message($("#error_modal"), 0, "操作失败.");
            }else{
                auditing_mail_table_obj.ajax.reload(null, false);
                Common.alert_message($("#error_modal"), 1, "操作成功.");
            }

            
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
}


function success_mail(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#mail_table").dataTable().fnGetData(nRoW);
    $('#mail_success_modal').modal("show");
    $("#btn_confirm").attr('onclick', "operate_mail(" + data["id"] + "," + "\"yes\"" + "," + 1 + ")");
}


function fail_mail(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#mail_table").dataTable().fnGetData(nRoW);
    $('#mail_fail_modal').modal("show");
    $("#btn_refuse").attr('onclick', "operate_mail(" + data["id"] + "," + "\"refuse\"" + "," + 2 + ")");
}

var $btn_approve = $("#btn_approve");
var $btn_success = $("#btn_success");
var $btn_fail = $("#btn_fail");

$btn_approve.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    get_mail_approve("no");
});

$btn_success.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    get_mail_approve("yes");
});

$btn_fail.on("click", function(e){
    e.preventDefault();
    change_class($(this));
    get_mail_approve("refuse");
});

$btn_approve.click();
