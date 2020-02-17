//全局变量
$start_date = $('#start_date');
$end_date = $('#end_date');
$role_ranking_server = $('#role_ranking_server');
$game_server_list = $('#game_server_list');

//初始化
handleDatePickers();
$start_date.val(getNowFormatDate(1));
$end_date.val(getNowFormatDate(0));
// getGameServerData($role_ranking_server, 2, 1);


//服务器列表初始化
$game_server_list.multiselect({
    numberDisplayed: 2,
    includeSelectAllOption: true,
    selectAllText: '选择全部',
    enableFiltering: true,
    nonSelectedText: "==请选择游戏服==",
    buttonWidth: '100%',
    maxHeight: 300
}
);
getGameServerData_2($game_server_list);


//生成角色充值排行榜表格函数
var table_success_func = function (data) {
    var columns = [{"title": "区服"}, {"title": "用户ID"}, {"title": "角色ID"},{"title":"角色名"},{"title":"充值时间"},
                {"title":"充值金额"}];
    var columnDefs = [
        {
            "targets": -2,
            "render": function (data) {
                if (data === '100'){
                    return '已完成'
                } else {
                    return data + '%'
                }

            }
        },
        {
            "targets": -1,
            "render": function (data, type, row) {
                var schedule = parseInt(row[6]);
                if (isNaN(schedule)){
                    return '进度异常'
                }else{
                    var btn_html = '<button type="button" onclick="btn_task_detail(this)" ' +
                        'class="btn btn-xs btn-primary">详情</button>';
                    return (schedule <= 100) ? btn_html : ''

                }
            }
        }
    ];
    new_front_page_table2($("#role_recharge_table"), data,columns,columnDefs,false);
};

var role_recharge_record = function () {
    var start_date = $start_date.val();
    var end_date = $end_date.val();
    var server_info;
    var server_list = [];
    for (server_info in $game_server_list.val()){
        server_list.push(server_info.split('区')[0])
    }
    $.ajax({
        "url": "/query/role_recharge_ranking",
        "type": "POST",
        "data": {"game_server_list": JSON.stringify(server_list), "start_date": start_date, "end_date": end_date},
        "error": function (jqXHR) {
            alert("访问异常：错误码（" + jqXHR.status + '）');
            table_success_func([])
        },
        "success": function (result) {
            var table_data = [];
            if (result['status'] === 'ok') {
                table_data = result['ranking_list']
            }
            table_success_func(table_data)
        }
    });
};

role_recharge_record();

//查询按钮点击事件
$('#btn_query_role').click(function () {
    var server_value = $game_server_list.val();
    if (server_value === null){
        alert('提示：游戏服不能为空！！！');
        return
    }
    role_recharge_record();
});