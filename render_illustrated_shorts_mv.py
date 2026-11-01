#!/usr/bin/env python3
"""
render_illustrated_shorts_mv.py - YouTube Shorts 9:16 Illustrated MV with Scene Switching & Cross-Fading
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
FRAMES_DIR = "/tmp/mv_illustrated_frames"

FONT_TSUKUSHI = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/60484a5d6f3fa8d51dcbeff43b7e70c9d42bcd2f.asset/AssetData/TsukushiBMaruGothic.ttc"
FONT_FALLBACK = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"

def get_font(size):
    font_path = FONT_TSUKUSHI if os.path.exists(FONT_TSUKUSHI) else FONT_FALLBACK
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

# タイムライン設計 (秒単位)
TIMELINE = [
    # Verse 1: 行きはスッキリ入ったのに...
    {
        "start": 0.0, "end": 2.2, "img": 1, "trans": "fade", "fade_dur": 0.4, "zoom": 1.02,
        "tag": "🎒 キャンプ準備完了！",
        "top": "＼ スッポリ入って余裕の笑顔 ／",
        "bottom": "行きは入った荷物が",
        "theme": "pink"
    },
    {
        "start": 2.2, "end": 4.5, "img": 2, "trans": "cut", "zoom": 1.10,
        "tag": "💦 撤収時の悲劇",
        "top": "えっ…チャックが閉まらん！？",
        "bottom": "帰りは入らんだに！",
        "theme": "red"
    },
    {
        "start": 4.5, "end": 6.8, "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.03,
        "tag": "🤔 思い出してみて？",
        "top": "来る時は余裕で入ったじゃん！",
        "bottom": "行きは入った荷物が",
        "theme": "cyan"
    },
    {
        "start": 6.8, "end": 9.2, "img": 2, "trans": "cut", "zoom": 1.12,
        "tag": "😱 現実逃避したい",
        "top": "どう見ても膨らんどる…！",
        "bottom": "帰りは入らんだに！",
        "theme": "orange"
    },
    # Verse 2: 高速押し込みバトル！
    {
        "start": 9.2, "end": 10.3, "img": 1, "trans": "cut", "zoom": 1.12,
        "tag": "⭕ 押し込め！",
        "top": "よし、イケるぞ！",
        "bottom": "入った！",
        "theme": "mint"
    },
    {
        "start": 10.3, "end": 11.5, "img": 2, "trans": "cut", "zoom": 1.15,
        "tag": "❌ 弾き出された！",
        "top": "跳ね返ってきた！！",
        "bottom": "入らん！",
        "theme": "red"
    },
    {
        "start": 11.5, "end": 12.7, "img": 1, "trans": "cut", "zoom": 1.12,
        "tag": "⭕ もう一回！",
        "top": "ねじ込めーーッ！",
        "bottom": "入った！",
        "theme": "yellow"
    },
    {
        "start": 12.7, "end": 13.9, "img": 2, "trans": "cut", "zoom": 1.18,
        "tag": "❌ 限界突破！",
        "top": "絶対無理だに！！",
        "bottom": "入らん！",
        "theme": "purple"
    },
    {
        "start": 13.9, "end": 16.3, "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.02,
        "tag": "❓ キャンプ七不思議",
        "top": "何も買ってないよ！？",
        "bottom": "同じカバン！同じギア！",
        "theme": "blue"
    },
    {
        "start": 16.3, "end": 18.8, "img": 2, "trans": "fade", "fade_dur": 0.25, "zoom": 1.08,
        "tag": "🌀 なんで膨張するの？",
        "top": "シュラフ畳んだだけなのに！",
        "bottom": "増えとらんに！増えとらんに！",
        "theme": "coral"
    },
    # Chorus (サビ：電波全開シャウト！)
    {
        "start": 18.8, "end": 21.0, "img": 2, "trans": "flash", "zoom": 1.22,
        "tag": "🔥 サビ：電波全開絶叫！ 🔥",
        "top": "なんでだや！？",
        "bottom": "パンパンだに！",
        "theme": "chorus_electric"
    },
    {
        "start": 21.0, "end": 23.3, "img": 2, "trans": "cut", "zoom": 1.18,
        "tag": "⚡ はち切れ寸前 ⚡",
        "top": "縫い目が悲鳴を上げとる！",
        "bottom": "チャックがパンパンだら！",
        "theme": "chorus_yellow"
    },
    {
        "start": 23.3, "end": 25.4, "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.05,
        "tag": "✨ 奇跡の過去回想",
        "top": "あの美しいパッキング…",
        "bottom": "行きはスッポリ！",
        "theme": "mint"
    },
    {
        "start": 25.4, "end": 27.6, "img": 2, "trans": "cut", "zoom": 1.16,
        "tag": "💥 残酷な現実",
        "top": "パンパンすぎて閉まらん！",
        "bottom": "帰りはパンパンだに！",
        "theme": "pink"
    },
    {
        "start": 27.6, "end": 30.0, "img": 2, "trans": "cut", "zoom": 1.14,
        "tag": "😤 踏みつけ作戦発動",
        "top": "体重かけても…！",
        "bottom": "入らん！入らん！",
        "theme": "orange"
    },
    {
        "start": 30.0, "end": 32.2, "img": 2, "trans": "cut", "zoom": 1.24,
        "tag": "💢 怒りの遠州弁シャウト 💢",
        "top": "頭抱えて絶叫！！",
        "bottom": "ばか入らん！",
        "theme": "dark_red"
    },
    # Climax Finale
    {
        "start": 32.2, "end": 34.6, "img": 1, "trans": "fade", "fade_dur": 0.25, "zoom": 1.03,
        "tag": "🏕️ 諦めずに詰め直す！",
        "top": "最初からやり直しだ！",
        "bottom": "行きは入った荷物が",
        "theme": "cyan"
    },
    {
        "start": 34.6, "end": 36.9, "img": 2, "trans": "cut", "zoom": 1.12,
        "tag": "😭 やっぱりダメでした",
        "top": "どう頑張っても…",
        "bottom": "帰りは入らんだに！",
        "theme": "magenta"
    },
    {
        "start": 36.9, "end": 39.2, "img": 1, "trans": "fade", "fade_dur": 0.2, "zoom": 1.05,
        "tag": "✨ 夢なら醒めて！",
        "top": "綺麗に収まるはずなのに！",
        "bottom": "行きは入った荷物が",
        "theme": "yellow"
    },
    {
        "start": 39.2, "end": 41.5, "img": 2, "trans": "cut", "zoom": 1.20,
        "tag": "🎉 魂のラストシャウト 🎉",
        "top": "手で持って帰るしかない！！",
        "bottom": "帰りは入らんだに！！",
        "theme": "rainbow"
    },
    # Outro
    {
        "start": 41.5, "end": 45.0, "img": 2, "trans": "fade", "fade_dur": 0.4, "zoom": 1.06,
        "tag": "🏕️ キャンプあるある完 🏕️",
        "top": "〜 チャック半開きで帰宅 〜",
        "bottom": "パンパンだに！！",
        "theme": "pink"
    }
]

THEMES = {
    "pink": {
        "text": (255, 40, 110), "stroke": (255, 255, 255), "shadow": (180, 15, 70),
        "tag_bg": (255, 45, 115), "tag_text": (255, 255, 255), "top_bg": (255, 235, 245), "top_text": (220, 20, 90)
    },
    "red": {
        "text": (230, 20, 40), "stroke": (255, 255, 255), "shadow": (140, 5, 20),
        "tag_bg": (225, 25, 45), "tag_text": (255, 255, 255), "top_bg": (255, 230, 230), "top_text": (200, 10, 30)
    },
    "cyan": {
        "text": (0, 150, 225), "stroke": (255, 255, 255), "shadow": (0, 80, 150),
        "tag_bg": (0, 170, 245), "tag_text": (255, 255, 255), "top_bg": (225, 248, 255), "top_text": (0, 120, 200)
    },
    "orange": {
        "text": (245, 80, 20), "stroke": (255, 255, 255), "shadow": (160, 40, 10),
        "tag_bg": (250, 90, 25), "tag_text": (255, 255, 255), "top_bg": (255, 240, 225), "top_text": (210, 60, 15)
    },
    "yellow": {
        "text": (245, 110, 10), "stroke": (255, 255, 255), "shadow": (160, 60, 5),
        "tag_bg": (255, 180, 20), "tag_text": (40, 20, 0), "top_bg": (255, 250, 215), "top_text": (200, 80, 5)
    },
    "mint": {
        "text": (10, 170, 130), "stroke": (255, 255, 255), "shadow": (5, 100, 75),
        "tag_bg": (20, 190, 145), "tag_text": (255, 255, 255), "top_bg": (225, 255, 245), "top_text": (10, 140, 105)
    },
    "purple": {
        "text": (130, 40, 220), "stroke": (255, 255, 255), "shadow": (80, 15, 150),
        "tag_bg": (145, 50, 240), "tag_text": (255, 255, 255), "top_bg": (245, 230, 255), "top_text": (110, 30, 190)
    },
    "blue": {
        "text": (30, 90, 230), "stroke": (255, 255, 255), "shadow": (15, 50, 150),
        "tag_bg": (40, 110, 245), "tag_text": (255, 255, 255), "top_bg": (230, 240, 255), "top_text": (20, 70, 200)
    },
    "coral": {
        "text": (235, 60, 85), "stroke": (255, 255, 255), "shadow": (160, 25, 45),
        "tag_bg": (245, 75, 100), "tag_text": (255, 255, 255), "top_bg": (255, 235, 235), "top_text": (210, 45, 65)
    },
    "magenta": {
        "text": (210, 25, 150), "stroke": (255, 255, 255), "shadow": (130, 10, 90),
        "tag_bg": (225, 35, 165), "tag_text": (255, 255, 255), "top_bg": (255, 230, 250), "top_text": (180, 15, 125)
    },
    "dark_red": {
        "text": (255, 235, 50), "stroke": (210, 10, 30), "shadow": (30, 0, 10),
        "tag_bg": (210, 10, 30), "tag_text": (255, 255, 255), "top_bg": (255, 220, 60), "top_text": (180, 10, 20)
    },
    "chorus_electric": {
        "text": (255, 235, 40), "stroke": (255, 20, 100), "shadow": (60, 10, 40),
        "tag_bg": (255, 20, 100), "tag_text": (255, 255, 255), "top_bg": (255, 245, 170), "top_text": (220, 10, 80)
    },
    "chorus_yellow": {
        "text": (255, 30, 110), "stroke": (255, 255, 255), "shadow": (160, 10, 65),
        "tag_bg": (255, 210, 30), "tag_text": (40, 20, 0), "top_bg": (255, 255, 200), "top_text": (220, 20, 90)
    },
    "rainbow": {
        "text": (255, 235, 50), "stroke": (230, 30, 120), "shadow": (40, 10, 80),
        "tag_bg": (0, 200, 255), "tag_text": (255, 255, 255), "top_bg": (255, 230, 245), "top_text": (210, 20, 100)
    }
}

# 画像の事前読み込み＆ブラー背景作成
RAW_IMG1 = Image.open(IMG1_PATH).convert("RGB")
RAW_IMG2 = Image.open(IMG2_PATH).convert("RGB")

def make_blurred_bg(img):
    # 1080x1920 に拡大してクロップ
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
    blurred = cropped.filter(ImageFilter.GaussianBlur(28))
    dim = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    return Image.blend(blurred, dim, 0.28)

BG1 = make_blurred_bg(RAW_IMG1)
BG2 = make_blurred_bg(RAW_IMG2)

def draw_sticker_text(draw, cx, cy, text, font, fill_col, stroke_col, shadow_col, stroke_w=15, shadow_off=14):
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

def fit_font_size(text, max_w, initial_size, min_size=42):
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

    # 現在のセグメント特定
    cur_idx = len(TIMELINE) - 1
    for idx, seg in enumerate(TIMELINE):
        if seg["start"] <= t < seg["end"]:
            cur_idx = idx
            break

    cur_seg = TIMELINE[cur_idx]
    prev_seg = TIMELINE[cur_idx - 1] if cur_idx > 0 else cur_seg

    seg_elapsed = t - cur_seg["start"]
    seg_dur = cur_seg["end"] - cur_seg["start"]

    # トランジション（フェード・カット）計算
    alpha = 1.0
    is_fading = False
    if cur_seg["trans"] == "fade" and cur_idx > 0:
        fade_dur = cur_seg.get("fade_dur", 0.3)
        if seg_elapsed < fade_dur:
            alpha = seg_elapsed / fade_dur
            is_fading = True
    elif cur_seg["trans"] == "flash":
        if seg_elapsed < 0.15:
            flash_alpha = 1.0 - (seg_elapsed / 0.15)
        else:
            flash_alpha = 0.0

    # 1. 背景の合成
    cur_raw = RAW_IMG1 if cur_seg["img"] == 1 else RAW_IMG2
    prev_raw = RAW_IMG1 if prev_seg["img"] == 1 else RAW_IMG2

    cur_bg = BG1 if cur_seg["img"] == 1 else BG2
    prev_bg = BG1 if prev_seg["img"] == 1 else BG2

    if is_fading:
        bg = Image.blend(prev_bg, cur_bg, alpha)
    else:
        bg = cur_bg.copy()

    # 2. 前景イラスト（角丸ウインドウ＆ズーム）の作成
    # ズーム率
    zoom = cur_seg.get("zoom", 1.0)
    # BPM200 パルス (微細なリズムの鼓動)
    beat_phase = (t % BEAT_SEC) / BEAT_SEC
    pulse = math.sin(beat_phase * math.pi) * 0.02
    total_zoom = zoom + pulse

    # シェイク（サビや叫び部分）
    shake_x = 0
    shake_y = 0
    if "！" in cur_seg["bottom"] or "？" in cur_seg["bottom"]:
        if "chorus" in cur_seg["theme"] or "dark" in cur_seg["theme"] or "rainbow" in cur_seg["theme"]:
            shake_x = random.randint(-8, 8) if (f % 2 == 0) else 0
            shake_y = random.randint(-8, 8) if (f % 2 == 0) else 0

    frame_w, frame_h = 1000, int(1000 * 572 / 1024)  # 1000 x 558
    frame_x = (WIDTH - frame_w) // 2 + shake_x
    frame_y = 480 + shake_y

    def get_zoomed_cropped_image(raw_img, z):
        rw, rh = raw_img.size
        cw, ch = int(rw / z), int(rh / z)
        # キャラクターの顔（やや上部・中央）を中心にクロップ
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
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, frame_w, frame_h], radius=32, fill=255)

    # ドロップシャドウ
    shadow_mask = Image.new("RGBA", (frame_w + 30, frame_h + 30), (0, 0, 0, 0))
    ImageDraw.Draw(shadow_mask).rounded_rectangle([15, 15, frame_w + 15, frame_h + 15], radius=32, fill=(0, 0, 0, 120))
    shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(12))
    bg.paste(shadow_blur, (frame_x - 15, frame_y - 15), shadow_blur)

    # 前景貼り付け
    bg.paste(fg_composite, (frame_x, frame_y), mask)

    # 白い太枠フレーム
    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle([frame_x, frame_y, frame_x + frame_w, frame_y + frame_h], radius=32, outline=(255, 255, 255), width=8)

    theme = THEMES.get(cur_seg["theme"], THEMES["pink"])

    # 3. 上部コンテンツ（Y: 160 〜 440）
    # ヘッダー情報（曲名 ＆ テンポ）
    hdr_font = get_font(30)
    draw.text((70, 170), "⚡ BPM 200 ULTRA FAST RAP", font=hdr_font, fill=(255, 255, 255))
    draw.text((WIDTH - 280, 170), "🏕️ パッキングあるある", font=hdr_font, fill=(255, 255, 255))

    # タグバッジ
    tag_font = get_font(36)
    tag_text = cur_seg["tag"]
    tbb = draw.textbbox((0, 0), tag_text, font=tag_font)
    tw, th = tbb[2] - tbb[0] + 44, tbb[3] - tbb[1] + 20
    tx, ty = (WIDTH - tw) // 2, 230
    draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=22, fill=theme["tag_bg"])
    draw.text((tx + 22, ty + 10), tag_text, font=tag_font, fill=theme["tag_text"])

    # 上部サブテロップ（ツッコミ / 状況解説）
    top_text = cur_seg["top"]
    if top_text:
        top_font, top_sz = fit_font_size(top_text, WIDTH - 160, 52)
        pbb = draw.textbbox((0, 0), top_text, font=top_font)
        pw, ph = pbb[2] - pbb[0] + 40, pbb[3] - pbb[1] + 20
        px, py = (WIDTH - pw) // 2, 330
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=20, fill=theme["top_bg"])
        draw.text((px + 20, py + 10), top_text, font=top_font, fill=theme["top_text"])

    # 4. 下部メイン歌詞テロップ（Y: 1100 〜 1640）
    # バウンス演出（登場時）
    entrance_scale = 1.0
    if seg_elapsed < 0.18:
        entrance_scale = 1.0 + (0.18 - seg_elapsed) * 0.8
    scale = entrance_scale + pulse

    main_text = cur_seg["bottom"]
    usable_w = WIDTH - 160  # 920px usable

    # サビ・叫びなら特大フォント
    base_sz = 108 if len(main_text) <= 6 else (96 if len(main_text) <= 10 else 82)
    font, actual_sz = fit_font_size(main_text, usable_w, int(base_sz * scale))

    # 下部中央Y座標
    lyric_center_y = 1320 + shake_y

    # 可愛いステッカー文字描画
    draw_sticker_text(
        draw, WIDTH // 2 + shake_x, lyric_center_y, main_text, font,
        theme["text"], theme["stroke"], theme["shadow"],
        stroke_w=16, shadow_off=16
    )

    # 5. フッター装飾 ＆ プログレスバー（Y: 1680 〜 1820）
    bar_y = 1710
    bar_w = WIDTH - 160
    draw.rounded_rectangle([80, bar_y, 80 + bar_w, bar_y + 14], radius=7, fill=(255, 255, 255, 120))
    prog_w = int(bar_w * (t / 45.0))
    draw.rounded_rectangle([80, bar_y, 80 + prog_w, bar_y + 14], radius=7, fill=theme["tag_bg"])

    ft_font = get_font(32)
    draw.text((WIDTH // 2 - 140, 1750), "✨ 高評価＆チャンネル登録 ✨", font=ft_font, fill=(255, 255, 255))

    # サビの白フラッシュ演出
    if cur_seg.get("trans") == "flash" and flash_alpha > 0:
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
    print(f"[SUCCESS] Illustrated Shorts MV generated at: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
