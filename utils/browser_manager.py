import os, json, time, shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SmartLoginManager:
    """多平台智能登录管理器（支持快手、B站、抖音）"""

    SUPPORTED_SITES = {
        "bilibili": "https://member.bilibili.com/platform/upload/video/frame",
        "douyin": "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web/",
        "kuaishou": "https://cp.kuaishou.com/article/publish/video?origin=www.kuaishou.com&source=PROFILE/"
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
                    if self.driver.find_elements(By.CSS_SELECTOR, "a[href*='space.bilibili.com'], .header-login-info, .user-name"):
                        return True
                except Exception:
                    pass

                # 2) URL 检查（上传/个人页/会员页）
                if "/member" in self.driver.current_url or "space.bilibili.com" in self.driver.current_url:
                    return True

                # 3) Cookie 检查（常见 cookie，如 `bili_jct` / `DedeUserID` 等）
                try:
                    cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
                    if any(k in cookies for k in ("bili_jct", "DedeUserID", "DedeUserID__ckMd5")):
                        return True
                except Exception:
                    pass

                # 最后回退到 page_source 判断（不可靠，作为最后手段）
                return ("个人中心" in self.driver.page_source) or ("登录" not in self.driver.page_source)

            # -----------------------
            # Douyin (抖音) 检测
            # -----------------------
            if self.site_name == "douyin":
            #     try:
            #         # 1️⃣ 登录状态检测：查找右上角头像或个人主页入口
            #         selectors = [
            #             "div[class*='login-avatar']",
            #             "div[class*='profile-entry']",
            #             "img[class*='avatar']",
            #             "div[class*='user-profile']",
            #         ]
            #         for sel in selectors:
            #             elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
            #             if elements and elements[0].is_displayed():
            #                 return True
            #     except Exception:
            #         pass

                # # 2️⃣ URL 检查
                # current_url = self.driver.current_url
                # if any(x in current_url for x in ["/user/", "/profile", "/creator"]):
                #     return True

                # # 3️⃣ localStorage 检查（更强）
                # try:
                #     user_info = self.driver.execute_script("""
                #         const keys = Object.keys(localStorage);
                #         for (let k of keys) {
                #             if (k.includes('user') || k.includes('profile')) {
                #                 return localStorage.getItem(k);
                #             }
                #         }
                #         return null;
                #     """)
                #     if user_info:
                #         return True
                # except Exception:
                #     pass

                # # 4️⃣ Cookies 检查（只在 URL / 页面上确认未登录时辅助）
                # try:
                #     cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
                #     # 抖音登录后会生成一些特殊 cookie
                #     if "sessionid" in cookies or "passport_csrf_token" in cookies:
                #         return True
                # except Exception:
                #     pass

                # 5️⃣ 最后回退：检测是否仍有“登录”按钮
                page_source = self.driver.page_source
                if "登录" in page_source or "login" in page_source:
                    return False
                else:
                    return True

                # return False


            # -----------------------
            # Kuaishou (快手) 检测
            # -----------------------
            if self.site_name == "kuaishou":
                try:
                    # 查找个人中心或头像
                    if self.driver.find_element(By.CSS_SELECTOR, ".user-info-name"):
                        return True
                except Exception:
                    pass

                if "/user" in self.driver.current_url or "/profile" in self.driver.current_url:
                    return True

                try:
                    cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
                    if any(k in cookies for k in ("kuaishou_app", "ks_user_id")):
                        return True
                except Exception:
                    pass

                return ("立即登录" not in self.driver.page_source)

            # 其他站点默认回退到 page_source
            return "登录" not in self.driver.page_source

        except Exception:
            return False

    def wait_for_manual_login(self, timeout=180):
        """等待人工登录"""
        print("⏳ 请手动完成登录（3分钟内），登录后自动检测状态。")
        start = time.time()
        while time.time() - start < timeout:
            if self.is_logged_in():
                print("✅ 检测到登录成功！")
                return
            time.sleep(5)
        raise TimeoutError("登录超时，请重试。")

    def start(self):
        return self.login()
