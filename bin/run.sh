#!/bin/sh


ROOT_DIR=/apps/platform/bin
LOG_PATH=/apps/logs/platform/access_log
########################################################################################
function platform_web()
{
    /bin/sh -x $ROOT_DIR/platform.sh web restart online $LOG_PATH 127.0.0.1 6001 False
    /bin/sh -x $ROOT_DIR/platform.sh web restart online $LOG_PATH 127.0.0.1 6002 False
    /bin/sh -x $ROOT_DIR/platform.sh web restart online $LOG_PATH 127.0.0.1 6003 False
    /bin/sh -x $ROOT_DIR/platform.sh web restart online $LOG_PATH 127.0.0.1 6004 False
}

function platform_reco()
{
    /bin/sh -x $ROOT_DIR/platform.sh reco restart online $LOG_PATH 127.0.0.1 6101 False
    /bin/sh -x $ROOT_DIR/platform.sh reco restart online $LOG_PATH 127.0.0.1 6102 False
    /bin/sh -x $ROOT_DIR/platform.sh reco restart online $LOG_PATH 127.0.0.1 6103 False
}

function platform_admin()
{
    /bin/sh -x $ROOT_DIR/platform.sh admin restart online $LOG_PATH 127.0.0.1 6010 True
}

function platform_stat()
{
    /bin/sh -x $ROOT_DIR/platform.sh stat restart online $LOG_PATH 127.0.0.1 6020 False
}

########################################################################################
function platform_web_test()
{
    /bin/sh -x $ROOT_DIR/platform.sh web restart test $LOG_PATH 127.0.0.1 7001 True
}

function platform_reco_test()
{
    /bin/sh -x $ROOT_DIR/platform.sh reco restart test $LOG_PATH 127.0.0.1 7101 True
}

function platform_admin_test()
{
    /bin/sh -x $ROOT_DIR/platform.sh admin restart test $LOG_PATH 127.0.0.1 7010 True
}

function platform_stat_test()
{
    /bin/sh -x $ROOT_DIR/platform.sh stat restart test $LOG_PATH 127.0.0.1 7020 True
}

########################################################################################
function platform_web_dev()
{
    /bin/sh -x $ROOT_DIR/platform.sh web restart dev $LOG_PATH 127.0.0.1 7001 True
}

function platform_reco_dev()
{
    /bin/sh -x $ROOT_DIR/platform.sh reco restart dev $LOG_PATH 127.0.0.1 7101 True
}

function platform_admin_dev()
{
    /bin/sh -x $ROOT_DIR/platform.sh admin restart dev $LOG_PATH 127.0.0.1 7010 True
}

function platform_stat_dev()
{
    /bin/sh -x $ROOT_DIR/platform.sh stat restart dev $LOG_PATH 127.0.0.1 7020 True
}

##############################################
function online()
{
    if [ "$1" = "web" ] ; then
        platform_web
    elif [ "$1" = "reco" ]; then
        platform_reco
    elif [ "$1" = "admin" ]; then
        platform_admin
    elif [ "$1" = "stat" ]; then
        platform_stat
    else
        platform_web
        platform_admin
        platform_reco
        platform_stat
    fi
}

function test()
{
    if [ "$1" = "web" ] ; then
        platform_web_test
    elif [ "$1" = "reco" ]; then
        platform_reco_test
    elif [ "$1" = "admin" ]; then
        platform_admin_test
    elif [ "$1" = "stat" ]; then
        platform_stat_test
    else
        platform_web_test
        platform_admin_test
        platform_reco_test
        platform_stat_test
    fi
}

function dev()
{
    if [ "$1" = "web" ] ; then
        platform_web_dev
    elif [ "$1" = "reco" ]; then
        platform_reco_dev
    elif [ "$1" = "admin" ]; then
        platform_admin_dev
    elif [ "$1" = "stat" ]; then
        platform_stat_dev
    else
        platform_web_dev
        platform_admin_dev
        platform_reco_dev
        platform_stat_dev
    fi
}

###############################################
if [ "$1" = "online" ] ; then
    online $2
elif [ "$1" = "test" ]; then
    test $2
elif [ "$1" = "dev" ]; then
    dev $2
else
    echo "usage: $0 online|test [web|reco|admin|reco]"
fi