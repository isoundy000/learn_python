/**
 * Created by wangrui on 15/9/7.
 */
handleDatePickers();



var $start_date  = $("#start_date");
var $end_date = $("#end_date");
var $select_recharge_game = $("#select_recharge_game");
var $select_game1 = $("#select_game1");
var $select_game2 = $("#select_game2");
var $recharge_log_type = $("#recharge_log_type");
var $recharge_ctype = $("#recharge_ctype");
var $recharge_type = $("#recharge_type");
var $role_id_info_1 = $('#role_id_info_1');
var $role_name_info_1 = $('#role_name_info_1');
var $role_id_info_2 = $('#role_id_info_2');
var $role_name_info_2 = $('#role_name_info_2');
var $recharge_mode = $('#recharge_mode');
var $recharge_log_mode =$('#recharge_log_mode');


getGameServerData($select_game1, 1);
getGameServerData($select_game2, 1);
getGameServerData($select_recharge_game, 2);

$start_date.val(getNowFormatDate(7));
$end_date.val(getNowFormatDate(0));

var RECHARGE_TYPE = {
    "test": '测试',
    "order": "补单",
    "recharge": "代充"
};

var RECHARGE_MODE = {
    "0": '游戏福利充值',
    "1": "补单"
};

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


init_select_html(false, RECHARGE_TYPE, $recharge_log_type);
init_select_html(false, RECHARGE_TYPE, $recharge_ctype);
init_select_html(false, RECHARGE_MODE, $recharge_mode);
init_select_html(false, RECHARGE_MODE, $recharge_log_mode);



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


var realRechargeValidation = function () {
    var form1 = $('#real_form');
    var rules = {
        role_info_1: {
            required: true
            // digits: true
        },
        recharge_ctype: {
            required: true
        },
        sim_desc: {
            required: true
        }
    };
    var messages = {
        role_id_info_1: {
            required: "请输入角色信息"
            // digits: "请输入数字"
        },
        recharge_ctype: {
            required: "请选择充值类型"
        },
        sim_desc: {
            required: "请输入充值描述详细信息"
        }
    };
    var submitFunction = function (form) {
        var server_id = $("#select_game1").val();
        var role_id = $role_id_info_1.val();
        var recharge_type1 = $("#recharge_type").val().split("_");
        var recharge_type = recharge_type1[0];
        var recharge_amount = recharge_type1[1];
        var recharge_ctype = $("#recharge_ctype").val();
        var recharge_mode = $recharge_mode.val();
        var sim_desc = $("#sim_desc").val();
        
        var success = function (data) {
            Common.alert_message($("#error_modal"), 1, "充值成功.");
            $role_id_info_1.val("");
            $role_name_info_1.val("");
            // $role_info_1.parent().parent().parent().find('.role_id').removeClass('role_id');
        };
        
        var data = {
            server_id: server_id,
            role_id: role_id,
            recharge_type: recharge_type,
            recharge_amount: recharge_amount,
            recharge_ctype: recharge_ctype,
            sim_desc: sim_desc,
            recharge_mode: recharge_mode
        };
        my_ajax(true, '/rolerecharge', 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitFunction);
};

realRechargeValidation();

var updateRoleValidation = function(){
    var form1 = $("#role_form");
    form1.validate({
        errorElement: 'span',
        errorClass: 'help-block',
        focusInvalid: false,
        ignore: "",
        groups: {
            gold_coin: "add_gold add_coin"
        },
        errorPlacement: function(error, element) {
             if (element.attr("name") == "add_gold" || element.attr("name") == "add_coin" ){
               error.insertAfter("#add_gold");
             }else{
               error.insertAfter(element);
             }
        },
        rules: {
            role_id_info_2: {
                required: true
                // digits: true
            },
            add_gold:{
                required: {
                    depends:function(){ //二选一
                        return ($('input[name=add_coin]').val().length <= 0);
                    }
                }
            },
            add_coin:{
                required: {
                    depends:function(){ //二选一
                        return ($('input[name=add_gold]').val().length <= 0);
                    }
                }
            }
        },
        messages: {
            role_id_info_2: {
                required: "请输入角色名或ID"
                // digits: "请输入数字"
            },
            add_gold: "请输入元宝或者金币.",
            add_coin: "请输入元宝或者金币."
        },

        highlight: function (element) {
            $(element)
                .closest('.form-group').addClass('has-error');
        },

        unhighlight: function (element) {
            $(element)
                .closest('.form-group').removeClass('has-error');
        },

        success: function (label) {
            label
                .closest('.form-group').removeClass('has-error');
        },

        submitHandler: function (form) {
            var server_id = $select_game2.val();
            var role_id = $role_id_info_2.val();
            var add_gold = $("#add_gold").val();
            var add_coin = $("#add_coin").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/addgold',
                    data: {
                        server_id: server_id,
                        role_id: role_id,
                        add_gold: add_gold,
                        add_coin: add_coin
                    },
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI($('.page-content'));
                        if (data.status == "fail") {
                            Common.alert_message($("#error_modal"), 0, "模拟充值失败.");
                        }
                        else{
                            Common.alert_message($("#error_modal"), 1, "模拟充值成功.");
                        }
                        $role_id_info_2.val("");
                        $role_name_info_2.val("");
                        $("#add_gold").val("");
                        $("#add_coin").val("");
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI($('.page-content'));
                        error_func(XMLHttpRequest);
                    }
                }
            )
        }
    });
};
updateRoleValidation();



