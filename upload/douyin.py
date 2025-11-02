# douyin.py
import os, time
from selenium.webdriver.common.by import By
from utils.browser_manager import SmartLoginManager
from config import ACCOUNT_NAME
from utils.image import resize_and_crop
from utils.common_utils import *

class DouyinUploader:
    def __init__(self, account_name=ACCOUNT_NAME):
        self.account_name = account_name
        self.manager = SmartLoginManager(site_name="douyin", account_name=account_name)
        self.driver = None
    
    def upload_to_douyin(self, media_files, platform):
        """上传到抖音"""
        print("\n" + "="*50)
        print("🚀 开始上传到抖音")
        print("="*50)
        
        self.driver = self.manager.start()
            
        for i, video in enumerate(media_files['videos'], 1):
            title = video['title']
            video_path = video['path']
            print(f"\n📤 正在上传第 {i}/{len(media_files['videos'])} 个视频: {title}")

            cover_path = None
            for img in media_files['images']:
                if img['title'].lower() == title.lower():
                    cover_path = img['path']
                    break

            success = self.upload_video(video_path, title, cover_path)

            if success:
                record_download(platform, "upload", video_path, "douyin", True)  # ✅ 上传+发布后移动文件
                print(f"✅ 抖音：第 {i} 个视频上传并移动完成")
            else:
                print(f"❌ 抖音：第 {i} 个视频上传失败")

            if i < len(media_files['videos']):
                print("⏳ 等待 5 秒后继续...")
                time.sleep(5)

        print("🎉 抖音：所有视频上传完成")
        self.quit()

    def upload_video(self, video_path, title, cover_path=None):    
        """上传视频到抖音"""
        try:
            print(f"📤 抖音：开始上传视频: {title}")
            # 确保在上传页面 
            if "upload?enter_from=dou_web" not in self.driver.current_url: 
                self.driver.get("https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web") 
                time.sleep(3)
            
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            file_input.send_keys(video_path)
            print(f"✅ 抖音：视频文件已选择: {title}")
            
            # 填写视频标题
            videos_name = wait_for_element(self.driver, By.XPATH, "//div[@class='zone-container editor-kit-container editor editor-comp-publish notranslate chrome window chrome88']")
            videos_name.click()
            videos_name.send_keys(title)
            print("✅ 抖音：视频标题已设置")
            
            # 上传下载封面
            if cover_path and os.path.exists(cover_path):
                try:
                    videos_fengmian = wait_for_element_clickable(self.driver, By.XPATH, "//div[@class='coverControl-CjlzqC' and @style='margin-right: 8px;']")
                    videos_fengmian.click()    
                    time.sleep(2)
                    
                    # 图片缩放到1200*900
                    resize_and_crop(cover_path, cover_path, size=(1200, 900), crop=False)
                    # 上传文件
                    file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @class='semi-upload-hidden-input']")
                    file_input.send_keys(cover_path)
                    print(f"✅ 抖音：封面文件已选择: {cover_path}")
                    # 点击保存按钮
                    wait_for_element(self.driver, By.XPATH, "//button/span[contains(text(), '完成')]").click()
                    print("点击了完成按钮")
            
                except Exception as e:
                    print(f"⚠️ 抖音：封面设置失败: {e}")
                    # 自动设置封面
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
            
            # 等待上传完成
            upload_complete = False
            start_time = time.time()
            while time.time() - start_time < 600:  # 最多等待5分钟
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

            # 发布视频
            videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//button[contains(@class, 'button-dhlUZE')]")
            self.driver.execute_script("arguments[0].click();", videos_fabu)
            print("✅ 抖音：发布按钮已点击")
            
            # 等待发布完成
            time.sleep(5)
            start_time = time.time()
            while time.time() - start_time < 180:  # 最多等待3分钟
                quanbuzhuoqin = check_element_exists(self.driver, By.XPATH, "//div[contains(text(), '全部作品')]")
                if quanbuzhuoqin:
                    print(f"📊 抖音：上传成功")
            
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
                    # 重新发布视频
                    videos_fabu = wait_for_element_clickable(self.driver, By.XPATH, "//button[contains(@class, 'button-dhlUZE')]")
                    self.driver.execute_script("arguments[0].click();", videos_fabu)
                    print("✅ 抖音：重新点击发布按钮")
                    
            print(f"🎉 抖音：视频 '{title}' 发布流程完成")
            return True
                
        except Exception as e:
            print(f"❌ 抖音：上传视频失败: {e}")
            return False
        
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 抖音：浏览器已关闭")