#!/usr/bin/env python3
"""
render_illustrated_shorts_mv.py - YouTube Shorts 9:16 Illustrated MV
歌詞のみ表示 ＆ Whisper精密同期版
"""
import os
import sys
import math
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 1080
HEIGHT = 1920
FPS = 30
BPM = 200
BEAT_SEC = 60.0 / BPM  # 0.30s per beat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG1_PATH = os.path.join(BASE_DIR, "assets", "chara_happy.jpg")
IMG2_PATH = os.path.join(BASE_DIR, "assets", "chara_panic.jpg")
AUDIO_PATH = os.path.join(BASE_DIR, "hairan_dani_full_lyrics.mp3")
OUTPUT_PATH = os.path.join(BASE_DIR, "hairan_dani_shorts_mv.mp4")
DOWNLOADS_OUTPUT_PATH = "/Users/pupu/Downloads/hairan_dani_shorts_mv.mp4"
FRAMES_DIR = "/tmp/mv_illustrated_frames"

FONT_TSUKUSHI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/60484a5d6f3fa8d51dcbeff43b7e70c9d42bcd2f.asset/AssetData/TsukushiBMaruGothic.ttc"
FONT_FALLBACK = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"

def get_font(size):
    font_path = FONT_TSUKUSHI if os.path.exists(FONT_TSUKUSHI) else FONT_FALLBACK
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

# Whisper実測同期タイムライン (秒単位)
# 歌詞以外の文字は一切含めず、純粋な歌詞のみ
TIMELINE = [
    # 0.0 - 0.92s: 前奏
    {
        "start": 0.0, "end": 0.92,
        "img": 1, "trans": "fade", "fade_dur": 0.3, "zoom": 1.0,
        "lyrics": "",
        "theme": "pink"
    },
    # 0.92 - 3.96s: 行きは入った荷物が
    {
        "start": 0.92, "end": 3.96,
        "img": 1, "trans": "cut", "zoom": 1.03,
        "lyrics": "行きは入った荷物が",
        "theme": "pink"
    },
    # 3.96 - 5.50s: 帰りは入らんだに！
    {
        "start": 3.96, "end": 5.50,
        "img": 2, "trans": "cut", "zoom": 1.10,
        "lyrics": "帰りは入らんだに！",
        "theme": "red"
    },
    # 5.50 - 8.64s: 行きは入った荷物が
    {
        "start": 5.50, "end": 8.64,
        "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.03,
        "lyrics": "行きは入った荷物が",
        "theme": "cyan"
    },
    # 8.64 - 10.20s: 帰りは入らんだに！
    {
        "start": 8.64, "end": 10.20,
        "img": 2, "trans": "cut", "zoom": 1.12,
        "lyrics": "帰りは入らんだに！",
        "theme": "orange"
    },
    # 10.20 - 11.00s: 入った！
    {
        "start": 10.20, "end": 11.00,
        "img": 1, "trans": "cut", "zoom": 1.12,
        "lyrics": "入った！",
        "theme": "mint"
    },
    # 11.00 - 11.84s: 入らん！
    {
        "start": 11.00, "end": 11.84,
        "img": 2, "trans": "cut", "zoom": 1.15,
        "lyrics": "入らん！",
        "theme": "red"
    },
    # 11.84 - 12.65s: 入った！
    {
        "start": 11.84, "end": 12.65,
        "img": 1, "trans": "cut", "zoom": 1.12,
        "lyrics": "入った！",
        "theme": "yellow"
    },
    # 12.65 - 14.50s: 入らん！
    {
        "start": 12.65, "end": 14.50,
        "img": 2, "trans": "cut", "zoom": 1.16,
        "lyrics": "入らん！",
        "theme": "purple"
    },
    # 14.50 - 17.16s: 同じカバン！同じギア！
    {
        "start": 14.50, "end": 17.16,
        "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.02,
        "lyrics": "同じカバン！同じギア！",
        "theme": "blue"
    },
    # 17.16 - 20.00s: 増えとらんに！増えとらんに！
    {
        "start": 17.16, "end": 20.00,
        "img": 2, "trans": "fade", "fade_dur": 0.25, "zoom": 1.08,
        "lyrics": "増えとらんに！増えとらんに！",
        "theme": "coral"
    },
    # 20.00 - 22.42s: なんでだや！？パンパンだに！ (サビ突入！)
    {
        "start": 20.00, "end": 22.42,
        "img": 2, "trans": "flash", "zoom": 1.22,
        "lyrics": "なんでだや！？パンパンだに！",
        "theme": "chorus_electric"
    },
    # 22.42 - 24.86s: チャックがパンパンだら！
    {
        "start": 22.42, "end": 24.86,
        "img": 2, "trans": "cut", "zoom": 1.18,
        "lyrics": "チャックがパンパンだら！",
        "theme": "chorus_yellow"
    },
    # 24.86 - 26.54s: 行きはスッポリ！
    {
        "start": 24.86, "end": 26.54,
        "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.06,
        "lyrics": "行きはスッポリ！",
        "theme": "mint"
    },
    # 26.54 - 29.62s: 帰りはパンパンだに！
    {
        "start": 26.54, "end": 29.62,
        "img": 2, "trans": "cut", "zoom": 1.18,
        "lyrics": "帰りはパンパンだに！",
        "theme": "pink"
    },
    # 29.62 - 31.52s: 入らん！入らん！
    {
        "start": 29.62, "end": 31.52,
        "img": 2, "trans": "cut", "zoom": 1.14,
        "lyrics": "入らん！入らん！",
        "theme": "orange"
    },
    # 31.52 - 34.50s: ばか入らん！
    {
        "start": 31.52, "end": 34.50,
        "img": 2, "trans": "cut", "zoom": 1.24,
        "lyrics": "ばか入らん！",
        "theme": "dark_red"
    },
    # 34.50 - 37.14s: 行きは入った荷物が
    {
        "start": 34.50, "end": 37.14,
        "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.03,
        "lyrics": "行きは入った荷物が",
        "theme": "cyan"
    },
    # 37.14 - 40.50s: 帰りは入らんだに！！
    {
        "start": 37.14, "end": 40.50,
        "img": 2, "trans": "cut", "zoom": 1.22,
        "lyrics": "帰りは入らんだに！！",
        "theme": "rainbow"
    },
    # 40.50 - 45.00s: アウトロ (余韻)
    {
        "start": 40.50, "end": 45.00,
        "img": 2, "trans": "fade", "fade_dur": 0.5, "zoom": 1.05,
        "lyrics": "",
        "theme": "pink"
    }
]

