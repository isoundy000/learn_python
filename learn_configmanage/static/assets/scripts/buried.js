/**
 * Created by wangrui on 14-10-15.
 */
getGameServerData($("#select_gameserver"), 1);

var enter_guide = null;

handleDatePickers();
$("#text_liveness_date").val(getNowFormatDate(1));
$("#login_start_date").val(getNowFormatDate(1));
$("#login_end_date").val(getNowFormatDate(1));

$("#online_start_date").val(getNowFormatDate(1));
$("#online_end_date").val(getNowFormatDate(1));

$("#login_num_start_date").val(getNowFormatDate(1));
$("#login_num_end_date").val(getNowFormatDate(1));

$("#guide_date").val(getNowFormatDate(1));

$("#copy_count_start_date").val(getNowFormatDate(1));
$("#copy_count_end_date").val(getNowFormatDate(1));

$("#copy_start_date").val(getNowFormatDate(1));
$("#copy_end_date").val(getNowFormatDate(1));

$("#brave_copy_count_date").val(getNowFormatDate(1));
$("#brave_copy_date").val(getNowFormatDate(1));

$("#strengthen_start_date").val(getNowFormatDate(1));
$("#strengthen_end_date").val(getNowFormatDate(1));

$("#rid_ip_start_date").val(getNowFormatDate(1));
$("#rid_ip_end_date").val(getNowFormatDate(1));

$("#limit_shop_start_date").val(getNowFormatDate(1));
$("#limit_shop_end_date").val(getNowFormatDate(1));

$("#world_boss_date").val(getNowFormatDate(1));

create_del_modal($("#param_del_modal"), "是否删除此参数?", "del_param_btn");
create_del_modal($("param_data_del_modal"), "是否删除此埋点漏斗数据?", "del_param_data_btn");


var LOGIN_TYPE = {
    "1": "正常",
    "2": "重连",
    "3": "断网",
    "4": "超时重连",
    "11": "首冲",
    "12": "商城",
    "13": "领奖",
    "14": "副本",
    "15": "体力"
};

var QUALITY_CSS = {
    2: "success",
    3: "primary",
    4: "purple",
    5: "warning"
};

var GUIDE_JSON = null;
var GUIDE_STEP_JSON = null;
var COPY_JSON = null;
var GENERAL_COPY_JSON = null;
var MAP_JSON = null;
var GENERAL_MAP = null;
var DATA = null;


var CONFIG_TYPE = ["guide_section", "guide_step", "copy", "star_copy", "star_map", "map", "mystery_shop", "general_fragment", "props", "general"];

function init_type(){
    var str_info = "";
    for(var u in LOGIN_TYPE){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"login_type\" value=\"" +
                    u + "\">" + LOGIN_TYPE[u] + "</label>";
    }
    $("#login_type").html(str_info);
}
init_type();




var init_data = function(){

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var server_id = $("#select_gameserver").val();
    $.ajax({
            type: 'get',
            url: "/queryjsondatabyserver",
            data: {
                server_id: server_id,
                type: JSON.stringify(CONFIG_TYPE)
            },
            async: false,
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                DATA = data;
                GUIDE_JSON = data["guide_section"];
                GUIDE_STEP_JSON = data["guide_step"];
                COPY_JSON = data["copy"];
                GENERAL_COPY_JSON = data["star_copy"];
                GENERAL_MAP = data["star_map"];
                MAP_JSON = data["map"];
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        }
    )

};


setTimeout("init_data()", 2000);

$("#select_gameserver").on("change", function (e) {
    e.preventDefault();
    init_data();
});


$("#a_guide").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var select_area = $("#select_area");
    for (var s in GUIDE_JSON){
        str_info1 += "<option value='" + s + "'>" + s + "</option>";
    }
    select_area.html(str_info1);
    select_area.change();
    $("#btn_guide").click();
});

$("#select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='guide_step_type']").prop("checked", true);
    $("input[name='guide_step_type']").parent("span").addClass("checked");
});

