/**
 * Created by liuzhaoyang on 15/10/21.
 */

var getExcelFile = function () {
    var sAjaxSource = "/world_drop_query_record";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "player_type",
            'sClass': 'center',
            "sTitle": "玩家类型"
        },
        {
            "mDataProp": "player_grade",
            'sClass': 'center',
            "sTitle": "玩家等级"
        },
        {
            "mDataProp": "stay_days",
            'sClass': 'center',
            "sTitle": "滞留天数"
        },
        {
            "mDataProp": "save_date",
            'sClass': 'center',
            "sTitle": "查询日期"
        },
        {
            "mDataProp": "drop_result",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_rule(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">查询 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_rule(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    dataTablePage($("#query_record"), aoColumns, sAjaxSource, {}, false, null);
};
getExcelFile();

var mod_rule = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#query_record").dataTable().fnGetData(nRoW);
    var drop_result = $.parseJSON(data["drop_result"]);
    var player_type = data["player_type"];
    var player_grade = data["player_grade"];
    var stay_days = data["stay_days"];

    var record_payer_type = '<input type="text" class="form-control" value="' + player_type + '" placeholder="Disabled" disabled>';
    var record_payer_grade = '<input type="text" class="form-control" value="' + player_grade + '级" placeholder="Disabled" disabled>';
    var record_stay_days = '<input type="text" class="form-control" value="' + stay_days + '天" placeholder="Disabled" disabled>';

    var world_drop_gd = "<tr>";
    world_drop_gd += "<td class='active'>" + player_type + "</td>";
    world_drop_gd += "<td class='success'>" + drop_result['power'] + "</td>";
    world_drop_gd += "<td class='warning'>" + drop_result['need_time'] + "</td>";
    world_drop_gd += "</tr>";

    var world_drop_money = "<tr>";
    world_drop_money += "<td class='active'>" + drop_result['total_currency'][1]['num'] + "</td>";
    world_drop_money += "<td class='success'>" + drop_result['total_currency'][2]['num'] + "</td>";
    world_drop_money += "<td class='success'>" + drop_result['total_currency'][2]['value'] + "</td>";
    world_drop_money += "<td class='warning'>" + drop_result['total_currency'][0]['num'] + "</td>";
    world_drop_money += "<td class='warning'>" + drop_result['total_currency'][0]['value'] + "</td>";
    world_drop_money += "</tr>";

    var equip_total_value = "<p>" + drop_result['total_equip']['total_value'] + "</p>";
    var prop_total_value = "<p>" + drop_result['total_prop']['total_value'] + "</p>";
    var general_total_value = "<p>" + drop_result['total_general']['total_value'] + "</p>";

    var world_drop_goods = '';
    for (var i = 0; i < drop_result['num']; i++) {
        world_drop_goods += "<tr>";
        if (drop_result['total_equip_num'] - 1 >= i) {

            world_drop_goods += "<td class='active'>" + drop_result['total_equip'][i]['name'] + "</td>";
            world_drop_goods += "<td class='active'>" + drop_result['total_equip'][i]['num'] + "</td>";
            world_drop_goods += "<td class='active'>" + drop_result['total_equip'][i]['value'] + "</td>";
        } else {
            world_drop_goods += "<td class='active'>" + "</td>";
            world_drop_goods += "<td class='active'>" + "</td>";
            world_drop_goods += "<td class='active'>" + "</td>";
        }
        if (drop_result['total_prop_num'] - 1 >= i) {

            world_drop_goods += "<td class='success'>" + drop_result['total_prop'][i]['name'] + "</td>";
            world_drop_goods += "<td class='success'>" + drop_result['total_prop'][i]['num'] + "</td>";
            world_drop_goods += "<td class='success'>" + drop_result['total_prop'][i]['value'] + "</td>";
        } else {
            world_drop_goods += "<td class='success'>" + "</td>";
            world_drop_goods += "<td class='success'>" + "</td>";
            world_drop_goods += "<td class='success'>" + "</td>";
        }
        if (drop_result['total_general_num'] - 1 >= i) {

            world_drop_goods += "<td class='warning'>" + drop_result['total_general'][i]['name'] + "</td>";
            world_drop_goods += "<td class='warning'>" + drop_result['total_general'][i]['num'] + "</td>";
            world_drop_goods += "<td class='warning'>" + drop_result['total_general'][i]['value'] + "</td>";
        } else {
            world_drop_goods += "<td class='warning'>" + "</td>";
            world_drop_goods += "<td class='warning'>" + "</td>";
            world_drop_goods += "<td class='warning'>" + "</td>";
        }
        world_drop_goods += "</tr>";
    }

    $('#record_payer_type').html(record_payer_type);
    $('#record_player_grade').html(record_payer_grade);
    $('#record_stay_days').html(record_stay_days);

    $('#equip_values').html(equip_total_value);
    $('#prop_values').html(prop_total_value);
    $('#general_values').html(general_total_value);

    $('#world_power_list').html(world_drop_gd);
    $('#world_drop_coin').html(world_drop_money);
    $('#world_drop_list').html(world_drop_goods);

    $("#query_drop_record").modal("show");
};

var del_rule = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#query_record").dataTable().fnGetData(nRoW);
    var record_id = data['id'];

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/del_drop_record',
        data: {
            record_id: record_id
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            if (data['status'] = true) {
                getExcelFile();
            } else {
                Common.alert_message($("#error_modal"), 1, "删除失败");
            }
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })

};