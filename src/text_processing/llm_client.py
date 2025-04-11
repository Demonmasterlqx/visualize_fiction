"""
大语言模型客户端模块

该模块封装了与大语言模型API的交互。
"""

import json
import time
import requests
import yaml
import os
from typing import Dict, List, Any, Optional

from ..utils.logger import get_logger


class LLMClient:
    """大语言模型客户端，封装API调用"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化客户端
        
        Args:
            config: 配置对象，包含API密钥、模型名称等
        """
        self.config = config
        self.api_key = self._load_api_key()
        self.model = config.get('model', 'deepseek-chat')
        self.base_url = "https://api.deepseek.com"  # DeepSeek API基础URL
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
        self.retry_count = config.get('retry_count', 3)
        self.timeout = config.get('timeout', 30)
        self.logger = get_logger(__name__)
        
        self.logger.info(f"LLM客户端初始化完成，使用模型: {self.model}")
    
    def _load_api_key(self) -> str:
        """加载API密钥
        
        Returns:
            str: API密钥
        """
        # 首先检查配置中是否直接提供了API密钥
        api_key = self.config.get('api_key')
        if api_key:
            return api_key
            
        # 然后检查是否提供了API密钥文件路径
        api_key_file = self.config.get('api_key_file')
        if api_key_file:
            try:
                # 获取项目根目录
                root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                api_key_path = os.path.join(root_dir, api_key_file)
                
                # 根据文件扩展名选择解析方法
                if api_key_file.endswith('.json'):
                    with open(api_key_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        return config.get('api_key')
                elif api_key_file.endswith('.yaml') or api_key_file.endswith('.yml'):
                    with open(api_key_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        return config.get('api_key')
                else:
                    # 假设是纯文本文件
                    with open(api_key_path, 'r', encoding='utf-8') as f:
                        return f.read().strip()
            except Exception as e:
                self.logger.error(f"无法从文件加载API密钥: {e}")
                raise ValueError(f"无法从文件加载API密钥: {e}")
        
        # 最后检查环境变量
        api_key_env = os.environ.get('DEEPSEEK_API_KEY')
        if api_key_env:
            return api_key_env
            
        # 如果都没有找到，抛出异常
        raise ValueError("未提供API密钥，请在配置中设置api_key或api_key_file，或设置DEEPSEEK_API_KEY环境变量")
    
    def query(self, prompt: Dict[str, str], json_mode: bool = True) -> str:
        """发送查询到LLM
        
        Args:
            prompt: 提示词，包含system和user部分
            json_mode: 是否启用JSON模式
            
        Returns:
            str: 模型响应
            
        Raises:
            Exception: 如果查询失败
        """
        # 构建消息
        messages = [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]}
        ]
        
        # 构建请求参数
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # 如果启用JSON模式，添加response_format参数
        if json_mode:
            params["response_format"] = {"type": "json_object"}
        
        # 重试机制
        for attempt in range(self.retry_count):
            try:
                # 发送请求
                response = self._send_request(params)
                
                # 解析响应
                content = self._parse_response(response)
                
                # 如果启用JSON模式，验证JSON格式
                if json_mode:
                    try:
                        json.loads(content)
                    except json.JSONDecodeError:
                        self.logger.warning(f"响应不是有效的JSON格式，尝试修复")
                        content = self._fix_json(content)
                
                return content
                
            except Exception as e:
                self.logger.error(f"查询失败 (尝试 {attempt+1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise Exception(f"查询失败，已重试{self.retry_count}次: {e}")
    
    def _send_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到API
        
        Args:
            params: 请求参数
            
        Returns:
            Dict[str, Any]: API响应
            
        Raises:
            Exception: 如果API请求失败
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/v1/chat/completions"
        
        self.logger.debug(f"发送请求到: {url}")
        
        response = requests.post(
            url,
            headers=headers,
            json=params,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            error_msg = f"API请求失败: {response.status_code} {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        """解析API响应
        
        Args:
            response: API响应
            
        Returns:
            str: 模型生成的内容
            
        Raises:
            Exception: 如果无法解析API响应
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            error_msg = f"无法解析API响应: {e}, 响应内容: {response}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def _fix_json(self, text: str) -> str:
        """尝试修复无效的JSON
        
        Args:
            text: 可能包含JSON的文本
            
        Returns:
            str: 修复后的JSON文本
        """
        self.logger.debug("尝试修复JSON格式")
        
        # 尝试提取JSON部分
        import re
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            return json_match.group(1).strip()
        
        # 尝试找到JSON的开始和结束
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx+1]
        
        # 如果无法修复，返回原文本
        self.logger.warning("无法修复JSON格式，返回原文本")
        return text
