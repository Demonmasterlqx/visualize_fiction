# Visualize_fiction

这是一个基于uv管理的小说可视化项目，目标是实现将小说生成视频的环节自动化，让创作者只用注意其中的几个关键点便可以完成视频的生成。

这个项目是受到来自B站的某些up，总是更新到一半就不更了！！！！（或者更的太慢？）

[【26小时精品漫画】得知我和青梅联姻后，一向高冷矜贵的京圈大小姐彻底急了！](https://www.bilibili.com/video/BV1CTQkYfELF?spm_id_from=333.788.videopod.episodes&vd_source=7c5af907927ab5070c4787c2f1712d49&p=5)

## 进度

### 2025.4.6

项目立项，探究工作流

## 工作流

### 0.01

**当前工作流假设小说人物肖像不会出现太大改动**  

详细的开发计划请查看：[开发计划文档 v0.01](docs/development_plan_v0.01.md)

该文档包含以下内容：
- 开发阶段划分与里程碑计划
- 各模块详细开发计划与时间安排
- 技术栈选型与替代方案
- 系统架构设计
- 接口设计规范
- 配置文件设计
- 开发规范
- 风险评估

## 模块解析

### 系统性角色管理策略

```mermaid
graph TD
  A[新场景需求] --> B{角色存在?}
  B -->|是| C[提取特征向量+参考图]
  B -->|否| D[新建角色档案]
  C --> E[参数化约束]
  E --> F[生成质量检测]
  F --> G{CLIP-I>0.85?}
  G -->|否| H[调整参考图权重]
  G -->|是| I[输出]
```

## 一些链接

### 理论工具

[【小白】一文读懂CLIP图文多模态模型](https://blog.csdn.net/weixin_47228643/article/details/136690837)

[Midjourney 实现角色一致性的新方法](https://juejin.cn/post/7312759727994028071)

[DALL-E 3 中神奇的格子布局 使用 4 格布局实现了高度的角色一致性](https://myaiforce.com.cn/dalle-3-grid-layout/)

[IP Adapter 实现人物一致性](https://zhuanlan.zhihu.com/p/655898828)

[Stable Diffusion【ControlNet】：ControlNet的IP-Adapter预处理器：SD垫图实现](https://zhuanlan.zhihu.com/p/673371624)

[【小白】一文读懂CLIP图文多模态模型](https://blog.csdn.net/weixin_47228643/article/details/136690837)

[小红书开源StoryMaker：让图像生成中的角色与背景完美融合，个性化与一致性兼得](https://zhuanlan.zhihu.com/p/11051569775)

[StoryMaker](https://github.com/RedAIGC/StoryMaker)

### 模型提供

[可灵](https://app.klingai.com/cn/)
