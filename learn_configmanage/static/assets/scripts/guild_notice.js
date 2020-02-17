var $select_server = $('#select_server');
var $president_id = $('#president_id');
var $btn_query_guild = $('#btn_query_guild');
var $btn_modify_inner_guild = $('#btn_modify_inner_guild');
var $btn_modify_out_guild = $('#btn_modify_out_guild');
var $inner_guild_content = $('#inner_guild_content');
var $out_guild_content = $('#out_guild_content');
var $notice_modal = $('#notice_modal');
var $notice_modal_title = $('#notice_modal_title');
var $notice_modal_content = $('#notice_modal_content');
var $commit_modify = $('#commit_modify');
var $modal_prompt = $('#modal_prompt');
var $query_notice_tab = $('#query_notice_tab');

var $guild_list_table =$('#guild_list_table');
var $operate_guild_modal = $('#operate_guild_modal');
var $operate_guild_modal_title = $('#operate_guild_modal_title');
var $operate_guild_modal_body = $('#operate_guild_modal_body');
var $btn_confirm_guild_modify = $('#btn_confirm_guild_modify');

getGameServerData($select_server, 1);



$president_id.bind('input propertychange', function () {
    var input_value = $president_id.val();
    if (input_value.length > 0 && $.isNumeric(input_value)){
        $btn_query_guild.removeAttr('disabled');
    }else{
        $btn_query_guild.attr('disabled', 'disabled');
    }

});

var inner_guild_content = '';
var out_guild_content = '';
var g_role_id = '';
var g_game_id = '';
$btn_query_guild.click(function () {
    g_game_id = $select_server.val();
    g_role_id = $president_id.val();
    var send_data = {'game_id': g_game_id, 'role_id': g_role_id, 'query_type': 'single'};
    my_ajax(true, '/operate/guild/notice', "get", send_data, false, function (result) {
        if (result['status'] === 'ok'){
            if (result['data'] === null || result['data'].length === 0){
                $inner_guild_content.html('没有内容');
                $out_guild_content.html('没有内容');

                $btn_modify_inner_guild.attr('disabled', 'disabled');
                $btn_modify_out_guild.attr('disabled', 'disabled');
            }else{
                var inner_temp = result['data'][0]['content1'];
                var out_temp = result['data'][0]['content2'];
                if (inner_temp === null){
                    inner_guild_content = '';
                    $inner_guild_content.html('没有内容');
                }else{
                    inner_guild_content = inner_temp;
                    $inner_guild_content.html(inner_temp);
                }
                if (out_temp === null){
                    out_guild_content = '';
                    $out_guild_content.html('没有内容');
                }else{
                    out_guild_content = out_temp;
                    $out_guild_content.html(out_temp);
                }

                $btn_modify_inner_guild.removeAttr('disabled');
                $btn_modify_out_guild.removeAttr('disabled');

            }
        }else{
            $inner_guild_content.html('没有内容');
            $out_guild_content.html('没有内容');

            $btn_modify_inner_guild.attr('disabled', 'disabled');
            $btn_modify_out_guild.attr('disabled', 'disabled');
        }
        console.log(result);
    });

});

var modify_type = '';
$btn_modify_inner_guild.click(function () {
    $notice_modal_title.html('修改内部公告（公会会长ID为：'+g_role_id+'）');
    $notice_modal_content.val(inner_guild_content);
    modify_type = 'inner';
    $notice_modal.modal('show');
});

$btn_modify_out_guild.click(function () {
    $notice_modal_title.html('修改外部公告（公会会长ID为：'+g_role_id+'）');
    $notice_modal_content.val(out_guild_content);
    modify_type = 'out';
    $notice_modal.modal('show');

});


$notice_modal.on('hide.bs.modal', function () {
  $modal_prompt.hide();
  modify_type = '';
});

var $error_modal = $('#error_modal');
$commit_modify.click(function () {
    var temp_content = $notice_modal_content.val();
    if (temp_content.length > 0){
        var send_date = '';
        if ( modify_type === 'inner' && temp_content !== inner_guild_content){
            send_date = {'game_id': g_game_id, 'role_id': g_role_id, 'type': modify_type, 'content': temp_content};
            my_ajax(true, '/operate/guild/notice', "post", send_date, false, function (result) {
                $notice_modal.modal('hide');
                Common.alert_message($error_modal, 1, "操作成功");
                $btn_query_guild.click();

            });
        }else if (modify_type === 'out' && temp_content !== out_guild_content){
            send_date = {'game_id': g_game_id, 'role_id': g_role_id, 'type': modify_type, 'content': temp_content};
            my_ajax(true, '/operate/guild/notice', "post", send_date, false, function (result) {
                $notice_modal.modal('hide');
                Common.alert_message($error_modal, 1, "操作成功");
                $btn_query_guild.click();
            });
        }else{
            $modal_prompt.text('异常');
            $modal_prompt.show();
        }
    }else{
        $modal_prompt.text('错误：内容不能为空');
        $modal_prompt.show();
    }


});



