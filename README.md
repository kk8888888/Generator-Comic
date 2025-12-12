# Generator-Comic

一个把任何语言写成的故事转化为中文动漫对白，并输出彩色漫画页的命令行小工具。

## 功能
- 自动将输入故事翻译为中文（使用 `googletrans`）。
- 将句子重写成充满日式动漫感的对白，角色与旁白自动分配。
- 生成 2x2 彩色漫画页（PNG），适合作为教学或创意草稿，例如机器猫主题的 AI 学习小册子。

## 安装
```bash
pip install -r requirements.txt
```

> 可选：如需自动翻译，可额外安装 `googletrans==4.0.0-rc1`。
> 提示：生成中文文本时请提供支持中文的 TTF 字体路径，否则默认字体可能无法正常显示中文。

## 使用示例
```bash
python comic_generator.py "Doraemon teaches Nobita what artificial intelligence means." \
  --title "机器猫的AI冒险" \
  --font /path/to/your/chinese_font.ttf \
  --output doraemon_ai.png
```

生成的 `doraemon_ai.png` 将包含四个色块分区的漫画页，每个分区内有标题与动漫化的中文对白。

## 开发提示
- 对话拆分采用轻量分句规则，如需更精准的分句或翻译，可自行替换 `translate_story` 或 `split_sentences`。
- 默认使用 2400x2400 画布，若想调整版面可修改 `render_comic` 中的尺寸和间距。
