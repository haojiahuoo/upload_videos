import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, by, locator):
    return WebDriverWait(driver, 15).until(EC.presence_of_element_located((by, locator)))

def upload_to_douyin(video_path, title, description, tags, username, password):
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    try:
        # Navigate to Douyin login page
        driver.get("https://www.douyin.com/login")

        # Log in to Douyin
        username_field = wait_for_element(driver, By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[text()='Log In']")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # Wait for login to complete (this may require more sophisticated handling)
        driver.implicitly_wait(10)

        # Navigate to the upload page
        driver.get("https://www.douyin.com/upload")

        # Upload the video
        upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_input.send_keys(video_path)

        # Fill in title, description, and tags
        title_field = driver.find_element(By.NAME, "title")
        description_field = driver.find_element(By.NAME, "description")
        tags_field = driver.find_element(By.NAME, "tags")

        title_field.send_keys(title)
        description_field.send_keys(description)
        tags_field.send_keys(", ".join(tags))

        # Submit the upload
        submit_button = driver.find_element(By.XPATH, "//button[text()='Submit']")
        submit_button.click()

        # Wait for upload to complete
        driver.implicitly_wait(10)

    finally:
        # Close the WebDriver
        driver.quit()