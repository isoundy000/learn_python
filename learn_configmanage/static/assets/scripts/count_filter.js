/**
 * Created by wangrui on 15/12/11.
 */
display_left_filter();

create_del_modal($("#filter_delete_modal"), "是否删除此角色?", "confirm_del");
getGameServerData($("#select_server"), 1);

$("#add_filter").on("click", function(e){
    e.preventDefault();
    $("#role_id").val("");
    $("#filter_modal").modal("show");
});

var filterValidation = function () {
    var form1 = $('#filter_form');
    var rules = {
        role_id: {
            required: true,
            digits: true
        }
    };
    var messages = {
        role_id: {
            required: "请输入角色ID",
            digits: "请输入数字"
        }
    };

    var submitHandler = function (form) {
        var success = function(data){
            if (data.status == "fail") {
                show_error_modal(0, "操作失败");
            }
            else if (data.status == "no") {
                show_error_modal(0, "角色不存在,请重新输入.");
            }
            else if(data.status == "exists"){
                show_error_modal(0, "数据已存在,请重新输入.");
            }
            $("#filter_modal").modal("hide");
            getFilter();
        };
        my_ajax(true, '/addfilteruser', 'get', form1.serialize(), true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
filterValidation();

var TAG = false;
var count = 0;
var $set_status = $("#switch_status");

var getFilter = function () {
    var aoColumns = [
        {
            "mDataProp": "uid",
            'sClass': 'center',
            "sTitle": "UID"
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
            "mDataProp": "tag",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"del_filter(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        if (aData.tag == "yes") {
            TAG = true;
        }
        else {
            TAG = false;
        }
        return nRow;
    };
    dataTablePage($("#filter_table"), aoColumns, "/getfilteruser", {}, false, fnRowCallback);

};
getFilter();

if (TAG) {
    $set_status.bootstrapSwitch('toggleState');
    $set_status.bootstrapSwitch('setState', true);
    count += 1;
}
else {
    $set_status.bootstrapSwitch('toggleState');
    $set_status.bootstrapSwitch('setState', false);
    count += 1;
}

function del_filter(s) {
    var nRoW = $(s).parents('tr')[0];
    var data = $("#filter_table").dataTable().fnGetData(nRoW);
    $('#filter_delete_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_filter(" + data["uid"] + "," + data["gid"] + ")");
}

function confirm_del_filter(uid, gid) {
    var data = {
        uid: uid,
        gid: gid
    };
    var success = function(data){
        if (data.status == "fail") {
            show_error_modal(0, "设置失败");
        }
        getFilter();
    };
    my_ajax(true, "/deletefilter", "get", data, true, success);
}


$('#switch_status').on('switch-change', function (e, data) {
    var $el = $(data.el)
      , value = data.value;
    e.preventDefault();

    var success = function(data){
        if (data.status == "fail") {
            show_error_modal(0, "设置失败");
        }
        getFilter();
    };
    if (count != 0) {
        var my_tag = "";
        if (value) {
            my_tag = "yes";
        }
        else {
            my_tag = "no";
        }
        var data1 = {
            tag: my_tag
        };
        my_ajax(true, '/setfiltertag', "get", data1, true, success);
    }
});
