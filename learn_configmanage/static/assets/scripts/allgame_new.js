/**
 * Created by wangrui on 15/5/11.
 */
get_left_game_server();
create_del_modal($("#start_game_modal"), "是否启动所选服务器?", "btn_start_confirm");
create_del_modal($("#alert_game_modal"), "是否重启所选服务器?", "btn_reboot_confirm");
create_del_modal($("#close_game_modal"), "是否关闭所选服务器?", "btn_halt_confirm");

var $gameserver_list = $("#gameserver_list");

function get_game_error(server){
    var sAjaxSource = "/getgameerror";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "platform",
            'sClass': 'center',
            "sTitle": "平台"
        },
        {
            "mDataProp": "server",
            'sClass': 'center',
            "sTitle": "游戏服"
        },
        {
            "mDataProp": "tag",
            'sClass': 'center',
            "sTitle": "错误类型"
        },
        {
            "mDataProp": "message",
            'sClass': 'center',
            "sTitle": "错误信息"
        },
        {
            "mDataProp": "otime",
            'sClass': 'center',
            "sTitle": "时间"
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html = "";
        if (aData.tag == "game"){
            str_html = "游戏";
        }
        else{
            str_html = "扩展";
        }
        $('td:eq(2)', nRow).html(str_html);
        return nRow;
    };
    var data = {
        server_id: server
    };
    dataTablePage($("#game_error_table"), aoColumns, sAjaxSource, data, false, fnRowCallback);
    $("#gameerror_modal").modal("show");
}


var get_game_status = function(server_id, h){
    var data = {
        server_id: server_id
    };
    var success = function(data){
        var run_html = "<span class='badge badge-success'>运行</span>";
        var stop_html = "<span class='badge badge-danger'>关闭</span>";
        var set_div = $gameserver_list.children('tr').eq(h).children('td');
        if (data["gate"] == "on") {
            set_div.eq(1).html(run_html);
        }
        else {
            set_div.eq(1).html(stop_html);
        }
        if (data["game"] == "on") {
            set_div.eq(2).html(run_html);
        }
        else {
            set_div.eq(2).html(stop_html);
        }
        if (data["ext"] == "on") {
            set_div.eq(3).html(run_html);
        }
        else {
            set_div.eq(3).html(stop_html);
        }
    };
    my_ajax(true, "/getgamestatus", "get", data, true, success);
};

var get_one_line = function(server_id, m){
    var data = {
        server_id: server_id
    };
    var success = function(data){
        var set_div = $gameserver_list.children('tr').eq(m).children('td');
        if (data["online"]["status"] == "success") {
            set_div.eq(5).html(data["online"]["total"]);
            set_div.eq(6).html(data["online"]["online"]);
            set_div.eq(7).html(data["online"]["cache"]);
        }
        set_div.eq(8).html(data["servertime"]["value"]);
    };
    my_ajax(true, "/getoneonline", "get", data, true, success);
};


var getAllGame = function () {
    var data = {
        tag: 1
    };
    var success = function(data){
        var str_info = "";
        if (data.length != 0) {
            var k = 0;
            for (var i in data) {
                str_info += "<tr>";
                str_info += "<td>" + "<div class='checkbox-list'>";
                str_info += "<label> <input type=\"checkbox\" name=\"check_game\" value=\"" +
                    data[i]["gameid"] + "\">" + data[i]["gameid"] + "区:" + data[i]["name"] + "</label></div></td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                str_info += "<td>" + "</td>";
                if (data[i]["error"] == 0) {
                    str_info += "<td>" + "<span class='badge badge-success'>0</span></td>";
                }
                else {
                    str_info += "<td><a onclick='get_game_error(" + data[i]["gameid"] + ")'>" + "<span class='badge badge-danger'>" + data[i]["error"] + "</span></a></td>";
                }

                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
                str_info += "<td>";
                str_info += "<a class='badge badge-success' onclick='flush_online(" + data[i]["gameid"] + "," + k + ")'>" + "刷新"  + "</a>";
                str_info += "&nbsp;<a class='badge badge-info' href='/game_manage?server_id=" + data[i]["gameid"] + "'>游戏管理" + "</a>";
                str_info += "&nbsp; <a class='badge badge-default' href='/data_manage?server_id=" + data[i]["gameid"] + "'>数据管理" + "</td>";
                str_info += "</tr>";
                k += 1;
            }
            var h = 0;
            for (var s in data){
                get_game_status(data[s]["gameid"], h);
                h += 1;
            }
            var m = 0;
            for (var n in data){
                get_one_line(data[n]["gameid"], m);
                m += 1;
            }
        }
        else {
            str_info += "<tr>";
            str_info += '<td colspan="7" class="text-center"><span class="label label-danger">无数据</span></td>';
            str_info += '</tr>';
        }
        $gameserver_list.html(str_info);
    };

    my_ajax(true, "/getallgame", "get", data, true, success);
};
getAllGame();

