"""
配置加载模块

该模块负责加载和解析配置文件。
"""

import os
import yaml
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径，如果为None则使用默认配置

    Returns:
        Dict[str, Any]: 配置字典

    Raises:
        FileNotFoundError: 如果配置文件不存在
        yaml.YAMLError: 如果配置文件格式错误
    """
    # 如果未指定配置文件路径，使用默认路径
    if config_path is None:
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(root_dir, 'config', 'config.yaml')

    # 检查文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    # 加载配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件格式错误: {e}")


def get_nested_config(config: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    获取嵌套配置项

    Args:
        config: 配置字典
        *keys: 嵌套键路径
        default: 默认值，如果键不存在则返回该值

    Returns:
        Any: 配置值或默认值
    """
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
