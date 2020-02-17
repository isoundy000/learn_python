/**
 * Created by wangrui on 2017/8/14.
 */

get_left_game_server();
setLeftStyle();

var $select_server = $("#select_server");
var $select_server2 = $("#select_server2");
var $in_select_server = $("#in_select_server");
var $in_select_server2 = $("#in_select_server2");

getGameServerData($select_server, 2);
getGameServerData($select_server2, 1);
getGameServerData($in_select_server, 2);
getGameServerData($in_select_server2, 1);



create_del_modal($("#pick_role_del_modal"), "是否删除角色导出信息?", "confirm_del");

$("#role_out_add").on("click", function (e) {
   e.preventDefault();
   $("#role_id").val("");
   $("#pick_role_out_modal").modal("show");
});


var pickRoleOutValidation = function () {
    var pick_form = $('#pick_role_out_form');
    var validate_data = {
        role_id: {
            required: true,
            digits:true
        }
    };
    var messages_data = {
        role_id: {
            required: "请输入角色ID",
            digits: "请输入数字"
        }
    };
    var submit_method = function() {
        var success = function(data){
            $("#pick_role_out_modal").modal("hide");
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "添加失败");
            }
            else if (data["status"] == "exists"){
                Common.alert_message($("#error_modal"), 0, "导出数据已存在");
            }
            getPickRoleOutData();
        };
        var data = pick_form.serialize();
        my_ajax(true, '/pick/add', 'get', data, true, success);
    };
    commonValidation(pick_form, validate_data, messages_data, submit_method);
};
pickRoleOutValidation();


