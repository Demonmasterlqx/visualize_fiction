# Visualize_fiction

这是一个基于uv管理的小说可视化项目，目标是实现将小说生成视频的环节自动化，让创作者只用注意其中的几个关键点便可以完成视频的生成。

## 进度

### 2025.4.6

项目立项，探究工作流

## 工作流

**当前工作流假设小说人物肖像不会出现太大改动**  

1. 文本预处理
    1.1 首先将小说按照章节分段，储存下来
    1.2 大模型阅读小说，对于每一章进行分析，提取出重要的角色及其有关信息，按照一定方式储存，按照时间线总结分析主要次要人物，分析出哪些人物需要生成肖像以获得更好的观感，哪些人物的肖像可以直接临场生成
    1.3 大模型根据对应信息，总结输出对应人物的肖像特征，并且整理成为图像生成模型的prompt
2. 肖像生成，建立​​角色特征数据库
   2.1 调用图像生成大模型对于肖像进行生成，并且人工审核后生成对应的肖像库，包含人物不同表情的照片，使用IP Adapter来生成prompt，并且将prompt和对应的图片储存下来
   2.2 建立

## 一些链接

### 理论工具

[【小白】一文读懂CLIP图文多模态模型](https://blog.csdn.net/weixin_47228643/article/details/136690837)

[Midjourney 实现角色一致性的新方法](https://juejin.cn/post/7312759727994028071)

[DALL-E 3 中神奇的格子布局 使用 4 格布局实现了高度的角色一致性](https://myaiforce.com.cn/dalle-3-grid-layout/)

[IP Adapter 实现人物一致性](https://zhuanlan.zhihu.com/p/655898828)

[Stable Diffusion【ControlNet】：ControlNet的IP-Adapter预处理器：SD垫图实现](https://zhuanlan.zhihu.com/p/673371624)

[【小白】一文读懂CLIP图文多模态模型](https://blog.csdn.net/weixin_47228643/article/details/136690837)

### 模型提供

[可灵](https://app.klingai.com/cn/)