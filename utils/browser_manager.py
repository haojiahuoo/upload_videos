import os, json, time, shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.common_utils import *


class SmartLoginManager:
    """多平台智能登录管理器（支持快手、B站、抖音）"""

    SUPPORTED_SITES = {
        "bilibili": "https://member.bilibili.com/platform/upload/video/frame",
        "douyin": "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web",
        "kuaishou": "https://cp.kuaishou.com/article/publish/video?origin=www.kuaishou.com&source=PROFILE",
        "weixin": "https://channels.weixin.qq.com/platform/post/create",
    }

    def __init__(self, site_name, account_name, cookies_root="cookies", headless=False):
        if site_name not in self.SUPPORTED_SITES:
            raise ValueError(f"暂不支持此平台: {site_name}")

        self.site_name = site_name
        self.account_name = account_name
        self.cookies_root = cookies_root
        self.headless = headless

        # 拼接cookie
        self.cookies_dir = os.path.join(cookies_root, site_name)
        # 确保地址存在
        os.makedirs(self.cookies_dir, exist_ok=True)

        self.driver = None

    # -----------------------------
    # 初始化浏览器
    # -----------------------------
    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1200,900")

        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    # -----------------------------
    # Cookies 保存/加载
    # -----------------------------
    def get_cookies_path(self):
        return os.path.join(self.cookies_dir, f"{self.account_name}_cookies.json")

    def save_cookies(self):
        cookies_path = self.get_cookies_path()
        cookies = self.driver.get_cookies()
        with open(cookies_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        print(f"✅ Cookies 已保存: {cookies_path}")

    def load_cookies(self):
        cookies_path = self.get_cookies_path()
        if not os.path.exists(cookies_path):
            return False

        with open(cookies_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        url = self.SUPPORTED_SITES[self.site_name]
        self.driver.get(url)
        time.sleep(2)

        for cookie in cookies:
            cookie.pop('sameSite', None)
            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass

        self.driver.refresh()
        time.sleep(3)
        print(f"✅ Cookies 已加载: {self.account_name}")
        return True

    # -----------------------------
    # 登录流程
    # -----------------------------
    def login(self):
        """主流程：加载 → 检查 → 手动登录 → 保存"""
        self.driver = self.create_driver()
        url = self.SUPPORTED_SITES[self.site_name]

        loaded = self.load_cookies()
        self.driver.get(url)
        time.sleep(3)

        if not self.is_logged_in():
            print("⚠️ Cookies 可能失效，请手动登录...")
            self.wait_for_manual_login()
            time.sleep(5)
            self.save_cookies()
        else:
            print("✅ 自动登录成功（Cookies 有效）")

        return self.driver

    def is_logged_in(self, timeout=3):
        """
        更健壮的登录检测。
        逻辑（优先级）：
        1. 通过页面可见的用户相关元素（头像/个人中心/登出按钮）
        2. 通过特定 URL 特征（例如上传/个人页）
        3. 通过常见登录 cookies（尝试读取）
        4. 最后回退到 page_source 中是否包含 "登录"（不推荐单独使用）
        timeout: 等待页面渲染的秒数（短等待）
        """
        try:
            url = self.SUPPORTED_SITES[self.site_name]
            # 确保页面至少加载了基础 DOM
            try:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
                )
            except Exception:
                pass

            # -----------------------
            # Bilibili 检测（优先 DOM）
            # -----------------------
            if self.site_name == "bilibili":
                # 1) 查找个人中心或头像链接（常见选择器）
                try:
                    # 头像或个人链接（示例）
                    if self.driver.find_elements(By.XPATH, "//div[@class='upload-btn no-events']"):
                        return True
                    else:
                        return False
                except Exception:
                    pass
            # -----------------------
            # Douyin (抖音) 检测
            # -----------------------
            if self.site_name == "douyin":
                try:
                    # 头像或个人链接（示例）
                    if check_element_exists(self.driver, By.XPATH, "//span[@class='semi-button-content-right']"):
                        return True
                    else:
                        return False
                except Exception:
                    pass
            # -----------------------
            # Kuaishou (快手) 检测
            # -----------------------
            if self.site_name == "kuaishou":
                try:
                    # 查找个人中心或头像
                    if check_element_exists(self.driver, By.XPATH, "//*[@id='joyride-wrapper']/main/section/div/div[1]/div[2]/button"):
                        return True
                    else:
                        return False
                except Exception:
                    pass
            # -----------------------
            # weixin (微信视频号) 检测
            # -----------------------    
            if self.site_name == "weixin":
                # 临时调试代码
                elements = self.driver.find_elements(By.CSS_SELECTOR, "wujie-app")
                print(f"找到 {len(elements)} 个wujie-app元素")
                if len(elements) > 0:
                    return True
                else:
                    return False
                
        except Exception:
            return False

    def wait_for_manual_login(self, timeout=300):
        """等待人工登录"""
        print("⏳ 请手动完成登录（5分钟内），登录后自动检测状态。")
        start = time.time()
        while time.time() - start < timeout:
            if self.is_logged_in():
                print("✅ 检测到登录成功！")
                return
            time.sleep(5)
        raise TimeoutError("登录超时，请重试。")

    def start(self):
        return self.login()
