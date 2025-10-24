# douyin.py
from utils.browser_manager import create_driver_with_user_data
from utils.common_utils import wait_for_element, wait_for_element_clickable, check_element_exists
from selenium.webdriver.common.by import By
import time

class DouyinUploader:
    def __init__(self):
        self.driver = None
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://creator.douyin.com/creator-micro/home")
            time.sleep(3)
            
            if "creator-micro/home" in self.driver.current_url:
                print("✅ 抖音：已处于登录状态")
                return True
            else:
                print("❌ 抖音：未登录或登录已过期")
                return False
        except Exception as e:
            print(f"抖音：检查登录状态时出错: {e}")
            return False
    
    def login(self):
        """登录抖音创作者平台"""
        try:
            # 创建带用户数据的浏览器实例
            self.driver = create_driver_with_user_data()
            print("🚀 抖音：浏览器启动成功")
            
            # 检查是否已经登录
            if self.check_login_status():
                # 已经登录，直接点击发布按钮
                try:
                    publish_btn = wait_for_element_clickable(self.driver, By.XPATH, "//div[contains(@class, 'title-HvY9Az')]")
                    publish_btn.click()
                    print("✅ 抖音：已进入发布页面")
                    return True
                except Exception as e:
                    print(f"抖音：点击发布按钮失败: {e}")
                    # 尝试直接访问发布页面
                    self.driver.get("https://creator.douyin.com/creator-micro/content/upload")
                    time.sleep(3)
                    return True
            else:
                # 需要手动登录
                print("🔐 抖音：需要手动登录...")
                input("请手动完成抖音登录，登录完成后按回车键继续...")
                
                # 验证登录是否成功
                if self.check_login_status():
                    print("✅ 抖音：登录成功！")
                    return True
                else:
                    print("❌ 抖音：登录失败，请检查")
                    return False
                    
        except Exception as e:
            print(f"抖音：登录过程中出错: {e}")
            return False
    
    def upload_video(self, video_path, name):    
        """上传视频到抖音"""
        try:
            print(f"📤 抖音：开始上传视频: {name}")
            
            # 确保在上传页面
            if "upload" not in self.driver.current_url:
                self.driver.get("https://creator.douyin.com/creator-micro/content/upload")
                time.sleep(3)
            
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            file_input.send_keys(video_path)
            print(f"✅ 抖音：视频文件已选择: {name}")
            
            # 等待上传完成
            upload_complete = False
            start_time = time.time()
            while time.time() - start_time < 300:  # 最多等待5分钟
                try:
                    # 检查上传进度
                    progress_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'text-')]")
                    if progress_elements:
                        print(f"📊 抖音：上传进度: {progress_elements[0].text}")
                    
                    # 检查是否上传完成（出现重新上传按钮）
                    self.driver.find_element(By.XPATH, "//div[contains(text(), '重新上传')]")
                    print("✅ 抖音：视频上传完成")
                    upload_complete = True
                    break
                except:
                    time.sleep(5)
            
            if not upload_complete:
                print("❌ 抖音：视频上传超时")
                return False
            
            # 填写视频标题
            videos_name = wait_for_element_clickable(self.driver, By.XPATH, "//input[@class='semi-input semi-input-default']")
            videos_name.clear()
            videos_name.send_keys(name)
            print("✅ 抖音：视频标题已设置")
            
            # 设置封面
            try:
                videos_fengmian = wait_for_element_clickable(self.driver, By.XPATH, "//div[contains(@class, 'maskBox-FrHA4G')]")
                videos_fengmian.click()    
                time.sleep(2)
                
                popup_button = wait_for_element_clickable(self.driver, By.XPATH, "//button[@class='semi-button semi-button-primary']")
                popup_button.click()
                
                # 等待封面检测通过
                wait_for_element(self.driver, By.XPATH, "//span[contains(text(), '封面效果检测通过')]")
                print("✅ 抖音：封面设置成功")
            except Exception as e:
                print(f"⚠️ 抖音：封面设置失败: {e}")
            
            # 发布视频
            videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//button[contains(@class, 'button-dhlUZE')]")
            self.driver.execute_script("arguments[0].click();", videos_fabu)
            print("✅ 抖音：发布按钮已点击")
            
            # 等待发布完成
            time.sleep(5)
            start_time = time.time()
            while time.time() - start_time < 60:  # 最多等待1分钟
                if "manage" in self.driver.current_url:
                    # 点击高清发布
                    try:
                        videos_gaoqingfabu = wait_for_element_clickable(self.driver, By.XPATH, "//span[@id='douyin-creator-master-side-upload']")
                        self.driver.execute_script("arguments[0].click();", videos_gaoqingfabu)
                        print("✅ 抖音：高清发布已点击")
                        break
                    except Exception as e:
                        print(f"⚠️ 抖音：高清发布点击失败: {e}")
                        break
                else:
                    time.sleep(3)
            
            print(f"🎉 抖音：视频 '{name}' 发布流程完成")
            return True
            
        except Exception as e:
            print(f"❌ 抖音：上传视频失败: {e}")
            return False
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 抖音：浏览器已关闭")