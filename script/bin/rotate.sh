
baselogdir=$1
rotatelogs=/apps/httpd/httpd/bin/rotatelogs

while [ 1 ]
do
    echo `date +"%F %T"`" rotatelogs access start"
    $rotatelogs $baselogdir/access/%Y%m%d%H 3600 480 < $baselogdir/access_log
    echo `date +"%F %T"`" rotatelogs access stop"
    sleep 1;
done
