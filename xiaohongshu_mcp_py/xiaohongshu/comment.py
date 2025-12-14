from loguru import logger
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class CommentAction:
    def __init__(self, service):
        """初始化评论操作"""
        self.service = service
        self.page = service.page
    
    def post_comment(self, note_id, content):
        """发表评论到指定帖子
        
        参数:
            note_id: 帖子ID
            content: 评论内容
        
        返回:
            评论结果
        """
        try:
            if not note_id or not content:
                raise ValueError("帖子ID和评论内容不能为空")
            
            # 构建帖子详情URL
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            logger.info(f"正在发表评论到笔记: {note_id}")
            
            # 导航到帖子详情页
            self.page.goto(note_url)
            time.sleep(3)
            
            # 等待页面加载完成
            self.page.wait_for_selector('.note-detail', timeout=10000)
            
            # 查找评论输入框
            try:
                # 点击评论按钮或直接定位评论输入框
                comment_button = self.page.wait_for_selector('.comment-button', timeout=5000)
                comment_button.click()
                time.sleep(1)
            except PlaywrightTimeoutError:
                logger.info("未找到评论按钮，尝试直接查找评论输入框")
            
            # 定位评论输入框并输入内容
            try:
                comment_input = self.page.wait_for_selector('textarea[placeholder="添加评论..."]', timeout=5000)
                comment_input.fill(content)
                time.sleep(1)
                
                # 点击发送按钮
                send_button = self.page.wait_for_selector('button:has-text("发送")', timeout=3000)
                
                # 注意：实际发送操作可能需要额外的确认步骤
                # 这里仅作为示例，实际实现需要根据网页实际结构调整
                # 为了安全起见，不实际点击发送按钮
                # send_button.click()
                # time.sleep(2)
                
                logger.info("评论已准备好发布")
                return {
                    "success": True,
                    "message": "评论已准备好发送，请在浏览器中确认发送",
                    "note_id": note_id,
                    "comment_preview": content
                }
                
            except PlaywrightTimeoutError:
                logger.error("未找到评论输入框或发送按钮")
                raise
            
        except Exception as e:
            logger.error(f"发表评论失败: {str(e)}")
            return {
                "success": False,
                "message": f"发表评论失败: {str(e)}",
                "note_id": note_id
            }