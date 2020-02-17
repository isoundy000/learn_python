get_section($("#select_section1"));

create_del_modal($("#recharge_gift_del_modal"), "是否删除此记录", "confirm_del");
create_del_modal($("#day_gift_del_modal"), "是否删除此记录", "confirm_del2");
create_del_modal($("#consume_gift_del_modal"), "是否删除此记录", "confirm_del3");
handleDatePickers();

var section = $("#select_section1").val();
var recharge_gift_data = {};

var content_arr = ["id", "rmb", "reward"];
var content_time = ["id", "systemid", "icon", "type", "name", "seq", "begin", "end"];
var content_arr2 = ["id", "day", "rmb", "reward"];
var content_arr3 = ["id", "gold", "reward"];

var recharge_gift_name = "recharge_gift";
var day_gift_name = "daydaygift_item";
var activity_time = "activity_time";
var consume_name = "consumegift_reward";


var operate_gift = function (div_m, gift, param) {

    $.ajax({
            type: 'post',
            url: '/operategift',
            data: {
                section: section,
                gift: gift,
                param: JSON.stringify(param),
                recharge_gift: JSON.stringify(recharge_gift_data[section][gift])
            },
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "fail") {
                    Common.alert_message($("#error_modal"), 0, "操作失败.")
                }
                div_m.modal("hide");
                get_recharge_gift_data();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};


$("#btn_recharge_gift").on("click", function (e) {
    e.preventDefault();
    var recharge_gift_id = $("#recharge_gift_id").val();
    var recharge_gift_rmb = $("#recharge_gift_rmb").val();
    var recharge_gift_reward = $("#recharge_gift_reward").val();

    recharge_gift_data[section][recharge_gift_name][recharge_gift_id] = {
        id: recharge_gift_id,
        rmb: recharge_gift_rmb,
        reward: recharge_gift_reward
    };
    operate_gift($("#recharge_gift_modal"), recharge_gift_name, content_arr);
});


$("#btn_day_gift").on("click", function (e) {
    e.preventDefault();
    var day_gift_id = $("#day_gift_id").val();
    var day_rmb = $("#day_gift_rmb").val();
    var day_day = $("#day_day").val();
    var day_gift_reward = $("#day_gift_reward").val();
    recharge_gift_data[section][day_gift_name][day_gift_id] = {
        id: day_gift_id,
        day: day_day,
        rmb: day_rmb,
        reward: day_gift_reward
    };
    operate_gift($("#day_gift_modal"), day_gift_name, content_arr2);
});


$("#btn_consume_gift").on("click", function (e) {
    e.preventDefault();
    var consume_gift_id = $("#consume_gift_id").val();
    var consume_gold = $("#consume_gold").val();
    var consume_gift_reward = $("#consume_gift_reward").val();
    recharge_gift_data[section][consume_name][consume_gift_id] = {
        id: consume_gift_id,
        gold: consume_gold,
        reward: consume_gift_reward
    };
    operate_gift($("#consume_gift_modal"), consume_name, content_arr3);
});

var recharge_gift = 1;
var day_gift = 1;
var consume_gift = 1;
var recharge_gift_end_time = null;
var day_gift_end_time = null;
var consume_end_time = null;

var get_start_end_date = function (v_data) {
    var e_temp = parseInt(v_data.substring(4, 6)) - 1;
    return new Date(v_data.substring(0, 4), e_temp, v_data.substring(6, 8)).getTime();
};

var set_date = function (v_data, div_date) {
    var temp = v_data.substring(0, 4) + "-" + v_data.substring(4, 6) + "-" + v_data.substring(6, 8);
    div_date.val(temp);
};

var space_timer1 = function () {
    var ts = recharge_gift_end_time - new Date().getTime();
    var dd = Math.floor(ts / 1000 / 60 / 60 / 24);
    var hh = Math.floor(ts / 1000 / 60 / 60 % 24);
    var mm = Math.floor(ts / 1000 / 60 % 60);
    var ss = Math.floor(ts / 1000 % 60);
    $("#spare_time").html(dd + "天" + hh + "时" + mm + "分" + ss + "秒");
};

var space_timer2 = function () {
    var ts = day_gift_end_time - new Date().getTime();
    var dd = Math.floor(ts / 1000 / 60 / 60 / 24);
    var hh = Math.floor(ts / 1000 / 60 / 60 % 24);
    var mm = Math.floor(ts / 1000 / 60 % 60);
    var ss = Math.floor(ts / 1000 % 60);
    $("#spare_time2").html(dd + "天" + hh + "时" + mm + "分" + ss + "秒");
};

var space_timer3 = function () {
    var ts = consume_end_time - new Date().getTime();
    var dd = Math.floor(ts / 1000 / 60 / 60 / 24);
    var hh = Math.floor(ts / 1000 / 60 / 60 % 24);
    var mm = Math.floor(ts / 1000 / 60 % 60);
    var ss = Math.floor(ts / 1000 % 60);
    $("#spare_time3").html(dd + "天" + hh + "时" + mm + "分" + ss + "秒");
};

var t1 = null;
var t2 = null;
var t3 = null;

var set_timer_data = function (start_time, s_end_time, tag, div_spare) {
    var now_date = new Date().getTime();
    if (now_date > start_time && now_date < s_end_time) {
        div_spare.removeClass();
        div_spare.addClass("badge badge-success");
        if (tag == 1) {
            if (t1 != null){
                clearInterval(t1);
            }
            t1 = setInterval(space_timer1, 1000);
        }
        else if (tag == 2) {
            if (t2 != null){
                clearInterval(t2);
            }
            t2 = setInterval(space_timer2, 1000);
        }
        else if (tag == 3) {
            if (t3 != null){
                clearInterval(t3);
            }
            t3 = setInterval(space_timer3, 1000);
        }
    }
    else if (now_date < start_time) {
        div_spare.removeClass();
        div_spare.addClass("badge badge-info");
        div_spare.html("活动未开始");
    }
    else if (now_date > s_end_time) {
        div_spare.removeClass();
        div_spare.addClass("badge badge-danger");
        div_spare.html("活动已结束");
    }
};

var get_recharge_gift_data = function () {
    var section = $("#select_section1").val();
    var ajax_url = '/queryjsondatabysection';
    var send_data = {
        section: section,
        type: JSON.stringify([recharge_gift_name, activity_time, day_gift_name, consume_name])
    };
    var success_func = function (data) {
        recharge_gift_data[section] = data;

        //累计充值
        var str_html = "";
        for (var i in data[recharge_gift_name]) {

            str_html += "<tr>";
            for (var s = 0; s < content_arr.length; s++) {
                str_html += "<td>" + data[recharge_gift_name][i][content_arr[s]] + "</td>";
            }
            if (i > recharge_gift) {
                recharge_gift = i;
            }
            str_html += "<td>";
            str_html += '&nbsp; <a onclick="mod_recharge_gift(' + "'" + i + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
            str_html += '&nbsp; <a onclick="del_recharge_gift(' + "'" + i + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
            str_html += "</td>";
            str_html += "</tr>";
        }
        // 天天好礼
        var str_html1 = "";
        for (var d in data[day_gift_name]) {
            str_html1 += "<tr>";
            for (var k = 0; k < content_arr2.length; k++) {
                str_html1 += "<td>" + data[day_gift_name][d][content_arr2[k]] + "</td>";
            }
            if (d > day_gift) {
                day_gift = d;
            }
            str_html1 += "<td>";
            str_html1 += '&nbsp; <a onclick="mod_day_gift(' + "'" + d + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
            str_html1 += '&nbsp; <a onclick="del_day_gift(' + "'" + d + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
            str_html1 += "</td>";
            str_html1 += "</tr>";
        }

        //消费有礼
        var str_html2 = "";
        for (var c in data[consume_name]) {
            str_html2 += "<tr>";
            for (var n = 0; n < content_arr3.length; n++) {
                str_html2 += "<td>" + data[consume_name][c][content_arr3[n]] + "</td>";
            }
            if (c > consume_gift) {
                consume_gift = c;
            }
            str_html2 += "<td>";
            str_html2 += '&nbsp; <a onclick="mod_consume_gift(' + "'" + c + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
            str_html2 += '&nbsp; <a onclick="del_consume_gift(' + "'" + c + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
            str_html2 += "</td>";
            str_html2 += "</tr>";
        }


        //累计充值
        var end = data[activity_time]["16"]["end"];
        var s_end_time = get_start_end_date(end);
        var begin = data[activity_time]["16"]["begin"];
        var start_time = get_start_end_date(begin);
        recharge_gift_end_time = s_end_time;
        set_timer_data(start_time, s_end_time, 1, $("#spare_time"));
        set_date(begin, $("#start_date"));
        set_date(end, $("#end_date"));

        //天天好礼
        var end2 = data[activity_time]["14"]["end"];
        var s_end_time2 = get_start_end_date(end2);
        var begin2 = data[activity_time]["14"]["begin"];
        var start_time2 = get_start_end_date(begin2);
        day_gift_end_time = s_end_time2;
        set_timer_data(start_time2, s_end_time2, 2, $("#spare_time2"));
        set_date(begin2, $("#start_date2"));
        set_date(end2, $("#end_date2"));

        //消费有礼
        var end3 = data[activity_time]["15"]["end"];
        var s_end_time3 = get_start_end_date(end3);
        var begin3 = data[activity_time]["15"]["begin"];
        var start_time3 = get_start_end_date(begin3);
        consume_end_time = s_end_time3;
        set_timer_data(start_time3, s_end_time3, 3, $("#spare_time3"));
        set_date(begin3, $("#start_date3"));
        set_date(end3, $("#end_date3"));


        $("#consume_gift_list").html(str_html2);
        $("#recharge_gift_list").html(str_html);
        $("#day_gift_list").html(str_html1);
    };
    common_table(ajax_url, send_data, success_func);
};

get_recharge_gift_data();


$("#select_section1").on("change", function (e) {
    e.preventDefault();
    section = $("#select_section1").val();
    get_recharge_gift_data();
});


$("#add_recharge_gift").on("click", function (e) {
    e.preventDefault();
    var $recharge_gift_id = $("#recharge_gift_id");
    $recharge_gift_id.val(parseInt(recharge_gift) + 1);
    $recharge_gift_id.attr("disabled", true);
    $("#recharge_gift_rmb").val("");
    $("#recharge_gift_reward").val("");
    $("#recharge_gift_modal").modal("show");
});

$("#add_day_gift").on("click", function (e) {
    e.preventDefault();
    var $day_gift_id = $("#day_gift_id");
    $day_gift_id.val(parseInt(day_gift) + 1);
    $day_gift_id.attr("disabled", true);
    $("#day_gift_rmb").val("");
    $("#day_day").val("");
    $("#day_gift_reward").val("");
    $("#day_gift_modal").modal("show");
});

$("#add_consume_gift").on("click", function (e) {
    e.preventDefault();
    var $consume_gift_id = $("#consume_gift_id");
    $consume_gift_id.val(parseInt(consume_gift) + 1);
    $consume_gift_id.attr("disabled", true);
    $("#consume_gold").val("");
    $("#consume_gift_reward").val("");
    $("#consume_gift_modal").modal("show");
});


var mod_recharge_gift = function (rid) {
    var rech_data = recharge_gift_data[section][recharge_gift_name][rid];
    var $recharge_gift_id = $("#recharge_gift_id");
    $recharge_gift_id.val(rid);
    $recharge_gift_id.attr("disabled", true);

    $("#recharge_gift_rmb").val(rech_data["rmb"]);
    $("#recharge_gift_reward").val(rech_data["reward"]);
    $("#recharge_gift_modal").modal("show");
};

var mod_day_gift = function (rid) {
    var rech_data = recharge_gift_data[section][day_gift_name][rid];
    var $day_gift_id = $("#day_gift_id");
    $day_gift_id.val(rid);
    $day_gift_id.attr("disabled", true);
    $("#day_gift_rmb").val(rech_data["rmb"]);
    $("#day_day").val(rech_data["day"]);
    $("#day_gift_reward").val(rech_data["reward"]);
    $("#day_gift_modal").modal("show");
};

var mod_consume_gift = function (rid) {
    var rech_data = recharge_gift_data[section][consume_name][rid];
    var $consume_gift_id = $("#consume_gift_id");
    $consume_gift_id.val(rid);
    $("#consume_gold").val(rech_data["gold"]);
    $("#consume_gift_reward").val(rech_data["reward"]);
    $("#consume_gift_modal").modal("show");
};


var del_recharge_gift = function (nid) {
    $("#recharge_gift_del_modal").modal("show");
    $("#confirm_del").attr('onclick', "confirm_del_recharge_gift(" + nid + ")");
};

function confirm_del_recharge_gift(nid) {
    delete recharge_gift_data[section][recharge_gift_name][nid];
    operate_gift($("#recharge_gift_del_modal"), recharge_gift_name, content_arr);
}

var del_day_gift = function (nid) {
    $("#day_gift_del_modal").modal("show");
    $("#confirm_del2").attr('onclick', "confirm_del_day_gift(" + nid + ")");
};

function confirm_del_day_gift(nid) {
    delete recharge_gift_data[section][day_gift_name][nid];
    operate_gift($("#day_gift_del_modal"), day_gift_name, content_arr2);
}

var del_consume_gift = function (nid) {
    $("#consume_gift_del_modal").modal("show");
    $("#confirm_del3").attr('onclick', "confirm_del_consume_gift(" + nid + ")");
};

function confirm_del_consume_gift(nid) {
    delete recharge_gift_data[section][consume_name][nid];
    operate_gift($("#consume_gift_del_modal"), consume_name, content_arr3);
}


$("#set_time").on("click", function (e) {
    $("#recharge_gift_time_modal").modal("show");
});

$("#set_time2").on("click", function (e) {
    $("#day_gift_time_modal").modal("show");
});

$("#set_time3").on("click", function (e) {
    $("#consume_gift_time_modal").modal("show");
});


var time_set_function = function(div_start_date, div_end_date, div_gift, num){
    var start_date = div_start_date.val().split("-");
    var end_date = div_end_date.val().split("-");

    var full_start_date = start_date[0] + start_date[1] + start_date[2] + "000000";
    var full_end_date = end_date[0] + end_date[1] + end_date[2] + "000000";
    if (recharge_gift_data[section][activity_time][num]["begin"] != full_start_date ||
        recharge_gift_data[section][activity_time][num]["end"] != full_end_date) {

        recharge_gift_data[section][activity_time][num]["begin"] = full_start_date;
        recharge_gift_data[section][activity_time][num]["end"] = full_end_date;
        operate_gift(div_gift, activity_time, content_time);
    }
};

$("#btn_settime").on("click", function (e) {
    e.preventDefault();
    time_set_function($("#start_date"), $("#end_date"), $("#recharge_gift_time_modal"), 16);
});

$("#btn_settime2").on("click", function (e) {
    e.preventDefault();
    time_set_function($("#start_date2"), $("#end_date2"), $("#day_gift_time_modal"), 14);
});

$("#btn_settime3").on("click", function (e) {
    e.preventDefault();
    time_set_function($("#start_date3"), $("#end_date3"), $("#consume_gift_time_modal"), 15);
});

$("#reload_config").on("click", function(){
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/reloadconfig',
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                console.log(data);
                if (data["status"] == "success") {
                    Common.alert_message($("#error_modal"), 1, "配置加载成功.");
                }
                else {
                    Common.alert_message($("#error_modal"), 0, "配置加载失败.")
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    );
});