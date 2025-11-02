# bibi.py
from utils.common_utils import wait_for_element, wait_for_element_clickable, check_element_exists
from selenium.webdriver.common.by import By
import time
COOKIES_DIR = "C:/ChromeUserData_xiaohongshu_Cookies"

class XiaohongshuUploader:
    def __init__(self):
        self.driver = None
    
    def login(self, account_name):
        """登录小红书"""
        from utils.browser_manager import create_driver, save_cookies, load_cookies
        self.driver = create_driver()
        
        if load_cookies(account_name, self.driver, COOKIES_DIR, "https://www.xiaohongshu.com/"):
            if self.check_login_status():
                print(f"✅ {account_name}账号 小红书：自动登录成功")
                return True

        # 需要手动登录
        self.driver.get("https://www.xiaohongshu.com/")
        print(f"🔐 请手动登录账号 {account_name}，登录完成后按回车继续...")
        input()
        save_cookies(account_name, self.driver, COOKIES_DIR)
        return True
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=video")
            time.sleep(3)
            
            if "menu&target=video" in self.driver.current_url:
                return True
            else:
                print("❌ 小红书：未登录或登录已过期")
                return False
        except Exception as e:
            print(f"小红书：检查登录状态时出错: {e}")
            return False
    
    def upload_video(self, video_path, name):    
        """上传视频到小红书"""
        try:
            print(f"📤 小红书：开始上传视频: {name}")
            
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            file_input.send_keys(video_path)
            print(f"✅ 小红书：视频文件已选择: {name}")
            
            # 等待上传完成
            upload_complete = False
            start_time = time.time()
            while time.time() - start_time < 300:  # 最多等待5分钟
                try:
                    # 检查上传进度
                    progress_element = self.driver.find_element(By.XPATH, "//div[@class='stage']/div[1]")
                    if progress_element:
                        print(f"📊 小红书：上传进度: {progress_element.text}")
                        time.sleep(5)
                    # 检查是否上传完成（出现重新上传按钮）
                    text = self.driver.find_element(By.XPATH, "//div[@class='stage']/div[1]")
                    if "上传成功" in text.text:
                        print("✅ 小红书：视频上传完成")
                        upload_complete = True
                        break
                except:
                    time.sleep(5)
            
            if not upload_complete:
                print("❌ 小红书：视频上传超时")
                return False
            
            # 填写视频标题
            videos_name = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='tiptap ProseMirror']")
            videos_name.click()
            videos_name.send_keys(name)
            print("✅ 小红书：视频标题已设置")
            
            # 设置封面
            try:
                videos_fengmian = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='defaults']/div[3]/div[contains(@class, 'cover-image')]")
                videos_fengmian.click()    
                time.sleep(2)
            
                # 等待封面检测通过
                fengmian = wait_for_element(self.driver, By.XPATH, "//span[@class='loadingText']")
                if "封面效果评估通过，未发现封面质量问题" in fengmian.text:
                    print("✅ 小红书：封面设置成功")
            except Exception as e:
                print(f"⚠️ 小红书：封面设置失败: {e}")
            
            # 发布视频
            videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='d-button-content']/span[(text()='发布')]")
            self.driver.execute_script("arguments[0].click();", videos_fabu)
            print("✅ 小红书：发布按钮已点击")
            # 等待发布完成
            chenggong = wait_for_element(self.driver, By.XPATH, "//span[contains(@class, 'title') and text()='上传视频']")
            if chenggong:
                print("✅ 小红书：视频发布成功")
            
            
            print(f"🎉 小红书：视频 '{name}' 发布流程完成")
            return True
            
        except Exception as e:
            print(f"❌ 小红书：上传视频失败: {e}")
            return False
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 小红书：浏览器已关闭")