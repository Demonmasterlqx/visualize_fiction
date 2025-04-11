"""
角色信息提取器模块

该模块负责从小说文本中提取角色信息。
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple

from ..utils.logger import get_logger
from ..utils.file_manager import ensure_dir
from .feature_standardizer import FeatureStandardizer


class CharacterExtractor:
    """角色信息提取器，从小说文本中提取角色信息"""
    
    def __init__(self, config: Dict[str, Any], llm_client=None):
        """初始化角色提取器
        
        Args:
            config: 配置对象
            llm_client: 大语言模型客户端，如果为None则创建新实例
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # 如果未提供LLM客户端，创建一个新实例
        if llm_client is None:
            from .llm_client import LLMClient
            llm_config = config.get('llm', {})
            self.llm_client = LLMClient(llm_config)
        else:
            self.llm_client = llm_client
            
        # 加载提示模板
        self.prompts = config.get('prompts', {})
        
        # 初始化特征标准化器
        self.feature_standardizer = FeatureStandardizer(config, self.llm_client)
        
        # 提取配置
        self.extraction_config = config.get('extraction', {})
        self.batch_size = self.extraction_config.get('batch_size', 5)
        self.max_relevant_chapters = self.extraction_config.get('max_relevant_chapters', 10)
        
        # 输出目录
        self.output_dir = config.get('output_dir', 'data/characters/')
        ensure_dir(self.output_dir)
        
        self.logger.info("角色提取器初始化完成")
    
    def extract_from_chapters(self, chapters: List[Dict[str, Any]], book_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """从章节中提取角色信息
        
        Args:
            chapters: 章节数据列表
            book_info: 书籍信息，可选
            
        Returns:
            Dict[str, Any]: 角色信息数据库
        """
        self.logger.info(f"开始从 {len(chapters)} 个章节中提取角色信息")
        
        # 1. 提取基本角色列表
        basic_characters = self._extract_basic_characters(chapters)
        self.logger.info(f"提取到 {len(basic_characters)} 个基本角色信息")
        
        # 2. 提取详细特征
        detailed_characters = self._extract_detailed_features(basic_characters, chapters)
        self.logger.info(f"完成 {len(detailed_characters)} 个角色的详细特征提取")
        
        # 3. 标准化所有角色的特征描述
        standardization_config = self.config.get('feature_standardization', {})
        if standardization_config.get('enabled', True):
            mode = standardization_config.get('mode', 'all')
            
            # 筛选需要标准化的角色
            characters_to_standardize = []
            for character in detailed_characters:
                if mode == 'all' or \
                   (mode == 'missing' and (not character.get('appearance') or not character['appearance'].get('face'))) or \
                   (mode == 'main' and character.get('importance') == '主角'):
                    characters_to_standardize.append(character)
            
            total_to_standardize = len(characters_to_standardize)
            self.logger.info(f"开始标准化 {total_to_standardize} 个角色的特征")
            
            # 标准化每个角色的特征
            for i, character in enumerate(characters_to_standardize):
                # 输出进度信息
                progress = ((i + 1) / total_to_standardize) * 100
                self.logger.info(f"标准化角色 {i+1}/{total_to_standardize} ({progress:.1f}%): '{character['name']}'...")
                
                # 标准化特征
                character = self.feature_standardizer.standardize_features(character)
            
            self.logger.info(f"完成 {total_to_standardize} 个角色的特征标准化")
        
        # 4. 构建最终数据结构
        result = {
            'characters': detailed_characters,
            'metadata': self._create_metadata(detailed_characters, book_info)
        }
        
        # 5. 保存结果
        if self.config.get('save_results', True):
            self._save_results(result, book_info)
        
        return result
    
    def _extract_basic_characters(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取基本角色列表
        
        Args:
            chapters: 章节数据列表
            
        Returns:
            List[Dict[str, Any]]: 基本角色列表
        """
        # 合并章节文本用于角色提取
        all_characters = []
        total_batches = (len(chapters) + self.batch_size - 1) // self.batch_size
        
        self.logger.info(f"开始提取基本角色信息，共 {total_batches} 个批次")
        
        # 分批处理章节
        for i in range(0, len(chapters), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch_chapters = chapters[i:i+self.batch_size]
            
            # 输出进度信息
            progress = (batch_num / total_batches) * 100
            self.logger.info(f"处理批次 {batch_num}/{total_batches} ({progress:.1f}%)...")
            
            # 合并章节文本
            chapters_text = self._prepare_chapters_text(batch_chapters)
            
            # 创建提示
            prompt = self._create_character_extraction_prompt(chapters_text)
            
            # 调用LLM提取角色
            try:
                response = self.llm_client.query(prompt, json_mode=True)
                batch_characters = self._parse_character_response(response)
                all_characters.extend(batch_characters)
                
                self.logger.info(f"批次 {batch_num}/{total_batches} 完成，提取到 {len(batch_characters)} 个角色")
            except Exception as e:
                self.logger.error(f"批次 {batch_num}/{total_batches} 角色提取失败: {e}")
        
        # 合并和去重角色
        merged_characters = self._merge_characters(all_characters)
        
        # 为每个角色分配ID
        for i, character in enumerate(merged_characters):
            character['id'] = f"char{i+1:03d}"
        
        return merged_characters
    
    def _prepare_chapters_text(self, chapters: List[Dict[str, Any]]) -> str:
        """准备用于提取的章节文本
        
        Args:
            chapters: 章节数据列表
            
        Returns:
            str: 合并的章节文本
        """
        text = ""
        for chapter in chapters:
            title = chapter.get('title', '无标题')
            content = chapter.get('content', '')
            
            text += f"章节: {title}\n\n"
            
            # 如果内容太长，截取前2000个字符和后1000个字符
            if len(content) > 3000:
                text += f"{content[:2000]}...\n...\n{content[-1000:]}\n\n"
            else:
                text += f"{content}\n\n"
                
            text += "---\n\n"
        return text
    
    def _create_character_extraction_prompt(self, chapters_text: str) -> Dict[str, str]:
        """创建角色提取提示
        
        Args:
            chapters_text: 章节文本
            
        Returns:
            Dict[str, str]: 提示词
        """
        # 使用配置中的提示模板，或使用默认模板
        template = self.prompts.get('character_extraction', {})
        
        if not template:
            # 使用默认模板
            system_prompt = """
            你是一个专业的文学分析助手，擅长从小说文本中提取角色信息。
            你的任务是从提供的小说章节中识别所有角色，并按重要性分类。
            请严格按照指定的JSON格式返回结果，不要添加任何额外的解释或评论。
            """
            
            user_prompt = f"""
            请从以下小说章节中识别所有角色，并提供他们的基本信息。
            
            小说章节:
            ```
            {chapters_text}
            ```
            
            请以JSON格式返回结果，必须包含以下字段:
            
            ```json
            {{
              "characters": [
                {{
                  "name": "角色名称",
                  "aliases": ["可能的别名1", "可能的别名2"],
                  "importance": "主角/配角/次要角色",
                  "first_appearance": "首次出现的章节标题或位置",
                  "attributes": {{
                    "gender": "性别",
                    "age": "年龄描述",
                    "occupation": "职业或身份"
                  }}
                }}
              ]
            }}
            ```
            
            重要说明:
            1. 只识别有名字的角色，忽略匿名角色
            2. 主角是故事的核心人物，配角是对故事有重要影响的人物，次要角色是短暂出现或影响有限的人物
            3. 如果某些信息无法确定，使用null值
            4. 确保JSON格式正确，可以被直接解析
            """
        else:
            # 使用配置中的模板
            system_prompt = template.get('system', "")
            user_prompt = template.get('user', "").format(chapters_text=chapters_text)
        
        return {"system": system_prompt, "user": user_prompt}
    
    def _parse_character_response(self, response: str) -> List[Dict[str, Any]]:
        """解析角色提取响应
        
        Args:
            response: LLM响应
            
        Returns:
            List[Dict[str, Any]]: 角色列表
        """
        try:
            data = json.loads(response)
            return data.get('characters', [])
        except json.JSONDecodeError as e:
            self.logger.error(f"解析角色响应失败: {e}")
            return []
    
    def _merge_characters(self, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并和去重角色
        
        Args:
            characters: 角色列表
            
        Returns:
            List[Dict[str, Any]]: 合并后的角色列表
        """
        # 按名称分组
        character_map = {}
        
        for character in characters:
            name = character.get('name', '').strip()
            if not name:
                continue
                
            # 检查是否已存在该角色
            if name in character_map:
                # 合并别名
                existing_aliases = set(character_map[name].get('aliases', []))
                new_aliases = set(character.get('aliases', []))
                merged_aliases = list(existing_aliases.union(new_aliases))
                
                # 更新属性（保留非空值）
                existing_attrs = character_map[name].get('attributes', {})
                new_attrs = character.get('attributes', {})
                
                for key, value in new_attrs.items():
                    if value and (key not in existing_attrs or not existing_attrs[key]):
                        existing_attrs[key] = value
                
                character_map[name]['aliases'] = merged_aliases
                character_map[name]['attributes'] = existing_attrs
                
                # 保留最早的首次出现记录
                if character.get('first_appearance') and not character_map[name].get('first_appearance'):
                    character_map[name]['first_appearance'] = character['first_appearance']
            else:
                # 添加新角色
                character_map[name] = character
        
        # 转换回列表
        return list(character_map.values())
    
    def _extract_detailed_features(self, basic_characters: List[Dict[str, Any]], chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取角色详细特征
        
        Args:
            basic_characters: 基本角色列表
            chapters: 章节数据列表
            
        Returns:
            List[Dict[str, Any]]: 带详细特征的角色列表
        """
        # 根据重要性筛选角色
        importance_threshold = self.extraction_config.get('importance_threshold', {})
        
        # 筛选需要提取详细特征的角色
        characters_to_process = []
        for character in basic_characters:
            importance = character.get('importance', '次要角色')
            if importance == '主角' or importance == '配角':
                characters_to_process.append(character)
        
        total_characters = len(characters_to_process)
        self.logger.info(f"开始提取 {total_characters} 个角色的详细特征")
        
        # 为每个角色提取详细特征
        for i, character in enumerate(characters_to_process):
            # 输出进度信息
            progress = ((i + 1) / total_characters) * 100
            self.logger.info(f"处理角色 {i+1}/{total_characters} ({progress:.1f}%): '{character['name']}'...")
            
            try:
                # 准备相关章节文本
                relevant_chapters = self._find_relevant_chapters(character, chapters)
                chapters_text = self._prepare_chapters_text(relevant_chapters)
                
                # 创建提示
                prompt = self._create_feature_extraction_prompt(character['name'], chapters_text)
                
                # 调用LLM提取特征
                response = self.llm_client.query(prompt, json_mode=True)
                features = self._parse_feature_response(response)
                
                # 更新角色信息
                if features:
                    character.update(features)
                
                self.logger.info(f"角色 '{character['name']}' 的特征提取完成")
            except Exception as e:
                self.logger.error(f"角色 '{character['name']}' 特征提取失败: {e}")
        
        return basic_characters
    
    def _find_relevant_chapters(self, character: Dict[str, Any], chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找与角色相关的章节
        
        Args:
            character: 角色信息
            chapters: 所有章节数据
            
        Returns:
            List[Dict[str, Any]]: 相关章节列表
        """
        # 简单实现：查找包含角色名称的章节
        name = character['name']
        aliases = character.get('aliases', [])
        all_names = [name] + aliases
        
        relevant_chapters = []
        for chapter in chapters:
            content = chapter.get('content', '')
            if any(name in content for name in all_names):
                relevant_chapters.append(chapter)
        
        # 限制章节数量
        return relevant_chapters[:self.max_relevant_chapters]
    
    def _create_feature_extraction_prompt(self, character_name: str, chapters_text: str) -> Dict[str, str]:
        """创建特征提取提示
        
        Args:
            character_name: 角色名称
            chapters_text: 章节文本
            
        Returns:
            Dict[str, str]: 提示词
        """
        # 使用配置中的提示模板，或使用默认模板
        template = self.prompts.get('feature_extraction', {})
        
        if not template:
            # 使用默认模板
            system_prompt = """
            你是一个专业的文学分析助手，擅长从小说文本中提取角色的外观特征描述。
            你的任务是从提供的小说章节中提取指定角色的外观特征。
            请严格按照指定的JSON格式返回结果，不要添加任何额外的解释或评论。
            """
            
            user_prompt = f"""
            请从以下小说章节中提取角色"{character_name}"的外观特征描述。
            
            小说章节:
            ```
            {chapters_text}
            ```
            
            请以JSON格式返回结果，必须包含以下字段:
            
            ```json
            {{
              "appearance": {{
                "face": "面部特征描述，包括原文中提及的所有细节",
                "body": "体型特征描述，包括身高、体格、姿态等",
                "clothing": "服饰特征描述，包括常见着装、特殊装饰等",
                "text_references": [
                  {{
                    "description": "原文中的描述片段",
                    "context": "描述出现的上下文"
                  }}
                ]
              }}
            }}
            ```
            
            重要说明:
            1. 尽可能提取原文中的所有描述，保持原文表述
            2. text_references字段应包含原文中的直接引用，以便验证
            3. 如果某些信息在文本中未提及，使用null值
            4. 确保JSON格式正确，可以被直接解析
            """
        else:
            # 使用配置中的模板
            system_prompt = template.get('system', "")
            user_prompt = template.get('user', "").format(
                character_name=character_name,
                chapters_text=chapters_text
            )
        
        return {"system": system_prompt, "user": user_prompt}
    
    def _parse_feature_response(self, response: str) -> Dict[str, Any]:
        """解析特征提取响应
        
        Args:
            response: LLM响应
            
        Returns:
            Dict[str, Any]: 特征信息
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"解析特征响应失败: {e}")
            return {}
    
    def _create_metadata(self, characters: List[Dict[str, Any]], book_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建元数据
        
        Args:
            characters: 角色列表
            book_info: 书籍信息，可选
            
        Returns:
            Dict[str, Any]: 元数据
        """
        # 统计主要角色数量
        main_characters = sum(1 for c in characters if c.get('importance') == '主角')
        
        # 创建元数据
        metadata = {
            "total_characters": len(characters),
            "main_characters": main_characters,
            "extraction_date": self._get_current_date(),
            "version": "0.01"
        }
        
        # 添加书籍信息
        if book_info:
            metadata["book_title"] = book_info.get('title', '未知')
        
        return metadata
    
    def _get_current_date(self) -> str:
        """获取当前日期
        
        Returns:
            str: 当前日期，格式为YYYY-MM-DD
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _save_results(self, results: Dict[str, Any], book_info: Optional[Dict[str, Any]] = None) -> str:
        """保存提取结果
        
        Args:
            results: 提取结果
            book_info: 书籍信息，可选
            
        Returns:
            str: 保存的文件路径
        """
        # 确定文件名
        if book_info and book_info.get('title'):
            filename = f"{book_info['title']}_characters.json"
        else:
            filename = f"characters_{self._get_current_date()}.json"
        
        # 确保文件名安全
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # 完整路径
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"角色提取结果已保存到: {filepath}")
        
        return filepath
