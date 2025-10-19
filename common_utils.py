# common_utils.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def wait_for_element(driver, by, locator, timeout=60):
    """等待元素出现"""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def wait_for_element_clickable(driver, by, locator, timeout=60):
    """等待元素可点击"""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))

def check_element_exists(driver, by, locator, timeout=5):
    """检查元素是否存在"""
    try:
        wait_for_element(driver, by, locator, timeout)
        return True
    except:
        return False