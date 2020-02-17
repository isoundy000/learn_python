
var $game_server_1 = $('#game_server_1');
var $game_server_2 = $('#game_server_2');
var $btn_player_offline = $('#btn_player_offline');
var $btn_drop_guild = $('#btn_drop_guild');
var $operate_confirm_modal = $('#operate_confirm_modal');
var $president_id = $('#president_id');
var $operate_confirm_modal_title = $('#operate_confirm_modal_title');
var $operate_confirm_modal_body = $('#operate_confirm_modal_body');
var $operate_confirm_modal_btn = $('#operate_confirm_modal_btn');
var $role_id = $('#role_id');
var $out_all_player_modal = $('#out_all_player_modal');
var $confirm_out_all_player = $('#confirm_out_all_player');
var $opt_password = $('#opt_password');
var $out_all_player_prompt = $('#out_all_player_prompt');

display_left_count();
getGameServerData($game_server_1, 1);
getGameServerData($game_server_2, 1);


var tag;
var server_id;
var role_name;
$btn_player_offline.click(function () {
    var server_id = $game_server_1.val();
    var input_value = $role_id.val();
    if (input_value.length === 0){
        $out_all_player_modal.find('.modal-title').html(server_id+'区 的所有玩家将被踢下线');
        $out_all_player_modal.modal('show')
    }else{
        $operate_confirm_modal_title.html('踢玩家下线');
        $operate_confirm_modal_body.html(
            '<h3><span style="color: red">'+$game_server_1.find("option:selected").text()+'  角色ID为'+$role_id.val()
            +' 游戏名为: '+role_name+'</span>   的玩家将被踢下线</h3>'
        );
        tag = 'player_offline';

        $operate_confirm_modal.modal('show');
    }

});

$out_all_player_modal.on('show.bs.modal', function () {
  $out_all_player_prompt.hide()
});

$confirm_out_all_player.click(function () {
    if ( $opt_password.val() === 'wozhendeyaozhemezuo'){
        my_ajax(true, '/put/player/status', "post", {tag: 'player_offline', server_id: $game_server_1.val(), role_id: ''}, false,function (result) {
            if (result['status'] === 'success'){
                $out_all_player_modal.modal('hide');
                Common.alert_message($error_modal, 1, "操作成功");
            }else{
                $out_all_player_modal.modal('hide');
                Common.alert_message($error_modal, 0, "操作失败："+ result['errmsg']);
            }
        })
    }else{
        $out_all_player_prompt.show()
    }
});

$role_id.bind('input propertychange', function () {
    var input_value = $role_id.val();
    if ( $.isNumeric(input_value) ){
        server_id = $game_server_1.val();
        my_ajax(true, '/getroleinfo', "get", {'server_id': server_id, 'role_type': 'role_id', 'role_search': input_value},
        false, function (result) {
            if (result === null){
                $btn_player_offline.attr('disabled', 'disabled');
            }else{
                role_name = result['name'];
                $btn_player_offline.removeAttr('disabled');
            }
        });
    }else if (input_value.length === 0){
        $btn_player_offline.removeAttr('disabled');
    }else{
        $btn_player_offline.attr('disabled', 'disabled');
    }

});

$president_id.bind('input propertychange', function () {
    var input_value = $president_id.val();
    if (input_value.length > 0 && $.isNumeric(input_value)){
        $btn_drop_guild.removeAttr('disabled')
    }else{
        $btn_drop_guild.attr('disabled', 'disabled')
    }

});

$btn_drop_guild.click(function () {
    $operate_confirm_modal_title.html('解散公会');
    $operate_confirm_modal_body.html(
        '<h3><span style="color: red">'+$game_server_2.find("option:selected").text()+'  玩家id为'+
        $president_id.val()+'</span>  创建的公会将被解散</h3>'
    );
    tag = 'drop_guild';
    server_id = $game_server_2.val();
    $operate_confirm_modal.modal('show')
});

var $error_modal = $('#error_modal');
$operate_confirm_modal_btn.click(function () {
    $operate_confirm_modal_btn.attr('disabled', 'disabled');
    $operate_confirm_modal_btn.text('执行中');
    var send_data = {tag: tag, server_id: server_id};
    if (tag === 'drop_guild'){
        send_data['president_id'] = $president_id.val()
    }else if (tag === 'player_offline'){
        send_data['role_id'] = $role_id.val()
    }

    var success_func = function(result){
        if (result['status'] === 'success'){
            $operate_confirm_modal.modal('hide');
            Common.alert_message($error_modal, 1, "操作成功");
        }else{
            $operate_confirm_modal.modal('hide');
            Common.alert_message($error_modal, 0, "操作失败："+ result['errmsg']);
        }
    };
    my_ajax(true, '/put/player/status', "post", send_data, false, success_func);

    $operate_confirm_modal_btn.removeAttr('disabled');
    $operate_confirm_modal_btn.text('确认操作');
});