/**
 * Created by wangrui on 17/3/13.
 */
handleDatePickers();
var $start_date = $("#start_date"); 
var $end_date = $("#end_date");

$start_date.val(getNowFormatDate(7));
$end_date.val(getNowFormatDate(0));


var exchange_list = ["vietnam", 'yinni', 'thailand'];
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
    // "yinni": {
    //     "name": "印尼",
    //     "url": "http://209.58.162.41:10050",
    //     "total": 0,
    //     "total2": 0,
    //     "total3": 0,
    //     "exchange": 0
    // },
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
// get_total_exchange();

function display_title(){
    var str_html = "<th>时间</th>";
    str_html += "<th>充值总计</th>";
    for (var pf in plat_form){
        var name = plat_form[pf]["name"];
        str_html += "<th>" + name + "</th>";
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


function get_data2(){
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var recharge_type = $("#recharge_type").val();
    
    var date_array = get_date_array(start_date, end_date);

    var str_html = "";
    for(var i=0; i<date_array.length; i++){
        str_html += "<tr>";
        var s = 0;
        str_html += "<td>" + date_array[i] + "</td>";
        str_html += "<td id='recharge_total_" + i + "'></td>";
        for (var p in plat_form){
            str_html += "<td id='recharge_td_" + i + "_" + s + "_" + p + "'>" + "</td>";
            s += 1;
        }
        str_html += "</tr>";
    }
    
    str_html += "<tr>";
    str_html += "<td>总计" + "</td>";
    str_html += "<td id='recharge_total'></td>";
    for (var pform in plat_form) {
        str_html += "<td id='recharge_total_" + pform + "'></td>";
    }
    str_html += "</tr>";
    $("#recharge_list").html(str_html);
    
    var xxx = 0;
    var date_total = [];
    for(var d =0; d<date_array.length; d++){
        date_total.push(0);
    }
    
    var recharge_total = 0;

    for (var pf in plat_form) {
        var p_url = plat_form[pf]["url"];
        var url = "/flower/usersimrecharge";
        var new_url = p_url + url;

        plat_form[pf]["recharge_total"] = 0;

        function make_recharge_func(channel, m){
            return function(data){
                if (data["success"]) {
                    var exchange = plat_form[channel]["exchange"];
                    for (var t = 0; t < data["result"].length; t++) {
                        var number = parseInt(data["result"][t] / exchange);
                        plat_form[channel]["recharge_total"] += number;
                        
                        date_total[t] += number;
                        recharge_total += number;
                        $("#recharge_td_" + t + "_" + m + "_" + channel).html(number);
                        $("#recharge_total_" + t).html(date_total[t]);
                        $("#recharge_total_" + channel).html(plat_form[channel]["recharge_total"]);
                        $("#recharge_total").html(recharge_total);
                    }
                }
            };
        }
        var data = {
            "start_time": start_date,
            "end_time": end_date,
            "recharge_type": recharge_type,
            "time_unit": "day"
        };
        my_ajax(true, new_url, 'get', data, true, make_recharge_func(pf, xxx));
        xxx = xxx + 1;
    }
    $("#recharge_list").html(str_html);
}

$("#btn_query").on("click", function (e) {
    e.preventDefault();
    get_data2();
});