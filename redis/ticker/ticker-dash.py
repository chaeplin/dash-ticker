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
from config.twitter import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, ISS_BUCKET_NAME, ISS_BUCKET_KEY, ISS_BUCKET_AKEY, ISS_PREFIX_DASHBTC, ISS_PREFIX_DASHUSD, ISS_PREFIX_DASHUSD_TT, ISS_PREFIX_DASHUSD_TS, ISS_PREFIX_DASHBTC_TT, ISS_PREFIX_DASHBTC_TS
from config.rkeys import r_KEY_DASH_BTC_PRICE, r_KEY_DASH_USD_PRICE, r_SS_DASH_BTC_PRICE, r_SS_DASH_USD_PRICE

def get_espochtime():
    return time.time()

def get_tooktime(START):
    return (time.time() - START)

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

def get_poloniex():
    START         = get_espochtime()
    URL           = 'https://poloniex.com/public?command=returnTicker'
    CHECK_STRRING = 'BTC_DASH'
    SECON_STRRING = 'USDT_DASH'
    exsymbol      = 'poloniex'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if SECON_STRRING in rawjson:
            valbtc = round(float(rawjson[CHECK_STRRING]['last']), 5)
            valusd = round(float(rawjson[SECON_STRRING]['last']), 2)
            if valbtc > 0 and valusd > 0:
                dashbtc[exsymbol] = valbtc
                dashusd[exsymbol] = valusd
                dashbtc_ttook[exsymbol]  = dashusd_ttook[exsymbol] =  get_tooktime(START)
                dashbtc_tstamp[exsymbol] = dashusd_tstamp[exsymbol] = epoch00

def get_exmo():
    START         = get_espochtime()
    URL           = 'https://api.exmo.com/v1/ticker/'
    CHECK_STRRING = 'DASH_BTC'
    SECON_STRRING = 'DASH_USD'
    exsymbol      = 'exmo'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if SECON_STRRING in rawjson:
            valbtc = round(float(rawjson[CHECK_STRRING]['last_trade']), 5)
            valusd = round(float(rawjson[SECON_STRRING]['last_trade']), 2)
            if valbtc > 0 and valusd > 0:
                dashbtc[exsymbol] = valbtc
                dashusd[exsymbol] = valusd
                dashbtc_ttook[exsymbol]  = dashusd_ttook[exsymbol] =  get_tooktime(START)
                dashbtc_tstamp[exsymbol] = dashusd_tstamp[exsymbol] = epoch00


def get_bittrex():
    START         = get_espochtime()
    URL           = 'https://bittrex.com/api/v1.1/public/getticker?market=btc-dash'
    CHECK_STRRING = 'success'
    exsymbol      = 'bittrex'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if rawjson[CHECK_STRRING] == True:
            valbtc = round(float(rawjson['result']['Last']), 5)
            if valbtc > 0:
                dashbtc[exsymbol] = valbtc
                dashbtc_ttook[exsymbol] =  get_tooktime(START)
                dashbtc_tstamp[exsymbol] = epoch00

def get_btcebtc():
    START         = get_espochtime()
    URL           = 'https://btc-e.com/api/3/ticker/dsh_btc'
    CHECK_STRRING = 'dsh_btc'
    exsymbol      = 'btce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        valbtc = round(float(rawjson[CHECK_STRRING]['last']), 5)
        if valbtc > 0:
            dashbtc[exsymbol] = valbtc
            dashbtc_ttook[exsymbol] =  get_tooktime(START)
            dashbtc_tstamp[exsymbol] = epoch00


def get_btceusd():
    START         = get_espochtime()
    URL           = 'https://btc-e.com/api/3/ticker/dsh_usd'
    CHECK_STRRING = 'dsh_usd'
    exsymbol      = 'btce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        valusd = round(float(rawjson[CHECK_STRRING]['last']), 2)
        if valusd > 0:
            dashusd[exsymbol] = valusd
            dashusd_ttook[exsymbol] =  get_tooktime(START)
            dashusd_tstamp[exsymbol] = epoch00


def get_xbtcebtc():
    START         = get_espochtime()
    URL           = 'https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/ticker/DSHBTC'
    CHECK_STRRING = 'Symbol'
    exsymbol      = 'xbtce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if rawjson[CHECK_STRRING] == 'DSHBTC':
            valbtc = round(float(rawjson['BestBid']), 5)
            if valbtc > 0:
               dashbtc[exsymbol] = valbtc 
               dashbtc_ttook[exsymbol] =  get_tooktime(START)
               dashbtc_tstamp[exsymbol] = epoch00

def get_xbtceusd():
    START         = get_espochtime()
    URL           = 'https://cryptottlivewebapi.xbtce.net:8443/api/v1/public/ticker/DSHUSD'
    CHECK_STRRING = 'Symbol'
    exsymbol      = 'xbtce'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        if rawjson[CHECK_STRRING] == 'DSHUSD':
            valusd = round(float(rawjson['BestBid']), 2)
            if valusd > 0:
                dashusd[exsymbol] = valusd
                dashusd_ttook[exsymbol] =  get_tooktime(START)
                dashusd_tstamp[exsymbol] = epoch00

