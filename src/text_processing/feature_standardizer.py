"""
特征标准化器模块

该模块负责对角色外观特征进行标准化和结构化处理。
"""

import json
from typing import Dict, List, Any, Optional

from ..utils.logger import get_logger


class FeatureStandardizer:
    """特征标准化器，对角色外观特征进行标准化和结构化处理"""
    
    def __init__(self, config: Dict[str, Any], llm_client=None):
        """初始化特征标准化器
        
        Args:
            config: 配置对象
            llm_client: 大语言模型客户端，如果为None则创建新实例
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # 如果未提供LLM客户端，创建一个新实例
        if llm_client is None:
            from .llm_client import LLMClient
            self.llm_client = LLMClient(config.get('llm', {}))
        else:
            self.llm_client = llm_client
            
        # 加载提示模板
        self.prompts = config.get('prompts', {})
        
        self.logger.info("特征标准化器初始化完成")
    
    def standardize_features(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """标准化角色特征
        
        Args:
            character: 角色信息
            
        Returns:
            Dict[str, Any]: 标准化后的角色信息
        """
        self.logger.info(f"开始标准化角色 '{character.get('name', 'unknown')}' 的特征")
        
        # 检查角色是否有外观信息
        if not character.get('appearance'):
            self.logger.warning(f"角色 '{character.get('name', 'unknown')}' 没有外观信息，无法标准化")
            return character
            
        # 创建标准化提示
        prompt = self._create_standardization_prompt(character)
        
        try:
            # 调用LLM进行标准化
            response = self.llm_client.query(prompt, json_mode=True)
            
            # 解析响应
            standardized_features = self._parse_standardization_response(response)
            
            if standardized_features:
                # 更新角色信息
                if 'appearance' not in character:
                    character['appearance'] = {}
                    
                # 添加标准化的面部描述
                if 'standardized_appearance' in standardized_features:
                    if 'face' in standardized_features['standardized_appearance']:
                        character['appearance']['face'] = standardized_features['standardized_appearance']['face']
                    
                    # 添加结构化特征
                    if 'structured_features' in standardized_features['standardized_appearance']:
                        character['appearance']['structured_features'] = standardized_features['standardized_appearance']['structured_features']
                        
                # 标记为已标准化
                character['appearance']['features_standardized'] = True
                
                self.logger.info(f"角色 '{character.get('name', 'unknown')}' 的特征标准化完成")
            else:
                self.logger.warning(f"角色 '{character.get('name', 'unknown')}' 的特征标准化失败，未返回有效数据")
        
        except Exception as e:
            self.logger.error(f"角色 '{character.get('name', 'unknown')}' 的特征标准化出错: {e}")
        
        return character
    
    def _create_standardization_prompt(self, character: Dict[str, Any]) -> Dict[str, str]:
        """创建标准化提示
        
        Args:
            character: 角色信息
            
        Returns:
            Dict[str, str]: 提示词
        """
        # 使用配置中的提示模板，或使用默认模板
        template = self.prompts.get('feature_standardization', {})
        
        if not template:
            # 使用默认模板
            system_prompt = """
            你是一个专业的文学角色设计师，擅长标准化角色的外观特征描述。
            你的任务是基于提供的角色信息，生成标准化的面部特征描述。
            请严格按照指定的JSON格式返回结果，不要添加任何额外的解释或评论。
            """
            
            # 提取角色信息
            name = character.get('name', '未知')
            gender = character.get('attributes', {}).get('gender', '未知')
            age = character.get('attributes', {}).get('age', '未知')
            occupation = character.get('attributes', {}).get('occupation', '未知')
            face_description = character.get('appearance', {}).get('face', '')
            
            user_prompt = f"""
            请基于以下角色信息，生成标准化的面部特征描述:
            
            角色名称: {name}
            性别: {gender}
            年龄: {age}
            职业: {occupation}
            原有描述: {face_description}
            
            请以JSON格式返回结果，必须包含以下字段:
            
            ```json
            {{
              "standardized_appearance": {{
                "face": "完整的面部描述段落，整合原有描述和补充内容",
                "structured_features": {{
                  "face_shape": "脸型描述（圆形、方形、椭圆形等）",
                  "eyes": "眼睛描述（形状、大小、颜色、特点）",
                  "nose": "鼻子描述（形状、大小、特点）",
                  "mouth": "嘴巴描述（形状、特点）",
                  "eyebrows": "眉毛描述（形状、颜色、特点）",
                  "skin": "肤色和肤质描述",
                  "distinctive_features": "其他显著特征（如疤痕、胎记、雀斑等）"
                }}
              }}
            }}
            ```
            
            重要说明:
            1. 如果原有描述中已有某些特征信息，请保留并整合到标准化描述中
            2. 对于原有描述中没有的特征，请根据角色的性别、年龄、职业等信息合理推断
            3. 确保描述足够详细，以便用于肖像生成
            4. 确保JSON格式正确，可以被直接解析
            """
        else:
            # 使用配置中的模板
            system_prompt = template.get('system', "")
            
            # 提取角色信息
            name = character.get('name', '未知')
            gender = character.get('attributes', {}).get('gender', '未知')
            age = character.get('attributes', {}).get('age', '未知')
            occupation = character.get('attributes', {}).get('occupation', '未知')
            face_description = character.get('appearance', {}).get('face', '')
            
            # 替换模板中的变量
            user_prompt = template.get('user', "").format(
                name=name,
                gender=gender,
                age=age,
                occupation=occupation,
                face_description=face_description
            )
        
        return {"system": system_prompt, "user": user_prompt}
    
    def _parse_standardization_response(self, response: str) -> Dict[str, Any]:
        """解析标准化响应
        
        Args:
            response: LLM响应
            
        Returns:
            Dict[str, Any]: 标准化特征
        """
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"解析标准化响应失败: {e}")
            return {}
