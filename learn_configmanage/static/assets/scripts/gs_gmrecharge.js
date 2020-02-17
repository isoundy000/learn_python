var $recharge_table = $('#recharge_table');
var $user_table = $('#user_table');
var $confirm_add_user = $('#confirm_add_user');
var $user_uid = $('#user_uid');
var $add_recharge_row = $('#add_recharge_row');

var $select_uid = $('#select_uid');
var $select_server = $('#select_server');
var $role_id = $('#role_id');
var $role_name = $('#role_name');
var $recharge_type = $('#recharge_type');
var $confirm_add_recharge = $('#confirm_add_recharge');
var $recharge_num = $('#recharge_num');
var $add_recharge_row_title = $('#add_recharge_row_title');

var $confirm_recharge_modal = $('#confirm_recharge_modal');
var $btn_confirm_recharge = $('#btn_confirm_recharge');
var $recharge_description = $('#recharge_description');

var $select_uid_log = $('#select_uid_log');
var $start_date = $('#start_date');
var $end_date = $('#end_date');
var $recharge_log_table = $('#recharge_log_table');
var $total_recharge = $('#total_recharge');


handleDatePickers();
$start_date.val(getNowFormatDate(7));
$end_date.val(getNowFormatDate(0));
$.fn.modal.Constructor.prototype.enforceFocus = function () { };


$.ajax({
   'url': '/gs_recharge/init/uid_rid_rel',
    'type': 'post'
});


var query_json_data = function(server_id, config_data){
    var json_data = null;
    var success = function(data){
        json_data = data;
    };
    var req_data = {
        server_id: server_id,
        type: JSON.stringify(config_data)
    };

    my_ajax(true, "/queryjsondatabyserver", 'get', req_data, false, success);
    return json_data;
};

var config_data = ["recharge"];
var recharge_data = query_json_data(1, config_data)["recharge"];


function init_recharge_type_option(){
    var str_html = "";
    for (var d in recharge_data) {
        if (recharge_data[d].hasOwnProperty("name")){
            str_html += "<option value='" + d + "_" + recharge_data[d]["rmb"] +  "'>" + recharge_data[d]["name"] + "</option>";
        }else{
            str_html += "<option value='" + d + "_" + recharge_data[d]["rmb"] +  "'>" + recharge_data[d]["name_CN"] + "</option>";
        }
    }

    $recharge_type.html(str_html);
}
init_recharge_type_option();


var total_uid_rid_rel;
var total_recharge_data = [['','','','','','','', '']];
var recharge_table_obj;
var total_recharge_type;


$select_uid.change(function () {
    "use strict";
    $role_id.html('');
    $role_name.val('');
    $select_server.html('');
    $.ajax({
       url: '/gs_recharge/get/uid_rid_rel',
        data: {'uid': $select_uid.val()},
        dataType: 'json',
        success: function (result) {
           total_uid_rid_rel = {};
           var str_html = "";
           var temp_data;
           for(var i=0;i<result.length;i++){
               if (!(result[i]['gid'] in total_uid_rid_rel)){
                   if (i === 0){
                       temp_data = result[i]['gid'];
                   }
                   total_uid_rid_rel[result[i]['gid']] = [];
                   str_html += "<option value='" + result[i]['gid'] +  "'>" + result[i]['gid'] + "区:"+result[i]['game_name'] +"</option>";
               }
               total_uid_rid_rel[result[i]['gid']].push([result[i]['rid'], result[i]['r_name']]);
           }
            $select_server.html(str_html);
            $select_server.val(temp_data).trigger('change');
        }
    });
});

var modal_role_name = {};
$select_server.change(function () {
    "use strict";
    $role_id.html('');
    $role_name.val('');
    var s_gid = parseInt($select_server.val());
    if (s_gid in total_uid_rid_rel && total_uid_rid_rel[s_gid].length>0){
        console.log(total_uid_rid_rel[s_gid]);
        var i_str = '';
        for(var i=0;i<total_uid_rid_rel[s_gid].length;i++){
            i_str += '<option value="'+total_uid_rid_rel[s_gid][i][0]+'">'+total_uid_rid_rel[s_gid][i][0]+'</option>';
            modal_role_name[total_uid_rid_rel[s_gid][i][0]] = total_uid_rid_rel[s_gid][i][1];
        }
        $role_id.html(i_str);
        $role_name.val(total_uid_rid_rel[s_gid][0][1]);
    }
});

$role_id.change(function () {
    "use strict";
    $role_name.val('');
    var role_name = modal_role_name[$role_id.val()];
    $role_name.val(role_name);

});

