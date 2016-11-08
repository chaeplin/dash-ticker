#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import simplejson as json
import redis
from datetime import datetime
import time
from statistics import mean

from ISStreamer.Streamer import Streamer
from twython import Twython, TwythonError

from config.role import HOST_ROLE, MASTER_SETINEL_HOST, MASTER_REDIS_MASTER, SLAVE_SETINEL_HOST, SLAVE_REDIS_MASTER
from config.twitter import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, ISS_BUCKET_NAME, ISS_BUCKET_KEY, ISS_BUCKET_AKEY, ISS_PREFIX_BTCUSD
from config.rkeys import r_KEY_BTC_PRICE, r_SS_BTC_PRICE 

def make_request(URL, CHECK_STRRING):
    USERAGET = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers = {'user-agent': USERAGET}    

    try:
        response = requests.get(URL, headers=headers, timeout=(2,5))
        if response.status_code == requests.codes.ok and len(response.text) > 2:
            if isinstance(response.json(), list):
                if CHECK_STRRING in response.json()[0]:
                    return response.json()[0]

            else:
                if CHECK_STRRING in response.json():
                    return response.json()

    except requests.exceptions.RequestException:
        return None

def get_bitfinex():
    URL           = 'https://api.bitfinex.com/v1/pubticker/BTCUSD'
    CHECK_STRRING = 'last_price'
    exsymbol      = 'bitfinex'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        value = round(float(rawjson[CHECK_STRRING]), 2)
        if value > 0:
            btcusd[exsymbol] = value

def get_gdax():
    URL           = 'https://api.gdax.com/products/BTC-USD/ticker'
    CHECK_STRRING = 'price'
    exsymbol      = 'gdax'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        value = round(float(rawjson[CHECK_STRRING]), 2)
        if value > 0:
            btcusd[exsymbol] = value

def get_btce():
    URL           = 'https://btc-e.com/api/3/ticker/btc_usd'
    CHECK_STRRING = 'btc_usd'
    exsymbol      = 'btce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        value = round(float(rawjson[CHECK_STRRING]['last']), 2)
        if value > 0:
            btcusd[exsymbol] = value

def get_xbtce():
    URL           = 'https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/ticker/BTCUSD'
    CHECK_STRRING = 'Symbol'
    exsymbol      = 'xbtce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if rawjson[CHECK_STRRING] == 'BTCUSD':
            value = round(float(rawjson['BestBid']), 2)
            if value > 0:
                btcusd[exsymbol] = value

def get_bitstamp():
    URL           = 'https://www.bitstamp.net/api/v2/ticker_hour/btcusd/'
    CHECK_STRRING = 'last'
    exsymbol      = 'bitstamp'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        value = round(float(rawjson[CHECK_STRRING]), 2)
        if value > 0:
            btcusd[exsymbol] = value

def get_okcoin():
    URL           = 'https://www.okcoin.com/api/v1/ticker.do?exsymbol=btc_usd'
    CHECK_STRRING = 'ticker'
    exsymbol      = 'okcoin'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        value = round(float(rawjson['ticker']['last']), 2)
        if value > 0:
            btcusd[exsymbol] = value


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

#---------------------------------
def check_update():
    cur_time = time.time()
    lastupdate = json.loads(r.get(r_KEY_BTC_PRICE))['tstamp']

    if cur_time - lastupdate > 270 and cur_time - lastupdate < 330:
        twitter.update_status(status='ticker btc has prob - 1')

    if cur_time - lastupdate > 570 and cur_time - lastupdate < 630:
        twitter.update_status(status='ticker btc has prob - 2')

#---------------------------------
streamer = Streamer(bucket_name=ISS_BUCKET_NAME, bucket_key=ISS_BUCKET_KEY, access_key=ISS_BUCKET_AKEY, buffer_size=50)
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

#
btcusd = {}
now = datetime.now()
epoch00 = int(time.mktime(now.timetuple())) - now.second

#
try:
    check_redis()

except Exception as e:
    print(e.args[0])

try:
    check_update()
    get_bitfinex()
    get_gdax()
    get_btce()
    get_xbtce()
    get_bitstamp()
    get_okcoin()

    l_btcusd = []
    for key in btcusd:
        l_btcusd.append(btcusd[key])

    btcusd['avg'] = round(mean(sorted(l_btcusd)[1:-1]), 2)
    btcusd['tstamp'] = epoch00

    # redis
    try:
        pipe = r.pipeline()
        pipe.set(r_KEY_BTC_PRICE, json.dumps(btcusd, sort_keys=True))
        pipe.zadd(r_SS_BTC_PRICE, epoch00, str(epoch00) + ':' + str(btcusd['avg']))
        response = pipe.execute()

    except Exception as e:
        print(e.args[0])
        pass

    # ISS
    try:
        streamer.log_object(btcusd, key_prefix=ISS_PREFIX_BTCUSD, epoch=epoch00)
        streamer.flush()
        streamer.close()

    except Exception as e:
        print(e.args[0])
        pass

except Exception as e:
    print(e.args[0])

except KeyboardInterrupt:
    sys.exit()

