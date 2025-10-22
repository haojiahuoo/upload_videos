# bibi.py
from browser_manager import create_driver_with_user_data
from common_utils import wait_for_element, wait_for_element_clickable, check_element_exists
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class XiaohongshuUploader:
    def __init__(self):
        self.driver = None
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=video")
            time.sleep(3)
            
            if "menu&target=video" in self.driver.current_url:
                print("✅ 小红书：已处于登录状态")
                return True
            else:
                print("❌ 小红书：未登录或登录已过期")
                return False
        except Exception as e:
            print(f"小红书：检查登录状态时出错: {e}")
            return False
        
    def login(self):
        """登录小红书"""
        try:
            self.driver = create_driver_with_user_data("C:/ChromeUserData_xiaohongshu")  # 使用不同的用户目录
            print("🚀 小红书：浏览器启动成功")
            
            if self.check_login_status():
                try:
                    # 检查是否已经登录
                    if 'menu&target=video' in self.driver.current_url: 
                        print("✅ 小红书：已进入发布页面")
                        return True
                except Exception as e:
                    print(f"小红书为登录: {e}")
                # 尝试直接访问发布页面
                self.driver.get("https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=video")
                time.sleep(3)
                return True
            else:
                # 需要手动登录
                print("🔐 小红书：需要手动登录...")
                input("请手动完成小红书登录，登录完成后按回车键继续...")
                
                # 验证登录是否成功
                if self.check_login_status():
                    print("✅ 小红书：登录成功！")
                    return True
                else:
                    print("❌ 小红书：登录失败，请检查")
                    return False
                    
        except Exception as e:
            print(f"小红书：登录过程中出错: {e}")
            return False
    
    def upload_video(self, video_path, name):    
        """上传视频到小红书"""
        try:
            print(f"📤 小红书：开始上传视频: {name}")
            
            # 确保在上传页面
            if "'menu&target=video" not in self.driver.current_url:
                self.driver.get("https://creator.xiaohongshu.com/publish/publish?source=official&from=menu&target=video")
                time.sleep(3)
            
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
            videos_name = wait_for_element_clickable(self.driver, By.XPATH, "//input[@class='d-text']")
            videos_name.clear()
            videos_name.send_keys(name)
            print("✅ 小红书：视频标题已设置")
            
            # 设置封面
            try:
                videos_fengmian = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='defaults']/div[3]/div[@class='cover-image column']")
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
            chenggong = wait_for_element(self.driver, By.XPATH, "//div[contains(text(), '发布成功')]")
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