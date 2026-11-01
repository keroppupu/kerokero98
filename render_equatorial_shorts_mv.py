import os
import sys
import math
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def wrap_and_fit_text(draw, lines, max_w, max_h, start_size=125, min_size=46):
    font_size = start_size
    while font_size >= min_size:
        font = get_font(FONT_HEAVY, font_size)
        total_h = 0
        line_boxes = []
        fits = True
        line_spacing = int(font_size * 0.28)
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w > max_w:
                fits = False
                break
            line_boxes.append((w, h))
            total_h += h
        total_h += line_spacing * (len(lines) - 1)
        
        if fits and total_h <= max_h:
            return font, font_size, line_boxes, line_spacing, total_h
        font_size -= 4

    font = get_font(FONT_HEAVY, min_size)
    line_spacing = int(min_size * 0.28)
    line_boxes = [draw.textbbox((0, 0), l, font=font)[2:4] for l in lines]
    total_h = sum(b[1] for b in line_boxes) + line_spacing * (len(lines) - 1)
    return font, min_size, line_boxes, line_spacing, total_h

timeline = [
    (0.00, 2.70, ["ガガゼト ムイムイ", "パラポラ ピー"]),
    (2.70, 5.40, ["チェケダ ドロロト", "シュビドゥバ ドン"]),
    (5.40, 9.90, ["キリマノ", "ルルッタ"]),
    (9.90, 12.40, ["ポロピロ マカラパ", "ポロピロ パン"]),
    (12.40, 15.00, ["ズンガラ ベッチャラ", "ポロピロ ペン"]),
    (15.00, 20.00, []), # 間奏（文字なし）
    (20.00, 21.80, ["シャラマポ", "ギギギデ"]),
    (21.80, 23.00, ["アチャラパ", "ポン"]),
    (23.00, 24.20, ["ルパラパ", "チキチキ"]),
    (24.20, 25.40, ["チャンガラ", "ガッ"]),
    (25.40, 26.50, ["ミソベレ", "ペケペケ"]),
    (26.50, 27.60, ["ピャラピャラ", "ポッ"]),
    (27.60, 28.80, ["ビビリボ", "ババラボ"]),
    (28.80, 31.00, ["シュラララ", "チャ"]),
    (31.00, 40.00, []) # 伴奏・余韻（文字なし）
]

accent_colors = [
    (255, 69, 0),     # 赤橙
    (255, 20, 147),   # ネオンピンク
    (0, 245, 160),    # エメラルドグリーン
    (255, 215, 0),    # ゴールドイエロー
    (0, 210, 255),    # シアンブルー
    (255, 80, 0),     # オレンジ
]

width, height = 1080, 1920
fps = 30
total_frames = int(40.0 * fps)
audio_path = "/Users/pupu/projects/Vtuber/audio.mp3"
bg_img_path = "/Users/pupu/projects/Vtuber/ritual_bg.jpg"
output_path = "/Users/pupu/Downloads/jizura_shorts_mv.mp4"

# 背景画像を読み込み
orig_bg = Image.open(bg_img_path).convert("RGB")
bw, bh = orig_bg.size

temp_dir = tempfile.mkdtemp()
frames_dir = os.path.join(temp_dir, "frames")
os.makedirs(frames_dir, exist_ok=True)

print(f"[INFO] Rendering {total_frames} frames with moving image background...")

