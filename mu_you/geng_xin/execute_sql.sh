#!/bin/bash
export MYSQL_PWD=sanguo_passwd
platform="kuaiyou"
user="sanguo_bg"
pass="sanguo_passwd"
manage="3306"
host="127.0.0.1"

result_from_server=$(mysql -u${user} -h ${host} -P ${manage} -N -e "use ${platform}_config;select gameid,ip from t_server order by gameid;")
section_numbers=$(mysql -u${user} -h ${host} -P ${manage} -N -e "use ${platform}_config;select count(*) from t_server;")

base_name=""
port_name=""
count=0

if [[ $# -ne 1 ]];then
    echo -e "\033[;31mUsage: sh execute_sql.sh file.sql \033[0m"
    echo -e "\033[;31mExample: sh execute_sql.sh 1108.sql \033[0m"
    exit -1
fi

for i in $(seq 1 2 $((${section_numbers} * 2)))
do
    server_id=$(echo ${result_from_server} | awk '{print $'${i}'}')
    server_ip=$(echo ${result_from_server} | awk '{print $'$((${i}+1))'}')

    if [[ ${server_id}x == 999998x ]] || [[ ${server_id}x == 997x ]] || [[ ${server_id}x == 999999x ]] || [[ ${server_id}x == 1000000x ]] || [[ ${server_id}x == 998x ]];then
        continue
    fi

    result=$(mysql -u${user} -h ${host} -P ${manage} -N -e "use ${platform}_config;select port,\`database\` from t_gamebase where server=${server_id}")
    port=$(echo ${result} | awk '{print $1}')
    datase=$(echo ${result} | awk '{print $2}')
    if [[ ${port}x == ${port_name}x ]] && [[ ${base_name}x == ${datase}x ]];then
        continue
    fi

    if [[ "${datase}"x != ""x ]];then
        echo -e 正在${server_ip}上对库--"\033[;32m${datase}\033[0m"进行处理... ...
        mysql -u${user} -h${server_ip} -P${port} -f ${datase} < ./$1
        count=$((${count} + 1))
        base_name=${datase}
        port_name=$port
        echo " "
    fi
done

echo -e "\033[;32m总共执行了${count}次 \033[0m"
