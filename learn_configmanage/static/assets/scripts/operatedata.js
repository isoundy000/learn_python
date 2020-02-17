/**
 * Created by wangrui on 15/1/27.
 */

display_left_count();


function hide_channel_data() {
    var user_session = $.cookie("user_session");
    if (user_session == "wangjie" || user_session == "wangjie2"
        || user_session == "anfeng" || user_session == "anfeng2"
       || user_session == "ihangmei1" || user_session == "ihangmei2" || user_session == "ihangmei3"
        || user_session == "beiyou888" || user_session == "jx_yd"
        || user_session == "huanwenios" || user_session == "zhisheng"
        || user_session == "huanwengp5" || user_session == "huanwengp6" ||user_session == "huanwengp8" ){
        $("#a_channel").hide();
    }
}
hide_channel_data();


handleDatePickers();

$("#q_date").val(getNowFormatDate(1));
$("#login_start_date").val(getNowFormatDate(7));
$("#login_end_date").val(getNowFormatDate(0));
$("#pay_date").val(getNowFormatDate(0));
//$("#recharge_date").val(getNowFormatDate(1));
getGameServerData($("#select_gameserver"), 2);
getGameServerData($("#select_gameserver1"), 2);
getGameServerData($("#select_gameserver2"), 2);

var $channel_start_date = $('#channel_start_date');
var $channel_end_date = $('#channel_end_date');
var $partner3_list = $("#partner3_list");
$("#start_date").val(getNowFormatDate(7));
$("#end_date").val(getNowFormatDate(0));
$("#channel_date").val(getNowFormatDate(0));



setPartnerData($("#user_channel").val(), $("#partner_list"));
setPartnerData($("#user_channel").val(), $("#partner1_list"));
setPartnerData($("#user_channel").val(), $("#partner2_list"));


$partner3_list.multiselect({
    numberDisplayed: 10,
    enableFiltering: true,
    nonSelectedText: "==请选择==",
    buttonWidth: '100%',
    selectAllNumber: false,
    onChange: function(option, checked) {
        if (option.val() === '0' && checked){
            var SelectedOptions = $('#partner3_list option').filter(function() {
                return $(this).is(':selected');
              });

            SelectedOptions.each(function(a, b) {
                var s_data = $(b).val();
                if ( s_data !== '0'){
                    $partner3_list.multiselect('deselect', s_data);
                }
            });

        }else {
          $partner3_list.multiselect('deselect', '0');
        }

    },
    allSelectedText:'全部渠道',
    maxHeight: 250
});
if ($("#user_channel").val() === '0'){
    // $(".actions .btn-group").removeClass("hide");
    var channel_data = getChannelData();
    channel_data.unshift( {"label": '全部渠道',"value": '0'} );
    $partner3_list.multiselect('dataprovider', channel_data);
    $partner3_list.multiselect('select', '0');
}else{
    $('#partner3_list_from').hide()

}

$("#partner_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner_list").val());
    $("#query_button").click();
});

$("#partner1_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner1_list").val());
    $("#query_login").click();
});

$("#partner2_list").on("change", function(e){
    e.preventDefault();
    $("#user_channel").val($("#partner2_list").val());
    $("#pay_query").click();
});


