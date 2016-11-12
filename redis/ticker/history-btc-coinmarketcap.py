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
from config.rkeys import r_SS_BTC_USD_24H_HISTORY

def make_request():
    URL        = "https://api.coinmarketcap.com/v1/datapoints/bitcoin/"
    USERAGET   = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers    = {'user-agent': USERAGET}

    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == requests.codes.ok:
            with open(filetow, 'w') as fp:
                json.dump(response.json(), fp)

    except requests.exceptions.RequestException:
        print(e.args[0])
        sys.exit(1)

    except Exception as e:
        print(e.args[0])
        sys.exit(1)


def getload():
    with open(filetow) as data_file:
        data = json.load(data_file)

    for x in data['price_usd']:
        date = int(x[0] / 1000)
        Avg  = x[1]

        # redis
        try:
            pipe = r.pipeline()
            pipe.zadd(r_SS_BTC_USD_24H_HISTORY, date, str(date) + ':' + str(Avg))
            response = pipe.execute()

        except Exception as e:
            print(e.args[0])
            sys.exit()


#-----------
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

#-------------------------------------------------------------------
# FILE TO SAVE
filetow = 'btc_coinmarketcap_history.log'

print('Keys is : %s' % r_SS_BTC_USD_24H_HISTORY)

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

print(r.zcard(r_SS_BTC_USD_24H_HISTORY))
name = input("Do you want delete key first: [Yes/No] ")
if name == 'Yes':
    r.delete(r_SS_BTC_USD_24H_HISTORY)
    print(r.zcard(r_SS_BTC_USD_24H_HISTORY))
else:
    sys.exit()

#
try:

    try:
        check_redis()

    except Exception as e:
        print(e.args[0])


    try:
        make_request()
        pass

    except Exception as e:
        print(e.args[0])
        sys.exit()


    try:
        getload()

    except Exception as e:
        print(e.args[0])
        sys.exit()

except Exception as e:
    print(e.args[0])
    sys.exit()

except KeyboardInterrupt:
    sys.exit()