$("#no_select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='guide_step_type']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});

$("#login_select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='login_type']").prop("checked", true);
    $("input[name='login_type']").parent("span").addClass("checked");
});

$("#no_login_select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='login_type']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});

$("#copy_select_all").bind("click", function(e){
    e.preventDefault();
    var copy_map_type = $("input[name='copy_map_type']");
    copy_map_type.prop("checked", true);
    copy_map_type.parent("span").addClass("checked");
});

$("#copy_no_select_all").bind("click", function(e){
    e.preventDefault();
    $("input[name='copy_map_type']").each(function(){
        if ($(this).is(":checked")){
            $(this).prop("checked", false);
            $(this).parent("span").removeClass("checked");
        }
        else{
            $(this).prop("checked", true);
            $(this).parent("span").addClass("checked");
        }
    });
});


$("#select_area").on("change", function(e){
    e.preventDefault();
    var area = $("#select_area").val();
    var str_info = "";
    var area_array = GUIDE_STEP_JSON[area];
    for (var i in area_array) {
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"guide_step_type\" value=\"" +
                    area_array[i]["step"] + "\">" + area_array[i]["_param2"] + "</label>";
    }
    $("#guide_step").html(str_info);
});

var get_temp_json = function(div_type){
    var tag = div_type.val();
    var temp_json = null;
    if (tag == "1"){
        temp_json = COPY_JSON;
    }
    else{
        temp_json = GENERAL_COPY_JSON;
    }
    return temp_json;
};


$("#a_copy_count").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var temp_json = get_temp_json($("#select_copy_type"));

    var select_section = $("#select_section");
    for (var s in temp_json){
        str_info1 += "<option value='" + s + "'>" + s + "_" + MAP_JSON[s]["name"] + "</option>";
    }
    select_section.html(str_info1);
    select_section.change();
});

$("#select_section").on("change", function(e){
    e.preventDefault();
    var temp_json = get_temp_json($("#select_copy_type"));
    var select_section = $("#select_section").val();
    var str_info = "";
    var section_array = temp_json[select_section];
    for(var i in section_array){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"copy_map_type\" value=\"" +
                    section_array[i]["point"] + "\">" + section_array[i]["point"] + "_" + section_array[i]["name"] + "</label>";
    }
    $("#select_map").html(str_info);
});

$("#a_brave_copy_count").on("click", function(e){
    e.preventDefault();
    var str_info1 = "";
    var select_brave_section = $("#select_brave_section");
    for (var s in GENERAL_COPY_JSON){
        str_info1 += "<option value='" + s + "'>" + s + "</option>";
    }
    select_brave_section.html(str_info1);
    select_brave_section.change();
});

$("#select_brave_section").on("change", function(e){
    e.preventDefault();
    var select_brave_section = $("#select_brave_section").val();
    var str_info = "";
    var section_array = COPY_JSON[select_brave_section];
    for(var i in section_array){
        str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"brave_copy_type\" value=\"" +
                    section_array[i]["point"] + "\">" + section_array[i]["name"] + "</label>";
    }
    $("#select_brave_map").html(str_info);
});