function flush_online(server, col){
    get_game_status(server, col);
    get_one_line(server, col);
}

function set_game_service(game_tag, method) {
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var game_list = [];
    $("input[name='check_game']").each(function(e){
        if ($(this).is(":checked")){
            game_list.push($(this).val());
        }
    });
    $.ajax({
            type: 'get',
            url: '/setallgameservice',
            data: {server_list: JSON.stringify(game_list), game_tag: game_tag, method: method},
            dataType: 'JSON',
            success: function (data, xm) {
                App.unblockUI(page_content);
                setTimeout("getAllGame()", 5000);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                console.log("eroor", XMLHttpRequest);
                error_func(XMLHttpRequest);
            }
        }
    )
}

function check_game(){
    var str_game = "";
    var str_list = [];

    $("input[name='check_game']").each(function(e){
        str_game += $(this).val() + ",";
        if($(this).is(":checked")){
            str_list.push($(this).val());
        }
    });
    if(str_list.length == 0){
        show_error_modal(0, "请选择区服.");
        return false;
    }
    return true;
}


function start_game(method){
    $("#btn_start_confirm").attr("onclick", "set_game_service(1," + method + ")");
    $("#start_game_modal").modal("show");
}


function close_game(method){
    $("#btn_halt_confirm").attr("onclick", "set_game_service(2," + method + ")");
    $("#close_game_modal").modal("show");
}


function reboot(method){
    set_game_service(3, method);
}


$("#gate_reboot_game").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        $("#btn_reboot_confirm").attr("onclick", "reboot(2)");
        $("#alert_game_modal").modal("show");
    }
});

$("#gate_start_game").on("click", function(e){
    e.preventDefault();
    if (check_game())
        start_game(2);
});

$("#close_gate").on("click", function(e){
    e.preventDefault();
    if (check_game())
        close_game(2);
});

//网关模式game控制
$("#gate_game_reboot_game").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        $("#btn_reboot_confirm").attr("onclick", "reboot(1)");
        $("#alert_game_modal").modal("show");
    }
});

$("#gate_game_start_game").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        start_game(1);
    }
});

$("#close_gate_game").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        close_game(1);
    }
});

//网关模式ext控制
$("#reboot_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        $("#btn_reboot_confirm").attr("onclick", "reboot(4)");
        $("#alert_game_modal").modal("show");
    }
});

$("#start_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        start_game(4);
    }
});

$("#close_ext2").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        close_game(4);
    }
});

//网关模式总控制
$("#reboot_all").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        $("#btn_reboot_confirm").attr("onclick", "reboot(5)");
        $("#alert_game_modal").modal("show");
    }
});

$("#start_all").on("click", function(e){
    e.preventDefault();
    if (check_game()) {
        start_game(5);
    }
});

$("#close_all").on("click", function(e){
    e.preventDefault();
    if (check_game()){
        close_game(5);
    }

});


$("#all_check").on("change", function (e) {
    e.preventDefault();
    var $check_game = $("input[name='check_game']");

    if ($(this).is(":checked")) {
        $check_game.prop("checked", true);
        $check_game.parent("span").addClass("checked");
    }
    else{
        $check_game.prop("checked", false);
        $check_game.parent("span").removeClass("checked");
    }
});

$("#flush_current").bind("click", function(e){
    e.preventDefault();
    getAllGame();
});