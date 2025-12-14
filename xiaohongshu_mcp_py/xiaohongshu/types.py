from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class User(BaseModel):
    """用户信息"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[int] = None  # 0: 未知, 1: 男, 2: 女
    description: Optional[str] = None
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0


class Interaction(BaseModel):
    """互动信息"""
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    collections: Optional[int] = 0
    share_count: Optional[int] = 0


class Tag(BaseModel):
    """标签信息"""
    tag_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[int] = 0  # 0: 普通标签, 1: 话题标签


class Image(BaseModel):
    """图片信息"""
    url: Optional[str] = None
    width: Optional[int] = 0
    height: Optional[int] = 0


class Comment(BaseModel):
    """评论信息"""
    comment_id: Optional[str] = None
    user: Optional[User] = None
    content: Optional[str] = None
    create_time: Optional[str] = None
    likes: Optional[int] = 0
    reply_count: Optional[int] = 0
    reply_comments: Optional[List['Comment']] = None


class Note(BaseModel):
    """笔记信息"""
    note_id: Optional[str] = None
    user: Optional[User] = None
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[Image]] = None
    videos: Optional[List[str]] = None
    tags: Optional[List[Tag]] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    interaction: Optional[Interaction] = None
    comments: Optional[List[Comment]] = None
    url: Optional[str] = None


class Feed(BaseModel):
    """Feed信息"""
    note: Optional[Note] = None
    reason: Optional[str] = None  # 推荐理由
    position: Optional[int] = 0  # 在Feed流中的位置


class FeedResponse(BaseModel):
    """Feed列表响应"""
    feeds: Optional[List[Feed]] = None
    total_count: Optional[int] = 0
    has_more: Optional[bool] = False
    next_cursor: Optional[str] = None


class SearchResult(BaseModel):
    """搜索结果"""
    keyword: Optional[str] = None
    results: Optional[List[Note]] = None
    total_count: Optional[int] = 0
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    total_pages: Optional[int] = 1


class NoteDetailResponse(BaseModel):
    """笔记详情响应"""
    note: Optional[Note] = None
    related_notes: Optional[List[Note]] = None


class PublishRequest(BaseModel):
    """发布请求"""
    images: List[str]
    title: str
    content: str
    tags: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    is_private: Optional[bool] = False
    location: Optional[str] = None


class PublishResponse(BaseModel):
    """发布响应"""
    success: bool
    message: str
    note_id: Optional[str] = None
    publish_time: Optional[str] = None


class CommentRequest(BaseModel):
    """评论请求"""
    note_id: str
    content: str
    reply_to_comment_id: Optional[str] = None


class CommentResponse(BaseModel):
    """评论响应"""
    success: bool
    message: str
    comment_id: Optional[str] = None
    create_time: Optional[str] = None


class LoginStatus(BaseModel):
    """登录状态"""
    is_logged_in: bool
    user_info: Optional[User] = None
    message: Optional[str] = None