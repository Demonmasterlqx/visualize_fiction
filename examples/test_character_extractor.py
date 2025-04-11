#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
角色提取器测试脚本

该脚本用于测试角色提取器的功能，使用斗罗大陆小说作为测试数据。
"""

import os
import sys
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.text_processing import ChapterParser, CharacterExtractor
from src.utils.logger import get_logger
from src.utils.config_loader import load_config


def main() -> None:
    """主函数"""
    # 设置日志
    logger = get_logger("test_character_extractor", "DEBUG")
    logger.info("开始测试角色提取器")
    
    try:
        # 加载配置
        config = load_config()
        logger.info("配置加载成功")
        
        # 小说文件路径
        novel_file = "斗罗大陆(1-500章).txt"
        if not os.path.exists(novel_file):
            logger.error(f"小说文件不存在: {novel_file}")
            return
        
        # 初始化章节解析器
        logger.info("初始化章节解析器...")
        chapter_parser = ChapterParser()
        
        # 解析小说文件（仅解析前10章用于测试）
        logger.info(f"解析小说文件: {novel_file}")
        parse_result = chapter_parser.parse_file(
            novel_file,
            save=False  # 不保存章节解析结果
        )
        
        # 提取章节和书籍信息
        chapters = parse_result['result']['chapters']  # 仅使用前10章
        book_info = parse_result['result']['book_info']
        
        logger.info(f"成功解析 {len(chapters)} 个章节")
        
        # 初始化角色提取器
        logger.info("初始化角色提取器...")
        character_extractor_config = config['text_processing']['character_extractor']
        
        # 修改配置，减小批处理大小和最大相关章节数，加快测试速度
        character_extractor_config['extraction']['batch_size'] = 2
        character_extractor_config['extraction']['max_relevant_chapters'] = 3
        
        # 创建输出目录
        output_dir = "data/test_output"
        os.makedirs(output_dir, exist_ok=True)
        character_extractor_config['output_dir'] = output_dir
        
        character_extractor = CharacterExtractor(character_extractor_config)
        
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
        
        # 保存结果到JSON文件
        output_file = os.path.join(output_dir, "test_result.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试结果已保存到: {output_file}")
        logger.info("测试完成")
    
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    main()