def get_yobit():
    START         = get_espochtime()
    URL           = 'https://yobit.net/api/2/dash_btc/ticker'
    CHECK_STRRING = 'ticker'
    exsymbol      = 'yobit'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        valbtc = round(float(rawjson['ticker']['last']), 5)
        if valbtc > 0:
            dashbtc[exsymbol] = valbtc    
            dashbtc_ttook[exsymbol] =  get_tooktime(START)
            dashbtc_tstamp[exsymbol] = epoch00


def get_livecoinbtc():
    START         = get_espochtime()
    URL           = 'https://api.livecoin.net/exchange/ticker?currencyPair=DASH/BTC'
    CHECK_STRRING = 'last'
    exsymbol      = 'livecoin'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        valbtc = round(float(rawjson[CHECK_STRRING]), 5)
        if valbtc > 0:
            dashbtc[exsymbol] = valbtc
            dashbtc_ttook[exsymbol] =  get_tooktime(START)
            dashbtc_tstamp[exsymbol] = epoch00

def get_livecoinusd():
    START         = get_espochtime()
    URL           = 'https://api.livecoin.net/exchange/ticker?currencyPair=DASH/USD'
    CHECK_STRRING = 'last'
    exsymbol      = 'livecoin'
    rawjson       = make_request(URL, CHECK_STRRING)
    if rawjson:
        valusd = round(float(rawjson[CHECK_STRRING]), 2)
        if valusd > 0:
            dashusd[exsymbol] = valusd
            dashusd_ttook[exsymbol] =  get_tooktime(START)
            dashusd_tstamp[exsymbol] = epoch00

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


#-----------------#
streamer = Streamer(bucket_name=ISS_BUCKET_NAME, bucket_key=ISS_BUCKET_KEY, access_key=ISS_BUCKET_AKEY, buffer_size=50)
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# redis
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.StrictRedis(connection_pool=POOL)

#
dashbtc = {}
dashbtc_ttook = {}
dashbtc_tstamp = {}

dashusd = {}
dashusd_ttook = {}
dashusd_tstamp = {}


now = datetime.now()
epoch00 = int(time.mktime(now.timetuple())) - now.second

#
try:
    check_redis()

except Exception as e:
    print(e.args[0])

try:
    check_update()
    get_poloniex()
    get_exmo()
    get_bittrex()
    get_btcebtc()
    get_btceusd()
    get_xbtcebtc()
    get_xbtceusd()
    get_yobit()
    get_livecoinbtc()
    get_livecoinusd()

    l_dashbtc = []
    for key in dashbtc:
        l_dashbtc.append(dashbtc[key])

    l_dashusd = []
    for key in dashusd:
        l_dashusd.append(dashusd[key])

    dashbtc['avg'] = round(mean(sorted(l_dashbtc)[1:-1]), 5)
    dashusd['avg'] = round(mean(sorted(l_dashusd)[1:-1]), 2)

    #dashbtc['tstamp'] = dashusd['tstamp'] = epoch00
    dashbtc['tstamp'] = dashusd['tstamp'] = int(time.time())
    
    # redis
    try:
        pipe = r.pipeline()
        pipe.set(r_KEY_DASH_BTC_PRICE, json.dumps(dashbtc, sort_keys=True))
        pipe.set(r_KEY_DASH_USD_PRICE, json.dumps(dashusd, sort_keys=True))
        pipe.zadd(r_SS_DASH_BTC_PRICE, epoch00, str(epoch00) + ':' + str(dashbtc['avg']))
        pipe.zadd(r_SS_DASH_USD_PRICE, epoch00, str(epoch00) + ':' + str(dashusd['avg']))
        response = pipe.execute()

    except Exception as e:
        print(e.args[0])
        pass

    # ISS
    try:
        streamer.log_object(dashbtc, key_prefix=ISS_PREFIX_DASHBTC, epoch=epoch00)
        streamer.log_object(dashusd, key_prefix=ISS_PREFIX_DASHUSD, epoch=epoch00)
        streamer.log_object(dashbtc_ttook, key_prefix=ISS_PREFIX_DASHBTC_TT, epoch=epoch00)
        streamer.log_object(dashbtc_tstamp, key_prefix=ISS_PREFIX_DASHBTC_TS, epoch=epoch00)
        streamer.log_object(dashusd_ttook, key_prefix=ISS_PREFIX_DASHUSD_TT, epoch=epoch00)
        streamer.log_object(dashusd_tstamp, key_prefix=ISS_PREFIX_DASHUSD_TS, epoch=epoch00)
        streamer.flush()
        streamer.close()

    except Exception as e:
        print(e.args[0])
        pass

except Exception as e:
    print(e.args[0])

except KeyboardInterrupt:
    sys.exit()

