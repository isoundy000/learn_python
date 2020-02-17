/**
 * Created by liuzhaoyang on 15/9/7.
 */
getGameServerData($("#select_gameserver"), 1);

var server_id = 0;

var CONFIG = ["general","pet2_attr","pet2_fragment","equip","props","soul","copy","brave_copy","map"];
var GLOBAL_DATA = {};

var QUALITY_CSS = {
    2: "green",
    3: "blue",
    4: "purple",
    5: "yellow"
};
var GENERAL_QUALITY = {
    2:"绿色",
    3:"蓝色",
    4:"紫色",
    5:"橙色"
};


$("#select_gameserver").on("change", function(e){
    e.preventDefault();
    server_id = $(this).val();
});
$("#select_gameserver").change();

var init_data = function(){
//    var s_id = $('#select_gameserver').val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: "/queryjsondatabyserver",
        async: false,
        data: {
            server_id: server_id,
            type: JSON.stringify(CONFIG)
        },
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            GLOBAL_DATA = data;
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    });
};
setTimeout("init_data()", 2000);
//init_data();

var UserQueryData = function () {
    var form1 = $('#role_form');
    var rules = {
        role_search: {
            required: true,
            digits: true
        }
    };
    var messages = {
        role_search: {
            required: "请输入账号ID",
            digits: "请输入整数."
        }
    };
    var submitFunc = function () {
        var role_id = $("#role_id").val();
        var page_content = $('.page-content');
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/queryrole2',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                $("#a_role").parent("li").addClass("active");
                $("#tab_role").addClass("active");

                $("#a_role").parent("li").nextAll().each(function(){
                    if ($(this).hasClass("active")) {
                        $(this).removeClass("active");
                        var tab_name = $(this).children("a").attr("id");
                        $("#tab_" + tab_name + "_1").removeClass("active");
                    }
                });
                var str_info = "<tr>";
                if (data['status']) {
                    str_info += "<td>" + data["name"] + "</td>";
                    str_info += "<td>" + data["level"] + "</td>";
                    str_info += "<td>" + data["vip"] + "</td>";
                    str_info += "<td>" + data["recharge"] + "</td>";


                    str_info += "<td>" + data["gold"] + "</td>";
                    str_info += "<td>" + data["coin"] + "</td>";
                    str_info += "<td>" + data["channel_name"] + "</td>";
                    str_info += "<td>" + data["account"] + "</td>";
                    str_info += "</tr>"
                }
                else {
                    str_info += '<td colspan="8" class="text-center"><span class="label label-danger">无此角色编号数据</span></td>';
                    str_info += '</tr>';
                }
                $("#role_list").html(str_info);

            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        })
    };
    commonValidation(form1, rules, messages, submitFunc);
};
UserQueryData();


var validate_role = function(){
    var role_id = $("#role_id").val();
    var tag = true;
    if (role_id == "" || role_id == null || role_id == undefined)
        tag = false;
    return tag;
};


//主角
$('#role_1').bind("click",function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if (v_str) {
        $("#role_1").attr("href", "#tab_role_1");
        var GENERAL_JSON = GLOBAL_DATA["general"];
        var PET_JSON = GLOBAL_DATA["pet2_attr"];
        var PET_FRAGMENT_JSON = GLOBAL_DATA["pet2_fragment"];

        $.ajax({
            type: 'get',
            url: '/queryLead',
            data: {server_id: server_id, role_id: role_id},
            dataType: 'JSON',
            success: function (data) {
                var str_g = "";
                var str_p = "";
                var str_pf = "";
                if (data.length != 0) {

                    var cid = data['cid'];
                    var quality = GENERAL_JSON[cid]["quality"];
                    str_g += "<tr>";
                    str_g += "<td>";
                    str_g += "<span class=\"btn default btn-xs " + QUALITY_CSS[quality] + "\">";

                    var name = '';
                    if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'shou') {
                        name = '魔王'
                    } else if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'nan') {
                        name = '男主'
                    } else if (GENERAL_JSON[cid]["icon"].slice(0, -1) == 'nv') {
                        name = '女主'
                    }
                    str_g += name + "</span></td>";
                    str_g += "<td>" + GENERAL_QUALITY[quality] + "</td>";
                    str_g += "</tr>";

                    var pet = data['pet'];
                    for (var p in pet){
                        var pet_rank = pet[p]['level2'];
                        var pet_cid = pet[p]['cid'];
                        str_p += "<tr>";
                        str_p += "<td>" + PET_JSON[pet_cid][pet_rank]['name'] + "</td>";
                        str_p += "<td>" + pet[p]['level1'] + "</td>";
                        str_p += "<td>" + pet[p]['level2'] + "</td>";
                        str_p += "</tr>";
                    }

                    var pet_fragment = data['pet_fragment'];
                    for (var pf in pet_fragment){
                        var pet_fragment_cid = PET_FRAGMENT_JSON[pet_fragment[pf]['cid']]['petid'];
                        str_pf += "<tr>";
                        str_pf += "<td>" + PET_JSON[pet_fragment_cid][0]['name'] + "</td>";
                        str_pf += "<td>" + pet_fragment[pf]['num'] + "</td>";
                        str_pf += "</tr>";
                    }
                }
                $('#role2_list').html(str_g);
                $('#devil_list').html(str_p);
                $('#devil_fragment_list').html(str_pf);
            },
            error: function () {
            }
        })
    } else {
        $("#role_1").attr("href", "#");
    }
});