THEMES = {
    "pink": {
        "text": (255, 45, 120), "stroke": (255, 255, 255), "shadow": (180, 15, 75)
    },
    "red": {
        "text": (235, 20, 45), "stroke": (255, 255, 255), "shadow": (145, 5, 20)
    },
    "cyan": {
        "text": (0, 155, 230), "stroke": (255, 255, 255), "shadow": (0, 85, 155)
    },
    "orange": {
        "text": (250, 85, 20), "stroke": (255, 255, 255), "shadow": (165, 45, 10)
    },
    "yellow": {
        "text": (250, 120, 10), "stroke": (255, 255, 255), "shadow": (170, 65, 5)
    },
    "mint": {
        "text": (10, 175, 135), "stroke": (255, 255, 255), "shadow": (5, 105, 80)
    },
    "purple": {
        "text": (135, 45, 225), "stroke": (255, 255, 255), "shadow": (85, 15, 155)
    },
    "blue": {
        "text": (30, 95, 235), "stroke": (255, 255, 255), "shadow": (15, 55, 155)
    },
    "coral": {
        "text": (240, 65, 90), "stroke": (255, 255, 255), "shadow": (165, 30, 50)
    },
    "dark_red": {
        "text": (255, 240, 50), "stroke": (215, 10, 35), "shadow": (40, 0, 10)
    },
    "chorus_electric": {
        "text": (255, 240, 40), "stroke": (255, 20, 105), "shadow": (70, 10, 45)
    },
    "chorus_yellow": {
        "text": (255, 35, 115), "stroke": (255, 255, 255), "shadow": (165, 10, 70)
    },
    "rainbow": {
        "text": (255, 240, 50), "stroke": (235, 30, 125), "shadow": (50, 10, 90)
    }
}

RAW_IMG1 = Image.open(IMG1_PATH).convert("RGB")
RAW_IMG2 = Image.open(IMG2_PATH).convert("RGB")