var getPickRoleOutData = function(){
    var sAjaxSource = "/pick/queryout";
    var aoColumns = [{
        "mDataProp": "id",
        'sClass': 'center',
        "bVisible": false
    },
        {
        "mDataProp": "gid",
        'sClass': 'center',
        "sTitle": "区服"
    },
        {
        "mDataProp": "rid",
        'sClass': 'center',
        "sTitle": "角色编号"
    },
        {
        "mDataProp": "role_name",
        'sClass': 'center',
        "sTitle": "角色名称"
    },
        {
        "mDataProp": "json_path",
        'sClass': 'center',
        "sTitle": "文件路径"
    },

        {
        "mDataProp": "json_url",
        'sClass': 'center',
        "bVisible": false
    },
        {
        "mDataProp": "otime",
        'sClass': 'center',
        "sTitle": "时间"
    },
        {
        "sTitle": "操作",
        "sClass": "center",
        "sDefaultContent": ""
    }];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = '<span class="badge badge-danger">' + aData.gid + "</span>" + "区:";
        if (GAME_SERVER_DICT.hasOwnProperty(aData.gid)) {
            str_html1 += GAME_SERVER_DICT[aData.gid]["name"];
        }

        $('td:eq(0)', nRow).html(str_html1);
        var str_html2 = "";
        str_html2 += "<a download target=\"_blank\" class=\"btn btn-xs blue-madison\" href=\""
            + aData.json_url + "\">下载</a>&nbsp;&nbsp;&nbsp;<button onclick=\"p_delete(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>";
        $('td:eq(5)', nRow).html(str_html2);
        return nRow;
    };
    var data = {
        server_id: $select_server.val()
    };

    dataTablePage($("#pick_role_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
};



$select_server.on("change", function (e) {
    e.preventDefault();
    getPickRoleOutData();
});
$select_server.change();


var p_delete = function(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#pick_role_table").dataTable().fnGetData(nRoW);
    $("#pick_role_del_modal").modal("show");
    $("#confirm_del").attr('onclick', "confirm_del(" + data["id"] + ")");
};

var confirm_del = function(id){
    var success = function(data){
        $("#pick_role_del_modal").modal("hide");
        if (data["status"] == "fail")
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        getPickRoleOutData();
    };
    var data = {did: id};
    my_ajax(true, '/pick/delete', 'get', data, true, success);
};


$("#role_in_add").on("click", function (e) {
    e.preventDefault();
    $("#pick_role_in_modal").modal("show");
});

var getPickRoleIn = function () {
    var sAjaxSource = "/pick/queryin";
    var aoColumns = [{
        "mDataProp": "id",
        'sClass': 'center',
        "bVisible": false
    },
        {
        "mDataProp": "gid",
        'sClass': 'center',
        "sTitle": "区服"
    },
        {
        "mDataProp": "new_rid",
        'sClass': 'center',
        "sTitle": "新角色编号"
    },
        {
        "mDataProp": "to_rid",
        'sClass': 'center',
        "sTitle": "转角色编号"
    },
        {
        "mDataProp": "json_path",
        'sClass': 'center',
        "sTitle": "文件路径"
    },
         {
        "mDataProp": "otime",
        'sClass': 'center',
        "sTitle": "迁入时间"
    },
        {
        "mDataProp": "otime2",
        'sClass': 'center',
        "sTitle": "转角色时间"
    },

        {
        "sTitle": "操作",
        "sClass": "center",
        "sDefaultContent": ""
    }];
    var fnRowCallback = function (nRow, aData) {
        var str_html1 = '<span class="badge badge-danger">' + aData.gid + "</span>" + "区:"
        if (GAME_SERVER_DICT.hasOwnProperty(aData.gid)) {
            str_html1 += GAME_SERVER_DICT[aData.gid]["name"];
        }
        $('td:eq(0)', nRow).html(str_html1);
        var str_html2 = "";
        str_html2 += "<button onclick=\"change_role(this)\" class=\"btn default btn-xs green-haze\" data-toggle=\"modal\">转角色</button>"
        $('td:eq(6)', nRow).html(str_html2);
        return nRow;
    };
    var data = {
        server_id: $in_select_server.val()
    };

    dataTablePage($("#pick_role_in_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
};


var change_role = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#pick_role_in_table").dataTable().fnGetData(nRoW);
    $("#pick_role_in_id").val(data["id"]);
    $("#pick_role_in_change_modal").modal("show");
};


$in_select_server.on('change', function (e) {
    e.preventDefault();
    getPickRoleIn();
});


$("#a_pick_in").on("click", function (e) {
    e.preventDefault();
    $in_select_server.change();
});


var choose_div = $("#choose_div").html();
$("#btn_upload").on("click", function (e) {
    e.preventDefault();
    $("#pick_role_in_modal").modal("hide");
    App.blockUI($page_content, false);
    $.ajaxFileUpload(
        {
            url: "/pick/upload",
            secureuri: false,
            type: "post",
            fileElementId: 'pick_in_file',
            data: {
                server_id: $("#in_select_server2").val()
            },
            dataType: 'json',
            success: function (data, status) {
                App.unblockUI($page_content);
                if (data["status"] == "fail"){
                    Common.alert_message($("#error_modal"), 0, "处理失败.");
                }
                $("#choose_div").empty();
                $("#choose_div").html(choose_div);
                getPickRoleIn();
            },
            error: function (data, status, e) {
                App.unblockUI($page_content);
                error_func();
            }
        }
    );
});


var pickRoleChangeValidation = function () {
    var pick_form = $('#pick_role_change_form');
    var validate_data = {
        change_id: {
            required: true,
            digits:true
        }
    };
    var messages_data = {
        change_id: {
            required: "请输入角色ID",
            digits: "请输入数字"
        }
    };
    var submit_method = function() {
        var success = function(data){
            $("#pick_role_in_change_modal").modal("hide");
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "添加失败");
            }
            else if (data["status"] == "exists"){
                Common.alert_message($("#error_modal"), 0, "角色不存在");
            }
            getPickRoleIn();
        };
        var data = pick_form.serialize();
        my_ajax(true, '/pick/change', 'get', data, true, success);
    };
    commonValidation(pick_form, validate_data, messages_data, submit_method);
};
pickRoleChangeValidation();
