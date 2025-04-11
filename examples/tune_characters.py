#!/usr/bin/env python
"""
角色微调工具命令行界面

该脚本提供命令行界面，用于对角色提取器提取的角色形象进行微调和定制。
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.character_tuner import CharacterTuner
from src.utils.config_loader import load_config
from src.utils.logger import get_logger, setup_logger


def setup_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(description='角色微调工具')
    
    # 全局选项
    parser.add_argument('-i', '--input', type=str, required=True, help='输入的角色数据文件')
    parser.add_argument('-o', '--output', type=str, help='输出文件路径')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('--interactive', action='store_true', help='使用交互式模式')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出已提取的角色')
    list_parser.add_argument('--filter', type=str, help='筛选条件，格式为"key=value"，支持多个条件（逗号分隔）')
    
    # view命令
    view_parser = subparsers.add_parser('view', help='查看指定角色的详细信息')
    view_parser.add_argument('character_id', type=str, help='角色ID')
    
    # edit命令
    edit_parser = subparsers.add_parser('edit', help='编辑指定角色的特征')
    edit_parser.add_argument('character_id', type=str, help='角色ID')
    edit_parser.add_argument('--feature', type=str, required=True, help='指定要编辑的特征（face_shape, eyes, etc.）')
    edit_parser.add_argument('--value', type=str, help='设置特征的新值')
    edit_parser.add_argument('--prompt', type=str, help='使用提示重新生成特征')
    
    # batch命令
    batch_parser = subparsers.add_parser('batch', help='批量编辑多个角色')
    batch_parser.add_argument('--filter', type=str, required=True, help='筛选要编辑的角色（如 "importance=主角"）')
    batch_parser.add_argument('--feature', type=str, required=True, help='指定要编辑的特征')
    batch_parser.add_argument('--value', type=str, help='设置特征的新值')
    batch_parser.add_argument('--prompt', type=str, required=True, help='使用提示批量修改特征')
    
    # regenerate命令
    regenerate_parser = subparsers.add_parser('regenerate', help='重新生成角色特征')
    regenerate_parser.add_argument('character_id', type=str, help='角色ID')
    regenerate_parser.add_argument('--keep', type=str, help='保留的特征列表（逗号分隔）')
    regenerate_parser.add_argument('--prompt', type=str, required=True, help='重新生成的提示')
    regenerate_parser.add_argument('--style', type=str, help='应用的风格')
    
    # export命令
    export_parser = subparsers.add_parser('export', help='导出角色信息')
    export_parser.add_argument('character_id', type=str, nargs='?', help='角色ID，如果提供则只导出该角色')
    export_parser.add_argument('--format', type=str, choices=['json', 'yaml'], default='json', help='输出格式')
    
    # undo命令
    subparsers.add_parser('undo', help='撤销上一次编辑')
    
    # redo命令
    subparsers.add_parser('redo', help='重做上一次撤销的编辑')
    
    return parser


def parse_filter(filter_str: str) -> Dict[str, str]:
    """解析筛选条件
    
    Args:
        filter_str: 筛选条件字符串，格式为"key=value"，支持多个条件（逗号分隔）
        
    Returns:
        Dict[str, str]: 筛选条件字典
    """
    if not filter_str:
        return {}
        
    filter_dict = {}
    for item in filter_str.split(','):
        if '=' in item:
            key, value = item.split('=', 1)
            filter_dict[key.strip()] = value.strip()
    
    return filter_dict


def format_character_summary(character: Dict[str, Any]) -> str:
    """格式化角色摘要信息
    
    Args:
        character: 角色信息
        
    Returns:
        str: 格式化后的角色摘要
    """
    char_id = character.get('id', '未知ID')
    name = character.get('name', '未知')
    importance = character.get('importance', '未知')
    gender = character.get('attributes', {}).get('gender', '未知')
    age = character.get('attributes', {}).get('age', '未知')
    occupation = character.get('attributes', {}).get('occupation', '未知')
    
    return f"ID: {char_id}, 名称: {name}, 重要性: {importance}, 性别: {gender}, 年龄: {age}, 职业: {occupation}"


def format_character_detail(character: Dict[str, Any]) -> str:
    """格式化角色详细信息
    
    Args:
        character: 角色信息
        
    Returns:
        str: 格式化后的角色详细信息
    """
    result = []
    
    # 基本信息
    result.append("=== 基本信息 ===")
    result.append(f"ID: {character.get('id', '未知ID')}")
    result.append(f"名称: {character.get('name', '未知')}")
    result.append(f"别名: {', '.join(character.get('aliases', []))}")
    result.append(f"重要性: {character.get('importance', '未知')}")
    result.append(f"首次出现: {character.get('first_appearance', '未知')}")
    
    # 属性
    result.append("\n=== 属性 ===")
    attributes = character.get('attributes', {})
    for key, value in attributes.items():
        result.append(f"{key}: {value}")
    
    # 外观
    result.append("\n=== 外观 ===")
    appearance = character.get('appearance', {})
    
    if 'face' in appearance:
        result.append(f"面部描述: {appearance['face']}")
    
    if 'body' in appearance:
        result.append(f"体型描述: {appearance['body']}")
    
    if 'clothing' in appearance:
        result.append(f"服饰描述: {appearance['clothing']}")
    
    # 结构化特征
    result.append("\n=== 结构化特征 ===")
    structured_features = appearance.get('structured_features', {})
    for key, value in structured_features.items():
        result.append(f"{key}: {value}")
    
    # 编辑历史
    if 'edit_history' in appearance and appearance['edit_history']:
        result.append("\n=== 编辑历史 ===")
        for edit in appearance['edit_history']:
            timestamp = edit.get('timestamp', '未知时间')
            if 'feature' in edit:
                feature = edit.get('feature', '未知特征')
                old_value = edit.get('old_value', '')
                new_value = edit.get('new_value', '')
                result.append(f"{timestamp}: 编辑 {feature}")
                if old_value:
                    result.append(f"  旧值: {old_value}")
                if new_value:
                    result.append(f"  新值: {new_value}")
            elif 'operation' in edit:
                operation = edit.get('operation', '未知操作')
                result.append(f"{timestamp}: {operation}")
                if 'prompt' in edit:
                    result.append(f"  提示: {edit['prompt']}")
                if 'keep_features' in edit:
                    result.append(f"  保留特征: {', '.join(edit['keep_features'] or [])}")
    
    return "\n".join(result)


def interactive_mode(tuner: CharacterTuner, input_file: str, output_file: Optional[str] = None) -> None:
    """交互式模式
    
    Args:
        tuner: 角色微调工具
        input_file: 输入文件路径
        output_file: 输出文件路径，可选
    """
    print("=== 角色微调工具交互式模式 ===")
    print(f"已加载角色数据文件: {input_file}")
    
    while True:
        print("\n请选择操作:")
        print("1. 列出角色")
        print("2. 查看角色详情")
        print("3. 编辑特征")
        print("4. 重新生成特征")
        print("5. 批量编辑")
        print("6. 导出结果")
        print("7. 撤销")
        print("8. 重做")
        print("0. 退出")
        
        choice = input("\n请输入选项编号: ")
        
        if choice == '0':
            print("退出程序")
            break
            
        elif choice == '1':
            # 列出角色
            filter_str = input("请输入筛选条件（可选，格式为'key=value'，支持多个条件用逗号分隔）: ")
            filter_dict = parse_filter(filter_str)
            characters = tuner.list_characters(filter_dict)
            
            print(f"\n找到 {len(characters)} 个角色:")
            for char in characters:
                print(format_character_summary(char))
                
        elif choice == '2':
            # 查看角色详情
            character_id = input("请输入角色ID: ")
            character = tuner.get_character(character_id)
            
            if character:
                print("\n" + format_character_detail(character))
            else:
                print(f"未找到ID为 {character_id} 的角色")
                
        elif choice == '3':
            # 编辑特征
            character_id = input("请输入角色ID: ")
            feature_name = input("请输入要编辑的特征名称: ")
            
            print("\n编辑方式:")
            print("1. 直接设置新值")
            print("2. 使用提示编辑")
            edit_choice = input("请选择编辑方式: ")
            
            if edit_choice == '1':
                new_value = input("请输入新的特征值: ")
                result = tuner.edit_feature(character_id, feature_name, new_value)
                if result:
                    print(f"已成功编辑角色 '{result.get('name', character_id)}' 的 {feature_name} 特征")
                else:
                    print("编辑失败")
            elif edit_choice == '2':
                edit_instruction = input("请输入编辑指令: ")
                result = tuner.edit_feature_with_prompt(character_id, feature_name, edit_instruction)
                if result:
                    print(f"已成功编辑角色 '{result.get('name', character_id)}' 的 {feature_name} 特征")
                else:
                    print("编辑失败")
            else:
                print("无效的选项")
                
        elif choice == '4':
            # 重新生成特征
            character_id = input("请输入角色ID: ")
            prompt = input("请输入生成提示: ")
            keep_str = input("请输入要保留的特征列表（可选，用逗号分隔）: ")
            keep_features = [f.strip() for f in keep_str.split(',')] if keep_str else None
            
            result = tuner.regenerate_features(character_id, prompt, keep_features)
            if result:
                print(f"已成功重新生成角色 '{result.get('name', character_id)}' 的特征")
            else:
                print("重新生成失败")
                
        elif choice == '5':
            # 批量编辑
            filter_str = input("请输入筛选条件（格式为'key=value'，支持多个条件用逗号分隔）: ")
            filter_dict = parse_filter(filter_str)
            feature_name = input("请输入要编辑的特征名称: ")
            edit_instruction = input("请输入编辑指令: ")
            
            results = tuner.batch_edit(filter_dict, feature_name, edit_instruction)
            if results:
                print(f"已成功批量编辑 {len(results)} 个角色的 {feature_name} 特征")
            else:
                print("批量编辑失败")
                
        elif choice == '6':
            # 导出结果
            export_choice = input("是否只导出特定角色？(y/n): ")
            if export_choice.lower() == 'y':
                character_id = input("请输入角色ID: ")
                output_path = tuner.export_characters(output_file, character_id)
            else:
                output_path = tuner.export_characters(output_file)
                
            print(f"已导出角色信息到: {output_path}")
            
        elif choice == '7':
            # 撤销
            if tuner.undo():
                print("撤销成功")
            else:
                print("没有可撤销的编辑")
                
        elif choice == '8':
            # 重做
            if tuner.redo():
                print("重做成功")
            else:
                print("没有可重做的编辑")
                
        else:
            print("无效的选项")


def main():
    """主函数"""
    # 解析命令行参数
    parser = setup_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logger(log_level)
    logger = get_logger(__name__)
    
    # 加载配置
    config = load_config(args.config)
    tuner_config = config.get('character_tuner', {})
    
    # 创建角色微调工具
    tuner = CharacterTuner(tuner_config)
    
    try:
        # 加载角色数据
        tuner.load_characters(args.input)
        
        # 交互式模式
        if args.interactive:
            interactive_mode(tuner, args.input, args.output)
            return
            
        # 非交互式模式
        if args.command == 'list':
            # 列出角色
            filter_dict = parse_filter(args.filter)
            characters = tuner.list_characters(filter_dict)
            
            print(f"找到 {len(characters)} 个角色:")
            for char in characters:
                print(format_character_summary(char))
                
        elif args.command == 'view':
            # 查看角色详情
            character = tuner.get_character(args.character_id)
            
            if character:
                print(format_character_detail(character))
            else:
                print(f"未找到ID为 {args.character_id} 的角色")
                
        elif args.command == 'edit':
            # 编辑特征
            if args.value:
                # 直接设置新值
                result = tuner.edit_feature(args.character_id, args.feature, args.value)
                if result:
                    print(f"已成功编辑角色 '{result.get('name', args.character_id)}' 的 {args.feature} 特征")
                else:
                    print("编辑失败")
            elif args.prompt:
                # 使用提示编辑
                result = tuner.edit_feature_with_prompt(args.character_id, args.feature, args.prompt)
                if result:
                    print(f"已成功编辑角色 '{result.get('name', args.character_id)}' 的 {args.feature} 特征")
                else:
                    print("编辑失败")
            else:
                print("错误: 必须提供 --value 或 --prompt 参数")
                
        elif args.command == 'batch':
            # 批量编辑
            filter_dict = parse_filter(args.filter)
            results = tuner.batch_edit(filter_dict, args.feature, args.prompt)
            if results:
                print(f"已成功批量编辑 {len(results)} 个角色的 {args.feature} 特征")
            else:
                print("批量编辑失败")
                
        elif args.command == 'regenerate':
            # 重新生成特征
            keep_features = args.keep.split(',') if args.keep else None
            result = tuner.regenerate_features(args.character_id, args.prompt, keep_features)
            if result:
                print(f"已成功重新生成角色 '{result.get('name', args.character_id)}' 的特征")
            else:
                print("重新生成失败")
                
        elif args.command == 'export':
            # 导出角色信息
            output_path = tuner.export_characters(args.output, args.character_id)
            print(f"已导出角色信息到: {output_path}")
            
        elif args.command == 'undo':
            # 撤销
            if tuner.undo():
                print("撤销成功")
            else:
                print("没有可撤销的编辑")
                
        elif args.command == 'redo':
            # 重做
            if tuner.redo():
                print("重做成功")
            else:
                print("没有可重做的编辑")
                
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
