from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from dotenv import load_dotenv
import json

# Wait for all redirects to complete
def wait_for_redirects_to_finish(driver, max_wait=30, check_interval=0.5):
    # Store the initial URL
    previous_url = driver.current_url
    # Time elapsed
    elapsed = 0
    
    while elapsed < max_wait:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Get current URL after page load
        current_url = driver.current_url
        
        # If URL hasn't changed, wait a bit and check again
        if current_url == previous_url:
            time.sleep(check_interval)
            elapsed += check_interval
            
            # Check if URL is still the same after waiting
            if driver.current_url == previous_url:
                # If no change after waiting, assume redirects are done
                return True
        else:
            # URL changed, update previous_url and reset elapsed time
            previous_url = current_url
            elapsed = 0
            
    # Timeout reached
    return False

URL = {
    'cas': 'https://cas.rutgers.edu',
    'dn': 'https://dn.rutgers.edu',
    'webreg': 'https://sims.rutgers.edu/webreg/chooseSemester.htm?login=cas'
}

# Gets the user login from .env, if present
def get_user_login():
    user_login = None
    try:
        user_login = {
            'username': os.getenv('USERNAME'),
            'password': os.getenv('PASSWORD')
        }
    finally:
        return user_login

# Reads the user cookies from cookies.json, if present
def read_user_cookies(username):
    try:
        with open(f"{username}_cookies.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None  # no cookies.json file

# Writes the user cookies to cookies.json
def write_user_cookies(username, cookies_dict):
    with open(f"{username}_cookies.json", "w") as file:
        json.dump(cookies_dict, file, indent=2)

# Checks if the driver is authenticated
def is_authenticated(driver, log=False, website_url=URL['cas']):
    driver.get(website_url)  # reload the page to see if login was successful
    try:
        driver.find_element(By.CLASS_NAME, "accesskey").text
        return False  # authentication failed; back to login page
    except NoSuchElementException:
        return True   # authentication succeeded

# Given cookies, authenticates the user
def can_authenticate_with_cookies(driver, username, log=False, website_url=URL['cas']):
    driver.delete_all_cookies()
    driver.get(website_url)  # load the webpage

    # Reads in the cookies and adds them to the browser
    cookies = read_user_cookies(username)
    if cookies:
        for cookie in cookies.values(): driver.add_cookie(cookie)
    else: return False  # no cookies.json file
    
    if is_authenticated(driver, log, website_url):
        return cookies
    else:
        driver.delete_all_cookies()  # cookies are incorrect; delete them
        return False

def authenticate_service(driver, user=None, username=None, log=False, website_url=URL['cas']):
    """
    Authenticates the user into the Rutgers service given by the website_url.
    First, tries to authenticate with cookies, if they exist. If the cookies
    do not exist or are invalid, grabs the cookies and returns them.
    
    Args:
        driver: Selenium webdriver instance
        user: Dictionary containing username and password
        log: Boolean to enable/disable logging
        website_url: URL of the service to authenticate
        
    Returns:
        driver, cookies if authentication succeeds; None, None if cookie-based
        authentication fails; False, None if login fails
    """
    
    # If cookies exist and are valid, skip authentication
    cookies = can_authenticate_with_cookies(driver, username, log, website_url)
    if cookies:
        if log: print("Grabbed cookies. Service loaded!")
        return driver, cookies
    elif not user and username:
        user = get_user_login()
        if user == None or user['username'] != username:
            if log: print("Cookies expired or were not found. Require " +
                        f"username and password again for {username}.")
            return None, None

    # Navigate to the login page
    driver.get(website_url)
    if log: print("Authentication page accessed.")

    # Enter user login info
    username_selector = '#username'
    password_selector = '#password'
    login_button_selector = '#fm1 > input.btn.btn-block.btn-submit'
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, username_selector))
    )
    
    driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(user['username'])
    driver.find_element(By.CSS_SELECTOR, password_selector).send_keys(user['password'])
    driver.find_element(By.CSS_SELECTOR, login_button_selector).click()
    
    if log: print('Login information entered.')

    # TODO: HANDLE INCORRECT INPUT OF NETID.
    # Assume login info is correct ... (for now)

    # Wait for redirects to complete
    if not wait_for_redirects_to_finish(driver):
        if log: print("Timeout waiting for redirects to complete")
    
    # Wait for the Duo header to appear
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#header-text'))
    )
    
    header_text = driver.find_element(By.CSS_SELECTOR, '#header-text').text
    # if log: print(f"HEADER TEXT: {header_text}")
    
    if 'Duo' in header_text:
        if log: print("Duo Push notification sent!")
    
    # Wait for either success or failure selector
    try:
        # First check if trust browser element appears (success case)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#trust-this-browser-label'))
        )
        
        if log: print('Duo Push approved. Loading main page.')
        
        # Click the trust browser button
        trust_browser_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#trust-browser-button'))
        )
        trust_browser_button.click()
        
        if log: print("Clicked the trust-browser button.")
        
        # Wait until the "Success!" label disappears
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#push-success-label"))
        )
        
        if log: print("Service loaded!")

        # Grab the TGC and JSESSIONID cookies and write them to cookies.json
        cookies = driver.get_cookies()
        cookies_dict = {cookie["name"]: cookie for cookie in cookies}
        write_user_cookies(user['username'], cookies_dict)
        
        return driver, cookies
        
    except TimeoutException:
        # Check if error view appeared
        if driver.find_element(By.CSS_SELECTOR, '#error-view-header-text'):
            print("Duo Push failed. Login again.")
            return False, None
        else:
            print("Unexpected error during authentication.")
            return False, None