def make_blurred_bg(img):
    w, h = img.size
    target_aspect = WIDTH / float(HEIGHT)
    cur_aspect = w / float(h)
    if cur_aspect > target_aspect:
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        crop_box = (left, 0, left + new_w, h)
    else:
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        crop_box = (0, top, w, top + new_h)

    cropped = img.crop(crop_box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
    blurred = cropped.filter(ImageFilter.GaussianBlur(32))
    dim = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    return Image.blend(blurred, dim, 0.32)

BG1 = make_blurred_bg(RAW_IMG1)
BG2 = make_blurred_bg(RAW_IMG2)

def draw_sticker_text(draw, cx, cy, text, font, fill_col, stroke_col, shadow_col, stroke_w=16, shadow_off=16):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = cx - tw // 2
    y = cy - th // 2

    # 3D shadow
    for sx in range(1, shadow_off + 1, 2):
        for sy in range(1, shadow_off + 1, 2):
            draw.text((x + sx, y + sy), text, font=font, fill=shadow_col)

    # Stroke
    for dx in range(-stroke_w, stroke_w + 1, 3):
        for dy in range(-stroke_w, stroke_w + 1, 3):
            if dx * dx + dy * dy <= stroke_w * stroke_w:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_col)

    # Main text
    draw.text((x, y), text, font=font, fill=fill_col)
    return tw, th

def fit_font_size(text, max_w, initial_size, min_size=48):
    sz = initial_size
    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    while sz > min_size:
        f = get_font(sz)
        bb = d.textbbox((0, 0), text, font=f)
        if (bb[2] - bb[0]) <= max_w:
            return f, sz
        sz -= 4
    return get_font(min_size), min_size

