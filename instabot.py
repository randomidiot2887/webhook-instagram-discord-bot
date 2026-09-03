import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

INSTAGRAM_URL = "https://www.instagram.com/"
TARGET_NOTE_TEXT = "Do Not Disturb (My bot works <3)"  # 60 char limit enforced by IG
COOKIE_FILE = "instagram_cookies.pkl"


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1024,768")
    options.add_argument("--force-device-scale-factor=0.8")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 2}
    )
    options.binary_location = "/usr/bin/chromium"  # Debian image path, not Fedora's

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def dismiss_notifications_dialog(driver):
    try:
        wait = WebDriverWait(driver, 3)
        not_now_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Not Now') or contains(text(),'Not now')]")
            )
        )
        driver.execute_script("arguments[0].click();", not_now_btn)
        print("Dismissed notifications dialog.")
    except TimeoutException:
        print("No notifications dialog appeared.")


def load_cookies_and_login(driver):
    driver.get(INSTAGRAM_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    try:
        with open(COOKIE_FILE, "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            cookie.pop("sameSite", None)
            driver.add_cookie(cookie)
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Cookies loaded.")
    except FileNotFoundError:
        print("No cookie file found. Log in manually in the opened browser window.")
        input("Press Enter after logging in...")
        with open(COOKIE_FILE, "wb") as file:
            pickle.dump(driver.get_cookies(), file)

    dismiss_notifications_dialog(driver)


def clear_existing_note(driver):
    wait = WebDriverWait(driver, 3)
    try:
        status_bubble = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'x7wppnt')]"))
        )
        driver.execute_script("arguments[0].click();", status_bubble)

        delete_btn = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='button'][contains(text(),'Delete note')]")
            )
        )
        driver.execute_script("arguments[0].click();", delete_btn)
        print("Existing note deleted.")
    except TimeoutException:
        print("No existing note found — skipping delete.")


def set_instagram_note(driver, phrase):
    print("Navigating to inbox...")
    driver.get("https://www.instagram.com/direct/inbox/")
    wait = WebDriverWait(driver, 15)

    clear_existing_note(driver)

    try:
        note_trigger = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='button'][.//span[contains(text(),'note')]]")
            )
        )
        driver.execute_script("arguments[0].click();", note_trigger)

        note_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][.//p]"))
        )
        note_input.click()
        note_input.send_keys(phrase[:60])

        ActionChains(driver).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
        print("Note set.")

    except TimeoutException as e:
        print(f"Selector failed — Instagram's DOM likely changed. Inspect manually: {e}")


# if __name__ == "__main__":
#     driver = init_driver()
#     try:
#         load_cookies_and_login(driver)
#         set_instagram_note(driver, TARGET_NOTE_TEXT)
#     finally:
#         driver.quit()
if __name__ == "__main__":
    driver = init_driver()
    try:
        load_cookies_and_login(driver)
        set_instagram_note(driver, TARGET_NOTE_TEXT)
    finally:
        driver.quit()