for f in range(total_frames):
    t = f / fps
    
    seg_idx = 0
    current_lines = []
    seg_start, seg_end = 0.0, 40.0
    
    for idx, (st, en, lines) in enumerate(timeline):
        if st <= t < en:
            seg_idx = idx
            current_lines = lines
            seg_start, seg_end = st, en
            break
            
    seg_duration = max(0.1, seg_end - seg_start)
    progress_in_seg = (t - seg_start) / seg_duration
    
    # --- カメラワーク / ズーム・パン演出 ---
    # 音楽のビート（低音ドラム）とセクションに合わせてズーム＆パン
    # ベースのゆっくりとした緩急ズーム
    base_zoom = 1.25 + 0.15 * math.sin(t * 0.4)
    # ビートに合わせた律動（パルス）
    beat_pulse = 0.04 * math.sin(t * 12.0)
    # フレーズ切り替わり（アタック）時の瞬間的なズームイン
    attack_zoom = 0.08 * max(0.0, 1.0 - progress_in_seg / 0.25)
    
    current_zoom = base_zoom + beat_pulse + attack_zoom
    
    # ズームに応じたクロップ領域の計算（中央のミラーボール・DJ・ダンサー群を中心にパン）
    crop_w = int(bw / current_zoom)
    crop_h = int(bh / current_zoom)
    
    # わずかに左右上下にゆっくり視線移動（浮遊感）
    pan_x = int((bw - crop_w) * 0.5 + (bw * 0.06) * math.sin(t * 0.55))
    pan_y = int((bh - crop_h) * 0.45 + (bh * 0.04) * math.cos(t * 0.45))
    
    pan_x = max(0, min(bw - crop_w, pan_x))
    pan_y = max(0, min(bh - crop_h, pan_y))
    
    cropped_bg = orig_bg.crop((pan_x, pan_y, pan_x + crop_w, pan_y + crop_h))
    
    # 縦型 9:16 (1080x1920) に合わせてリサイズ＆カバー配置
    # aspect ratio fit cover
    target_ratio = width / height
    cw, ch = cropped_bg.size
    crop_aspect = cw / ch
    if crop_aspect > target_ratio:
        new_cw = int(ch * target_ratio)
        offset = (cw - new_cw) // 2
        cropped_bg = cropped_bg.crop((offset, 0, offset + new_cw, ch))
    else:
        new_ch = int(cw / target_ratio)
        offset = (ch - new_ch) // 2
        cropped_bg = cropped_bg.crop((0, offset, cw, offset + new_ch))
        
    bg_frame = cropped_bg.resize((width, height), Image.Resampling.BILINEAR)
    
    # 文字の視認性を高めるため、コントラストを強調しつつ全体をわずかにダークトーン化
    enhancer = ImageEnhance.Brightness(bg_frame)
    bg_frame = enhancer.enhance(0.55 + 0.10 * math.sin(t * 1.5))
    
    draw = ImageDraw.Draw(bg_frame)
    ac_col = accent_colors[seg_idx % len(accent_colors)]
    
    # --- JIZURAの円・トライバルリング効果（そのまま継承） ---
    center_x, center_y = width // 2, height // 2
    ring_radius = int(330 + 40 * math.sin(t * 8.0))
    for r_offset in [-16, 0, 16]:
        draw.ellipse([center_x - ring_radius + r_offset, center_y - ring_radius + r_offset,
                      center_x + ring_radius - r_offset, center_y + ring_radius - r_offset],
                     outline=(*ac_col, ), width=2)
                     
    # セーフエリア
    safe_left = 90
    safe_right = width - 90
    safe_top = 260
    safe_bottom = height - 350
    safe_w = safe_right - safe_left
    safe_h = safe_bottom - safe_top
    
    # --- 歌詞テキスト描画（歌詞のみ） ---
    if current_lines:
        shake_x = 0
        shake_y = 0
        if progress_in_seg < 0.20:
            shake_intensity = int(22 * (1.0 - progress_in_seg / 0.20))
            shake_x = random.randint(-shake_intensity, shake_intensity)
            shake_y = random.randint(-shake_intensity, shake_intensity)
        elif f % 2 == 0:
            shake_x = random.randint(-2, 2)
            shake_y = random.randint(-2, 2)
            
        font, font_size, line_boxes, line_spacing, total_h = wrap_and_fit_text(
            draw, current_lines, max_w=safe_w - 40, max_h=safe_h - 60, start_size=135, min_size=52
        )
        
        curr_y = (height - total_h) // 2 + shake_y
        for line in current_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            curr_x = (width - tw) // 2 + shake_x
            
            # 多重アクセントグロー・シャドウ
            shadow_offset = max(6, int(font_size * 0.08))
            draw.text((curr_x + shadow_offset, curr_y + shadow_offset), line, fill=ac_col, font=font)
            draw.text((curr_x - shadow_offset, curr_y - shadow_offset), line, fill=ac_col, font=font)
            
            # 漆黒のアウトライン（写真背景でも歌詞がくっきり浮き上がる太縁）
            stroke_w = max(5, int(font_size * 0.08))
            draw.text((curr_x, curr_y), line, fill=(255, 255, 255), font=font, stroke_width=stroke_w, stroke_fill=(0, 0, 0))
            curr_y += th + line_spacing
            
    # CRT風走査線エフェクト
    for y in range(0, height, 6):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 45))
        
    frame_path = os.path.join(frames_dir, f"frame_{f:05d}.jpg")
    bg_frame.save(frame_path, quality=88)
    
    if f % 200 == 0:
        print(f"Render progress: {f}/{total_frames} ({int(f/total_frames*100)}%)")

print("[INFO] Rendering completed! Assembling MP4 with FFmpeg...")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-r", str(fps),
    "-i", os.path.join(frames_dir, "frame_%05d.jpg"),
    "-i", audio_path,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    output_path
]
subprocess.run(ffmpeg_cmd, check=True)
print(f"[SUCCESS] MV with background image created: {output_path}")