function query_sim_recharge_log(){
    var sAjaxSource = "/simrecharge/querylog";
    var total = 0;    
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "gid",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "区服"
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色"
        },
        {
            "mDataProp": "mode",
            'sClass': 'center',
            "sTitle": "充值模式"
        },
        {
            "mDataProp": "type",
            'sClass': 'center',
            "sTitle": "配置类型"
        },
        {
            "mDataProp": "cid",
            'sClass': 'center',
            "sTitle": "金额"
        },
        {
            "mDataProp": "user",
            'sClass': 'center',
            "sTitle": "操作者"
        },
        {
            "mDataProp": "rechargetime",
            'sClass': 'center',
            "sTitle": "充值时间"
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "sTitle": "描述"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html = aData.gid + "区:" + aData.name;
        $('td:eq(0)', nRow).html(str_html);
        var str_html2 = RECHARGE_MODE[aData.mode];
        $('td:eq(2)', nRow).html(str_html2);
        var str_html3 = RECHARGE_TYPE[aData.type];
        $('td:eq(3)', nRow).html(str_html3);

        var str_html4 = recharge_data[aData.cid]["rmb"];
        total += recharge_data[aData.cid]["rmb"];
        $('td:eq(4)', nRow).html(str_html4);
    };
    
    var server_id = $select_recharge_game.val();
    var recharge_log_type = $recharge_log_type.val();
    var recharge_log_mode = $recharge_log_mode.val();
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    
    var data = {
        server_id: server_id,
        log_type: recharge_log_type,
        log_mode: recharge_log_mode,
        start_date: start_date,
        end_date: end_date
    };
    dataTablePage($("#recharge_log_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
    $("#total_recharge").html("总金额:" + total);
}


$("#a_recharge_log").on("click", function(e){
    e.preventDefault();
    query_sim_recharge_log();
});


$select_recharge_game.on("change", function (e) {
    e.preventDefault();
    query_sim_recharge_log();
});


$recharge_log_type.on("change", function(e){
    e.preventDefault();
    query_sim_recharge_log();
});

$recharge_log_mode.on("change", function(e){
    e.preventDefault();
    query_sim_recharge_log();
});


$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_sim_recharge_log();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_sim_recharge_log();
});


var query_role_info = function (this_div, other_div, server_div, role_type) {
    var success = function (data) {
        if (data){
            if (role_type === 'role_id'){
                other_div.val(data['name']);
            }else if(role_type === 'role_name'){
                other_div.val(data['id']);
            }else{
                other_div.val('');
            }
        }else{
            other_div.val('')
        }
    };
    var server_id = server_div.val();
    var role_search = this_div.val();
    var data = {role_type: role_type, role_search: role_search, server_id: server_id};
    if (role_search.length > 0){
        my_ajax(true, "/getroleinfo", 'get', data, true, success);
    }else{
        other_div.val('')
    }
};


// $role_info_1.bind("input propertychange",function () {
//     var this_div = $(this);
//     query_role_info(this_div, $select_game1)
// });
// $role_info_2.bind("input propertychange",function () {
//     var this_div = $(this);
//     query_role_info(this_div, $select_game2)
// });