//新手引导时间查询
$("#btn_guide").on("click", function(e){
    e.preventDefault();
    var guide_date = $("#guide_date").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    var server_id = $("#select_gameserver").val();
    $.ajax({
            type: 'get',
            url: '/queryguidebytime',
            data: {server_id: server_id, guide_date: guide_date},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                $("#enter_guide").html(data["enter"]);
                enter_guide = data["enter"];
                $("#choose_profile").html(data["choose_profile"]);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

//新手引导类型查询
$("#btn_type_guide").on("click", function(e){
    e.preventDefault();
    var select_area = $("#select_area").val();
    var guide_date = $("#guide_date").val();
    var server_id = $("#select_gameserver").val();
    var guide_step_type = "";
    $("input[name='guide_step_type']:checked").each(function(){
        guide_step_type += $(this).val() + ",";
    });
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/queryguidebytype',
            data: {
                    server_id: server_id,
                    guide_date: guide_date,
                    select_area: select_area,
                    guide_step_type: guide_step_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){
                    var temp = enter_guide;
                    for(var i in data){
                        str_info += "<tr>";
                        str_info += "<td>" + GUIDE_STEP_JSON[select_area][i]["_param2"] + "</td>";
                        str_info += "<td>" + data[i] + "</td>";
                        str_info += "<td>" + (temp - data[i]) + "</td>";
                        str_info += "</tr>";
                        temp = data[i];
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#guide_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});


$("#btn_copy_count").on("click", function(e){
    e.preventDefault();
    var select_copy_type = $("#select_copy_type").val();
    var select_section = $("#select_section").val();
    var select_map = "";
    $("input[name='copy_map_type']:checked").each(function(){
        select_map += $(this).val() + ",";
    });
    var start_date = $("#copy_count_start_date").val();
    var end_date = $("#copy_count_end_date").val();
    var page_content = $('.page-content');
    var server_id = $("#select_gameserver").val();
    App.blockUI(page_content, false);
    var temp_json = null;
    if (select_copy_type == "1") {
        temp_json = COPY_JSON;
    }
    else {
        temp_json = GENERAL_COPY_JSON
    }
    $("#copy_count_list").empty();
    $.ajax({
        type: 'get',
        url: '/querycopycount',
        data: {
            server_id: server_id,
            select_copy_type: select_copy_type,
            start_date: start_date,
            end_date: end_date,
            select_section: select_section,
            select_map: select_map
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0) {
                for (var i in data) {
                    str_info += "<tr>";
                    str_info += "<td>" + temp_json[select_section][i]["name"] + "</td>";
                    str_info += "<td>" + data[i]["c1"] + "</td>";
                    str_info += "<td>" + data[i]["c2"] + "</td>";
                    str_info += "<td>" + data[i]["c3"] + "</td>";
                    str_info += "<td>" + data[i]["c4"] + "</td>";
                    str_info += "<td>" + data[i]["c5"] + "</td>";
                    str_info += "<td>" + data[i]["c6"] + "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="8" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#copy_count_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
});

$("#btn_copy").on("click", function(e){
    e.preventDefault();
    var s_type = $("#s_type").val();

    var copy_start_date = $("#copy_start_date").val();
    var copy_end_date = $("#copy_end_date").val();
    var page_content = $('.page-content');
    var server_id = $("#select_gameserver").val();
    App.blockUI(page_content, false);
    $("#copy_list").empty();
    $.ajax({
            type: 'get',
            url: '/querycopylimit',
            data: {
                s_type: s_type,
                server_id: server_id,
                copy_start_date: copy_start_date,
                copy_end_date: copy_end_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                var T_JSON = null;
                var T_JSON2 = null;
                if (s_type == 1){
                    T_JSON = MAP_JSON;
                    T_JSON2 = COPY_JSON;
                }
                else{
                    T_JSON = GENERAL_MAP;
                    T_JSON2 = GENERAL_COPY_JSON;
                }
                if(data.length != 0){
                    for(var i in data){
                        for(var s in data[i]){
                            str_info += "<tr>";
                            str_info += "<td>" + i + "_" + T_JSON[i]["name"] + "</td>";
                            str_info += "<td>" + s + "_" + T_JSON2[i][s]["name"] + "</td>";
                            str_info += "<td>" + data[i][s] + "</td>";
                            str_info += "</tr>";
                        }
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#copy_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});


$("#btn_online").on("click", function(e){
    e.preventDefault();
    var online_param = $("#online_param").val();
    var start_date = $("#online_start_date").val();
    var end_date = $("#online_end_date").val();
    var page_content = $('.page-content');
    var server_id = $("#select_gameserver").val();
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/queryonlinedata',
            data: {
                server_id: server_id,
                online_param: online_param,
                start_date: start_date,
                end_date: end_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                if(data.length != 0){
                    for(var i=0; i < data.length; i ++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[i][0] + "</td>";
                        str_info += "<td>" + data[i][1] + "</td>";
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="2" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }
                $("#online_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

$("#btn_login").on("click", function(e){
    e.preventDefault();
    var login_start_date = $("#login_start_date").val();
    var login_end_date = $("#login_end_date").val();
    var login_param = $("#login_param").val();
    var login_type = "";
    var server_id = $("#select_gameserver").val();
    $("input[name='login_type']:checked").each(function(){
        login_type += $(this).val() + ",";
    });
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/queryrolecount',
            data: {
                server_id: server_id,
                login_param: login_param,
                start_date: login_start_date,
                end_date: login_end_date,
                login_type: login_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var str_info = "";
                var str_title = "<tr><th>漏斗名称</th>";
                $("input[name='login_type']:checked").each(function(){
                    str_title += "<th>" + LOGIN_TYPE[$(this).val()] + "</th>";
                });
                str_title += "</tr>";
                if(data.length != 0){
                    for(var s=0; s<data.length; s++){
                        str_info += "<tr>";
                        str_info += "<td>" + data[s][0] + "</td>";
                        for (var i in data[s][1]){
                            str_info += "<td>";
                            str_info +=  data[s][1][i];
                            str_info += "</td>";
                        }
                        str_info += "</tr>";
                    }
                }
                else{
                    str_info += "<tr>";
                    str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                    str_info += '</tr>';
                }

                $("#buried_title").html(str_title);
                $("#buried_list").html(str_info);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

$("#btn_strengthen").on("click", function(e){
    e.preventDefault();
    var strengthen_start_date = $("#strengthen_start_date").val();
    var strengthen_end_date = $("#strengthen_end_date").val();
    var strengthen_param = $("#strengthen_param").val();
    var server_id = $("#select_gameserver").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/querystrengthen',
        data: {
            server_id: server_id,
            start_date: strengthen_start_date,
            end_date: strengthen_end_date,
            strengthen_param: strengthen_param
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                    str_info += "<tr>";
                    str_info += "<td>" + data[i][0] + "</td>";
                    str_info += "<td>" + data[i][1] + "</td>";
                    str_info += "<td>" + data[i][2] + "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#strengthen_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
});


//登陆次数
$('#btn_login_num').on('click', function(e){
    e.preventDefault();
    var login_start_date = $("#login_num_start_date").val();
    var login_end_date = $("#login_num_end_date").val();
    var login_type = "c1";
    var server_id = $("#select_gameserver").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/queryloginnum',
            data: {
                server_id: server_id,
                start_date: login_start_date,
                end_date: login_end_date,
                login_type: login_type
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var ave_login_num = "<p>" + data['ave_login_num'] + "次" + "</p>";
                var role_rid = "";
                if (data['ave_login_num'] != 0) {
                    for (var i in data['role_login']) {
                        role_rid += "<tr>";
                        role_rid += "<td class='active'>" + i + "</td>";
                        role_rid += "<td class='success'>" + data['role_login'][i]['name'] + "</td>";
                        role_rid += "<td class='warning'>" + data['role_login'][i]['login_num'] + "次" + "</td>";
                        role_rid += "</tr>";
                    }
                }else{
                    role_rid += "<tr>";
                    role_rid += '<td colspan="3" class="text-center"><span class="label label-danger">无登陆数据</span></td>';
                    role_rid += '</tr>';
                }
                $("#ave_login_num").html(ave_login_num);
                $("#login_num_list").html(role_rid);

            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

//登陆ip_rid
$('#btn_rid_ip').on('click', function(e){
    e.preventDefault();
    var server_id = $("#select_gameserver").val();
    var key_val = $("#rid_ip_param").val();

    var rid_ip_start_date = $("#rid_ip_start_date").val();
    var rid_ip_end_date = $("#rid_ip_end_date").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
            type: 'get',
            url: '/query_rid_ip',
            data: {
                server_id: server_id,
                start_date: rid_ip_start_date,
                end_date: rid_ip_end_date,
                key_val: key_val
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var rid_ip = "";
                if (data['sta'] != false) {
                    for (var i in data['result']){
                        rid_ip += "<tr>";
                        rid_ip += "<td class='success'>"+ i +"</td>";
                        var d_list = "";
                        if (data['result'][i].length > 8){
                            for (var j = 0; j < data['result'][i].length; j++){
                                d_list += data['result'][i][j];
                                d_list += ",";
                                if((j+1)%8 == 0){
                                    d_list += "<br>"
                                }
                            }
                        }else{
                            d_list = data['result'][i]
                        }
                        rid_ip += "<td class='warning'>"+ d_list +"</td>";
                        rid_ip += "</tr>";
                    }
                }else{
                    rid_ip += "<tr>";
                    rid_ip += '<td colspan="2" class="text-center"><span class="label label-danger">无登陆ip数据</span></td>';
                    rid_ip += '</tr>';
                }
                var rid_ip_title = '';
                if (key_val == '0'){
                    rid_ip_title += "<tr>";
                    rid_ip_title += "<th class='success'> rid </th>";
                    rid_ip_title += "<th class='warning'> 对应ip </th>";
                    rid_ip_title += "</tr>";
                }
                else if (key_val == '1'){
                    rid_ip_title += "<tr>";
                    rid_ip_title += "<th class='success'> ip </th>";
                    rid_ip_title += "<th class='warning'> 对应rid </th>";
                    rid_ip_title += "</tr>";
                }
                $('#rid_ip_title').html(rid_ip_title);
                $('#rid_ip_body').html(rid_ip);
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

//data.sort(compare("buy_number"));
//function compare(propertyName) {
//    return function (object1, object2) {
//        var value1 = object1[propertyName];
//        var value2 = object2[propertyName];
//        if (value2 < value1) {
//            return -1;
//        }
//        else if (value2 > value1) {
//            return 1;
//        }
//        else {
//            return 0;
//        }
//    }
//}

// 神魂商店
$('#btn_limit_shop').on('click', function(e){
    e.preventDefault();
    var server_id = $("#select_gameserver").val();
    var limit_shop_start_date = $("#limit_shop_start_date").val();
    var limit_shop_end_date = $("#limit_shop_end_date").val();

    var LIMITJSON = DATA["mystery_shop"];
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/query_limit_shop',
            data: {
                server_id: server_id,
                start_date: limit_shop_start_date,
                end_date: limit_shop_end_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                if (data.length != 0) {
                    var $limit_shop = $("#limit_shop_list");
                    $limit_shop.empty();
                    var str_p = "";
                    if (limit_shop_start_date == limit_shop_end_date) {
                        for (var n = 0; n < data.length; n++) {
                            str_p += "<tr>";
                            var prop_id = data[n]["prop_id"];
                            str_p += "<td>" + prop_id + "</td>";
                            var good = LIMITJSON[prop_id]["good"];
                            var good_list = good.split(",");
                            str_p += "<td>";
                            str_p += "<span class=\"label label-" + QUALITY_CSS[quality_validation(good_list[0])] + "\">";
                            str_p += cid_validation(good_list[0]) + "</span></td>";
                            str_p += "<td>" + good_list[1].substring(0,good_list[1].length-1) + "</td>";
                            var consume = LIMITJSON[prop_id]["consume"];
                            var consume_list = consume.split(",");
                            str_p += "<td>" + consume_list[1].substring(0,consume_list[1].length-1) + "</td>";
                            str_p += "<td>" + data[n]["buy_number"] + "</td>";
                            str_p += "<td>" + data[n]["buy_person_number"] + "</td>";
                            str_p += "</tr>";
                        }
                    }
                    else {
                        for (var n in data) {
                            str_p += "<tr>";
                            str_p += "<td>" + n + "</td>";
                            var good = LIMITJSON[n]["good"];
                            var good_list = good.split(",");
                            str_p += "<td>";
                            str_p += "<span class=\"label label-" + QUALITY_CSS[quality_validation(good_list[0])] + "\">";
                            str_p += cid_validation(good_list[0]) + "</span></td>";
                            str_p += "<td>" + good_list[1].substring(0,good_list[1].length-1) + "</td>";
                            var consume = LIMITJSON[n]["consume"];
                            var consume_list = consume.split(",");
                            str_p += "<td>" + consume_list[1].substring(0,consume_list[1].length-1) + "</td>";
                            str_p += "<td>" + data[n]["buy_number"] + "</td>";
                            str_p += "<td>" + data[n]["buy_person_number"] + "</td>";
                            str_p += "</tr>";
                        }
                    }
                    $limit_shop.html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});

function quality_validation(cid) {
    if (11201 <= parseInt(cid) && parseInt(cid) <= 11701) {
        var general_id = DATA["general_fragment"][cid]["general"];
        var quality = DATA["general"][general_id]["quality"];
    }
    else if (20001 <= parseInt(cid) && parseInt(cid) <= 20273) {
        var quality = "2";
    }
    else {
        return "2";
    }
    return quality;
}

function cid_validation(cid) {
    //if (10101 <= parseInt(cid) && parseInt(cid) <= 10606) {
    //    var name = DATA["general"][cid]["name"];
    //}
    if (11201 <= parseInt(cid) && parseInt(cid) <= 11701) {
        var general_id = DATA["general_fragment"][cid]["general"];
        var name = DATA["general"][general_id]["name"] + "魂魄";
    }
    else if (20001 <= parseInt(cid) && parseInt(cid) <= 20273) {
        var name = DATA["props"][cid]["name"];
    }
    //else if (21101 <= parseInt(cid) && parseInt(cid) <= 26999) {
    //    var name = DATA["equip"][cid]["name"];
    //}
    //else if (27001 <= parseInt(cid) && parseInt(cid) <= 27048) {
    //    var name = DATA["equip_fragment"][cid]["name"];
    //}
    //else if(33001 <= parseInt(cid) && parseInt(cid) <= 33090) {
    //    var name = DATA["sigil"][cid]["name"];
    //}
    //else if (91001 <= parseInt(cid) && parseInt(cid) <= 91005) {
    //    var petid = DATA["pet3_fragment"][cid]["petid"];
    //    var name = DATA["pet3_attr"][petid][0]["name"] + "碎片";
    //}
    //else if (92001 <= parseInt(cid) && parseInt(cid) <= 92024) {
    //    var name = DATA["pet3_passiveskill"][cid]["name"];
    //}
    else {
        return cid;
    }
    return name;
}


// 世界BOSS
$("#btn_world_boss").on("click", function(e){
    e.preventDefault();
    var server_id = $("#select_gameserver").val();
    var boss_param = $("#boss_param").val();
    var world_boss_date = $("#world_boss_date").val();

    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/query_world_boss',
            data: {
                server_id: server_id,
                boss_param: boss_param,
                world_boss_date: world_boss_date
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                var world_boss_list = $("#world_boss_list");
                world_boss_list.empty();
                var str_p = "";
                if (data.length != 0) {
                    for (var p = 0; p < data.length; p++) {
                        str_p += "<tr>";
                        str_p += "<td>" + data[p]["rank"] + "</td>";
                        str_p += "<td>" + data[p]["role_name"] + "</td>";
                        str_p += "<td>" + data[p]["rid"] + "</td>";
                        str_p += "<td>" + data[p]["damage_num"] + "</td>";
                        str_p += "<td>" + data[p]["fire_num"] + "</td>";
                        str_p += "<td>" + data[p]["damage"] + "</td>";
                        str_p += "<td>" + data[p]["damage_percent"] + "</td>";
                        str_p += "</tr>";
                    }
                    world_boss_list.html(str_p);
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
    })
});