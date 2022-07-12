import psutil
import subprocess as sp
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

DRIVER = None

def login(driver):
    driver.get("http://127.0.0.1/login.php")# -*- coding: utf-8 -*-
    login_username = "/html/body/div/div[2]/form/fieldset/input[1]"
    login_password = "/html/body/div/div[2]/form/fieldset/input[2]"
    login_button = "/html/body/div/div[2]/form/fieldset/p/input"

    driver.find_element_by_xpath(login_username).send_keys("admin")
    driver.find_element_by_xpath(login_password).send_keys("password")

    button = driver.find_element_by_xpath(login_button)
    driver.execute_script("arguments[0].click();", button)

def security(driver):
    #set security
    driver.get("http://127.0.0.1/security.php")
    security_dropdown = "/html/body/div/div[3]/div/form/select"
    security_submit = "/html/body/div/div[3]/div/form/input[1]"

    select = Select(driver.find_element_by_xpath(security_dropdown))
    select.select_by_visible_text('Low')
    driver.find_element_by_xpath(security_submit).click()
    # End DVWA set to low

def setupDriver():

    SERVER_RUNNING = False
    for process in psutil.process_iter():
        if '/opt/lampp/bin/' in process.name():
            SERVER_RUNNING = True
            print("Web server is running, connection now...")
    if not SERVER_RUNNING:
        print("Starting Apache Web Server...")
        startCommand = "sudo /opt/lampp/lampp start"
        proc = sp.Popen(startCommand.split(), stdout=sp.PIPE)
        output, error = proc.communicate()
        time.sleep(3)


    chromeOptions = Options()
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-dev-shm-using")
    chromeOptions.add_argument("--autoplay-policy=no-user-gesture-required")
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", chrome_options=chromeOptions)
    login(driver)
    security(driver)
    global DRIVER
    DRIVER = driver
    print("Driver initialized.")
    return driver
