/**
 * Created by liuzhaoyang on 15/8/28.
 */

create_del_modal($("#system_del_modal"), "是否删除此系统及系统下的所有子系统?", "del_system_btn");
create_del_modal($("#subsystem_del_modal"), "是否删除此子系统及子系统下得所有子目录?", "subsystem_func_btn");
create_del_modal($("#subdirectory_del_modal"), "是否删除此子目录及子目录下所有标签?", "subdirectory_func_btn");
create_del_modal($("#subtab_del_modal"), "是否删除此子标签?", "subtab_func_btn");
getGameServerData($("#subdirectory_server"), 1);

//添加
$("#add_system").on("click", function () {
    $("#system_id").val("");
    $("#system_name").val("");
    $("#system_desc").val("");
    $("#system_modal").modal("show");
});

var systemValidate = function () {
    var form1 = $('#system_form');
    var rules = {
        system_name: {
            required: true
        }
    };
    var messages = {
        system_name: {
            required: "请输入参数名."
        }
    };
    var submitFunc = function () {
        var system_id = $("#system_id").val();
        var system_name = $('#system_name').val();
        var system_desc = $("#system_desc").val();
        $.ajax({
                type: 'get',
                url: '/operatesystem',
                data: {
                    system_id: system_id,
                    system_name: system_name,
                    system_desc: system_desc
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#system_modal").modal("hide");
                    get_system_data();
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitFunc);
};
systemValidate();

//显示系统详情
var get_system_data = function () {
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
        type: 'get',
        url: '/querysystem',
        data: {},
        dataType: 'JSON',
        success: function (data) {
            App.unblockUI(page_content);

            var str_info = "";
            if (data.length != 0) {
                for (var i = 0; i < data.length; i++) {
                    str_info += "<tr>";
                    str_info += "<td>" + data[i]["name"] + "</td>";
                    str_info += "<td>" + data[i]["desc"] + "</td>";
                    str_info += "<td>";
                    str_info += '&nbsp; <a onclick="set_system(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs blue" data-toggle="modal">配置 <i class="fa fa-gear"></i></a>';
                    str_info += '&nbsp; <a onclick="mod_system(this,' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs yellow" data-toggle="modal">修改 <i class="fa fa-edit"></i></a>';
                    str_info += '&nbsp; <a onclick="del_system(' + "'" + data[i]["id"] + "'" + ')"' + 'class="btn default btn-xs red" data-toggle="modal">删除 <i class="fa fa-trash-o"></i></a>';
                    str_info += "</td>";
                    str_info += "</tr>";
                }
            }
            else {
                str_info += "<tr>";
                str_info += '<td colspan="3" class="text-center"><span class="label label-danger">无数据</span></td>';
                str_info += '</tr>';
            }
            $("#system_list1").html(str_info);
        },
        error: function () {
            App.unblockUI(page_content);
        }
    })
};
get_system_data();

//删除
var del_system = function (id) {
    $('#system_del_modal').modal("show");
    $("#del_system_btn").attr('onclick', 'fun_del_system(' + id + ');');
};

var fun_del_system = function (id) {
    $.ajax({
        type: 'get',
        url: '/deletesystem',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#system_del_modal').modal("hide");
            get_system_data();
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

//修改
var mod_system = function (div, sid) {
    var name = $(div).parents('tr').children('td').eq(0).html();
    var desc_ = $(div).parents('tr').children('td').eq(1).html();
    $("#system_id").val(sid);
    $("#system_name").val(name);
    $("#system_desc").val(desc_);
    $("#system_modal").modal("show");
};

//配置
var set_system = function (id) {
    $("#system_set_id").val(id);
    query_subsystem(id);
    $("#system_set_modal").modal("show");
};

var query_subsystem = function (id) {

    var ajax_source = "/querysubsystem";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "子系统名称"
        },
        {
            "mDataProp": "desc",
            "sClass": "center",
            "sTitle": "描述"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"set_subsystem(this)\" class=\"btn default btn-xs blue\" data-toggle=\"modal\">配置 <i class=\"fa fa-gear\"></i></button>" + "<button onclick=\"mod_subsystem(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_subsystem(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        system_id: id
    };
    dataTablePage($("#subsystem_list"), aoColumns, ajax_source, data, false);
};

//添加子系统
$("#add_subsystem").on("click", function (e) {
    e.preventDefault();
    $("#subsystem_id").val("");
    $("#subsystem_name").val("");
    $("#subsystem_desc").val("");
    $("#subsystem_modal").modal("show");
});

$("#btn_subsystem").on("click", function (e) {
    e.preventDefault();
    var subsystem_id = $("#subsystem_id").val();
    var system_set_id = $("#system_set_id").val();
    var subsystem_name = $("#subsystem_name").val();
    var subsystem_desc = $("#subsystem_desc").val();
    if (subsystem_name != "") {
        $.ajax({
            type: 'get',
            url: '/operatesubsystem',
            data: {
                subsystem_id: subsystem_id,
                system_set_id: system_set_id,
                subsystem_name: subsystem_name,
                subsystem_desc: subsystem_desc
            },
            dataType: 'JSON',
            success: function (data) {
                if (data["status"] == "fail") {
                    Common.alert_message($("#error_modal"), 0, "操作失败");
                }
                $("#subsystem_modal").modal("hide");
                query_subsystem(system_set_id);
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        });
    }
    else {
        $(".alert-danger span").html("子系统名称不能为空");
        $('.alert-danger', $('.form-body')).show();
    }
});


//修改子系统
var mod_subsystem = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subsystem_list").dataTable().fnGetData(nRoW);
    $("#subsystem_id").val(data["id"]);
    $("#subsystem_name").val(data["name"]);
    $("#subsystem_desc").val(data["desc"]);
    $("#subsystem_modal").modal("show");
};

//删除子系统
var del_subsystem = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subsystem_list").dataTable().fnGetData(nRoW);
    $('#subsystem_del_modal').modal("show");
    $("#subsystem_func_btn").attr('onclick', 'fun_del_subsystem(' + data["id"] + ');');
};

var fun_del_subsystem = function (id) {
    var system_set_id = $("#system_set_id").val();
    $.ajax({
        type: 'get',
        url: '/deletesubsystem',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#subsystem_del_modal').modal("hide");
            query_subsystem(system_set_id);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

//子系统设置
var set_subsystem = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subsystem_list").dataTable().fnGetData(nRoW);
    var id = data["id"];
    $("#subsystem_set_id").val(id);
    query_subdirectory(id);
    $("#subsystem_set_modal").modal("show");
};

var query_subdirectory = function (id) {

    var ajax_source = "/querysubdirectory";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "子目录名称"
        },
        {
            "mDataProp": "desc",
            "sClass": "center",
            "sTitle": "描述"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"set_subdirectory(this)\" class=\"btn default btn-xs blue\" data-toggle=\"modal\">配置 <i class=\"fa fa-gear\"></i></button>" + "<button onclick=\"mod_subdirectory(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_subdirectory(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        subsystem_id: id
    };
    dataTablePage($("#subdirectory_list"), aoColumns, ajax_source, data, false);
};

//添加子目录
$("#add_subdirectory").on("click", function (e) {
    e.preventDefault();
    $("#subdirectory_id").val("");
    $("#subdirectory_name").val("");
    $("#subdirectory_desc").val("");
    $("#subdirectory_modal").modal("show");
});

$("#btn_subdirectory").on("click", function (e) {
    e.preventDefault();
    var subdirectory = $('#subdirectory_server');
    var subdirectory_id = $("#subdirectory_id").val();
    var subsystem_set_id = $("#subsystem_set_id").val();
    var subdirectory_name = $("#subdirectory_name").val();
    var subdirectory_server_text = subdirectory.find("option:selected").text();
    var subdirectory_server_val = subdirectory.val();
    var subdirectory_desc = $("#subdirectory_desc").val();

    var name = "";
    var status = 1;
    console.log(subdirectory_name);
    if (subdirectory_name == "" && subdirectory_server_val == 0) {
        $(".alert-danger span").html("子目录名称和服务器不能都为空");
        $('.alert-danger', $('.form-body')).show();
        status = 0
    }
    else if (subdirectory_name == "" && subdirectory_server_val != 0) {
        name = subdirectory_server_text;
    }
    else if (subdirectory_name != "" && subdirectory_server_val == 0) {
        name = subdirectory_name;
    }
    else {
        $(".alert-danger span").html("子目录名称和服务器只填一个");
        $('.alert-danger', $('.form-body')).show();
        status = 0
    }


    if (status == 1) {
        $.ajax({
                type: 'get',
                url: '/operatesubdirectory',
                data: {
                    subdirectory_id: subdirectory_id,
                    subsystem_set_id: subsystem_set_id,
                    subdirectory_name: name,
                    subdirectory_desc: subdirectory_desc
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#subdirectory_modal").modal("hide");
                    query_subdirectory(subsystem_set_id);
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        );
    }
});

//修改子目录
var mod_subdirectory = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subdirectory_list").dataTable().fnGetData(nRoW);
    $("#subdirectory_id").val(data["id"]);
    $("#subdirectory_name").val(data["name"]);
    $("#subdirectory_desc").val(data["desc"]);
    $("#subdirectory_modal").modal("show");
};

//删除子目录
var del_subdirectory = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subdirectory_list").dataTable().fnGetData(nRoW);
    $('#subdirectory_del_modal').modal("show");
    $("#subdirectory_func_btn").attr('onclick', 'fun_del_subdirectory(' + data["id"] + ');');

};

var fun_del_subdirectory = function (id) {
    var subsystem_set_id = $("#subsystem_set_id").val();
    $.ajax({
        type: 'get',
        url: '/deletesubdirectory',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#subdirectory_del_modal').modal("hide");
            query_subdirectory(subsystem_set_id);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};

//子目录设置
var set_subdirectory = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subdirectory_list").dataTable().fnGetData(nRoW);
    console.log(data);
    var id = data["id"];
    $("#subdirectory_set_id").val(id);
    query_subtab(id);
    $("#subdirectory_set_modal").modal("show");
};

var query_subtab = function (id) {

    var ajax_source = "/querysubtab";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "子标签名称"
        },
        {
            "mDataProp": "desc",
            "sClass": "center",
            "sTitle": "描述"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_subtab(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_subtab(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        subdirectory_id: id
    };
    dataTablePage($("#subtab_list"), aoColumns, ajax_source, data, false);
};

//添加子标签
$("#add_subtab").on("click", function (e) {
    e.preventDefault();
    $("#subtab_id").val("");
    $("#subtab_name").val("");
    $("#subtab_desc").val("");
    $("#subtab_modal").modal("show");
});

$("#btn_subtab").on("click", function (e) {
    e.preventDefault();
    var subtab_id = $("#subtab_id").val();
    var system_set_id = $("#system_set_id").val();
    var subsystem_set_id = $("#subsystem_set_id").val();
    var subdirectory_set_id = $("#subdirectory_set_id").val();
    var subtab_name = $("#subtab_name").val();
    var subtab_desc = $("#subtab_desc").val();
    if (subtab_name != "") {
        $.ajax({
                type: 'get',
                url: '/operatesubab',
                data: {
                    subtab_id: subtab_id,
                    system_set_id: system_set_id,
                    subsystem_set_id: subsystem_set_id,
                    subdirectory_set_id: subdirectory_set_id,
                    subtab_name: subtab_name,
                    subtab_desc: subtab_desc
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == "fail") {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#subtab_modal").modal("hide");
                    query_subtab(subdirectory_set_id);
                },
                error: function (XMLHttpRequest) {
                    error_func(XMLHttpRequest);
                }
            }
        );
    }

    else {
        $(".alert-danger span").html("子标签名称不能为空");
        $('.alert-danger', $('.form-body')).show();
    }
});

//修改子标签
var mod_subtab = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subtab_list").dataTable().fnGetData(nRoW);
    $("#subtab_id").val(data["id"]);
    $("#subtab_name").val(data["name"]);
    $("#subtab_desc").val(data["desc"]);
    $("#subtab_modal").modal("show");
};

//删除子标签
var del_subtab = function (btn) {
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#subtab_list").dataTable().fnGetData(nRoW);
    $('#subtab_del_modal').modal("show");
    $("#subtab_func_btn").attr('onclick', 'fun_del_subtab(' + data["id"] + ');');

};

var fun_del_subtab = function (id) {
    var subdirectory_set_id = $("#subdirectory_set_id").val();
    $.ajax({
        type: 'get',
        url: '/deletesubtab',
        data: {id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data["status"] == "fail") {
                Common.alert_message($("#error_modal"), 0, "删除失败.")
            }
            $('#subtab_del_modal').modal("hide");
            query_subtab(subdirectory_set_id);
        },
        error: function (XMLHttpRequest) {
            error_func(XMLHttpRequest);
        }
    })
};
