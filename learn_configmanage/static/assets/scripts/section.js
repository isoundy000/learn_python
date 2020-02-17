/**
 * Created by wangrui on 14-10-14.
 */


create_del_modal($("#section_del_modal"), "是否删除分区？", "confirm_del_section");
var choose_div = $("#choose_div").html();
var SECTION_DATA = {};

var getSection = function () {
    var success = function(data){
        var str_info = "<tr>";
        var str_s = "";
        var str_t = "";
        if (data.length != 0) {
            for (var i in data) {
                SECTION_DATA[data[i]["id"]] = data[i]["name"];
                str_info += "<td>" + [data[i]["id"]] + "</td>";
                str_info += "<td>" + data[i]["name"] + "</td>";
                str_info += "<td>" + data[i]["desc"] + "</td>";
                str_info += "<td>";
                str_info += '&nbsp; <a onclick="mod_section(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                str_info += '&nbsp; <a onclick="del_section(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                str_info += '&nbsp; <a onclick="download_section(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs purple">下载zip<i class="fa fa-download"></i></a>';
                str_info += "</td>";
                str_info += "</tr>";
                str_s += '<option value="' + data[i]["id"] + '">' + data[i]["name"] + '</option>';
                str_t += "<label class=\"checkbox-inline\"><input name=\"check_s\" type=\"checkbox\" value=\""
                    + data[i]["id"] + "\">" + data[i]["name"] + "</label>";
            }
//                $("#section_select").html(str_s);
            $("#source_section").html(str_s);
            $("#target_section").html(str_s);
            $("#section_check").html(str_t);
            $("#select_section_move").html(str_s);
        }
        else {
            str_info += '<td colspan="4" class="text-center"><span class="label label-danger">无数据</span></td>';
            str_info += '</tr>';
        }
        $('#sections_list').html(str_info);
    };

    my_ajax(true, "/querysection", 'get', {}, true, success);
};
getSection();

var sectionValidation = function () {
    var form1 = $('#section_form');
    var rules = {
        section_name: {
            required: true
        }
    };
    var messages = {
        section_name: {
            required: "请输入分区名."
        }
    };
    var submitFunc = function () {
        var section_id = $("#hid_section").val();
        var section_name = $('#section_name').val();
        var section_desc = $('#section_content').val();
        $.ajax({
                type: 'get',
                url: '/operatesection',
                data: {section_id: section_id, section_name: section_name, section_desc: section_desc},
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == 0) {
                        alert("添加分区失败.");
                    }
                    else if (data["status"] == 2) {
                        alert("分区名称重复,请重新输入。");
                    }
                    else {
                        $("#section_modal").modal("hide");
                        getSection();
                    }
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunc);
};
sectionValidation();

$("#section_server").on("click", function (e) {
    e.preventDefault();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/getsectionserver',
        data: {},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            var str_info = "";
            if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                    str_info += "<tr>";

                    str_info += "<td>" + data[i]["id"] + "区:" + data[i]["name"] + "</td>";
                    str_info += '<td><span class="badge badge-info">' + SECTION_DATA[data[i]["configsection"]] + "</span></td>";
                    str_info += "<td>";
                    str_info += '&nbsp; <a onclick="mod_sg(' + data[i]["id"] + "," + data[i]["configsection"] + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                    str_info += "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="4" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#section_server_list").html(str_info);
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


$("#btn_confirm").on("click", function (e) {
    e.preventDefault();
    var hid_section_server = $("#hid_section_server").val();
    var section_select = $("#section_select").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/updatesectionserver',
        data: {hid_section_server: hid_section_server, section_select: section_select},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            if (data["status"] == 0) {
                Common.alert_message($("#error_modal"), 0, "修改失败.");
            }
            $("#section_server_modal").modal("hide");
            $("#section_server").click();
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


//添加分区事件
$("#add_section").click(function (e) {
    e.preventDefault();
    $("#hid_section").val("");
    $('#section_name').val("");
    $('#section_content').val("");
    $("#section_modal").modal("show");
});

//修改分区
var mod_section = function (section_id) {
    $.ajax({
        type: 'get',
        url: '/queryonesection',
        data: {section_id: section_id},
        dataType: 'JSON',
        success: function (data) {
            $("#hid_section").val(data["id"]);
            $('#section_name').val(data["name"]);
            $('#section_content').val(data["desc"]);
            $("#section_modal").modal("show");
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

//删除section 层弹出
var del_section = function (section_id) {
    $('#section_del_modal').modal("show");
    $("#confirm_del_section").attr('onclick', 'fun_del_section(' + section_id + ');');
};

//删除section确认
var fun_del_section = function (section_id) {
    $.ajax({
        type: 'get',
        url: '/deletesection',
        data: {section_id: section_id},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 2) {
                alert("删除分区配置失败.");
            }
            $('#section_del_modal').modal("hide");
            getSection();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

var mod_sg = function (id, section) {
    $("#hid_section_server").val(id);
    $("#section_select").val(section);
    $("#section_server_modal").modal("show");
};

$("#confirm_section_copy").on("click", function (e) {
    e.preventDefault();
    var source_section = $("#source_section").val();
    var target_section = $("#target_section").val();
    if (source_section == target_section) {
        Common.alert_message($("#error_modal"), false, "两个分区不能相同.");
        return;
    }
    var page_content = $('.page-content');
    App.blockUI(page_content, false);

    $.ajax({
        type: 'get',
        url: '/sectioncopy',
        data: {source_section: source_section, target_section: target_section},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);
            if (data["status"] == "success") {
                Common.alert_message($("#error_modal"), true, "复制成功.");
            }
            else {
                Common.alert_message($("#error_modal"), true, "复制失败.");
            }
        },
        error: function (XMLHttpRequest) {
            App.unblockUI(page_content);
            error_func(XMLHttpRequest);
        }
    })
});


var download_section = function (id) {
    var winRef = window.open("", "_blank");
    var success = function (data) {
        function loc() {
            var url_d = "../../static/" + data["url"];
            console.log(url_d);
            winRef.location = url_d;
        }
        setTimeout(loc(), 100);
    };
    var data = {
        section_id: id
    };
    my_ajax(true, "/section/downloadzip", 'get', data, true, success);
};


var get_section_log_details_info = function(log_id, tag){
    var success = function(data){
        var str_info = "";
        if (tag == 1){
            $("#th_all_check").show();   
            $("#btn_confirm_move").show();
        }
        else{
            $("#th_all_check").hide();
            $("#btn_confirm_move").hide();
        }
        if(data.length != 0){
            for (var i = 0; i < data.length; i++) {
                str_info += "<tr>";
                if (tag == 1) {
                    str_info += "<td>" + "<div class='checkbox-list'>";
                    str_info += "<label> <input type=\"checkbox\" name=\"check_type\" value=\"" +
                        data[i]["id"] + "\">" + "</label></div></td>";
                }
                str_info += "<td>" + data[i]["type"] + "</td>";
                var opt = data[i]["opt"];
                if (opt == "add") {
                    str_info += "<td><span class='badge badge-success'>添加</span></td>";
                }
                else {
                    str_info += "<td><span class='badge badge-warning'>修改</span></td>";
                }

                str_info += "</tr>";
            }
        }
        else{
            str_info += "</tr>";
            str_info += '<tr>';
            str_info += '<td colspan="3" class="text-center"><span class="label label-success">分区数据相同.</span></td>';
            str_info += '</tr>';
        }

        $("#diff_sections_list").html(str_info);
        $("#change_modal").modal("show");
    };
    var data = {
        "sid": log_id
    };
    my_ajax(true, "/section/getsectionlogdetails", 'get', data, true, success);
};

function check_type(){
    var str_game = "";
    var str_list = [];

    $("input[name='check_type']").each(function(e){
        str_game += $(this).val() + ",";
        if($(this).is(":checked")){
            str_list.push($(this).val());
        }
    });
    if(str_list.length == 0){
        show_error_modal(0, "请选择类型.");
        return false;
    }
    return true;
}


$("#all_check").on("change", function (e) {
    e.preventDefault();
    var $check_type = $("input[name='check_type']");

    if ($(this).is(":checked")) {
        $check_type.prop("checked", true);
        $check_type.parent("span").addClass("checked");
    }
    else{
        $check_type.prop("checked", false);
        $check_type.parent("span").removeClass("checked");
    }
});

function upload_zip_file(){
    $.ajaxFileUpload(
        {
            url: "/section/uploadzip",
            secureuri: false,
            type: "post",
            fileElementId: 'zip_file',
            data: {
                section: $("#select_section_move").val()
            },
            dataType: 'json',
            success: function (data, status){
                
                if (data["status"] == "success") {
                    $("#choose_div").empty();
                    $("#choose_div").html(choose_div);
                    var log_id = data["data"];
                    get_section_log_details_info(log_id, 1);
                }
                else{
                    Common.alert_message($("#error_modal"), 0, "上传文件失败,请重新上传");
                }
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    );
}

$("#btn_upload").on("click", function (e) {
    e.preventDefault();
    upload_zip_file();
});

$("#btn_confirm_move").on("click", function (e) {
    e.preventDefault();
    if (check_type()){
        var success = function(data){
            if (data["status"] == "success"){
                $("#change_modal").modal("hide");
                Common.alert_message($("#error_modal"), 1, "迁移成功.");
            }
            else{
                Common.alert_message($("#error_modal"), 0, "迁移失败.");
            }
        };
        var type_list = [];
        $("input[name='check_type']").each(function(e){
            if ($(this).is(":checked")){
                type_list.push($(this).val());
            }
        });
        var data = {
            type_list: JSON.stringify(type_list)
        };
        my_ajax(true, "/section/confirmmove", 'post', data, true, success);
        $("#change_modal").modal("hide");
    }
});


function get_section_log(){
    var sAjaxSource = "/section/sectionlog";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "section",
            'sClass': 'center',
            "sTitle": "分区"
        },
        {
            "mDataProp": "type",
            'sClass': 'center',
            "sTitle": "类型"
        },
        {
            "mDataProp": "user",
            'sClass': 'center',
            "sTitle": "上传者"
        },
        {
            "mDataProp": "opt_time",
            'sClass': 'center',
            "sTitle": "时间"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": ""
        }
    ];

    var fnRowCallback = function (nRow, aData, iDisplayIndex) {
        var str_html1 = '';
        if (aData.type == "move"){
            str_html1 += "<span class='badge badge-success'>迁移</span>";
        }
        else{
            str_html1 += "<span class='badge badge-success'>复制</span>";
        }
        $('td:eq(1)', nRow).html(str_html1);
        
        var str_html3 = "";
        str_html3 += "<button onclick=\"query_section_log(this)\" class=\"btn default btn-xs dark\">查看</button>";
        $('td:eq(4)', nRow).html(str_html3);
        return nRow;
    };

    dataTablePage($("#section_log_table"), aoColumns, sAjaxSource, {}, false, fnRowCallback);
}

var query_section_log = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#section_log_table").dataTable().fnGetData(nRoW);
    get_section_log_details_info(data["id"], 2);
};

$("#section_log").on("click", function(e){
    e.preventDefault();
    get_section_log();
}); 


