# kuaishou.py
from utils.browser_manager import create_driver_with_user_data
from utils.common_utils import wait_for_element, wait_for_element_clickable, check_element_exists
from selenium.webdriver.common.by import By
import time


class KuaishouUploader:
    def __init__(self):
        self.driver = None
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://cp.kuaishou.com/article/publish/video")
            time.sleep(3)
            
            if "publish/video" in self.driver.current_url:
                print("✅ 抖音：已处于登录状态")
                return True
            else:
                print("❌ 抖音：未登录或登录已过期")
                return False
        except Exception as e:
            print(f"抖音：检查登录状态时出错: {e}")
            return False
        
    def login(self):
        """登录快手"""
        try:
            self.driver = create_driver_with_user_data("C:/ChromeUserData_Kuaishou")  # 使用不同的用户目录
            print("🚀 快手：浏览器启动成功")
            
            if self.check_login_status():
                try:
                    # 检查是否已经登录
                    if 'video' in self.driver.current_url: 
                        print("✅ 抖音：已进入发布页面")
                        return True
                except Exception as e:
                    print(f"快手为登录: {e}")
                # 尝试直接访问发布页面
                self.driver.get("https://cp.kuaishou.com/article/publish/video")
                time.sleep(3)
                return True
            else:
                # 需要手动登录
                print("🔐 快手：需要手动登录...")
                input("请手动完成抖音登录，登录完成后按回车键继续...")
                
                # 验证登录是否成功
                if self.check_login_status():
                    print("✅ 快手：登录成功！")
                    return True
                else:
                    print("❌ 快手：登录失败，请检查")
                    return False
                    
        except Exception as e:
            print(f"快手：登录过程中出错: {e}")
            return False
    
    def upload_video(self, video_path, name):
        """上传视频到快手"""
        try:
            print(f"📤 抖音：开始上传视频: {name}")
            
            # 确保在上传页面
            if "video" not in self.driver.current_url:
                self.driver.get("https://cp.kuaishou.com/article/publish/video")
                time.sleep(3)
            
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            file_input.send_keys(video_path)
            print(f"✅ 快手：视频文件已选择: {name}")
            
            # 等待上传完成
            upload_complete = False
            start_time = time.time()
            while time.time() - start_time < 300:  # 最多等待5分钟
                try:
                    # 检查上传进度
                    progress_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'ant-progress-text')]")
                    if progress_elements:
                        print(f"📊 快手：上传进度: {progress_elements[0].text}")
                    
                    # 检查是否上传完成（出现重新上传按钮）
                    self.driver.find_element(By.XPATH, "//span[contains(text(), '预览作品')]")
                    print("✅ 快手：视频上传完成")
                    upload_complete = True
                    break
                except:
                    time.sleep(5)
            
            if not upload_complete:
                print("❌ 快手：视频上传超时")
                return False
            
            # 填写视频标题
            videos_name = wait_for_element_clickable(self.driver, By.XPATH, "//div[@id='work-description-edit']")
            videos_name.clear()
            videos_name.send_keys(name)
            print("✅ 快手：视频标题已设置")
        
            # 设置封面
            try:
                videos_pk = wait_for_element(self.driver, By.XPATH, "//button[@class='ant-switch ant-switch-small']")
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", videos_pk)
                time.sleep(1)
                videos_fengmian = wait_for_element(self.driver, By.XPATH, "//div[contains(@class, '_recommend-cover-main_ps02t_168')]/div[3]//span/img")
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", videos_fengmian)
                time.sleep(1)
                videos_pk1 = wait_for_element(self.driver, By.XPATH, "(//label[@class='ant-radio-wrapper'])[1]")
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", videos_pk1)
                print("✅ 快手：封面设置成功")
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ 快速：封面设置失败: {e}")
            
            # 发布视频
            videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//div[contains(@class, '_button_3a3lq_1 _button-primary_3a3lq_60')]")
            self.driver.execute_script("arguments[0].click();", videos_fabu)
            print("✅ 快手：发布按钮已点击")
            
            # 等待发布完成
            time.sleep(5)
            start_time = time.time()
            while time.time() - start_time < 60:  # 最多等待1分钟
                if "manage" in self.driver.current_url:
                    # 点击高清发布
                    try:
                        videos_gaoqingfabu = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='publish-button__text']")
                        self.driver.execute_script("arguments[0].click();", videos_gaoqingfabu)
                        print("✅ 快手：高清发布已点击")
                        break
                    except Exception as e:
                        print(f"⚠️ 快手：高清发布点击失败: {e}")
                        break
                else:
                    time.sleep(3)
            
            print(f"🎉 快手：视频 '{name}' 发布流程完成")
            return True
            
        except Exception as e:
            print(f"❌ 快手：上传视频失败: {e}")
            return False
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()