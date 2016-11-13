#!/bin/sh

ROOT_DIR=/apps/platform
LOGS_DIR=/apps/logs/platform_demand
PYTHON2=/apps/python/python2/bin/python

mkdir -p $LOGS_DIR

cd $ROOT_DIR/script/yidao

date_time=`date '+%Y%m%d'`

$PYTHON2 demand_monitor.py --mode $1 --log_path $LOGS_DIR/$date_time

last_month=`date --date='1 month ago' '+%Y%m'`
rm -rf $LOGS_DIR/$last_month*
