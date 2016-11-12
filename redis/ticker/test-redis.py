#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import simplejson as json
import redis

from config.role import HOST_ROLE, MASTER_SETINEL_HOST, MASTER_REDIS_MASTER, SLAVE_SETINEL_HOST, SLAVE_REDIS_MASTER
from config.rkeys import * 

import pprint


# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

pp = pprint.PrettyPrinter(indent=4)

#r.flushdb()
#sys.exit()

#r.delete(r_SS_DASH_BTC_1H_HISTORY)
#sys.exit()

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

check_redis()


try:

#
    print('r_KEY_DASH_BTC_PRICE')
    pp.pprint(r.get(r_KEY_DASH_BTC_PRICE))

    print('r_KEY_DASH_USD_PRICE')
    pp.pprint(r.get(r_KEY_DASH_USD_PRICE))

    print('r_KEY_BTC_PRICE')
    pp.pprint(r.get(r_KEY_BTC_PRICE))

    print('r_SS_DASH_BTC_PRICE')
    pp.pprint(r.zrange(r_SS_DASH_BTC_PRICE, -10, -1, withscores=True))

    print('r_SS_DASH_USD_PRICE')
    pp.pprint(r.zrange(r_SS_DASH_USD_PRICE, -10, -1, withscores=True))

    print('r_SS_BTC_PRICE')
    pp.pprint(r.zrange(r_SS_BTC_PRICE, -10, -1, withscores=True))

    print('r_SS_DASH_BTC_5MIN_HISTORY')
    pp.pprint(r.zrange(r_SS_DASH_BTC_5MIN_HISTORY, -10, -1, withscores=True))

    print('r_SS_BTC_USD_24H_HISTORY')
    pp.pprint(r.zrange(r_SS_BTC_USD_24H_HISTORY, -10, -1, withscores=True))

    print('r_SS_DASH_BTC_1H_HISTORY')
    pp.pprint(r.zrange(r_SS_DASH_BTC_1H_HISTORY, -10, -1, withscores=True))

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit(1)