var guild_list_table_obj;
var get_guild_list = function () {
    "use strict";
     var columns = [{"title": "序号",'data':'guild_id'},{"title": "公会名",'data':'name'},
        {"title": "等级",'data':'level'},{"title":"区服",'data':'game_id'},{"title":"会长id",'data':'rid'},
         {"title":"会长vip",'data':'vip'},{"title": "副会长",'data':'rid1'},
        {"title": "内部公告",'data':'content1'}, {"title": "外部公告",'data':'content2'},
         {"title": "创建时间",'data':'time'}, {"title":"解散次数",'data':'num'}, {"title":"操作",'data':'gid'}

    ];
    var columnDefs = [
        {
            "targets": [6],
            "render": function (data,type,row) {
                var r_str = '';
                var h_list = [data, row['rid2'], row['rid3']];
                for (var i=0;i<h_list.length;i++){
                    if (Number(h_list[i]) > 0){
                        if (r_str.length>0){
                            r_str += ',' + h_list[i];
                        }else{
                            r_str += h_list[i];
                        }
                    }
                }
                return r_str;

            }
        },
        {
            "targets": [-2],
            "render": function (data) {
                var t_str = data;
                if (data > 0){
                    t_str = '<span class="badge badge-success">'+data+'</span>';
                }
                return t_str;
            }
        },
        {
            "targets": [-1],
            "render": function () {
                return '<button class="btn btn-danger btn-sm" onclick="operate_guild(this, \'dissolution\')" type="button">解散</button>&nbsp;&nbsp;' +
                    '<button class="btn btn-primary btn-sm" onclick="operate_guild(this, \'close_user\')" type="button">封号</button>&nbsp;&nbsp;' +
                        '<button class="btn btn-success btn-sm" onclick="operate_guild(this, \'modify_notice\')" type="button">修改公告</button>';

            }
        }
    ];

    var ajax_data = {
        "url": "/operate/guild/notice",
        "type": "get",
        'data': function (d) {
            var send_data = {};
            send_data['start'] = d['start'];
            send_data['length'] = d['length'];
            send_data['draw'] = d['draw'];
            send_data['query_type'] = 'all';
            send_data['search'] = d['search']['value'];
            return send_data;
        },
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#guild_list_table_processing').hide();
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
    var temp_txt = oLanguage;
    temp_txt['sSearch'] = '区服搜索';
    guild_list_table_obj = $guild_list_table.DataTable({
        "destroy" : false,
        'serverSide': true,
        "autoWidth" : true,
        "processing" : true,
        "ajax": ajax_data,
        "searching": true,    //去掉搜索框方法三：这种方法可以
        "lengthChange": true,
        "paging": true,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : false,
        "oLanguage" : temp_txt,
        fixedColumns: {
            leftColumns: 1,
            rightColumns: 2
        },
        "scrollCollapse": false,
        "scrollX": true

   });



};

var init_guild_list = function () {
    "use strict";
    if (guild_list_table_obj === undefined){
        get_guild_list();
    }else{
        guild_list_table_obj.ajax.reload(null, false);
    }
};

var operate_guild_row_data;
var operate_guild  = function (this_div, o_type) {
    "use strict";
    var row_obj = $(this_div).closest('tr');
    var row_data = guild_list_table_obj.row(row_obj).data();
    operate_guild_row_data = row_data;
    if (o_type === 'dissolution'){
        $operate_guild_modal_title.html('解散公会');
        $operate_guild_modal_body.html('<p>区服：'+row_data['game_id']+'</p><p>会长标识：'+row_data['rid']+'</p>' +
            '<p>公会名称：'+row_data['name']+'</p>');
        $btn_confirm_guild_modify.attr('o_type', 'dissolution');
        $operate_guild_modal.modal('show');
    }else if (o_type === 'modify_notice'){
        $query_notice_tab.click();
        $select_server.val(row_data['game_id']);
        $president_id.val(row_data['rid']);
        $btn_query_guild.removeAttr('disabled');
        $btn_query_guild.click();
    }else{
        $operate_guild_modal_title.html('封号');
        $operate_guild_modal_body.html('<p>区服：'+row_data['game_id']+'</p><p>会长标识：'+row_data['rid']+'</p>' +
            '<p>公会名称：'+row_data['name']+'</p>');
        $btn_confirm_guild_modify.attr('o_type', 'close_user');
        $operate_guild_modal.modal('show');
    }


};

$btn_confirm_guild_modify.click(function () {
    'use strict';
    var o_type = $(this).attr('o_type');
    var o_url;
    var send_data;
    var request_method;
    if (o_type === 'dissolution'){
        o_url = '/put/player/status';
        request_method = 'post';
        send_data = {tag: 'drop_guild', server_id: operate_guild_row_data['game_id'], 'president_id': operate_guild_row_data['rid']};

    }else{
        o_url = '/operateseal';
        request_method = 'get';
        send_data = {'server_id': operate_guild_row_data['game_id'], 'close_role': operate_guild_row_data['rid'], 'close_type': 4, 'close_id': ''};
    }

    var success_func = function(result){
        if (result['status'] === 'success'){
            $operate_guild_modal.modal('hide');
            Common.alert_message($error_modal, 1, "操作成功");
            if (o_type === 'dissolution'){
                guild_list_table_obj.ajax.reload(null, false);
            }
        }else{
            $operate_guild_modal.modal('hide');
            Common.alert_message($error_modal, 0, "操作失败");
        }
    };
    my_ajax(true, o_url, request_method, send_data, false, success_func);

});
