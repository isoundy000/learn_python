import os
import time
os.system("ps -aux| grep 'supervisor'|awk '{print $2}'|sudo xargs kill -9")
time.sleep(1)
os.system("ps -aux| grep 'celery'|awk '{print $2}'|sudo xargs kill -9")
time.sleep(2)
os.system("sudo supervisord -c /etc/supervisor/supervisord.conf")
time.sleep(2)
os.system("sudo service apache2 restart")
time.sleep(3)
print "Services restart successfully"
