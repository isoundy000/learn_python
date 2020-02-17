/**
 * Created by wangrui on 16/10/17.
 */
/**
 * Created by liuzhaoyang on 15/9/7.
 */

var game_server = $("#select_gameserver");
getGameServerData(game_server, 1);

var QUALITY_CSS = {
    2: "green",
    3: "blue",
    4: "purple",
    5: "yellow"
};

var GENERAL_QUALITY = {
    2: "绿将",
    3: "蓝将",
    4: "紫将",
    5: "橙将"
};

var mail_con=0;
var GLOBAL_DATA = {};
var EQUIP_JSON = null;
var PROPS_JSON = null;
var SOUL_JSON = null;
var GENERAL_JSON=null;

var GENERAL_F_JSON = null;
var EQUIP_F_JSON = null;
var TREASURE_F_JSON = null;

var PET_FRAGMENT_JSON = {
    91001: {
        name: "炽炎犬碎片"
    },
    91002: {
        name: "太极熊碎片"
    },
    91003: {
        name: "紫极魔碎片"
    },
    91004: {
        name: "青光妖龙碎片"
    },
    91005: {
        name: "炽炎朱雀碎片"
    }
};

var CONFIG_TYPE = ["equip", "props", "soul", "general", "general_fragment", "equip_fragment", "treasure2_fragment"];


//function init_select(temp_json){
//    var temp = "<option value=''>" + "请选择" + "</option>";
//    for(var t in temp_json){
//        temp +="<option value='" + e + "'>" + EQUIP_JSON[e]["quality"] + "星:" + EQUIP_JSON[e]["name_CN"] + "</option>";
//    }
//}

