/**
 * Created by liuzhaoyang on 15/12/7.
 */

var $select_game = $('#select_game');
var $operate_chat_modal = $('#operate_chat_modal');
var $role_operate_type = $('#role_operate_type');
var $close_role = $('#close_role');
var $no_chat = $('#no_chat');
var $chat_info = $('#chat_info');
var $role_info = $('#role_info');
var $btn_confirm_operate = $('#btn_confirm_operate');
var $no_chat_button_txt = $('#no_chat_button_txt');
var $no_chat_num = $('#no_chat_num');

var $select_server_2 = $('#select_server_2');
var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $chat_type = $('#chat_type');
var $btn_query_chat = $('#btn_query_chat');
var $guild_private_chat_table = $('#guild_private_chat_table');
var $guild_private_chat_modal = $('#guild_private_chat_modal');
var $guild_private_chat_modal_body = $('#guild_private_chat_modal_body');
var $btn_guild_private_chat_confirm = $('#btn_guild_private_chat_confirm');


getGameServerData($select_game, 0);
getGameServerData($select_server_2, 0);
handleDatePickers();
$start_date.val(getNowFormatDate(1));
$end_date.val(getNowFormatDate(0));

var server_pos;
var str_info2 = "";
var operate_server_id;
var operate_role_id;

