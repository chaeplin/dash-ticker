#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import simplejson as json
import redis
from datetime import datetime
import time

from config.role import HOST_ROLE, MASTER_SETINEL_HOST, MASTER_REDIS_MASTER, SLAVE_SETINEL_HOST, SLAVE_REDIS_MASTER
from config.rkeys import r_KEY_TOTALBC

def get_gettotalbc():
    URL = 'https://explorer.dash.org/chain/Dash/q/totalbc'
    USERAGET = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers = {'user-agent': USERAGET}

    try:
        response = requests.get(URL, headers=headers, timeout=(2,5))
        if response.status_code == requests.codes.ok and len(response.text) > 2:
            totalbc = int(float(response.text))
            if totalbc > 0:
                return totalbc

    except requests.exceptions.RequestException:
        return None

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

#--------------
def check_update():
    cur_time = time.time()
    lastupdate = json.loads(r.get(r_KEY_DASH_BTC_PRICE))['tstamp']

    if cur_time - lastupdate > 270 and cur_time - lastupdate < 330:
        twitter.update_status(status='ticker dash has prob -1')

    if cur_time - lastupdate > 570 and cur_time - lastupdate < 630:
        twitter.update_status(status='ticker dash has prob -2')


# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

now = datetime.now()
epoch00 = int(time.mktime(now.timetuple())) - now.second

#
try:
    check_redis()

except Exception as e:
    print(e.args[0])

try:
    totalbc = get_gettotalbc()
    if totalbc:
    # redis
        try:
            pipe = r.pipeline()
            pipe.set(r_KEY_TOTALBC, totalbc)
            response = pipe.execute()

        except Exception as e:
            print(e.args[0])
            pass    

    else:
        print('x')


except Exception as e:
    print(e.args[0])

except KeyboardInterrupt:
    sys.exit()


