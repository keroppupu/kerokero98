import os
import sys
import math
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def wrap_and_fit_text(draw, lines, max_w, max_h, start_size=120, min_size=44):
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

# 歌詞以外のテキスト（間奏タグや英語ヘッダー等）は一切表示しない
# 実測の精密タイムライン:
# 20.0s: シャラマポ ギギギデ
# 21.8s: アチャラパ ポン
# 23.0s: ルパラパ チキチキ
# 24.2s: チャンガラ ガッ
# 25.4s: ミソベレ ペケペケ
# 26.5s: ピャラピャラ ポッ
# 27.6s: ビビリボ ババラボ
# 28.8s: シュラララ チャ
# 30.0s〜: 余韻・伴奏
timeline = [
    (0.00, 2.70, ["ガガゼト ムイムイ", "パラポラ ピー"]),
    (2.70, 5.40, ["チェケダ ドロロト", "シュビドゥバ ドン"]),
    (5.40, 9.90, ["キリマノ", "ルルッタ"]),
    (9.90, 12.40, ["ポロピロ マカラパ", "ポロピロ パン"]),
    (12.40, 15.00, ["ズンガラ ベッチャラ", "ポロピロ ペン"]),
    (15.00, 20.00, []), # 間奏時は歌詞なし（無文字）
    (20.00, 21.80, ["シャラマポ", "ギギギデ"]),
    (21.80, 23.00, ["アチャラパ", "ポン"]),
    (23.00, 24.20, ["ルパラパ", "チキチキ"]),
    (24.20, 25.40, ["チャンガラ", "ガッ"]),
    (25.40, 26.50, ["ミソベレ", "ペケペケ"]),
    (26.50, 27.60, ["ピャラピャラ", "ポッ"]),
    (27.60, 28.80, ["ビビリボ", "ババラボ"]),
    (28.80, 31.00, ["シュラララ", "チャ"]),
    (31.00, 40.00, []) # 伴奏・ラストフェード時は無文字
]

palette = [
    ((15, 12, 10), (255, 250, 240), (255, 69, 0)),     # 呪術赤橙
    ((20, 10, 25), (255, 240, 255), (220, 20, 60)),     # 妖艶パープル
    ((10, 22, 18), (240, 255, 245), (0, 230, 150)),     # 熱帯密林グリーン
    ((28, 8, 8), (255, 255, 255), (255, 40, 40)),       # 警戒ブラッドレッド
    ((12, 18, 30), (240, 250, 255), (0, 180, 255)),     # 夜影ブルー
    ((30, 20, 5), (255, 255, 240), (255, 180, 0)),      # トーテムゴールド
]

width, height = 1080, 1920
fps = 30
total_frames = int(40.0 * fps)
audio_path = "/Users/pupu/projects/Vtuber/audio.mp3"
output_path = "/Users/pupu/Downloads/jizura_shorts_mv.mp4"

temp_dir = tempfile.mkdtemp()
frames_dir = os.path.join(temp_dir, "frames")
os.makedirs(frames_dir, exist_ok=True)

print(f"[INFO] Rendering {total_frames} frames to {frames_dir}...")

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
    
    bg_col, fg_col, ac_col = palette[seg_idx % len(palette)]
    im = Image.new("RGB", (width, height), bg_col)
    draw = ImageDraw.Draw(im)
    
    center_x, center_y = width // 2, height // 2
    
    # 幾何学リング（トライバルな背景装飾）
    ring_radius = int(320 + 35 * math.sin(t * 8.0))
    for r_offset in [-15, 0, 15]:
        draw.ellipse([center_x - ring_radius + r_offset, center_y - ring_radius + r_offset,
                      center_x + ring_radius - r_offset, center_y + ring_radius - r_offset],
                     outline=(*ac_col[:3], ), width=2)
                     
    # YouTubeショートのUIセーフエリア（上下左右のマージン確保で見切れを完全防止）
    safe_left = 90
    safe_right = width - 90
    safe_top = 260
    safe_bottom = height - 350
    safe_w = safe_right - safe_left
    safe_h = safe_bottom - safe_top
    
    # 歌詞が存在する場合のみタイポグラフィを描画（純粋な歌詞のみ）
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
            
            # 多重アクセントシャドウ
            shadow_offset = max(6, int(font_size * 0.08))
            draw.text((curr_x + shadow_offset, curr_y + shadow_offset), line, fill=ac_col, font=font)
            draw.text((curr_x - shadow_offset, curr_y - shadow_offset), line, fill=ac_col, font=font)
            
            # 縁取り黒ストローク＋本体文字
            stroke_w = max(3, int(font_size * 0.05))
            draw.text((curr_x, curr_y), line, fill=fg_col, font=font, stroke_width=stroke_w, stroke_fill=(0, 0, 0))
            curr_y += th + line_spacing
            
    # CRT走査線エフェクト
    for y in range(0, height, 6):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 45))
        
    frame_path = os.path.join(frames_dir, f"frame_{f:05d}.jpg")
    im.save(frame_path, quality=88)
    
    if f % 200 == 0:
        print(f"Render progress: {f}/{total_frames} ({int(f/total_frames*100)}%)")

print("[INFO] Rendering done! Encoding with FFmpeg...")
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
print(f"[SUCCESS] Updated MV saved to: {output_path}")
