/**
 * Created by wangrui on 14/12/11.
 */
display_left_filter();
create_del_modal($("#partner_del_modal"), "是否删除此渠道信息?", "confirm_del_partner");

$("#partner_add").bind("click", function(e){
    e.preventDefault();
    $("#partner_id").val("");
    $("#partner_nname").val("");
    $("#partner_name").val("");
    $("#partner_desc").val("");
    $("#partner_modal").modal("show");
});

var partnerValidation = function () {
    var partner_form = $('#partner_form');
    var validate_data = {
        partner_nname: {
            required: true
        },
        partner_name: {
            required: true
        },
        discount: {
            required: true
        }
    };
    var messages_data = {
        partner_nname: {
            required: "请输入渠道标识"
        },
        partner_name: {
            required: "请输入名称."
        },
        discount: {
            required: "请输入折扣"
        }
    };
    var submit_method = function() {
        var partner_id = $("#partner_id").val();
        var partner_nname = $("#partner_nname").val();
        var partner_name = $("#partner_name").val();
        var partner_desc = $("#partner_desc").val();
        var discount = $("#discount").val();
        var success = function(data){
            $("#partner_modal").modal("hide");
            if (data["status"] == 0) {
                Common.alert_message($("#error_modal"), 0, "编码重复,请重新输入.");
            } else if (data["status"] == 2) {
                Common.alert_message($("#error_modal"), 0, "操作数据库失败.");
            } else {
                getPartnerData();
            }
        };
        var data = {
            partner_id: partner_id,
            partner_name: partner_name,
            partner_nname: partner_nname,
            discount: discount,
            partner_desc: partner_desc
        };
        my_ajax(true, '/operate_partner', 'get', data, true, success);
    };
    commonValidation(partner_form, validate_data, messages_data, submit_method);
};
partnerValidation();


var getPartnerData = function(){
    var sAjaxSource = "/query_partner";
    var aoColumns = [{
        "mDataProp": "id",
        'sClass': 'center',
        "bVisible": false
    }, {
        "mDataProp": "name",
        'sClass': 'center',
        "sTitle": "名称"
    }, {
        "mDataProp": "alias",
        'sClass': 'center',
        "sTitle": "别名"
    }, {
        "mDataProp": "discount",
        'sClass': 'center',
        "sTitle": "折扣"
    }, {
        "mDataProp": "desc",
        'sClass': 'center',
        "sTitle": "描述"
    }, {
        "sTitle": "操作",
        "sClass": "center",
        "sDefaultContent": "<button onclick=\"modify(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button><button onclick=\"p_delete(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\"> <i class=\"fa fa-trash-o\"></i></button>"
    }];

    dataTablePage($("#partner_table"), aoColumns, sAjaxSource, {}, false, null);
};
getPartnerData();

var modify = function(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#partner_table").dataTable().fnGetData(nRoW);
    $("#partner_id").val(data["id"]);
    $("#partner_nname").val(data["alias"]);
    $("#partner_name").val(data["name"]);
    $("#discount").val(data["discount"]);
    $("#partner_desc").val(data["desc"]);
    $("#partner_modal").modal("show");
};

var p_delete = function(s){
    var nRoW = $(s).parents('tr')[0];
    var data = $("#partner_table").dataTable().fnGetData(nRoW);
    $("#partner_del_modal").modal("show");
    $("#confirm_del_partner").attr('onclick', "confirm_del(" + data["id"] + ")");
};

var confirm_del = function(id){
    var success = function(data){
        if (data["status"] < 0) {
            Common.alert_message($("#error_modal"), 0, "操作失败.")
        } else {
            $("#partner_del_modal").modal("hide");
            getPartnerData();
        }
    };
    var data = {id: id};
    my_ajax(true, '/delete_partner', 'get', data, true, success);
};
