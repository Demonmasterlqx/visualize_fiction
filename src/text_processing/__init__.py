"""文本预处理模块

负责处理原始小说文本，包括:
- 章节分割
- 角色信息提取
- prompt生成
"""
from typing import List, Dict

class TextProcessor:
    """文本处理器基类
    
    提供文本处理的基本接口，具体实现可由不同API提供
    """
    
    def split_chapters(self, novel_text: str) -> List[str]:
        """将小说文本按章节分割
        
        Args:
            novel_text: 完整的小说文本
            
        Returns:
            章节列表，每个元素为一章的内容
        """
        raise NotImplementedError
        
    def extract_characters(self, chapter_text: str) -> List[Dict]:
        """从章节文本中提取角色信息
        
        Args:
            chapter_text: 单章小说文本
            
        Returns:
            角色信息列表，每个元素为包含角色特征的字典
        """
        raise NotImplementedError
        
    def generate_prompts(self, character_info: Dict) -> str:
        """生成角色肖像的prompt
        
        Args:
            character_info: 角色特征信息
            
        Returns:
            用于图像生成的prompt文本
        """
        raise NotImplementedError
