from selenium import webdriver
import util.alerthandling as ah
from util.driversetup import DRIVER

global DRIVER

#DRIVER = ds.setupDRIVER()
DRIVER.get("http://127.0.0.1/vulnerabilities/xss_s/")

xss_stored_name = "/html/body/div/div[3]/div/div/form/table/tbody/tr[1]/td[2]/input"
xss_stored_message = "/html/body/div/div[3]/div/div/form/table/tbody/tr[2]/td[2]/textarea"
xss_stored_submit = "/html/body/div/div[3]/div/div/form/table/tbody/tr[3]/td[2]/input[1]"

ah.clearAllAlerts(DRIVER)
# An exception gets thrown somewhere around here if an alert is open
DRIVER.find_element_by_xpath(xss_stored_name).send_keys("Test")
DRIVER.find_element_by_xpath(xss_stored_message).send_keys("<script>alert('This is stored XSS')</script>")

DRIVER.find_element_by_xpath(xss_stored_submit).click()
ah.clearAllAlerts(DRIVER)
#driver.close()
