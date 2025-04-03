from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
import login_with_selenium as login

def scrape_schedule(driver, username, log):
    # Build initial user profile via CAS using user login from .env
    user_profile = login.get_user_cas_data(driver, log)
    print(user_profile)

    # Go to Webreg and wait for page to load
    driver.get("https://sims.rutgers.edu/webreg/chooseSemester.htm?login=cas")
    time.sleep(2)  # wait for the page to load internally
    driver.get("https://sims.rutgers.edu/webreg/viewScheduleByCourse.htm")
    driver.find_element(By.CLASS_NAME, "btn-submit").click()
    time.sleep(2)  # wait for the page to load internally
    driver.save_screenshot(os.path.join(os.getcwd(), f"{username}_schedule.png"))
    # PROOF OF CONCEPT: WE HAVE REACHED THE SCHEDULE PAGE!!!

    # Now let's scrape degree navigator for fun

def main():
    login.scrape(scrape_schedule, username="am3606", log=True)

if __name__ == "__main__":
    main()
