from playwright.sync_api import sync_playwright
from loguru import logger
import time
import os
from xiaohongshu_mcp_py.xiaohongshu.login import LoginAction
from xiaohongshu_mcp_py.xiaohongshu.publish import PublishAction
from xiaohongshu_mcp_py.xiaohongshu.search import SearchAction
from xiaohongshu_mcp_py.xiaohongshu.feed import FeedAction
from xiaohongshu_mcp_py.xiaohongshu.comment import CommentAction


class XiaohongshuService:
    def __init__(self):
        """初始化小红书服务"""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.init_browser()
        
        # 初始化各功能模块
        self.login_action = LoginAction(self)
        self.publish_action = PublishAction(self)
        self.search_action = SearchAction(self)
        self.feed_action = FeedAction(self)
        self.comment_action = CommentAction(self)
    
    def init_browser(self):
        """初始化浏览器"""
        try:
            headless = os.environ.get('HEADLESS_MODE', 'true').lower() == 'true'
            browser_bin_path = os.environ.get('BROWSER_BIN_PATH', '')
            
            logger.info(f"正在初始化浏览器，无头模式: {headless}")
            self.playwright = sync_playwright().start()
            
            browser_kwargs = {
                'headless': headless,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            }
            
            if browser_bin_path:
                browser_kwargs['executable_path'] = browser_bin_path
            
            self.browser = self.playwright.chromium.launch(**browser_kwargs)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # 设置默认超时
            self.page.set_default_timeout(60000)
            
        except Exception as e:
            logger.error(f"初始化浏览器失败: {str(e)}")
            self.close()
            raise
    
    def check_login_status(self):
        """检查登录状态"""
        return self.login_action.check_login_status()
    
    def publish_content(self, data):
        """发布内容"""
        return self.publish_action.publish_content(data)
    
    def get_feeds(self, page=1, size=20):
        """获取推荐列表"""
        return self.feed_action.get_feeds(page, size)
    
    def search_content(self, keyword, page=1, size=20):
        """搜索内容"""
        return self.search_action.search_content(keyword, page, size)
    
    def get_note_detail(self, note_id):
        """获取帖子详情"""
        return self.feed_action.get_note_detail(note_id)
    
    def post_comment(self, note_id, content):
        """发表评论"""
        return self.comment_action.post_comment(note_id, content)
    
    def close(self):
        """关闭浏览器资源"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"关闭资源时出错: {str(e)}")