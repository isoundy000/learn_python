/**
 * Created by wangrui on 15/1/26.
 */

var $tab2_select_gameserver = $('#tab2_select_gameserver');
var $tab2_start_date = $('#tab2_start_date');
var $tab2_end_date = $('#tab2_end_date');
var $tab2_table = $('#tab2_table');

handleDatePickers();
display_left_count();
getGameServerData($("#select_gameserver"), 2);
getGameServerData($("#select_gameserver_top"), 2);

setPartnerData($("#user_channel").val(), $("#partner_list"));
setPartnerData($("#user_channel").val(), $("#partner1_list"));
//setPartnerData($("#user_channel").val(), $("#partner2_list"));
setPartnerData($("#user_channel").val(), $("#partner3_list"));

// var exchange_num = get_exchange();
// $("#huilv").html("汇率:" + exchange_num);
//
// $("#change_recharge").on("click", function(e){
//     e.preventDefault();
//     if ($(this).hasClass("blue")){
//         queryRevenue(2);
//         $(this).removeClass("blue");
//         $(this).addClass("purple");
//         $(this).html("印尼盾");
//     }
//     else{
//         queryRevenue(1);
//         $(this).removeClass("purple");
//         $(this).addClass("blue");
//         $(this).html("人民币");
//     }
// });

$("#partner_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    $("#query_button").click();
});

$("#partner1_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $("#top_query_btn").click();
});

$("#partner2_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $("#query_button_userlife").click();
});

$("#partner3_list").on("change", function (e) {
    e.preventDefault();
    $("#user_channel").val($(this).val());
    $("#query_button_type").click();
});

$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));

$("#recharge_start_date").val(getNowFormatDate(1));
$("#recharge_end_date").val(getNowFormatDate(0));

getGameServerData($("#select_game"), 2);
$("#appoint_date").val(getNowFormatDate(7));
$("#count_date").val(getNowFormatDate(0));

getGameServerData($("#gameserver_type"), 2);
$("#start_type_date").val(getNowFormatDate(7));
$("#end_type_date").val(getNowFormatDate(0));

getGameServerData($tab2_select_gameserver, 2);
$tab2_start_date.val(getNowFormatDate(6));
$tab2_end_date.val(getNowFormatDate(0));

