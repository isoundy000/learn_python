import redis
import json, traceback

configs=["server", "db", "cmd", "global"]
rs = redis.StrictRedis(host='127.0.0.1', port=7979, db=0)
for c in configs:
    f = c+".json"
    try:
        js = json.loads(open(f, "r").read())
        jstr = json.dumps(js)
        rs.set("freetime:"+c, jstr)
    except:
        print "parse", f, "error!"
        traceback.print_exc()
