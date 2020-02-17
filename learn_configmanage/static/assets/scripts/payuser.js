/**
 * Created by wangrui on 15/11/18.
 */
display_left_count();
handleDatePickers();

var $partner = $("#partner_list");
var $vip_game_server = $('#vip_game_server');
var $vip_partner_list = $('#vip_partner_list');
var total_user_channel = $("#user_channel").val();

var $vip_data_table = $('#vip_data_table');

var $btn_query_vip_data = $('#btn_query_vip_data');

getGameServerData($vip_game_server, 2);
setPartnerData(total_user_channel, $partner);

$vip_partner_list.multiselect({
    numberDisplayed: 10,
    includeSelectAllOption: true,
    selectAllText: '全部渠道',
    allSelectedText: '全部渠道',
    selectAllValue: 0,
    enableFiltering: true,
    nonSelectedText: "==请选择==",
    buttonWidth: '100%',
    maxHeight: 250,
    enableClickableOptGroups: true,
    enableCollapsibleOptGroups: true,
    collapseOptGroupsByDefault: true

});

$.ajax({
    url: '/get/channel_groups',
    type: 'get',
    dataType: 'json',
    async: false,
    data:{'user_channel': total_user_channel},
    success: function (result) {
        if (result.length>0){
            var tag_json = {};
            var channel_data = [];
            if (parseInt(total_user_channel) < 0){
                for (var i=0;i<result.length;i++){
                    if (!(result[i]['platform_group'] in tag_json)){
                        tag_json[result[i]['platform_group']] = channel_data.length;
                        channel_data.push({label: result[i]['platform_group'], children: []})
                    }
                    channel_data[tag_json[result[i]['platform_group']]]['children'].push(
                        {"label":result[i]['p_name'],"value":result[i]['p_id']}
                    );
                }

            }else{
                for (var h=0;h<result.length;h++){
                    channel_data.push(
                        {"label":result[h]['name'],"value":result[h]['id']}
                    );
                }

            }

            $vip_partner_list.multiselect('dataprovider',channel_data);
            $vip_partner_list.multiselect('selectAll',false);
            $vip_partner_list.multiselect('updateButtonText');

        }

    }
});


$partner.on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    query_pay_user();
});

$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));


var G_DATA = null;

function tick_format(v){
    var temp = G_DATA[v][0].split("-");
    return temp[1] + "-" + temp[2];
}

$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_pay_user();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_pay_user();
});

function query_pay_user(){
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var user_channel = $("#user_channel").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querypayuser',
        data: {
            user_channel: user_channel,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI($('.page-content'));
            var str_info = "";
            var draw_data1 = [];
            var draw_data2 = [];
            G_DATA = data;

            for(var i in data){
                str_info += "<tr>";
                str_info += "<td>" + data[i][0] + "</td>";
                str_info += "<td>" + data[i][1] + "</td>";
                str_info += "<td>" + data[i][2] + "</td>";
                var percent = 0;
                if (data[i][3] != 0){
                    percent = (data[i][2] / data[i][3] * 100).toFixed(2)
                }
                str_info += "<td>" + percent + "%</td>";
                str_info += "</tr>";
                draw_data1.push([i, data[i][1]]);
                draw_data2.push([i, data[i][2]]);
            }
            var data_set = [
                {
                    label: "新增付费用户",
                    data: draw_data1
                },
                {
                    label: "付费用户",
                    data: draw_data2
                }
            ];
            DrawLineChart(data_set, $("#chart_pay_user"), tick_format);
            $("#pay_user_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
}
query_pay_user();


function hover(x, y){
    return G_DATA[x][0] + ":" + y;
}

chart_hover_display($("#chart_pay_user"), hover);


$("#export_button").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#pay_user_title"), $("#pay_user_list"), "付费用户");
});


// 生成vip数据表格
var $vip_grade = $('#vip_grade');
var re = /^[0-9]+.?[0-9]*/;
var show_vip_table = function () {
    var vip_grade = $vip_grade.val();
    if (!re.test(vip_grade)){
        vip_grade = '';
    }
    var $all_channel_box = $vip_partner_list.next().find('input[type="checkbox"]').eq(0);
    var ajax_data = {
        "url": "/get/vip_users",
        "type": "POST",
        "data": {"server_id": $vip_game_server.val(),
                 "vip_grade": vip_grade,"channel_list": $all_channel_box.is(':checked') ? total_user_channel : $vip_partner_list.val().join(',')},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#task_table_processing').hide();
        }
        // "dataSrc": function (result) {
        //     if (result['status'] === 'success'){
        //         return result['data']
        //     } else {
        //         return []
        //     }
        // }
    };
    var columns = [{"title":"vip等级", "data": "vip"}, {"title": "区服", "data": "game_id"},{"title": "角色编号", "data": "rid"}, {"title": "角色名", "data": "name"}];
    var columnDefs = [];
    return back_page_table($vip_data_table, ajax_data, columns,columnDefs,false);
};

