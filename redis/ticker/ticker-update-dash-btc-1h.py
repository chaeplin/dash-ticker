#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import simplejson as json
import redis
from datetime import datetime
import time
from statistics import mean

from config.role import HOST_ROLE, MASTER_SETINEL_HOST, MASTER_REDIS_MASTER, SLAVE_SETINEL_HOST, SLAVE_REDIS_MASTER
from config.rkeys import r_SS_DASH_BTC_1H_HISTORY, r_SS_DASH_BTC_5MIN_HISTORY

def check_dash_last_1h_entry():
    try:
        count = r.zcard(r_SS_DASH_BTC_1H_HISTORY)
        if count == 0:
            # then check first entry of 5 min history
            last = r.zrange(r_SS_DASH_BTC_5MIN_HISTORY, 0, 0, withscores=True)[0][1]
            return last

        else:
            last = r.zrange(r_SS_DASH_BTC_1H_HISTORY, -1, -1, withscores=True)[0][1]
            if last > 0:
                return last

            else:
                sys.exit()

    except Exception as e:
        print(e.args[0])
        sys.exit()


def timecheck(epoch_lastentry):
    date_last_entry = datetime.utcfromtimestamp(epoch_lastentry)
    print(date_last_entry)

    t_second = date_last_entry.second
    t_minute = date_last_entry.minute
    t_hour   = date_last_entry.hour
    t_day    = date_last_entry.day
    t_month  = date_last_entry.month
    t_year   = date_last_entry.year

    f_time = time.mktime((t_year, t_month, t_day, t_hour, 0, 0, 0, 0, 0))

    return f_time

def get_dash_5min_history(epoch_tocheck):
    while len(r.zrangebyscore(r_SS_DASH_BTC_5MIN_HISTORY, epoch_tocheck, epoch_tocheck + 3600)) < 1:
        epoch_tocheck = epoch_tocheck + 3600

    last_1h = r.zrangebyscore(r_SS_DASH_BTC_5MIN_HISTORY, epoch_tocheck, epoch_tocheck + 3600, withscores=True)
   
    list_1hval = []
    for x in last_1h:
        epoch_datetime, val = x[0].decode("utf-8").split(':')
        list_1hval.append(float(val))

    if len(list_1hval) > 2:
        Avg    = round(mean(sorted(list_1hval)[1:-1]), 5)
        minval = round(sorted(list_1hval)[0], 5)
        maxval = round(sorted(list_1hval)[-1], 5)

    else:
        Avg    = round(mean(sorted(list_1hval)), 5)
        minval = round(sorted(list_1hval)[0], 5)
        maxval = round(sorted(list_1hval)[-1], 5)

    print(minval, Avg, maxval)

    # redis
    try:
        pipe = r.pipeline()
        pipe.zadd(r_SS_DASH_BTC_1H_HISTORY, epoch_tocheck + 3600, str(int(epoch_tocheck + 3600)) + ':' + str(minval) + ':' + str(Avg) + ':' + str(maxval)) 
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

try:
    while True:
        last1hentry   = check_dash_last_1h_entry()
        epoch_tocheck = timecheck(last1hentry)

        if epoch_tocheck >= (epoch00 - (now.minute * 60)):
            break
        else:
            get_dash_5min_history(epoch_tocheck)

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)

