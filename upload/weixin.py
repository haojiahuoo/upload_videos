# weixin.py
import os, time, re
from selenium.webdriver.common.by import By
from utils.browser_manager import SmartLoginManager
from config import ACCOUNT_NAME
from utils.image import resize_and_crop
from utils.common_utils import *

class WeixinUploader:
    def __init__(self, account_name=ACCOUNT_NAME):
        self.account_name = account_name
        self.manager = SmartLoginManager(site_name="weixin", account_name=account_name)
        self.driver = None
    
    def wait_for_shadow_root(slef, selector="wujie-app", timeout=10):
        """等待 shadow DOM 挂载，返回 shadowRoot"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            shadow_root = slef.driver.execute_script(
                f"const el = document.querySelector('{selector}'); return el ? el.shadowRoot : null;"
            )
            if shadow_root:
                return True
            time.sleep(0.5)
        raise Exception(f"❌ shadowRoot 未挂载：{selector}")

    def get_shadow_element(self, shadow_selector: str, timeout: float = 10, click: bool = False):
        """
        获取 shadow DOM 内的元素，并可选点击

        参数:
            driver: Selenium WebDriver 实例
            wujie_selector: wujie-app CSS selector（通常是 'wujie-app'）
            shadow_selector: shadow DOM 内元素 CSS selector
            timeout: 等待元素的最长时间
            click: 是否自动点击元素

        返回:
            WebElement 或 None
        """
        from selenium.common.exceptions import JavascriptException
        wujie_selector="wujie-app"
        
        # 1️⃣ hack parentNode
        try:
            self.driver.execute_script(f"""
            const firstChild = document.querySelector('{wujie_selector}').shadowRoot.firstElementChild;
            if(firstChild) {{
                Object.defineProperty(firstChild, "parentNode", {{
                    enumerable: true,
                    configurable: true,
                    get: () => window.document
                }});
            }}
            """)
        except JavascriptException:
            pass  # 忽略已存在等异常

        # 2️⃣ 获取 shadowRoot
        shadow_root = self.driver.execute_script(f"return document.querySelector('{wujie_selector}').shadowRoot")

        # 3️⃣ 轮询等待元素出现
        start_time = time.time()
        element = None
        while time.time() - start_time < timeout:
            element = self.driver.execute_script(f"""
            const shadow = arguments[0];
            return shadow.querySelector("{shadow_selector}");
            """, shadow_root)
            if element:
                break
            time.sleep(0.3)

        if element and click:
            element.click()

        return element

    def upload_to_weixin(self, media_files, platform):
        """批量上传入口"""
        print("\n" + "="*50)
        print("🚀 开始上传到 微信视频号")
        print("="*50)

        self.driver = self.manager.start()
        
        for i, video in enumerate(media_files['videos'], 1):
            title = video['title']
            video_path = video['path']
            print(f"\n📤 正在上传第 {i}/{len(media_files['videos'])} 个视频: {title}")

            cover_path = None
            for img in media_files['images']:
                if clean_title(img['title'].lower()) == clean_title(title.lower()):
                    cover_path = img['path']
                    break


            success = self.upload_video(video_path, title, cover_path)

            if success:
                record_download(platform, "upload", video_path, "weixin", True)  # ✅ 上传+发布后移动文件
                print(f"✅ 微信视频号：第 {i} 个视频上传并移动完成")
            else:
                print(f"❌ 微信视频号：第 {i} 个视频上传失败")

            if i < len(media_files['videos']):
                print("⏳ 等待 5 秒后继续...")
                time.sleep(5)

        print("🎉 微信视频号：所有视频上传完成")
        self.quit()
    
    def upload_video(self, video_path, title, cover_path=None):    
        """上传视频到微信视频号"""
        try:
            print(f"📤 微信视频号：开始上传视频: {title}")
            if "post/create" not in self.driver.current_url:
                self.driver.get("https://channels.weixin.qq.com/platform/post/create")
                time.sleep(3)
            
            shadow_root = self.wait_for_shadow_root()
            if shadow_root:
                print("✅ shadow DOM 已挂载")
            
            # 查找 shadow DOM 内隐藏的文件上传 input
            file_input = self.get_shadow_element(shadow_selector="#container-wrap input[type=file][accept='video/mp4,video/x-m4v,video/*']")
            # 上传视频文件
            if file_input:
                file_input.send_keys(video_path)
                print("✅ 视频文件已选择")
            else:
                print("❌ 找不到文件上传 input")
            
            # 填写标题    
            miaoshu = self.get_shadow_element(shadow_selector=".input-editor")
            self.driver.execute_script("arguments[0].click();", miaoshu)
            miaoshu.send_keys(title)
            
            upload_complete = False
            start_time = time.time()
            while time.time() - start_time < 600:  # 最多等5分钟
                try:
                    # ✅ 只查找当前任务内部的状态
                    status_spans = self.get_shadow_element(shadow_selector= "#container-wrap div.media-progress > div > div > span")
                    if status_spans:
                        print(f"视频上传进度：{status_spans.text}")
                    else:
                        upload_complete = True
                        print("✅ 当前视频上传完成")
                        break
                except Exception as e:
                    # 任务可能被刷新或删除
                    pass

                time.sleep(5)
                
            if not upload_complete:
                print("❌ 微信视频号：视频上传超时")
                return False
            # 图片缩放到1200*900
            resize_and_crop(cover_path, cover_path, size=(1200, 900), crop=False)
            
            # 点击选择封面4:3
            cover = self.get_shadow_element(shadow_selector="#container-wrap .post-edit-wrap .horizon-img-wrap > div")
            self.driver.execute_script("arguments[0].click();", cover)
            time.sleep(2)
            cover_input = self.get_shadow_element(shadow_selector=".single-cover-uploader-wrap > input[type='file'][accept*='image/jpeg,image/jpg,image/png']")
            cover_input.send_keys(cover_path)
            
            # 点击确定按钮
            queding = self.get_shadow_element(shadow_selector="#container-wrap div.weui-desktop-dialog__ft > div > div > div:nth-child(2) > button")
            self.driver.execute_script("arguments[0].click();", queding)
            time.sleep(5)
            # 点击选择封面3:4
            cover_4_3 = self.get_shadow_element(shadow_selector="#container-wrap div.vertical-cover-wrap.img-popover-wrap > div.vertical-img-wrap > div.edit-btn.edit-btn-zIndex")
            self.driver.execute_script("arguments[0].click();", cover_4_3)
            time.sleep(2)
            cover_input_4_3 = self.get_shadow_element(shadow_selector="#container-wrap div.weui-desktop-btn_wrp.btn-use > button")
            self.driver.execute_script("arguments[0].click();", cover_input_4_3)
            
            # 点击确定按钮
            queding = self.get_shadow_element(shadow_selector="#container-wrap div.weui-desktop-dialog__ft > div > div > div:nth-child(2) > button")
            self.driver.execute_script("arguments[0].click();", queding)
            
            # 点击发表
            fabiao = self.get_shadow_element(shadow_selector="#container-wrap div.form > div.form-btns > div:nth-child(5) > span > div > button")
            self.driver.execute_script("arguments[0].click();", fabiao)
            # 点击发表视频进入新的发表页
            fabiaoye = self.get_shadow_element(shadow_selector="#container-wrap  div:nth-child(2) > div.feed-list-opt > div.video-btn-wrap > div > button")
            self.driver.execute_script("arguments[0].click();", fabiaoye)
            return True
        except Exception as e:
            print(f"❌ 微信视频号：上传视频失败: {e}")
            return False
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 微信视频号：浏览器已关闭")