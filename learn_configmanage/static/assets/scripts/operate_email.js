/**
 * Created by liuzhaoyang on 15/9/7.
 */


handleDatePickers();
$('input.end_date').val(getNowFormatDate(0));

//全局变量
var $no_reply_detail = $('#no_reply_detail');
var $reply_user =  $("#reply_user");
var $send_type = $("#send_type");
var $annex_modal = $('#annex_modal');
var $annex_cont= $("#annex_cont");
var $btn_add_role = $('#btn_add_role');
var $role_div = $('#role_div');
var $game_server = $("#select_gameserver1");
var $game_server_list = $('#game_server_list');
var $channel_list_select = $('#channel_list_select');
var $cancel_reply_mail = $('#cancel_reply_mail');
var $div_user_grade = $('#div_user_grade');
var $user_grade = $('#user_grade');
var $pet_cid = $('#pet_cid');


if (PLATFORM_NAME === 'hot_yuenan' && PLATFORM_TYPE === 'hot_blood'){
    $('#div_xyys_num').show();
}

var QUALITY_CSS = {
    2: "green-haze",
    3: "blue-madison",
    4: "purple-plum",
    5: "yellow"
};

var send_mail_type = {
    1: "单服",
    2: "单服全体",
    3: "全服",
    4: "单服渠道",
    5: "全服渠道",
    7: "单服VIP等级",
    8: "全服VIP等级"
};

getGameServerData($game_server, 1);
init_select_html(false, send_mail_type, $send_type);
$.fn.modal.Constructor.prototype.enforceFocus = function () { };

var EQUIP_JSON = null;
var PROPS_JSON = null;
var SOUL_JSON = null;
var GENERAL_JSON=null;

var GENERAL_F_JSON = null;
var EQUIP_F_JSON = null;
var TREASURE_F_JSON = null;
var PET_FRAGMENT_JSON = {};
var MAGIC_SYMBOL_JSON = null;
var RED_SOLDIER_ESSENCE_JSON = null;


var CONFIG_TYPE = ["equip", "props", "soul", "general", "general_fragment", "equip_fragment", "treasure2_fragment",
    'pet3_attr', 'pet3_fragment', 'sigil', 'redl_awake_item'];


var draw_select_data = function (div_select, temp_json, t_key, value) {
    var temp = "<option value=''>" + "请选择" + "</option>";
    for (var t in temp_json){
        temp += "<option value='" + t + "'>";
        if (t_key.length !=0){
            temp += temp_json[t][t_key] + value;
        }
        if (temp_json[t].hasOwnProperty("name_CN")){
            temp += temp_json[t]["name_CN"] + "</option>";
        }
        else{
            temp += temp_json[t]["name"] + "</option>";
        }
    }

    div_select.html(temp);
    div_select.val('').trigger('change');
};

var init_data = function(){
    var server_id = $game_server.val();
    var success = function (data) {
        var middle_value = '';
        EQUIP_JSON = data["equip"];
        EQUIP_F_JSON = data["equip_fragment"];
        PROPS_JSON = data["props"];
        SOUL_JSON = data["soul"];
        GENERAL_JSON = data["general"];
        GENERAL_F_JSON = data["general_fragment"];
        TREASURE_F_JSON = data["treasure2_fragment"];

        for(var t in data["pet3_fragment"]){
            middle_value = data["pet3_attr"][data["pet3_fragment"][t]['petid']][0];
            PET_FRAGMENT_JSON[t] = {};
            if (middle_value.hasOwnProperty("name") ){
                PET_FRAGMENT_JSON[t]['name'] = middle_value['name'] + '碎片';
            }else{
                PET_FRAGMENT_JSON[t]['name_CN'] = middle_value['name_CN'] + '碎片';
            }

        }

        MAGIC_SYMBOL_JSON = data["sigil"];
        RED_SOLDIER_ESSENCE_JSON = data["redl_awake_item"];
    };

    var data = {
        server_id: server_id,
        type: JSON.stringify(CONFIG_TYPE)
    };
    my_ajax(false, "/queryjsondatabyserver", 'get', data, false, success);

    draw_select_data($("#equip_cid"), EQUIP_JSON, "quality", "星");
    draw_select_data($("#equip_f_cid"), EQUIP_F_JSON, "", "");
    draw_select_data($("#treasure_f_cid"), TREASURE_F_JSON, "", "");
    draw_select_data($("#prop_cid"), PROPS_JSON, "", "");
    draw_select_data($("#soul_cid"), SOUL_JSON, "quality", "星");

    draw_select_data($pet_cid, PET_FRAGMENT_JSON, "", "");

    draw_select_data($("#general_cid"), GENERAL_JSON, "quality", "星");

    var temp = "<option value=''>" + "请选择" + "</option>";
    var general_f_str = temp;
    for (var gfj in GENERAL_F_JSON) {
        if(GENERAL_JSON.hasOwnProperty(GENERAL_F_JSON[gfj]["general"])){
            if (GENERAL_JSON[GENERAL_F_JSON[gfj]["general"]].hasOwnProperty("name")){
                general_f_str += "<option value='" + gfj + "'>" + GENERAL_JSON[GENERAL_F_JSON[gfj]["general"]]["name"] + "</option>";
            }else{
                general_f_str += "<option value='" + gfj + "'>" + GENERAL_JSON[GENERAL_F_JSON[gfj]["general"]]["name_CN"] + "</option>";
            }
        }
    }
    $("#general_f_cid").html(general_f_str);
    $("#general_f_cid").val('').trigger('change');

    draw_select_data($("#magic_symbol_cid"), MAGIC_SYMBOL_JSON, "", "");
    draw_select_data($("#red_soldier_essence_cid"), RED_SOLDIER_ESSENCE_JSON, "", "");
};
setTimeout("init_data()", 2000);


