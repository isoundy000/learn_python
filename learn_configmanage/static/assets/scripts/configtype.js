/**
 * Created by wangrui on 14-10-14.
 */

var ConfigType = function(){
    var typeValidation = function () {
        var form1 = $('#type_form');
        var error1 = $('.alert-danger', form1);
        form1.validate({

            errorElement: 'span', //default input error message container
            errorClass: 'help-block', // default input error message class
            focusInvalid: false, // do not focus the last invalid input
            ignore: "",
            rules: {
                type_name: {
                    required: true
                },
                type_key: {
                    required: true
                }
            },
            messages: {
                type_name: {
                    required: "请输入配置类型名."
                },
                type_key: {
                    required: "请输入配置主键."
                }
            },
            invalidHandler: function (event, validator) { //display error alert on form submit
                error1.show();
                App.scrollTo(error1, -200);
            },

            highlight: function (element) { // hightlight error inputs
                $(element)
                    .closest('.form-group').addClass('has-error'); // set error class to the control group
            },

            unhighlight: function (element) { // revert the change done by hightlight
                $(element)
                    .closest('.form-group').removeClass('has-error'); // set error class to the control group
            },

            success: function (label) {
                label
                    .closest('.form-group').removeClass('has-error'); // set success class to the control group
            },

            submitHandler: function (form) {
                error1.hide();
                var config_type_id = $("#config_type_id").val();
                var type_name = $("#type_name").val();
                var type_alias = $("#type_alias").val();
                var type_key = $("#type_key").val();
                var type_section = $('#query_section_s').val();
                $.ajax({
                        type: 'get',
                        url: '/operatetype',
                        data: {config_type_id: config_type_id, type_key: type_key,
                               type_alias: type_alias, type_name: type_name, type_section: type_section},
                        dataType: 'JSON',
                        success: function (data) {
                            if (data.status == 0) {
                                alert("添加配置类型失败.");
                            }
                            else if (data.status == 2){
                                alert("配置类型名称重复或者相同的配置不能属于同一分区");
                            }
                            else{
                                $("#type_modal").modal("hide");
                                $("#query_section_s").change();
                            }
                        },
                        error: function (XMLHttpRequest) {
                            error_func(XMLHttpRequest);
                        }
                    }
                )
            }
        });
    };
    //查询分区表
    var getSection = function (){
        var page_content = $('.page-content');
        App.blockUI(page_content, false);
        $.ajax({
            type: 'get',
            url: '/querysection',
            dataType: 'JSON',
            async: false,
            success: function (data) {
                App.unblockUI(page_content);
                if (data.length != 0) {
                    var str_info = "";
                    for (var i in data) {
                        str_info += "<option value='" + data[i].id + "'>" + data[i].name;
                        str_info += "</option>";
                    }
                    $("#query_section_s").html(str_info);
                }
            },
            error: function (XMLHttpRequest) {
                App.unblockUI(page_content);
                error_func(XMLHttpRequest);
            }
        });
    };

    getSection();

    typeValidation();
}();

$("#query_section_s").on("change", function(e){
    e.preventDefault();
    var section_id = $("#query_section_s").val();
    var ajaxSource = "/querytype";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "name",
            "sClass": "center",
            "sTitle": "类型名称"
        },
        {
            "mDataProp": "alias",
            "sClass": "center",
            "sTitle": "中文名称"
        },
        {
            "mDataProp": "type_key",
            'sClass': 'center',
            "sTitle": "主键"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_type(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button><button onclick=\"del_type(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    var data = {
        section_id: section_id
    };
    dataTablePage($("#type_table"), aoColumns, ajaxSource, data, false, null);
});

$("#query_section_s").change();


//添加type
$("#add_type").click(function(e){
    e.preventDefault();
    $("#type_modal").modal("show");
    $("#config_type_id").val("");
    $("#type_name").val("");
    $("#type_alias").val("");
    $("#type_key").val("");
});

//修改type
function mod_type(t){
    var nRow = $(t).parents('tr')[0];
    var data = $("#type_table").dataTable().fnGetData(nRow);
    $("#config_type_id").val(data["id"]);
    $("#type_name").val(data["name"]);
    $("#type_alias").val(data["alias"]);
    $("#type_key").val(data["type_key"]);
    $("#type_modal").modal("show");
}

//删除type
function del_type(t){
    $("#type_del_modal").modal("show");
    var nRow = $(t).parents('tr')[0];
    var data = $("#type_table").dataTable().fnGetData(nRow);
    $("#confirm_del_type").attr('onclick', 'fun_del_type(' + data["id"] + ');');
}

//删除type 确认
function fun_del_type(type_id){
    $.ajax({
            type: 'get',
            url: '/deletetype',
            data: {type_id: type_id},
            dataType: 'JSON',
            success: function (data) {
                if(data.status == 0){
                    alert("删除配置类型失败.");
                }
                $("#query_section_s").change();
            },
            error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
        }
    )
}
