import os
os.system("sudo hping3 -c 2000 -S -w 64 -d 120 -p 80 --faster --rand-source 127.0.0.1")