def get_user_cas_data(driver, log=False):
    """
    Scrapes basic user data by authenticating the user into CAS.
    
    Args:
        driver: Selenium webdriver instance
        user: Dictionary containing username and password
        log: Boolean to enable/disable logging
        
    Returns:
        Dictionary containing user profile information
    """

    # Map attribute textContent on CAS to attr names
    attr_to_name = {
        'cn': 'fullName',
        'givenName': 'name',
        'rutgersEduStudentLocation': 'campus',
        'rutgersEduRUID': 'RUID',
        'rutgersEduStudentUnit': 'unitName',
        'rutgersEduStudentUnitCode': 'unitCode',
        'uid': 'netID',
        'mail': 'email'
    }
    
    # Scrape CAS service main page to get key-value pairs for user profile
    selector = '#attributesTable > tbody > tr > td:nth-child(1) > code > kbd'
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    
    user_profile = {}
    for i, element in enumerate(elements, 1):
        if not element or not element.text:
            continue
            
        attr = attr_to_name.get(element.text)
        if not attr:
            continue
            
        value_selector = f'#attributesTable > tbody > tr:nth-child({i}) > td:nth-child(2) > code > kbd'
        value_element = driver.find_element(By.CSS_SELECTOR, value_selector)
        
        if not value_element or not value_element.text:
            continue
            
        value = value_element.text[1:-1]  # Remove quotes
        user_profile[attr] = value
    
    return user_profile

# Run a web scraping function
def scrape(fn, username=None, log=False, website_url=URL['cas']):
    # Load environment variables
    load_dotenv()
    user_login = None
    if not username: user_login = get_user_login()
    
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the line below to run in headless mode
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1280,720")
    # chrome_options.add_argument("--headless")  # Enables headless mode
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Authenticate the user if not already authenticated
        if user_login and not username: username = user_login['username']
        if not is_authenticated(driver, website_url=website_url):
            authenticated_driver, _ = authenticate_service(driver, user=user_login,
                                       username=username, log=True)
            if authenticated_driver == False or authenticated_driver == None:
                raise SystemExit
        # Run the web scraping function
        fn(driver, username, log=log)
            
    finally:
        # Close the browser
        driver.quit()

# Demo function
def my_scraping_function(driver, username, log):
    # Build initial user profile via CAS using user login from .env
    user_profile = get_user_cas_data(driver, log)
    print(user_profile)
    # Go to my.rutgers.edu and wait for page to load
    driver.get("https://cas.rutgers.edu/login?service=https://my.rutgers.edu/casShell/ngLogin")
    time.sleep(5)  # wait for the page to load internally
    driver.save_screenshot(os.path.join(os.getcwd(), f"{username}_dashboard.png"))

def main():
    # Run scrape with a lambda function
    scrape(my_scraping_function, username="pr572")

if __name__ == "__main__":
    main()