//充值档类型统计
$("#query_button_type").on("click", function (e) {
    e.preventDefault();
    var start_date = $("#start_type_date").val();
    var end_date = $("#end_type_date").val();
    var server_id = $("#gameserver_type").val();
    var user_channel = $("#user_channel").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryrevenuetype',
        data: {
            user_channel: user_channel,
            server_id: server_id,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var dataset1 = [];
            var dataset2 = [];
            if (data["data"].length != 0) {
                for (var i = 0; i < data["data"].length; i++) {
                    str_info += "<tr>";
                    var recharge = parseInt(data["data"][i][0]) + "元";
                    str_info += "<td>" + recharge + "</td>";
                    str_info += "<td>" + data["data"][i][1] + "</td>";
                    var c = commonPercent(data["data"][i][1], data["count"]);
                    var p = commonPercent(data["data"][i][2], data["person"]);
                    str_info += "<td>" + c + "%</td>";
                    str_info += "<td>" + data["data"][i][2] + "</td>";
                    str_info += "<td>" + p + "%</td>";
                    str_info += "</tr>";
                    var temp = {label: recharge,
                        data: c
                    };
                    var temp2 = {label: recharge,
                        data: p
                    };
                    dataset1.push(temp);
                    dataset2.push(temp2);
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="5" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }

            $("#revenue_type_list").html(str_info);
            drawPieChart($("#count_chats"), dataset1);
            drawPieChart($("#person_chats"), dataset2);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


$("#a_recharge_type").on("click", function (e) {
    e.preventDefault();
    $("#query_button_type").click();
});

function queryRevenue(tag){
    
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var server_id = $("#select_gameserver").val();
    var user_channel = $("#user_channel").val();
    var r_yin = 1;
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryrevenue',
        data: {
            user_channel: user_channel,
            server_id: server_id,
            start_date: start_date,
            end_date: end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var total_recharge = 0;
            var total_need = 0;
            var total_new_apa = 0;
            var total_num = 0;
            var total_valid_num = 0;
            for (var i = 0; i < data[0].length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + data[0][i]["date"] + "</td>";
                var total_money = parseFloat(data[0][i]["total_money"]);
                var need_money = parseFloat(data[0][i]["need_money"]);
                if (tag == 2){
                    total_money = (total_money / r_yin).toFixed(2);
                    need_money = (need_money / r_yin).toFixed(2);
                }
                str_info += "<td>" + total_money + "</td>";
                str_info += "<td>" + need_money + "</td>";

                str_info += "<td>" + data[0][i]["apa"] + "</td>";
                str_info += "<td>" + data[0][i]["new_apa"] + "</td>";
                str_info += "<td>" + data[0][i]["total_num"] + "</td>";
                if (data[0][i]["total_num"] != 0) {
                    str_info += "<td>" + data[0][i]["valid_num"] + "</td>";
                    str_info += "<td>" + commonPercent(data[0][i]["valid_num"], data[0][i]["total_num"]) + "%</td>";
                }
                else {
                    str_info += "<td>0</td>";
                    str_info += "<td>0%</td>";
                }

                if (data[0][i]["apa"] != 0) {
                    str_info += "<td>" + (total_money / data[0][i]["apa"]).toFixed(2) + "</td>";
                    str_info += "<td>" + (need_money / data[0][i]["apa"]).toFixed(2) + "</td>";
                }
                else {
                    str_info += "<td>0</td>";
                    str_info += "<td>0</td>";
                }
                str_info += "</tr>";
                total_recharge += parseFloat(total_money);
                total_need += parseFloat(need_money);

                total_valid_num += parseInt(data[0][i]["valid_num"]);
                total_new_apa += parseInt(data[0][i]["new_apa"]);
                total_num += parseInt(data[0][i]["total_num"]);
            }
            str_info += "<tr class=\"success\">";
            str_info += "<td>总计</td>";
            str_info += "<td>" + total_recharge.toFixed(2) + "</td>";
            str_info += "<td>" + total_need.toFixed(2) + "</td>";
            str_info += "<td>" + data[1] + "</td>";
            str_info += "<td>" + total_new_apa + "</td>";
            str_info += "<td>" + total_num + "</td>";
            if (total_num != 0) {
                str_info += "<td>" + total_valid_num + "</td>";
                str_info += "<td>" + commonPercent(total_valid_num, total_num) + "%</td>";
            }
            else {
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
            }

            if (data[1] != 0) {
                str_info += "<td>" + (total_recharge / data[1]).toFixed(2) + "</td>";
                str_info += "<td>" + (total_need / data[1]).toFixed(2) + "</td>";
            }
            else {
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
            }
            str_info += "</tr>";

            $("#revenue_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
}


//充值数据统计
$("#query_button").on("click", function (e) {
    e.preventDefault();
    queryRevenue(1);
});

$('#btn_down_ranking_data').click(function () {
    $('#role_recharge_list_table').tableExport({
        type:'excel',
        escape:'false',
        excelstyles: ['border-bottom', 'border-top', 'border-left', 'border-right'],
        fileName: '充值排行榜'
    });
});


$("#top_query_btn").on("click", function (e) {
    e.preventDefault();
    var start_date = $("#recharge_start_date").val();
    var end_date = $("#recharge_end_date").val();
    var top_select = $("#top_select").val();
    var user_channel = $("#user_channel").val();
    var game_id = $("#select_gameserver_top").val();

    var page_content = $('.page-content');
    top_select = Number(top_select);
    if (!isNaN(top_select) && top_select <10000 && top_select>0){
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/querytoprecharge',
            data: {start_date: start_date,
                end_date: end_date,
                user_channel: user_channel,
                game_id: game_id,
                top_select: top_select},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if (data.length != 0) {
                    for (var d = 0; d < data.length; d++) {
                        str_info += "<tr>";
                        str_info += "<td>" + data[d]["game"] + "</td>";
                        str_info += "<td>" + data[d]["name"] + "</td>";
                        str_info += "<td>" + data[d]["recharge"] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else {
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#role_recharge_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        })
    }else{
        alert('top值为数字且不能大于10000')
    }   
});

$("#query_button_userlife").bind("click", function (e) {
    e.preventDefault();
    var count_type = $("input[name='query_type']:checked").val();
    var server = $("#select_game").val();
    var user_channel = $("#user_channel").val();
    var s_date = $("#appoint_date").val();
    var e_date = $("#count_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryuserlife',
        data: {count_type: count_type,
            user_channel: user_channel,
            server: server,
            s_date: s_date,
            e_date: e_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            str_info += "<tr>";
            str_info += "<td>" + data["login"] + "</td>";
            str_info += "<td>" + data["t_recharge"] + "</td>";
            str_info += "<td>" + data["recharge_num"] + "</td>";
            str_info += "<td>" + data["total_recharge_num"] + "</td>";
            str_info += "<td>" + data["total_recharge"] + "</td>";
            str_info += "<td>" + (data["total_recharge_num"] / data["total_login"] * 100.0).toFixed(2) + "%</td>";
            str_info += "</tr>";
            $("#life_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


$("#query_button").click();

$("#a_recharge_top").on("click", function (e) {
    e.preventDefault();
    $("#top_query_btn").click();
});

$("#a_userlife").on("click", function (e) {
    e.preventDefault();
    $("#query_button_userlife").click();
});


Date.prototype.format = function() {
      var s = '';
      var mouth = (this.getMonth() + 1)>=10?(this.getMonth() + 1):('0'+(this.getMonth() + 1));
      var day = this.getDate()>=10?this.getDate():('0'+this.getDate());
      s += this.getFullYear() + '-'; // 获取年份。
      s += mouth + "-"; // 获取月份。
      s += day; // 获取日。
      return (s); // 返回日期。
  };

function getAll(begin, end) {
  var date_list = [];
  var ab = begin.split("-");
  var ae = end.split("-");
  var db = new Date();
  db.setUTCFullYear(ab[0], ab[1] - 1, ab[2]);
  var de = new Date();
  de.setUTCFullYear(ae[0], ae[1] - 1, ae[2]);
  var unixDb = db.getTime();
  var unixDe = de.getTime();
  for (var k = unixDb; k <= unixDe;) {
      date_list.push( (new Date(parseInt(k))).format() );
      k = k + 24 * 60 * 60 * 1000;
  }
  return date_list
}







var package_recharge_record = function () {
    var game_id = $tab2_select_gameserver.val();
    var start_date = $tab2_start_date.val();
    var end_date = $tab2_end_date.val();
    var ajax_data = {
        "url": "/get/package/recharge",
        "type": "GET",
        "data":{game_id: game_id, start_date: start_date, end_date: end_date},
        "error": function(jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            $('#cut_partition_record_tab_processing').hide();
        },
        "dataSrc": function (result) {

            if (result.status === 'ok' ) {
                if (result.data === null){
                    return []
                }else{
                    var data = [];

                    var date_list = getAll(start_date, end_date);
                    for (var i=0;i<date_list.length;i++){
                        var amount_value = {'com.ldfs.zyj.apple': 0, 'com.dyc.zyj.apple': 0};
                        for (var d=0;d<result.data.length;d++){

                            if (result.data[d]['date'] === date_list[i] ){
                                console.log(1111);
                                if (result.data[d]['package_name'] === 'com.ldfs.zyj.apple'){
                                    amount_value['com.ldfs.zyj.apple'] += result.data[d]['amount']
                                }else if (result.data[d]['package_name'] === 'com.dyc.zyj.apple'){
                                    amount_value['com.dyc.zyj.apple'] += result.data[d]['amount']
                                }

                            }
                        }
                        data.push([date_list[i], amount_value['com.ldfs.zyj.apple'], amount_value['com.dyc.zyj.apple']])
                    }
                    console.log(data);
                    return data
                }
            }else {

                return []
            }
        }
    };
    var columns = [{"title": "日期"},{"title": "作妖计"},{"title": '作妖计HD'}];
    var columnDefs = [];
    return new_front_page_table($tab2_table, ajax_data,columns,columnDefs,false);
};
$('#tab2_query_button').click(function () {
    package_recharge_record()
});