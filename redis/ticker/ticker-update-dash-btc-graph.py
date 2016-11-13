#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import simplejson as json
import redis
from datetime import datetime
import time
from statistics import mean

from config.role import *
from config.rkeys import *


def get_data():

    list_min = []
    list_avg = []
    list_max = []

    epochfirst = r.zrange(r_SS_DASH_BTC_1H_HISTORY, 0, 0, withscores=True)[0][1]

    data1h = r.zrangebyscore(r_SS_DASH_BTC_1H_HISTORY, epochfirst, epoch5minlast) 
    for x in data1h:
        tstampx, minvalx, avgvalx, maxvalx = x.decode("utf-8").split(':')
#        list_min.append([int(tstampx + '000'), float(minvalx)])
#        list_avg.append([int(tstampx + '000'), float(avgvalx)])
#        list_max.append([int(tstampx + '000'), float(maxvalx)])
        list_avg.append([int(tstampx + '000'), float(maxvalx)])

    data5m = r.zrangebyscore(r_SS_DASH_BTC_5MIN_HISTORY, epoch5minlast, epoch1minlast)
    for y in data5m:
        tstampy, avgvaly = y.decode("utf-8").split(':')
        list_avg.append([int(tstampy + '000'), float(avgvaly)])

    data1m = r.zrangebyscore(r_SS_DASH_BTC_PRICE, epoch1minlast, epoch00)
    for z in data1m:
        tstampz, avgvalz = z.decode("utf-8").split(':')
        list_avg.append([int(tstampz + '000'), float(avgvalz)])

    pipe = r.pipeline()
    pipe.set(r_KEY_DASH_BTC_AVG_HISTORY, list_avg)
#    pipe.set(r_KEY_DASH_BTC_MIN_HISTORY, list_min)
#    pipe.set(r_KEY_DASH_BTC_MAX_HISTORY, list_max)
    response = pipe.execute()

def make_ticker():
    ticker = {}
    ticker['totalbc']       = int(r.get(r_KEY_TOTALBC))
    ticker['btcusd']        = json.loads(r.get(r_KEY_BTC_PRICE))
    ticker['btcusd_stamp']  = json.loads(r.get(r_KEY_BTC_PRICE_TSTAMP))
    ticker['dashbtc']       = json.loads(r.get(r_KEY_DASH_BTC_PRICE))
    ticker['dashbtc_stamp'] = json.loads(r.get(r_KEY_DASH_BTC_PRICE_TSTAMP))
    ticker['dashusd']       = json.loads(r.get(r_KEY_DASH_USD_PRICE))
    ticker['dashusd_stamp'] = json.loads(r.get(r_KEY_DASH_USD_PRICE_TSTAMP))
#
    pipe = r.pipeline()
    pipe.set(r_KEY_TICKER, json.dumps(ticker))
    response = pipe.execute()

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
epoch1minlast = epoch00 - (86400 * 1)
epoch5minlast = epoch1minlast - (86400 * 7)

#---------------------
#
try:
    check_redis()

except Exception as e:
    print(e.args[0])

try:
    get_data()
    make_ticker()

except Exception as e:
    print(e.args[0])

except KeyboardInterrupt:
    sys.exit()

