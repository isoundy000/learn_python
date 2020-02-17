/**
 * Created by wangrui on 15/5/7.
 */

var show_auth_modal = function(){
    $("#auth_modal").modal("show");
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
    "6": {
        "name": "封号",
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
    }
};

var name = $.cookie("name");
$("#username").html(name);

var setSystem = function (){
    var user_role1 = $.cookie("user_role1");
    var user_role2 = $.cookie("user_role2");
    var user_role3 = $.cookie("user_role3");
    var user_role4 = $.cookie("user_role4");
    var user_role5 = $.cookie("user_role5");

    if (user_role1 == "0") {
        $("#enter_manage").attr("onclick", "show_auth_modal()");
    }
    else {
        $("#enter_manage").attr("href", "/server");
    }
    if (user_role2 == "0") {
        $("#enter_art").attr("onclick", "show_auth_modal()");
    }
    else {
        $("#enter_art").attr("href", "/config/configfile");
    }
    if (user_role3 == "0") {
        $("#enter_count").attr("onclick", "show_auth_modal()");
    }
    else {
        if (username == "wangjie" || username == "wangjie2" || username == "anfeng" || username == "anfeng2"
          || username == "ihangmei1" || username == "ihangmei2" || username == "ihangmei3"
          || username == 'beiyou888'){
            $("#enter_count").attr("href", "/operatedata");
        }
        else{
            $("#enter_count").attr("href", "/trend");    
        }
    }
    if (user_role4 == "0") {
        $("#enter_operate").attr("onclick", "show_auth_modal()");
    }
    else {
        $("#enter_operate").attr("href", "/allgame");
    }
    if (user_role5 == "0") {
        $("#enter_service").attr("onclick", "show_auth_modal()");
    }
    else {
        var user_custom = $.cookie("user_custom");
        var url_t = "";
        if (user_custom == "") {
            url_t = custom_left_type["1"]["url"];
        }
        else{
            var custom_split = user_custom.split("|");
            url_t = custom_left_type[custom_split[0]]["url"];
        }
        $("#enter_service").attr("href", url_t);
    }
};

setSystem();

