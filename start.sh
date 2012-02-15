#!/bin/bash

# Replace these three settings.
PROJDIR="`pwd`"

cd $PROJDIR
sudo ./stop.sh

PIDFILE="$PROJDIR/logs/fcgi.pid"
sudo ./manage.py runfcgi pidfile=$PIDFILE host=127.0.0.1 port=3051 #daemonize=false

CELERY_PIDFILE="$PROJDIR/logs/celeryd.pid"
CELERY_LOGFILE="$PROJDIR/logs/celeryd.log"
sudo ./manage.py celeryd --pidfile=$CELERY_PIDFILE -f $CELERY_LOGFILE &