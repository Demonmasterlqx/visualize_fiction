"""
角色微调工具测试模块

该模块包含对角色微调工具的单元测试。
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.character_tuner import CharacterTuner


class TestCharacterTuner(unittest.TestCase):
    """角色微调工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试配置
        self.config = {
            'llm': {
                'model': 'test-model',
                'api_key_file': 'test-api-key-file',
                'max_tokens': 1000,
                'temperature': 0.5,
                'retry_count': 2,
                'timeout': 10,
                'json_mode': True
            },
            'tuning': {
                'history_size': 5,
                'auto_validate': True,
                'default_style': 'test-style'
            },
            'output': {
                'dir': self.temp_dir,
                'backup': True,
                'format': 'json',
                'indent': 2
            },
            'prompts': {
                'feature_edit': {},
                'feature_regenerate': {},
                'batch_edit': {}
            }
        }
        
        # 创建测试角色数据
        self.test_characters = {
            'metadata': {
                'book_title': 'Test Book',
                'total_characters': 2
            },
            'characters': [
                {
                    'id': 'char001',
                    'name': '测试角色1',
                    'aliases': ['小测试'],
                    'importance': '主角',
                    'first_appearance': '第一章',
                    'attributes': {
                        'gender': '男',
                        'age': '25岁',
                        'occupation': '程序员'
                    },
                    'appearance': {
                        'face': '一张普通的脸',
                        'structured_features': {
                            'face_shape': '方形脸',
                            'eyes': '黑色眼睛',
                            'nose': '高挺的鼻子',
                            'mouth': '薄嘴唇',
                            'eyebrows': '浓眉',
                            'skin': '白皙的皮肤',
                            'distinctive_features': '左脸有一颗痣'
                        }
                    }
                },
                {
                    'id': 'char002',
                    'name': '测试角色2',
                    'aliases': ['小测试2'],
                    'importance': '配角',
                    'first_appearance': '第二章',
                    'attributes': {
                        'gender': '女',
                        'age': '22岁',
                        'occupation': '设计师'
                    },
                    'appearance': {
                        'face': '一张漂亮的脸',
                        'structured_features': {
                            'face_shape': '瓜子脸',
                            'eyes': '大眼睛',
                            'nose': '小巧的鼻子',
                            'mouth': '樱桃小嘴',
                            'eyebrows': '细眉',
                            'skin': '白皙的皮肤',
                            'distinctive_features': '无'
                        }
                    }
                }
            ],
            'edit_history': []
        }
        
        # 创建测试数据文件
        self.test_file_path = os.path.join(self.temp_dir, 'test_characters.json')
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_characters, f, ensure_ascii=False, indent=2)
        
        # 创建模拟LLM客户端
        self.mock_llm_client = MagicMock()
        
        # 创建角色微调工具实例
        self.tuner = CharacterTuner(self.config, self.mock_llm_client)
        
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_load_characters(self):
        """测试加载角色数据"""
        # 加载角色数据
        result = self.tuner.load_characters(self.test_file_path)
        
        # 验证结果
        self.assertEqual(len(result['characters']), 2)
        self.assertEqual(result['characters'][0]['id'], 'char001')
        self.assertEqual(result['characters'][1]['id'], 'char002')
        self.assertEqual(result['metadata']['book_title'], 'Test Book')
    
    def test_list_characters(self):
        """测试列出角色"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 列出所有角色
        characters = self.tuner.list_characters()
        self.assertEqual(len(characters), 2)
        
        # 使用筛选条件
        characters = self.tuner.list_characters({'importance': '主角'})
        self.assertEqual(len(characters), 1)
        self.assertEqual(characters[0]['id'], 'char001')
        
        # 使用嵌套筛选条件
        characters = self.tuner.list_characters({'attributes.gender': '女'})
        self.assertEqual(len(characters), 1)
        self.assertEqual(characters[0]['id'], 'char002')
    
    def test_get_character(self):
        """测试获取指定角色"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 获取存在的角色
        character = self.tuner.get_character('char001')
        self.assertIsNotNone(character)
        self.assertEqual(character['name'], '测试角色1')
        
        # 获取不存在的角色
        character = self.tuner.get_character('char999')
        self.assertIsNone(character)
    
    def test_edit_feature(self):
        """测试编辑特征"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 编辑特征
        result = self.tuner.edit_feature('char001', 'eyes', '蓝色眼睛')
        
        # 验证结果
        self.assertEqual(result['appearance']['structured_features']['eyes'], '蓝色眼睛')
        self.assertTrue(result['appearance']['user_edited'])
        self.assertEqual(len(result['appearance']['edit_history']), 1)
        self.assertEqual(result['appearance']['edit_history'][0]['feature'], 'eyes')
        self.assertEqual(result['appearance']['edit_history'][0]['old_value'], '黑色眼睛')
        self.assertEqual(result['appearance']['edit_history'][0]['new_value'], '蓝色眼睛')
        
        # 验证全局编辑历史
        self.assertEqual(len(self.tuner.edit_history), 1)
        self.assertEqual(self.tuner.edit_history[0]['operation'], 'edit_feature')
        self.assertEqual(self.tuner.edit_history[0]['character_id'], 'char001')
        self.assertEqual(self.tuner.edit_history[0]['details']['feature'], 'eyes')
    
    def test_edit_feature_with_prompt(self):
        """测试使用提示编辑特征"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 模拟LLM响应
        self.mock_llm_client.query.return_value = json.dumps({
            'edited_feature': {
                'eyes': '明亮的蓝色眼睛'
            },
            'reasoning': '测试理由'
        })
        
        # 使用提示编辑特征
        result = self.tuner.edit_feature_with_prompt('char001', 'eyes', '改为蓝色')
        
        # 验证结果
        self.assertEqual(result['appearance']['structured_features']['eyes'], '明亮的蓝色眼睛')
        
        # 验证LLM调用
        self.mock_llm_client.query.assert_called_once()
        args, kwargs = self.mock_llm_client.query.call_args
        self.assertEqual(kwargs['json_mode'], True)
        self.assertIn('system', args[0])
        self.assertIn('user', args[0])
    
    def test_regenerate_features(self):
        """测试重新生成特征"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 模拟LLM响应
        self.mock_llm_client.query.return_value = json.dumps({
            'regenerated_appearance': {
                'face': '一张帅气的脸',
                'structured_features': {
                    'face_shape': '方形脸',
                    'eyes': '明亮的蓝色眼睛',
                    'nose': '高挺的鼻子',
                    'mouth': '性感的嘴唇',
                    'eyebrows': '浓眉',
                    'skin': '健康的小麦色皮肤',
                    'distinctive_features': '左脸有一颗痣'
                }
            }
        })
        
        # 重新生成特征，保留某些特征
        result = self.tuner.regenerate_features('char001', '更帅气一些', ['face_shape', 'eyebrows'])
        
        # 验证结果
        self.assertEqual(result['appearance']['face'], '一张帅气的脸')
        self.assertEqual(result['appearance']['structured_features']['face_shape'], '方形脸')  # 保留
        self.assertEqual(result['appearance']['structured_features']['eyebrows'], '浓眉')  # 保留
        self.assertEqual(result['appearance']['structured_features']['eyes'], '明亮的蓝色眼睛')  # 更新
        self.assertEqual(result['appearance']['structured_features']['skin'], '健康的小麦色皮肤')  # 更新
        
        # 验证LLM调用
        self.mock_llm_client.query.assert_called_once()
    
    def test_batch_edit(self):
        """测试批量编辑"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 模拟LLM响应
        self.mock_llm_client.query.return_value = json.dumps({
            'batch_edits': [
                {
                    'character_id': 'char001',
                    'character_name': '测试角色1',
                    'edited_feature': '明亮的蓝色眼睛'
                },
                {
                    'character_id': 'char002',
                    'character_name': '测试角色2',
                    'edited_feature': '明亮的绿色眼睛'
                }
            ],
            'reasoning': '测试理由'
        })
        
        # 批量编辑
        results = self.tuner.batch_edit({}, 'eyes', '更明亮的眼睛')
        
        # 验证结果
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['appearance']['structured_features']['eyes'], '明亮的蓝色眼睛')
        self.assertEqual(results[1]['appearance']['structured_features']['eyes'], '明亮的绿色眼睛')
        
        # 验证LLM调用
        self.mock_llm_client.query.assert_called_once()
    
    def test_export_characters(self):
        """测试导出角色信息"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 编辑特征
        self.tuner.edit_feature('char001', 'eyes', '蓝色眼睛')
        
        # 导出所有角色
        output_path = self.tuner.export_characters()
        
        # 验证导出文件存在
        self.assertTrue(os.path.exists(output_path))
        
        # 验证导出内容
        with open(output_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
            
        self.assertEqual(len(exported_data['characters']), 2)
        self.assertEqual(exported_data['characters'][0]['appearance']['structured_features']['eyes'], '蓝色眼睛')
        
        # 导出单个角色
        output_path = self.tuner.export_characters(character_id='char001')
        
        # 验证导出文件存在
        self.assertTrue(os.path.exists(output_path))
        
        # 验证导出内容
        with open(output_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
            
        self.assertEqual(len(exported_data['characters']), 1)
        self.assertEqual(exported_data['characters'][0]['id'], 'char001')
    
    def test_undo_redo(self):
        """测试撤销和重做"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 编辑特征
        self.tuner.edit_feature('char001', 'eyes', '蓝色眼睛')
        self.assertEqual(self.tuner.get_character('char001')['appearance']['structured_features']['eyes'], '蓝色眼睛')
        
        # 撤销编辑
        result = self.tuner.undo()
        self.assertTrue(result)
        self.assertEqual(self.tuner.get_character('char001')['appearance']['structured_features']['eyes'], '黑色眼睛')
        
        # 重做编辑
        result = self.tuner.redo()
        self.assertTrue(result)
        self.assertEqual(self.tuner.get_character('char001')['appearance']['structured_features']['eyes'], '蓝色眼睛')
    
    def test_validate_features(self):
        """测试验证特征"""
        # 加载角色数据
        self.tuner.load_characters(self.test_file_path)
        
        # 验证完整的特征
        result = self.tuner.validate_features('char001')
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['missing_features']), 0)
        
        # 删除一个特征
        character = self.tuner.get_character('char001')
        del character['appearance']['structured_features']['eyes']
        
        # 验证不完整的特征
        result = self.tuner.validate_features('char001')
        self.assertFalse(result['valid'])
        self.assertIn('eyes', result['missing_features'])
        self.assertIn('使用edit_feature命令添加eyes特征', result['suggestions'])


if __name__ == '__main__':
    unittest.main()
