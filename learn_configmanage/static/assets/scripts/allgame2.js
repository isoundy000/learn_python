/**
 * Created by wangrui on 15/5/11.
 */
var $gameserver_list = $("#gameserver_list");

var get_one_line = function (server_id, m) {
    var data = {
        server_id: server_id
    };
    var success = function (data) {

        var set_div = $gameserver_list.children('tr').eq(m).children('td');
        if (data["online"]["status"] == "success") {
            set_div.eq(1).html("<span class='badge badge-success'>运行</span>");
            set_div.eq(2).html(data["online"]["total"]);
            set_div.eq(3).html(data["online"]["online"]);
            set_div.eq(4).html(data["servertime"]["value"]);
        }
        else{
            set_div.eq(1).html("<span class='badge badge-danger'>关闭</span>");
        }
    };
    my_ajax(true, "/server/getoneonline", "get", data, true, success);
};

var getAllGame = function () {

    var data = {
        tag: 2
    };
    var success = function(data){
        var str_info = "";
        if (data.length != 0) {
            for (var i in data) {
                str_info += "<tr>";
                str_info += "<td>" + data[i]["gameid"] + "区:" + data[i]["name"] + "</td>";

                str_info += "<td></td>";
                str_info += "<td>0</td>";
                str_info += "<td>0</td>";
                str_info += "<td></td>";
                str_info += "</tr>";
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

$("#flush_current").bind("click", function(e){
    e.preventDefault();
    getAllGame();
});