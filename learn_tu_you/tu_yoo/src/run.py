#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/4


from datetime import datetime


def main():
    import sys
    if len(sys.argv) < 5:
        print "Usage:pypy run.py <server_id> <config_redis_ip> <config_redis_port> <config_redis_dbid>"
        print "Currentn command line is :", sys.argv
        return

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'sys.path=', sys.path
    try:
        import time
        t1 = time.time()
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'initepollreactor begin'
        # from twisted.internet import epollreactor
        # epollreactor.install()
        from twisted.internet import reactor
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'initepollreactor done, use time ', time.time() - t1, 'reactor=', reactor
    except Exception, e:
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'reactor install error !', e
    # set default coding to utf8...
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'getdefaultencoding=', sys.getdefaultencoding()
    if sys.getdefaultencoding().lower() != "utf-8":
        reload(sys)
        sys.setdefaultencoding("utf-8")
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'setdefaultencoding to utf-8'

    _server_id = sys.argv[1]
    _conf_ip = sys.argv[2]
    _conf_port = int(sys.argv[3])
    _conf_dbid = int(sys.argv[4])

    import freetime.entity.service as ftsvr
    import poker.protocol.startup as pstartup
    ftsvr.run(
        config_redis=(_conf_ip, _conf_port, _conf_dbid),
        server_id=_server_id,
        init_fun=pstartup.initialize,
        protocols=pstartup
    )


if __name__ == '__main__':
    main()