//系统邮件查询
var table_html =   '<div class="table-responsive">'+
                        '<table id="system_mail_table" class="table table-bordered table-hover">'+
                        '</table>'+
                    '</div>';
//回复邮件
var reply_mail = function (row_data, server_id, server_name, start_date, end_date) {
    var reply_role_id = $("#no_reply_detail_table").dataTable().fnGetData($(row_data).parent().parent()[0]);
    $no_reply_detail.modal('hide');

    $no_reply_detail.on('hidden.bs.modal',function () {
        $('#write_mail').click();
        $send_type.val(1).trigger('change');
        $send_type.attr('disabled','disabled');
        $game_server.val(server_id).trigger('change');
        $game_server.attr('disabled','disabled');
        $btn_add_role.hide();
        $cancel_reply_mail.show();
        $reply_user.attr('value',reply_role_id['rid']);
        query_role_ajax($reply_user);
        $reply_user.attr('disabled','disabled');
        $ok_mail.attr('value',reply_role_id['id']);
        $no_reply_detail.off().on( 'hidden', 'hidden.bs.modal');
        $('#cancel_reply_mail').click(function () {
            $('#no_replay').click();
            single_server_no_reply(server_id, server_name, start_date, end_date)
        })

    });

};
//写邮件页面初始化
var write_mail_init = function () {
    // init_select_html(false, send_mail_type, $send_type);
    $('#cancel_reply_mail').hide();
    $reply_user.removeAttr('disabled');
    $('#send_type').removeAttr('disabled');
    $game_server.removeAttr('disabled');
    // getGameServerData($game_server, 1);
    $reply_user.parent().parent().siblings().remove();
    $reply_user.parent().parent().find('input:text').val('');
    $('#mail_title').val('');
    $('#mail_content').val('');
    $user_grade.val('');
    $annex_cont.html('');
    $ok_mail.removeAttr('value');
    $send_type.trigger('change');
};

var confirm_del_mail = function (server_id) {
    var del_reason = $('#del_reason').val();
    var $del_mail_prompt = $('#del_mail_prompt');
    if (del_reason.length === 0){
        $del_mail_prompt.text('错误：删除理由不能为空');
        $del_mail_prompt.show();
    }else{
        var send_data = {server_id: server_id, mail_id: detail_table_row_data['id'], del_reason: del_reason,
            mail_time: detail_table_row_data['time1'], role_id: detail_table_row_data['rid'], mail_content: detail_table_row_data['ask']};
        my_ajax(true, "/del/mails/id", "get", send_data, false, function (result) {
            if (result['status'] === 'success'){
                replay_table.ajax.reload();
            }else{
                $del_mail_prompt.text('删除失败，服务器异常');
                $del_mail_prompt.show();
            }
             
        },function () {
            $del_mail_prompt.text('删除失败，服务器异常');
            $del_mail_prompt.show();
        });
    }


};
function format_table (server_id) {
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td><textarea id="del_reason" class="form-control" rows="3" placeholder="请输入删除理由"></textarea></td>'+
            '<td><button type="button" onclick="confirm_del_mail('+server_id+')" class="btn btn-primary">确认删除</button></td>'+
            '<td><p id="del_mail_prompt" style="display: none;color: red"></p></td>'+
        '</tr>'+
    '</table>';
}

var detail_table_row_data;
var del_mail = function (this_div, server_id) {

    var mail_table_tr = $(this_div).closest('tr');
    var mail_table_row = replay_table.row( mail_table_tr );
    if ( mail_table_row.child.isShown() ) {
            // This row is already open - close it
            mail_table_row.child.hide();
            mail_table_tr.removeClass('shown');
        }
        else {
            $('.even.shown').each(function (a, b) {
                b = $(b);
                replay_table.row( b ).child.hide();
                b.removeClass('shown');
            });
            $('.odd.shown').each(function (a, b) {
                b = $(b);
                replay_table.row( b ).child.hide();
                b.removeClass('shown');
            });
            // Open this row
            detail_table_row_data = mail_table_row.data();
            mail_table_row.child( format_table(server_id)).show();
            mail_table_tr.addClass('shown');
        }
};

