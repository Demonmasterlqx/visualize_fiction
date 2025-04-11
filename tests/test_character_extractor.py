"""
角色提取器测试模块

该模块包含对角色提取器的单元测试。
"""

import os
import json
import pytest
import tempfile
from unittest.mock import MagicMock, patch

from src.text_processing.character_extractor import CharacterExtractor
from src.text_processing.llm_client import LLMClient
from src.text_processing.feature_standardizer import FeatureStandardizer


class TestCharacterExtractor:
    """角色提取器测试类"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """模拟LLM客户端"""
        mock_client = MagicMock(spec=LLMClient)
        
        # 模拟角色提取响应
        mock_client.query.side_effect = lambda prompt, json_mode: self._mock_llm_response(prompt)
        
        return mock_client
    
    @pytest.fixture
    def test_config(self):
        """测试配置"""
        return {
            'llm': {
                'model': 'test-model',
                'api_key': 'test-key',
                'max_tokens': 1000,
                'temperature': 0.5
            },
            'extraction': {
                'batch_size': 2,
                'max_relevant_chapters': 3
            },
            'feature_standardization': {
                'enabled': True,
                'mode': 'all'
            },
            'save_results': False
        }
    
    @pytest.fixture
    def test_chapters(self):
        """测试章节数据"""
        return [
            {
                'title': '第一章 开始',
                'content': '唐三和小舞是好朋友。唐三有着蓝银草武魂，他的老师是大师。小舞有着兔子武魂，她来自星斗大森林。'
            },
            {
                'title': '第二章 发展',
                'content': '唐三和小舞来到了史莱克学院，遇到了戴沐白、奥斯卡、马红俊、宁荣荣和朱竹清。戴沐白是白虎武魂，是史莱克学院的老大。'
            },
            {
                'title': '第三章 比赛',
                'content': '唐昊是唐三的父亲，他是昊天斗罗。比比东是武魂殿的教皇，她对唐三有敌意。'
            }
        ]
    
    def _mock_llm_response(self, prompt):
        """模拟LLM响应"""
        # 根据提示内容返回不同的响应
        user_prompt = prompt.get('user', '')
        
        # 角色提取响应
        if '识别所有角色' in user_prompt:
            if '唐三' in user_prompt and '小舞' in user_prompt:
                return json.dumps({
                    'characters': [
                        {
                            'name': '唐三',
                            'aliases': [],
                            'importance': '主角',
                            'first_appearance': '第一章 开始',
                            'attributes': {
                                'gender': '男',
                                'age': '少年',
                                'occupation': '魂师'
                            }
                        },
                        {
                            'name': '小舞',
                            'aliases': [],
                            'importance': '主角',
                            'first_appearance': '第一章 开始',
                            'attributes': {
                                'gender': '女',
                                'age': '少女',
                                'occupation': '魂师'
                            }
                        }
                    ]
                })
            elif '戴沐白' in user_prompt:
                return json.dumps({
                    'characters': [
                        {
                            'name': '戴沐白',
                            'aliases': [],
                            'importance': '配角',
                            'first_appearance': '第二章 发展',
                            'attributes': {
                                'gender': '男',
                                'age': '少年',
                                'occupation': '魂师'
                            }
                        }
                    ]
                })
            elif '唐昊' in user_prompt:
                return json.dumps({
                    'characters': [
                        {
                            'name': '唐昊',
                            'aliases': ['昊天斗罗'],
                            'importance': '配角',
                            'first_appearance': '第三章 比赛',
                            'attributes': {
                                'gender': '男',
                                'age': '中年',
                                'occupation': '斗罗'
                            }
                        },
                        {
                            'name': '比比东',
                            'aliases': ['教皇'],
                            'importance': '配角',
                            'first_appearance': '第三章 比赛',
                            'attributes': {
                                'gender': '女',
                                'age': '成年',
                                'occupation': '武魂殿教皇'
                            }
                        }
                    ]
                })
        
        # 特征提取响应
        elif '外观特征描述' in user_prompt:
            if '唐三' in user_prompt:
                return json.dumps({
                    'appearance': {
                        'face': '唐三有着清秀的面容，黑色的短发，明亮的眼睛。',
                        'body': '身材匀称，略显瘦弱但充满力量感。',
                        'clothing': '通常穿着简朴的布衣。',
                        'text_references': [
                            {
                                'description': '唐三有着蓝银草武魂',
                                'context': '第一章 开始'
                            }
                        ]
                    }
                })
            elif '小舞' in user_prompt:
                return json.dumps({
                    'appearance': {
                        'face': '小舞有着可爱的脸蛋，粉红色的长发，大大的眼睛。',
                        'body': '身材娇小，灵活敏捷。',
                        'clothing': '通常穿着粉色的裙装。',
                        'text_references': [
                            {
                                'description': '小舞有着兔子武魂',
                                'context': '第一章 开始'
                            }
                        ]
                    }
                })
        
        # 特征标准化响应
        elif '标准化的面部特征描述' in user_prompt:
            return json.dumps({
                'standardized_appearance': {
                    'face': '标准化的面部描述',
                    'structured_features': {
                        'face_shape': '椭圆形',
                        'eyes': '明亮的黑色眼睛',
                        'nose': '挺直的鼻子',
                        'mouth': '薄唇',
                        'eyebrows': '浓密的眉毛',
                        'skin': '健康的肤色',
                        'distinctive_features': '无'
                    }
                }
            })
        
        # 默认响应
        return '{}'
    
    def test_init(self, test_config):
        """测试初始化"""
        extractor = CharacterExtractor(test_config)
        
        assert extractor.config == test_config
        assert extractor.batch_size == 2
        assert extractor.max_relevant_chapters == 3
        assert extractor.output_dir == 'data/characters/'
    
    def test_extract_from_chapters(self, test_config, test_chapters, mock_llm_client):
        """测试从章节提取角色信息"""
        # 创建提取器
        extractor = CharacterExtractor(test_config, mock_llm_client)
        
        # 模拟特征标准化器
        mock_standardizer = MagicMock(spec=FeatureStandardizer)
        mock_standardizer.standardize_features.side_effect = lambda char: char
        extractor.feature_standardizer = mock_standardizer
        
        # 提取角色信息
        result = extractor.extract_from_chapters(test_chapters)
        
        # 验证结果
        assert 'characters' in result
        assert 'metadata' in result
        assert len(result['characters']) > 0
        
        # 验证调用
        assert mock_llm_client.query.call_count >= 3  # 至少调用3次（每个批次一次）
    
    def test_prepare_chapters_text(self, test_config):
        """测试准备章节文本"""
        extractor = CharacterExtractor(test_config)
        
        chapters = [
            {'title': '第一章', 'content': '短内容'},
            {'title': '第二章', 'content': '很长的内容' * 1000}  # 超过3000字符
        ]
        
        text = extractor._prepare_chapters_text(chapters)
        
        assert '章节: 第一章' in text
        assert '短内容' in text
        assert '章节: 第二章' in text
        assert '...' in text  # 长内容被截断
    
    def test_merge_characters(self, test_config):
        """测试合并角色"""
        extractor = CharacterExtractor(test_config)
        
        characters = [
            {
                'name': '唐三',
                'aliases': ['小三'],
                'attributes': {'gender': '男', 'age': None}
            },
            {
                'name': '唐三',  # 重复角色
                'aliases': ['三少'],
                'attributes': {'gender': None, 'age': '少年'}
            },
            {
                'name': '小舞',
                'aliases': [],
                'attributes': {'gender': '女'}
            }
        ]
        
        merged = extractor._merge_characters(characters)
        
        assert len(merged) == 2  # 应该合并为2个角色
        
        # 验证唐三的信息被正确合并
        tang_san = next(c for c in merged if c['name'] == '唐三')
        assert set(tang_san['aliases']) == {'小三', '三少'}
        assert tang_san['attributes']['gender'] == '男'
        assert tang_san['attributes']['age'] == '少年'
    
    def test_find_relevant_chapters(self, test_config, test_chapters):
        """测试查找相关章节"""
        extractor = CharacterExtractor(test_config)
        
        character = {
            'name': '唐三',
            'aliases': ['小三']
        }
        
        relevant = extractor._find_relevant_chapters(character, test_chapters)
        
        assert len(relevant) > 0
        assert any('唐三' in chapter['content'] for chapter in relevant)
    
    def test_save_results(self, test_config):
        """测试保存结果"""
        # 修改配置，启用保存
        config = test_config.copy()
        config['save_results'] = True
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 设置输出目录
            config['output_dir'] = temp_dir
            
            # 创建提取器
            extractor = CharacterExtractor(config)
            
            # 准备测试数据
            results = {
                'characters': [
                    {'name': '唐三', 'id': 'char001'},
                    {'name': '小舞', 'id': 'char002'}
                ],
                'metadata': {
                    'total_characters': 2,
                    'main_characters': 2,
                    'extraction_date': '2025-04-11',
                    'version': '0.01'
                }
            }
            
            book_info = {'title': '测试小说'}
            
            # 保存结果
            filepath = extractor._save_results(results, book_info)
            
            # 验证文件是否创建
            assert os.path.exists(filepath)
            
            # 验证文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                assert saved_data['characters'][0]['name'] == '唐三'
                assert saved_data['characters'][1]['name'] == '小舞'
                assert saved_data['metadata']['total_characters'] == 2


if __name__ == "__main__":
    pytest.main(["-v", __file__])