//武将
$('#general').bind("click",function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            $("#general").attr("href", "#tab_general_1");
            var GENERAL_JSON = GLOBAL_DATA["general"];
            var EQUIP_JSON = GLOBAL_DATA["equip"];
            $.ajax({
                    type: 'get',
                    url: '/querygeneral2',
                    data: {server_id: server_id, role_id: role_id},
                    dataType: 'JSON',
                    success: function (data) {
                        var str_g = "";
                        var general_arr = {};
                        if (data.length != 0) {
                            for (var general in data){
                                var g_data = data[general];
                                var cid = g_data['cid'];
                                var quality = GENERAL_JSON[cid]["quality"];
                                str_g += "<tr>";

                                // 名称
                                str_g += "<td>";
                                str_g += "<span class=\"btn default btn-xs " + QUALITY_CSS[quality] + "\">";
                                general_arr[g_data['id']] = {
                                    "name": GENERAL_JSON[cid]["name"],
                                    "quality": QUALITY_CSS[quality]
                                };
                                str_g += GENERAL_JSON[cid]["name"] + "</span></td>";

                                //位置
                                var addr = '';
                                if (g_data['addr'] == 2){
                                    addr = '上阵'
                                }else if (g_data['addr'] == 1){
                                    addr = '助阵'
                                }
                                str_g += "<td>" + addr + "</td>";

                                //等级
                                str_g += "<td>" + g_data['level1'] + "</td>";

                                //碎片数量
                                if(GENERAL_JSON[cid]["name"]=='主角'){
                                    str_g += "<td>" + 0 + "</td>";
                                }else{
                                    str_g += "<td>" + g_data['num'] + "</td>";
                                }

                                //装备
                                var weapon = '';
                                var armor = '';
                                var accessory = '';
                                var head = '';
                                var treasure = '';
                                var horse = '';

                                if(g_data["weapon"]!=null){
                                    weapon = EQUIP_JSON[g_data["weapon"]]['name']
                                }
                                if(g_data["armor"]!=null){
                                    armor = EQUIP_JSON[g_data["armor"]]['name']
                                }
                                if(g_data["accessory"]!=null){
                                    accessory = EQUIP_JSON[g_data["accessory"]]['name']
                                }
                                if(g_data["head"]!=null){
                                    head = EQUIP_JSON[g_data["head"]]['name']
                                }
                                if(g_data["treasure"]!=null){
                                    treasure = EQUIP_JSON[g_data["treasure"]]['name']
                                }
                                if(g_data["horse"]!=null){
                                    horse = EQUIP_JSON[g_data["horse"]]['name']
                                }
                                str_g += "<td>" + weapon + "</td>";
                                str_g += "<td>" + armor + "</td>";
                                str_g += "<td>" + accessory + "</td>";
                                str_g += "<td>" + head + "</td>";
                                str_g += "<td>" + treasure + "</td>";
                                str_g += "<td>" + horse + "</td>";
                                str_g += "</tr>";
                            }
                            $('#generals_list').html(str_g);
                        }

                    },
                    error : function () {
                    }
            })
        }else{
            $("#general").attr("href", "#");
        }
});

//装备
$('#equip').bind('click', function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str) {
            $("#equip").attr("href", "#tab_equip_1");
            var EQUIP_JSON = GLOBAL_DATA["equip"];
            $.ajax({
                type: 'get',
                url: '/queryequip2',
                data: {server_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    var str_e = "";
                    if (data.length != 0) {
                        for (var e = 0; e < data.length; e++) {
                            str_e += "<tr>";
                            str_e += "<td>";
                            var quality = EQUIP_JSON[data[e].cid]["quality"];
                            str_e += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                            str_e += EQUIP_JSON[data[e].cid]["name"] + "</span></td>";
                            str_e += "<td>" + data[e]["level1"] + "</td>";
                            str_e += "<td>" + data[e]["level2"] + "</td>";
                            str_e += "<td>" + data[e]["exp2"] + "</td>";
                            str_e += "</tr>";
                        }
                        $("#equip_list").html(str_e);
                    }
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            });
        }else{
            $("#equip").attr("href", "#");
        }
});