var modify_row_obj;
var mod_recharge_info = function (this_div) {
    "use strict";
    $add_recharge_row_title.text('修改充值信息');
    $confirm_add_recharge.text('确认修改');
    total_recharge_type = 'modify';
    modify_row_obj = $(this_div).closest('tr');
    var row_data = recharge_table_obj.row( modify_row_obj ).data();
    $select_uid.val(row_data[0]).select2();
    $select_server.val(row_data[1]).select2();
    $role_id.val(row_data[2]);
    $role_name.val(row_data[3]);
    $recharge_type.val(row_data[5]);
    $recharge_num.val(row_data[6]);
    $add_recharge_row.modal('show');
};
var del_recharge_info = function (this_div) {
    "use strict";
    var row_div = $(this_div).closest('tr');
    total_recharge_data.splice(row_div.index(),1);
    row_div.remove();

};
var empty_recharge_table = function () {
    "use strict";
    total_recharge_data = [['','','','','','','', '']];
    recharge_func();
};

var show_recharge_modal = function () {
    "use strict";
    if (total_recharge_data.length>1){
        $confirm_recharge_modal.modal('show');
    }else{
        alert('错误，充值列表不能为空');
    }
};
var get_uid_data = function () {
    $.ajax({
        url: '/gs_recharge/show_user',
        type: 'get',
        data: {'uid_status': 'checked'},
        dataType: 'json',
        success: function (result) {
            var str_html = "";
            var temp_data;
            for (var d=0;d<result.length;d++) {
                if (d === 0){
                    temp_data = result[d]['uid'];
                }
                str_html += "<option value='" + result[d]['uid'] +  "'>" + result[d]['uid'] + "</option>";
            }
            $select_uid.html(str_html);
            $select_uid.val(temp_data).trigger('change');

            $select_uid_log.html(str_html);
            $select_uid_log.val(temp_data).select2();

        }
    });
};
get_uid_data();


var recharge_func = function () {
    "use strict";
    if (recharge_table_obj !== undefined){
        recharge_table_obj.clear();
    }

    var recharge_length = total_recharge_data.length;
    var columns = [{"title": "账号标识"}, {"title":"区服"},{"title":"角色标识"},{"title":"角色名"}, {"title":"档位"},
        {"title":"cid"}, {"title":"数量"},{"title":"操作"}];
    var columnDefs = [
        {
            "visible": false,
            "targets": 5
        },

        {
            "targets": [-1],
            "render": function () {
                return '<button onclick="mod_recharge_info(this)" class="btn default btn-xs yellow" ' +
                    '>修改 <i class="fa fa-edit"></i></button><button onclick="del_recharge_info(this)" ' +
                    'class="btn default btn-xs red" >删除 <i class="fa fa-trash-o"></i></button>';
            }
        }

    ];

    recharge_table_obj = $recharge_table.DataTable({
        "destroy" : true,
        "data":total_recharge_data,
        "bAutoWidth" : false,
        "bProcessing" : true,
        "bFilter": false,    //去掉搜索框方法三：这种方法可以
        "bLengthChange": false,
        "paging": false,
        "info": false,
        "columns" : columns,
        "aoColumnDefs": columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage,
        "createdRow": function( row, data, dataIndex ) {
            if ( dataIndex === recharge_length-1) {
              $(row).html('<td colspan="8" style="text-align: center"><button type="button" class="btn btn-danger btn-sm" onclick="empty_recharge_table()">清空</button>&nbsp' +
                            '<button type="button" class="btn btn-primary btn-sm" onclick="add_recharge_row()">添加充值</button>&nbsp' +
                            '<button type="button" class="btn btn-success btn-sm" onclick="show_recharge_modal()">充值</button></td>');
            }
          }
    });
};
var add_recharge_row = function () {
    "use strict";
    $add_recharge_row_title.text('增加充值信息');
    $confirm_add_recharge.text('确认增加');
    total_recharge_type = 'add';
    $add_recharge_row.modal('show');
};
$confirm_add_recharge.click(function () {
    var select_uid = $select_uid.val();
    var select_server = $select_server.val();
    var role_id = $role_id.val();
    var role_name= $role_name.val();
    var recharge_type = $recharge_type.find('option:selected').text();
    var recharge_num = $recharge_num.val();

    if (role_id === ''){
        alert('角色ID不能为空');
    }else{
        var new_row_data = [select_uid, select_server, role_id, role_name, recharge_type, $recharge_type.val(), recharge_num, ''];
        if (total_recharge_type === 'modify'){
            var row_div = $(modify_row_obj).closest('tr');
            total_recharge_data.splice(row_div.index(),1, new_row_data);
            row_div.data(new_row_data);
        }else{
            total_recharge_data.unshift(new_row_data);
        }
        $add_recharge_row.modal('hide');

        recharge_func();

    }
});

recharge_func();