$("#query_count").on("click", function(e){
    e.preventDefault();
    var user_channel = $('#partner3_list_from').is(':hidden') ? $("#user_channel").val() : $partner3_list.val().join(',');
    var select_gameserver = $("#select_gameserver").val();
    var count_start_date = $("#start_date").val();
    var count_end_date = $("#end_date").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryregistercount',
        data: {user_channel: user_channel,
               select_gameserver: select_gameserver,
               start_date: count_start_date,
               end_date: count_end_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var regist_total = 0;
            var role_total = 0;
            var new_total = 0;

            var second_total = 0;
            var three_total = 0;
            var four_total = 0;
            var five_total = 0;
            var six_total = 0;
            var seven_total = 0;
            var week_total = 0;

            var reg_pay_total = 0;
            var reg_pay_num_total = 0.0;
            var recharge_total = 0.0;
            var temp_total = 0;

            var add_second_total_retain = 0;
            var add_three_total_retain = 0;
            var add_seven_total_retain = 0;
            var seven_total_ltv = 0;

            if (data[0].length != 0 ){
                var temp = "";
                if (select_gameserver == "0") {
                    temp = "regist";
                }
                else {
                    temp = "create_role";
                }
                for (var i = 0; i < data[0].length; i ++ ){
                    str_info += "<tr>";
                    str_info += "<td>" + data[0][i]["date"] + "</td>";
                    str_info += "<td>" + data[0][i][temp] + "</td>";
                    str_info += "<td>" + data[0][i]["create_role"] + "</td>";
                    str_info += "<td>" + data[0][i]["new_login"] + "</td>";
                    str_info += "<td>" + data[0][i]["active"] + "</td>";
                    var reg_pay_percent = 0;


                    if (data[0][i][temp] != 0){
                        str_info += "<td>"  + parseFloat(data[0][i]["second_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["three_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["four_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["five_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["six_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["seven_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>" + data[0][i]["week_login"] + "/" + parseFloat(data[0][i]["week_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        reg_pay_percent = parseFloat(data[0][i]["reg_pay_user"] / data[0][i][temp] * 100).toFixed(2);

                    }
                    else{
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                    }

                    str_info += "<td>" + data[0][i]["pay_user"]  + "</td>";
                    var pay_percent = 0;
                    var arpu = 0;
                    if (data[0][i]["active"] != 0){
                        pay_percent = parseFloat(data[0][i]["pay_user"] / data[0][i]["active"] * 100).toFixed(2);
                        arpu = parseFloat(data[0][i]["recharge"] / data[0][i]["active"]).toFixed(2);
                    }
                    var new_arpu = 0;
                    if (data[0][i]["new_login"] != 0){
                        new_arpu = parseFloat(data[0][i]["reg_pay_num"] / data[0][i]["new_login"]).toFixed(2);
                    }
                    var arppu = 0;
                    if (data[0][i]["pay_user"] != 0){
                        arppu = parseFloat(data[0][i]["recharge"] / data[0][i]["pay_user"]).toFixed(2);
                    }
                    str_info += "<td>" + pay_percent + "%</td>";
                    str_info += "<td>" + parseFloat(data[0][i]["recharge"]).toFixed(2)  + "</td>";
                    str_info += "<td>" + arpu + "</td>";
                    str_info += "<td>" + arppu + "</td>";
                    str_info += "<td>" + data[0][i]["reg_pay_user"]  + "</td>";
                    str_info += "<td>" + data[0][i]["go_recharge"] + "</td>";
                    str_info += "<td>" + reg_pay_percent  + "%</td>";
                    str_info += "<td>" + parseFloat(data[0][i]["reg_pay_num"]).toFixed(2)   + "</td>";
                    str_info += "<td>" + new_arpu  + "</td>";


                    if (data[0][i]["reg_pay_user"] !== 0){
                        str_info += "<td>" + parseFloat(data[0][i]["reg_pay_user"] / data[0][i]["pay_user"] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>" + parseFloat(data[0][i]["reg_pay_num"] / data[0][i]["recharge"] * 100).toFixed(2)  + "%</td>";
                    }else{
                        str_info += "<td>0%</td>";
                        str_info += "<td>0%</td>";
                    }


                    var second_add_pay_login_pre = 0;
                    var three_add_pay_login_pre = 0;
                    var seven_add_pay_login_pre = 0;
                    if (data[0][i]["pay_user"] !== 0){

                        second_add_pay_login_pre = parseFloat(data[0][i]["second_add_pay_login"] / data[0][i]["reg_pay_user"] * 100).toFixed(2);
                        three_add_pay_login_pre = parseFloat(data[0][i]["three_add_pay_login"] / data[0][i]["reg_pay_user"] * 100).toFixed(2);
                        seven_add_pay_login_pre = parseFloat(data[0][i]["seven_add_pay_login"] / data[0][i]["reg_pay_user"] * 100).toFixed(2);

                        add_second_total_retain += data[0][i]["second_add_pay_login"];
                        add_three_total_retain += data[0][i]["three_add_pay_login"];
                        add_seven_total_retain += data[0][i]["seven_add_pay_login"];

                    }
                    str_info += "<td>"+second_add_pay_login_pre+"%</td>";
                    str_info += "<td>"+three_add_pay_login_pre+"%</td>";
                    str_info += "<td>"+seven_add_pay_login_pre+"%</td>";


                    var seven_ltv_value_pre = 0;
                    if (data[0][i]["regist"] !== 0){
                        seven_ltv_value_pre = parseFloat(data[0][i]["seven_ltv_value"] / data[0][i]["regist"]).toFixed(2);

                        seven_total_ltv += data[0][i]["seven_ltv_value"];

                    }

                    str_info += "<td>"+seven_ltv_value_pre+"</td>";


                    str_info += "</tr>";

                    regist_total += data[0][i]["regist"];
                    role_total += data[0][i]["create_role"];
                    new_total += data[0][i]["new_login"];
                    temp_total += data[0][i][temp];

                    second_total += data[0][i]["second_login"];
                    three_total += data[0][i]["three_login"];
                    four_total += data[0][i]["four_login"];
                    five_total += data[0][i]["five_login"];
                    six_total += data[0][i]["six_login"];
                    seven_total += data[0][i]["seven_login"];
                    week_total += data[0][i]["week_login"];

                    recharge_total += parseFloat(data[0][i]["recharge"]);

                    reg_pay_total += data[0][i]["reg_pay_user"];
                    reg_pay_num_total += data[0][i]["reg_pay_num"];
                }
                str_info += "<tr class=\"success\">";
                str_info += "<td>总计</td>";
                str_info += "<td>" + regist_total + "</td>";
                str_info += "<td>" + role_total + "</td>";
                str_info += "<td>" + new_total + "</td>";
                str_info += "<td>" + data[2] + "</td>";
                var reg_percent = 0;
                if (temp_total != 0) {
                    str_info += "<td>"  + parseFloat(second_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(three_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(four_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(five_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(six_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>" + parseFloat(seven_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>" + week_total + "/" + parseFloat(week_total / temp_total * 100).toFixed(2) + "%</td>";
                    reg_percent = parseFloat(reg_pay_total / temp_total * 100).toFixed(2);

                }
                else {
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0/0%</td>";
                }

                str_info += "<td>" + data[1] + "</td>";
                var pay_percent_total = 0;
                var recharge_t = 0;
                if (data[2] != 0) {
                    pay_percent_total = parseFloat(data[1] / data[2] * 100).toFixed(2);
                    recharge_t = parseFloat(recharge_total / data[2]).toFixed(2);
                }

                var arppu_t = 0;
                if (data[1] != 0) {
                    arppu_t = parseFloat(recharge_total / data[1]).toFixed(2);
                }
                var total_new_arpu = 0;
                if (new_total != 0){
                    total_new_arpu = parseFloat(reg_pay_num_total / new_total).toFixed(2);
                }
                str_info += "<td>" + pay_percent_total + "%</td>";
                str_info += "<td>" + parseFloat(recharge_total).toFixed(2) + "</td>";
                str_info += "<td>" + recharge_t + "</td>";
                str_info += "<td>" + arppu_t + "</td>";
                str_info += "<td>" + reg_pay_total + "</td>";
                str_info += "<td>" + data[3] + "</td>";
                str_info += "<td>" + reg_percent + "%</td>";
                str_info += "<td>" + parseFloat(reg_pay_num_total).toFixed(2) + "</td>";
                str_info += "<td>" + total_new_arpu + "</td>";

                if (data[1] !== 0 ){
                    str_info += "<td>" + parseFloat(data[3] / data[1] * 100).toFixed(2) + "%</td>";
                    add_second_total_retain = parseFloat(add_second_total_retain / reg_pay_total * 100).toFixed(2);
                    add_three_total_retain = parseFloat(add_three_total_retain / reg_pay_total * 100).toFixed(2);
                    add_seven_total_retain = parseFloat(add_seven_total_retain / reg_pay_total * 100).toFixed(2);
                }else{
                    str_info += "<td>0%</td>";
                }

                if (recharge_total !== 0 ){
                    str_info += "<td>" + parseFloat(reg_pay_num_total / recharge_total * 100).toFixed(2) + "%</td>";
                    seven_total_ltv = parseFloat(seven_total_ltv / regist_total).toFixed(2);
                }else{
                    str_info += "<td>0%</td>";
                }

                str_info += "<td>" + add_second_total_retain + "%</td>";
                str_info += "<td>" + add_three_total_retain + "%</td>";
                str_info += "<td>" + add_seven_total_retain + "%</td>";
                str_info += "<td>" + seven_total_ltv + "</td>";
                str_info += "</tr>";
            }
            $("#count_list").html(str_info);
        },
        error: function(){
        }
    });
});


$("#query_channel_button").on("click", function(e){
    e.preventDefault();
    var select_gameserver = $("#select_gameserver2").val();
    var channel_date = $("#channel_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/queryalldatabychannel',
        data: {
            game_server: select_gameserver,
            channel_date: channel_date
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            var regist_total = 0;
            var role_total = 0;
            var new_total = 0;

            var second_total = 0;
            var three_total = 0;
            var four_total = 0;
            var five_total = 0;
            var six_total = 0;
            var seven_total = 0;
            var week_total = 0;

//            var pay_total = 0;
            var reg_pay_total = 0;
            var reg_pay_num_total = 0.0;
            var recharge_total = 0.0;
            var temp_total = 0;
            if (data[0].length != 0 ){
                var temp = "";
                if (select_gameserver == "0") {
                    temp = "regist";
                }
                else {
                    temp = "create_role";
                }
                for (var i = 0; i < data[0].length; i ++ ){
                    str_info += "<tr>";
                    str_info += "<td>" + data[0][i]["channel"] + "</td>";
                    str_info += "<td>" + data[0][i]["date"] + "</td>";
                    str_info += "<td>" + data[0][i]["regist"] + "</td>";
                    str_info += "<td>" + data[0][i]["create_role"] + "</td>";
                    str_info += "<td>" + data[0][i]["new_login"] + "</td>";
                    str_info += "<td>" + data[0][i]["active"] + "</td>";
                    var reg_pay_percent = 0;

                    if (data[0][i][temp] != 0){
                        str_info += "<td>"  + parseFloat(data[0][i]["second_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["three_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["four_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["five_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["six_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>"  + parseFloat(data[0][i]["seven_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        str_info += "<td>" + data[0][i]["week_login"] + "/" + parseFloat(data[0][i]["week_login"] / data[0][i][temp] * 100).toFixed(2)  + "%</td>";
                        reg_pay_percent = parseFloat(data[0][i]["reg_pay_user"] / data[0][i][temp] * 100).toFixed(2);
                    }
                    else{
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                        str_info += "<td>0/0%</td>";
                    }

                    str_info += "<td>" + data[0][i]["pay_user"]  + "</td>";
                    var pay_percent = 0;
                    var arpu = 0;
                    if (data[0][i]["active"] != 0){
                        pay_percent = parseFloat(data[0][i]["pay_user"] / data[0][i]["active"] * 100).toFixed(2);
                        arpu = parseFloat(data[0][i]["recharge"] / data[0][i]["active"]).toFixed(2);
                    }
                    var arppu = 0;
                    if (data[0][i]["pay_user"] != 0){
                        arppu = parseFloat(data[0][i]["recharge"] / data[0][i]["pay_user"]).toFixed(2);
                    }
                    str_info += "<td>" + pay_percent + "%</td>";

                    str_info += "<td>" + data[0][i]["recharge"]  + "</td>";
                    str_info += "<td>" + arpu + "</td>";
                    str_info += "<td>" + arppu + "</td>";
                    str_info += "<td>" + data[0][i]["reg_pay_user"]  + "</td>";
                    str_info += "<td>" + reg_pay_percent  + "%</td>";
                    str_info += "<td>" + data[0][i]["reg_pay_num"]  + "</td>";
                    str_info += "</tr>";

                    regist_total += data[0][i]["regist"];
                    role_total += data[0][i]["create_role"];
                    new_total += data[0][i]["new_login"];
                    temp_total += data[0][i][temp];
//                    active_total += data[0][i]["active"];

                    second_total += data[0][i]["second_login"];
                    three_total += data[0][i]["three_login"];
                    four_total += data[0][i]["four_login"];
                    five_total += data[0][i]["five_login"];
                    six_total += data[0][i]["six_login"];
                    seven_total += data[0][i]["seven_login"];
                    week_total += data[0][i]["week_login"];

//                    pay_total += data[i]["pay_user"];
                    recharge_total += parseFloat(data[0][i]["recharge"]);

                    reg_pay_total += data[0][i]["reg_pay_user"];
                    reg_pay_num_total += parseFloat(data[0][i]["reg_pay_num"]);
                }
                str_info += "<tr class=\"success\">";
                str_info += "<td>总计</td>";
                str_info += "<td>" + channel_date + "</td>";
                str_info += "<td>" + regist_total + "</td>";
                str_info += "<td>" + role_total + "</td>";
                str_info += "<td>" + new_total + "</td>";
                str_info += "<td>" + data[2] + "</td>";
                var reg_percent = 0;
                if (temp_total != 0) {
                    str_info += "<td>"  + parseFloat(second_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(three_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(four_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(five_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>"  + parseFloat(six_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>" + parseFloat(seven_total / temp_total * 100).toFixed(2) + "%</td>";
                    str_info += "<td>" + week_total + "/" + parseFloat(week_total / temp_total * 100).toFixed(2) + "%</td>";
                    reg_percent = parseFloat(reg_pay_total / temp_total * 100).toFixed(2);
                }
                else {
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0%</td>";
                    str_info += "<td>0/0%</td>";
                }

                str_info += "<td>" + data[1] + "</td>";
                var pay_percent_total = 0;
                var recharge_t = 0;
                if (data[2] != 0) {
                    pay_percent_total = parseFloat(data[1] / regist_total * 100).toFixed(2);
                    recharge_t = parseFloat(recharge_total / regist_total).toFixed(2);
                }
                var arppu_t = 0;
                if (data[1] != 0) {
                    arppu_t = parseFloat(recharge_total / data[1]).toFixed(2);
                }
                str_info += "<td>" + pay_percent_total + "%</td>";
                str_info += "<td>" + recharge_total.toFixed(2) + "</td>";
                str_info += "<td>" + recharge_t + "</td>";
                str_info += "<td>" + arppu_t + "</td>";
                str_info += "<td>" + reg_pay_total + "</td>";
                str_info += "<td>" + reg_percent + "%</td>";
                str_info += "<td>" + reg_pay_num_total.toFixed(2) + "</td>";
                str_info += "</tr>";
            }
            $("#channel_list").html(str_info);
        },
        error: function(){
        }
    });
});



$("#query_button").bind("click", function(e){
    e.preventDefault();
    var parnter = $("#user_channel").val();
    var start_date = $("#login_start_date").val();
    var end_date = $("#login_end_date").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryregister',
        data: {partner:parnter, start_date:start_date, end_date:end_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0){
                var reg_total = 0;
                var login_total = 0;
                var recharge_count = 0;
                var recharge_num = 0;
                var t_data = [];
                var t_data1 = [];
                var ticks = [];
                var s = 0;
                for(var i=0; i<data.length; i++){
                    var x_date = data[i]["date"];
                    ticks.push([s+2, x_date]);
                    var temp_data = [s+1, data[i]["total_reg"]];
                    t_data.push(temp_data);
                    var temp_data1 = [s+2, data[i]["total_login"]];
                    t_data1.push(temp_data1);
                    s += 3;
                    str_info += "<tr>";
                    str_info += "<td>" + data[i]["date"] + "</td>";
                    str_info += "<td>" + data[i]["total_reg"] + "</td>";
                    str_info += "<td>" + data[i]["total_login"] + "</td>";
                    str_info += "<td>" + data[i]["ia_percent"] + "%</td>";
//                    str_info += "<td>" + data[i]["recharge_count"] + "</td>";
//                    str_info += "<td>￥" + parseFloat(data[i]["recharge_num"]) + "</td>";
                    str_info += '</tr>';
                    reg_total += data[i]["total_reg"];
                    login_total += data[i]["total_login"];
//                    recharge_count += data[i]["recharge_count"];
//                    recharge_num += parseFloat(data[i]["recharge_num"]);
                }
                var draw_data = [
                    {
                        "label": "注册人数",
                        "data": t_data
                    },
                    {
                        "label": "登录人数",
                        "data": t_data1
                    }
                ];
                str_info += "<tr class=\"success\">";
                str_info += "<td>总计</td>";
                str_info += "<td>" + reg_total + "</td>";
                str_info += "<td>" + login_total + "</td>";
                str_info += "<td>" + (login_total / reg_total * 100).toFixed(2)  + "%</td>";
//                str_info += "<td>" + recharge_count + "</td>";
//                str_info += "<td>￥" + recharge_num + "</td>";
                str_info += '</tr>';
            }
            else{
                str_info += "<tr>";
                str_info += '<td colspan="4" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#register_list").html(str_info);
            drawBarsChart(draw_data, ticks, "left", 1, $("#chart_login"));
        },
        error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});


$("#pay_query").on("click", function(e){
    e.preventDefault();
    var channel = $("#user_channel").val();
    var pay_date = $("#pay_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryactivepay',
        data: {channel: channel, pay_date: pay_date},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            str_info += "<tr>";
            str_info += "<td>" + data["login"] + "</td>";
            str_info += "<td>" + data["one_apa"] + "</td>";
            str_info += "<td>" + data["three_apa"] + "</td>";
            str_info += "<td>" + data["seven_apa"] + "</td>";
            str_info += "<td>" + data["thirty_apa"] + "</td>";
            str_info += "<td>" + data["total_apa"] + "</td>";
            str_info += "</tr>";
            $("#pay_list").html(str_info);

            var str_info1 = "";
            str_info1 += "<tr>";
            str_info1 += "<td>" + data["one_amount"] + "</td>";
            str_info1 += "<td>" + data["three_amount"] + "</td>";
            str_info1 += "<td>" + data["seven_amount"] + "</td>";
            str_info1 += "<td>" + data["thirty_amount"] + "</td>";
            str_info1 += "<td>" + data["total_amount"] + "</td>";
            str_info1 += "</tr>";
            $("#pay_num_list").html(str_info1);
        },
        error: function() {
            App.unblockUI(page_content);
            error_func();
        }
    })
});


$("#select_gameserver1").on("change", function(e){
    $("#query_login").click();
});

$("#query_login").bind("click", function(e){
    e.preventDefault();
    var q_date = $("#q_date").val();
    var channel = $("#user_channel").val();
    var server_id = $("#select_gameserver1").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/queryactive',
        data: {
            channel: channel,
            q_date: q_date,
            server_id: server_id
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if(data.length != 0){
                str_info += "<tr>";
                str_info += "<td>" + data["total_regist"] + "</td>";
                str_info += "<td>" + data["two_count"] + "/" + commonPercent(data["two_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["three_count"] + "/" + commonPercent(data["three_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["four_count"] + "/" + commonPercent(data["four_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["five_count"] + "/" + commonPercent(data["five_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["six_count"] + "/" + commonPercent(data["six_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["seven_count"] + "/" + commonPercent(data["seven_count"], data["total_regist"]) + "%</td>";
                str_info += "<td>" + data["thirty_count"] + "/" + commonPercent(data["thirty_count"], data["total_regist"]) + "%</td>";

                str_info += "<td>" + commonPercent(data["week_keep"], data["total_regist"]) + "%</td>";
                str_info += '</tr>';
            }
            else{
                str_info += "<tr>";
                str_info += '<td colspan="9" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#active_list").html(str_info);
        },
        error: function(){
            App.unblockUI(page_content);
            error_func();
        }
    })
});

$("#a_channel").on("click", function(e){
    e.preventDefault();
    $("#query_channel_button").click();
});


$("#export_excel").on("click", function(e){
    e.preventDefault();
    var user_channel = $("#partner_list").find("option:selected").text();
    export_all_user_excel(user_channel, $("#export_title"), $("#count_list"), "运营数据");
});


// $("#export_excel").on("click", function(e){
//    e.preventDefault();
//    var user_channel = $("#user_channel").val();
//    var server_id = $("#select_gameserver").val();
//    var count_start_date = $("#count_start_date").val();
//    var count_end_date = $("#count_end_date").val();
//    var export_title = "";
//    $("#export_title").children().each(function(e){
//        export_title += $(this).html() + ",";
//    });
//
//    var str_s = "";
//    $("#count_list").children().each(function(e){
//        var str_data = "";
//        $(this).children().each(function (e) {
//            str_data += $(this).html() + ","
//        });
//        str_s += str_data;
//        str_s += "|";
//    });
//
//    var page_content = $('.page-content');
//    App.blockUI(page_content, false);
//
//    $.ajax({
//        type: 'get',
//        url: '/exportopreateexcel',
//        data: {
//            user_channel: user_channel,
//            server_id: server_id,
//            start_date: count_start_date,
//            end_date: count_end_date,
//            export_title: export_title,
//            query_data: str_s
//        },
//        dataType: 'JSON',
//        success: function (data) {
//            App.unblockUI(page_content);
//            window.open(data["url"]);
//        },
//        error: function() {
//            App.unblockUI(page_content);
//            error_func();
//        }
//    })
// });

$("#query_count").click();

$("#a_activeuser").on("click", function(e){
    e.preventDefault();
    $("#query_login").click();
});

$("#a_pay").on("click", function(e){
    e.preventDefault();
    $("#pay_query").click();
});

$("#a_login").on("click", function(e){
    e.preventDefault();
    $("#query_button").click();
});
