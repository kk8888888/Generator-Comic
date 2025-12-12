"""Comic generator that turns any story into Chinese anime-style dialogue.

This script translates an arbitrary story to Simplified Chinese, rewrites it as
expressive anime dialogue, and renders a simple four-panel color comic page.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

try:
    from googletrans import Translator as GoogleTranslator
except ImportError:  # pragma: no cover - optional dependency
    GoogleTranslator = None

from PIL import Image, ImageDraw, ImageFont


@dataclass
class Panel:
    """Represents one panel of the comic page."""

    title: str
    dialogue: str
    color: tuple[int, int, int]


def translate_story(story: str, target_lang: str = "zh-cn") -> str:
    """Translate the incoming story to Chinese using googletrans when available.

    Parameters
    ----------
    story: str
        Arbitrary user-provided story text.
    target_lang: str
        Target language code for translation.
    """

    if GoogleTranslator:
        translator = GoogleTranslator()
        translated = translator.translate(story, dest=target_lang)
        return translated.text

    return f"（翻译模块未安装，以下为原文直出）{story}"


def split_sentences(text: str) -> List[str]:
    """Lightweight sentence splitter that respects Chinese and Latin punctuation."""

    separators = "。！？!?\n"
    sentences: List[str] = []
    buffer: List[str] = []

    def flush():
        if buffer:
            sentences.append("".join(buffer).strip())
            buffer.clear()

    for char in text:
        buffer.append(char)
        if char in separators:
            flush()
    flush()
    return [s for s in sentences if s]


def rewrite_as_anime_dialogue(sentences: Sequence[str]) -> List[str]:
    """Transform raw translated sentences into bouncy anime dialogue lines."""

    anime_tags = [
        "（闪光特写）",
        "（Q版吐槽）",
        "（充满元气地）",
        "（背景音飘过）",
        "（热血BGM起）",
        "（小剧场旁白）",
    ]
    speakers = ["小未来", "知性猫", "AI讲解员", "热血同学", "好奇老师"]

    dialogue: List[str] = []
    for idx, sentence in enumerate(sentences):
        tag = anime_tags[idx % len(anime_tags)]
        speaker = speakers[idx % len(speakers)]
        dialogue.append(f"{speaker}{tag}：{sentence}")
    return dialogue


def build_panels(dialogue: Sequence[str], title: str | None = None) -> List[Panel]:
    """Create four colorful panels from dialogue lines."""

    palette = [
        (247, 106, 108),
        (255, 203, 71),
        (93, 179, 255),
        (138, 201, 87),
    ]
    panels: List[Panel] = []
    chunks = _chunk(dialogue, 4)

    for idx, chunk in enumerate(chunks):
        if not chunk:
            continue
        panel_title = title or "缤纷动漫课堂"
        panels.append(
            Panel(
                title=f"{panel_title} · 第{idx + 1}幕",
                dialogue="\n".join(chunk),
                color=palette[idx % len(palette)],
            )
        )
    return panels


def _chunk(items: Sequence[str], size: int) -> List[List[str]]:
    return [list(items[i : i + size]) for i in range(0, len(items), size)]


def _load_font(font_path: str | None, font_size: int) -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(font_path, font_size)
    return ImageFont.load_default()


def render_comic(panels: Iterable[Panel], output: Path, font_path: str | None = None) -> Path:
    """Render the panels as a 2x2 comic page."""

    panels = list(panels)
    if not panels:
        raise ValueError("No panels to render.")

    width, height = 2400, 2400
    margin = 60
    panel_w = (width - margin * 3) // 2
    panel_h = (height - margin * 3) // 2

    image = Image.new("RGB", (width, height), color=(250, 250, 250))
    draw = ImageDraw.Draw(image)

    title_font = _load_font(font_path, 48)
    body_font = _load_font(font_path, 32)

    for idx, panel in enumerate(panels[:4]):
        row = idx // 2
        col = idx % 2
        x0 = margin + col * (panel_w + margin)
        y0 = margin + row * (panel_h + margin)
        x1 = x0 + panel_w
        y1 = y0 + panel_h
        draw.rectangle((x0, y0, x1, y1), fill=panel.color, outline=(0, 0, 0), width=6)

        title_y = y0 + 18
        draw.text((x0 + 24, title_y), panel.title, font=title_font, fill=(0, 0, 0))

        text_area_w = panel_w - 48
        wrapped = _wrap_text(panel.dialogue, body_font, text_area_w)
        draw.multiline_text(
            (x0 + 24, title_y + 72),
            wrapped,
            font=body_font,
            fill=(15, 15, 15),
            spacing=10,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    return output


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: List[str] = []
    for raw_line in text.split("\n"):
        if not raw_line:
            lines.append("")
            continue
        line = ""
        for char in raw_line:
            if font.getlength(line + char) <= max_width:
                line += char
            else:
                lines.append(line)
                line = char
        lines.append(line)
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story", help="The input story text (any language)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("comic.png"),
        help="Where to write the generated comic image",
    )
    parser.add_argument(
        "-t",
        "--title",
        default=None,
        help="Custom comic title, e.g. '机器猫的AI冒险'",
    )
    parser.add_argument(
        "-f",
        "--font",
        default=None,
        help="Path to a TTF font that支持中文显示; defaults to Pillow's built-in font.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    translated = translate_story(args.story)
    sentences = split_sentences(translated)
    anime_lines = rewrite_as_anime_dialogue(sentences)
    panels = build_panels(anime_lines, args.title)
    render_comic(panels, args.output, args.font)
    print(f"漫画已生成：{args.output}")


if __name__ == "__main__":
    main()
