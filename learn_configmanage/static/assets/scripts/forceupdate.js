/**
 * Created by wangrui on 14/12/11.
 */
create_del_modal($("#channel_force_del_modal"), "是否删除渠道强更信息?", "confirm_del");
var $channel_force_modal = $("#channel_force_modal");


$("#force_add").bind("click", function(e){
    e.preventDefault();
    $("#channel_id").val("");
    $("#channel_cn_name").val("");
    $("#channel_name").val("");
    $("#version").val("");
    $("#url").val("");
    $("#force_desc").val("");
    $channel_force_modal.modal("show");
});

var channelForceValidation = function () {
    var partner_form = $('#channel_force_form');
    var validate_data = {
        channel_cn_name: {
            required: true
        },
        channel_name: {
            required: true
        },
        version: {
            required: true
        },
        url: {
            required: true
        }
    };
    var messages_data = {
        channel_cn_name: {
            required: "请输入名称"
        },
        channel_name: {
            required: "请输入渠道标识"
        },
        version: {
            required: "请输入版本"
        },
        url: {
            required:  "请输入下载地址"
        }
    };
    var submit_method = function() {
        partner_form.serialize();
        var success = function(data){
            $channel_force_modal.modal("hide");
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "添加失败");
            }
            getChannelForceData();
        };
        var data = partner_form.serialize();
        my_ajax(true, '/force/operate', 'get', data, true, success);
    };
    commonValidation(partner_form, validate_data, messages_data, submit_method);
};
channelForceValidation();


var getChannelForceData = function(){
    var sAjaxSource = "/force/query";
    var aoColumns = [{
        "mDataProp": "id",
        'sClass': 'center',
        "bVisible": false
    },
        {
        "mDataProp": "cn_name",
        'sClass': 'center',
        "sTitle": "名称"
    },
        {
        "mDataProp": "name",
        'sClass': 'center',
        "sTitle": "渠道标识"
    },
        {
        "mDataProp": "version",
        'sClass': 'center',
        "sTitle": "版本"
    },
        {
        "mDataProp": "url",
        'sClass': 'center',
        "sTitle": "下载地址"
    },
        {
        "mDataProp": "desc",
        'sClass': 'center',
        "sTitle": "描述"
    },
        {
        "sTitle": "操作",
        "sClass": "center",
        "sDefaultContent": "<button onclick=\"modify(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button><button onclick=\"p_delete(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
    }];

    dataTablePage($("#channel_force_table"), aoColumns, sAjaxSource, {}, false, null);
};
getChannelForceData();

var modify = function(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#channel_force_table").dataTable().fnGetData(nRoW);
    $("#channel_id").val(data["id"]);
    $("#channel_cn_name").val(data["cn_name"]);
    $("#channel_name").val(data["name"]);
    $("#version").val(data["version"]);
    $("#url").val(data["url"]);
    $("#force_desc").val(data["desc"]);
    $channel_force_modal.modal("show");
};

var p_delete = function(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#channel_force_table").dataTable().fnGetData(nRoW);
    $("#channel_force_del_modal").modal("show");
    $("#confirm_del").attr('onclick', "confirm_del(" + data["id"] + ")");
};

var confirm_del = function(id){
    var success = function(data){
        $("#channel_force_del_modal").modal("hide");
        if (data["status"] == "fail")
            Common.alert_message($("#error_modal"), 0, "操作失败.");
        getChannelForceData();
    };
    var data = {channel_id: id};
    my_ajax(true, '/force/delete', 'get', data, true, success);
};
