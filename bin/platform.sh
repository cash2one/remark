#!/bin/sh

PYTHON2=/apps/python/python2/bin/python
ROOT_DIR=/apps/platform
LOGS_DIR=/apps/logs/platform

###########################################################
mkdir -p $LOGS_DIR

############################################################
function start()
{
    nohup $PYTHON2 -u index.py --appname $1 --mode $2 --log_path $3 --address $4 --port $5 --debug $6 &
}

function stop()
{
    ps -ef | grep index | grep $1 | awk '{printf("kill -9 %s\n",$2)}' | sh
}

echo $#
cd $ROOT_DIR/$1
if [ "$2" = "stop" ] ; then
    stop $6

elif [ "$2" = "restart" ]; then
    stop $6
    start $1 $3 $4 $5 $6 $7

elif [ "$2" = "start" ]; then
    start $1 $3 $4 $5 $6 $7

else
    echo "usage: $0 web|admin start|stop|restart port"
fi
