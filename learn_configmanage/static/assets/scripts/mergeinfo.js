/**
 * Created by wangrui on 17/3/1.
 */
var $mp_id = $("#mp_id");
var $mid = $("#mid");
var $oid_list = $("#oid_list");
var $listen_ip = $("#listen_ip");
var $game_port = $("#game_port");
var $base_port = $("#base_port");
var $filter_login = $("#filter_login");
var $filter_level = $("#filter_level");
var $merge_modal = $("#merge_modal");
var $div_game_port = $("#div_game_port");
var $div_base_port = $("#div_base_port");
var $div_sql_file = $("#div_sql_file");
var $div_listen_ip = $("#div_listen_ip");
var $div_create_mysql_instance = $("#div_create_mysql_instance");
var $div_world_method = $("#div_world_method");
var $world_method = $("#world_method");
var $create_instance = $("#create_mysql_instance");
var $div_world_ip = $("#div_world_ip");
var $div_world_port = $("#div_world_port");

var $world_ip = $("#world_ip");
var $world_port = $("#world_port");
var $merge_m = $("#merge_m");

$("#add_merge").on("click", function (e) {
    e.preventDefault();
    $mp_id.val("");
    $merge_m.val(1);
    $merge_m.change();

    $create_instance.change();
    $world_method.change();
    $mid.val("");
    $oid_list.val("");
    $listen_ip.val("");
    $game_port.val("");
    $base_port.val("");
    $filter_login.val("");
    $filter_level.val("");
    $merge_modal.modal("show");
});


var query_sql_and_merge = function () {
    var success = function (data) {
        var html = "";
        var html2 = "";
        for(var i = 0; i<data.length; i++){
            if (data[i]["type"] == 1){
                html += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + "</option>";
            }
            else if (data[i]["type"] == 3){
                html2 += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + "</option>";
            }
        }
        $("#select_sql").html(html);
        $("#select_merge").html(html2);
    };
    my_ajax(true, '/update/getsqlandmerge', 'get', {}, true, success);
};
query_sql_and_merge();


$merge_m.on("change", function (e) {
    e.preventDefault();
    var merge_mod = $(this).val();
    if (merge_mod == "1"){
        $div_create_mysql_instance.show();
        $div_world_method.show();
        $div_game_port.show();
        $div_base_port.show();
        $div_sql_file.show();
        $div_listen_ip.show();
    }
    else{
        $div_create_mysql_instance.hide();
        $div_world_method.hide();
        $div_game_port.hide();
        $div_base_port.hide();
        $div_sql_file.hide();
        $div_listen_ip.hide();
    }

    $world_method.change();
});


$world_method.on("change", function (e) {
    e.preventDefault();
    if ($(this).is(":checked")){
        $world_method.prop("checked", true);
        $world_method.parent("span").addClass("checked");
        $div_world_ip.removeClass("hidden");
        $div_world_port.removeClass("hidden");
    }
    else{
        $world_method.prop("checked", false);
        $world_method.parent("span").removeClass("checked");
        $div_world_ip.addClass("hidden");
        $div_world_port.addClass("hidden");
    }
});

var mod_merge = function (mp_id) {
    var success = function (data) {
        $mp_id.val(data["id"]);
        $mid.val(data["mid"]);
        $merge_m.val(data["method"]);
        $merge_m.change();
        if (data["method"] == "1"){
            $listen_ip.val(data["listen_ip"]);
            $world_ip.val(data["world_ip"]);
            $world_port.val(data["world_port"]);
            $("#select_sql").val(data["sql_id"]);
            if (data["world_method"] == 1) {
                $world_method.prop("checked", true);
            }
            else{
                $world_method.prop("checked", false);
            }
            $world_method.change();

            if (data["create_instance"] == 1){
                $create_instance.prop("checked", true);
                $create_instance.parent("span").addClass("checked");
            }
            else{
                $create_instance.prop("checked", false);
                $create_instance.parent("span").removeClass("checked");
            }

            $game_port.val(data["game_port"]);
            $base_port.val(data["base_port"]);
        }
        $("#mysql_version").val(data["mysql_version"]);
        $oid_list.val(data["oid_list"]);
        $("#select_merge").val(data["merge_source"]);
        $filter_level.val(data["filter_level"]);
        $merge_modal.modal("show");
    };
    var data = {
        mp_id: mp_id
    };
    my_ajax(true, "/merge/getoneinfo", 'get', data, true, success);
};


var del_merge = function (mp_id) {
    var success = function (data) {
        if(data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "删除失败");
        }
        get_merge_info();
    };
    var data = {
        mp_id: mp_id
    };
    my_ajax(true, "/merge/deleteinfo", 'get', data, true, success);
};


var merge_prepare = function(mp_id){
    var success = function(data){
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "合服准备失败");
        }
        get_merge_info();
    };
    var data = {
        mp_id: mp_id
    };
    my_ajax(true, "/merge/preparemerge", 'get', data, true, success);
};

