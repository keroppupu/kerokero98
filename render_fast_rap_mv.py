import os
import sys
import math
import random
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# 歌詞タイムライン（ミリ秒単位同期）
LYRICS_TIMELINE = [
    # 0.0s - 2.25s: 男性
    {"start": 0.0, "end": 1.15, "text": "取り替えるなら", "type": "male"},
    {"start": 1.15, "end": 2.25, "text": "電話はヨイフロ", "type": "male"},
    # 2.25s - 5.0s: 男性
    {"start": 2.25, "end": 3.4, "text": "おせちもいいけど", "type": "male"},
    {"start": 3.4, "end": 5.0, "text": "ハエハエカカカ", "type": "male"},
    # 5.0s - 9.0s: 間奏ビート
    {"start": 5.0, "end": 9.0, "text": "", "type": "beat"},
    # 9.0s - 13.5s: 女性
    {"start": 9.0, "end": 11.3, "text": "それは 君が見た光", "type": "female"},
    {"start": 11.3, "end": 13.5, "text": "そうでない方はそれなりに", "type": "female"},
    # 13.5s - 16.0s: 女性
    {"start": 13.5, "end": 14.8, "text": "ハエハエカカカ", "type": "female"},
    {"start": 14.8, "end": 16.0, "text": "ちゃっぷい、ちゃっぷい", "type": "female"},
    # 16.0s - 18.5s: 男性
    {"start": 16.0, "end": 17.3, "text": "風が語りかけます", "type": "male"},
    {"start": 17.3, "end": 18.5, "text": "教えてあげないよ", "type": "male"},
    # 18.5s - 22.55s: 女性＆シャウト
    {"start": 18.5, "end": 20.0, "text": "ちゃっぷい、ちゃっぷい", "type": "female"},
    {"start": 20.0, "end": 22.55, "text": "ダッダーン", "type": "shout"},
]

# 画像パス
IMG_MALE_PATH = "/Users/pupu/.gemini/antigravity/brain/61ad325a-1d7e-450b-a0e9-fd5c4dedc62e/.user_uploaded/media_1793751320216_e9ff03ea.jpg"
IMG_FEMALE_PATH = "/Users/pupu/.gemini/antigravity/brain/61ad325a-1d7e-450b-a0e9-fd5c4dedc62e/.user_uploaded/media_1793751331884_40f8d4e9.jpg"

FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def wrap_text_if_needed(text, max_len=8):
    if len(text) > max_len and " " in text:
        return text.split(" ")
    if len(text) > 8:
        mid = len(text) // 2
        return [text[:mid], text[mid:]]
    return [text]