// 查询聊天
var chat_query = function (server_id, str_info2, server_pos) {
    $.ajax({
            type: 'get',
            url: '/chatquery',
            data: {server_id: server_id,
                pos: server_pos
            },
            dataType: 'JSON',
            success: function (data) {
                var str_info = "";
                if (data["status"] === "success") {
                    if (server_id === '0'){
                        for (var i in data["server_data"]) {
                            for (var d in data["server_data"][i]['data']){
                                if (data["server_data"][i]['data'][d]["rid"] === 0) {
                                    str_info += "<li class='out'><span class='chat_name badge badge-danger'>";
                                }
                                else {
                                    str_info += "<li class='in'><span  class='role_info' style='display: none'>"+i+','+data["server_data"][i]['data'][d]["rid"]+"</span>" +
                                        "<span class='chat_name server_id badge badge-primary'>"+i+"区</span>" +
                                        "<span class='chat_name role_name badge badge-success'>";
                                }
                                str_info += data["server_data"][i]['data'][d]["name"] + "(" + data["server_data"][i]['data'][d]["rid"] + ")" + ":</span>";
                                str_info += "<div class=\"message\"> <span class=\"arrow\"></span>";
                                str_info += "<span class=\"body\">" + data["server_data"][i]['data'][d]["content"];
                                str_info += "</span></div></li>";
                            }
                            server_pos[i] = data["server_data"][i]['pos'];

                        }
                    }else{
                        for (var i in data["data"]) {
                            if (data["data"][i]["rid"] === 0) {
                                str_info += "<li class='out'><span class='chat_name badge badge-danger'>";
                            }
                            else {
                                str_info += "<li class='in'><span  class='role_info' style='display: none'>"+server_id+','+data["data"][i]["rid"]+"</span>" +
                                        "<span class='chat_name server_id badge badge-primary'>"+server_id+"区</span>" +
                                        "<span class='chat_name role_name badge badge-success'>";
                            }
                            str_info += data["data"][i]["name"] + "(" + data["data"][i]["rid"] + ")" + ":</span>";
                            str_info += "<div class=\"message\"> <span class=\"arrow\"></span>";
                            str_info += "<span class=\"body\">" + data["data"][i]["content"];
                            str_info += "</span></div></li>";

                        }
                        server_pos = data["pos"];
                    }

                    str_info2 += str_info;
                    $("#chats_list").html(str_info2);
                    $('#chats .scroller').slimScroll({
                        scrollTo: $("#chats .chats").height()
                    });
                    str_info2 = "";

                }else{
                    $("#chats_list").html('<li>查询异常</li>');
                }
                $('#chats_list .in').click(function () {
                    $operate_chat_modal.modal('show');
                    var role_info = $(this).find('.role_info').text().split(',');
                    operate_server_id = role_info[0];
                    operate_role_id = role_info[1];
                    $role_info.text($(this).find('.server_id').text() + ',' + $(this).find('.role_name').text());
                    $chat_info.text($(this).find('.body').text());
                });
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};
var server_id = $select_game.val();
// chat_query(server_id, str_info2, pos);

//游戏服选择
$select_game.on('change', function(e) {
    e.preventDefault();
    server_id = $(this).val();
    if (server_id === '0'){
        server_pos = {};
        for(var i in GAME_SERVER_DICT){
            server_pos[i] = 0;
        }
        server_pos = JSON.stringify(server_pos);
        $('#chat_content').hide();
        $('#confirm_send').hide();
    }else{
        server_pos = 0;
        $('#chat_content').show();
        $('#confirm_send').show();
    }
    chat_query(server_id, str_info2, server_pos);
});
$select_game.change();

//5秒，10秒刷新
var ten = null;
var five = null;
$("input[name='chat_type']").on("click", function (e) {
    e.preventDefault();
    var flush_value = $("input[name='chat_type']:checked").val();
    var server_id = $('#select_game').val();
    if (flush_value == "5") {
        if (ten != null)
            clearInterval(ten);
        if (five == null)
            five = setInterval("chat_query(server_id, str_info2, server_pos)", 5000);
    }
    if (flush_value == "10") {
        if (five != null) {
            clearInterval(five);
        }
        if (ten == null) {
            ten = setInterval("chat_query(server_id, str_info2, server_pos)", 10000);
        }
    }
});

//停止刷新
$("#clearInterval").on("click", function (e) {
    e.preventDefault();
    var refresh_chat = $("input[name=chat_type]");
    if (five != null){
        refresh_chat.attr("checked",false);
        refresh_chat.parent("span").removeClass("checked");
        five = window.clearInterval(five);
    }
    else if (ten != null){
        refresh_chat.attr("checked",false);
        refresh_chat.parent("span").removeClass("checked");
        ten = window.clearInterval(ten);
    }

});

//发送聊天
$("#confirm_send").on("click", function (e) {
    e.preventDefault();
    var server_id = $('#select_game').val();
    var chat_content = $("#chat_content").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/sendchat',
            data: {
                server_id: server_id,
                chat_content: chat_content
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data['status'] === 'success'){
                    $("#chat_content").val("");
                    chat_query(server_id, str_info2, server_pos);
                }else{
                    alert('操作失败')
                }

            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )
});


$role_operate_type.change(function () {
    var s_o_type = $role_operate_type.val();
    if (s_o_type === 'close_role'){
        $no_chat.hide();
        $close_role.show();
    }else {
        $no_chat.show();
        $close_role.hide();

    }

});

$btn_confirm_operate.click(function () {
    var op_type = $role_operate_type.val();
    var url;
    var data;
    if (op_type === 'close_role'){
        url = '/operateseal';
        data = {server_id: operate_server_id, close_role: operate_role_id, close_id: '', close_type: $('#close_role_num').val()}

    }else{
        url = '/addgag';

        var no_chat_type = $no_chat_button_txt.text();
        var gag_type;
        if (no_chat_type === '小时'){
            gag_type = 'hour'
        }else if (no_chat_type === '天'){
            gag_type = 'day'
        }else{
            gag_type = 'forever'
        }

        var gag_num = $no_chat_num.val();
        if ( isNaN(Number(gag_num)) && gag_type !== 'forever'){
            alert('限制类型不能为空');
            return
        }
        data = {server_id: operate_server_id, role_id: operate_role_id, gag_type: gag_type, gag_num: gag_num}
    }
    my_ajax(true, url, "get", data, true, function (result) {
        $operate_chat_modal.modal('hide');
        if (result['status'] === 'success' || result['status'] === 1){
            Common.alert_message($error_modal, 1, "操作成功");
        }else{
            Common.alert_message($error_modal, 0, "操作失败");
        }
    });
});

var $error_modal = $("#error_modal");
$('.dropdown-menu a').click(function () {
    $no_chat_button_txt.text($(this).text());
    if ($(this).text() === '永久'){
        $no_chat_num.val('');
        $no_chat_num.attr('disabled', 'disabled')
    }else{
        $no_chat_num.val(1);
        $no_chat_num.removeAttr('disabled')
    }
});

$operate_chat_modal.on('show.bs.modal', function () {
  $role_operate_type.val('close_role').change();
});




var chat_row_data;
var operate_chat = function (this_div) {
    var row_obj = $(this_div).closest('tr');
    var row_data = chat_table_obj.row(row_obj).data();
    chat_row_data = row_data;

    $guild_private_chat_modal_body.html(row_data['server_id'] + '区，' + '角色编号为：' +row_data['rid'] + '，将被封号');
    $guild_private_chat_modal.modal('show');

};

$guild_private_chat_modal.click(function () {
    var success_func = function () {
        $guild_private_chat_modal.modal('hide');
        Common.alert_message($error_modal, 1, "操作成功");
        chat_table_obj.ajax.reload(null, false);
    };
    var send_data = {close_id: '', server_id: chat_row_data['server_id'], close_role: chat_row_data['rid'], close_type: 4};

    my_ajax(true, "/operateseal", "get", send_data, false, success_func);
});

var chat_table_obj;
var query_chat = function () {
    var game_id = $select_server_2.val();
    var chat_type = $chat_type.val();
    var start_date = $start_date.val();
    var end_date = $end_date.val();

    var ajax_data = {
        "url": "/chatquery",
        "type": "POST",
        "data": function (d) {
          return {
              draw: d['draw'],
              start: d['start'],
              length: d['length'],
              'server_id': game_id,
              'chat_type': chat_type,
              'start_date': start_date,
              'end_date': end_date
          }
        },
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#guild_private_chat_table_processing').hide();
        }
    };
    var columns = [{"title": "序号", 'data': 'id'}, {"title": "区服", 'data': 'server_id'}, {"title": "角色", 'data': 'rid'},
        {"title":"聊天内容", 'data': 'content'},{"title":"时间", 'data': 'time'}, {"title":"状态", 'data': 'close_status'},
        {"title":"操作"}];
    var columnDefs = [
        {
            "targets": [-2],
            "render": function (data) {
                var t_str = '';
                if (data === 'yes'){
                    t_str = '<span class="badge badge-success">已封号</span>';
                }
                return t_str;

            }
        },
        {
            "targets": [-1],
            "render": function () {
                return '<button class="btn btn-primary btn-sm" onclick="operate_chat(this)" type="button">封号</button>'

            }
        }
    ];
    chat_table_obj = $guild_private_chat_table.DataTable({
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
            leftColumns: 1,
            rightColumns: 2
        },
        "scrollCollapse": false,
        "scrollX": true

   });
    // chat_table_obj = back_page_table($guild_private_chat_table, ajax_data,columns,columnDefs,false);
};

$btn_query_chat.click(function () {
    query_chat()
});