def render_frame(f, total_frames):
    t = f / float(FPS)

    # セグメント探索
    cur_idx = len(TIMELINE) - 1
    for idx, seg in enumerate(TIMELINE):
        if seg["start"] <= t < seg["end"]:
            cur_idx = idx
            break

    cur_seg = TIMELINE[cur_idx]
    prev_seg = TIMELINE[cur_idx - 1] if cur_idx > 0 else cur_seg

    seg_elapsed = t - cur_seg["start"]

    # トランジション
    alpha = 1.0
    is_fading = False
    flash_alpha = 0.0
    if cur_seg["trans"] == "fade" and cur_idx > 0:
        fade_dur = cur_seg.get("fade_dur", 0.3)
        if seg_elapsed < fade_dur:
            alpha = seg_elapsed / fade_dur
            is_fading = True
    elif cur_seg["trans"] == "flash":
        if seg_elapsed < 0.15:
            flash_alpha = 1.0 - (seg_elapsed / 0.15)

    # 背景合成
    cur_raw = RAW_IMG1 if cur_seg["img"] == 1 else RAW_IMG2
    prev_raw = RAW_IMG1 if prev_seg["img"] == 1 else RAW_IMG2

    cur_bg = BG1 if cur_seg["img"] == 1 else BG2
    prev_bg = BG1 if prev_seg["img"] == 1 else BG2

    if is_fading:
        bg = Image.blend(prev_bg, cur_bg, alpha)
    else:
        bg = cur_bg.copy()

    # 前景イラストフレーム
    zoom = cur_seg.get("zoom", 1.0)
    beat_phase = (t % BEAT_SEC) / BEAT_SEC
    pulse = math.sin(beat_phase * math.pi) * 0.02
    total_zoom = zoom + pulse

    shake_x = 0
    shake_y = 0
    if "！" in cur_seg["lyrics"] or "？" in cur_seg["lyrics"]:
        if "chorus" in cur_seg["theme"] or "dark" in cur_seg["theme"] or "rainbow" in cur_seg["theme"]:
            shake_x = random.randint(-8, 8) if (f % 2 == 0) else 0
            shake_y = random.randint(-8, 8) if (f % 2 == 0) else 0

    frame_w = 1000
    frame_h = int(1000 * 572 / 1024)  # 558
    frame_x = (WIDTH - frame_w) // 2 + shake_x
    # 画面の中央やや上寄りに配置し、上下のバランスを完璧に保つ
    frame_y = 520 + shake_y

    def get_zoomed_cropped_image(raw_img, z):
        rw, rh = raw_img.size
        cw, ch = int(rw / z), int(rh / z)
        cx = rw // 2
        cy = int(rh * 0.45)
        left = max(0, min(rw - cw, cx - cw // 2))
        top = max(0, min(rh - ch, cy - ch // 2))
        cropped = raw_img.crop((left, top, left + cw, top + ch))
        return cropped.resize((frame_w, frame_h), Image.Resampling.BILINEAR)

    fg_cur = get_zoomed_cropped_image(cur_raw, total_zoom)
    if is_fading:
        fg_prev = get_zoomed_cropped_image(prev_raw, prev_seg.get("zoom", 1.0))
        fg_composite = Image.blend(fg_prev, fg_cur, alpha)
    else:
        fg_composite = fg_cur

    # 角丸マスク
    mask = Image.new("L", (frame_w, frame_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, frame_w, frame_h], radius=36, fill=255)

    # シャドウ
    shadow_mask = Image.new("RGBA", (frame_w + 32, frame_h + 32), (0, 0, 0, 0))
    ImageDraw.Draw(shadow_mask).rounded_rectangle([16, 16, frame_w + 16, frame_h + 16], radius=36, fill=(0, 0, 0, 130))
    shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(14))
    bg.paste(shadow_blur, (frame_x - 16, frame_y - 16), shadow_blur)

    # 前景貼り付け
    bg.paste(fg_composite, (frame_x, frame_y), mask)

    # 白枠フレーム
    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle([frame_x, frame_y, frame_x + frame_w, frame_y + frame_h], radius=36, outline=(255, 255, 255), width=8)

    # 歌詞テキスト描画（歌詞以外の文字は一切描画しない）
    lyrics = cur_seg["lyrics"].strip()
    if lyrics:
        theme = THEMES.get(cur_seg["theme"], THEMES["pink"])

        # 登場時の可愛いポップバウンス
        entrance_scale = 1.0
        if seg_elapsed < 0.16:
            entrance_scale = 1.0 + (0.16 - seg_elapsed) * 1.0
        scale = entrance_scale + pulse

        usable_w = WIDTH - 140  # 940px (左右70pxセーフマージン)

        # サビや短文なら大きく、長文なら画面内にぴったり収まるサイズ
        if len(lyrics) <= 4:
            base_sz = 140
        elif len(lyrics) <= 6:
            base_sz = 120
        elif len(lyrics) <= 10:
            base_sz = 100
        else:
            base_sz = 86

        font, actual_sz = fit_font_size(lyrics, usable_w, int(base_sz * scale))

        # イラスト枠の下側（Y: 1320）に配置
        lyric_center_y = 1330 + shake_y

        draw_sticker_text(
            draw, WIDTH // 2 + shake_x, lyric_center_y, lyrics, font,
            theme["text"], theme["stroke"], theme["shadow"],
            stroke_w=18, shadow_off=16
        )

    # サビの白フラッシュ
    if flash_alpha > 0:
        white = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        bg = Image.blend(bg, white, flash_alpha * 0.75)

    return bg

def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    total_duration = 45.0
    total_frames = int(total_duration * FPS)

    print(f"[INFO] Rendering {total_frames} frames ({total_duration}s at {FPS}fps) in {WIDTH}x{HEIGHT}...")
    step_log = total_frames // 10

    for f in range(total_frames):
        im = render_frame(f, total_frames)
        frame_file = os.path.join(FRAMES_DIR, f"frame_{f:05d}.jpg")
        im.save(frame_file, quality=88)

        if f % step_log == 0 or f == total_frames - 1:
            pct = int((f + 1) / total_frames * 100)
            print(f"[PROGRESS] Rendered {f+1}/{total_frames} frames ({pct}%)")

    print("[INFO] Encoding video with ffmpeg...")
    cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-r", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%05d.jpg"),
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        OUTPUT_PATH
    ]
    subprocess.run(cmd, check=True)

    # Downloadsにもコピー
    import shutil
    shutil.copy2(OUTPUT_PATH, DOWNLOADS_OUTPUT_PATH)
    print(f"[SUCCESS] Updated Shorts MV generated at: {OUTPUT_PATH} and {DOWNLOADS_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
