#!/usr/bin/env bash
MYPATH="/apps/stat"
hour=$(date -d"-1 hour" +%H)
day=$(date -d"-1 hour" +%d)
month=$(date -d"-1 hour" +%b)
month_int=$(date -d"-1 hour" +%m)
year=$(date -d"-1 hour" +%Y)
min=$(date +%M)
#date=${year}${month_int}${day}
date=$(date -d"$year-$month_int-$day $hour:$min" +%s)

#MYPATH="/home/yanzhiwu/stat"

mkdir -p $MYPATH
##########
myfile=${year}${month_int}${day}${hour}
echo $myfile

if [ ! -f "${MYPATH}/${myfile}" ]; then
    wget -P $MYPATH --http-user=yidao --http-passwd=yidao http://log.yidao.info/nginx_access/${myfile}
fi
echo $day $month $year
fp_pv=$(grep "yidao.info\/\"" ${MYPATH}\/${myfile} -c)
all_pv=$(grep "yidao.info" ${MYPATH}\/${myfile} -c)
echo $all_pv
echo $fp_pv
fp_uv=$(grep "yidao.info\/\"" ${MYPATH}\/${myfile} | grep -o 'ci&token=[A-Za-z0-9]\+' | sort -u |grep 'token' -c )
all_uv=$(grep "yidao.info\/" ${MYPATH}\/${myfile} | grep -o 'ci&token=[A-Za-z0-9]\+' | sort -u |grep 'token' -c )
echo $all_uv
echo $fp_uv
fp_ip=$(grep "yidao.info\/\"" ${MYPATH}\/${myfile} | awk 'BEGIN{FS=" "} {print $1}' | sort -u | grep '.' -c)
all_ip=$(grep "yidao.info\/" ${MYPATH}\/${myfile} | awk 'BEGIN{FS=" "} {print $1}' | sort -u | grep '.' -c)
echo $all_ip
echo $fp_ip
all_user=$(grep "yidao.info\/\"" ${MYPATH}\/${myfile} | grep -o "Hm_lvt_[A-Za-z0-9]\+\=[A-Za-z0-9]\+"|sort -u | grep 'Hm_lvt_' -c)
echo $all_user
echo $day $month $year
echo $date
HOSTNAME="rdshf7hicnex6yhgi3h8.mysql.rds.aliyuncs.com";
PORT="3306";
USERNAME="yidao";
PASSWORD=$1;
DBNAME="yidao_stat"
TABLENAME_ALL="site"
TABLENAME_FP="\`index\`"

replace_sql_all="replace into ${TABLENAME_ALL}(day,hour,pv,uv,ip,user) values($date,$hour,$all_pv,$all_uv,$all_ip,$all_user)"
replace_sql_fp="replace into ${TABLENAME_FP}(day,hour,pv,uv,ip) values($date,$hour,$fp_pv,$fp_uv,$fp_ip)"
/apps/mysql/mysql5/bin/mysql -h${HOSTNAME} -P${PORT} -u${USERNAME} -p"${PASSWORD}" ${DBNAME} -e "${replace_sql_all}"
/apps/mysql/mysql5/bin/mysql -h${HOSTNAME} -P${PORT} -u${USERNAME} -p"${PASSWORD}" ${DBNAME} -e "${replace_sql_fp}"

rm -rf $MYPATH/`date +%Y%m%d -d -10days`*