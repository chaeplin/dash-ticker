#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import simplejson as json
import redis
from datetime import datetime
import time
from statistics import mean

from config.role import *
from config.rkeys import *

#-------
def check_dash_last_5min_entry():
    try:
        count = r.zcard(r_SS_DASH_BTC_5MIN_HISTORY)
        if count < 288512:
            print('dash 5 min history has less than ' + 288512)
            sys.exit()

        last = r.zrange(r_SS_DASH_BTC_5MIN_HISTORY, -1, -1, withscores=True)[0][1]
        if last > 0:
            return last

        else:
            sys.exit()

    except Exception as e:
        print(e.args[0])
        sys.exit()    


def timecheck(epoch_lastentry):
    date_last_entry = datetime.utcfromtimestamp(epoch_lastentry)

    t_second = date_last_entry.second
    t_minute = date_last_entry.minute
    t_hour   = date_last_entry.hour
    t_day    = date_last_entry.day
    t_month  = date_last_entry.month
    t_year   = date_last_entry.year

    c_min_div = t_minute / 5
    f_min = (int(c_min_div) + 1) * 5
    f_time = time.mktime((t_year, t_month, t_day, t_hour, f_min, 0, 0, 0, 0))

    return f_time


def get_dash_1min_history(epoch_tocheck):
    while len(r.zrangebyscore(r_SS_DASH_BTC_PRICE, epoch_tocheck - 300, epoch_tocheck)) < 1: 
        print(epoch_tocheck)
        epoch_tocheck = epoch_tocheck + 300
        if epoch_tocheck > epoch00:
            sys.exit()

    last_5min = r.zrangebyscore(r_SS_DASH_BTC_PRICE, epoch_tocheck - 300, epoch_tocheck, withscores=True)

    listof5minval = []
    for x in last_5min:
        epoch_datetime, val = x[0].decode("utf-8").split(':')
        listof5minval.append(float(val))

    if len(listof5minval) > 2:
        Avg = round(mean(sorted(listof5minval)[1:-1]), 5)

    else:
        Avg = round(mean(sorted(listof5minval)), 5)

    # redis
    try:
        pipe = r.pipeline()
        pipe.zadd(r_SS_DASH_BTC_5MIN_HISTORY, epoch_tocheck, str(int(epoch_tocheck)) + ':' + str(Avg))
        response = pipe.execute()
        return True

    except Exception as e:
        print(e.args[0])
        sys.exit()

#---------------------
def check_redis():
    if HOST_ROLE == 'MASTER':
        SETINEL_HOST = MASTER_SETINEL_HOST
        REDIS_MASTER = MASTER_REDIS_MASTER

    else:
        SETINEL_HOST = SLAVE_SETINEL_HOST
        REDIS_MASTER = SLAVE_REDIS_MASTER        

    s = redis.StrictRedis(host=SETINEL_HOST, port=26379, socket_timeout=0.1)
    try:
        h = s.execute_command("SENTINEL get-master-addr-by-name mymaster")[0].decode("utf-8")
        print(h)
        if h == REDIS_MASTER:
            print('Other host is redis master')
            sys.exit()

        else:
            pass

    except Exception as e:
        print(e.args[0])
        sys.exit()

#----------------------
# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

#
now = datetime.now()
epoch00 = int(time.mktime(now.timetuple())) - now.second

#---------------------
#
try:
    check_redis()

except Exception as e:
    print(e.args[0])

#
try:
    while True:
        last5minentry = check_dash_last_5min_entry()
        epoch_tocheck = timecheck(last5minentry)
        print(time.time(), epoch_tocheck, epoch00)
        if epoch_tocheck >= epoch00:
           break 
        else:
            get_dash_1min_history(epoch_tocheck)

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)

