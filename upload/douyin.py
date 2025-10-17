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
        # 登录网站
        driver.get("https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web")

        # 点击登录按钮
        wait_for_element(driver, By.XPATH, "//span[@text='密码登录']").click()
        wait_for_element(driver, By.XPATH, "//div[@class='douyin_login_comp_normal_input-ft2LbF']").send_keys("13869586968")
        wait_for_element(driver, By.XPATH, "//div[@class='input-XjvQLQ']").send_keys("libin123")
        login_button = wait_for_element(driver, By.XPATH, "//div[@class='douyin_login_comp_btn-S_beyL content-JgElQ7 primary-rpXI7f disabled-xlNs7G ']")
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