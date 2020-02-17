/**
 * Created by wangrui on 17/3/13.
 */
handleDatePickers();
var $start_date = $("#start_date"); 
var $end_date = $("#end_date");
var $true_start_date = $("#true_start_date");
var $true_end_date = $("#true_end_date");
var $tab2_start_date = $('#tab2_start_date');
var $tab2_end_date = $('#tab2_end_date');
var $tab2_platform_name = $('#tab2_platform_name');
var $btn_tab2_query = $('#btn_tab2_query');
var $platform_channel_recharge_tab = $('#platform_channel_recharge_tab');
var $btn_conf_show = $('#btn_conf_show');
var $commit_channel_show_change = $('#commit_channel_show_change');
var $conf_channel_modal = $('#conf_channel_modal');
var $conf_channel_modal_content = $('#conf_channel_modal_content');
var $conf_commit_status = $('#conf_commit_status');

$start_date.val(getNowFormatDate(7));
$end_date.val(getNowFormatDate(0));
$tab2_start_date.val(getNowFormatDate(7));
$tab2_end_date.val(getNowFormatDate(0));
$true_start_date.val("2017-01-01");
$true_end_date.val(getNowFormatDate(0));


var platform_name = {
    'android': "安卓",
    'xiaomi': '小米'
};

init_select_html(false, platform_name, $tab2_platform_name);
create_del_modal($("#platform_del_modal"), "是否删除此信息", "confirm_del");