//点击 邮件 初始化数据
var init_data = function(){
    var server_id = game_server.val();
    $.ajax({
            type: 'get',
            url: "/queryjsondatabyserver",
            data: {
                server_id: server_id,
                type: JSON.stringify(CONFIG_TYPE)
            },
            async: false,
            dataType: 'JSON',
            success: function (data) {
                GLOBAL_DATA[server_id] = {};
                GLOBAL_DATA[server_id]["equip_list"] = data["equip"];
                GLOBAL_DATA[server_id]["equip_f_list"] = data["equip_fragment"];
                GLOBAL_DATA[server_id]["treasure_f_list"] = data["treasure2_fragment"];
                GLOBAL_DATA[server_id]["props_list"] = data["props"];
                GLOBAL_DATA[server_id]["soul_list"] = data["soul"];
                GLOBAL_DATA[server_id]["general_list"] = data["general"];
                GLOBAL_DATA[server_id]["general_f_list"] = data["general_fragment"];
                EQUIP_JSON = data["equip"];
                EQUIP_F_JSON = data["equip_fragment"];
                PROPS_JSON = data["props"];
                SOUL_JSON = data["soul"];
                GENERAL_JSON = data["general"];
                GENERAL_F_JSON = data["general_fragment"];
                TREASURE_F_JSON = data["treasure2_fragment"];
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );

    var equip_str = "";
    var props_str = "";
    var soul_str = "";
    var general_str = "";
    var general_f_str = "";
    var pet_fragment_str = "";
    var equip_f_str = "";
    var treasure_f_str = "";

    equip_str += "<option value=''>" + "请选择" + "</option>";
    props_str += "<option value=''>" + "请选择" + "</option>";
    soul_str += "<option value=''>" + "请选择" + "</option>";
    general_str += "<option value=''>" + "请选择" + "</option>";
    general_f_str += "<option value=''>" + "请选择" + "</option>";
    pet_fragment_str += "<option value=''>" + "请选择" + "</option>";
    equip_f_str += "<option value=''>" + "请选择" + "</option>";
    treasure_f_str += "<option value=''>" + "请选择" + "</option>";

    for (var e in EQUIP_JSON){
        equip_str += "<option value='" + e + "'>" + EQUIP_JSON[e]["quality"] + "星:" + EQUIP_JSON[e]["name_CN"] + "</option>";
    }
    for (var ef in EQUIP_F_JSON){
        equip_f_str += "<option value='" + ef + "'>" + EQUIP_F_JSON[ef]["name_CN"] + "</option>";
    }
    for (var tf in TREASURE_F_JSON){
        treasure_f_str += "<option value='" + tf + "'>" + TREASURE_F_JSON[tf]["name_CN"] + "</option>";
    }

    for (var p in PROPS_JSON) {
        props_str += "<option value='" + p + "'>" + PROPS_JSON[p]["name_CN"] + "</option>";
    }
    for (var s in SOUL_JSON) {
        soul_str += "<option value='" + s + "'>" + SOUL_JSON[s]["quality"] + "星" + SOUL_JSON[s]["name_CN"] + "</option>";
    }
    for (var g in GENERAL_JSON) {
        if (GENERAL_JSON[g]["actor"] != "lead"){
            general_str += "<option value='" + g + "'>" + GENERAL_QUALITY[GENERAL_JSON[g]["quality"]] + ": " + GENERAL_JSON[g]["name_CN"] + "</option>";
        }
    }
    for (var gfj in GENERAL_F_JSON) {
        general_f_str += "<option value='" + gfj + "'>" + GENERAL_JSON[GENERAL_F_JSON[gfj]["general"]]["name_CN"] + "</option>";
    }

    for (var pf in PET_FRAGMENT_JSON) {
        pet_fragment_str += "<option value='" + pf + "'>" + PET_FRAGMENT_JSON[pf]["name"] + "</option>";
    }

    // if(mail_con==1){
    //     console.log(11111);
    //     console.log(equip_str);
        $("#all_equip_cid").html(equip_str);
        $("#all_equip_f_cid").html(equip_f_str);
        $("#all_treasure_f_cid").html(treasure_f_str);
        $("#all_prop_cid").html(props_str);
        $("#all_soul_cid").html(soul_str);
        $("#all_general_cid").html(general_str);
        $("#all_general_f_cid").html(general_f_str);
        $("#all_pet_cid").html(pet_fragment_str);
    // }
    // else{
        $("#equip_cid").html(equip_str);
        $("#equip_f_cid").html(equip_f_str);
        $("#treasure_f_cid").html(treasure_f_str);
        $("#prop_cid").html(props_str);
        $("#soul_cid").html(soul_str);
        $("#general_cid").html(general_str);
        $("#general_f_cid").html(general_f_str);
        $("#pet_cid").html(pet_fragment_str);
    // }
};
init_data();

//点击 所有服邮件 初始化数据
$("#all_mail").click(function () {
    mail_con=1;
   // init_data();
});


//系统邮件查询
function get_system_mail(){
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "rid",
            'sClass': 'center',
            "sTitle": "角色编号"
        },
        {
            "mDataProp": "ask",
            'sClass': 'center',
            "sTitle": "邮件内容"
        },
        {
            "mDataProp": "status",
            'sClass': 'center',
            "sTitle": "状态"
        },
        {
            "mDataProp": "time1",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">回复 <i class=\"fa fa-edit\"></i></button>"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html = "";
        if (aData.status == "yes"){
            str_html = "<span class='badge badge-success'>已回复</span>"
        }
        else{
            str_html = "<span class='badge badge-danger'>未回复</span>"
        }
        $('td:eq(2)', nRow).html(str_html);
    };
    var sAjaxSource = "/getsystemmail";
    var data = {
        server_id: $("#select_gameserver").val()
    };
    dataTablePage($("#system_mail_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
}
get_system_mail();

//点击 系统邮件 再调系统邮件查询函数
$("#a_mail").bind("click", function (e) {
    e.preventDefault();
    get_system_mail();
});

//勾选服务器 刷新添加表单中的数据
game_server.change(function(){
//    init_data();
    $("#a_mail").click();
});

//回复邮件
function mod(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#system_mail_table").dataTable().fnGetData(nRoW);
    $("#sys_mail_id").val(data["id"]);
    var mail_all = $("input[name='mail_all']");
    mail_all.prop("checked", false);
    mail_all.parent("span").removeClass("checked");
    $("#reply_user").attr("disabled", false);
    $("#reply_user").val(data["rid"]);
    $("#mail_title").val("");
    $("#mail_content").val("");
    $("#annex_cont").html("");
    $('#tab_single_mail').modal("show");
}

//写单服邮件
$('#write_mail').on("click", function(e){
    e.preventDefault();
    var mail_all = $("input[name='mail_all']");
    $("#sys_mail_id").val("");
    mail_all.prop("checked", false);
    mail_all.parent("span").removeClass("checked");
    $("#reply_user").attr("disabled", false);
    $("#reply_user").val("");
    $("#mail_title").val("");
    $("#mail_content").val("");
    $("#annex_cont").html("");
    $('#tab_single_mail').modal("show");
});

//点击添加表单数据清空
$('#add_annex').click(function (){
    $("#equip_cid").val("");
    $("#equip_f_cid").val("");
    $("#prop_cid").val("");
    $("#soul_cid").val("");
    $("#general_cid").val("");
    $("#general_f_cid").val("");
    $("#treasure_f_cid").val("");
    $("#pet_cid").val("");
    $("#equip_num").val("");
    $("#prop_num").val("");
    $("#soul_num").val("");
    $("#general_num").val("");
    $("#pet_num").val("");
    $("#gold_num").val("");
    $("#silver_num").val("");
    $('#annex_modal').modal('show');

});

//将所添加内容打印到 附件内容
var annextext='';
var reward_alias = "";
$("#annex_form").on("click", function(e){
    e.preventDefault();
    var equip = $('#equip_cid').val();
    var equip_num = $("#equip_num").val();
    var props = $('#prop_cid').val();
    var props_num = $("#prop_num").val();
    var soul = $('#soul_cid').val();
    var soul_num = $("#soul_num").val();
    var general = $('#general_cid').val();
    var general_num = $("#general_num").val();
    var gold_num = $("#gold_num").val();
    var pet_cid = $("#pet_cid").val();
    var pet_num = $("#pet_num").val();
    var general_frag = $("#general_f_cid").val();
    var general_frag_num = $("#general_f_num").val();
    var equip_frag = $("#equip_f_cid").val();
    var equip_frag_num = $("#equip_f_num").val();
    var treasure_frag = $("#treasure_f_cid").val();
    var treasure_frag_num = $("#treasure_f_num").val();
    var silver_num = $("#silver_num").val();
    var annexlist = {
        equip:{
            cid: equip,
            num: equip_num
        },
        equip_frag:{
            cid: equip_frag,
            num: equip_frag_num
        },
        treasure_frag:{
            cid: treasure_frag,
            num: treasure_frag_num
        },
        props:{
            cid:props,
            num:props_num
        },
        soul:{
            cid:soul,
            num:soul_num
        },
        general:{
            cid:general,
            num:general_num
        },
        general_frag: {
            cid: general_frag,
            num: general_frag_num
        },
        pet: {
            cid: pet_cid,
            num: pet_num
        },
        gold_num: gold_num,
        silver_num: silver_num
    };
    for (var i in annexlist) {

        var temp_json = null;
        if (i == 'equip' && annexlist[i]['cid'] != '' && annexlist[i]['num']) {
            temp_json = EQUIP_JSON;
        }
        else if(i == 'equip_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = EQUIP_F_JSON;
        }
        else if(i == 'treasure_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = TREASURE_F_JSON;
        }
        else if(i == 'props' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PROPS_JSON;
        }
        else if(i == 'soul' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = SOUL_JSON;
        }
        else if(i == 'general' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_JSON;
        }
        else if(i == 'general_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_F_JSON;
        }
        else if(i == "pet" && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PET_FRAGMENT_JSON;
        }
        if (temp_json != null){
            reward_alias += "[" + temp_json[annexlist[i]['cid']]["name_CN"] + ":" + annexlist[i]['num'] + "]";
            if (i == 'general'){
                annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs " + QUALITY_CSS[temp_json[annexlist[i]['cid']]["quality"]] + "'>" + temp_json[annexlist[i]['cid']]["name_CN"] + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
            else if(i == "general_frag"){
                var general_cid = GENERAL_F_JSON[annexlist[i]['cid']]["general"];
                var general_name = GENERAL_JSON[general_cid]["name_CN"] + "碎片";
                var general_quality = GENERAL_JSON[general_cid]["quality"];
                annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs " + QUALITY_CSS[general_quality] + "'>" + general_name + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
            else{
               annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='label label-success'>" + temp_json[annexlist[i]['cid']]["name_CN"] + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
            console.log("annextext", annextext);
        }

        if(i=='gold_num' && annexlist[i] != ''){
            reward_alias += "[元宝:" + annexlist[i] + "]";
            annextext += "<p><input type='hidden' value='1001'><span class='label label-success'>" + "元宝:" + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i] + "</span></p>"
        }

        else if(i=='silver_num' && annexlist[i] != ''){
            reward_alias += "[银两:" + annexlist[i] + "]";
            annextext += "<p><input type='hidden' value='1000'><span class='label label-success'>" + "银两:" + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i] + "</span></p>"
        }
    }

    $("#annex_modal").modal("hide");
    $("#annex_cont").html(annextext);

});

//清空
$('#clear_annex').click(function(){
    pub_claer_annex()
});

//单服一级弹窗 取消 清空附件内容
$("#cannel_first").click(function(){
    pub_claer_annex()
});

//单服清空 通用功能
var pub_claer_annex = function(){
    annextext = '';
    reward_alias = "";
    $("#annex_cont").html(annextext);
};


//点击全体，锁定收件人文本框
$("#mail_all").on("change", function(e){
    e.preventDefault();
    if ($("#mail_all").is(":checked")) {
        $("#reply_user").attr("disabled", true);
        $("#reply_user").val("");
    }
    else{
        $("#reply_user").attr("disabled", false);
    }
});

//二次确认表单
$('#mail_form1').click(function(form){
    form.preventDefault();
    var mail_all = 0;
    if ($("#mail_all").is(":checked")) {
        mail_all = 1;
    }
    var reply_user = $("input[name='reply_user']").val();
    var reply_user_s = "";
    if (mail_all == 1){
        reply_user_s = '全体玩家'
    }
    else{
        reply_user_s = reply_user
    }
    var server_name = $("#select_gameserver").find("option:selected").text();
    var mail_content = $("textarea[name='mail_content']").val();
    var mail_title = $("#mail_title").val();
    var annex_cont = $('#annex_cont').html();
    if (reply_user_s=='' && mail_all==0){
        $(".alert-danger span").html("必填信息不能为空.");
        $('.alert-danger', $('#mail_single')).show();
        return;
    }
    else{
        if (!isNaN(reply_user) == false) {
            $(".alert-danger span").html("角色ID必须为数字.");
            $('.alert-danger', $('#mail_single')).show();
            return;
        }
        $('.alert-danger', $('#mail_single')).hide();
        var mail_user = "<p>" + reply_user_s + "</p>";
        var mail_cont = "<p>" + mail_content + "</p>";
        $("#mail_tit").html(mail_title);
        $("#send_game").html(server_name);
        $('#mail_user').html(mail_user);
        $('#mail_cont').html(mail_cont);
        $('#mail_annex').html(annex_cont);

        $('#confirm_modal').modal('show');
    }
});

$("#btn_cancel").on("click", function(e){
    e.preventDefault();
    $('#confirm_modal').modal('hide');
});

//发送邮件

$('#sendmail').click(function () {
    var mail_all = 0;
    if ($("#mail_all").is(":checked")) {
        mail_all = 1;
    }
    var server_id = $('#select_gameserver').val();
    var reply_user = $("input[name='reply_user']").val();
    var mail_content = $("textarea[name='mail_content']").val();
    var mail_title = $("#mail_title").val();
    var sys_mail_id = $("#sys_mail_id").val();
    var tag = false;
    if(sys_mail_id.length != 0){
        tag = true;
    }
    var export_title = '';
    $("#annex_cont").children().each(function () {
        var cid = $(this).find("input").val();
        var num = $(this).find("span:eq(1)").html();
        export_title += "\"" + cid + "\":\"" + num + "\",";
    });
    var mail_annex = "{" + export_title.substring(0, export_title.length - 1) + "}";
    if (mail_annex == "{}"){
        mail_annex = ''
    }
    var data = {
        server_id: server_id, mail_all: mail_all, mail_con: 0, sys_mail_id: sys_mail_id,
        reply_user: reply_user, mail_title: mail_title, mail_content: mail_content, mail_annex: mail_annex, reward_alias:reward_alias
    };
    send_mail_method(tag, data, $("#confirm_modal"), $("#tab_single_mail"));
});

//==============================================================================================

//将所添加内容打印到 附件内容
$('#add_annex2').click(function (){
    $("#all_equip_cid").val("");
    $("#all_equip_f_cid").val("");
    $("#all_treasure_f_cid").val("");
    $("#all_prop_cid").val("");
    $("#all_soul_cid").val("");
    $("#all_general_cid").val("");
    $("#all_pet_cid").val("");
    $("#all_equip_num").val("");
    $("#all_prop_num").val("");
    $("#all_soul_num").val("");
    $("#all_general_num").val("");
    $("#all_general_f_cid").val("");
    $("#all_pet_num").val("");
    $("#all_gold_num").val("");
    $("#all_silver_num").val("");
    $('#all_annex_modal').modal('show');

});

//将所添加内容打印到 附件内容
var all_annextext='';
$("#annex_form_all").on("click", function(e){
    e.preventDefault();
    var equip = $('#all_equip_cid').val();
    var equip_num = $("#all_equip_num").val();
    var equip_frag = $("#all_equip_f_cid").val();
    var equip_frag_num = $("#all_equip_f_num").val();
    var treasure_frag = $("#all_treasure_f_cid").val();
    var treasure_num = $("#all_treasure_f_num").val();
    var props = $('#all_prop_cid').val();
    var props_num = $("#all_prop_num").val();
    var soul = $('#all_soul_cid').val();
    var soul_num = $("#all_soul_num").val();
    var general = $('#all_general_cid').val();
    var general_num = $("#all_general_num").val();
    var general_frag = $("#all_general_f_cid").val();
    var general_frag_num = $("#all_general_f_num").val();
    var pet = $('#all_pet_cid').val();
    var pet_num = $("#all_pet_num").val();
    var gold_num = $("#all_gold_num").val();
    var silver_num = $("#all_silver_num").val();
    var annexlist = {
        equip:{
            cid: equip,
            num: equip_num
        },
        equip_frag:{
            cid: equip_frag,
            num: equip_frag_num
        },
        treasure_frag:{
            cid: treasure_frag,
            num: treasure_num
        },
        props:{
            cid:props,
            num:props_num
        },
        soul:{
            cid:soul,
            num:soul_num
        },
        general:{
            cid:general,
            num:general_num
        },
        general_frag: {
            cid: general_frag,
            num: general_frag_num
        },
        pet: {
            cid: pet_cid,
            num: pet_num
        },
        gold_num: gold_num,
        silver_num: silver_num
    };
    for (var i in annexlist) {

        var temp_json = null;
        if (i == 'equip' && annexlist[i]['cid'] != '' && annexlist[i]['num']) {
            temp_json = EQUIP_JSON;
        }
        else if(i == 'equip_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = EQUIP_F_JSON;
        }
        else if(i == 'treasure_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = TREASURE_F_JSON;
        }
        else if(i == 'props' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PROPS_JSON;
        }
        else if(i == 'soul' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = SOUL_JSON;
        }
        else if(i == 'general' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_JSON;
        }
        else if(i == 'general_frag' && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = GENERAL_F_JSON;
        }
        else if(i == "pet" && annexlist[i]['cid'] != '' && annexlist[i]['num']){
            temp_json = PET_FRAGMENT_JSON;
        }
        if (temp_json != null){
            reward_alias += "[" + temp_json[annexlist[i]['cid']]["name_CN"] + ":" + annexlist[i]['num'] + "]";
            if (i == 'general'){
                all_annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs " + QUALITY_CSS[temp_json[annexlist[i]['cid']]["quality"]] + "'>" + temp_json[annexlist[i]['cid']]["name_CN"] + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
            else if(i == "general_frag"){
                var general_cid = GENERAL_F_JSON[annexlist[i]['cid']]["general"];
                var general_name = GENERAL_JSON[general_cid]["name_CN"] + "碎片";
                var general_quality = GENERAL_JSON[general_cid]["quality"];
                all_annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='btn default btn-xs " + QUALITY_CSS[general_quality] + "'>" + general_name + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
            else{
               all_annextext += "<p><input type='hidden' value='" + annexlist[i]['cid'] + "'><span class='label label-success'>" + temp_json[annexlist[i]['cid']]["name_CN"] + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i]['num'] + "</span></p>";
            }
        }

        if(i=='gold_num' && annexlist[i] != ''){
            reward_alias += "[元宝:" + annexlist[i] + "]";
            all_annextext += "<p><input type='hidden' value='1001'><span class='label label-success'>" + "元宝:" + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i] + "</span></p>"
        }

        else if(i=='silver_num' && annexlist[i] != ''){
            reward_alias += "[银两:" + annexlist[i] + "]";
            all_annextext += "<p><input type='hidden' value='1000'><span class='label label-success'>" + "银两:" + "</span>&nbsp;&nbsp;<span class='badge badge-danger'>" + annexlist[i] + "</span></p>"
        }
    }
    $("#all_annex_modal").modal("hide");
    $("#all_annex_cont").html(all_annextext);

});

//清空
var all_clear_annex = function(){
    all_annextext='';
    $("#all_annex_cont").html(all_annextext);
};

$('#all_clear_annex').click(function(){
    all_clear_annex();
});

//二次确认表单
$('#all_mail_form1').click(function(form){
    form.preventDefault();
    var mail_content = $("textarea[name='all_mail_content']").val();
    var annex_cont = $('#all_annex_cont').html();
    var all_mail_title = $("#all_mail_title").val();
    var mail_cont = "<p>" + mail_content + "</p>";
    $("#all_mail_tit").html(all_mail_title);
    $('#all_mail_cont').html(mail_cont);
    $('#all_mail_annex').html(annex_cont);

    $('#all_confirm_modal').modal('show');
});

var send_mail_method = function (tag, s_data, div_modal, div_modal2){
    var data = s_data;
    var success = function(data){
        div_modal.modal("hide");
        if (data["status"] == "fail") {
            Common.alert_message($("#error_modal"), 0, data["errmsg"]);
        }
        else if (data["status"] == "approve") {
            Common.alert_message($("#error_modal"), 1, "邮件已发送,请等待审核");
        }
        else {
            Common.alert_message($("#error_modal"), 1, "邮件发送成功");
        }
        if (div_modal2 != "") {
            div_modal2.modal("hide");
        }
        pub_claer_annex();
        all_clear_annex();
        $("#all_mail_title").val("");
        $('#all_mail_content').val("");
        $('#mail_content').val("");
        if (tag) {
            get_system_mail();
        }
    };
    my_ajax(true, "/sendmail2", "get", data, true, success);
};

//发送邮件
$('#sendallmail').on("click", function (e) {
    e.preventDefault();
    var mail_content = $("textarea[name='all_mail_content']").val();
    var all_mail_title = $("#all_mail_title").val();
    var export_title = '';
    $("#all_annex_cont").children().each(function () {
        var cid = $(this).find("input").val();
        var num = $(this).find("span:eq(1)").html();
        export_title += "\"" + cid + "\":\"" + num + "\",";
    });
    var mail_annex = "{" + export_title.substring(0, export_title.length - 1) + "}";
    if (mail_annex == "{}"){
        mail_annex = ''
    }

    var data = {
        mail_title: all_mail_title, mail_content: mail_content, mail_annex: mail_annex,
        mail_con: 1, reward_alias: reward_alias
    };
    var div_modal2 = "";
    send_mail_method(false, data, $("#all_confirm_modal"), div_modal2);
});


//==============================================================
//model弹框取消
var cancle_modal = function(modal_id){
    modal_id.modal("hide");
};

$("#cancel_annex_cont").on("click", function(){
    var modal_id = $("#annex_modal");
    cancle_modal(modal_id);
});

////将 附件 打印到 附件内容，通用代码
//var pub_annex = function(str_annex){
//
//};