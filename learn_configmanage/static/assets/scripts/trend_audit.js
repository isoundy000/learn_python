/**
 * Created by wangrui on 15/11/23.
 */


!function getTotal(){
    var success = function(data){
        console.log(data);
        for(var i=0; i<data["data"].length; i++){
            for (var k=0; k<data["data"][i].length; k++){
                console.log(data["data"][i][k]);
                var str_html = "";
                str_html += '<div class="col-lg-3 col-md-3 col-sm-6 col-xs-12"><div class="dashboard-stat blue"><div class="visual"></div><div class="details"><div class="number">';
                str_html += data["data"][i][k]  + '</div><div class="desc1">' + data["title"][k] + '</div></div></div></div>';
            }
        }
        $("#trend_list").html(str_html);
    };
    var req = {
        name: "trend"
    };
    my_ajax(true, "/queryaudit", "get", req, true, success);
}();

