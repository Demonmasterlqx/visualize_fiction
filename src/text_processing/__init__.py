"""
文本预处理模块

该模块负责处理小说文本，包括章节解析、角色提取和肖像特征提取。
"""

from .chapter_parser import ChapterParser

__all__ = ['ChapterParser']
