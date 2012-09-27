#!/bin/bash


# To make uwsgi auto run when system up,
# add the following line in /etc/rc.local
# /data/project/python_gears/bin/manage_uwsgi.sh start > /dev/null 2>&1


if [[ $UID != 0 ]]
then
    echo "must run as root"
    exit 1
fi

usage(){
    echo "$0 {start|stop|restart|status}"
    exit 0
}

check_uwsgi_pid(){
    if [[ ! -e run/uwsgi.pid ]]
    then
        echo "run/uwsgi.pid not exists"
        exit 2
    fi
}

start_uwsgi(){
    uwsgi --ini ./deploy/python_gears_uwsgi.ini
    [[ $? == 0 ]] && echo "staring done"
}

stop_uwsgi(){
    check_uwsgi_pid
    kill -QUIT `cat run/uwsgi.pid`
    [[ $? == 0 ]] && echo "stop done"
}

restart_uwsgi(){
    check_uwsgi_pid
    kill `cat run/uwsgi.pid`
    [[ $? == 0 ]] && echo "restart done"
}

status_uwsgi(){
    process_amount=`ps -ef | grep python_gears_uwsgi.ini | grep -v grep | wc -l`
    if [[ $process_amount == 0 ]]
    then
        echo "NOT running"
    else
        echo "running"
    fi
}


[[ $# != 1 ]] && usage

cd /data/project/python_gears


case $1 in
    start)
        start_uwsgi
        ;;
    stop)
        stop_uwsgi
        ;;
    restart)
        restart_uwsgi
        ;;
    status)
        status_uwsgi
        ;;
    *)
        usage
        ;;
esac

exit 0