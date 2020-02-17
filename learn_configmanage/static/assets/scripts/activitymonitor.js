/**
 * Created by wangrui on 17/4/24.
 */


handleDatePickers();


var $activity_title = $("#activity_title");
var $activity_list = $("#activity_list");
var $select_game = $("#select_game");
var $start_date  = $("#start_date");
var $end_date = $("#end_date");
var $select_section = $("#select_section");
var $activity_version = $("#activity_version");
var $select_activity_table = $('#select_activity_table');

var now_date = getNowFormatDate(0).replace(/-/g, "");

$start_date.val(getNowFormatDate(0));
$end_date.val(getNowFormatDate(0));
getGameServerData($select_game, 1);

var week_day_dict = {
    0: '周日',
    1: '周一',
    2: '周二',
    3: '周三',
    4: '周四',
    5: '周五',
    6: '周六'
};

var activity = ["activity_time"];
var SECTION_DATA = null;
var ACTIVITY_DATA = null;

var make_section_select = function(s_data){
    var str_info = "";
    for (var i in s_data) {
        str_info += "<option value='" + s_data[i].id + "'>" + s_data[i].name + "</option>";
    }
    $select_section.html(str_info);
    $select_section.change();
};



var get_version_list = function (){
    var success = function(data){
        var str_html = "";
        var online_version = null;
        if (data.length != 0){
            for (var i = 0; i < data.length; i++) {
                if (data[i]["status"] == "online") {
                    
                    online_version = data[i]["version"];
                    str_html += "<option value='" + data[i]["version"] + "'>线上版本:" + data[i]["version"] + "</option>";
                }
                else {

                    str_html += "<option value='" + data[i]["version"] + "'>版本:" + data[i]["version"] + "</option>";
                }
            }
        }
        $activity_version.html(str_html);
        $activity_version.val(online_version);
    };
    var section = $select_section.val();
    var data = {
        section: section,
        table_name: $select_activity_table.val()
    };
    my_ajax(true, '/activity/queryversion', 'get', data, true, success);
};

$select_activity_table.change(function () {
    get_version_list();
});



$select_section.on("change", function (e) {
    e.preventDefault();
    get_version_list();
});


var display_activity_data = function () {
    var success = function (data) {
        var str_title = "<tr>";
        str_title += "<th >编号</th>";
        str_title += "<th >活动</th>";
        var t = 0;
        var str_html = "";
        if (data["title"].length != 0){
            for (var dt = 0; dt < data["title"].length; dt++) {
                if (now_date == data["title"][dt]){
                    t = dt;
                    str_title += "<th class='success'>" + data["title"][dt] + "</th>";
                }
                else{
                    str_title += "<th>" + data["title"][dt] + "</th>";
                }
            }
            str_title += "</tr>";
            str_title += "<tr>";
            str_title += "<th></th>";
            str_title += "<th></th>";
            for (var week = 0; week < data["week"].length; week++) {
                if (t == week){
                    str_title += "<th class='success'>" + week_day_dict[data["week"][week]] + "</th>";
                }
                else{
                    str_title += "<th>" + week_day_dict[data["week"][week]] + "</th>";
                }
            }
            str_title += "</tr>";
            $("#activity_monitor_title").html(str_title);


            for (var d = 0; d < data["data2"].length; d++) {
                str_html += "<tr>";
                str_html += "<td>" + data["ids"][d] + "</td>";
                str_html += "<td>" + data["name"][d] + "</td>";
                for (var s = 0; s<data["data2"][d].length; s++){
                    var temp = data["data2"][d][s];
                    if (temp == 0) {
                        str_html += "<td class='danger'>关闭</td>";
                    }
                    else if (temp == 1) {
                        str_html += "<td class='success'>开启</td>";
                    }
                    else if (temp == 2) {
                        str_html += "<td class='warning'>将开启</td>";
                    }
                }
                str_html += "</tr>";
            }
        }
        else{
            str_html += "</tr>";
            str_html += '<tr>';
            str_html += '<td colspan="2" class="text-center"><span class="label label-danger">无活动数据</span></td>';
            str_html += '</tr>';
        }

        $("#activity_monitor_list").html(str_html);
    };
    var req_data = {
        "section": $select_section.val(),
        "version": $activity_version.val(),
        'table_name': $select_activity_table.val()
    };
    my_ajax(true, "/activity/display", 'get', req_data, true, success);  
};


