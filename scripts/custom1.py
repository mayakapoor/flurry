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
DRIVER.find_element_by_xpath(xss_stored_name).send_keys("r/shitposting automod")
DRIVER.find_element_by_xpath(xss_stored_message).send_keys("""Sir I am 16 weeks old in my mom's womb. I am unsure of whether my mother is planning to get me aborted or keep me. On the sad off chance that she decides to let me live, I am planning to crack JEE and get a selection in IIT Delhi. I am however worried that I won't be able to finish the portions by the time I am born. I would like to acknowledge that I am a fast learner, I have learnt basic concepts of class 10 maths and science already like real numbers, linear equations, electric current, optics, basic nomenclature, etc. I have also skimmed through FIITJEE material for 11th such as resonance, P block, s block, SHM, sets and relations, rotational mechanics, vectors, limits and derivatives, etc. within 2 weeks. I am hopefully going to get aborted. But if the odds are not with me then I will have to continue going through the pain of having to study. Note: My brain is still under structural development since I am only 16 fetal weeks old. I am planning to enroll in online coaching class as of now due to lockdown. Is it already too late to start preparing for JEE?? My mom's friends' kids are younger and have completed entire 11th and 12th syllabus and are revising important concepts with one shot videos on YouTube. Pls help.

I am a bot, and this action was performed automatically. Please contact the moderators of this subreddit if you have any questions or concerns.""")

DRIVER.find_element_by_xpath(xss_stored_submit).click()
ah.clearAllAlerts(DRIVER)
