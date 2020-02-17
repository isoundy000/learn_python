/**
 * Created by wangrui on 16/1/19.
 */


function query_down_center(){
    var ajax_source = "/querydowncenter";
    var aoColumns = [
        {
            "mDataProp": "id",
            "sClass": "center",
            "bVisible": false
        },
        {
            "mDataProp": "time",
            "sClass": "center",
            "sTitle": "日期"
        },
        {
            "mDataProp": "filename",
            "sClass": "center",
            "sTitle": "文件名"
        },
        {
            "mDataProp": "size",
            "sClass": "center",
            "sTitle": "文件大小(B)"
        },
        {
            "mDataProp": "url",
            'sClass': 'center',
            "sTitle": "操作"
        }
    ];
    var fnRowCallback = function (nRow, aData) {
        var str_html2 = "";
        str_html2 += '&nbsp; <a target="_blank" class="btn default btn-xs blue" href="';
        str_html2 += aData.url + '">下载<i class="fa fa-download"></i></a>';
        $('td:eq(3)', nRow).html(str_html2);
        return nRow;
    };
    dataTablePage($("#downcenter_table"), aoColumns, ajax_source, {}, false, fnRowCallback);
}

query_down_center();