var exchange_list = ["vietnam", 'yinni', 'qtym'];
// var exchange_list = [];
var plat_form = {
    "ios": {
        "name": "IOS",
        "url": "http://39.107.54.50:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "android": {
        "name": "安卓",
        "url": "http://39.107.52.248:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "msdk": {
        "name": "应用宝",
        "url": "http://console-yyb.zyj.16801.com:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "yueyu":{
        "name": "越狱",
        "url": "http://39.106.249.186:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "vietnam": {
        "name": "越南平台",
        "url": "http://platform.t427.gaba.vn:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "yinni": {
        "name": "印尼",
        "url": "http://209.58.162.41:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 0
    },
   // "gat" : {
       // "name": "港澳台",
       // "url": "http://47.89.30.44:10050",
       // "total": 0,
       // "total2": 0,
       // "total3": 0,
       // "exchange": 1
   // },
    // "btw": {
    //     "name": "变态玩",
    //     "url": "http://139.196.238.151:10050",
    //     "total": 0,
    //     "total2": 0,
    //     "total3": 0,
    //     "exchange": 1
    // },
    "anqu": {
        "name": "安趣",
        "url": "http://admin.zyjiosly.52muyou.com",
        "total": 0,
        "total2": 0,
        "exchange": 1
    },
    //"thailand": {
        //"name": "泰国",
        //"url": "http://209.58.165.209:10050",
        //"total": 0,
        //"total2": 0,
        //"total3": 0,
        //"exchange": 0
    //},
    "JP": {
        "name": "极品",
        "url": "http://221.5.35.187:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    // "jingxun": {
    //     "name": "景讯",
    //     "url": "http://118.89.21.38:10050",
    //     "total": 0,
    //     "total3": 0,
    //     "total2": 0,
    //     "exchange": 1
    // },
    "hanfeng": {
        "name": "汉风",
        "url": "http://admin.zyjiosly.52muyou.com:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "anfeng": {
        "name": "安峰",
        "url": "http://admin.zyjiosly.52muyou.com:40050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    // "mogu": {
    //     "name": "蘑菇互娱",
    //     "url": "http://admin.zyjiosly.52muyou.com:60050",
    //     "total": 0,
    //     "total2": 0,
    //     "total3": 0,
    //     "exchange": 1
    // },
    "qipa": {
        "name": "奇葩互娱",
        "url": "http://101.37.15.132:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
   // "haiyou": {
     //   "name": "海游",
       // "url": "http://47.88.51.16:10050",
       // "total": 0,
       // "total2": 0,
       // "total3": 0,
       // "exchange": 1
    //},
    "huoyou": {
        "name": "火柚",
        "url": "http://120.132.30.34:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "aishang": {
        "name": "爱上游戏",
        "url": "http://120.92.141.243:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "xiaomi": {
        "name": "小米",
        "url": "http://47.93.77.25:15050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    //"shengtai": {
      //  "name": "圣泰",
      //  "url": "http://47.92.5.15:10050",
      //  "total": 0,
      //  "total2": 0,
      //  "total3": 0,
      //  "exchange": 1
    //},
    //"motianlun": {
    //    "name": "摩天轮",
    //    "url": "http://106.75.17.112:10050",
    //    "total": 0,
    //    "total2": 0,
    //    "total3": 0,
    //    "exchange": 1
    //},
    "qilinyou": {
        "name": "麒麟游",
        "url": "http://47.93.77.25:18050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    //"zhijian": {
      //  "name": "360平台",
      //  "url": "http://47.93.77.25:55050",
      //  "total": 0,
      //  "total2": 0,
      //  "total3": 0,
      //  "exchange": 1
    //},
    "kuaiyou": {
        "name": "快游",
        "url": "http://47.93.77.25:30050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
     "qtym": {
        "name": "气吞云梦",
        "url": "http://47.52.107.164:20050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "kuaiwan": {
        "name": "快玩",
        "url": "http://47.93.77.25:65050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "zsy": {
        "name": "中手游",
        "url": "http://47.95.28.95:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "play800": {
        "name": "PLAY800",
        "url": "http://47.93.77.25:47050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
    "yiyou": {
        "name": "意游",
        "url": "http://47.95.28.95:20050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    }, 
    "17wan": {
        "name": "17玩",
        "url": "http://115.159.33.173:10050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    }, 
    "qiyu": {
        "name": "奇遇",
        "url": "http://47.93.77.25:46050",
        "total": 0,
        "total2": 0,
        "total3": 0,
        "exchange": 1
    },
};

function get_total_exchange(){
    for(var i=0; i <exchange_list.length; i++){
        var value = exchange_list[i];
        var exchange_num = get_exchange(value);
        plat_form[value]["exchange"] = parseFloat(exchange_num);
        plat_form[value]["name"] += "(" + exchange_num + ")";
    }
}
get_total_exchange();


function get_platform_recharge_type() {
    var success = function (data) {
        for(var i=0; i<data.length; i++){

            var platform = data[i]["platform"];
            var percent = data[i]["percent"];
            var tongdao = data[i]["tongdao"];
            var kuajing = data[i]["kuajing"];
            var month_total = data[i]["month_total"];
            var total_total = data[i]["total_total"];
            if (plat_form.hasOwnProperty(platform)){
                plat_form[platform]["percent"] = percent;
                plat_form[platform]["tongdao"] = tongdao;
                plat_form[platform]["kuajing"] = kuajing;
                plat_form[platform]["month_total"] = month_total;
                plat_form[platform]["total_total"] = total_total;
            }
        }
    };
    var data = {
        tag: 2
    };
    my_ajax(true, "/platform/queryrecharge", 'get', data, false, success);
}

get_platform_recharge_type();

function display_title(){
    var str_html = "<th>时间</th>";
    str_html += "<th>充值总计</th>";
    str_html += "<th>真实总计</th>";
    str_html += "<th>注册总计</th>";
    str_html += "<th>活跃总计</th>";
    str_html += "<th>ARPU</th>";
    for (var pf in plat_form){
        var name = plat_form[pf]["name"];
        str_html += "<th colspan='4'>" + name + "-" + plat_form[pf]["percent"]  + "%" + "</th>";
    }
    $("#recharge_title").html(str_html);
}
display_title();

function get_date_array(start_time, end_time){
    var bd = new Date(start_time),be = new Date(end_time);
    var bd_time = bd.getTime(), be_time = be.getTime(),time_diff = be_time - bd_time;
    var d_arr = [];
    for (var i = 0; i <= time_diff; i += 86400000) {
        var ds = new Date(bd_time + i);
        d_arr.push(ds.getFullYear() + "-" + (ds.getMonth() + 1) + '-' + ds.getDate());
    }
    return d_arr;
}

function getYearAndMonth(start, end) {
    var result = [];
    var starts = start.split('-');
    var ends = end.split('-');
    var staYear = parseInt(starts[0]);
    var staMon = parseInt(starts[1]);
    var endYear = parseInt(ends[0]);
    var endMon = parseInt(ends[1]);
    while (staYear <= endYear) {
        if (staYear === endYear) {
            while (staMon <= endMon) {
                var day = new Date(staYear,staMon,0);
                var start_t = "";
                var end_t = "";
                if (staMon < 10){
                    start_t = staYear + "-0" + staMon + "-" + "01";
                    end_t = staYear + "-0" + staMon + "-" + day.getDate();
                }
                else{
                    start_t = staYear + "-" + staMon + "-" + "01";
                    end_t = staYear + "-" + staMon + "-" + day.getDate();
                }
                result.push([start_t, end_t]);
                staMon++;
            }
            staYear++;
        } else {
            staMon++;
            if (staMon > 12) {
                staMon = 1;
                staYear++;
            }
            var day = new Date(staYear,staMon,0);
            var start_t = staYear + "-" + staMon + "01";
            var end_t = staYear + "-" + staMon + day.getDate();
            result.push([start_t, end_t]);
        }
    }

    return result;
}


$("input[name='hide_common']").on("change", function (e) {
    e.preventDefault();
    if ($(this).prop('checked')){
        $("td span").hide();
    }
    else{
        $("td span").show();
    }
});

var class_list = ["active", 'success', 'warning', 'danger'];

function get_data2(){
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var date_array = get_date_array(start_date, end_date);

    var str_html = "";
    for(var i=0; i<date_array.length; i++){
        str_html += "<tr>";
        var s = 0;
        str_html += "<td>" + date_array[i] + "</td>";
        str_html += "<td id='recharge_total_" + i + "'></td>";
        str_html += "<td id='true_recharge_total_" + i + "'></td>";
        str_html += "<td id='regist_total_" + i + "'></td>";
        str_html += "<td id='active_total_" + i + "'></td>";
        str_html += "<td id='arpu_total_" + i + "'></td>";
        var temp = 0;
        for (var p in plat_form){
            if (temp % 4 == 0){
                temp = 0;
            }
            str_html += "<td class='" + class_list[temp] + "' id='recharge_td_" + i + "_" + s + "_" + p + "'>" + "</td>";
            str_html += "<td class='" + class_list[temp] + "' id='true_recharge_td_" + i + "_" + s + "_" + p + "'>" + "</td>";
            str_html += "<td class='" + class_list[temp] + "' id='reg_td_" + i + "_" + s  + "_" + p + "'>" + "</td>";
            str_html += "<td class='" + class_list[temp] + "' id='active_td_" + i + "_" + s  + "_" + p + "'>" + "</td>";
            s += 1;
            temp += 1;
        }
        str_html += "</tr>";
    }

    str_html += "<tr>";
    str_html += "<td>总计" + "</td>";
    str_html += "<td id='recharge_total'></td>";
    str_html += "<td id='true_total'></td>";
    str_html += "<td id='reg_total'></td>";
    str_html += "<td id='active_total'></td>";
    str_html += "<td id='arpu_total'></td>";
    var count1 = 0;
    var count2 = 0;
    for (var pform in plat_form) {
        str_html += "<td id='recharge_total_" + pform + "'></td>";
        str_html += "<td id='true_recharge_total_" + pform + "'></td>";
        str_html += "<td id='reg_total_" + pform + "'></td>";
        str_html += "<td id='active_total_" + pform + "'></td>";
        count1 += 1;
    }
    count1 *= 3;
    str_html += "</tr>";
    $("#recharge_list").html(str_html);

    var xxx = 0;
    var date_total = [];
    var date_total2 = [];
    var date_total3 = [];
    var date_total4 = [];

    var wmcd_recharge = [];
    var wmcd_active = [];
    for(var d =0; d<date_array.length; d++){
        date_total.push(0);
        date_total2.push(0);
        date_total3.push(0);
        date_total4.push(0);
    }

    var recharge_total = 0;
    var reg_total = 0;
    var active_total = 0;
    var true_recharge_num = 0.0;

    for (var pf in plat_form) {
        var p_url = plat_form[pf]["url"];
        var url = "/flower/user_payment";
        var url2 = "/flower/adduse";
        var url3 = "/flower/activeuser";
        var new_url = p_url + url;
        var new_url2 = p_url + url2;
        var new_url3 = p_url + url3;
        plat_form[pf]["recharge_total"] = 0;
        plat_form[pf]["true_recharge"] = 0;
        plat_form[pf]["reg_total"] = 0;
        plat_form[pf]["active_total"] = 0;
        function make_arpu(){
            if (count1 == count2){
                var wm_recharge_total = 0;
                var wm_active_total = 0;
                for (var sd=0; sd<date_array.length; sd++){
                    // var arpu = parseFloat((date_total[sd] - wmcd_recharge[sd]) /  (date_total3[sd] - wmcd_active[sd])).toFixed(2);
                    var arpu = parseFloat((date_total[sd]) /  (date_total3[sd])).toFixed(2);
                    $("#arpu_total_"+ sd).html(arpu);
                    wm_recharge_total += wmcd_recharge[sd];
                    wm_active_total += wmcd_active[sd];
                }
                //$("#arpu_total").html(parseFloat((recharge_total - wm_recharge_total) / (active_total - wm_active_total)).toFixed(2));
                $("#arpu_total").html(parseFloat((recharge_total) / (active_total)).toFixed(2));
            }
        }

        function compute_true_recharge(channel, recharge_total) {
            var true_recharge = recharge_total;
            if (plat_form[channel].hasOwnProperty("percent")){
                var percent = plat_form[channel]["percent"];
                var tongdao = plat_form[channel]["tongdao"];
                var kuajing = plat_form[channel]["kuajing"];

                true_recharge = parseInt(recharge_total * percent / 100);
                true_recharge = parseInt(true_recharge - true_recharge * tongdao / 100);
                true_recharge = parseInt(true_recharge - true_recharge * kuajing / 100);
            }
            return true_recharge;
        }

        function make_recharge_func(channel, m){
            return function(data){
                if (data["success"]) {
                    var exchange = plat_form[channel]["exchange"];
                    for (var t = 0; t < data["result"].length; t++) {
                        var number = 0;
                        if (channel == 'haiyou'){
                            console.log(data["result"][t]["number"]);
                            console.log(exchange);
                            number = parseInt(data["result"][t]["number"] * exchange)
                        }
                        else{
                            number = parseInt(data["result"][t]["number"] / exchange);
                        }

                        plat_form[channel]["recharge_total"] += number;
                        var true_recharge = compute_true_recharge(channel, number);
                        plat_form[channel]["true_recharge"] += true_recharge;

                        date_total[t] += number;
                        date_total4[t] += true_recharge;

                        recharge_total += number;
                        true_recharge_num += true_recharge;

                        $("#recharge_td_" + t + "_" + m + "_" + channel).html(number);
                        $("#true_recharge_td_" + t + "_" + m + "_" + channel).html(true_recharge);

                        $("#recharge_total_" + t).html(date_total[t]);
                        $("#true_recharge_total_" + t).html(date_total4[t]);
                        $("#recharge_total_" + channel).html(plat_form[channel]["recharge_total"]);
                        $("#true_recharge_total_" + channel).html(plat_form[channel]["true_recharge"]);
                        $("#recharge_total").html(recharge_total);
                        $("#true_total").html(true_recharge_num);

                        if (channel == "ios"){
                            wmcd_recharge.push(0);
                        }
                    }
                    count2 += 1;
                    make_arpu();
                }
            };
        }
        function make_regist_func(channel, m) {
            return function(data){
                if (data["success"]) {

                    for (var t = 0; t < data["result"].length; t++) {
                        var number2 = parseInt(data["result"][t]["number"]);
                        date_total2[t] += number2;
                        reg_total += number2;
                        plat_form[channel]["reg_total"] += number2;
                        $("#reg_td_" + t + "_" + m + "_" + channel).html(number2);
                        $("#regist_total_" + t).html(date_total2[t]);
                        $("#reg_total_" + channel).html(plat_form[channel]["reg_total"]);
                        $("#reg_total").html(reg_total);
                    }
                }
                count2 += 1;
            };
        }
        function make_active_func(channel, m) {
            return function(data){
                if (data["success"]) {
                    for (var t = 0; t < data["result"].length; t++) {
                        var number3 = parseInt(data["result"][t]["number"]);
                        var active_total_num = parseInt(data["result"][t]["active_total"]);
                        date_total3[t] += number3;
                        if (t ===0 ){
                            active_total += active_total_num;
                        }

                        plat_form[channel]["active_total"] = active_total_num;
                        $("#active_td_" + t + "_" + m + "_" + channel).html(number3);
                        $("#active_total_" + t).html(date_total3[t]);
                        $("#active_total_" + channel).html(plat_form[channel]["active_total"]);
                        $("#active_total").html(active_total);
                        if (channel == "wmcd"){
                            wmcd_active.push(number3);
                        }
                    }
                    count2 += 1;
                    make_arpu();
                }
            };
        }
        var data = {
            "start_time": start_date,
            "end_time": end_date,
            "time_unit": "day"
        };
        my_ajax2(true, new_url, 'get', data, true, make_recharge_func(pf, xxx));
        my_ajax2(true, new_url2, 'get', data, true, make_regist_func(pf, xxx));
        my_ajax2(true, new_url3, 'get', data, true, make_active_func(pf, xxx));
        xxx = xxx + 1;
    }
    $("#recharge_list").html(str_html);
}

$('#btn_down_data').click(function () {
    $('#recharge_table').tableExport({
        type:'excel',
        escape:'false',
        excelstyles: ['border-bottom', 'border-top', 'border-left', 'border-right'],
        fileName: '充值总计'
    });
});
$("#btn_query").on("click", function (e) {
    e.preventDefault();
    get_data2();
});


var getPlatFormRecharge = function () {
    var sAjaxSource = "/platform/queryrecharge";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "platform",
            'sClass': 'center',
            "sTitle": "平台标识"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "平台名称"
        },
        {
            "mDataProp": "percent",
            'sClass': 'center',
            "sTitle": "比例分成"
        },
        {
            "mDataProp": "tongdao",
            'sClass': 'center',
            "sTitle": "通道费"
        },
        {
            "mDataProp": "kuajing",
            'sClass': 'center',
            "sTitle": "跨境税"
        },
        {
            "mDataProp": "month_total",
            'sClass': 'center',
            "sTitle": "阶梯月累计"
        },
        {
            "mDataProp": "total_total",
            'sClass': 'center',
            "sTitle": "总累计流水"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_platform_recharge(this)\" class=\"btn default btn-xs yellow\"" +
            " data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>"
            + "<button onclick=\"del_platform_recharge(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];

    var data = {
        tag: 1
    };
    dataTablePage($("#platform_recharge_table"), aoColumns, sAjaxSource, data, false, null);
};

var platformRechargeValidation = function () {
    var form1 = $('#platform_form');
    var rules = {
        platform_platform: {
            required: true
        },
        platform_name: {
            required: true
        },
        percent: {
            required: true,
            digits: true
        },
        tongdao: {
            required: true,
            digits: true
        },
        kuajing: {
            required: true,
            digits: true
        },
        month_total: {
            required: true,
            digits: true
        },
        total_total: {
            required: true,
            digits: true
        }
    };
    var messages = {
        platform_platform: {
            required: "输入平台标识"
        },
        platform_name: {
            required: "输入平台名称"
        },
        percent: {
            required: "输入平台分成",
            digits: "请输入数字"
        },
        tongdao: {
            required: "输入平台通道费",
            digits: "请输入数字"
        },
        kuajing: {
            required: "输入平台跨境税",
            digits: "请输入数字"
        },
        month_total: {
            required: "输入平台累计流水",
            digits: "请输入数字"
        },
        total_total: {
            required: "输入平台总流水",
            digits: "请输入数字"
        }
    };

    var submitHandler = function (form) {
        var platform_id = $("#platform_id").val();
        var platform_platform = $("#platform_platform").val();
        var platform_name = $("#platform_name").val();
        var percent = $("#percent").val();
        var tongdao = $("#tongdao").val();
        var kuajing = $("#kuajing").val();
        var month_total = $("#month_total").val();
        var total_total = $("#total_total").val();
        var success = function (data) {
            if (data.status == "fail") {
                Common.alert_message($("#error_modal"), 0, "操作失败");
            }
            $("#platform_modal").modal("hide");
            getPlatFormRecharge();
        };
        var data = {
            platform_id: platform_id,
            platform_platform: platform_platform,
            platform_name: platform_name,
            percent: percent,
            tongdao: tongdao,
            kuajing: kuajing,
            month_total: month_total,
            total_total: total_total
        };
        my_ajax(true, "/platform/operate", 'get', data, true, success);
    };
    commonValidation(form1, rules, messages, submitHandler);
};
platformRechargeValidation();


$("#add_platform").on("click", function (e) {
    e.preventDefault();
    $("#platform_id").val("");
    $("#platform_platform").val("");
    $("#platform_name").val("");
    $("#percent").val("");
    $("#tongdao").val("");
    $("#kuajing").val("");
    $("#month_total").val("");
    $("#total_total").val("");
    $("#platform_modal").modal("show");
});


$("#a_platform_recharge").on("click", function (e) {
    e.preventDefault();
    getPlatFormRecharge();
});

function del_platform_recharge(btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#platform_recharge_table").dataTable().fnGetData(nRoW);
    $('#platform_del_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_platform_recharge(" + data["id"] + ")");
}

function confirm_del_platform_recharge(platform_id) {
    var success = function (data) {
        if (data.status == "fail") {
            Common.alert_message($("#error_modal"), 0, "操作失败");
        }
        getPlatFormRecharge();
    };
    var data = {
        "platform_id": platform_id
    };
    my_ajax(true, '/platform/delete', 'get', data, true, success);
}


var mod_platform_recharge = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#platform_recharge_table").dataTable().fnGetData(nRoW);
    $("#platform_id").val(data["id"]);
    $("#platform_platform").val(data["platform"]);
    $("#platform_name").val(data["name"]);
    $("#percent").val(data["percent"]);
    $("#tongdao").val(data["tongdao"]);
    $("#kuajing").val(data["kuajing"]);
    $("#month_total").val(data["month_total"]);
    $("#total_total").val(data["total_total"]);
    $("#platform_modal").modal("show");
};


function display_true_title(){
    var str_html = "<th>时间</th>";
    str_html += "<th>真实总计</th>";
    for (var pf in plat_form){
        var name = plat_form[pf]["name"];
        str_html += "<th>" + name + "-" + plat_form[pf]["percent"]  + "%" + "</th>";
    }
    $("#true_recharge_title").html(str_html);
}
display_true_title();


function get_data(){
    var start_date = $true_start_date.val();
    var end_date = $true_end_date.val();
    var date_array = getYearAndMonth(start_date, end_date);

    var str_html = "";
    for(var i=0; i<date_array.length; i++){
        str_html += "<tr>";
        var s = 0;
        str_html += "<td>" + date_array[i][0] + "</td>";
        str_html += "<td id='true_recharge_month_" + i + "'></td>";
        for (var p in plat_form){
            str_html += "<td id='true_recharge_month_td_" + i + "_" + s + "_" + p + "'>" + "</td>";
            s += 1;
        }
        str_html += "</tr>";
    }

    str_html += "<tr>";
    str_html += "<td>总计" + "</td>";
    str_html += "<td id='true_total_month'></td>";
    for (var pform in plat_form) {
        str_html += "<td id='true_recharge_month_total_" + pform + "'></td>";
    }
    str_html += "</tr>";
    $("#true_recharge_list").html(str_html);

    var xxx = 0;
    var date_total = [];
    for(var d =0; d<date_array.length; d++){
        date_total.push(0);
    }

    var true_recharge_num = 0.0;

        for (var pf in plat_form) {
            var p_url = plat_form[pf]["url"];
            var url = "/flower/user_payment";
            var new_url = p_url + url;

            plat_form[pf]["true_recharge"] = 0;

            function compute_true_recharge(channel, recharge_total) {
                var true_recharge = recharge_total;

                if (plat_form[channel].hasOwnProperty("percent")) {
                    var percent = plat_form[channel]["percent"];
                    var tongdao = plat_form[channel]["tongdao"];
                    var kuajing = plat_form[channel]["kuajing"];

                    true_recharge = parseInt(recharge_total * percent / 100);
                    true_recharge = parseInt(true_recharge - true_recharge * tongdao / 100);
                    true_recharge = parseInt(true_recharge - true_recharge * kuajing / 100);
                }

                return true_recharge;
            }

            function make_recharge_func(channel, m, n) {
                return function (data) {
                    if (data["success"]) {
                        var exchange = plat_form[channel]["exchange"];
                        var number = 0;
                        for (var t = 0; t < data["result"].length; t++) {
                            number += parseInt(data["result"][t]["number"]);
                        }
                        number = parseInt(number / exchange);
                        var true_recharge = compute_true_recharge(channel, number);
                        plat_form[channel]["true_recharge"] += true_recharge;

                        date_total[n] += true_recharge;
                        true_recharge_num += true_recharge;

                        $("#true_recharge_month_td_" + n + "_" + m + "_" + channel).html(true_recharge);

                        $("#true_recharge_month_" + n).html(date_total[n]);
                        $("#true_recharge_month_total_" + channel).html(plat_form[channel]["true_recharge"]);
                        $("#true_total_month").html(true_recharge_num);
                    }
                };
            }
            for (var da = 0; da<date_array.length; da++) {
                var true_start = date_array[da][0];
                var true_end = date_array[da][1];
                var data = {
                    "start_time": true_start,
                    "end_time": true_end,
                    "time_unit": "day"
                };

                my_ajax2(true, new_url, 'get', data, true, make_recharge_func(pf, xxx, da));
            }
            xxx = xxx + 1;
        }

}

$("#btn_true_query").on("click", function (e) {
   e.preventDefault();
   get_data();
});


function getDate (datestr) {
        var temp = datestr.split("-");
        if (temp[1] === '01') {
            temp[0] = parseInt(temp[0],10) - 1;
            temp[1] = '12';
        } else {
            temp[1] = parseInt(temp[1],10) - 1;
        }
        //new Date()的月份入参实际都是当前值-1
        var date = new Date(temp[0], temp[1], temp[2]);
        return date;
    }
  /**
  ***获取两个日期间的所有日期
  ***默认start<end
  **/
  function getDiffDate (start, end) {
        var startTime = getDate(start);
        var endTime = getDate(end);
        var dateArr = [];
        while ((endTime.getTime() - startTime.getTime()) > 0) {
            var year = startTime.getFullYear();
            var month = startTime.getMonth().toString().length === 1 ? "0" + (parseInt(startTime.getMonth().toString(),10) + 1) : (startTime.getMonth() + 1);
            var day = startTime.getDate().toString().length === 1 ? "0" + startTime.getDate() : startTime.getDate();
            dateArr.push(year + "-" + month + "-" + day);
            startTime.setDate(startTime.getDate() + 1);
        }
        return dateArr;
    }

var query_channel;
var channel_dict;
var all_platform_channel;
var p_id_dict;
var id_p_dict;
var recharge_channel_click = function () {
    my_ajax2(true, "/get/platform/channel", 'get', {'platform': $tab2_platform_name.val()}, false, function (result) {
        p_id_dict = {};
        id_p_dict = {};
        query_channel = [];
        channel_dict = {};
        all_platform_channel = {'yes': [], 'no': []};
        if (result.status === 'ok'){
            for (var i=0; i<result['data'].length; i++){
                if (result['data'][i]['status'] === 'yes'){
                    query_channel.push( result['data'][i]['p_id'].toString() );
                }else if (result['data'][i]['status'] === 'no'){
                    all_platform_channel['no'].push(result['data'][i]['p_id']);
                }
                p_id_dict[result['data'][i]['p_id']] = result['data'][i]['id'];
                id_p_dict[result['data'][i]['id']] = result['data'][i]['p_id'];
                channel_dict[result['data'][i]['p_id']] = result['data'][i]['name']
            }
            all_platform_channel['yes'] = query_channel

        }
    });
};

$commit_channel_show_change.click(function () {
    $commit_channel_show_change.attr('disabled', 'disabled');
    $commit_channel_show_change.text('保存中。。');
    var show_list = [];
    var hide_list = [];
    $conf_channel_modal_content.find('input:checkbox').each(function(){
        if ($(this).is(":checked")) {
            show_list.push($(this).val())
        }else{
            hide_list.push($(this).val())
        }
    });

    my_ajax2(true, "/put/platform/channel", 'post', {'show_list': show_list.join(','), 'hide_list': hide_list.join(',')}, false, function (result) {
        if (result.status === 'ok'){
            all_platform_channel['yes']=[];
            var i;
            for (i=0;i<show_list.length;i++){
                all_platform_channel['yes'].push(id_p_dict[show_list[i]])
            }
            for (i=0;i<hide_list.length;i++){
                all_platform_channel['no'].push(id_p_dict[hide_list[i]])
            }
            // all_platform_channel['yes'] = show_list;
            // all_platform_channel['no'] = hide_list;
            query_channel=all_platform_channel['yes'];
            $conf_channel_modal.modal('hide')
        }else{
            $conf_commit_status.html('保存失败');
            $conf_commit_status.show();
        }
    });
});




$btn_conf_show.click(function () {

    var i;
    var check_box_html = '';
    var temp_str;
    for (i=0;i<all_platform_channel['yes'].length;i++){
        temp_str = all_platform_channel['yes'][i];
        check_box_html += '<label class="checkbox-inline"><input type="checkbox" value="'+ p_id_dict[temp_str]+'" checked="checked"/>'+channel_dict[temp_str] + '</label>'
    }
    for (i=0;i<all_platform_channel['no'].length;i++){
        temp_str = all_platform_channel['no'][i];
        check_box_html += '<label class="checkbox-inline"><input type="checkbox" value="'+ p_id_dict[temp_str]+'" />'+channel_dict[temp_str] + '</label>'

    }
    $conf_channel_modal_content.html(check_box_html);

    $commit_channel_show_change.removeAttr('disabled');
    $commit_channel_show_change.text('提交更改');
    $conf_commit_status.hide();
    $conf_channel_modal.modal('show')
});


$tab2_platform_name.change(function () {
    recharge_channel_click()
});

$btn_tab2_query.click(function () {
    var channel_data = '';

    $btn_tab2_query.attr('disabled', 'disabled');
    $btn_tab2_query.text('查询中。。');
    var $thead =  $platform_channel_recharge_tab.children('thead');



    var start_date = $tab2_start_date.val();
    var end_date = $tab2_end_date.val();
    var date_array = getDiffDate(start_date, end_date);
    var data = {
        "start_time": start_date,
        "end_time": end_date,
        "time_unit": "day"
    };
    var all_data = {};
    var platform_url = plat_form[$tab2_platform_name.val()]['url'];
    my_ajax2(true, platform_url + "/flower/user_payment", 'get', data, false, function (data) {
        if (data.success){
            all_data['user_pay'] = data['result']
        }
    });
    my_ajax2(true, platform_url + "/flower/adduse", 'get', data, false, function (data) {
        if (data.success){
            all_data['add_user'] = data['result']
        }
    });
    my_ajax2(true, platform_url + "/flower/activeuser", 'get', data, false, function (data) {
        if (data.success){
            all_data['active_user'] = data['result']
        }
    });

     my_ajax2(true, platform_url + "/flower/channel/PAA", 'get', {'start_date': start_date, 'end_date': end_date, 'channel': query_channel.join(',')}, false, function (result) {
        if (result.status === 'success'){
            channel_data = result.data;
        }
    });
    var total_data = {};
     for (i=0;i<date_array.length;i++){
        for (d=0;d<query_channel.length;d++){
            if (!(query_channel[d] in total_data)){
                total_data[query_channel[d]] = 0;
            }
            if (query_channel[d] in channel_data){
                total_data[query_channel[d]] += channel_data[query_channel[d]][date_array[i]]['pay_total']
            }
        }
    }
    var order_list =  Object.keys(total_data).sort(function (a, b) {
        return total_data[b] - total_data[a]
    });
    var table_head_row_1 = '<tr><th rowspan="2">日期</th><th colspan="3">'+plat_form[$tab2_platform_name.val()]['name']+'</th>';
    var table_head_row_2 = '<tr><th>充值</th><th>新增</th><th>活跃</th>';

     for(i=0;i<order_list.length;i++){
         table_head_row_1 += '<th colspan="3">'+channel_dict[order_list[i]]+'</th>';
         table_head_row_2 += '<th>充值</th><th>新增</th><th>活跃</th>';

    }
    $thead.html(table_head_row_1 +'</tr>' + table_head_row_2 + '</tr>');
    var table_data = [];
    var table_data_tmp = [];

    for (var i=0;i<date_array.length;i++){
        table_data_tmp = [];
        table_data_tmp.push(date_array[i]);
        var d;
        for (d=0;d<all_data['user_pay'].length;d++){
            if (all_data['user_pay'][i]['time'] === date_array[i]){
                table_data_tmp.push(all_data['user_pay'][i]['number']);
                break
            }
        }
        for (d=0;d<all_data['add_user'].length;d++){
            if (all_data['add_user'][i]['time'] === date_array[i]){
                table_data_tmp.push(all_data['add_user'][i]['number']);
                break
            }
        }
        for (d=0;d<all_data['active_user'].length;d++){
            if (all_data['active_user'][i]['time'] === date_array[i]){
                table_data_tmp.push(all_data['active_user'][i]['number']);
                break
            }
        }
        for (d=0;d<order_list.length;d++){
            if (order_list[d] in channel_data){

                table_data_tmp.push( channel_data[order_list[d]][date_array[i]]['pay_total'] );
                table_data_tmp.push( channel_data[order_list[d]][date_array[i]]['add_total'] );
                table_data_tmp.push( channel_data[order_list[d]][date_array[i]]['active_total'] );

            }else{
                table_data_tmp.push(0,0,0)
            }
        }

        table_data.push(table_data_tmp)
    }
    var last_row = ['总计'];
    var line_index = [0];
    for (i=0;i<date_array.length;i++){
        for (d=1;d<table_data[i].length;d++){
            if (d>=last_row.length){
                last_row.push(0)
            }
            last_row[d] += table_data[i][d];
            line_index.push(d)
        }

    }
    table_data.push(last_row);


    if ($platform_channel_recharge_tab.hasClass('dataTable')) {
          var dttable = $platform_channel_recharge_tab.dataTable();
          dttable.fnClearTable(); //清空一下table
          dttable.fnDestroy(); //还原初始化了的datatable
    }
    var columnDefs = [];
    var class_list = ['active', 'success', 'warning', 'danger'];
    d = 0;
    for (i=1;i<last_row.length;i++){
        columnDefs.push({"className":class_list[d], 'targets': i});
        if (i%3 === 0){
            d = d<4 ? d+1 : 0
        }

    }
    $platform_channel_recharge_tab.dataTable({
        "destroy" : true,
        "bAutoWidth" : false,
        "bProcessing" : true,
        "data": table_data,
        "bFilter": false,    //去掉搜索框方法三：这种方法可以
        "bLengthChange": false,
        "aLengthMenu":[10],

        "paging": false,
        // "columns" : columns,
        "aoColumnDefs": columnDefs,
        "ordering" : false,
        "oLanguage" : oLanguage
   });

    $btn_tab2_query.text('查询');
    $btn_tab2_query.removeAttr('disabled');


});

