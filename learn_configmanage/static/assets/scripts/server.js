/**
 * Created by ghou on 20-03-28.
 */

var $open_datetime = $('#open_datetime');
var $sync_create_time = $('#sync_create_time');
// display_left_filter(;

handleDatePickers2();
handleTimePickers();

var now_date = getNowFormatDate(0);
$("#create_date").val(now_date);
$("#restart_date").val(now_date);