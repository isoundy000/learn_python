/**
 * Created by wangrui on 17/3/20.
 */



$("#del_source").on("click", function (e) {
    e.preventDefault();
    var success = function(data){
        if (data["status"] == "success"){
            Common.alert_message($("#error_modal"), 1, "删除成功");
        }
        else{
            Common.alert_message($("#error_modal"), 0, "删除失败");
        }
    };
    var del_password = $("#del_password").val();
    if (del_password == "sanguo_passwd"){
        my_ajax(true, "/deletesource", 'get', {}, true, success);
    }
    else{
        Common.alert_message($("#error_modal"), 0, "密码错误.");
    }

});