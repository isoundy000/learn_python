#!/bin/bash
export MYSQL_PWD=sanguo_passwd
pla="blood"
file=$1

TIME=$(date '+%Y%m%d%H%M')

if [[ $# != 1 ]];then
    echo "必须带一个参数"
    exit -1
fi


list=""
for i in $(cat /root/deploy_code/${file})
do
    [ ! -e /data/hot_${pla}/source999999/${i} ] && echo "${i}不存在" && exit -1
    list=${list}${i}" "
done

echo "被派发的代码列表是："
echo $list
echo " "

cd /data/hot_${pla}/source999999/
tar -zcf /root/deploy_code/${pla}_source.${TIME}.tar.gz ${list}

ip_list=$(mysql -usanguo_bg -h 10.104.93.220 -P 3306 -N -e "use config_manage;select distinct(ip) from t_server")

count=0
for ip in ${ip_list}
do
    if [[ "${ip}"x != "10.104.31.44"x ]];then
        echo "${ip}"
        scp /root/deploy_code/${pla}_source.${TIME}.tar.gz ${ip}:/data/hot_${pla}/
        ssh ${ip} "cd /data/hot_${pla}/ && cp -rf source source_${TIME} && mv ${pla}_source.${TIME}.tar.gz source/ && cd source/ && tar xf ${pla}_source.${TIME}.tar.gz && rm -f ${pla}_source.${TIME}.tar.gz"
        echo " "
        count=$((${count}+1))
    fi
done

rm -f /root/deploy_code/${pla}_source.${TIME}.tar.gz
echo "总共派发了${count}台服务器"