//道具
$("#props").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            $("#props").attr("href", "#tab_props_1");
            var PROPS_JSON = GLOBAL_DATA["props"];
            $.ajax({
                type: 'get',
                url: '/queryprops2',
                data: {server_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    if (data.length != 0) {
                        var str_p = "";
                        for (var p = 0; p < data.length; p++) {
                            console.log(data[p].num);
                            if (data[p].num != 0){
                                str_p += "<tr>";
                                str_p += "<td>";
                                str_p += PROPS_JSON[data[p].cid]["name"] + "</td>";
                                str_p += "<td>" + data[p].num + "</td>";
                                str_p += "</tr>";
                            }

                        }
                        $("#props_list").html(str_p);
                    }
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            });
        }else{
            $("#props").attr("href", "#");
        }
});

//命格
$("#soul").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            $("#soul").attr("href", "#tab_soul_1");
            var SOUL_JSON = GLOBAL_DATA["soul"];
            $.ajax({
                type: 'get',
                url: '/querysoul2',
                data: {server_id: server_id, role_id: role_id},
                dataType: 'JSON',
                success: function (data) {
                    if (data.length != 0) {
                        var str_s = "";
                        data = data.sort(function (x,y) {
                            return x.general_cid - y.general_cid
                        });
                        for (var s = 0; s < data.length; s++) {
                            str_s += "<tr>";
                            str_s += "<td>";
                            var quality = SOUL_JSON[data[s].cid]["quality"];
                            str_s += "<span class='btn btn-xs " + QUALITY_CSS[quality] + "'>";
                            str_s += SOUL_JSON[data[s].cid]["name"] + "</span></td>";
                            str_s += "<td>" + data[s]["level"] + "</td>";
                            str_s += "<td>" + data[s]["exp"] + "</td>";
                            str_s += "</tr>";
                        }
                        $("#soul_list").html(str_s);
                    }
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            });
        }else{
            $("#soul").attr("href", "#");
        }
});

//副本
$("#copy").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            $("#copy").attr("href", "#tab_copy_1");
            query_copy(role_id, 1, $("#copy_list"));
        }else{
            $("#copy").attr("href", "#");
        }
});

//精英副本
$("#bravecopy").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    var role_id = $("#role_id").val();
    if(v_str){
            $("#bravecopy").attr("href", "#tab_brave_copy_1");
            query_copy(role_id, 2, $("#bravecopy_list"));
        }else{
            $("#bravecopy").attr("href", "#");
        }

});

var query_copy = function(role_id, tag, div){
    $.ajax({
        type: 'get',
        url: '/querycopyinfo',
        data: {game_id: server_id, role_id: role_id, tag: tag},
        dataType: 'JSON',
        success: function (data) {
            var str_info = "";
            var copy = null;
            if (tag == 1)
                copy = GLOBAL_DATA["copy"];
            else
                copy = GLOBAL_DATA["brave_copy"];

            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                str_info += "<td>" + GLOBAL_DATA["map"][data[i]["map"]]["name"] + "</td>";

                str_info += "<td>" + copy[data[i]["map"]][data[i]["point"]]["name"] + "</td>";
                var star = data[i]["star"];
                str_info += "<td>" ;
                for(var j = 0; j < star; j++){
                    str_info += "<i class='fa fa-star'></i>";
                }
                for(var k=3; k > star; k--){
                    str_info += "<i class='fa fa-star-o'></i>";
                }
                str_info += "</td>";
                str_info += "</tr>";
            }
            div.html(str_info);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    });
};

//战斗力
var POWER_TYPE = {
    "equip": "装备",
    "general": "武将",
    "pet": "魔宠",
    "soul": "命格",
    "treasure": "宝物"
};

$("#power").bind("click", function(e){
    e.preventDefault();
    var v_str = validate_role();
    if (v_str) {
            $("#power").attr("href", "#tab_power_1");
            var role_id = $("#role_id").val();
            var page_content = $('.page-content');
            App.blockUI(page_content, false);
            $.ajax({
                    type: 'get',
                    url: '/getrolepower',
                    data: {server_id: server_id, role_id: role_id},
                    dataType: 'JSON',
                    success: function (data) {
                        App.unblockUI(page_content);
                        var str_info = "";
                        var data_set = [];
                        for (var p in POWER_TYPE) {
                            str_info += "<tr>";
                            str_info += "<td>" + POWER_TYPE[p] + "</td>";
                            str_info += "<td>" + data[p] + "</td>";
                            str_info += "</tr>";
                            var temp = {
                                label: POWER_TYPE[p],
                                data: data[p] / data["total"] * 100
                            };
                            data_set.push(temp);
                        }
                        str_info += "<tr class=\"success\">";
                        str_info += "<td>总战力</td>";
                        str_info += "<td>" + data["total"] + "</td>";
                        str_info += "</tr>";

                        drawPieChart($("#chart_power"), data_set);
                        $("#power_list").html(str_info);
                    },
                    error: function (XMLHttpRequest) {
                        App.unblockUI(page_content);
                        error_func(XMLHttpRequest);
                    }
                }
            )
        }else{
            $("#power").attr("href", "#");
        }
});