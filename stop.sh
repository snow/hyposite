#!/bin/bash

# Replace these three settings.
PROJDIR="`pwd`"
cd $PROJDIR

PIDFILE="$PROJDIR/logs/fcgi.pid"
if [ -f $PIDFILE ]; then
    sudo kill `cat -- $PIDFILE`
    sudo rm -f -- $PIDFILE
fi

CELERY_PIDFILE="$PROJDIR/logs/celeryd.pid"
if [ -f $CELERY_PIDFILE ]; then
    sudo kill `cat -- $CELERY_PIDFILE`
    sudo rm -f -- $CELERY_PIDFILE
fi