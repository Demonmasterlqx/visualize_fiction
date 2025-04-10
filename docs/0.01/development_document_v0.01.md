# Visualize Fiction 开发文档 v0.01

## 文档信息

| 文档属性 | 值 |
|---------|-----|
| 文档名称 | Visualize Fiction 开发文档 |
| 版本号   | v0.01 |
| 创建日期 | 2025-04-11 |
| 最后更新 | 2025-04-11 |
| 状态     | 草稿 |
| 作者     | 项目团队 |

## 目录

1. [开发环境配置](#开发环境配置)
2. [项目结构](#项目结构)
3. [模块实现详情](#模块实现详情)
4. [API文档](#API文档)
5. [测试计划](#测试计划)
6. [部署指南](#部署指南)
7. [常见问题](#常见问题)

## 开发环境配置

### 系统要求

- Python 3.10+
- Node.js 16+（用于前端界面）
- FFmpeg 5.0+
- CUDA 11.7+（用于GPU加速，可选）

### 环境搭建步骤

1. **克隆代码库**

```bash
git clone https://github.com/your-org/visualize-fiction.git
cd visualize-fiction
```

2. **创建虚拟环境**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
# 前端依赖
cd frontend
npm install
cd ..
```

4. **配置环境变量**

创建 `.env` 文件，填入必要的API密钥：

```
GPT_API_KEY=your_openai_api_key
SD_API_KEY=your_stable_diffusion_api_key
AZURE_TTS_KEY=your_azure_tts_api_key
```

5. **验证安装**

```bash
python -m pytest tests/
```

## 项目结构

```
visualize_fiction/
├── config/                  # 配置文件
│   ├── config.yaml          # 主配置文件
│   └── models/              # 模型配置
├── docs/                    # 文档
|   └──0.01            
│       ├── development_plan_v0.01.md  # 开发计划
│       └── development_document_v0.01.md  # 开发文档
├── src/                     # 源代码
│   ├── text_processing/     # 文本预处理模块
│   │   ├── __init__.py
│   │   ├── chapter_parser.py
│   │   ├── character_extractor.py
│   │   └── portrait_feature_extractor.py
│   ├── portrait_generation/ # 肖像生成模块
│   │   ├── __init__.py
│   │   ├── image_generator.py
│   │   ├── portrait_reviewer.py
│   │   └── character_db.py
│   ├── audio_processing/    # 音频处理模块
│   │   ├── __init__.py
│   │   ├── text_splitter.py
│   │   └── tts_engine.py
│   ├── video_synthesis/     # 视频合成模块
│   │   ├── __init__.py
│   │   ├── scene_generator.py
│   │   ├── animation_generator.py
│   │   └── video_composer.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── config_loader.py
│       ├── logger.py
│       └── file_manager.py
├── tests/                   # 测试
│   ├── test_text_processing.py
│   ├── test_portrait_generation.py
│   ├── test_audio_processing.py
│   └── test_video_synthesis.py
├── frontend/                # 前端界面
│   ├── src/
│   ├── public/
│   └── package.json
├── data/                    # 数据目录
│   ├── novels/              # 小说文本
│   ├── characters/          # 角色数据
│   ├── portraits/           # 肖像图片
│   ├── audio/               # 音频文件
│   └── output/              # 输出视频
├── .env                     # 环境变量
├── requirements.txt         # Python依赖
├── setup.py                 # 安装脚本
└── README.md                # 项目说明
```

## 模块实现详情

### 文本预处理模块

#### 章节解析器 (ChapterParser)

**实现文件**: `src/text_processing/chapter_parser.py`

**功能概述**:

章节解析器负责将原始小说文本解析为结构化的章节数据，是文本预处理模块的核心组件。主要功能包括：
- 支持多种文件格式（TXT、EPUB、DOCX等）的读取
- 自动识别章节标题和分隔符
- 处理特殊格式和排版
- 提取章节基本元数据（标题、编号、字数等）
- 将解析结果以结构化格式存储（YAML/JSON）

**详细文档**:

章节解析器的详细设计、实现和使用说明请参考：[章节解析器模块开发文档](chapter_parser_document.md)

#### 角色信息提取器 (CharacterExtractor)

**实现文件**: `src/text_processing/character_extractor.py`

**主要类和方法**:

```python
class CharacterExtractor:
    def __init__(self, config, llm_client):
        """初始化角色提取器
        
        Args:
            config: 配置对象
            llm_client: 大语言模型客户端
        """
        self.config = config
        self.llm_client = llm_client
        
    def extract_characters(self, chapters):
        """从章节中提取角色信息
        
        Args:
            chapters: 章节数据
            
        Returns:
            dict: 角色信息数据库
        """
        # 实现角色提取逻辑
        
    def analyze_relationships(self, characters, chapters):
        """分析角色关系
        
        Args:
            characters: 角色列表
            chapters: 章节数据
            
        Returns:
            dict: 角色关系图
        """
        # 实现关系分析
```

### 肖像生成模块

#### 图像生成引擎 (ImageGenerator)

**实现文件**: `src/portrait_generation/image_generator.py`

**主要类和方法**:

```python
class ImageGenerator:
    def __init__(self, config):
        """初始化图像生成器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.model = self._load_model()
        
    def generate_portraits(self, character_prompt):
        """生成角色肖像
        
        Args:
            character_prompt: 角色描述prompt
            
        Returns:
            list: 生成的图像路径列表
        """
        # 实现图像生成逻辑
        
    def _load_model(self):
        """加载图像生成模型
        
        Returns:
            object: 模型对象
        """
        # 实现模型加载
```

## API文档

### 文本预处理API

```python
from text_processing import ChapterParser, CharacterExtractor

# 初始化解析器
parser = ChapterParser(config)

# 解析小说文件
chapters = parser.parse_file("path/to/novel.txt")

# 提取角色信息
extractor = CharacterExtractor(config, llm_client)
characters = extractor.extract_characters(chapters)
```

### 肖像生成API

```python
from portrait_generation import ImageGenerator, CharacterDatabase

# 初始化生成器
generator = ImageGenerator(config)

# 生成肖像
portraits = generator.generate_portraits(character_prompt)

# 存储到角色数据库
char_db = CharacterDatabase(config)
char_db.add_character(character_id, portraits, character_prompt)
```

## 测试计划

### 单元测试

每个模块的核心功能都应有对应的单元测试，确保基本功能正常工作。

### 集成测试

测试模块间的交互，确保数据流正确传递。

### 端到端测试

测试完整流程，从小说文本输入到最终视频输出。

## 部署指南

### 本地部署

1. 按照[开发环境配置](#开发环境配置)设置环境
2. 修改`config/config.yaml`中的配置
3. 运行主程序：`python src/main.py`

### Docker部署

```bash
# 构建镜像
docker build -t visualize-fiction .

# 运行容器
docker run -v $(pwd)/data:/app/data -p 8080:8080 visualize-fiction
```

## 常见问题

### 1. API密钥配置问题

**问题**: 无法连接到OpenAI API

**解决方案**: 
- 检查`.env`文件中的API密钥是否正确
- 确认网络连接正常
- 检查API使用额度是否已用完

### 2. 图像生成质量问题

**问题**: 生成的角色肖像质量不佳

**解决方案**:
- 调整`config/models/stable_diffusion.yaml`中的参数
- 增加生成步数和CFG scale值
- 优化prompt描述，添加更多细节

### 3. 内存占用过高

**问题**: 处理大型小说时内存不足

**解决方案**:
- 启用增量处理模式：`config.yaml`中设置`incremental_processing: true`
- 减小批处理大小
- 使用SSD缓存：`enable_disk_cache: true`
