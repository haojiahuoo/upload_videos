import os, time, re
from selenium.webdriver.common.by import By
from utils.browser_manager import SmartLoginManager
from config import ACCOUNT_NAME
from utils.image import resize_and_crop
from utils.common_utils import *

class BibiUploader:
    def __init__(self, account_name=ACCOUNT_NAME):
        self.account_name = account_name
        self.manager = SmartLoginManager(site_name="bilibili", account_name=account_name)
        self.driver = None
        
    def upload_to_bibi(self, media_files, platform):
        """批量上传入口"""
        print("\n" + "="*50)
        print("🚀 开始上传到 B站")
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
                if self.fapu_video():
                    record_download(platform, "upload", video_path, "bilibili", True)  # ✅ 上传+发布后移动文件
                    print(f"✅ B站：第 {i} 个视频上传并移动完成")
            else:
                print(f"❌ B站：第 {i} 个视频上传失败")

            if i < len(media_files['videos']):
                print("⏳ 等待 5 秒后继续...")
                time.sleep(5)

        print("🎉 B站：所有视频上传完成")
        self.quit()

    def upload_video(self, video_path, title, cover_path=None):
        """上传视频文件"""
        try:
            print(f"📤 B站：开始上传视频: {title}")
            if "video/frame" not in self.driver.current_url:
                self.driver.get("https://member.bilibili.com/platform/upload/video/frame")
                time.sleep(3)
            
            # 如果没有看到上传视频按钮就刷新网页
            time.sleep(2)
            if check_element_exists(self.driver, By.XPATH, "//div[contains(text(), '稿件投递成功')]"):
                self.driver.refresh()
            buyongle = check_element_exists(self.driver, By.XPATH, "//div[contains(text(), '不用了')]")
            if buyongle:
                wait_for_element(self.driver, By.XPATH, "//div[contains(text(), '不用了')]").click()
            
                
            file_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept]")
            self.driver.execute_script("arguments[0].value = '';", file_input)
            time.sleep(0.5)
            file_input.send_keys(video_path)
            print(f"✅ 视频文件已选择: {title}")

            button_zhidao = check_element_exists(self.driver, By.XPATH, "//button/span[contains(text(), '知道了')]")
            if button_zhidao:
                button_zhidao = wait_for_element(self.driver, By.XPATH, "//button/span[contains(text(), '知道了')]")
                self.driver.execute_script("arguments[0].click();", button_zhidao)
                print("关闭弹窗")
            
            if cover_path and os.path.exists(cover_path):
                if check_element_exists(self.driver, By.XPATH, "//span[text()='更换封面']"):
                    cover = wait_for_element(self.driver, By.XPATH, "//span[text()='更换封面']")
                    self.driver.execute_script("arguments[0].click();", cover)
                    print("点击了更换封面")
                    upload_cover = wait_for_element(self.driver, By.XPATH, "//div[text()='上传封面']")
                    self.driver.execute_script("arguments[0].click();", upload_cover)
                    print("点击了上传封面")
                # 图片缩放到1200*900
                resize_and_crop(cover_path, cover_path, size=(1200, 900), crop=False)
                # 点击上传
                cover_input = wait_for_element(self.driver, By.XPATH, "//input[@type='file' and @accept='image/png, image/jpeg']")
                cover_input.send_keys(cover_path)
                print("点击了上传")
                # 点击完成                                             
                click_cover = wait_for_element(self.driver, By.XPATH, "//button/span[contains(text(), '完成')]")
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", click_cover)
                print("点击了完成")
                print(f"🖼️ 封面已加载: {os.path.basename(cover_path)}")
            else:
                print("⚠️ 未找到封面，使用默认封面")

            
            # 分区操作
            # 1. 点击下拉框
            dropdown = wait_for_element(self.driver, By.XPATH, "//div[@class='video-human-type']//div[@class='select-controller']")
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", dropdown)
            print("已展开下拉菜单")
    
            # 2. 等待并选择户外潮流
            outdoor_option = wait_for_element(self.driver, By.XPATH, "//div[@class='drop-list-v2-item' and @title='户外潮流']")
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", outdoor_option)
            print("已选择户外潮流")

            return True
        except Exception as e:
            print(f"❌ 上传视频失败: {e}")
            return False

    def fapu_video(self):
        """发布视频"""
        try:
            if check_element_exists(self.driver, By.XPATH, "//span[contains(text(), '发布视频')]"):
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

                    while time.time() - start_time < 600:  # 最多等5分钟
                        try:
                            # ✅ 只查找当前任务内部的状态
                            status_spans = self.driver.find_elements(By.XPATH, "//div[@class='file-item-content-status-text']/span")
                            # 检查任意一个span是否包含"上传完成"
                            for span in status_spans:
                                print(span.text)
                            if "上传完成" in span.text.strip():
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
                    time.sleep(2)
                    if check_element_exists(self.driver, By.XPATH, "//div[contains(text(),'稿件投递成功')]"):
                        return True
        except Exception as e:
            print(f"❌ 发布视频时出错: {e}")
            return False

    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🧹 浏览器已关闭")

    