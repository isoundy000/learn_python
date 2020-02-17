/**
 * Created by wangrui on 15/6/25.
 */


create_del_modal($("#del_modal"), "是否删除此配置信息?", "confirm_btn_del");
handleDatePickers();
$("#start_date").val(getNowFormatDate(0));
$("#end_date").val(getNowFormatDate(0));

$("#select_type").on("change", function(e){
    e.preventDefault();
    var select_type = $("#select_type").val();
    var ajax_source = "/getexcelsetpage";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "sheet_name",
            'sClass': 'center',
            "sTitle": "工作表"
        },
        {
            "mDataProp": "ctype",
            'sClass': 'center',
            "sTitle": "名称"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button>" +
                "<button onclick=\"del_excel(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        select_type: select_type
    };
    dataTablePage($("#table_excel"), aoColumns, ajax_source, data, false);

    $.ajax({
            type: 'get',
            url: '/querysection',
            dataType: 'JSON',
            success: function (data) {
                if (data.length != 0) {
                    var str_info = "";
                    for (var i = 0; i < data.length; i++) {
                        str_info += "<option value='" + data[i].id + "'>" + data[i].name + "</option>";
                    }
                    $("#select_section").html(str_info);
                }
            },
            error: function () {
                error_func();
            }
        }
    );
});

$("#select_type").change();

var mod = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_excel").dataTable().fnGetData(nRoW);
    $("#excel_id").val(data["id"]);
    $("#sheet_name").val(data["sheet_name"]);
    $("#ctype").val(data["ctype"]);
    $("#add_modal").modal("show");
};

var del_excel = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#table_excel").dataTable().fnGetData(nRoW);
    $('#del_modal').modal("show");
    $("#confirm_btn_del").attr('onclick', "confirm_del_excel(" + data["id"] + ")");
};

var confirm_del_excel = function(id){
    $.ajax({
        type: 'get',
        url: '/deleteexcel',
        data: {excel_id: id},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 0) {
                Common.alert_message($("#error_modal"), 0, "删除失败");
            }
            $('#del_modal').modal("hide");
            $("#a_fight").click();
        },
        error: function () {
        }
    })
};

