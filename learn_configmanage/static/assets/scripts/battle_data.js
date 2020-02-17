/**
 * Created by wangrui on 15/10/21.
 */

 create_del_modal($("#battle_modal"), "是否删除此记录", "confirm_del");

var getbattle = function () {
    var sAjaxSource = "/getbattledata";
    var aoColumns = [
        {
            "mDataProp": "id",
            'sClass': 'center',
            "bVisible": false
        },
        {
            "mDataProp": "name",
            'sClass': 'center',
            "sTitle": "名称"
        },
        {
            "mDataProp": "level",
            'sClass': 'center',
            "sTitle": "战队等级"
        },
        {
            "mDataProp": "power",
            'sClass': 'center',
            "sTitle": "战斗力"
        },
        {
            "mDataProp": "desc",
            'sClass': 'center',
            "sTitle": "描述"
        },
        {
            "sTitle": "操作",
            "sClass": "center",
            "sDefaultContent": "<button onclick=\"mod_battle(this)\" class=\"btn default btn-xs yellow\" data-toggle=\"modal\">修改 <i class=\"fa fa-edit\"></i></button><button onclick=\"del_battle(this)\" class=\"btn default btn-xs red\" data-toggle=\"modal\">删除 <i class=\"fa fa-trash-o\"></i></button>"
        }
    ];
    dataTablePage($("#battle_table"), aoColumns, sAjaxSource, {}, false, null);
};
getbattle();

var mod_battle = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#battle_table").dataTable().fnGetData(nRoW);
    window.location.href = "/battle_simulation?id=" + data["id"];
};

var del_battle = function(btn){
    var nRoW = $(btn).parents('tr')[0];
    var data = $("#battle_table").dataTable().fnGetData(nRoW);
    $('#battle_modal').modal("show");
    $("#confirm_del").attr('onclick', "confirm_battle(" + data["id"] + ")");
};

var confirm_battle = function(bid){
    $.ajax({
        type: 'get',
        url: '/deletebattle',
        data: {bid: bid},
        dataType: 'JSON',
        success: function (data) {
            if (data.status == 0) {
                Common.alert_message($("#error_modal"), 0, "删除失败");
            }
            $('#battle_modal').modal("hide");
            getbattle();
        },
        error: function () {
        }
    })
};