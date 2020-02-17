var title = '';
var PLATFORM_NAME = '';
var PLATFORM_TYPE = '';

$.ajax({
    url: '/get/web_info',
    async: false,
    success:function (result) {
        title = result['data']['title'];
        PLATFORM_NAME = result['data']['platform_name'];
        PLATFORM_TYPE = result['data']['platform_group'];
    }
});
$("title").html(title);
$("#left_title").html("<i class=\"fa fa-gamepad\"></i>游戏管理-" + title);
var $page_content = $('.page-content');
var _js_debug = false;
$.ajaxSetup({
    cache: false
});

var show_error_modal = function (tag, message){
    var $error_modal = $("#error_modal");
    var mess = '<div class="modal-dialog modal-wide"><div class="modal-content">';
    mess += '<div class="modal-header"><button type="button" class="close" data-dismiss="modal"></button>';
    mess += '<h4 class="modal-title">信息</h4></div>';
    mess += '<div class="modal-body">';
    if (tag == 1) {
        mess += '<div class="note note-success">';
    } else {
        mess += '<div class="note note-danger">';
    }
    var arry = message.split("|");
    mess += '<h4 class="block">';
    for (var a in arry) {
        mess += arry[a] + '<br>';
    }
    mess += '</h4></div></div>';
    mess += '<div class="modal-footer"><button type="button" data-dismiss="modal" class="btn red">关闭</button></div></div></div>';
    $error_modal.html(mess);
    $error_modal.modal("show");
};

var my_ajax = function(is_load, url_handler, type, data, async, success_func, error_func){
    error_func = typeof error_func !==  'undefined' ? error_func : function () { };
    if (is_load) {
        App.blockUI($page_content, false);
    }
    $.ajaxSetup({
       cache: false
    });
    $.ajax({
        url: url_handler,
        type: type,
        data: data,
        dataType: 'json',
        async: async,
//        timeout: 20000,
        error: function (x, t, e) {
            if (is_load) {
                App.unblockUI($page_content);
            }
            error_func();
            show_error_modal(0, x.responseText);
        },
        success: function (data) {
            if (_js_debug) {
                console.log(data);
            }
            if (is_load) {
                App.unblockUI($page_content);
            }
            success_func(data);
        }
    })
};

var my_ajax2 = function(is_load, url_handler, type, data, async, success_func){
    if (is_load) {
        App.blockUI($page_content, false);
    }
    $.ajaxSetup({
       cache: false
    });
    $.ajax({
        url: url_handler,
        type: type,
        data: data,
        dataType: 'json',
        async: async,
//        timeout: 20000,
        error: function (x, t, e) {
            if (is_load) {
                App.unblockUI($page_content);
            }
        },
        success: function (data) {
            if (_js_debug) {
                console.log(data);
            }
            if (is_load) {
                App.unblockUI($page_content);
            }
            success_func(data);
        }
    })
};


var my_ajax_file = function(is_load, url_handler, file_id, data, async, success_func){
    if (is_load) {
        App.blockUI(this.$page_content, false);
    }
    $.ajaxFileUpload({
        url: url_handler,
        secureuri: false,
        type: "post",
        data: data,
        fileElementId: file_id,
        dataType: 'json',
        error: function (x, t, e) {
            if (is_load) {
                App.unblockUI($page_content);
            }
            show_error_modal(0, x.responseText);
        },
        success: function (data, status) {
            if (_js_debug) {
                console.log(data);
            }
            if (is_load) {
                App.unblockUI($page_content);
            }
            success_func(data);
        }
    })
};


var custom_left_type = {
    "1": {
        "name": "广播",
        "url": "/broadcast"
    },
    "2": {
        "name": "邮件",
        "url": "/mail"
    },
    "3": {
        "name": "邮件审核",
        "url": "/mail_approve"
    },
    "4": {
        "name": "充值",
        "url": "/gmrecharge"
    },
    "5": {
        "name": "活动",
        "url": "/activity"
    },
    "6": {
        "name": "账号封停",
        "url": "/closeaccount"
    },
    "7": {
        "name": "公告",
        "url": "/notice"
    },
    "8": {
        "name": "聊天",
        "url": "/chat"
    },
    "9": {
        "name": "玩家查询",
        "url": "/account"
    },
    "10": {
        "name": "日志查询",
        "url": "/rolelog"
    },
    "11": {
        "name": "客服用户",
        "url": "/custom"
    },
    "12": {
        "name": "排行榜",
        "url": "/ranking_list"
    },
    "13": {
        "name": "系统公告",
        "url": "/notice"
    },
    "14": {
        "name": '充值排行榜',
        "url": '/recharge/ranking'
    },
    "15": {
        "name": '踢玩家下线&解散公会',
        "url": '/game/info/part'
    },
    "16": {
        "name": '公会公告',
        "url": '/guild/notice'
    },
    "17": {
        "name": '手动开服',
        "url": '/openserver/index'
    },
    "18": {
        "name": 'GS_充值',
        "url": '/gs_recharge/index'
    },
    "19": {
        "name": 'GS_用户审核',
        "url": '/gs_auditing_users/index'
    }
};