var file_upload = function(tag, file_id, div_modal){
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajaxFileUpload(
        {
            url: "/uploadvaluefile",
            secureuri: false,
            type: "post",
            data:{tag: tag},
            fileElementId: file_id,
            dataType: 'json',
            success: function (data)
            {
                App.unblockUI(page_content);
                div_modal.modal("hide");
                getExcelFile(tag);
            },
            error: function ()
            {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
};

var getExcelFile = function(tag){
    $("#table_number").dataTable({
        "oLanguage": oLanguage,
        "aoColumns" :[
            {
                "mDataProp": "id",
                'sClass': 'center',
                "bVisible": false
            },
            {
                "mDataProp": "file_name",
                'sClass': 'center',
                "sTitle": "文件名"
            },
            {
                "mDataProp": "version",
                'sClass': 'center',
                "sTitle": "版本"
            },
            {
                "mDataProp": "author",
                'sClass': 'center',
                "sTitle": "用户"
            },
            {
                "mDataProp": "otime",
                'sClass': 'center',
                "sTitle": "时间"
            },
            {
                "mDataProp": "url",
                'sClass': 'center',
                "sTitle": "操作"
            }
        ],
        "fnRowCallback": function (nRow, aData, iDisplayIndex) {
            var str_html2 = '<a onclick="process_excel(\'';
            str_html2 += aData.file_name + "')\" class=\"btn default btn-xs purple\" data-toggle=\"modal\">处理 <i class=\"fa fa-cog\"></i></a>";
            str_html2 += '&nbsp; <a target="_blank" class="btn default btn-xs green" href="';
            str_html2 += aData.url + '">下载<i class="fa fa-download"></i></a>';

            str_html2 += '&nbsp; <a onclick="delete_file(';
            str_html2 += aData.id + ',\'' + aData.file_name + "\')\" class=\"btn default btn-xs red\">删除 <i class=\"fa fa-trash-o\"></i></a>";
            $('td:eq(4)', nRow).html(str_html2);
            console.log(nRow);
            return nRow;
        },
        "bPaginate" : true,
        "bFilter" : false,
        "bDestroy": true,
        "bLengthChange" : true,
        "bWidth": true,
        "iDisplayLength" : 10,
        "bSort" : false,
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth": true,
        "sAjaxSource": "/getexcelfilelist",
        "fnServerData": function (sSource, aoData, fnCallback) {
            $.ajax({
                    type: 'get',
                    url: sSource,
                    data: { aoData: JSON.stringify(aoData),
                            tag: tag
                    },
                    dataType: 'JSON',
                    success: function (resp) {
                        fnCallback(resp);
                    },
                    error: function () {
                    }
                }
            );
        }
    });

};

var process_excel = function(file_name){
    $("#file_name").val(file_name);
    $("#process_modal").modal("show");
};

var delete_file = function(n_id, file_name){
    var select_type1 = $("#select_type1").val();
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/deletevaluefile',
            data: {
                n_id: n_id,
                file_name: file_name,
                s_type: select_type1
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                getExcelFile(select_type1, $("#table_fight"));
            },
            error: function () {
                App.unblockUI(page_content);
                error_func();
            }
        }
    );
};

$("#btn_upload_value").on("click", function(e){
    e.preventDefault();
    var select_type1 = $("#select_type1").val();
    file_upload(select_type1, "value_excel_file", $("#upload_value_modal"));
});


$("#btn_add").on("click", function(e){
    e.preventDefault();
    $("#excel_id").val("");
    $("#sheet_name").val("");
    $("#ctype").val("");
    $("#add_modal").modal("show");

});
var excelValidation = function () {
    var form1 = $('#excel_form');
    var rules = {
        sheet_name: {
            required: true
        },
        ctype: {
            required: true
        }
    };
    var messages = {
        sheet_name: {
            required: "请输入工作表."
        },
        ctype: {
            required: "请输入类型名称"
        }
    };

    var submitHandler = function (form) {
        var excel_id = $("#excel_id").val();
        var sheet_name = $("#sheet_name").val();
        var ctype = $("#ctype").val();
        var select_type = $("#select_type").val();
        $.ajax({
                type: 'get',
                url: '/operateexcel',
                data: {
                    excel_id: excel_id,
                    sheet_name: sheet_name,
                    ctype: ctype,
                    stype: select_type
                },
                dataType: 'JSON',
                success: function (data) {
                    if (data.status == 0) {
                        Common.alert_message($("#error_modal"), 0, "操作失败");
                    }
                    $("#add_modal").modal("hide");
                    $("#select_type").change();
                },
                error: function () {
                }
            }
        )
    };
    commonValidation(form1, rules, messages, submitHandler);
};

excelValidation();


$("#btn_process").on("click", function(e){
    e.preventDefault();
    var section = $("#select_section").val();
    var sheet_str = "";
    $("input[name='sheet_type']:checked").each(function(){
        sheet_str += $(this).val() + ",";
    });
    var file_name = $("#file_name").val();
    var select_type1 = $("#select_type1").val();

    $("#process_modal").modal("hide");
    var page_content = $('.page-content');
    App.blockUI(page_content, false);
    $.ajax({
            type: 'get',
            url: '/excelcreate',
            data: {
                section: section,
                sheet_name: sheet_str,
                file_name: file_name,
                s_type: select_type1
            },
            dataType: 'JSON',
            success: function (data) {
                App.unblockUI(page_content);
                Common.alert_message($("#error_modal"), 1, "生成配置文件成功");
            },
            error: function () {
            }
        }
    )
});



var getExcel = function(tag, div_sheet){
    $.ajax({
        type: 'get',
        url: '/getexcelset',
        data: {tag: tag},
        dataType: 'JSON',
        success: function (data) {
            var str_info = "";
            for(var i=0; i < data.length; i ++){
                str_info += "<label class=\"checkbox-inline\"><input type=\"checkbox\" name=\"sheet_type\" value=\"" +
                    data[i]["id"] + "\">" + data[i]["sheet_name"] + "</label>";
            }
            div_sheet.html(str_info);
        },
        error: function () {
        }
    });
};


$("#select_type1").on("change", function(e){
    e.preventDefault();
    console.log(111);
    var select_type1 = $("#select_type1").val();
    getExcelFile(select_type1, $("#table_fight"));
    getExcel(select_type1, $("#sheet_names"));
});

$("#a_fight").on("click", function(e){
    e.preventDefault();
    $("#select_type1").change();
});

$("#select_all").on("click", function(e){
    e.preventDefault();
    $("input[name='sheet_type']").prop("checked", true);
    $("input[name='sheet_type']").parent("span").addClass("checked");
});

$("#no_select_all").on("click", function(e){
    e.preventDefault();
    $("input[name='sheet_type']").each(function(){
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

$("#btn_log").on("click", function(e){
    e.preventDefault();
    var start_date = $("#start_date").val();
    var end_date = $("#end_date").val();
    var select_type2 = $("#select_type2").val();
    var ajax_source = "/getnumberlog";
    var aoColumns = [
        {
            "mDataProp": "user",
            'sClass': 'center',
            "sTitle": "用户"
        },
        {
            "mDataProp": "file_name",
            'sClass': 'center',
            "sTitle": "文件名"
        },
        {
            "mDataProp": "process",
            'sClass': 'center',
            "sTitle": "处理工作表"
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "分区"
        },
        {
            "mDataProp": "otime",
            'sClass': 'center',
            "sTitle": "时间"
        }
    ];
    var data = {
        start_date: start_date,
        end_date: end_date,
        s_type: select_type2
    };
    dataTablePage($("#table_numberlog"), aoColumns, ajax_source, data, false);
});