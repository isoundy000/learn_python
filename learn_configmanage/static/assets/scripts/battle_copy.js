/**
 * Created by wangrui on 15/10/21.
 */


var JSON_DATA = null;
var copy_array = ["map", "copy", "general", "copy_monster"];
var GENERAL_JSON = {};

var quality_css = {
    2: "btn green",
    3: "btn blue",
    4: "btn purple",
    5: "btn yellow"
};
var quality_css2 = {
    2: "label label-success",
    3: "label label-info",
    4: "label label-purple",
    5: "label label-warning"
};

getGameServerData($("#game_server"), 1);


var set_map_data = function(){
    var str_html = MakeOptionList(JSON_DATA["map"], MyGetDataFunc);
    var $map1 = $("#maps");
    var $map2 = $("#maps_2");
    var $map3 = $("#maps_3");
    $map1.html(str_html);
    $map2.html(str_html);
    $map3.html(str_html);

    $map1.change();
    $map2.change();
    $map3.change();
};

var init_json_data = function(){
    var server_id = $("#game_server").val();
    $.ajax({
            type: 'get',
            url: "/queryjsondatabyserver",
            data: {
                server_id: server_id,
                type: JSON.stringify(copy_array)
            },
            dataType: 'JSON',
            success: function (data) {
                JSON_DATA = data;
                get_battle_data();
                set_map_data();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
};
init_json_data();

var get_battle_data = function(){
    $.ajax({
        type: 'get',
        url: '/getallbattle',
        dataType: 'JSON',
        success: function (data) {
            var str_html = "";

            for (var i in data) {
                str_html += "<option value='" + data[i]["id"] + "'>" + data[i]["name"] + "</option>";
                GENERAL_JSON[data[i]["id"]] = data[i];
            }
            $("#battle_data").html(str_html);
            $("#battle_data").change();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


var display_npc = function(){
    var maps = $("#maps").val();
    var point = $("#point").val();
    var power = JSON_DATA["copy"][maps][point]["power"];
    $("#npc_power").html(power);

    var str_html = "";
    for(var i = 1; i <= 7; i ++){
        var p_str = JSON_DATA["copy"][maps][point]["p" + i];
        if(p_str != 0){
            str_html += "<tr>";
            var quality = JSON_DATA["copy_monster"][p_str]["quality"];
            var general_name = JSON_DATA["copy_monster"][p_str]["name"];
            if (i % 2 == 0){
                str_html += "<td>" + "</td>";
                str_html += "<td><button onclick='get_property2(" + i + "," + parseInt(p_str) + ")' class='" + quality_css[quality] + "'>" +  general_name +  "</button><td>";
            }
            else{
                str_html += "<td><button onclick='get_property2(" + i + "," + parseInt(p_str) + ")' class='" + quality_css[quality] + "'>" +  general_name +  "</button><td>";
                str_html += "<td>" + "</td>";
            }
            str_html += "</tr>";
        }
    }
    $("#table_2").html(str_html);
};

var get_property2 = function(pos, cid){
    var server_id = $("#game_server").val();
    var map = $("#maps").val();
    var point = $("#point").val();
    $.ajax({
        type: 'get',
        url: "/npc_details",
        data: {
            tag: 1,
            pos: pos,
            map: map,
            point: point,
            server_id: server_id
        },
        dataType: 'JSON',
        success: function (data) {
            if(data["status"] == "success"){
                show_general_modal("copy_monster", data, cid);
            }
            else{
                Common.alert_message($("#error_modal"), 0, data["errmsg"]);
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


$("#battle_data").on("change", function(e){
    e.preventDefault();
    var battle_id = $("#battle_data").val();
    var power = GENERAL_JSON[battle_id]["power"];
    $("#power").html(power);
    var parse_json = $.parseJSON(GENERAL_JSON[battle_id]["json"]);
    var str_html = "";
    for(var p in parse_json["data"]["slot"]){
        var s = parseInt(p);
        var cid = 0;
        if (parseInt(p) == 0){
            s = parseInt(p) + 1;
        }
        else if (p == 1){
            s = parseInt(p) - 1;
        }
        str_html += "<tr>";
        cid = parse_json["data"]["slot"][s]["cid"];
        var quality = JSON_DATA["general"][cid]["quality"];
        var general_name = JSON_DATA["general"][cid]["name"];

        if (parseInt(p) % 2 == 0){
            str_html += "<td><button onclick='get_property(" + (parseInt(p)+1) + "," + parseInt(cid) + ")' class='" + quality_css[quality] + "'>" +  general_name +  "</button><td>";
            str_html += "<td>" + "</td>";
        }

        else{
            str_html += "<td>" + "</td>";
            str_html += "<td><button onclick='get_property(" + (parseInt(p)+1) + "," + parseInt(cid) + ")' class='" + quality_css[quality] + "'>" +  general_name +  "</button><td>";
        }
        str_html += "</tr>";
    }
    $("#table_1").html(str_html);
});

var show_general_modal = function(tag, data, cid){

    var quality = JSON_DATA[tag][cid]["quality"];
    var html = "<span class='" + quality_css2[quality] + "'>" + JSON_DATA[tag][cid]["name"] + "</span>";
    var generalData = data["data"];
    var attr_array = ["hp", "atk", "def", "speed", "critical", "resilience", "parry", "arp", "dodge",
                       "hit", "adddmg", "subdmg", "criticaldmg"];
    $("#general_name").html(html);
    $("#general_power").html(generalData["power"]);
    for(var attr in attr_array){
        $("#"+attr_array[attr]).html(generalData[attr_array[attr]]);
    }
    $("#general_modal").modal("show");
};

var get_property = function(slot_num, cid){
    var battle_id = $("#battle_data").val();
    var server_id = $("#game_server").val();
    $.ajax({
        type: 'get',
        url: "/general_details",
        data: {
            pos: slot_num,
            server_id: server_id,
            battle_id: battle_id
        },
        dataType: 'JSON',
        success: function (data) {
            if(data["status"] == "success"){
                show_general_modal("general", data, cid);
            }
            else{
                Common.alert_message($("#error_modal"), 0, data["errmsg"]);
            }
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};


$("#maps").on("change", function(e){
    e.preventDefault();
    var maps = $("#maps").val();
    var str_html = "";
    for(var i in JSON_DATA["copy"][maps]){
         str_html += "<option value='" + i + "'>" + i + "_" + JSON_DATA["copy"][maps][i]["name"] + "</option>";
    }
    $("#point").html(str_html);
    $("#point").change();
});

$("#maps_2").on("change", function(e){
    e.preventDefault();
    var maps = $("#maps_2").val();
    var str_html = "";
    for(var i in JSON_DATA["copy"][maps]){
         str_html += "<option value='" + i + "'>" + i + "_" + JSON_DATA["copy"][maps][i]["name"] + "</option>";
    }
    $("#point_2").html(str_html);
    $("#point_2").change();
});

$("#maps_3").on("change", function(e){
    e.preventDefault();
    var maps = $("#maps_3").val();
    var str_html = "";
    for(var i in JSON_DATA["copy"][maps]){
         str_html += "<option value='" + i + "'>" + i + "_" + JSON_DATA["copy"][maps][i]["name"] + "</option>";
    }
    $("#point_3").html(str_html);
    $("#point_3").change();
});


$("#point").on("change", function(e){
    e.preventDefault();
    display_npc();
});

$("#point_2").on("change", function(e){
    e.preventDefault();
    var maps = $("#maps_2").val();
    var point = $("#point_2").val();
    $("#copy_power_2").html(JSON_DATA["copy"][maps][point]["power"])
});

$("#point_3").on("change", function(e){
    e.preventDefault();
    var maps = $("#maps_3").val();
    var point = $("#point_3").val();
    $("#copy_power_3").html(JSON_DATA["copy"][maps][point]["power"])
});


$("#start_battle").on("click", function(e){
    var server_id = $("#game_server").val();
    var battle_data_id = $("#battle_data").val();
    var map = $("#maps").val();
    var point = $("#point").val();
    var battle_count = $("#battle_count").val();
    var pageContent = $('.page-content');
    var copy_list = [
        {
            "map": map,
            "point": point,
            "count": battle_count
        }
    ];
    App.blockUI(pageContent, false);
    $.ajax({
            type: 'post',
            url: "/startbattle",
            data: {
                tag: 1,
                server_id: server_id,
                battle_data_id: battle_data_id,
                copy_list: JSON.stringify(copy_list)
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(pageContent);
                console.log(data);
                for(var i in data){
                    if (data[i]["result"]["status"] == "success") {
                        $("#star3").html(data[i]["result"]["star3"]);
                        $("#star2").html(data[i]["result"]["star2"]);
                        $("#star1").html(data[i]["result"]["star1"]);
                        $("#fail").html(data[i]["result"]["fail"]);
                        var str_html = "";
                        for(var s = 1; s <= 10; s ++){
                            if (data[i]["result"]["round" + s] != 0 ){
                                str_html += "<div class=\"form-group\">" +
                                            "<label class=\"control-label col-md-1\">战斗" + s + "回合:</label>" +
                                            "<div class=\"col-md-3\"><span class=\"badge badge-success\">" +
                                            data[i]["result"]["round" + s] + "</span></div></div>";
                            }

                        }
                        $("#round").html(str_html);
                    }
                    else{
                        Common.alert_message($("#error_modal"), 0, data[i]["result"]["errmsg"]);
                    }
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

var G_COPY = null;

$('#start_battle_more').on("click", function(e){
    var server_id = $("#game_server").val();
    var battle_data_id = $("#battle_data").val();
    var map_2 = parseInt($("#maps_2").val());
    var point_2 = parseInt($("#point_2").val());
    var pageContent = $('.page-content');

    var map_3 = parseInt($("#maps_3").val());
    var point_3 = parseInt($("#point_3").val());
    var copy_list = [];
    for (var c in JSON_DATA["copy"]){
        if (parseInt(c) >= map_2 && parseInt(c) <= map_3) {
            for (var k in JSON_DATA["copy"][c]){
                if (parseInt(c) == map_2){
                    if (parseInt(k) < point_2){
                        continue;
                    }
                }
                if (parseInt(c) == map_3) {
                    if (parseInt(JSON_DATA["copy"][c][k]["point"]) > point_3) {
                        continue;
                    }
                }
                copy_list.push(
                    {
                        "map": parseInt(c),
                        "point": parseInt(JSON_DATA["copy"][c][k]["point"]),
                        "count": 1
                    }
                );
            }
        }
    }
    App.blockUI(pageContent, false);
    $.ajax({
            type: 'post',
            url: "/startbattle",
            data: {
                tag: 1,
                server_id: server_id,
                battle_data_id: battle_data_id,
                copy_list: JSON.stringify(copy_list)
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(pageContent);
                var str_html = "";
                var temp = [];
                G_COPY = data;
                for(var i in data){
                    str_html += "<div class='row'>";
                    str_html += "<div class='col-md-2'><span>" + data[i]["map"] + "_" + JSON_DATA["map"][data[i]["map"]]["name"] + "</span></div>";
                    str_html += "<div class='col-md-2'><span>" + data[i]["point"] + "_" + JSON_DATA["copy"][data[i]["map"]][data[i]["point"]]["name"] + "</span></div>";
                    str_html += "<div class='col-md-2'>3星:<span class='badge badge-success'>" + data[i]["result"]["star3"] + "</span></div>";
                    str_html += "<div class='col-md-2'>2星:<span class='badge badge-success'>" + data[i]["result"]["star2"] + "</span></div>";
                    str_html += "<div class='col-md-2'>1星:<span class='badge badge-success'>" + data[i]["result"]["star1"] + "</span></div>";
                    str_html += "<div class='col-md-2'>失败:<span class='badge badge-danger'>" + data[i]["result"]["fail"] + "</span></div>";
                    str_html += "</div>";

                    var result = 0;
                    if (data[i]["result"]["star3"] != 0){
                        result = 3;
                    }
                    else if (data[i]["result"]["star2"] != 0){
                        result = 2;
                    }
                    else if (data[i]["result"]["star1"] != 0){
                        result = 1;
                    }
                    temp.push([parseInt(i), result]);
                }
                var data_set = [
                    {
                        label: "普通副本",
                        data: temp
                    }
                ];
                DrawLineChart(data_set, $("#chart_battle"));
            },

            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
});

var g_map = 0;

var DrawLineChart = function (dataset, div_flot) {
    var options = {
        series: {
            lines: {
                show: true,
                lineWidth: 2,
                fill: true,
                fillColor: {
                    colors: [
                        {
                            opacity: 0.05
                        },
                        {
                            opacity: 0.01
                        }
                    ]
                }
            },
            points: {
                show: true,
                radius: 1
            },
            shadowSize: 2
        },
        grid: {
            hoverable: true,
            clickable: true,
            tickColor: "#eee",
            borderWidth: 0
        },
        colors: ["#37b7f3", "#d12610",  "#52e136"],
        xaxis: {
            axisLabel: "据点",
            ticks: 2,
            tickDecimals: 0,
            tickSize: 1,
            tickFormatter: function(v, axis){
//                var temp = JSON_DATA["copy"][G_COPY[v]["map"]][G_COPY[v]["point"]]["name"];
                var temp = "";
                if (G_COPY[v]["map"] != g_map){
                    temp = "<span style='color: red'>"  + JSON_DATA["map"][G_COPY[v]["map"]]["name"] + "</span>";
                    g_map = G_COPY[v]["map"];
                }
                return temp;
            }
        },
        yaxis: {
            ticks: 11,
            max: 3,
            tickDecimals: 0,
            tickFormatter: function(v, axis){
                if (v == 0){
                    return "失败";
                }
                return v + "星";
            }
        }
    };

    $.plot(div_flot, dataset, options);
};

var previousPoint = null;
$("#chart_battle").bind("plothover", function (event, pos, item) {
    $("#x").text(pos.x.toFixed(2));
    $("#y").text(pos.y.toFixed(2));

    if (item) {
        if (previousPoint != item.dataIndex) {
            previousPoint = item.dataIndex;

            $("#tooltip").remove();
            var x = item.datapoint[0],
                y = item.datapoint[1];

            var temp = "";
            if (y == 0){
                temp = "失败";
            }
            else{
                temp = y + "星";
            }
            var round = 0;
            for(var i = 1; i <= 10; i++){
                if (G_COPY[x]["result"]["round" + i] == 1){
                    round = i;
                    break;
                }
            }
            var dis_html = "地图:" + G_COPY[x]["map"] + "_" + JSON_DATA["map"][G_COPY[x]["map"]]["name"] + "</br>" +
                "据点:" + G_COPY[x]["point"] + "_" + JSON_DATA["copy"][G_COPY[x]["map"]][G_COPY[x]["point"]]["name"]+ "</br>" +
                "战斗力:" + JSON_DATA["copy"][G_COPY[x]["map"]][G_COPY[x]["point"]]["power"] + "</br>" + "结果:" + temp + "</br>" +
                "回合:" + round;
            showTooltip(item.pageX, item.pageY, dis_html);
        }
    } else {
        $("#tooltip").remove();
        previousPoint = null;
    }
});