$("#btn_query").on("click", function (e) {
    e.preventDefault();
    display_activity_data();
});


var getSection = function () {
    if (SECTION_DATA == null){
        var success = function (data) {
            SECTION_DATA = data;
            make_section_select(SECTION_DATA);
        };
        my_ajax(true, "/querysection", "get", {}, true, success);    
    }else{
        make_section_select(SECTION_DATA);
    }

};
getSection();


$("#btn_validate").on("click", function (e) {
    e.preventDefault();
    
    Common.alert_message($("#error_modal"), 0, '接口未通');
    
    // var success = function(data){
    //     var str_html = "";
    //     for(var s=0; s<data.length; s++){
    //         var d_length = data[s]["data"].length;
    //         if (d_length != 0){
    //             str_html += "<tr>";
    //             str_html += "<td rowspan='" + d_length + "'>" +  data[s]["server"] + "区:" + data[s]["server_name"] + "</td>";
    //             for (var i=0; i<d_length; i++){
    //                 var a_id = data[s]["data"][i]["id"];
    //                 var a_name = data[s]["data"][i]["name"];
    //                 var status = data[s]["data"][i]["status"];
    //                 str_html += "<td>" + a_id + "</td>";
    //                 str_html += "<td>" + a_name + "</td>";
    //                 var close_html = "<td><span class='badge badge-danger'>关闭</span></td>";
    //                 var open_html = "<td><span class='badge badge-success'>开启</span></td>";
    //                 if (status == 0){
    //                     str_html += close_html;
    //                     str_html += open_html;    
    //                 }
    //                 else{
    //                     str_html += open_html;
    //                     str_html += close_html;
    //                 }
    //                 str_html += "</tr>";
    //             }
    //         }
    //         str_html += "</tr>";
    //     }
    //     $("#validate_list").html(str_html);
    //     $("#validate_activity_modal").modal("show");
    // };
    // var req_data = {
    //     section: $select_section.val()
    // };
    // my_ajax(true, "/activity/validate", 'get', req_data, true, success);
});


var query_activity_monitor = function(){
    var success = function (data) {
        var str_title = "<th>活动</th>";
        for (var dt = 0; dt < data["title"].length; dt++) {
            str_title += "<th>" + data["title"][dt] + "</th>";
        }
        $activity_title.html(str_title);
        var str_html = "";
        for (var ad in ACTIVITY_DATA) {
            var open_type = ACTIVITY_DATA[ad]["open_type"];
            if (open_type <= 3) {
                var activity_name = ACTIVITY_DATA[ad]["name"];
                str_html += "<tr>";
                str_html += "<td>" + activity_name + "</td>";
                for (var dd =0; dd < data["data"].length; dd++){
                    var array = data["data"][dd];
                    var tag = $.inArray(parseInt(ad), array);
                    if (tag == -1){
                        str_html += "<td class='danger'>关闭</td>";
                    }
                    else{
                        str_html += "<td class='success'>开启</td>";
                    }
                }
                str_html += "</tr>";
            }
        }
        $activity_list.html(str_html);
    };
    var server_id = $select_game.val();
    var req_data = {
        "server_id": server_id,
        "start": $start_date.val(),
        "end": $end_date.val()
    };
    my_ajax(true, "/activity/query", 'get', req_data, true, success);
};

// query_activity_monitor();

$select_game.on("change", function(e){
    e.preventDefault();
    query_activity_monitor();
});


$("#div_start_date").on("changeDate", function(e){
    e.preventDefault();
    query_activity_monitor();
});

$("#div_end_date").on("changeDate", function(e){
    e.preventDefault();
    query_activity_monitor();
});