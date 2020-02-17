/**
 * Created by liuzhaoyang on 15/10/20.
 */

var auth_upload = function (div_modal) {
    var user_upload = $.cookie("user_upload");
    if (user_upload == "1") {
        div_modal.modal("show");
    }
    else {
        Common.alert_message($("#error_modal"), 0, "无权限上传文件");
    }
};


//上传文件
$("#upload_world_file").on("click", function (e) {
    e.preventDefault();
    auth_upload($("#upload_world_modal"));
});

var tag = 0;

var world_choose_div1 = $("#world_choose_div1").html();
$("#world_upload_value").on("click", function (e) {
    e.preventDefault();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajaxFileUpload(
        {
            url: "/uploadworldfile",
            secureuri: false,
            type: "post",
            fileElementId: "world_excel_file",
            dataType: 'json',
            success: function (data) {
                App.unblockUI(page_content);
                $("#world_choose_div1").html(world_choose_div1);
                $("#upload_world_modal").modal("hide");
                if (data["status"] == false) {
                    Common.alert_message($("#error_modal"), 0, "配置文件错误,工作表[" + data["sheet_name"] +
                        "],错误信息:[" + data["errinfo"] + "]");
                }
                else {
                    Common.alert_message($("#error_modal"), 1, "配置文件检测正确");
                    tag = 1;
                    world_drop();
                }

            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});

var drop_result = null;

var world_grade = '';
var stay_days = '';
var player_type = new Array();
player_type[1] = '非R';
player_type[2] = '小R';
player_type[3] = '大R';

//世界掉落模拟等级列表
var world_drop = function () {
    //滞留天数==============================
    if (stay_days != '') {
        $('#stay_days').html(stay_days);
    } else {
        stay_days += "<option value='0'>请选择</option>";
        for (var i = 1; i <= 100; i++) {
            stay_days += "<option value='" + i + "'>" + i + " 天 </option>";
        }
        $('#stay_days').html(stay_days);
        $('#stay_days').searchableSelect();

    }
    //======================================

    var world_drop_grade = $('#world_drop_grade');

    if (world_grade != '') {
        world_drop_grade.html(world_grade);
    } else {
        $.ajax({
                type: 'get',
                url: '/world_drop_grade',
                data: {tag: tag},
                dataType: 'JSON',
                success: function (data) {
                    if (data.length != 0) {
                        world_grade = "<option value='0'>请选择</option>";
                        for (var i = 0; i < data.length; i++) {
                            world_grade += "<option value='" + data[i] + "'>" + data[i] + "</option>";
                        }
                        world_drop_grade.html(world_grade);
                        world_drop_grade.searchableSelect();
                    }
                    else{
                        Common.alert_message($("#error_modal"), 0, "配置文件不存在,请先上传配置文件.");
                    }
                    tag = 0
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        );
    }

};
world_drop();


//世界模拟掉落查询
$("#world_config_file").on("click", function (e) {
    e.preventDefault();

    var world_drop_grade = $('#world_drop_grade').val();
    var game_player_type = $('#game_player_type').val();
    var stay_days = $('#stay_days').val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    if (world_drop_grade == 0) {
        App.unblockUI(page_content);
        Common.alert_message($("#error_modal"), 1, "模拟玩家等级不能为空");
    } else {

        $.ajax({
                type: 'get',
                url: '/world_drop_query',
                data: {
                    world_drop_grade: world_drop_grade,
                    game_player_type: game_player_type,
                    stay_days: stay_days
                },
                dataType: 'JSON',
                success: function (data) {
                    App.unblockUI(page_content);
                    if (data['total_currency'].length != 0 && data['num'] != 0) {

                        var world_drop_gd = "<tr>";
                        world_drop_gd += "<td class='active'>" + player_type[game_player_type] + "</td>";
                        world_drop_gd += "<td class='success'>" + data['power'] + "</td>";
                        world_drop_gd += "<td class='warning'>" + data['need_time'] + "</td>";
                        world_drop_gd += "</tr>";

                        var world_drop_money = "<tr>";
                        world_drop_money += "<td class='active'>" + data['total_currency'][1]['num'] + "</td>";
                        world_drop_money += "<td class='success'>" + data['total_currency'][2]['num'] + "</td>";
                        world_drop_money += "<td class='success'>" + data['total_currency'][2]['value'] + "</td>";
                        world_drop_money += "<td class='warning'>" + data['total_currency'][0]['num'] + "</td>";
                        world_drop_money += "<td class='warning'>" + data['total_currency'][0]['value'] + "</td>";
                        world_drop_money += "</tr>";

                        var equip_total_value = "<p>" + data['total_equip']['total_value'] + "</p>";
                        var prop_total_value = "<p>" + data['total_prop']['total_value'] + "</p>";
                        var general_total_value = "<p>" + data['total_general']['total_value'] + "</p>";

                        var world_drop_goods = '';
                        for (var i = 0; i < data['num']; i++) {
                            world_drop_goods += "<tr>";
                            if (data['total_equip_num'] - 1 >= i) {

                                world_drop_goods += "<td class='active'>" + data['total_equip'][i]['name'] + "</td>";
                                world_drop_goods += "<td class='active'>" + data['total_equip'][i]['num'] + "</td>";
                                world_drop_goods += "<td class='active'>" + data['total_equip'][i]['value'] + "</td>";
                            } else {
                                world_drop_goods += "<td class='active'>" + "</td>";
                                world_drop_goods += "<td class='active'>" + "</td>";
                                world_drop_goods += "<td class='active'>" + "</td>";
                            }
                            if (data['total_prop_num'] - 1 >= i) {

                                world_drop_goods += "<td class='success'>" + data['total_prop'][i]['name'] + "</td>";
                                world_drop_goods += "<td class='success'>" + data['total_prop'][i]['num'] + "</td>";
                                world_drop_goods += "<td class='success'>" + data['total_prop'][i]['value'] + "</td>";
                            } else {
                                world_drop_goods += "<td class='success'>" + "</td>";
                                world_drop_goods += "<td class='success'>" + "</td>";
                                world_drop_goods += "<td class='success'>" + "</td>";
                            }
                            if (data['total_general_num'] - 1 >= i) {

                                world_drop_goods += "<td class='warning'>" + data['total_general'][i]['name'] + "</td>";
                                world_drop_goods += "<td class='warning'>" + data['total_general'][i]['num'] + "</td>";
                                world_drop_goods += "<td class='warning'>" + data['total_general'][i]['value'] + "</td>";
                            } else {
                                world_drop_goods += "<td class='warning'>" + "</td>";
                                world_drop_goods += "<td class='warning'>" + "</td>";
                                world_drop_goods += "<td class='warning'>" + "</td>";
                            }
                            world_drop_goods += "</tr>";
                        }

                        drop_result = data;

                        $('#equip_values').html(equip_total_value);
                        $('#prop_values').html(prop_total_value);
                        $('#general_values').html(general_total_value);


                        $('#world_power_list').html(world_drop_gd);
                        $('#world_drop_coin').html(world_drop_money);
                        $('#world_drop_list').html(world_drop_goods);
                    }
                },
                error: function (XMLHttpRequest) {
                    App.unblockUI(page_content);
                    error_func(XMLHttpRequest);
                }
            }
        );
    }
});

function isEmptyObject(o) {
    for (var n in o) {

        return true;
    }
    return false;
}

//保存查询结果
$('#save_result').on("click", function (e) {
    e.preventDefault();

    var world_drop_grade = $('#world_drop_grade').val();
    var game_player_type = $('#game_player_type').val();
    var stay_days = $('#stay_days').val();
    if (isEmptyObject(drop_result)) {
        var page_content = $('.page-content');
        App.blockUI(page_content, false);
        $.ajax({
            type: "post",
            url: "/save_result",
            data: {
                world_drop_grade: world_drop_grade,
                game_player_type: game_player_type,
                stay_days: stay_days,
                result: JSON.stringify(drop_result)
            },
            dataType: 'json',
            success: function (data) {
                App.unblockUI(page_content);
                if (data["status"] == false) {
                    Common.alert_message($("#error_modal"), 0, "保存失败");
                }
                else {
                    Common.alert_message($("#error_modal"), 1, "保存成功");
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        });
    } else {
        Common.alert_message($("#error_modal"), 1, "查询数据为空");
    }
});