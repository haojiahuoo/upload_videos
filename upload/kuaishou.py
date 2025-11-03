# kuaishou.py
import os, time
from selenium.webdriver.common.by import By
from utils.browser_manager import SmartLoginManager
from config import ACCOUNT_NAME
from utils.image import resize_and_crop
from utils.common_utils import *

class KuaishouUploader:
    def __init__(self, account_name=ACCOUNT_NAME):
        self.account_name = account_name
        self.manager = SmartLoginManager(site_name="kuaishou", account_name=account_name)
        self.driver = None
        
    def upload_to_kuaishou(self,media_files, platform):
        """上传到快手"""
        print("\n" + "="*50)
        print("🚀 开始上传到快手")
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
                record_download(platform, "upload", video_path, "kuaishou", True)  # ✅ 上传+发布后移动文件
                print(f"✅ 快手：第 {i} 个视频上传并移动完成")
            else:
                print(f"❌ 快手：第 {i} 个视频上传失败")

            if i < len(media_files['videos']):
                print("⏳ 等待 5 秒后继续...")
                time.sleep(5)

        print("🎉 快手：所有视频上传完成")
        self.quit()

    def upload_video(self, video_path, title, cover_path=None):
        """上传视频到快手"""
        try:
            print(f"📤 快手：开始上传视频: {title}")
            
            # 确保在上传页面 
            if "www.kuaishou.com&source=PROFILE" not in self.driver.current_url: 
                self.driver.get("https://cp.kuaishou.com/article/publish/video?origin=www.kuaishou.com&source=PROFILE/") 
                time.sleep(3)
                
            # 上传文件
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            file_input.send_keys(video_path)
            print(f"✅ 快手：视频文件已选择: {title}")
            
            # 填写视频标题
            videos_title = wait_for_element_clickable(self.driver, By.XPATH, "//div[@id='work-description-edit']")
            videos_title.clear()
            videos_title.send_keys(title)
            print("✅ 快手：视频标题已设置")
            
            # 设置封面
            try:
                # 点击封面设置
                fengmian_shezhi = wait_for_element(self.driver, By.XPATH, "//div[contains(text(), '封面设置')]")
                self.driver.execute_script("arguments[0].click();", fengmian_shezhi)
                # 点击上传封面
                fengmian_shangchuan = wait_for_element(self.driver, By.XPATH, "//div[contains(text(), '上传封面')]")
                self.driver.execute_script("arguments[0].click();", fengmian_shangchuan)
                # 图片缩放到1280*980
                resize_and_crop(cover_path, cover_path, size=(1280, 980), crop=False)
                # 上传照片
                cover_input = wait_for_element(self.driver, By.XPATH, "//div[contains(@class, '_cropper-upload-upload_1i0wh_38')]//input[@type='file']")
                cover_input.send_keys(cover_path)
                time.sleep(1)
                # 点击确定
                fengmian_queding = wait_for_element(self.driver, By.XPATH, "//button/span[contains(text(), '确认')]")
                self.driver.execute_script("arguments[0].click();", fengmian_queding)
            except Exception as e:
                print(f"⚠️ 快速：封面设置失败: {e}")   
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
            
            print(f"🎉 快手：视频 '{title}' 发布流程完成")
            return True
            
        except Exception as e:
            print(f"❌ 快手：上传视频失败: {e}")
            return False
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()