#!/bin/sh

ROOT_DIR=/apps/platform/bin
LOGS_DIR=/apps/logs

function init()
{
    mkdir -p $LOGS_DIR/$1/access
    mkfifo $LOGS_DIR/$1/access_log
}

function start()
{
    nohup /bin/sh $ROOT_DIR/rotate.sh $LOGS_DIR/$1 >> $LOGS_DIR/$1/access_rotate.log 2>&1 &
}

function stop()
{
    ps -ef | grep $1 | grep rotate | awk '{printf("kill -9 %s\n",$2)}' | sh
    ps -ef | grep rotatelogs | awk '{printf("kill -9 %s\n",$2)}' | sh
}

function del()
{
    last_month=`date --date='1 month ago' '+%Y%m'`
    rm -rf $LOGS_DIR/$1/access/*$last_month*
}

##############################################
if [ "$2" = "stop" ] ; then
    stop $1
elif [ "$2" = "restart" ]; then
    stop $1
    start $1
elif [ "$2" = "start" ]; then
    start $1
elif [ "$2" = "del" ]; then
    del $1
elif [ "$2" = "init" ]; then
    init $1
else
    echo "usage: $0 nginx/platform start|stop|restart|del|init"
fi
