#!/bin/bash
export MYSQL_PWD=sanguo_passwd
user="sanguo_bg"
manage="3306"
host="127.0.0.1"

result_from_server=$(mysql -u${user} -h ${host} -P ${manage} -N -e "use config_manage;select gameid,ip from t_server order by gameid;")
section_numbers=$(mysql -u${user} -h ${host} -P ${manage} -N -e "use config_manage;select count(*) from t_server;")

for i in $(seq 1 2 $((${section_numbers} * 2)))
do
    server_id=$(echo ${result_from_server} | awk '{print $'${i}'}')
    server_ip=$(echo ${result_from_server} | awk '{print $'$((${i}+1))'}')

    if [[ ${server_id}x == 999998x ]] || [[ ${server_id}x == 997x ]] || [[ ${server_id}x == 999999x ]] || [[ ${server_id}x == 1000000x ]] || [[ ${server_id}x == 998x ]] || [[ ${server_id}x == 9999x ]] || [[ ${server_id}x == 99997x ]];then
        continue
    fi
    echo "当前处理的是${server_id}区"
    #ssh ${server_ip} "cat /data/hot_blood/log/hot_1/game_${server_id}/game/2018-08-17.log | grep -E \"2018-08-17 00|2018-08-17 01:[0-1][0-5]\" | grep \"athletics\]\[use\" | awk -F ',' '{print \$4 \$5}'"
    ssh ${server_ip} "cat /data/hot_blood/log/hot_1/game_${server_id}/game/2018-09-19.log | grep 'xxxxxxxxxxxxxxxxx'"
    echo "--------------------------"
done

