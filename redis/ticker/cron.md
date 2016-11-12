```
* * * * * test -x ~/dash-ticker/redis/ticker/ticker-btc.py && ~/dash-ticker/redis/ticker/ticker-btc.py >> ~/dash-ticker/logs/ticker-btc.log
* * * * * test -x ~/dash-ticker/redis/ticker/ticker-dash.py && ~/dash-ticker/redis/ticker/ticker-dash.py >> ~/dash-ticker/logs/ticker-dash.log
* * * * * test -x ~/dash-ticker/redis/ticker/ticker-update-dash-btc-graph.py && ~/dash-ticker/redis/ticker/ticker-update-dash-btc-graph.py  >> ~/dash-ticker/logs/ticker-update-dash-btc-graph.log
* * * * * test -x ~/dash-ticker/redis/ticker/ticker-update-dash-usd-graph.py && ~/dash-ticker/redis/ticker/ticker-update-dash-usd-graph.py  >> ~/dash-ticker/logs/ticker-update-dash-usd-graph.log
*/5 * * * * test -x ~/dash-ticker/redis/ticker/ticker-update-dash-btc-5min.py && ~/dash-ticker/redis/ticker/ticker-update-dash-btc-5min.py >> ~/dash-ticker/logs/ticker-update-dash-btc-5min.log
01 * * * * test -x ~/dash-ticker/redis/ticker/ticker-explorer.py && ~/dash-ticker/redis/ticker/ticker-explorer.py >> ~/dash-ticker/logs/ticker-explorer.log
01 * * * * test -x ~/dash-ticker/redis/ticker/ticker-update-dash-btc-1h.py && ~/dash-ticker/redis/ticker/ticker-update-dash-btc-1h.py >> ~/dash-ticker/logs/ticker-update-dash-btc-1h.log
```