var replay_table;
//单个区服的未回复邮件
var single_server_no_reply = function (server_id, server_name, start_date, end_date) {
    $annex_cont.html('');
    $('#mail_title,#mail_content').val('');
    $no_reply_detail.modal('show');
    $('#no_reply_modal').html('未读邮件详情');
    $('#detail_server').html('区服：' +server_name);
    $('#detail_start_time').html('起始时间：' + start_date);
    $('#detail_end_time').html('终止时间：' + end_date);
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "ask",
            'sClass': 'center',
            "sTitle": "邮件内容"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "time1",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": '<button onclick=reply_mail(this,"'+ server_id + '","'+server_name+'","' +start_date+'","'+end_date+'")' +
                              ' class="btn default btn-xs" data-toggle="modal">回复 <i class="fa fa-edit"></i></button>'+
                              '  <button onclick="del_mail(this,'+server_id+')" class="btn btn-xs  red-intense" data-toggle="modal"> <i class="fa fa-trash-o"></i></button>'
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html = "";
        if (aData.status === "yes"){
            str_html = "<span class='badge badge-success'>已回复</span>"
        }
        else{
            str_html = "<span class='badge badge-danger'>未回复</span>"
        }
        $('td:eq(2)', nRow).html(str_html);
    };
    var sAjaxSource = "/mail/noreplydetailrecord";
    var data = {
        server_id: server_id,start_date: start_date,end_date: end_date
    };
    replay_table = dataTablePage($("#no_reply_detail_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);

};

$no_reply_detail.on('hide.bs.modal', function () {
  no_reply_mail_table.ajax.reload(null, false);
});

//所有未回复邮件的数量
var no_reply_mail_table;
var show_no_reply_mail = function (src_tab, query_btn) {
    if (query_btn === 0){
        $('input.start_date').val(getNowFormatDate(1));
    }
    var start_date = $('input.start_date').val();
    var end_date = $('input.end_date').val();
    $('.table-responsive').remove();
    $('#' + src_tab).append(table_html);
     var aoColumns = [
        {
            "mDataProp": "server_id",
            'sClass': 'center server_id',
            "sTitle": "区服"
        },
        {
            "mDataProp": "n_num",
            'sClass': 'center',
            "sTitle": "未回复数"
        },
        {
            "mDataProp": "r_num",
            'sClass': 'center',
            "sTitle": "已回复数"
        },
        {
            "mDataProp": "a_num",
            'sClass': 'center',
            "sTitle": "邮件总数"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var server_html = aData["server_id"] + "区: " + GAME_SERVER_DICT[aData["server_id"]]["name"];
        $('td:eq(0)', nRow).html(server_html);
        $('td:eq(0)', nRow).attr('value',aData["server_id"]);
        var server_name = + aData["server_id"] +'区'  + GAME_SERVER_DICT[aData["server_id"]]["name"];
        var op_html = "<button onclick=single_server_no_reply(" +aData["server_id"]+",'"
            + server_name+"','" +start_date+"','"+end_date+"')" + " class='btn default btn-xs' " +
                                "data-toggle=\"modal\">查看 <i class=\"fa fa-detail\"></i></button>";
        $('td:eq(4)', nRow).html(op_html);
    };
    var sAjaxSource = "/mail/noreplyrecord";
    var data = {
        start_date:start_date,end_date:end_date
    };
    no_reply_mail_table = front_page_table($("#system_mail_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
};
show_no_reply_mail('tab_no_read_mail', 0);

var tab_del_mail_record = function () {
    $('input.start_date').val(getNowFormatDate(6));
    var start_date = $('#tab_del_mail_record input.start_date').val();
    var end_date = $('#tab_del_mail_record input.end_date').val();
    var ajax_data = {
        "url": "/mail/del_records",
        "type": "GET",
        "data": {start_date:start_date,end_date: end_date},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        },
        "dataSrc": function (result) {
            return result;
        }
    };
    var columns = [{"title": "操作人", 'data': 'op_user'}, {"title":"操作时间", 'data': 'create_time'},
        {"title":"删除原因", 'data': 'del_reason'},{"title":"区服", 'data': 'server_id'},
      {"title":"角色编号", 'data': 'role_id'}, {"title":"邮件内容", 'data': 'mail_content'}];
    var columnDefs = [];
    $('.table-responsive').remove();
    $('#tab_del_mail_record').append(table_html);
    new_front_page_table($('#system_mail_table'), ajax_data,columns,columnDefs,false);

};

$('#btn_query_del_record').click(function () {
    tab_del_mail_record();
});

//邮件记录
function tab_mail_record(src_tab, btn_query){
    if (btn_query === 0){
        $('input.start_date').val(getNowFormatDate(6));
    }
    var send_user = $('#'+src_tab +' input.send_user').val();
    var rec_user = $('#'+src_tab +' input.rec_user').val();
    var start_date = $('#'+src_tab +' input.start_date').val();
    var end_date = $('#'+src_tab +' input.end_date').val();

    var aoColumns = [
        {
            "mDataProp": "username",
            'sClass': 'center',
            "sTitle": "发件人"
        },
        {
            "mDataProp": "s_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "mail_type",
            'sClass': 'center',
            "sTitle": "类型"
        },
        {
            "mDataProp": "server_id",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "channel_id",
            'sClass': 'center',
            "sTitle": "渠道"
        },
        {
            "mDataProp": "vip_grade",
            'sClass': 'center',
            "sTitle": "VIP等级"
        },
        {
            "mDataProp": "r_rid",
            'sClass': 'center',
            "sTitle": "收件人"
        },
        {
            "mDataProp": "mail_content",
            'sClass': 'center',
            "sTitle": "邮件内容"
        },
        {
            "mDataProp": "mail_att_ch",
            'sClass': 'center',
            "sTitle": "附件"
        },
        {
            "mDataProp": "send_mail_way",
            'sClass': 'center',
            "sTitle": "发送方式"
        },
        {
            "mDataProp": "mail_status",
            'sClass': 'center',
            "sTitle": "状态"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        if (aData.server_id === 0){
            $('td:eq(3)', nRow).html('-');
        }
        if (aData.channel_id === '0'){
            $('td:eq(4)', nRow).html('-');
        }
        if (aData.vip_grade === 0){
            $('td:eq(5)', nRow).html('-');
        }
        if (aData.r_rid === '0'){
            $('td:eq(6)', nRow).html('-');
        }
        var str_html = "";
        if (aData.mail_type === "01"){
            str_html = "<span class='badge badge-success'>发送邮件</span>"
        }
        else if (aData.mail_type === "02"){
            str_html = "<span class='badge badge-danger'>回复邮件</span>"
        }
        $('td:eq(2)', nRow).html(str_html);

        var type_html = "";
        if (aData.mail_status === "02"){
            type_html = "<span class='badge badge-success'>发送成功</span>"
        }
        else if (aData.mail_status === "10"){
            type_html = "<span class='badge badge-info'>待审核</span>"
        }
        else if (aData.mail_status === "12"){
            type_html = "<span class='badge badge-danger'>审核不通过</span>"
        }
        else if (aData.mail_status === "01"){
            type_html = "<span class='badge badge-primary'>发送中</span>"
        }
        else if (aData.mail_status === "04"){
            type_html = "<span class='badge badge-warning'>部分邮件失败</span>"
        }else {
            type_html = "<span class='badge badge-warning'>发送失败</span>"
        }

        $('td:eq(10)', nRow).html(type_html);

        var add_msg = "";
        var data_send_way = aData.send_mail_way;
        if (data_send_way === "01"){
            add_msg = "单服"
        } else if ( data_send_way === "02" ){
            add_msg = "单服全体"
        } else if ( data_send_way === "03" ){
            add_msg = "全服"
        } else if ( data_send_way === "04" ){
            add_msg = "单服渠道"
        } else if ( data_send_way === "05" ){
            add_msg = "全服渠道"
        } else if ( data_send_way === "06" ){
            add_msg = "自定义邮件"
        }else if ( data_send_way === "07" ){
            add_msg = "单服VIP邮件"
        }else if ( data_send_way === "08" ){
            add_msg = "全服VIP邮件"
        }
        $('td:eq(9)', nRow).html('<span>'+ add_msg +'</span>');

    };
    var sAjaxSource = "/mail/sendrecord";
    var data = {send_user:send_user,rec_user:rec_user,start_date:start_date,end_date:end_date};
    $('.table-responsive').remove();
    $('#' + src_tab).append(table_html);
    dataTablePage($("#system_mail_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
}


//自定义邮件
function tab_custom_mail(src_tab, btn_query){
    if (btn_query === 0){
        $('input.start_date').val(getNowFormatDate(6));
    }
    var send_user = $('#'+src_tab +' input.send_user').val();
    var start_date = $('#'+src_tab +' input.start_date').val();
    var end_date = $('#'+src_tab +' input.end_date').val();
    var aoColumns = [
        {
            "mDataProp": "username",
            'sClass': 'center',
            "sTitle": "操作用户"
        },
        {
            "mDataProp": "s_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "mDataProp": "att_name",
            'sClass': 'center',
            "sTitle": "文件名"
        },
        {
            "mDataProp": "remark_con",
            'sClass': 'center',
            "sTitle": "备注"
        },
        {
            "mDataProp": "batch_status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];
    var fnRowCallback = function (nRow, aData) {

        var status_html = "";
        var op_html = "";
        if (aData.batch_status === "00"){
            status_html = "<span class='badge badge-success'>文件上传成功</span>";
            op_html = '<button type="button" onclick="btn_send_file_mail(this)" class="btn btn-xs btn-primary">发送  <i class="fa fa-play"></i></button>'
        }
        else if (aData.batch_status === "01"){
            status_html = "<span class='badge badge-warning'>没有权限</span>"
        }
        else if (aData.batch_status === "02"){
            status_html = "<span class='badge badge-success'>文件上传成功</span><span class='badge badge-info'>已发送</span>"
        }else if (aData.batch_status === "03"){
            status_html = "<span class='badge badge-danger'>邮件发送异常</span>"
        }else if (aData.batch_status === "04"){
            status_html = "<span class='badge badge-danger'>上传失败</span>"
        }
        $('td:eq(4)', nRow).html(status_html);
        $('td:eq(5)', nRow).html(op_html);

    };
    var sAjaxSource = "/mail/batchrecord";
    var data = {send_user:send_user,start_date:start_date,end_date:end_date};
    $('.table-responsive').remove();
    $('#' + src_tab).append(table_html);
    dataTablePage($("#system_mail_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
}

//上传自定义文件
$batch_txt =  $('#batch_txt');
var upload_file = function () {
    var fromdata = new FormData();
    var name = $batch_txt.val();
    fromdata.append("file",$batch_txt[0].files[0]);
    fromdata.append("name",name);
    $.ajax({
        url:"/mail/batchrecord",
        type:"post",
        data: fromdata,
        contentType:false,
        processData: false,
        error: function () {
          alert('服务器异常')
        }
    });
    var $myModal = $('#myModal');
    $myModal.modal("hide");
    $myModal.on('hidden.bs.modal',function () {
        tab_custom_mail('tab_custom_mail', 0);
        $myModal.off().on( 'hidden', 'hidden.bs.modal');
    });
};


//文件格式成功，发送文件邮件
$file_name = $('#file_name');
var btn_send_file_mail = function (row_data) {
    $('#send_model').modal('show');
    var file_name =  $("#system_mail_table").dataTable().fnGetData($(row_data).parent().parent()[0]);
    $file_name.html(file_name["att_name"]);
    $file_name.attr("value",file_name["id"])
};

//附件邮件确认发送
var $btn_ok_file_mail = $('#btn_ok_file_mail');
var btn_ok_file_mail =function () {
    var mail_title = $('#send_model .mail_title').val();
    var mail_content = $('#send_model .mail_content').val();
    $btn_ok_file_mail.text('发送中');
    $btn_ok_file_mail.attr('disabled', 'disabled');
    if (mail_title === '' || mail_content ===''){
        alert('标题或内容不能为空');
        return
    }
    var file_name = $file_name.text();
    var file_id = $file_name.val();
    $.ajax({
        url:"/mail/filemail",
        type:"get",
        async: true,
        data: {file_name:file_name,mail_title:mail_title,mail_content:mail_content,file_id:file_id},
        error: function () {
          alert('服务器异常')
        },
        success:function () {
            $('#send_model').modal('hide');
            tab_custom_mail('tab_custom_mail', 0);
        }
     });
};

$('#send_model').on('show.bs.modal', function () {
  $btn_ok_file_mail.text('确认发送');
  $btn_ok_file_mail.removeAttr('disabled')
});

//点击添加表单数据清空
$('#add_annex').click(function (){
    $annex_modal.find('.select2me').select2("val", "");
    $annex_modal.find('input').val("");
});


//将所添加内容打印到 附件内容
$("#annex_form").on("click", function(e){
    var equip = $('#equip_cid').val();
    var equip_num = $("#equip_num").val();
    var props = $('#prop_cid').val();
    var props_num = $("#prop_num").val();
    var soul = $('#soul_cid').val();
    var soul_num = $("#soul_num").val();
    var general = $('#general_cid').val();
    var general_num = $("#general_num").val();
    var gold_num = $("#gold_num").val();
    var pet_cid = $("#pet_cid").val();
    var pet_num = $("#pet_num").val();
    var general_frag = $("#general_f_cid").val();
    var general_frag_num = $("#general_f_num").val();
    var equip_frag = $("#equip_f_cid").val();
    var equip_frag_num = $("#equip_f_num").val();
    var treasure_frag = $("#treasure_f_cid").val();
    var treasure_frag_num = $("#treasure_f_num").val();
    var silver_num = $("#silver_num").val();
    var vip_experience_num = $('#vip_experience_num').val();
    var xyys_num = $('#xyys_num').val();
    var magic_symbol_cid = $('#magic_symbol_cid').val();
    var magic_symbol_num = $('#magic_symbol_num').val();
    var red_soldier_essence_cid = $('#red_soldier_essence_cid').val();
    var red_soldier_essence_num = $('#red_soldier_essence_num').val();
    var annexlist = {
        equip:{
            cid: equip,
            num: equip_num
        },
        equip_frag:{
            cid: equip_frag,
            num: equip_frag_num
        },
        treasure_frag:{
            cid: treasure_frag,
            num: treasure_frag_num
        },
        props:{
            cid:props,
            num:props_num
        },
        soul:{
            cid:soul,
            num:soul_num
        },
        general:{
            cid:general,
            num:general_num
        },
        general_frag: {
            cid: general_frag,
            num: general_frag_num
        },
        pet: {
            cid: pet_cid,
            num: pet_num
        },
        magic_symbol: {
            cid: magic_symbol_cid,
            num: magic_symbol_num
        },
         red_soldier_essence: {
            cid: red_soldier_essence_cid,
            num: red_soldier_essence_num
        },
        gold_num: gold_num,
        silver_num: silver_num,
        vip_experience_num: vip_experience_num,
        xyys_num: xyys_num
    };
    for (var i in annexlist) {
        var annex_text_1 = '';
        var annex_text_2 = '';
        var temp_json = null;
        if (i == 'equip' && annexlist[i]['cid'] != '' && annexlist[i]['num']) {
            temp_json = EQUIP_JSON;
        }
        else if(i == 'equip_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = EQUIP_F_JSON;
        }
        else if(i == 'treasure_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = TREASURE_F_JSON;
        }
        else if(i == 'props' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PROPS_JSON;
        }
        else if(i == 'soul' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = SOUL_JSON;
        }
        else if(i == 'general' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_JSON;
        }
        else if(i == 'general_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_F_JSON;
        }
        else if(i == "pet" && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PET_FRAGMENT_JSON;
        }
        else if(i === "magic_symbol" && annexlist[i]['cid'] !== '' && annexlist[i]['num']){
            temp_json = MAGIC_SYMBOL_JSON;
        }
        else if(i === "red_soldier_essence" && annexlist[i]['cid'] !== '' && annexlist[i]['num']){
            temp_json = RED_SOLDIER_ESSENCE_JSON;
        }
        if (temp_json != null){
            if (i == 'general'){
                annex_text_1 = "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs "
                    + QUALITY_CSS[temp_json[annexlist[i]['cid']]["quality"]] + "'>" + temp_json[annexlist[i]['cid']]["name"] +
                    "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] +
                    "</span><button type=\"button\" class=\"close\" onclick=\"removeClear(this)\"></button></p>";
            }
            else if(i == "general_frag"){
                var general_cid = GENERAL_F_JSON[annexlist[i]['cid']]["general"];
                var general_name = GENERAL_JSON[general_cid]["name"] + "碎片";
                var general_quality = GENERAL_JSON[general_cid]["quality"];
                annex_text_1 = "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs "
                    + QUALITY_CSS[general_quality] + "'>" + general_name + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>"
                    + annexlist[i]['num'] + "</span><button type=\"button\" class=\"close\" onclick=\"removeClear(this)\"></button></p>";
            }
            else{
               annex_text_1 = "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='label label-success'>"
                   + temp_json[annexlist[i]['cid']]["name"] + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" +
                   annexlist[i]['num'] + "</span><button type=\"button\" class=\"close\" onclick=\"removeClear(this)\"></button></p>"
            }
        }

        if(i=='gold_num' && annexlist[i] != ''){
            annex_text_2 = "<p><input type='hidden' value='1001'><span class='label label-success'>" + "元宝:" +
                "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" +
                annexlist[i] + "</span><button type=\"button\" class=\"close\" onclick=\"removeClear(this)\"></button></p>"
        }

        else if(i=='silver_num' && annexlist[i] != ''){
            annex_text_2 = "<p><input type='hidden' value='1000'><span class='label label-success'>" + "银两:" +
                "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" +
                annexlist[i] + "</span><button type=\"button\" class=\"close heavy\" onclick=\"removeClear(this)\"></button></p>"
        }
        else if(i==='xyys_num' && annexlist[i] !== ''){
            annex_text_2 = "<p><input type='hidden' value='1023'><span class='label label-success'>" + "许愿御手:" +
                "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" +
                annexlist[i] + "</span><button type=\"button\" class=\"close heavy\" onclick=\"removeClear(this)\"></button></p>"
        }
        else if(i==='vip_experience_num' && annexlist[i] !== ''){
            annex_text_2 = "<p><input type='hidden' value='1008'><span class='label label-success'>" + "VIP经验:" +
                "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" +
                annexlist[i] + "</span><button type=\"button\" class=\"close heavy\" onclick=\"removeClear(this)\"></button></p>"
        }
        $annex_cont.append(annex_text_1 + annex_text_2);
    }

    $annex_modal.modal("hide");

});

var removeClear = function (this_mess) {
    $(this_mess).parent().remove();
};


var query_role_ajax = function (this_obj) {
    var this_div = this_obj.parent().parent().find('.role_name');
    var rid = this_obj.val();
    var server_id = $game_server.val();
    if (rid.length === 0){
        this_div.val('');
    } else {
        $.ajax({
            type: 'get',
            url: '/query_role_info',
            data: {'query_info':JSON.stringify(['name']), 'by_id':rid, 'game_server_id': server_id},
            success: function (result) {
                if (result['status'] === 'ok'){
                    if (result['data'].length > 0){
                        this_div.val(result['data'][0]['name']);
                        this_div.attr('name', '1')
                    } else {
                        this_div.val('提示：角色不存在');
                        this_div.attr('name', '0')
                    }
                }
            }
        })
    }
};
//查询角色名
var query_role_name = function () {
    $role_div.find("input:text").bind("input propertychange",function () {
        var this_obj = $(this);
        query_role_ajax(this_obj)
    });
};

$game_server.bind('change', function () {
    $.each($role_div.find(".role_id:text"), function () {
        var this_obj = $(this);
        query_role_ajax(this_obj)
    });
});

//邮件类型改变，触发事件
$send_type.on("change",function () {
    var mail_type = $('#send_type option:selected').val();
    if (mail_type === '1'){
        // getGameServerData($game_server, 1);
         $('#channel_list').hide();
         $div_user_grade.hide();
        $game_server_list.show();
        $('#div_reply_user').show();
    }else if (mail_type === '2'){
        $('#div_reply_user').hide();
        $('#channel_list').hide();
        $div_user_grade.hide();
        $game_server_list.show();
    }else if (mail_type === '3'){
        $('#channel_list').hide();
        $('#div_reply_user').hide();
        $div_user_grade.hide();
        $game_server_list.hide()
    }else if (mail_type === '4'){
        $('#div_reply_user').hide();
        $div_user_grade.hide();
        $game_server_list.show();
        $('#channel_list').show();
    }else if (mail_type === '5'){
        $('#div_reply_user').hide();
        $div_user_grade.hide();
        $game_server_list.hide();
        $('#channel_list').show();
    }else if (mail_type === '7'){
        $('#div_reply_user').hide();
        $('#channel_list').hide();
        $game_server_list.show();
        $div_user_grade.show();
    }else if (mail_type === '8'){
        $('#div_reply_user').hide();
        $game_server_list.hide();
        $('#channel_list').hide();
        $div_user_grade.show();
    }

});
$btn_add_role.click(function () {
    var role_div_html =
        '<div class="form-group">' +
            '<div class="input-icon col-md-5" style="padding-right: 0">' +
            '<i class="fa fa-user"></i>' +
                '<input class="form-control role_id" name="reply_user" placeholder="角色编号" type="text"/>'+
            '</div>' +
            '<div class="input-group col-md-7" >' +
            '<div style="padding-left: 0">' +
                '<input class="form-control role_name" name="1" style="border-left: none" placeholder="角色名" type="text" readonly/>' +
            '</div>'+
             '<span class="input-group-btn">' +
                '<button class="btn default date-reset" onclick="$(this).parent().parent().parent().remove()" type="button">' +
                    '<i class="fa fa-times"></i></button>' +
            '</span></div>' +
        '</div>';

    $role_div.append(role_div_html);
    $role_div.find("input:text").unbind();
    query_role_name()
});

query_role_name();

$channel_list_select.multiselect({
    numberDisplayed: 10,
    // includeSelectAllOption: true,
    // selectAllText: '选择全部',
    enableFiltering: true,
    nonSelectedText: "==请选择(最多选择4项)==",
    buttonWidth: '100%',
    maxHeight: 300,
    onChange: function(option, checked) {
        // Get selected options.
        var selectedOptions = $('#channel_list_select option:selected');

        if (selectedOptions.length >= 4) {
          // Disable all other checkboxes.
          var nonSelectedOptions = $('#channel_list_select option').filter(function() {
            return !$(this).is(':selected');
          });

          var dropdown = $channel_list_select.siblings('.multiselect-container');
          nonSelectedOptions.each(function() {
            var input = $('input[value="' + $(this).val() + '"]');
            input.prop('disabled', true);
            input.parent('li').addClass('disabled');
          });
        }
        else {
          // Enable all checkboxes.
          var dropdown = $channel_list_select.siblings('.multiselect-container');
          $('#channel_list_select option').each(function() {
            var input = $('input[value="' + $(this).val() + '"]');
            input.prop('disabled', false);
            input.parent('li').addClass('disabled');
          });
        }
    }
}
);

$channel_list_select.multiselect('dataprovider', getChannelData());

$("#mail_type").on("change", function (e) {
    e.preventDefault();
    if ($(this).is(":checked")) {
        $reply_user.val("");
        $("#mail_all").attr("checked", false);
        $("#div_reply_user").hide();
    }
    else{
        $("#mail_all").attr("checked", true);
        $("#div_reply_user").show();
    }
});

//提取邮件发送内容
var $ok_mail = $('#ok_mail');
var mail_data = {};
$ok_mail.click(function () {
    var reward_alias = "";
    $annex_cont.children('p').each(function () {
        var att_obj = $(this).find('span');
       var att_name = att_obj.eq(0).text();
       var att_num = att_obj.eq(1).text();
       reward_alias += "[" + att_name + ": " + att_num + "]";
    });
    var mail_title = $("#mail_title").val();
    var mail_content = $("#mail_content").val();
    var annex_cont = $annex_cont.html();
    var reply_mail_id = $ok_mail.val();
    var write_server_name = "";
    var role_id_list = [];
    var role_display_list = [];
    var export_title = '';
    var server_id = '';
    var channel_list_select ='';

    if (mail_title === "" || mail_content === "" ){
        alert('提示：标题或内容不能为空');
        return
    }
    $annex_cont.children().each(function () {
        var cid = $(this).find("input").val();
        var num = $(this).find("span:eq(1)").html();
        export_title += "\"" + cid + "\":\"" + num + "\",";
    });
    var mail_annex = "{" + export_title.substring(0, export_title.length - 1) + "}";
    if (mail_annex === "{}"){
        mail_annex = ''
    }
    var mail_type = $('#send_type option:selected').val();
    var mail_value = send_mail_type[mail_type];
    if (mail_type === '1'){
        write_server_name = $game_server.find("option:selected").text();
        $.each($role_div.find('.form-group'), function () {
            var role_name_obj = $(this).find('.role_name');
            if (role_name_obj.attr('name') === '1'){
                var role_id = $(this).find('.role_id').val();
                role_id_list.push(role_id);
                role_display_list.push(role_id + '（' + role_name_obj.val() + '）')
            }
        });
        if (role_id_list.length === 0){
            alert('提示：角色编号不能为空');
            return
        }
        server_id = $game_server.val();

        mail_data = {mail_type:mail_type,server_id:server_id,role_id_list:JSON.stringify(role_id_list),mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias,reply_mail_id:reply_mail_id}
    }else if (mail_type === '2'){
        write_server_name = $game_server.find("option:selected").text();
        server_id = $game_server.val();
        role_display_list = ['以上区服、渠道下的所有角色'];
        mail_data = {mail_type:mail_type,server_id:server_id,mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }else if (mail_type === '3'){
        role_display_list = ['所有角色'];
        mail_data = {mail_type:mail_type,mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }else if (mail_type === '4'){
        write_server_name = $game_server.find("option:selected").text();
        channel_list_select = $channel_list_select.val();
        role_display_list = ['以上区服、渠道下的所有角色'];
        server_id = $game_server.val();
        mail_data = {mail_type:mail_type,server_id:server_id,channel_list_select:JSON.stringify(channel_list_select),mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }else if (mail_type === '5'){
        channel_list_select = $('#channel_list_select').val();
        role_display_list = ['以上区服、渠道下的所有角色'];
        mail_data = {mail_type:mail_type,channel_list_select:JSON.stringify(channel_list_select),mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }else if (mail_type === '7'){
        user_grade_value = $user_grade.val();
        reg=/^[1-9]\d*$/;
        if (!reg.test(user_grade_value)){
            alert('提示：VIP等级输入有误');
            return
        }
        write_server_name = $game_server.find("option:selected").text();
        server_id = $game_server.val();
        role_display_list = [server_id+'区，VIP等级为 '+user_grade_value+' 的所有角色'];
        mail_data = {mail_type:mail_type,server_id:server_id,user_grade: user_grade_value, mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }else if (mail_type === '8'){
        user_grade_value = $user_grade.val();
        reg=/^[1-9]\d*$/;
        if (!reg.test(user_grade_value)){
            alert('提示：VIP等级输入有误');
            return
        }
        role_display_list = ['VIP等级为 '+user_grade_value+' 的所有角色'];
        mail_data = {mail_type:mail_type,user_grade: user_grade_value,mail_title:mail_title,
            mail_content:mail_content,mail_annex:mail_annex,reward_alias:reward_alias}
    }

    if (write_server_name === ''){
        write_server_name = '全服'
    }
    if (channel_list_select === ''){
        channel_list_select = ["不限"]
    }else{
        channel_list_select = [];
        $channel_list_select.find("option:selected").each(function () {
           channel_list_select.push( $(this).text() )
        });
    }
    if (channel_list_select === null){alert("渠道不能为空!!!");return}
    $("#send_mail_type").html(mail_value);
    $("#send_game").html(write_server_name);
    $("#send_channel_list").html(channel_list_select.join(', '));
    $('#mail_user').html(role_display_list.join(', '));
    $("#mail_tit").html(mail_title);
    $('#mail_cont').html(mail_content);
    $('#mail_annex').html(annex_cont);

    $('#confirm_modal').modal('show');

});

var $error_modal = $("#error_modal");
$('#send_mail').click(function () {
    var reply_mail_id = $ok_mail.val();
    var success_func = function(data){
        $("#confirm_modal").modal("hide");
        if (data["status"] === "fail") {
            Common.alert_message($error_modal, 0, data["errmsg"]);
        }
        else if (data["status"] === "approve") {
            Common.alert_message($error_modal, 1, "邮件需要审核，可通过邮件记录查看结果");
        }
        else {
            Common.alert_message($error_modal, 1, "邮件已发送，可通过邮件记录查看结果");
        }
        $error_modal.on('hidden.bs.modal',function () {
            if (reply_mail_id === ''){
                write_mail_init();
            }else{
                $('#no_replay').click();
            }
            $error_modal.off().on( 'hidden', 'hidden.bs.modal');
        });
        $("#tab_single_mail").modal("hide");
        $annex_cont.html('');
    };
    my_ajax(true, "/mail/writemail", "get", mail_data, false, success_func);
});


