#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io, os, sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.decode('utf-8'))
import simplejson as json
import datetime
import time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# --- change 
# rpc
rpcuser     = 'dashmnb'
rpcpassword = 'iamok'
#rpcbindip   = '163.44.167.237'
rpcbindip   = 'test.stats.dash.org'
rpcport     = 587


def checksynced():
    try:
        synced = access.mnsync('status')
        return (synced['IsSynced'])


    except JSONRPCException as e:
        print(e.args)
        sys.exit()

    except Exception as e:
        print(e.args)
        sys.exit()

serverURL = 'https://' + rpcuser + ':' + rpcpassword + '@' + rpcbindip + ':' + str(rpcport)
access = AuthServiceProxy(serverURL)

# testnet
# uncomment below to ses mnsync is not allowed
#checksynced()

txhash = b'4a1f3f89d95dd162e30399386dd7748c7fa02ec958320f4542923cf3a63fde48'
tx = access.getrawtransaction(_b(txhash), 1)

print(tx)

address = 'ydWWT8kCMij5LhMMGVzBDyXZ9j3ZPkkuiN'

listunspent = access.listunspent(0, 99999, [address])
print(listunspent)