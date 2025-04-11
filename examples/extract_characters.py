#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小说角色提取示例

该脚本展示如何使用角色提取器从小说中提取角色信息。
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text_processing import ChapterParser, CharacterExtractor
from src.utils.logger import get_logger
from src.utils.config_loader import load_config


def parse_args() -> Dict[str, Any]:
    """
    解析命令行参数
    
    Returns:
        Dict[str, Any]: 参数字典
    """
    parser = argparse.ArgumentParser(description='小说角色提取工具')
    
    parser.add_argument('file', help='小说文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('--no-save', action='store_true', help='不保存提取结果')
    parser.add_argument('--no-standardize', action='store_true', help='不进行特征标准化')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--api-key-file', help='API密钥文件路径')
    parser.add_argument('--model', help='LLM模型名称')
    
    return vars(parser.parse_args())


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args['verbose'] else "INFO"
    logger = get_logger("extract_characters", log_level)
    
    try:
        # 加载配置
        config = load_config(args['config'])
        
        # 更新配置
        if args['api_key']:
            config['text_processing']['character_extractor']['llm']['api_key'] = args['api_key']
        if args['api_key_file']:
            config['text_processing']['character_extractor']['llm']['api_key_file'] = args['api_key_file']
        if args['model']:
            config['text_processing']['character_extractor']['llm']['model'] = args['model']
        if args['no_save']:
            config['text_processing']['character_extractor']['save_results'] = False
        if args['no_standardize']:
            config['text_processing']['character_extractor']['feature_standardization']['enabled'] = False
        if args['output']:
            config['text_processing']['character_extractor']['output_dir'] = os.path.dirname(args['output'])
        
        # 初始化章节解析器
        logger.info("初始化章节解析器...")
        chapter_parser = ChapterParser(args['config'])
        
        # 解析小说文件
        logger.info(f"解析小说文件: {args['file']}")
        parse_result = chapter_parser.parse_file(
            args['file'],
            save=False  # 不保存章节解析结果
        )
        
        # 提取章节和书籍信息
        chapters = parse_result['result']['chapters']
        book_info = parse_result['result']['book_info']
        
        logger.info(f"成功解析 {len(chapters)} 个章节")
        
        # 初始化角色提取器
        logger.info("初始化角色提取器...")
        character_extractor = CharacterExtractor(config['text_processing']['character_extractor'])
        
        # 提取角色信息
        logger.info("开始提取角色信息...")
        result = character_extractor.extract_from_chapters(chapters, book_info)
        
        # 输出提取结果摘要
        characters = result['characters']
        metadata = result['metadata']
        
        logger.info(f"提取完成，共找到 {metadata['total_characters']} 个角色，其中主要角色 {metadata['main_characters']} 个")
        
        # 输出主要角色列表
        logger.info("\n主要角色列表:")
        main_characters = [c for c in characters if c.get('importance') == '主角']
        for character in main_characters:
            gender = character.get('attributes', {}).get('gender', '未知')
            age = character.get('attributes', {}).get('age', '未知')
            occupation = character.get('attributes', {}).get('occupation', '未知')
            
            logger.info(f"- {character['name']} ({gender}, {age}, {occupation})")
            
            # 如果有外观描述，显示摘要
            if 'appearance' in character and character['appearance'].get('face'):
                face_desc = character['appearance']['face']
                if len(face_desc) > 100:
                    face_desc = face_desc[:97] + '...'
                logger.info(f"  外观: {face_desc}")
        
        # 如果指定了输出文件，保存结果
        if args['output']:
            output_path = args['output']
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"提取结果已保存到: {output_path}")
    
    except Exception as e:
        logger.error(f"提取失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
