#!/usr/bin/env python3
"""
render_jizura_mv_v6.py
- 最新のWhisper単語アライメント解析に基づくミリ秒単位の完全同期TIMELINE
- 迫真の喉が裂ける絶叫悲鳴＋機材倒壊音＋TV砂嵐ノイズに対応
- GitHub 100MB制限をクリアするCRF 23最適化エンコード
- 写真素材の目線処理・動的演出（ズーム/パン/チルト）
"""
import os
import sys
import math
import random
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, max(14, int(size)))
    except Exception:
        return ImageFont.load_default()

# タイムライン定義 (start_t, end_t, lyrics_text, style_mode, bg_type, zoom_mode)
# bg_type: 'photo1', 'photo2', 'photo3', 'video1', 'video2', 'video3', 'color', 'noise'
TIMELINE = [
    # --- Intro (0.00s - 11.48s) ---
    (0.00, 2.66, "はいどーも！\n限界探索チャンネルです！", "intro", "photo1", "zoom_in"),
    (2.66, 6.40, "今日はネットで噂の\n『地図から消えた廃村』来てます！", "warning", "video1", "normal"),
    (6.40, 7.58, "みんな！", "shout", "video1", "zoom_in"),
    (7.58, 11.48, "高評価 & チャンネル登録\nよろしくね！", "intro", "photo1", "face_focus"),

    # --- Aメロ (11.48s - 31.26s) ---
    (11.48, 14.96, "画角ばっちり\nジンバル片手に", "fast", "video1", "pan_left"),
    (14.96, 18.16, "立ち入り禁止の\nサビついたフェンス越え", "warning", "photo3", "zoom_in"),
    (18.16, 21.12, "「ここヤバくない？」\nカメラにウィンク", "intro", "photo1", "zoom_out"),
    (21.12, 24.78, "同接じわじわ\n伸びるアドレナリン", "fast", "color", "normal"),
    (24.78, 27.92, "床の抜けそうな\n木造の廃旅館", "horror", "photo2", "wide"),
    (27.92, 31.26, "ホコリの匂いと\nカビた黒電話", "horror", "video2", "pan_right"),

    # --- Bメロ (31.26s - 49.96s) ---
    (31.26, 36.40, "コメント欄は\n「うしろ！うしろ！」のお約束", "glitch", "video3", "zoom_in"),
    (36.40, 40.30, "はいはい いつものノリでしょ？\n分かってるって", "fast", "color", "normal"),
    (40.30, 42.84, "やらせはしない主義だけど", "intro", "photo2", "face_focus"),
    (42.84, 46.70, "ちょっとくらい盛るのが\nクリエイター魂", "fast", "color", "normal"),
    (46.70, 49.96, "「おっと、今なんか\n音がしたような…？」", "horror", "video3", "wide"),

    # --- サビ1 (49.96s - 66.00s) ---
    (49.96, 53.84, "ああ バズりたい！\nバズりたい！", "shout", "color", "normal"),
    (53.84, 57.46, "深夜の廃墟で\n神回をプリーズ！", "climax", "video1", "zoom_in"),
    (57.46, 61.50, "懐中電灯の明かりが\n不自然にチカチカ", "glitch", "video3", "pan_left"),
    (61.50, 66.00, "（あれ 演出じゃないよ\nガチでヤバいやつ？）", "warning", "photo3", "zoom_in"),

    # --- Aメロ2 (66.00s - 85.78s) ---
    (66.00, 68.72, "圏外ギリギリ\n電波が途切れる", "glitch", "color", "normal"),
    (68.72, 71.26, "スパチャの通知も\nバグってループ", "glitch", "video2", "pan_left"),
    (71.26, 74.90, "「気のせいだよね…」\n足音ペタ、ペタ", "horror", "photo3", "wide"),
    (74.90, 78.02, "俺しかいないはずの\n長い廊下", "horror", "video2", "pan_right"),
    (78.02, 81.28, "カメラを下ろして\nそっと振り返る", "horror", "photo2", "face_focus"),
    (81.28, 85.78, "肉眼じゃ見えないのに\nモニターには映る", "horror", "photo3", "zoom_in"),

    # --- Bメロ2 (85.78s - 112.52s) ---
    (85.78, 91.92, "『何か』激流だった\nコメント欄が", "glitch", "video3", "zoom_in"),
    (91.92, 94.34, "一斉にピタッと止まる", "horror", "color", "normal"),
    (94.34, 96.88, "数秒後、画面いっぱいの", "horror", "video3", "wide"),
    (96.88, 99.36, "『逃げて』『逃げて』『逃げて』", "warning", "color", "normal"),
    (99.36, 101.54, "やらせじゃない\nマジで無理！！", "shout", "photo2", "face_focus"),
    (101.54, 103.66, "三脚なんて捨てて", "fast", "video1", "pan_left"),
    (103.66, 106.44, "とにかく走り出したい！", "shout", "video1", "zoom_in"),
    (106.44, 108.54, "なのに足が床に", "horror", "photo3", "wide"),
    (108.54, 112.52, "張り付いたみたいに\n動かない", "horror", "photo3", "zoom_in"),

    # --- サビ2 (112.52s - 136.26s) ---
    (112.52, 115.34, "ああ 帰りたい！\n帰りたい！", "shout", "color", "normal"),
    (115.34, 120.36, "心霊スポットで\nガチ泣き土下座配信", "climax", "photo1", "face_focus"),
    (120.36, 124.82, "息が切れる\n心臓が破裂しそう！", "fast", "video1", "pan_right"),
    (124.82, 129.88, "登録者数より\n自分の命が大事！！", "shout", "color", "normal"),
    (129.88, 131.36, "", "horror", "color", "normal"),
    (131.36, 136.26, "でも待って、\n出口のドアが開かないんだけど！！", "warning", "photo2", "zoom_in"),

    # --- 終焉: 迫真の絶叫悲鳴＋機材倒壊＋TV砂嵐ノイズ (136.26s - 151.02s) ---
    (136.26, 146.00, "「いやあああああああっ！！」", "shout", "video3", "glitch_heavy"),
    (146.00, 149.50, "", "horror", "noise", "normal"),
    (149.50, 151.02, "", "horror", "black", "normal")
]