var GAME_SERVER_DICT = null;
var PARTITION_DATA = null;
//禁用modal框的空白和ESC键
var common_modal = $(".modal");
common_modal.modal({backdrop: 'static', keyboard: false});
common_modal.modal("hide");

var show_auth_modal = function(){
    $("#auth_modal").modal("show");
};

var getUserNameAndRole = function () {
    var channel = $.cookie("channel_name");
    var user_name = $.cookie("user_session");
    var name = $.cookie("name");
    var user_channel = $.cookie("user_channel");
    var user_role1 = $.cookie("user_role1");
    var user_role2 = $.cookie("user_role2");
    var user_role3 = $.cookie("user_role3");
    var user_role4 = $.cookie("user_role4");
    var user_role5 = $.cookie("user_role5");
    $("#user_channel").val(user_channel);
    $("#username").html(name);
    var str_info = "";
    if (user_role1 == "1"){
        $("#enter_manage").attr("href", "/server");
        if (typeof(role_tag) != "undefined" && role_tag == 1) {
            str_info += '<a class="btn green-haze dark-stripe" href="/server">管理</a>';
        }
        else {
            str_info += '<a class="btn default dark-stripe" href="/server">管理</a>';
        }
    }
    else{
        $("#enter_manage").attr("onclick", "show_auth_modal()");
    }
    if (user_role2 == "1") {
        $("#enter_art").attr("href", "/config/configfile");
        if (typeof(role_tag) != "undefined" && role_tag == 2) {
            str_info += '<a  class="btn green-haze dark-stripe" href="/config/configfile">策划</a>';
        }
        else {
            str_info += '<a  class="btn default dark-stripe" href="/config/configfile">策划</a>';
        }
    }
    else{
        $("#enter_art").attr("onclick", "show_auth_modal()");
    }
    if (user_role3 == "1") {
        if (user_name == "wangjie" || user_name == "wangjie2" || user_name == "anfeng" || user_name == "anfeng2"
          || user_name == "ihangmei1" || user_name == "ihangmei2" || user_name == "ihangmei3"
          || user_name == 'beiyou888'  || user_name == "jx_yd"
        || user_name == "huanwenios" || username == "zhisheng"
        || user_name == "huanwengp5" || user_name == "huanwengp6" || user_name == "huanwengp8"){
            $("#enter_count").attr("href", "/operatedata");
        }
        else{
            $("#enter_count").attr("href", "/trend");
        }
        if (typeof(role_tag) != "undefined" && role_tag == 3) {
            $("#username").html(channel + ":" + user_name);
            str_info += '<a id="enter_count" class="btn green-haze dark-stripe" href="/trend">统计</a>';
        }
        else {
            str_info += '<a id="enter_count" class="btn default dark-stripe" href="/trend">统计</a>';
        }
    }
    else{
        $("#enter_count").attr("onclick", "show_auth_modal()");
    }
    if (user_role4 == "1") {
        $("#enter_operate").attr("href", "/allgame_b/total");
        if (typeof(role_tag) != "undefined" && role_tag == 4) {
            str_info += '<a  class="btn green-haze dark-stripe" href="/allgame_b/total">运维</a>';
        }
        else {
            str_info += '<a  class="btn default dark-stripe" href="/allgame_b/total">运维</a>';
        }
    }
    else{
        $("#enter_operate").attr("onclick", "show_auth_modal()");
    }
    if (user_role5 == "1") {
        var user_custom = $.cookie("user_custom");
        var custom_split = user_custom.split("|");
        var url_t = custom_left_type[custom_split[0]]["url"];
        $("#enter_service").attr("href", url_t);
        if (typeof(role_tag) != "undefined" && role_tag == 5) {
            var str_html2 = "";
            for (var c in custom_split) {
                if (custom_split[c].length != 0) {
                    str_html2 += "<li id=\"channel" + custom_split[c] + "\"><a href=\"" + custom_left_type[custom_split[c]]["url"] + "\"" +
                        "<span class=\"title\">" + custom_left_type[custom_split[c]]["name"] + "</span></a></li>";
                }
            }
            $(".page-sidebar-menu").append(str_html2);
            str_info += '<a  class="btn green-haze dark-stripe" href="' + url_t + '">运营</a>';
        }
        else {
            str_info += '<a class="btn default dark-stripe" href="' + url_t + '">运营</a>';
        }
    }
    else{
        $("#enter_service").attr("onclick", "show_auth_modal()");
    }
    $("#system_list").html(str_info);
};
getUserNameAndRole();



