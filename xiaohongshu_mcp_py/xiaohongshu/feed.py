from loguru import logger
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class FeedAction:
    def __init__(self, service):
        """初始化Feed操作"""
        self.service = service
        self.page = service.page
        self.feed_url = "https://www.xiaohongshu.com/explore"
    
    def get_feeds(self, page=1, size=20):
        """获取推荐列表
        
        参数:
            page: 页码
            size: 每页数量
        
        返回:
            推荐内容列表
        """
        try:
            logger.info(f"正在获取推荐列表，第 {page} 页，每页 {size} 条")
            
            # 导航到探索页
            self.page.goto(self.feed_url)
            time.sleep(3)
            
            # 等待feed内容加载
            self.page.wait_for_selector('.note-item', timeout=10000)
            
            # 如果需要翻页，执行滚动操作
            if page > 1:
                self._scroll_to_page(page)
            
            # 提取feed数据
            feeds = []
            note_items = self.page.query_selector_all('.note-item')
            
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            
            for item in note_items[start_idx:end_idx]:
                try:
                    feed_data = self._extract_feed_data(item)
                    if feed_data:
                        feeds.append(feed_data)
                except Exception as e:
                    logger.warning(f"提取推荐内容数据失败: {str(e)}")
                    continue
            
            return {
                "page": page,
                "size": size,
                "feeds": feeds,
                "total_count": len(feeds)
            }
            
        except PlaywrightTimeoutError:
            logger.error("推荐内容未找到或超时")
            return {
                "page": page,
                "size": size,
                "feeds": [],
                "total_count": 0,
                "error": "推荐内容加载超时"
            }
        except Exception as e:
            logger.error(f"获取推荐列表失败: {str(e)}")
            return {
                "page": page,
                "size": size,
                "feeds": [],
                "total_count": 0,
                "error": str(e)
            }
    
    def get_note_detail(self, note_id):
        """获取帖子详情
        
        参数:
            note_id: 帖子ID
        
        返回:
            帖子详细信息
        """
        try:
            if not note_id:
                raise ValueError("帖子ID不能为空")
            
            # 构建帖子详情URL
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            logger.info(f"正在获取笔记详情，ID: {note_id}")
            
            # 导航到帖子详情页
            self.page.goto(note_url)
            time.sleep(3)
            
            # 等待页面加载完成
            self.page.wait_for_selector('.note-detail', timeout=10000)
            
            # 提取帖子详细信息
            detail = self._extract_note_detail()
            
            return {
                "note_id": note_id,
                "detail": detail
            }
            
        except PlaywrightTimeoutError:
            logger.error(f"笔记详情未找到或超时，ID: {note_id}")
            return {
                "note_id": note_id,
                "detail": {},
                "error": "帖子详情加载超时"
            }
        except Exception as e:
            logger.error(f"获取笔记详情失败: {str(e)}")
            return {
                "note_id": note_id,
                "detail": {},
                "error": str(e)
            }
    
    def _scroll_to_page(self, page):
        """滚动到指定页码位置"""
        try:
            # 简单实现，每次滚动一定距离
            # 实际实现需要根据具体的加载机制调整
            for _ in range(page - 1):
                self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)  # 等待内容加载
        except Exception as e:
            logger.warning(f"滚动失败: {str(e)}")
    
    def _extract_feed_data(self, feed_item):
        """从feed元素中提取数据"""
        try:
            # 提取笔记ID和URL
            note_link = feed_item.query_selector('a')
            if not note_link:
                return None
            
            href = note_link.get_attribute('href')
            note_id = self._extract_note_id(href)
            
            # 提取封面图
            cover_img = feed_item.query_selector('img')
            cover_url = cover_img.get_attribute('src') if cover_img else ''
            
            # 提取标题
            title_element = feed_item.query_selector('.title')
            title = title_element.inner_text() if title_element else ''
            
            # 提取用户信息
            user_element = feed_item.query_selector('.user-avatar')
            if user_element:
                username = user_element.get_attribute('alt') or ''
            else:
                username = ''
            
            # 提取互动数据
            likes_element = feed_item.query_selector('.likes-count')
            likes = likes_element.inner_text() if likes_element else '0'
            
            return {
                "note_id": note_id,
                "title": title,
                "cover_url": cover_url,
                "username": username,
                "likes": likes,
                "url": href
            }
            
        except Exception as e:
            logger.warning(f"提取推荐内容数据失败: {str(e)}")
            return None
    
    def _extract_note_detail(self):
        """提取帖子详细信息"""
        try:
            # 提取标题
            title_element = self.page.query_selector('.note-title')
            title = title_element.inner_text() if title_element else ''
            
            # 提取内容
            content_element = self.page.query_selector('.note-content')
            content = content_element.inner_text() if content_element else ''
            
            # 提取图片列表
            images = []
            image_elements = self.page.query_selector_all('.note-image')
            for img in image_elements:
                img_url = img.get_attribute('src')
                if img_url:
                    images.append(img_url)
            
            # 提取用户信息
            user_info = {
                "username": self.page.query_selector('.username').inner_text() if self.page.query_selector('.username') else '',
                "avatar": self.page.query_selector('.avatar').get_attribute('src') if self.page.query_selector('.avatar') else ''
            }
            
            # 提取互动数据
            interactions = {
                "likes": self.page.query_selector('.likes-count').inner_text() if self.page.query_selector('.likes-count') else '0',
                "comments": self.page.query_selector('.comments-count').inner_text() if self.page.query_selector('.comments-count') else '0',
                "collections": self.page.query_selector('.collections-count').inner_text() if self.page.query_selector('.collections-count') else '0'
            }
            
            # 提取标签
            tags = []
            tag_elements = self.page.query_selector_all('.tag')
            for tag in tag_elements:
                tags.append(tag.inner_text())
            
            return {
                "title": title,
                "content": content,
                "images": images,
                "user": user_info,
                "interactions": interactions,
                "tags": tags,
                "publish_time": self.page.query_selector('.publish-time').inner_text() if self.page.query_selector('.publish-time') else ''
            }
            
        except Exception as e:
            logger.warning(f"提取笔记详情数据失败: {str(e)}")
            return {}
    
    def _extract_note_id(self, href):
        """从URL中提取笔记ID"""
        try:
            # 假设URL格式为 /explore/6123456789abcdef
            if href.startswith('/explore/'):
                return href.split('/')[2]
            return href
        except:
            return href