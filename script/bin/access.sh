ROOT_DIR=/apps/platform/script/admin
LOGS_DIR=/apps/logs
PYTHON2=/apps/python/python2/bin/python

function start()
{
   nohup $PYTHON2 -u $ROOT_DIR/clear_user_access.py $2 >> $LOGS_DIR/$1/access_log  2>&1 &
   echo -n `date +"%F %T" `"  " >> $LOGS_DIR/$1/access_log
}

function stop()
{
    ps -ef | grep $1 | grep clear_user_access | awk '{printf("kill -9 %s\n",$2)}' | sh
}

##############################################
if [ "$2" = "start" ] ; then
    start $1 $3
elif [ "$2" = "stop" ]; then
    stop $1
elif [ "$2" = "restart" ]; then
    stop $1
    start $1 $3
else
    echo "usage: $0 nginx/platform start|stop|restart"
fi
