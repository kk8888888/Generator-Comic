"""Utility to turn any-language stories into Chinese anime-style comic panels.

This version tolerates environments without external translation or imaging
libraries. If `googletrans`, `langdetect`, or `Pillow` are unavailable, the
script will fall back to best-effort language detection, a no-op translator, and
plain-text panel exports, allowing the app to "run" even in offline containers.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import textwrap
from dataclasses import dataclass
from typing import Iterable, List

_googletrans_spec = importlib.util.find_spec("googletrans")
if _googletrans_spec:
    from googletrans import Translator as _GoogleTranslator
else:
    _GoogleTranslator = None

_langdetect_spec = importlib.util.find_spec("langdetect")
if _langdetect_spec:
    from langdetect import detect as _langdetect_detect
else:
    _langdetect_detect = None

_pillow_spec = importlib.util.find_spec("PIL")
if _pillow_spec:
    from PIL import Image, ImageDraw, ImageFont
else:
    Image = ImageDraw = ImageFont = None


@dataclass
class DialogueLine:
    speaker: str
    text: str
    style: str


class StoryComicGenerator:
    def __init__(self, font_path: str | None = None) -> None:
        self.font_path = font_path
        self._translator = _GoogleTranslator() if _GoogleTranslator else None

    def translate_to_chinese(self, text: str) -> str:
        language = self.detect_language(text)
        if language.startswith("zh"):
            return text
        if self._translator:
            try:
                translation = self._translator.translate(text, dest="zh-cn")
                return translation.text
            except Exception:
                # Continue to fallback logic below.
                pass
        return text

    def detect_language(self, text: str) -> str:
        if _langdetect_detect:
            try:
                return _langdetect_detect(text)
            except Exception:
                pass
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh-cn"
        return "unknown"

    def split_sentences(self, text: str) -> List[str]:
        cleaned = re.sub(r"\s+", " ", text.strip())
        parts = re.split(r"(?<=[。！？!?.])\s+", cleaned)
        return [p for p in parts if p]

    def stylize_dialogues(self, sentences: Iterable[str]) -> List[DialogueLine]:
        speakers = ["未来科学少年", "AI猫搭档", "旁白"]
        styles = ["热血", "萌系", "叙述"]
        dialogues: List[DialogueLine] = []
        for idx, sentence in enumerate(sentences):
            speaker = speakers[idx % len(speakers)]
            style = styles[idx % len(styles)]
            flavored = self._add_anime_flavor(sentence, style)
            dialogues.append(DialogueLine(speaker=speaker, text=flavored, style=style))
        return dialogues

    def _add_anime_flavor(self, sentence: str, style: str) -> str:
        if style == "热血":
            return f"{sentence}！！让梦想燃烧起来！"
        if style == "萌系":
            return f"{sentence}～喵！一切都会变得超可爱！"
        return f"{sentence}（镜头切换，光影闪烁）"

    def render_comic(self, dialogues: List[DialogueLine], output_dir: str, size=(900, 600)) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        paths: List[str] = []
        for idx, dialogue in enumerate(dialogues, start=1):
            if Image:
                panel_path = self._render_image_panel(dialogue, idx, size, output_dir)
            else:
                panel_path = self._render_text_panel(dialogue, idx, output_dir)
            paths.append(panel_path)
        return paths

    def _render_image_panel(self, dialogue: DialogueLine, idx: int, size: tuple[int, int], output_dir: str) -> str:
        width, height = size
        base = Image.new("RGB", size, self._panel_color(idx))
        draw = ImageDraw.Draw(base)
        font = self._load_font(36)
        title_font = self._load_font(40, bold=True)

        padding = 30
        speech_box = [padding, padding + 50, width - padding, height - padding]
        draw.rectangle(speech_box, fill=(255, 255, 255, 180), outline=(255, 156, 187), width=4)

        title = f"第{idx}格 · {dialogue.speaker}"
        draw.text((padding, padding), title, font=title_font, fill=(255, 255, 255))

        wrapped = textwrap.fill(dialogue.text, width=15)
        draw.text((padding + 20, padding + 80), wrapped, font=font, fill=(46, 40, 42))

        draw.text((width - 220, height - 60), f"风格：{dialogue.style}", font=self._load_font(24), fill=(120, 120, 120))
        filename = os.path.join(output_dir, f"panel_{idx:02d}.png")
        base.save(filename)
        return filename

    def _render_text_panel(self, dialogue: DialogueLine, idx: int, output_dir: str) -> str:
        filename = os.path.join(output_dir, f"panel_{idx:02d}.txt")
        wrapped = textwrap.fill(dialogue.text, width=28)
        content = "\n".join(
            [
                f"第{idx}格 · {dialogue.speaker}",
                f"风格：{dialogue.style}",
                "--------------------",
                wrapped,
                "",
            ]
        )
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(content)
        return filename

    def _panel_color(self, idx: int) -> tuple[int, int, int]:
        palette = [
            (255, 87, 127),
            (120, 192, 255),
            (255, 213, 128),
            (180, 236, 170),
            (210, 172, 255),
        ]
        return palette[(idx - 1) % len(palette)]

    def _load_font(self, size: int, bold: bool = False):
        if not ImageFont:
            return None
        if self.font_path:
            return ImageFont.truetype(self.font_path, size=size)
        font_name = "msyhbd.ttc" if bold else "msyh.ttc"
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            return ImageFont.load_default()


def generate_comic_from_story(story: str, output_dir: str, font_path: str | None = None) -> List[str]:
    generator = StoryComicGenerator(font_path=font_path)
    chinese_story = generator.translate_to_chinese(story)
    sentences = generator.split_sentences(chinese_story)
    dialogues = generator.stylize_dialogues(sentences)
    return generator.render_comic(dialogues, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将任何语言的故事转换为中文动漫对白并生成彩色漫画。")
    parser.add_argument("story", help="故事文本内容，或者传入 --file 指定文件。", nargs="?")
    parser.add_argument("--file", dest="file", help="包含故事的文本文件路径。")
    parser.add_argument("--output", dest="output", default="output", help="漫画图片的输出文件夹。")
    parser.add_argument("--font", dest="font", default=None, help="用于渲染中文的字体路径。")
    parser.add_argument("--demo", action="store_true", help="使用内置的机器猫AI示例故事。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not (args.demo or args.file or args.story):
        print("未提供故事文本，自动使用内置示例。可以添加 --help 查看用法细节。")
        args.demo = True

    if args.demo:
        story = """Doraemon 带着小学生解释什么是 AI。\n他们从机器猫的口袋里拿出一本未来教科书，\n教科书会自己说话，告诉孩子们 AI 就像善良的伙伴，\n能帮忙画漫画、写诗歌，还能陪你一起学习。"""
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as fp:
            story = fp.read()
    elif args.story:
        story = args.story
    else:
        raise SystemExit("请提供故事文本、--file 或使用 --demo 示例。")

    panels = generate_comic_from_story(story, args.output, args.font)
    print("已生成漫画：")
    for panel in panels:
        print(panel)


if __name__ == "__main__":
    main()