var merge_execute = function(mp_id){
    var success = function(data){
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "合服准备失败");
        }
        else{
            Common.alert_message($("#error_modal"), 1, "设置成功");
        }
        get_merge_info();
    };
    var data = {
        mp_id: mp_id
    };
    my_ajax(true, "/merge/executemerge", 'get', data, true, success);
};

var merge_test = function(mp_id){
    var success = function(data){
        if (data["status"] == "fail"){
            Common.alert_message($("#error_modal"), 0, "合服测试失败");
        }
        else{
            Common.alert_message($("#error_modal"), 1, "设置成功,请修改区服信息,重启账号服务.");
        }
        get_merge_info();
    };
    var data = {
        mp_id: mp_id
    };
    my_ajax(true, "/merge/testmerge", 'get', data, true, success);
};



function get_merge_info(){
    var success = function (data) {
        var str_html = "";
        if (data.length != 0){
            for (var i = 0; i <data.length; i++) {
                str_html += "<tr>";
                str_html += "<td>" + data[i]["id"] + "</td>";
                var method = data[i]["method"];
                if (method == 1) {
                    str_html += "<td>一次合服</td>";
                }
                else {
                    str_html += "<td>多次合服</td>";
                }
                str_html += "<td>" + data[i]["mid"] + "</td>";
                str_html += "<td>" + data[i]["oid_list"] + "</td>";
                str_html += "<td>" + data[i]["listen_ip"] + "</td>";
                str_html += "<td>" + data[i]["game_port"] + "</td>";
                str_html += "<td>" + data[i]["base_port"] + "</td>";
                var status = data[i]["status"];
                if (status == "empty"){
                    str_html += "<td>就绪</td>";
                }
                else if(status == "prepare"){
                    str_html += "<td>准备完成</td>";
                }
                else if(status == "execute"){
                    str_html += "<td>执行完成</td>";
                }
                else if(status == "finish"){
                    str_html += "<td>测试完成</td>";
                }
                str_html += "<td>";
                str_html += '&nbsp; <button onclick="mod_merge(' + data[i]["id"] + ')" class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></button>';
                str_html += '&nbsp; <button onclick="del_merge(' + data[i]["id"] + ')" class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></button>';
                str_html += "</td>";
                if (status == "empty"){
                    str_html += '<td><button onclick="merge_prepare(' + data[i]["id"] + ')" class="btn default btn-xs blue" data-toggle="modal">合服准备</button></td>';
                }
                if (status == "prepare" || status == "empty"){
                    str_html += '<td><button onclick="merge_execute(' + data[i]["id"] + ')" class="btn default btn-xs blue" data-toggle="modal">合服执行</button></td>';
                }
                if (status == "prepare" || status == "empty" || status == 'execute'){
                    str_html += '<td><button onclick="merge_test(' + data[i]["id"] + ')" class="btn default btn-xs blue" data-toggle="modal">合服测试</button></td>';
                }
                else{
                    str_html += "<td></td>";
                }
                str_html += "</tr>";
            }
        }
        else{
            str_html += "<tr>";
            str_html += '<td colspan="12" class="text-center"><span class="label label-danger">无数据</span></td>';
            str_html += '</tr>';
        }
        $("#merge_table").html(str_html);
    };
    my_ajax(true, "/merge/getinfo", 'get', {}, true, success);
}
get_merge_info();



$("#btn_confirm").on("click", function (e) {
    e.preventDefault();
    var success = function (data) {
        if (data["status"] == "fail") {
            Common.alert_message($("#error_modal"), 0, "添加错误");
        }
        $merge_modal.modal("hide");
        get_merge_info();
    };
    var mysql_version = $("#mysql_version").val();
    var mp_id = $mp_id.val();
    var merge_mod = $merge_m.val();
    var mid = $mid.val();
    var world_tag = 0;
    var world_check = $world_method.is(":checked");
    if (world_check) {
        world_tag = 1;
    }
    var world_ip = $world_ip.val();
    var world_port = $world_port.val();
    var create_tag = 0;
    if ($create_instance.is(":checked")){
        create_tag = 1;
    }
    var oid_list = $oid_list.val();
    var listen_ip = $listen_ip.val();
    var game_port = $game_port.val();
    var base_port = $base_port.val();
    var filter_level = $filter_level.val();
    var sql_id = $("#select_sql").val();
    var merge_source = $("#select_merge").val();
    console.log(create_tag);
    var data = {
        mp_id: mp_id,
        merge_mode: merge_mod,
        mid: mid,
        oid_list: oid_list,
        listen_ip: listen_ip,
        game_port: game_port,
        base_port: base_port,
        mysql_version: mysql_version,
        filter_level: filter_level,
        world_tag: world_tag,
        world_ip: world_ip,
        world_port: world_port,
        sql_id: sql_id,
        merge_source: merge_source,
        create_tag: create_tag
    };

    my_ajax(true, '/merge/operatemergeinfo', 'post', data, false, success);
});

