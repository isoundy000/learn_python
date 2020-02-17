/**
 * Created by wangrui on 15/1/8.
 */
get_left_game_server();
setLeftStyle();
var userQueryValidation = function(){
    var form1 = $("#user_query_form");
    var rules = {
        user_id:{
            required: true
        }
    };
    var messages = {
        user_id:{
            required: "请输入账号ID或者账号"
        }
    };
    var submitFunc = function(){
        var user_account = $("#user_id").val();
        var page_content = $('.page-content');
        App.blockUI(page_content, false);

        $.ajax({
            type: 'get',
            url: '/queryuid',
            data: {account: user_account},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data.length != 0){
                    for(var i=0; i<data.length; i++) {
                        str_info += "<tr>";
                        str_info += "<td>" + data[i]["uid"] + "</td>";
                        str_info += "<td>" + data[i]["account"] + "</td>";
                        str_info += "<td>" + data[i]["gid"] + "区:" + data[i]["gamename"] + "</td>";
                        str_info += "<td>" + data[i]["recharge"] + "</td>";
                        str_info += "<td>" + data[i]["rid"] + "</td>";
                        str_info += "<td>" + data[i]["name"] + "</td>";
                        str_info += "<td>" + data[i]["level"] + "</td>";
                        str_info += "<td>" + data[i]["vip"] + "</td>";
                        str_info += "<td>" + data[i]["gold"] + "</td>";
                        str_info += "<td>" + data[i]["coin"] + "</td>";
                        str_info += "<td>" + data[i]["createtime"] + "</td>";
                        str_info += "<td>";
                        str_info += "<button onclick=\"reset_password(" + data[i]["uid"] + ")\" class=\"btn default btn-xs blue\" >重置密码<i class=\"fa fa-gear\"></i></button>";
                        str_info += "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="12" class="text-center"><span class="label label-danger">无此账户信息，请重新输入</span></td>';
                    str_info += '</tr>';
                }
                $("#account_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        });
    };
    commonValidation(form1, rules, messages, submitFunc);
};

userQueryValidation();

var reset_password = function(uid){
    $.ajax({
        type: 'get',
        url: '/resetpassword',
        data: {uid: uid},
        dataType: 'JSON',
        success: function (data) {
            if(data["status"] >= 0){
                Common.alert_message($("#error_modal"), 1, "重置成功");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "重置失败");
            }
        },
        error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
    });
};


$("#reset_pass").bind("click", function(e){
    e.preventDefault();
    
});