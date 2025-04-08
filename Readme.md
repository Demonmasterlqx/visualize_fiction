# 小说可视化项目

## 项目概述
将小说自动生成视频的流程工具，包含以下模块:
- 文本预处理
- 肖像生成
- 音频处理
- 视频合成

## 项目结构
```
visualize_fiction/
├── config.yaml            # YAML格式配置文件
├── src/                  # 主代码目录
│   ├── __init__.py       # 项目主模块
│   ├── text_processing/  # 文本处理模块
│   ├── portrait_generation/ # 肖像生成模块
│   ├── audio_processing/ # 音频处理模块
│   └── video_composition/ # 视频合成模块
├── data/                 # 数据目录(自动创建)
└── output/               # 输出目录(自动创建)
```

## 配置说明
项目使用YAML格式配置文件(config.yaml)，包含:
- 基础路径设置
- 各模块参数配置
- 需要自动创建的目录结构

## 使用方式
1. 编辑config.yaml配置项目参数
2. 实现各模块的具体功能类
3. 通过主程序调用各模块工作流