PHOTO1_PATH = "/Users/pupu/Downloads/vtuber_song/preview/photo1_perfect_censor.jpg"
PHOTO2_PATH = "/Users/pupu/Downloads/vtuber_song/preview/photo2_perfect_censor.jpg"
PHOTO3_PATH = "/Users/pupu/Downloads/vtuber_song/preview/photo3_1080p.jpg"
V1_DIR = "/Users/pupu/Downloads/vtuber_song/v1_frames"
V2_DIR = "/Users/pupu/Downloads/vtuber_song/v2_frames"
V3_DIR = "/Users/pupu/Downloads/vtuber_song/v3_frames"

photo1_img = Image.open(PHOTO1_PATH).convert("RGB")
photo2_img = Image.open(PHOTO2_PATH).convert("RGB")
photo3_img = Image.open(PHOTO3_PATH).convert("RGB")

def apply_transform(img, progress, zoom_mode, width=1920, height=1080):
    if zoom_mode == "normal":
        return img

    w, h = img.size
    if zoom_mode == "zoom_in":
        scale = 1.0 + 0.28 * progress
        crop_w, crop_h = int(w / scale), int(h / scale)
        cx, cy = w // 2, h // 2
        return img.crop((cx - crop_w // 2, cy - crop_h // 2, cx + crop_w // 2, cy + crop_h // 2)).resize((width, height), Image.Resampling.BILINEAR)

    elif zoom_mode == "zoom_out":
        scale = 1.28 - 0.28 * progress
        crop_w, crop_h = int(w / scale), int(h / scale)
        cx, cy = w // 2, h // 2
        return img.crop((cx - crop_w // 2, cy - crop_h // 2, cx + crop_w // 2, cy + crop_h // 2)).resize((width, height), Image.Resampling.BILINEAR)

    elif zoom_mode == "face_focus":
        scale = 1.45 + 0.1 * math.sin(progress * math.pi)
        crop_w, crop_h = int(w / scale), int(h / scale)
        cx, cy = int(w * 0.58), int(h * 0.35)
        x1 = max(0, min(w - crop_w, cx - crop_w // 2))
        y1 = max(0, min(h - crop_h, cy - crop_h // 2))
        return img.crop((x1, y1, x1 + crop_w, y1 + crop_h)).resize((width, height), Image.Resampling.BILINEAR)

    elif zoom_mode == "wide":
        crop_w, crop_h = int(w * 0.9), int(h * 0.9)
        y1 = int((h - crop_h) * (0.8 - 0.6 * progress))
        x1 = (w - crop_w) // 2
        return img.crop((x1, y1, x1 + crop_w, y1 + crop_h)).resize((width, height), Image.Resampling.BILINEAR)

    elif zoom_mode == "pan_left":
        scale = 1.15
        crop_w, crop_h = int(w / scale), int(h / scale)
        x1 = int((w - crop_w) * (0.8 - 0.6 * progress))
        y1 = (h - crop_h) // 2
        return img.crop((x1, y1, x1 + crop_w, y1 + crop_h)).resize((width, height), Image.Resampling.BILINEAR)

    elif zoom_mode == "pan_right":
        scale = 1.15
        crop_w, crop_h = int(w / scale), int(h / scale)
        x1 = int((w - crop_w) * (0.2 + 0.6 * progress))
        y1 = (h - crop_h) // 2
        return img.crop((x1, y1, x1 + crop_w, y1 + crop_h)).resize((width, height), Image.Resampling.BILINEAR)

    return img

def get_video_frame(v_dir, t, max_frames=300):
    idx = int((t * 30) % max_frames) + 1
    f_path = os.path.join(v_dir, f"f_{idx:04d}.jpg")
    try:
        return Image.open(f_path).convert("RGB")
    except Exception:
        return Image.new("RGB", (1920, 1080), (10, 10, 15))

def generate_tv_static(width, height):
    """テレビ砂嵐ノイズフレームを生成"""
    noise = np.random.randint(0, 256, (height // 2, width // 2), dtype=np.uint8)
    noise_img = Image.fromarray(noise, mode="L").resize((width, height), Image.Resampling.NEAREST).convert("RGB")
    draw = ImageDraw.Draw(noise_img)
    for _ in range(8):
        y = random.randint(0, height - 1)
        h = random.randint(2, 12)
        draw.rectangle([0, y, width, y + h], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    return noise_img

def render_frame(t, width, height, fps):
    seg = TIMELINE[-1]
    for s in TIMELINE:
        if s[0] <= t < s[1]:
            seg = s
            break

    start_t, end_t, text, style, bg_type, zoom_mode = seg
    progress = (t - start_t) / max(0.01, end_t - start_t)

    if bg_type == "noise":
        return generate_tv_static(width, height)
    elif bg_type == "black":
        return Image.new("RGB", (width, height), (0, 0, 0))

    theme_colors = {
        "intro": ((18, 18, 28), (255, 255, 255), (255, 70, 120)),
        "shout": ((220, 20, 40), (255, 255, 255), (10, 10, 10)),
        "glitch": ((10, 10, 15), (0, 255, 230), (255, 0, 80)),
        "fast": ((245, 245, 250), (15, 15, 20), (255, 40, 0)),
        "warning": ((255, 180, 0), (10, 10, 10), (255, 255, 255)),
        "horror": ((8, 10, 18), (230, 240, 250), (140, 20, 30)),
        "climax": ((180, 10, 30), (255, 255, 255), (0, 0, 0)),
    }
    bg_color, fg_color, ac_color = theme_colors.get(style, ((15, 15, 20), (255, 255, 255), (255, 50, 50)))

    # 背景素材取得
    if bg_type == "photo1":
        raw_bg = apply_transform(photo1_img, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.40)
    elif bg_type == "photo2":
        raw_bg = apply_transform(photo2_img, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.40)
    elif bg_type == "photo3":
        raw_bg = apply_transform(photo3_img, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.40)
    elif bg_type == "video1":
        v_frame = get_video_frame(V1_DIR, t)
        raw_bg = apply_transform(v_frame, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.45)
    elif bg_type == "video2":
        v_frame = get_video_frame(V2_DIR, t)
        raw_bg = apply_transform(v_frame, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.45)
    elif bg_type == "video3":
        v_frame = get_video_frame(V3_DIR, t)
        raw_bg = apply_transform(v_frame, progress, zoom_mode, width, height)
        im = Image.blend(raw_bg, Image.new("RGB", (width, height), (0, 0, 0)), 0.45)
    else:
        im = Image.new("RGB", (width, height), bg_color)

    # 激しいグリッチ揺れ（悲鳴時）
    if zoom_mode == "glitch_heavy":
        im_arr = np.array(im)
        shift = random.randint(-40, 40)
        im_arr = np.roll(im_arr, shift, axis=1)
        im = Image.fromarray(im_arr)

    draw = ImageDraw.Draw(im)

    shake_mag = 0
    if style in ["shout", "climax"]:
        shake_mag = int(14 * (1.0 - min(1.0, progress * 1.8)))
    elif style == "glitch":
        shake_mag = 8 if (int(t * fps) % 3 == 0) else 0
    elif style == "warning":
        shake_mag = 4

    sx = random.randint(-shake_mag, shake_mag) if shake_mag else 0
    sy = random.randint(-shake_mag, shake_mag) if shake_mag else 0

    if style == "warning":
        stripe_h = 36
        for x in range(-stripe_h, width + stripe_h, stripe_h * 2):
            draw.polygon([(x, 0), (x + stripe_h, 0), (x, stripe_h), (x - stripe_h, stripe_h)], fill=(20, 20, 20))
            draw.polygon([(x, height - stripe_h), (x + stripe_h, height - stripe_h), (x, height), (x - stripe_h, height)], fill=(20, 20, 20))

    if not text.strip():
        return im

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    font_family = FONT_MINCHO if style in ["horror"] else FONT_HEAVY

    max_w = width - 320
    max_h = height - 280

    target_fs = int(width * 0.082)
    if style in ["shout", "climax"]:
        target_fs = int(target_fs * 1.15)

    while target_fs > 24:
        main_font = get_font(font_family, target_fs)
        line_height = int(target_fs * 1.18)
        total_h = len(lines) * line_height

        max_lw = 0
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=main_font)
            lw = bbox[2] - bbox[0]
            if lw > max_lw:
                max_lw = lw

        if max_lw <= max_w and total_h <= max_h:
            break
        target_fs -= 2

    main_font = get_font(font_family, target_fs)
    line_height = int(target_fs * 1.18)
    total_text_h = len(lines) * line_height
    start_y = (height - total_text_h) // 2

    has_media_bg = (bg_type != "color")

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=main_font)
        lw = bbox[2] - bbox[0]
        lx = (width - lw) // 2 + sx
        ly = start_y + i * line_height + sy

        if has_media_bg:
            stroke_r = max(4, int(target_fs * 0.09))
            for ox in range(-stroke_r, stroke_r + 1):
                for oy in range(-stroke_r, stroke_r + 1):
                    if ox * ox + oy * oy <= stroke_r * stroke_r:
                        draw.text((lx + ox, ly + oy), line, fill=(0, 0, 0), font=main_font)

        if style == "glitch":
            draw.text((lx - 8, ly), line, fill=(255, 0, 80), font=main_font)
            draw.text((lx + 8, ly), line, fill=(0, 255, 230), font=main_font)
        else:
            offset = 6 if style in ["shout", "climax"] else 4
            draw.text((lx + offset, ly + offset), line, fill=ac_color, font=main_font)

        draw.text((lx, ly), line, fill=fg_color, font=main_font)

    return im

def main():
    audio_path = "/Users/pupu/Downloads/限界探索チャンネル_廃村配信.mp3"
    temp_video = "/Users/pupu/Downloads/vtuber_song/temp_video_only_v6.mp4"
    output_mp4 = "/Users/pupu/Downloads/限界探索チャンネル_廃村配信_JIZURA_MV.mp4"

    width, height = 1920, 1080
    fps = 30

    probe = subprocess.run(
        ["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        stdout=subprocess.PIPE, text=True, check=True
    )
    duration = float(probe.stdout.strip())
    total_frames = int(duration * fps)

    print(f"[INFO] Audio duration: {duration:.2f}s, Total Frames: {total_frames}")
    print(f"[INFO] Step 1: Rendering video stream with exact lyrics sync and scream/static outro...")

    ffmpeg_video_cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        temp_video
    ]

    proc = subprocess.Popen(ffmpeg_video_cmd, stdin=subprocess.PIPE)

    step = max(1, total_frames // 20)
    for f in range(total_frames):
        t = f / fps
        im = render_frame(t, width, height, fps)
        proc.stdin.write(im.tobytes())

        if f % step == 0 or f == total_frames - 1:
            pct = int((f + 1) / total_frames * 100)
            sys.stdout.write(f"\rRendering Video: {f+1}/{total_frames} frames ({pct}%)")
            sys.stdout.flush()

    proc.stdin.close()
    proc.wait()
    print("\n[INFO] Step 1 complete.")

    print(f"[INFO] Step 2: Merging audio {audio_path} into {output_mp4}...")
    ffmpeg_merge_cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        output_mp4
    ]
    subprocess.check_call(ffmpeg_merge_cmd)
    file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"\n[SUCCESS] Final MV generated: {output_mp4} ({file_size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
