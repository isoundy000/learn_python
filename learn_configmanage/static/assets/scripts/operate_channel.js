/**
 * Created by wangrui on 14/12/11.
 */
get_left_game_server();
setLeftStyle();


var $partner_table = $('#partner_table');
var $partner_name = $('#partner_name');
var $btn_confirm_channel_change = $('#btn_confirm_channel_change');



var channel_table_obj;
var operate_channel_id;
var getPartnerData = function () {
    "use strict";
    var ajax_data = {
        "url": "/getpartner",
        "type": "get",
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#partner_table_processing').hide();
        },
        "dataSrc": function (result) {
            return result;

        }
    };
    var columns = [{"title": "序号",'data':'id'}, {"title": "名称",'data':'name'},{"title":"初始渠道名",'data':'alias'},
        {"title":"折扣",'data':'discount'}, {"title":"描述",'data':'desc'},
        {"title":"操作",'data':'total'}];
    var columnDefs = [
        {
            "targets": -2,
            "visible": false
        },
        {
            "targets": -1,
            "render": function (data) {
                return '<button onclick=\"modify(this)\" class=\"btn default btn-xs \" data-toggle=\"modal\"> <i class=\"fa fa-edit\"></i></button>';
            }
        }
    ];
    channel_table_obj = new_front_page_table($partner_table, ajax_data, columns,columnDefs,false);
};

getPartnerData();

var modify = function(this_div){
    "use strict";
    var row_div = $(this_div).closest('tr');
    var data = channel_table_obj.row( row_div ).data();
    operate_channel_id = data["id"];
    $("#partner_nname").val(data["alias"]);
    $("#partner_name").val(data["name"]);
    $("#discount").val(data["discount"]);
    $("#partner_desc").val(data["desc"]);
    $("#partner_modal").modal("show");
};


$btn_confirm_channel_change.click(function () {
   "use strict";
   var channel_name = $partner_name.val();
   channel_name = $.trim(channel_name);
   if (channel_name.length>0){
        var partner_nname = $("#partner_nname").val();
        var partner_name = $("#partner_name").val();
        var partner_desc = $("#partner_desc").val();
        var discount = $("#discount").val();
        var success = function(data){
            $("#partner_modal").modal("hide");
            if (data["status"] === 0) {
                Common.alert_message($("#error_modal"), 0, "编码重复,请重新输入.");
            } else if (data["status"] === 2) {
                Common.alert_message($("#error_modal"), 0, "操作数据库失败.");
            } else {
                channel_table_obj.ajax.reload(null, false);
            }
        };
        var data = {
            partner_id: operate_channel_id,
            partner_name: partner_name,
            partner_nname: partner_nname,
            discount: discount,
            partner_desc: partner_desc
        };
        my_ajax(true, '/operate_partner', 'get', data, true, success);
   }else{
       alert('名称不能为空');
   }
});

