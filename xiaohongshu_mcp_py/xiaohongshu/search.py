from loguru import logger
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class SearchAction:
    def __init__(self, service):
        """初始化搜索操作"""
        self.service = service
        self.page = service.page
        self.search_url = "https://www.xiaohongshu.com/search_result/"
    
    def search_content(self, keyword, page=1, size=20):
        """搜索小红书内容
        
        参数:
            keyword: 搜索关键词
            page: 页码
            size: 每页数量
        
        返回:
            搜索结果列表
        """
        try:
            if not keyword:
                raise ValueError("搜索关键词不能为空")
            
            # 构建搜索URL
            search_url = f"https://www.xiaohongshu.com/search_result/{keyword}?page={page}"
            logger.info(f"正在搜索关键词: {keyword} (第 {page} 页)")
            
            # 导航到搜索页面
            self.page.goto(search_url)
            time.sleep(3)
            
            # 等待搜索结果加载
            self.page.wait_for_selector('.note-item', timeout=10000)
            
            # 提取搜索结果
            results = []
            note_items = self.page.query_selector_all('.note-item')
            
            for item in note_items[:size]:  # 限制返回数量
                try:
                    # 提取笔记信息
                    note_data = self._extract_note_data(item)
                    if note_data:
                        results.append(note_data)
                except Exception as e:
                    logger.warning(f"提取笔记数据失败: {str(e)}")
                    continue
            
            # 获取总页数信息（如果有）
            total_pages = self._get_total_pages()
            
            return {
                "keyword": keyword,
                "page": page,
                "total_pages": total_pages,
                "results": results,
                "total_count": len(results)
            }
            
        except PlaywrightTimeoutError:
            logger.error("搜索结果未找到或超时")
            return {
                "keyword": keyword,
                "page": page,
                "results": [],
                "total_count": 0,
                "error": "搜索结果加载超时"
            }
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return {
                "keyword": keyword,
                "page": page,
                "results": [],
                "total_count": 0,
                "error": str(e)
            }
    
    def _extract_note_data(self, note_item):
        """从笔记元素中提取数据"""
        try:
            # 提取笔记ID和URL
            note_link = note_item.query_selector('a')
            if not note_link:
                return None
            
            href = note_link.get_attribute('href')
            note_id = self._extract_note_id(href)
            
            # 提取封面图
            cover_img = note_item.query_selector('img')
            cover_url = cover_img.get_attribute('src') if cover_img else ''
            
            # 提取标题
            title_element = note_item.query_selector('.title')
            title = title_element.inner_text() if title_element else ''
            
            # 提取用户信息
            user_element = note_item.query_selector('.user-info')
            if user_element:
                username = user_element.query_selector('.username').inner_text() if user_element.query_selector('.username') else ''
            else:
                username = ''
            
            # 提取互动数据
            likes_element = note_item.query_selector('.likes')
            likes = likes_element.inner_text() if likes_element else '0'
            
            comments_element = note_item.query_selector('.comments')
            comments = comments_element.inner_text() if comments_element else '0'
            
            return {
                "note_id": note_id,
                "title": title,
                "cover_url": cover_url,
                "username": username,
                "likes": likes,
                "comments": comments,
                "url": href
            }
            
        except Exception as e:
            logger.warning(f"提取笔记数据失败: {str(e)}")
            return None
    
    def _extract_note_id(self, href):
        """从URL中提取笔记ID"""
        try:
            # 假设URL格式为 /explore/6123456789abcdef
            if href.startswith('/explore/'):
                return href.split('/')[2]
            return href
        except:
            return href
    
    def _get_total_pages(self):
        """获取总页数"""
        try:
            # 检查是否有分页控件
            pagination = self.page.query_selector('.pagination')
            if not pagination:
                return 1
            
            # 提取最大页码
            page_links = pagination.query_selector_all('a')
            if not page_links:
                return 1
            
            # 假设最后一个链接是总页数
            # 实际实现需要根据具体的分页结构调整
            return 10  # 简单返回一个默认值，实际应该从页面提取
            
        except Exception as e:
            logger.warning(f"获取总页数失败: {str(e)}")
            return 1