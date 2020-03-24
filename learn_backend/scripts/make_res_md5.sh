#!/usr/bin/env bash

file_name=$1
tag=$2

unzip $file_name

file_path=${file_name%%-*}.git
new_file_name=${file_name%%-*}_${tag}.zip

cd $file_path

zip -D -r $new_file_name .

cd ..

mv $file_path/$new_file_name .

aaa=`md5 $new_file_name`
echo $aaa
echo $aaa |awk -F'= ' '{print $2}' > $new_file_name.MD5
touch $new_file_name.UNZIP

rm -rf $file_path