$btn_confirm_recharge.click(function () {
    "use strict";
    var recharge_description = $recharge_description.val();
    if (recharge_description.length>0){
        $btn_confirm_recharge.attr('disabled', 'disabled');
        $btn_confirm_recharge.text('充值执行中');
        var recharge_temp_data = [];
        var recharge_value;
        for (var i=0;i<total_recharge_data.length-1;i++){
            recharge_value = total_recharge_data[i][5].split('_');
            recharge_temp_data.push({'uid': total_recharge_data[i][0], 'gid': total_recharge_data[i][1],
                'rid': total_recharge_data[i][2], 'cid': recharge_value[0], 'single_money': recharge_value[1],
                'recharge_num': total_recharge_data[i][6], 'total_money': parseInt(recharge_value[1]) * parseInt(total_recharge_data[i][6])
            });
        }

        $.ajax({
            url: '/gs_recharge/recharge',
            data: {'recharge_data': JSON.stringify(recharge_temp_data), 'recharge_description': recharge_description},
            type: 'post',
            dataType: 'json',
            success: function (result) {
                $confirm_recharge_modal.modal('hide');
                if (result['status'] === 'success'){
                    Common.alert_message($("#error_modal"), 1, "操作成功.");
                    empty_recharge_table();
                }else if (result['status'] === 'abnormal'){
                    Common.alert_message($("#error_modal"), 0, "有"+result['msg']+'笔充值失败');
                }
                else{
                    Common.alert_message($("#error_modal"), 0, "操作失败.");
                }

            },
            error: function () {
                $confirm_recharge_modal.modal('hide');
                Common.alert_message($("#error_modal"), 0, "操作失败.");
            }
        });

    }else{
        alert('错误，充值描述不能为空');
    }
});


$confirm_recharge_modal.on('hide.bs.modal', function () {
    'use strict';
  $btn_confirm_recharge.removeAttr('disabled');
  $btn_confirm_recharge.text('确认充值');
});




var get_gs_recharge_record = function () {
    "use strict";

    var ajax_data = {
        "url": "/gs_recharge/recharge_record",
        "type": "post",
        "data": {'uid': $select_uid_log.val(), 'start_date': $start_date.val(), 'end_date': $end_date.val()},
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#recharge_log_table_processing').hide();
        },
        "dataSrc": function (result) {
            if (result['status'] === 'success'){
                $total_recharge.html('总金额：'+result['total_money']);
                return result.data;
            }else{
                 result.recordsTotal = 0;
                 result.recordsFiltered = 0;
                return [];
            }
        }
    };

    var columns = [{"title": "用户标识", 'data': 'uid'}, {"title": "区服", 'data': 'gid'},{"title": "角色标识", 'data': 'rid'},
        {"title":"操作用户", 'data': 'op_user'},{"title":"操作时间", 'data': 'create_time'},{"title": "单笔金额", 'data': 'single_money'},
        {"title":"数量", 'data': 'recharge_num'}, {"title":"总金额", 'data': 'total_money'}, {"title":"状态", 'data': 'status'}];
    var columnDefs = [
        {
            "targets": [-1],
            "render": function (data) {
                if (data === 'success') {
                    return '<span  class="badge badge-success">成功</span>';
                } else {
                    return '<span  class="badge badge-danger">失败</span>';
                }
            }
        }
    ];


   back_page_table($recharge_log_table, ajax_data,columns, columnDefs,false);
};

$select_uid_log.change(function () {
    get_gs_recharge_record();
});

$start_date.change(function () {
    get_gs_recharge_record();
});

$end_date.change(function () {
    get_gs_recharge_record();
});



var show_user_table_obj;
var show_recharge_user = function () {
    "use strict";

    var ajax_data = {
        "url": "/gs_recharge/show_user",
        "type": "get",
        "dataType": 'json',
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#user_table_processing').hide();
        },
        "dataSrc": function (result) {
            return result;
        }
    };

    var columns = [{"title": "用户标识", 'data': 'uid'}, {"title":"创建用户", 'data': 'c_user'},
        {"title":"创建时间", 'data': 'create_time'},{"title":"状态", 'data': 'checked'}];
    var columnDefs = [
        {
            "targets": [-1],
            "render": function (data) {
                if (data === 'yes') {
                    return '<span  class="badge badge-success">已通过</span>';
                } else if (data === 'refuse'){
                    return '<span  class="badge badge-danger">审核不通过</span>';
                } else{
                    return '<span  class="badge badge-info">待审核</span>';
                }
            }
        }
    ];

   show_user_table_obj = new_front_page_table($user_table, ajax_data,columns,columnDefs,false);
};

$confirm_add_user.click(function () {
    var uid = $user_uid.val();
    if (uid.length>0 && !isNaN(uid)) {
        my_ajax(true, "/gs_recharge/add_user", 'post', {'account': uid}, true, function (result) {
            if (result['status'] === 'success'){
                show_user_table_obj.ajax.reload(null , false);
                $('#add_recharge_user_modal').modal('hide');
            }else{
                alert(result['msg'] );
            }

        });
    }else{
        alert('输入有有误');
    }
});