// $role_id_info_1.bind("blur",function () {
//     var this_div = $(this);
//     query_role_info(this_div, $select_game1)
// });
// $role_info_2.bind("blur",function () {
//     var this_div = $(this);
//     query_role_info(this_div, $select_game2)
// });

// var explain_common = function (this_div) {
//     var role_explain_type = this_div.val();
//     this_div.parent().next().find('.role_id').removeClass('role_id');
//     if (role_explain_type === '角色ID'){
//         this_div.parent().next().find('.role_info_left').attr({'placeholder':'输入角色ID','data-role':'role_id'});
//         this_div.parent().next().find('.role_info_left').addClass('role_id');
//     }else if (role_explain_type === '角色名'){
//         this_div.parent().next().find('.role_info_left').attr({'placeholder':'输入角色名','data-role':'role_name'});
//         this_div.parent().next().find('.role_info_right').addClass('role_id');
//     }
// };

// $('#role_explain_1').bind('change', function () {
//     var this_div = $(this);
//     explain_common(this_div);
//     query_role_info($role_info_1, $select_game1)
// });
//
// $('#role_explain_2').bind('change', function () {
//     var this_div = $(this);
//     explain_common(this_div);
//     query_role_info($role_info_2, $select_game2)
// });

$select_game1.bind('change', function () {
    var div_1 = $('#role_info_1').find('.current_input');
    var role_type = (div_1.attr('placeholder') === '角色名') ? 'role_name' : 'role_id';
    query_role_info(div_1, div_1.parent().siblings().find('input'), $select_game1, role_type)
});
$select_game2.bind('change', function () {
    var div_1 = $('#role_info_2').find('.current_input');
    var role_type = (div_1.attr('placeholder') === '角色名') ? 'role_name' : 'role_id';
    query_role_info(div_1, div_1.parent().siblings().find('input'), $select_game2, role_type)
});

$role_id_info_1.bind("blur",function () {
        var inner_this_div = $(this);
        query_role_info(inner_this_div, $role_name_info_1, $select_game1, 'role_id')
});
$role_name_info_1.bind("blur",function () {
        var inner_this_div = $(this);
        query_role_info(inner_this_div, $role_id_info_1, $select_game1, 'role_name')
});
$role_id_info_2.bind("blur",function () {
        var inner_this_div = $(this);
        query_role_info(inner_this_div, $role_name_info_2, $select_game2, 'role_id')
});
$role_name_info_2.bind("blur",function () {
        var inner_this_div = $(this);
        query_role_info(inner_this_div, $role_id_info_2, $select_game2, 'role_name')
});
var role_query_common = function (this_div, other_div) {
    other_div.removeClass('current_input');
    this_div.addClass('current_input');
    this_div.val('');
    this_div.removeAttr('readonly');
    other_div.val('');
    other_div.attr('readonly',"readonly");
};

$role_id_info_1.click(function () {
    role_query_common($(this), $role_name_info_1);
});

$role_name_info_1.click(function () {
    role_query_common($(this), $role_id_info_1);
});
$role_id_info_2.click(function () {
   role_query_common($(this), $role_name_info_2);
});
$role_name_info_2.click(function () {
    role_query_common($(this), $role_id_info_2);
});



$('#btn_down_data').click(function () {
    App.blockUI($page_content, false);
    var server_id = $select_recharge_game.val();
    var recharge_log_type = $recharge_log_type.val();
    var recharge_log_mode = $recharge_log_mode.val();
    var start_date = $start_date.val();
    var end_date = $end_date.val();

    var data = {
        server_id: server_id,
        log_type: recharge_log_type,
        log_mode: recharge_log_mode,
        start_date: start_date,
        end_date: end_date
    };

    $.ajax({
        url: '/simrecharge/download_file',
        type: 'get',
        dataType:'json',
        data: data,
        success: function (result) {
            App.unblockUI($page_content);
            if (result['status'] === 'success'){
                 window.location=result["url"];
            }else if (result['status'] ==='data_empty'){
                alert('当前条件，没有数据');
            }else{
                alert('处理失败');
            }
        },
        error: function () {
            alert('处理失败, error');
            App.unblockUI($page_content);
        }
    });

});
