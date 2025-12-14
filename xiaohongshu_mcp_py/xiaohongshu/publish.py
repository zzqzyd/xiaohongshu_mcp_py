from loguru import logger
import time
import os
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class PublishAction:
    def __init__(self, service):
        """初始化发布操作"""
        self.service = service
        self.page = service.page
        self.publish_url = "https://creator.xiaohongshu.com/publish/publish-note"
    
    def publish_content(self, data):
        """发布内容到小红书
        
        参数:
            data: 包含发布内容的字典，应包含以下字段:
                - images: 图片路径列表
                - title: 标题
                - content: 正文内容
                - tags: 标签列表
                - topics: 话题列表
        """
        try:
            # 检查必要字段
            if not data or 'images' not in data or 'title' not in data or 'content' not in data:
                raise ValueError("缺少必要的发布字段")
            
            # 导航到发布页面
            self.page.goto(self.publish_url)
            time.sleep(3)
            
            # 1. 上传图片
            logger.info(f"正在上传 {len(data['images'])} 张图片")
            self._upload_images(data['images'])
            time.sleep(2)
            
            # 2. 填写标题
            if 'title' in data:
                logger.info(f"正在设置标题: {data['title']}")
                self.page.fill('input[placeholder="添加标题"]', data['title'])
                time.sleep(1)
            
            # 3. 填写内容
            if 'content' in data:
                logger.info("正在设置内容")
                self.page.fill('textarea[placeholder="分享你的想法..."]', data['content'])
                time.sleep(1)
            
            # 4. 添加标签
            if 'tags' in data and data['tags']:
                logger.info(f"正在添加 {len(data['tags'])} 个标签")
                for tag in data['tags']:
                    self._add_tag(tag)
                    time.sleep(0.5)
            
            # 5. 添加话题
            if 'topics' in data and data['topics']:
                logger.info(f"正在添加 {len(data['topics'])} 个话题")
                for topic in data['topics']:
                    self._add_topic(topic)
                    time.sleep(0.5)
            
            # 6. 发布
            # 注意：实际发布操作可能需要额外的确认步骤
            # 这里仅作为示例，实际实现需要根据网页实际结构调整
            logger.info("正在发布内容")
            # self.page.click('button:has-text("发布")')
            # time.sleep(5)
            
            # 由于可能需要用户确认或有安全验证，这里不实际点击发布按钮
            # 可以返回预览信息或要求用户手动确认
            
            return {
                "success": True,
                "message": "内容准备发布成功，请在浏览器中确认发布",
                "preview": {
                    "title": data.get('title'),
                    "image_count": len(data['images']),
                    "tag_count": len(data.get('tags', [])),
                    "topic_count": len(data.get('topics', []))
                }
            }
            
        except Exception as e:
            logger.error(f"发布内容失败: {str(e)}")
            return {
                "success": False,
                "message": f"发布失败: {str(e)}"
            }
    
    def _upload_images(self, image_paths):
        """上传图片"""
        try:
            # 确保图片路径存在
            valid_paths = []
            for path in image_paths:
                if os.path.exists(path):
                    valid_paths.append(os.path.abspath(path))
                else:
                    logger.warning(f"Image file not found: {path}")
            
            if not valid_paths:
                raise ValueError("没有有效的图片文件")
            
            # 找到文件上传区域并上传文件
            file_input = self.page.wait_for_selector('input[type="file"]', timeout=5000)
            file_input.set_input_files(valid_paths)
            
            # 等待上传完成
            time.sleep(3)  # 简单等待，实际应该检查上传状态
            
        except PlaywrightTimeoutError:
            logger.error("未找到上传区域")
            raise
        except Exception as e:
            logger.error(f"上传图片失败: {str(e)}")
            raise
    
    def _add_tag(self, tag):
        """添加标签"""
        try:
            # 点击标签输入区域
            self.page.click('button:has-text("添加标签")')
            time.sleep(1)
            
            # 输入标签内容
            self.page.fill('input[placeholder="添加标签"]', tag)
            time.sleep(0.5)
            
            # 按回车确认
            self.page.keyboard.press('Enter')
            time.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"添加标签 {tag} 失败: {str(e)}")
            # 继续尝试其他标签，不中断流程
    
    def _add_topic(self, topic):
        """添加话题"""
        try:
            # 点击话题输入区域
            self.page.click('button:has-text("添加话题")')
            time.sleep(1)
            
            # 输入话题内容
            self.page.fill('input[placeholder="搜索话题"]', topic)
            time.sleep(0.5)
            
            # 选择第一个搜索结果
            self.page.click('.topic-item')
            time.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"添加话题 {topic} 失败: {str(e)}")
            # 继续尝试其他话题，不中断流程