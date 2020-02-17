SHOW VARIABLES LIKE 'validate_password%'
-- 参数说明：

--     validate_password_check_user_name :用户名检测，默认关闭
--     validate_password_dictionary_file :字典文件，就是要在字典规则里才能满足密码的条件。
--     validate_password_length :密码的长度至少为8位
--     validate_password_mixed_case_count ：密码中至少有一个大写小字母
--     validate_password_number_count ：密码中至少一个数字
--     validate_password_special_char_count :密码中至少一个特殊字符
--     validate_password_policy :密码的安全策略 MEDIUM或者0 、LOW或者1、STRONG或者2
--     LOW :策略仅测试密码长度。密码长度必须至少为8个字符。
--     MEDIUM :策略添加了密码必须至少包含1个数字字符，1个小写字符，1个大写字符和1个特殊（非字母数字）字符的条件。
--     STRONG :策略添加了长度为4或更长的密码子字符串不能匹配字典文件中的字词（如果已经指定）的条件。
--     所以最终的密码设置策略就是：不得低于8位，而且必须至少有一个大写和一个小写字母、至少一个数字和至少的一个特殊字符组成；

-- 在设置密码是建议的规则是：大写+小写+特殊字符+数字组成的8位以上密码

SET GLOBAL validate_password_policy=LOW;

create database kuaiyou_config default character set utf8 collate utf8_bin;
grant all on kuaiyou_config.* to 'sanguo_bg2'@'%' identified by 'sanguo_passwd';
grant all on kuaiyou_config.* to 'sanguo_bg2'@'localhost' identified by 'sanguo_passwd';
create database fantasy_sanguo_acc default character set utf8 collate utf8_bin;
grant all on fantasy_sanguo_acc.* to 'sanguo_bg2'@'%' identified by 'sanguo_passwd';
grant all on fantasy_sanguo_acc.* to 'sanguo_bg2'@'localhost' identified by 'sanguo_passwd';
create database sensor_online_kuaiyou default character set utf8 collate utf8_bin;
grant all on sensor_online_kuaiyou.* to 'sanguo_bg'@'%' identified by 'sanguo_passwd';
grant all on sensor_online_kuaiyou.* to 'sanguo_bg'@'localhost' identified by 'sanguo_passwd';
flush privileges;