var oLanguage = { // 汉化
    "sProcessing": "正在加载中...",
    "sLengthMenu": "显示_MENU_条 ",
    "sZeroRecords": "没有匹配的数据",
    // "sInfo": "第_START_ - _END_ 条/共 _TOTAL_ 条数据",
    "sInfo": "第_START_ - _END_ 条",
    "sInfoEmpty": "没有匹配的数据",
    // "sInfoFiltered": "(全部记录数 _MAX_  条)",
    "sInfoFiltered": "(共 _TOTAL_  条记录)",
    "sInfoPostFix": "",
    "sSearch": "搜索",
    "sUrl": "",
    "oPaginate": {
        "sFirst": "第一页",
        "sPrevious": " 上一页 ",
        "sNext": " 下一页 ",
        "sLast": " 最后一页 "
    }
};


//分页
var iDisplayStart = 0;
var iDisplayLength = 10;

var dataTablePage = function(div_table, aoColumns, ajaxSource, data, sort_tag, func_callback){
    return div_table.DataTable({
        "oLanguage": oLanguage,
        "bPaginate" : true,
        "bFilter" : false,
        "bDestroy": true,
        "bLengthChange" : true,
        // "bStateSave": true,
        "bWidth": true,
        // "iDisplayStart": iDisplayStart,
        // "iDisplayLength" : iDisplayLength,
        "bSort" : sort_tag,
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth": true,
        "bScrollCollapse" : true,
        "sAjaxSource": ajaxSource,
        "aoColumns": aoColumns,
        "sPaginationType": "bootstrap",
        "fnRowCallback": function (nRow, aData, iDisplayIndex) {
            if (func_callback != null)
                func_callback(nRow, aData);
        },
        "fnServerData": function (sSource, aoData, fnCallback) {
            data["aoData"] = JSON.stringify(aoData);
            $.ajax({
                type: 'get',
                url: sSource,
                data: data,
                dataType: 'JSON',
                async: false,
                success: function (resp) {
                    fnCallback(resp)
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            })
        }
    });
};

//后端分页表格
var back_page_table = function(table_div, ajax_data,columns,columnDefs, order_tag){
     return  table_div.DataTable({
                "destroy" : true,
                "bAutoWidth" : false,
                "bProcessing" : true,
                "serverSide" : true,
                "ajax":ajax_data,
                "bFilter": false,    //去掉搜索框方法三：这种方法可以
                "bLengthChange": true,
                "aLengthMenu":[10, 20, 50, 100],
                "paging": true,
                "columns" : columns,
                "columnDefs":columnDefs,
                "ordering" : order_tag,
                "oLanguage" :oLanguage

            });
};

//前端分页表格
var front_page_table = function(div_table, aoColumns, ajaxSource, data, sort_tag, func_callback){
    return div_table.DataTable({
        "oLanguage": oLanguage,
        "bPaginate" : true,
        "bFilter" : false,
        "bDestroy": true,
        "bLengthChange" : true,
        // "bStateSave": true,
        "bWidth": true,
        "bSort" : sort_tag,
        "bProcessing" : true,
        "bServerSide" : false,
        "bAutoWidth": true,
        "bScrollCollapse" : true,
        "sAjaxSource": ajaxSource,
        "aoColumns": aoColumns,
        "sPaginationType": "bootstrap",
        "fnRowCallback": function (nRow, aData, iDisplayIndex) {
            if (func_callback != null)
                func_callback(nRow, aData);
        },
        "fnServerData": function (sSource, aoData, fnCallback) {
            data["aoData"] = JSON.stringify(aoData);
            $.ajax({
                type: 'get',
                url: sSource,
                data: data,
                dataType: 'JSON',
                async: false,
                success: function (resp) {
                    fnCallback(resp)
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            })
        }
    });
};
//新前端分页表格
var new_front_page_table = function(div_obj, ajax_data,columns,columnDefs,order_tag){
    return div_obj.DataTable({
        "destroy" : true,
        "autoWidth" : false,
        "processing" : true,
        "ajax": ajax_data,
        "searching": false,    //去掉搜索框方法三：这种方法可以
        "lengthChange": true,
        "lengthMenu":[10,20,50,100],
        "paging": true,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : order_tag,
        "oLanguage" : oLanguage
   });
};

//新前端分页表格
var new_front_page_table2 = function(div_obj, data,columns,columnDefs,order_tag){
    return div_obj.DataTable({
        "destroy" : true,
        "bAutoWidth" : false,
        "bProcessing" : true,
        "data": data,
        "bFilter": false,    //去掉搜索框方法三：这种方法可以
        "bLengthChange": false,
        "aLengthMenu":[10],
        "paging": true,
        "columns" : columns,
        "aoColumnDefs":columnDefs,
        "ordering" : order_tag,
        "oLanguage" : oLanguage
   });
};


var get_left_game_server = function () {
    $.ajax({
        type: 'get',
        url: '/server/getgameserver',
        async: false,
        dataType: 'JSON',
        success: function (data) {
            var str_info2 = "";
            var str_info3 = "";
            var str_info4 = "<li><a href='/allgame?server_ip=all'>全部</a></li>";
            var temp_ip = {};
            var tmp_ip_str = '';
            for (var i in data) {
                var tag = true;
                if (tag){
                    str_info2 += '<li id="channel2_' + i + '">';
                    str_info2 += '<a href="/game_manage?server_id=' + i + '">';
                    str_info2 += i + "区:" + data[i]["name"];
                    str_info2 += '</a></li>';
                }
                str_info3 += '<li id="channel3_' + i + '">';
                str_info3 += '<a href="/data_manage?server_id=' + i + '">';
                str_info3 += i + "区:" + data[i]["name"];
                str_info3 += '</a></li>';
                tmp_ip_str = data[i]['extranet_ip'];
                if (!(tmp_ip_str in temp_ip)){
                    temp_ip[tmp_ip_str] = '';
                    str_info4 += '<li>';
                    str_info4 += '<a href="/allgame?server_ip=' + tmp_ip_str + '">';
                    str_info4 += (data[i]['ip_name'].length > 0) ? data[i]['ip_name'] : tmp_ip_str;
                    str_info4 += '</a></li>';
                }
            }
            $("#server_ip").html(str_info4);
            $("#game_gameserver").html(str_info2);
            $("#data_gameserver").html(str_info3);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
};


var setLeftStyle = function () {
    if ($(".page-sidebar-menu").length > 0){
        var str_selected = '<span class="selected"></span>';
        if (typeof(channel_second) != "undefined" && channel_second != null && channel_second != "") {
            $("#channel" + channel_id + '_' + channel_second).addClass("active");
        }
        $("#channel" + channel_id).addClass("active");
        $("#channel" + channel_id + " a").append(str_selected)
    }

};
setLeftStyle();

var Common = function (){
    var alert_message = function(modal_name, tag, message){
        var mess = '<div class="modal-dialog modal-wide"><div class="modal-content">';
        mess += '<div class="modal-header"><button type="button" class="close" data-dismiss="modal"></button>';
        mess += '<h4 class="modal-title">信息</h4></div>';
        mess += '<div class="modal-body">';
        if(tag == 1){
            mess += '<div class="note note-success">';
        }else{
            mess += '<div class="note note-danger">';
        }
        var arry = message.split("|");
        mess += '<h4 class="block">';
        for (var a in arry){
             mess += arry[a] + '<br>';
        }
        mess += '</h4></div></div>';
        mess += '<div class="modal-footer"><button type="button" data-dismiss="modal" class="btn red">关闭</button></div></div></div>';
        modal_name.html(mess);
        modal_name.modal("show");
    };
    return{
        alert_message: function(modal, tag, message){
            alert_message(modal, tag, message);
        }
    }
}();

var create_del_modal = function (modal_div, message, confirm_id){
    var mess = '<div class="modal-dialog"><div class="modal-content">';
    mess += '<div class="modal-header"><button type="button" class="close" data-dismiss="modal"></button>';
    mess += '<h4 class="modal-title">信息</h4></div>';
    mess += '<div class="modal-body"><div class="note note-danger">';

    mess += '<h4 class="block">' + message + '</h4></div></div>';
    mess += '<div class="modal-footer"><button type="button" data-dismiss="modal" class="btn red-intense">关闭</button>';
    mess += '<button id="' + confirm_id + '" type="button" data-dismiss="modal" class="btn green-haze">确定</button></div></div></div>';
    modal_div.html(mess);
};


var handleDatePickers = function () {

    if (jQuery().datepicker) {
        $('.date-picker').datepicker({
            rtl: App.isRTL(),
            autoclose: true,
            endDate: new Date()
        });
    }
};


var handleDatePickers2 = function () {
    if (jQuery().datepicker) {
        $('.date-picker').datepicker({
            rtl: App.isRTL(),
            autoclose: true
        });
    }
};

var handleTimePickers = function () {

    if (jQuery().timepicker) {
        $('.timepicker-24').timepicker({
            showInputs: false,
            minuteStep: 1,
            secondStep: 1,
            showSeconds: true,
            showMeridian: false
        });
    }
};


var getNowFormatDate = function (d) {
    var day = new Date();
    var CurrentDate = "";
    day.setDate(day.getDate() - d);
    var Year = day.getFullYear();
    var Month = day.getMonth() + 1;
    var Day = day.getDate();
    CurrentDate += Year + "-";
    if (Month >= 10) {
        CurrentDate += Month + "-";
    }
    else {
        CurrentDate += "0" + Month + "-";
    }
    if (Day >= 10) {
        CurrentDate += Day;
    }
    else {
        CurrentDate += "0" + Day;
    }
    return CurrentDate;
};



$("#update_pass").bind("click", function(e){
    e.preventDefault();
    $("#oldpass").val("");
    $("#newpass").val("");
    $("#confirmpass").val("");
    $("#update_pass_modal").modal("show");
});

var get_exchange = function(){
    var exchange_num = 0;
    
    var url = '/exchange/getexchange';
    var success = function(data){
        exchange_num = data["value"];
    };
    my_ajax(true, url, 'get', {}, false, success);
    return exchange_num
};

$("#set_exchange").on("click", function (e){
    e.preventDefault();
    var exchange_num = get_exchange();
    $("#exchange_num").html(exchange_num);
    $("#huilv_modal").modal("show");
});

var commonValidation = function (form1, validate_data, message_data, func) {
    var error1 = $('.alert-danger', form1);
    form1.validate({

        errorElement: 'span',
        errorClass: 'help-block',
        focusInvalid: false,
        ignore: "",
        rules: validate_data,
        messages: message_data,
        invalidHandler: function (event, validator) {
            error1.show();
            App.scrollTo(error1, -200);
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
            error1.hide();
            func();
        }
    });
};

var passValidation = function(){
    var form1 = $("#pass_form");
    var rules = {
        oldpass: {
            required: true
        },
        newpass: {
            rangelength: [6, 20],
            required: true
        },
        confirmpass: {
            equalTo: "#newpass"
        }
    };
    var messages = {
        oldpass: {
            required: "请输入旧密码."
        },
        newpass: {
            required: "请输入新密码.",
            rangelength: $.format("密码最小长度:{0}, 最大长度:{1}。")
        },
        confirmpass: {
            equalTo: "两次密码输入不一致."
        }
    };
    var submitFunc = function () {
        var old_pass = $('#oldpass').val();
        var new_pass = $('#newpass').val();
        $.ajax({
            type: 'get',
            url: '/updatepass',
            data: {old_pass: old_pass, new_pass: new_pass},
            dataType: 'JSON',
            success: function (data) {
                $("#update_pass_modal").modal("hide");
                if (data["status"] != 0) {
                    Common.alert_message($("#error_modal"), 0, "旧密码错误.")
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    };
    commonValidation(form1, rules, messages, submitFunc);
};
passValidation();


var $e_key = $("#exchange_plat");
var exchangeValidation = function(){
    var form1 = $("#exchange_form");
    var rules = {
        exchange_num: {
            required: true
        }
    };
    var messages = {
        exchange_num: {
            required: "请输入汇率."
        }
    };
    var submitFunc = function () {
        var exchange_num = $('#exchange_num').val();
        $.ajax({
            type: 'get',
            url: '/exchange/setexchange',
            data: {
                exchange_num: exchange_num,
                e_key: $e_key.val()
            },
            dataType: 'JSON',
            success: function (data) {
                $("#huilv_modal").modal("hide");
                if (data["status"] == 'success') {
                    Common.alert_message($("#error_modal"), 1, "设置成功.")
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    };
    commonValidation(form1, rules, messages, submitFunc);
};
exchangeValidation();

var get_exchange = function(e_key){
    var exchange_num = 0;
    var url = '/exchange/getexchange';
    var success = function(data){
        exchange_num = data["value"];
    };
    var data = {
        e_key: e_key
    };
    my_ajax(true, url, 'get', data, false, success);
    return exchange_num
};


$e_key.on("change", function (e) {
    e.preventDefault();
    var value = $(this).val();
    var exchange_num = get_exchange(value);
    $("#exchange_num").val(exchange_num);
});


$("#set_exchange").on("click", function (e){
    e.preventDefault();
    $e_key.change();
    $("#huilv_modal").modal("show");
});

var CHANNEL_DATA = "";
var getPartnerData = function(div_partner){
    if (CHANNEL_DATA == "") {
        var success = function (data) {
            CHANNEL_DATA += '<option value="0">全部渠道</option>';
            for (var i = 0; i < data.length; i++) {
                CHANNEL_DATA += '<option value="' + data[i]["id"] + '">' + data[i]["name"] + '</option>';
            }
            div_partner.html(CHANNEL_DATA);
        };
        my_ajax(true, '/getpartner', 'get', {}, false, success);
    }
    else {
        div_partner.html(CHANNEL_DATA);
    }
};

//获取渠道列表
var getChannelData= function(){
    var channel_list = [];
    var success = function (data) {

        for (var i = 0; i < data.length; i++) {
            channel_list.push({"label":data[i]["name"],"value":data[i]["id"]});
        }
        // div_partner.multiselect('dataprovider',channel_list);
    };
    my_ajax(true, '/getpartner', 'get', {}, false, success);
    return channel_list
};


var getChannelData_2= function(div_partner, all_control){
    var channel_list = [];
    if (all_control === 0){
        channel_list.push( {"label":'全部渠道',"value": 0} )
    }

    var success = function (data) {

        for (var i = 0; i < data.length; i++) {
            channel_list.push({"label":data[i]["name"],"value":data[i]["id"]});
        }
        div_partner.multiselect('dataprovider',channel_list);
    };
    my_ajax(true, '/getpartner', 'get', {}, false, success);

};

var setPartnerData = function(channel_id, div_partner){
    if (channel_id == 0){
        $(".actions .btn-group").removeClass("hide");
        getPartnerData(div_partner);
    }
};


var getGameServerData = function(div_select, tag, all_tag){
    var send_data = {};

    if (typeof all_tag != "undefined"){
        send_data = {"tag": 1};
    }
    if (GAME_SERVER_DICT == null){
        var success = function(data){
            GAME_SERVER_DICT = data;
        };
        my_ajax(true, '/server/getgameserver', 'get', send_data, false, success);
    }
    var str_html = "";
    if (tag == 2) {
        str_html += "<option value='0'>全服</option>";
    }
    for (var i in GAME_SERVER_DICT) {
        str_html += '<option value="' + i + '">' + i + "区:" + GAME_SERVER_DICT[i]["name"] + '</option>';
    }
    div_select.html(str_html);
};

var getPartitionData = function(div_select){
    if (PARTITION_DATA === null){
        var success = function(data){
            PARTITION_DATA = data;
        };
        my_ajax(true, '/server/get_partition', 'get', {}, false, success);
    }
    var str_html = "";
    for (var i in PARTITION_DATA) {
        str_html += '<option value="' + PARTITION_DATA[i]["id"] + '">'+ PARTITION_DATA[i]["name"] + '</option>';
    }
    div_select.html(str_html);
};

var getPartitionList = function(){
    if (PARTITION_DATA === null){
        var success = function(data){
            PARTITION_DATA = data;
        };
        my_ajax(true, '/server/get_partition', 'get', {}, false, success);
    }
    var partition_list = [];
    for (var i in PARTITION_DATA) {
        partition_list.push({id: PARTITION_DATA[i]["id"], text: PARTITION_DATA[i]["name"]});
    }
    return partition_list;
};


//获取渠道列表
var getChannelData2= function(div_partner){

    var success = function (data) {
        var str_html = '';
        for (var i = 0; i < data.length; i++) {
            str_html += '<option value="'+ data[i]["name"] +'">'+ data[i]["name"] +'</option>';
        }
        div_partner.html(str_html)
    };
    my_ajax(true, '/getpartner', 'get', {}, false, success);

};

var getGameServerData_2 = function(div_select, all_tag){
    var send_data = {};
    if (arguments[1]){
        send_data = {'tag': '1'}
    }
    if (GAME_SERVER_DICT == null){
        var success = function(data){
            GAME_SERVER_DICT = data;
        };
        my_ajax(true, '/server/getgameserver', 'get', send_data, false, success);
    }
    var server_list = [];
    for (var i in GAME_SERVER_DICT) {
        var server_name = GAME_SERVER_DICT[i]["name"];
        server_list.push({"label":i+'区('+server_name+')',"value":i+'区: '+server_name});
    }
    div_select.multiselect('dataprovider',server_list);
};


var getGameServerDataCheck = function(div_select){
    if (GAME_SERVER_DICT == null){
        var success = function (data) {
            GAME_SERVER_DICT = data;
        };
        my_ajax(true, '/server/getgameserver', 'get', {}, false, success);
    }
    var str_info = "";
    for (var i in GAME_SERVER_DICT) {
        str_info += "<label> <input type=\"checkbox\" name=\"game_server\" value=\"" +
            i + "\">" + i + "区:" + GAME_SERVER_DICT[i]["name"] + "</label>";
    }
    div_select.html(str_info);
};


var commonPercent = function(num_a, num_b){
    if (num_b == 0){
        return parseFloat(0).toFixed(2);
    }
    return parseFloat(num_a / num_b * 100).toFixed(2);
};


var error_func = function(XMLHttpRequest){
    Common.alert_message($("#error_modal"), 0, XMLHttpRequest.responseText);
};

var no_auth_func = function(){
    Common.alert_message($("#error_modal"), 0, "无权限操作！");
};


var gd = function(year, month, day) {
    return new Date(year, month-1, day).getTime();
};

var getNowFormatDate2 = function (){
    var day = new Date();
    var CurrentDate = "";
    day.setDate(day.getDate());
    var Year = day.getFullYear();
    var Month = day.getMonth() + 1;
    var Day = day.getDate();
    var hours = day.getHours();
    var minutes = day.getMinutes();
    var seconds = day.getSeconds();
    CurrentDate += Year;
    if (Month >= 10) {
        CurrentDate += Month;
    }
    else {
        CurrentDate += "0" + Month;
    }
    if (Day >= 10) {
        CurrentDate += Day;
    }
    else {
        CurrentDate += "0" + Day;
    }
    if (hours >= 10){
        CurrentDate += hours;
    }
    else{
        CurrentDate += "0" + hours;
    }

    if (minutes >= 10){
        CurrentDate += minutes;
    }
    else{
        CurrentDate += "0" + minutes;
    }

    if (seconds >= 10){
        CurrentDate += seconds;
    }
    else{
        CurrentDate += "0" + seconds;
    }

    return CurrentDate;
};


var SECTION_DATA = null;

var get_section = function (div_section) {
    if (SECTION_DATA == null) {
        var success = function(data){
            SECTION_DATA = data;
        };
        my_ajax(true, "/section/querysection", "get", {}, false, success);
    }
    var str_html = "";
    
    for (var i in SECTION_DATA) {
        str_html += "<option value=\"" + SECTION_DATA[i]["id"] + "\">" + SECTION_DATA[i]["name"] + "</option>";
    }
    div_section.html(str_html);
};


var common_table = function(ajax_url, send_data, success_func){
    $.ajax({
        type: 'get',
        url: ajax_url,
        data: send_data,
        dataType: 'JSON',
        success: function (data) {
            success_func(data);
        },
        error: function(){
            error_func();
        }
    });
};

function MakeOptionList(data, getdataFunc){
    var str_html = "";
    for(var i in data){
        str_html += "<option value='" + i + "'>" + i + "_" + getdataFunc(data[i]) + "</option>";
    }
    return str_html;
}

function MakeOptionList2(data, getdataFunc){
    var str_html = "";
    for(var i in data){
        str_html += "<option value='" + i + "'>" + MyGetDataFunc2(data[i]) + "_" + getdataFunc(data[i]) + "</option>";
    }
    return str_html;
}

function MyGetDataFunc(item){
    return item["name"];
}

function MyGetDataFunc2(item){
    return item["quality"] + "星";
}



function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css({
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x - 30,
        border: '1px solid #333',
        padding: '4px',
        color: '#fff',
        'border-radius': '3px',
        'background-color': '#333',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}


function chart_hover_display(div_chart, process){
    var previousPoint = null;
    div_chart.on("plothover", function (event, pos, item) {
        $("#x").text(pos.x.toFixed(2));
        $("#y").text(pos.y.toFixed(2));

        if (item) {
            if (previousPoint != item.dataIndex) {
                previousPoint = item.dataIndex;

                $("#tooltip").remove();
                var x = item.datapoint[0],
                    y = item.datapoint[1];
                var dis_html = "";
                if (process != null){
                    dis_html = process(x, y);
                }

                showTooltip(item.pageX, item.pageY, dis_html);
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
}

var drawBarsChart = function(dataset, ticks, align, width, div_flot){
     var options = {
        series:{
            bars: {
                show: true,
                fill: true,
                fillColor: { colors: [{ opacity: 1 }, { opacity: 1}] },
                steps: false
            }
        },
        bars: {
            align: align,
            barWidth: width
        },
        xaxis: {
            ticks: ticks
        },
        yaxis: {
            tickDecimals: 0
        },
        legend: {
            position: "nw",
            noColumns: 0
        },
        grid: {
            hoverable: true,
            borderWidth: 0
        },
         colors: ["#44b6ae", '#578ebe', '#67809f', '#e35b5a', '#3b3b3b'],
    };

    $.plot(div_flot, dataset, options);
};

var DrawLineChart = function (dataset, div_flot, tick_format) {
    var options = {
        series: {
            lines: {
                show: true,
                lineWidth: 1,
                fill: false,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.05
                        },
                        {
                            opacity: 0.01
                        }
                    ]
                }
            },
            points: {
                show: true,
                radius: 2
            },
            shadowSize: 2
        },
        grid: {
            hoverable: true,
            clickable: true,
            tickColor: "#eee",
            borderWidth: 0
        },
       colors: ["#44b6ae", '#578ebe', '#67809f', '#e35b5a', '#3b3b3b'],
        xaxis: {
            ticks: 2,
            tickDecimals: 0,
            tickSize: 1,
            tickFormatter: function(v, axis){
                return tick_format(v);
            }
        },
        legend: {
            position: "nw"
//            noColumns: 0,
//            margin: [400, -20]
        },
        yaxis: {
            ticks: 11,
            tickDecimals: 0,
            min:0
        }
    };

    $.plot(div_flot, dataset, options);
};


var DrawLineChartAndBarChart = function (dataset1, dataset2, div_flot, ticks, tick_format) {
    var data_set = [
        {
            data: dataset1,
            "label": "新增用户",
            bars: {
                show: true,
                fill: true,
                fillColor: { colors: [{ opacity: 1 }, { opacity: 1}] },
                steps: false,
                align: "center",
                barWidth: 0.2
            }
        },
        {
            data: dataset2,
            "label": "留存率",
            yaxis: 2,
            points: {show: true },
            lines: {show:true}
        }
    ];
    var options = {
        grid: {
            hoverable: true,
            clickable: true,
            tickColor: "#eee",
            borderWidth: 0
        },
        colors: ["#578ebe", "#44b6ae"],
        xaxis: {
            ticks: ticks
        },
        yaxes: [
            {
                 position: "left",
                 ticks: 11,
                 tickDecimals: 0
            },
            {
                position: "right",
                ticks: 11,
                tickDecimals: 0,
                tickFormatter: function(v, axies){
                    return v + "%";
                }
            }
        ],
        legend: {
            position: "nw"
        }
    };

    $.plot(div_flot, data_set, options);
};


var drawLineChartTime = function (dataset, div_flot) {
    var options = {
        series:{
            lines: {
                show: true,
                lineWidth: 1,
                fill: false,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.05
                        },
                        {
                            opacity: 0.01
                        }
                    ]
                }
            },
            points: {
                show: true,
                radius: 1
            },
            shadowSize: 1
        },
        grid: {
            hoverable: true,
            clickable: true,
            tickColor: "#eee",
            borderWidth: 0
        },
        xaxis:{
            mode: "time",
            tickSize: [1, "hour"],
            tickFormatter: function(v, axis){
                var date = new Date(v);
                return date.getHours() + "点";
            },
            axisLabel: "Time"
        },
        legend: {
            position: "nw"
        },
        colors: ["#67809f", "#999", "#d12610" ],
        yaxis: {
            ticks: 11,
            tickDecimals: 0,
            min:0
        }
    };

    $.plot(div_flot, dataset, options);
};

var drawPieChart = function(div_pie, data){
    $.plot(div_pie, data, {
        series: {
            pie: {
                show: true,
                radius: 1,
                label: {
                    show: true,
                    formatter: function (label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">' +label + ":"+ series.percent.toFixed(2) + '%</div>';
                    },
                    background: {
                        opacity: 0.5,
                        color: '#000'
                    }
                }
            }
        },
        legend: {
            show: true
        }
    })
};


function change_class(button){
    button.siblings().each(function(e){
        if ($(this).hasClass("red-intense")){
            $(this).removeClass("red-intense");
            $(this).addClass("btn-default");
        }
    });
    if(button.hasClass("btn-default")){
        button.removeClass("btn-default");
        button.addClass("red-intense");
    }
}


function export_all_user_excel(user_channel, title, list, type){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var export_title = "";
    title.children().each(function(e){
        export_title += $(this).html() + ",";
    });

    var str_s = "";
    list.children().each(function(e){
        var str_data = "";
        $(this).children().each(function (e) {
            str_data += $(this).html() + ","
        });
        str_s += str_data;
        str_s += "|";
    });

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/exportalluserexcel',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            end_date: end_date,
            export_title: export_title,
            export_data: str_s,
            type: type
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var message = "";
            if (data["status"] == true){
                message = "任务已提交,请到<a href='/downcenter'>下载中心</a>下载.";
            }
            else{
                message = "任务下载失败.请重新下载.";
            }
            Common.alert_message($("#error_modal"), 1, message);

        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}


function init_select_html(tag, data, div){
    var str_html = "";
    if (tag){
        str_html = "<option value=''>请选择</option>";
    }
    for (var d in data) {
        str_html += "<option value='" + d +  "'>" + data[d] + "</option>";
    }
    div.html(str_html);
}


function show_table_title(title_data, $table_title){
    var str_html = "";
    for (var i=0; i<title_data.length; i++){
        str_html += "<th>" + title_data[i] + "</th>";
    }
    $table_title.html(str_html);
}


function display_left_filter(){
    // var user_session = $.cookie("user_session");
    // if (user_session == "administrator_muyou") {
    //     var str_html2 ="<a href=\"/batch_recharge\"><i class=\"fa fa-random\"></i><span class=\"title\">批量处理</span></a>";
    //     $("#channel7").html(str_html2);
    //     var str_html = "<a href=\"/count_filter\"><i class=\"fa fa-file\"></i><span class=\"title\">统计过滤</span></a>";
    //     $("#channel5").html(str_html);
    //     var str_html1 ="<a href=\"/welfare\"><i class=\"fa fa-star\"></i><span class=\"title\">福利号</span></a>";
    //     $("#channel6").html(str_html1);
    // }
}


function display_left_count(){
    var user_session = $.cookie("user_session");
    if (user_session == "wangjie" || user_session == "wangjie2"
        || user_session == "anfeng" || user_session == "anfeng2"
       || user_session == "ihangmei1" || user_session == "ihangmei2" || user_session == "ihangmei3"
        || user_session == "beiyou888" || user_session == "jx_yd"
        || user_session == "huanwenios" || user_session == "zhisheng"
        || user_session == "huanwengp5" || user_session == "huanwengp6" ||user_session == "huanwengp8" ){
        $("#channel1").hide();
        $("#channel2_1").hide();
        $("#channel2_4").hide();
        $("#channel2_5").hide();
        $("#channel3_6").hide();
        $("#channel3_7").hide();
        $("#channel3_4").hide();
        $("#channel4").hide();
        $("#channel5").hide();
        $("#channel6").hide();
    }
    
}