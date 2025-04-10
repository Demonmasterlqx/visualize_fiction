#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小说章节解析示例

该脚本展示如何使用章节解析器解析小说文件。
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text_processing import ChapterParser
from src.utils.logger import get_logger


def parse_args() -> Dict[str, Any]:
    """
    解析命令行参数
    
    Returns:
        Dict[str, Any]: 参数字典
    """
    parser = argparse.ArgumentParser(description='小说章节解析工具')
    
    parser.add_argument('file', help='小说文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('--no-save', action='store_true', help='不保存解析结果')
    
    return vars(parser.parse_args())


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args['verbose'] else "INFO"
    logger = get_logger("parse_novel", log_level)
    
    try:
        # 初始化章节解析器
        parser = ChapterParser(args['config'])
        
        # 解析小说文件
        result = parser.parse_file(
            args['file'],
            save=not args['no_save'],
            output_path=args['output']
        )
        
        # 输出解析结果摘要
        book_info = result['result']['book_info']
        logger.info(f"书籍标题: {book_info['title']}")
        logger.info(f"章节数量: {book_info['total_chapters']}")
        logger.info(f"总字数: {book_info['total_words']}")
        
        # 如果保存了结果，显示保存路径
        if not args['no_save'] and 'file_path' in result['save_info']:
            logger.info(f"解析结果已保存到: {result['save_info']['file_path']}")
        
        # 输出章节列表
        logger.info("\n章节列表:")
        for i, chapter in enumerate(result['result']['chapters']):
            logger.info(f"{i+1}. {chapter['title']} ({chapter['word_count']}字)")
    
    except Exception as e:
        logger.error(f"解析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