def crop_and_zoom(img, target_w, target_h, center_ratio=(0.5, 0.5), zoom_factor=1.0):
    iw, ih = img.size
    cx = int(iw * center_ratio[0])
    cy = int(ih * center_ratio[1])

    crop_w = int((ih * (target_w / target_h)) / zoom_factor)
    crop_h = int(ih / zoom_factor)

    if crop_w > iw:
        crop_w = iw
        crop_h = int(iw * (target_h / target_w))

    x1 = max(0, min(iw - crop_w, cx - crop_w // 2))
    y1 = max(0, min(ih - crop_h, cy - crop_h // 2))
    x2 = x1 + crop_w
    y2 = y1 + crop_h

    cropped = img.crop((x1, y1, x2, y2))
    return cropped.resize((target_w, target_h), Image.Resampling.BILINEAR)

def main():
    audio_path = "/Users/pupu/fast_rap_complete_perfect.mp3"
    output_path = "/Users/pupu/fast_rap_jizura_shorts.mp4"

    width, height = 1080, 1920
    fps = 30
    total_duration = 22.55
    total_frames = int(total_duration * fps)

    img_male = Image.open(IMG_MALE_PATH).convert("RGB")
    img_female = Image.open(IMG_FEMALE_PATH).convert("RGB")

    palettes = {
        "male": {"fg": (255, 255, 255), "accent": (255, 45, 85), "glow": (255, 120, 0)},
        "female": {"fg": (255, 255, 255), "accent": (0, 240, 255), "glow": (200, 0, 255)},
        "shout": {"fg": (0, 0, 0), "accent": (255, 220, 0), "glow": (255, 255, 255)},
        "beat": {"fg": (255, 255, 255), "accent": (180, 180, 200), "glow": (100, 100, 120)},
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        frames_dir = os.path.join(temp_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        for f in range(total_frames):
            t = f / fps

            # セグメント特定
            current_seg = None
            seg_idx = 0
            for idx, seg in enumerate(LYRICS_TIMELINE):
                if seg["start"] <= t < seg["end"]:
                    current_seg = seg
                    seg_idx = idx
                    break
            if current_seg is None:
                current_seg = LYRICS_TIMELINE[-1]
                seg_idx = len(LYRICS_TIMELINE) - 1

            seg_type = current_seg["type"]
            text = current_seg["text"].strip()
            p = palettes.get(seg_type, palettes["male"])

            # セグメント内の進捗 (0.0 -> 1.0)
            seg_dur = max(0.1, current_seg["end"] - current_seg["start"])
            progress = (t - current_seg["start"]) / seg_dur

            # BPM 210 キックフラッシュ & ビートパルス
            beat_phase = (t % 0.2857) / 0.2857
            beat_pulse = max(0.0, 1.0 - beat_phase * 2.5) * 0.12

            # 背景画像・カメラワーク選択
            # 男声: img_male (男性の顔: (0.50, 0.25))
            # 女声: img_female (女性の顔: (0.43, 0.32))
            if seg_type in ["male"]:
                src_img = img_male
                # フレーズごとに顔アップとバストアップを交互に切り替え＆ズームイン
                if seg_idx % 2 == 0:
                    # 顔大アップ
                    zoom = 1.8 + progress * 0.3 + beat_pulse
                    center = (0.50, 0.24)
                else:
                    # バストアップ・歌唱姿
                    zoom = 1.35 + progress * 0.25 + beat_pulse
                    center = (0.49, 0.35)

            elif seg_type in ["female"]:
                src_img = img_female
                if seg_idx % 2 == 0:
                    # 顔大アップ
                    zoom = 1.9 + progress * 0.35 + beat_pulse
                    center = (0.43, 0.30)
                else:
                    # バストアップ・歌唱姿
                    zoom = 1.4 + progress * 0.25 + beat_pulse
                    center = (0.44, 0.38)

            elif seg_type == "beat":
                # 間奏: 2人の全体ショット（引き）から徐々に女性へパン
                src_img = img_female
                zoom = 1.15 + progress * 0.2 + beat_pulse
                cx = 0.55 - progress * 0.12
                cy = 0.40
                center = (cx, cy)

            else: # shout
                # 最後のダッダーン: 超急接近・猛烈ズーム
                src_img = img_male if (f % 4 < 2) else img_female
                zoom = 2.4 + progress * 0.6 + beat_pulse * 0.3
                center = (0.50, 0.24) if src_img == img_male else (0.43, 0.30)

            # 背景画像のクロップとリサイズ
            bg = crop_and_zoom(src_img, width, height, center_ratio=center, zoom_factor=zoom)

            # 歌詞の可読性を保つため、背景にスタイリッシュな暗幕・グラデーションビネットを付与
            enhancer = ImageEnhance.Brightness(bg)
            # ビートに合わせてほんのり明滅
            bg = enhancer.enhance(0.72 + beat_pulse * 0.8)

            # 上下のビネットグラデーション & 中央透過マスク
            draw = ImageDraw.Draw(bg)
            # 背景全体を少しダークトーンに落とす
            draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 50))

            # テキスト描画（歌詞以外の文字は一切描画しない）
            if text:
                max_w = width * 0.88
                lines = wrap_text_if_needed(text)

                font_size = 135 if len(lines) == 1 else 115
                if seg_type == "shout":
                    font_size = 160

                while font_size > 40:
                    font = get_font(font_size)
                    fits = True
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        if (bbox[2] - bbox[0]) > max_w:
                            fits = False
                            break
                    if fits:
                        break
                    font_size -= 4

                font = get_font(font_size)

                # シェイク演出
                shake_mag = int(14 * beat_pulse) if seg_type in ["male", "female", "shout"] else 0
                shake_x = random.randint(-shake_mag, shake_mag)
                shake_y = random.randint(-shake_mag, shake_mag)

                line_heights = []
                line_bboxes = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_bboxes.append(bbox)
                    line_heights.append(bbox[3] - bbox[1])

                line_spacing = int(font_size * 0.3)
                total_h = sum(line_heights) + line_spacing * (len(lines) - 1)
                start_y = (height - total_h) // 2 + shake_y

                # テキスト背面のボケ帯（可読性を極限まで高める）
                box_pad_x = 40
                box_pad_y = 30
                draw.rectangle(
                    [(box_pad_x, start_y - box_pad_y), (width - box_pad_x, start_y + total_h + box_pad_y)],
                    fill=(0, 0, 0, 160)
                )

                current_y = start_y
                for i, line in enumerate(lines):
                    bbox = line_bboxes[i]
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    cx = (width - tw) // 2 + shake_x

                    offset = max(5, int(font_size * 0.07))
                    # 重厚なアクセントカラーのフチ・シャドウ
                    for ox, oy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset),
                                  (-offset, -offset), (offset, offset), (-offset, offset), (offset, -offset)]:
                        draw.text((cx + ox, current_y + oy), line, fill=p["accent"], font=font)

                    # メインテキスト
                    draw.text((cx, current_y), line, fill=p["fg"], font=font)
                    current_y += th + line_spacing

            # スキャンラインエフェクト
            for y in range(0, height, 8):
                draw.line([(0, y), (width, y)], fill=(0, 0, 0, 35))

            frame_path = os.path.join(frames_dir, f"frame_{f:05d}.jpg")
            bg.save(frame_path, quality=88)

            if f % 150 == 0:
                print(f"Render progress: {f}/{total_frames} ({int(f/total_frames*100)}%)")

        print("[INFO] Encoding vertical MP4 with FFmpeg...")
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
            "-b:a", "320k",
            "-shortest",
            output_path
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"[SUCCESS] JIZURA MV with dynamic faces exported to: {output_path}")

if __name__ == "__main__":
    main()
