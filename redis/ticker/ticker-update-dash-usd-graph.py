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

# r_KEY_DASH_BTC_AVG_HISTORY

# r_KEY_DASH_USD_AVG_HISTORY
# r_SS_BTC_USD_24H_HISTORY


def get_btc_period():
    stop  = int(r.zrange(r_SS_BTC_USD_24H_HISTORY, -1, -1, withscores=True)[0][1])
    start = int(r.zrange(r_SS_BTC_USD_24H_HISTORY, 0, 0, withscores=True)[0][1])
    return start, stop

def get_dash_btc_avg_history():

    list_avg = []

    result = json.loads(r.get(r_KEY_DASH_BTC_AVG_HISTORY))
    for x in result:
        datestamp = int(x[0] /1000)
        dashavgbtc    = x[1]
        if datestamp >= btc_history_start and datestamp <= btc_history_stop:
            btcusd_price = r.zrangebyscore(r_SS_BTC_USD_24H_HISTORY, datestamp - 172800, datestamp + 86400, withscores=False)
            tempval = []
            for y in btcusd_price:
                epoch_datetime, val = y.decode("utf-8").split(':')
                tempval.append(float(val))

            btcavgval = round(mean(sorted(tempval)), 2)

        else:
            btcusd_price = r.zrangebyscore(r_SS_BTC_PRICE, datestamp - 3600, datestamp + 3600, withscores=False)
            tempval = []
            for y in btcusd_price:
                epoch_datetime, val = y.decode("utf-8").split(':')
                tempval.append(float(val))

            btcavgval = round(mean(sorted(tempval)), 2)

        dashavgusd = round(btcavgval*dashavgbtc, 2)
        list_avg.append([int(str(datestamp) + '000'), float(dashavgusd)])

    pipe = r.pipeline()
    pipe.set(r_KEY_DASH_USD_AVG_HISTORY, list_avg)
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

try:
    check_redis()

except Exception as e:
    print(e.args[0])


try:
    btc_history_start, btc_history_stop = get_btc_period()
    get_dash_btc_avg_history()

except Exception as e:
    print(e.args[0])

except KeyboardInterrupt:
    sys.exit()

