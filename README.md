# Generator-Comic

这个小工具可以把任意语言写成的故事翻译成中文的日式动漫对白，并用彩色面板生成一组漫画图片。默认附带了一段“机器猫解释什么是 AI”的示例，适合作为学习教材或灵感样本。

## 功能概览
- 自动检测故事语言并翻译成中文。
- 为每句话添加日式动漫的热血、萌系或旁白风格台词。
- 使用彩色背景、对白框和风格标记生成 PNG 漫画面板。
- 可选自定义字体，方便在不同系统上渲染中文。

## 快速开始
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 运行内置示例（机器猫讲解 AI）：
   ```bash
   python comic_generator.py --demo --output output
   ```
   若已安装 Pillow 和字体，生成的 `output/panel_*.png` 即为彩色漫画面板；
   在缺少依赖的环境下会自动退化为 `panel_*.txt` 文本面板，便于离线查看。
3. 转换自定义故事：
   ```bash
   python comic_generator.py "请在这里输入你的故事" --output my_comic
   ```
   或者从文件读取：
   ```bash
   python comic_generator.py --file story.txt --output my_comic
   ```

> 提示：如果系统没有自带中文字体，可通过 `--font /path/to/font.ttf` 指定字体文件以获得更好的视觉效果。

## 工作原理简述
1. **翻译**：使用 `langdetect` 检测故事语言，通过 `googletrans` 翻译为简体中文。
2. **台词风格化**：对每一句话轮流附加热血、萌系、旁白的动漫风格修饰，让故事更具动画感。
3. **面板绘制**：利用 `Pillow` 绘制彩色背景、对白框和风格角标，输出一张张 PNG 图片。

## 项目结构
- `comic_generator.py`：核心脚本，包含翻译、对白风格化和面板绘制逻辑，亦提供命令行接口；在缺少
  `googletrans`、`langdetect` 或 `Pillow` 的场景下自动降级为本地检测、原文输出和文本面板。
- `requirements.txt`：运行所需的第三方依赖列表。

欢迎根据自己的故事和角色修改台词模板或颜色方案，制作专属动漫教材或创意短篇！
