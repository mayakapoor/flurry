from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def clearAllAlerts(driver):
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present(), "a")
        alert = driver.switch_to.alert
        alert.accept()
        while True: # Iterates until a timeout exception happens
            WebDriverWait(driver, 0.5).until(EC.alert_is_present(), "b")
            alert = driver.switch_to.alert
            alert.accept()
    except TimeoutException:
        pass
