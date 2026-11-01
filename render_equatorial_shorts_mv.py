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

def wrap_and_fit_text(draw, lines, max_w, max_h, start_size=110, min_size=42):
    """
    複数行または単一行のテキストが max_w x max_h に収まる最大フォントサイズと各行のバウンディングボックスを計算
    """
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
    (0.00, 2.70, ["ガガゼト", "ムイムイ", "パラポラ ピー"]),
    (2.70, 5.40, ["チェケダ", "ドロロト", "シュビドゥバ ドン"]),
    (5.40, 9.90, ["キリマノ", "ルルッタ"]),
    (9.90, 12.40, ["ポロピロ マカラパ", "ポロピロ パン"]),
    (12.40, 15.00, ["ズンガラ ベッチャラ", "ポロピロ ペン"]),
    (15.00, 19.90, ["[ 間 奏 ]", "RITUAL BEATS"]),
    (19.90, 23.50, ["シャラマポ ギギギデ", "アチャラパ ポン"]),
    (23.50, 27.10, ["ルパラパ チキチキ", "チャンガラ ガッ"]),
    (27.10, 31.00, ["ミソベレ ペケペケ", "ピャラピャラ ポッ"]),
    (31.00, 35.00, ["ビビリボ ババラボ", "シュラララ チャ"]),
    (35.00, 37.84, ["ペケペケ ピャラピャラ", "シュラララ ソッ"]),
    (37.84, 40.00, ["ポロピロ パン！！"])
]

palette = [
    # bg, fg, accent, border
    ((15, 12, 10), (255, 250, 240), (255, 69, 0), (255, 215, 0)),     # 呪術赤橙
    ((20, 10, 25), (255, 240, 255), (220, 20, 60), (0, 255, 200)),     # 妖艶パープル
    ((10, 22, 18), (240, 255, 245), (0, 230, 150), (255, 165, 0)),     # 熱帯密林グリーン
    ((28, 8, 8), (255, 255, 255), (255, 40, 40), (255, 255, 0)),       # 警戒ブラッドレッド
    ((12, 18, 30), (240, 250, 255), (0, 180, 255), (255, 99, 71)),     # 深海・夜影ブルー
    ((30, 20, 5), (255, 255, 240), (255, 180, 0), (255, 50, 50)),      # 太陽・トーテムゴールド
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
    
    seg_idx = len(timeline) - 1
    current_lines = timeline[-1][2]
    seg_start, seg_end = timeline[-1][0], timeline[-1][1]
    
    for idx, (st, en, lines) in enumerate(timeline):
        if st <= t < en:
            seg_idx = idx
            current_lines = lines
            seg_start, seg_end = st, en
            break
            
    seg_duration = max(0.1, seg_end - seg_start)
    progress_in_seg = (t - seg_start) / seg_duration
    
    bg_col, fg_col, ac_col, bd_col = palette[seg_idx % len(palette)]
    im = Image.new("RGB", (width, height), bg_col)
    draw = ImageDraw.Draw(im)
    
    # 幾何学・トライバル風背景装飾
    center_x, center_y = width // 2, height // 2
    
    # トライバルサークル（回転・脈動）
    ring_radius = int(340 + 40 * math.sin(t * 8.0))
    for r_offset in [-20, 0, 20]:
        draw.ellipse([center_x - ring_radius + r_offset, center_y - ring_radius + r_offset,
                      center_x + ring_radius - r_offset, center_y + ring_radius - r_offset],
                     outline=(*ac_col[:3], ), width=2)
                     
    # コーナーフレーム（YouTubeショートのUIに被らないセーフエリアガイド）
    # 上部200px、下部300px、左右70pxをマージンとして確保
    safe_left = 80
    safe_right = width - 80
    safe_top = 220
    safe_bottom = height - 320
    safe_w = safe_right - safe_left
    safe_h = safe_bottom - safe_top
    
    # 枠線
    draw.line([(safe_left, safe_top), (safe_left + 60, safe_top)], fill=bd_col, width=4)
    draw.line([(safe_left, safe_top), (safe_left, safe_top + 60)], fill=bd_col, width=4)
    draw.line([(safe_right, safe_top), (safe_right - 60, safe_top)], fill=bd_col, width=4)
    draw.line([(safe_right, safe_top), (safe_right, safe_top + 60)], fill=bd_col, width=4)
    draw.line([(safe_left, safe_bottom), (safe_left + 60, safe_bottom)], fill=bd_col, width=4)
    draw.line([(safe_left, safe_bottom), (safe_left, safe_bottom - 60)], fill=bd_col, width=4)
    draw.line([(safe_right, safe_bottom), (safe_right - 60, safe_bottom)], fill=bd_col, width=4)
    draw.line([(safe_right, safe_bottom), (safe_right, safe_bottom - 60)], fill=bd_col, width=4)
    
    # 上下部ステータス / トライバルテキスト
    tag_font = get_font(FONT_BOLD, 28)
    draw.text((safe_left + 10, safe_top - 45), "EQUATORIAL TRIBAL FOLKLORE // JIZURA", fill=(180, 180, 180), font=tag_font)
    time_str = f"{int(t//60):02d}:{int(t%60):02d}:{int((t*100)%100):02d}"
    draw.text((safe_right - 180, safe_top - 45), time_str, fill=ac_col, font=tag_font)
    
    # 激しいカメラシェイク（キネティック・タイポグラフィのSLAM演出）
    shake_x = 0
    shake_y = 0
    if progress_in_seg < 0.22:
        # 切り替わり時の強烈なスラムシェイク
        shake_intensity = int(24 * (1.0 - progress_in_seg / 0.22))
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
    elif f % 2 == 0:
        shake_x = random.randint(-3, 3)
        shake_y = random.randint(-3, 3)
        
    # テキストの自動折返しとフォントサイズフィッティング（絶対に見切れない安全領域内）
    font, font_size, line_boxes, line_spacing, total_h = wrap_and_fit_text(
        draw, current_lines, max_w=safe_w - 40, max_h=safe_h - 60, start_size=125, min_size=48
    )
    
    # 縦方向中央揃え
    curr_y = (height - total_h) // 2 + shake_y
    
    for l_idx, line in enumerate(current_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        curr_x = (width - tw) // 2 + shake_x
        
        # JIZURA風の多重レイヤードシャドウ（影・輪郭・グロー）
        # 外側アクセントシャドウ
        shadow_offset = max(6, int(font_size * 0.08))
        draw.text((curr_x + shadow_offset, curr_y + shadow_offset), line, fill=ac_col, font=font)
        draw.text((curr_x - shadow_offset, curr_y - shadow_offset), line, fill=(*ac_col[:3], ), font=font)
        
        # 縁取り黒ストローク
        stroke_w = max(3, int(font_size * 0.05))
        draw.text((curr_x, curr_y), line, fill=fg_col, font=font, stroke_width=stroke_w, stroke_fill=(0, 0, 0))
        
        curr_y += th + line_spacing
        
    # CRT走査線エフェクト
    for y in range(0, height, 6):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 45))
        
    frame_path = os.path.join(frames_dir, f"frame_{f:05d}.jpg")
    im.save(frame_path, quality=88)
    
    if f % 150 == 0:
        print(f"Render progress: {f}/{total_frames} ({int(f/total_frames*100)}%)")

print("[INFO] Rendering done! Running FFmpeg to assemble MP4...")
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
print(f"[SUCCESS] YouTube Shorts MV ready at: {output_path}")
