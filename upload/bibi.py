# bibi.py
from utils.browser_manager import create_driver_with_user_data
from utils.common_utils import wait_for_element, wait_for_element_clickable, check_element_exists
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class BibiUploader:
    def __init__(self):
        self.driver = None
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://member.bilibili.com/platform/upload/video/frame?page_from=creative_home_top_upload")
            time.sleep(3)
            
            if "creative_home_top_upload" in self.driver.current_url:
                print("✅ B站：已处于登录状态")
                return True
            else:
                print("❌ B站：未登录或登录已过期")
                return False
        except Exception as e:
            print(f"B站：检查登录状态时出错: {e}")
            return False
        
    def login(self):
        """登录B站"""
        try:
            self.driver = create_driver_with_user_data("C:/ChromeUserData_Bibi")  # 使用不同的用户目录
            print("🚀 B站：浏览器启动成功")
            
            if self.check_login_status():
                try:
                    # 检查是否已经登录
                    if 'creative_home_top_upload' in self.driver.current_url: 
                        print("✅ B站：已进入发布页面")
                        return True
                except Exception as e:
                    print(f"B站为登录: {e}")
                # 尝试直接访问发布页面
                self.driver.get("https://member.bilibili.com/platform/upload/video/frame?page_from=creative_home_top_upload")
                time.sleep(3)
                return True
            else:
                # 需要手动登录
                print("🔐 B站：需要手动登录...")
                input("请手动完成B站登录，登录完成后按回车键继续...")
                
                # 验证登录是否成功
                if self.check_login_status():
                    print("✅ B站：登录成功！")
                    return True
                else:
                    print("❌ B站：登录失败，请检查")
                    return False
                    
        except Exception as e:
            print(f"B站：登录过程中出错: {e}")
            return False
    
    def upload_video(self, video_path, name):
        """上传视频到B站"""
        try:
            print(f"📤 B站：开始上传视频: {name}")
            
            # 确保在上传页面
            if "creative_home_top_upload" not in self.driver.current_url:
                self.driver.get("https://member.bilibili.com/platform/upload/video/frame?page_from=creative_home_top_upload")
                time.sleep(3)
            
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            # ✅ 清空旧的文件选择（重点）
            self.driver.execute_script("arguments[0].value = '';", file_input)
            time.sleep(0.5)
            # 选择新文件
            file_input.send_keys(video_path)
            print(f"✅ B站：视频文件已选择: {name}")
            return True
            
        except Exception as e:
            print(f"❌ B站：上传视频失败: {e}")
            return False
    
    def fapu_video(self):
        """发布视频"""
        upload_complete = False
        while True:
            # 获取所有任务元素
            tasks = self.driver.find_elements(By.XPATH, "//div[@class='task-list-content-item']")
            if not tasks:
                print("✅ 所有任务上传完成")
                break

            current = tasks[0]  # 拿第一个任务
            current.click()
            time.sleep(5)
            print("🎬 点击第一个任务")

            upload_complete = False
            start_time = time.time()

            while time.time() - start_time < 300:  # 最多等5分钟
                try:
                    # ✅ 只查找当前任务内部的状态
                    status_elem = current.find_element(By.XPATH, "//span[contains(text(),'上传完成')]")
                    status_text = status_elem.text.strip()
                    if "上传完成" in status_text:
                        print("✅ 当前视频上传完成")
                        upload_complete = True
                        break

                except Exception as e:
                    # 任务可能被刷新或删除
                    pass

                time.sleep(5)
                
            if not upload_complete:
                print("❌ B站：视频上传超时")
                return False
        
            # 发布视频     wait_for_element
            videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//span[contains(@class, 'submit-add')]")
            self.driver.execute_script("arguments[0].click();", videos_fabu)
            print("✅ B站：点击立即投稿")
            start_time = time.time()
            while time.time() - start_time < 60:
                try:
                    alert = self.driver.find_element(By.XPATH, "//div[@role='alert']/p[contains(@class, 'bcc-message')]")
                    message = alert.text.strip()
                    if message:
                        print(f"✅ B站提示：{message}")
                        time.sleep(3)
                        break
                except:
                    # 没有alert，继续等待
                    pass
                time.sleep(1)
            
            # # 刷新页面
            # self.driver.refresh()
            # if wait_for_element(self.driver, By.XPATH, "//div[contains(text(), '拖拽到此处也可上传')]"):
            #     print("✅ B站：准备上传下一个视频")
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()