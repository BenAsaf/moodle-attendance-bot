from selenium import webdriver
from selenium.common import exceptions
import time
import sched


MOODLE_USER_NAME = ""
MOODLE_PASSWORD = ""
MOODLE_HOME_PAGE = "Moodle Address"  # THe moodle main homepage
COURSE_TITLE = "Name of the course as it shows up on the left"  # What course to search for in the list
START_HOUR, START_MINUTE, START_SECS = 16, 0, 0  # Starts at 16:00:00


SLEEP_INTERVAL = 60  # For what duration to sleep in-between attempts (in seconds)


WEBDRIVER_EXECUTABLE_PATH = "./chromedriver"  # Path to the Chrome WebDriver
CHROME_EXECUTABLE_PATH = "/usr/bin/google-chrome"  # Path to the Chrome browser


IS_HEADLESS = True  # Whether or not to display the Chrome GUI.


def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    if IS_HEADLESS:
        options.add_argument("--headless")
    options.binary_location = CHROME_EXECUTABLE_PATH
    browser = webdriver.Chrome(executable_path=WEBDRIVER_EXECUTABLE_PATH, chrome_options=options)
    browser.get(MOODLE_HOME_PAGE)
    return browser


def login_to_moodle(browser):
    # <input type="text" name="username" id="login_username" class="form-control" value="" autocomplete="username">
    user_input = browser.find_element_by_id("login_username")
    user_input.send_keys(MOODLE_USER_NAME)
    # <input type="password" name="password" id="login_password" class="form-control" value="" autocomplete="current-password">
    password_input = browser.find_element_by_id("login_password")
    password_input.send_keys(MOODLE_PASSWORD)
    # <input type="submit" class="btn btn-primary btn-block" value="Log in">
    all_btns = browser.find_elements_by_class_name("btn-primary")
    for x in all_btns:
        if x.get_attribute("type") == "submit" and x.get_attribute("value") == "Log in":
            x.click()
            return
    raise Exception("Could not find the submit button for some reason.")


def go_to_course_page(browser):
    all_links = browser.find_elements_by_tag_name("a")
    for x in all_links:
        if x.get_attribute("title") == COURSE_TITLE:
            x.click()
            return


def go_to_attendance(browser):
    all_links = browser.find_elements_by_tag_name("a")
    for x in all_links:
        if x.text == "Attendance":
            x.click()
            return


def handle_attendance(browser):
    all_links = browser.find_elements_by_tag_name("a")
    found_submit_attendance = False
    for x in all_links:
        if x.text == "Submit attendance":
            x.click()
            found_submit_attendance = True
            break
    if not found_submit_attendance:
        return False
    all_spans = browser.find_elements_by_tag_name("span")
    for x in all_spans:
        if x.text == "Present":
            x.click()
            break
    submit_btn = browser.find_element_by_id("id_submitbutton")
    submit_btn.click()
    return True


def create_time_today(hour, min, sec):
    now = time.localtime()
    when = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, hour, min, sec, 1, 85, 0))
    return when


def log(msg):
    print(time.asctime()+": %s" % msg)


def wait_until_lesson_starts_and_launch_job(job):
    log("Waiting for the time %02d:%02d:%02d" % (START_HOUR, START_MINUTE, START_SECS))
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(create_time_today(START_HOUR, START_MINUTE, START_SECS), 1, job)
    s.run()



def main():
    log("The time has come! starting attempts.")
    is_successful = False
    browser = init_browser()
    while not is_successful:
        try:
            login_to_moodle(browser)
            go_to_course_page(browser)
            go_to_attendance(browser)
            is_successful = handle_attendance(browser)
        except exceptions.WebDriverException as e:
            log("Error WebDriverException...")
        browser.close()
        if is_successful:
            log("Done!")  # Will stop iterating afterwards (while condition)
        else:
            log("Failed. Sleeping now. will try again in %d seconds" % SLEEP_INTERVAL)
            time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    # main()
    wait_until_lesson_starts_and_launch_job(job=main)
