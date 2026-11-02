#!/usr/bin/env python3
"""
render_jizura_mv_v3.py
ユーザー指示に基づく全面修正版:
1. 【音の合成】映像生成後にffmpegで音声を完全合成し、プレイヤー依存の無音バグを解消
2. 【目線修正】目線（黒帯）を目の位置・角度に完全に合わせ、確実に目を覆うよう調整
3. 【歌詞以外の文字削除】
   - 英語サブタイトル削除
   - 「LIVE ● REC」「同接: 〇〇人」などの画面UI文字削除
   - 「NO SIGNAL」などのダミー演出文字削除
   - 純粋に歌唱歌詞（日本語テキスト）のみをJIZURA（キネティック・タイポグラフィ）として画面内に表示
4. 【歌詞見切れ防止】左右各160pxのセーフエリアで自動文字サイズ最適化
"""
import os
import sys
import math
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, max(14, int(size)))
    except Exception:
        return ImageFont.load_default()

# タイムライン定義: 純粋な歌詞のみ (start_t, end_t, lyrics_text, style_mode, bg_type)
TIMELINE = [
    # --- Intro ---
    (0.00, 2.66, "はいどーも！\n限界探索チャンネルです！", "intro", "photo1"),
    (2.66, 6.16, "今日はネットで噂の\n『地図から消えた廃村』来てます！", "warning", "video1"),
    (6.16, 7.68, "みんな！", "shout", "video1"),
    (7.68, 11.52, "高評価 & チャンネル登録\nよろしくね！", "intro", "photo1"),

    # --- Aメロ ---
    (11.52, 14.72, "画角ばっちり\nジンバル片手に", "fast", "video1"),
    (14.72, 18.16, "立ち入り禁止の\nサビついたフェンス越え", "warning", "color"),
    (18.16, 21.08, "「ここヤバくない？」\nカメラにウィンク", "intro", "photo1"),
    (21.08, 24.56, "同接じわじわ\n伸びるアドレナリン", "fast", "color"),
    (24.56, 27.84, "床の抜けそうな\n木造の廃旅館", "horror", "photo2"),
    (27.84, 31.28, "ホコリの匂いと\nカビた黒電話", "horror", "video2"),

    # --- Bメロ ---
    (31.28, 36.40, "コメント欄は\n「うしろ！うしろ！」のお約束", "glitch", "video2"),
    (36.40, 40.24, "はいはい いつものノリでしょ？\n分かってるって", "fast", "color"),
    (40.24, 42.80, "やらせはしない主義だけど", "intro", "photo2"),
    (42.80, 46.64, "ちょっとくらい盛るのが\nクリエイター魂", "fast", "color"),
    (46.64, 50.32, "「おっと、今なんか\n音がしたような…？」", "horror", "video2"),

    # --- サビ1 ---
    (50.32, 53.76, "ああ バズりたい！\nバズりたい！", "shout", "color"),
    (53.76, 57.12, "深夜の廃墟で\n神回をプリーズ！", "climax", "video1"),
    (57.20, 61.60, "懐中電灯の明かりが\n不自然にチカチカ", "glitch", "video2"),
    (61.60, 64.96, "（あれ 演出じゃないよ\nガチでヤバいやつ？）", "warning", "photo2"),

    # --- Aメロ2 ---
    (64.96, 67.28, "圏外ギリギリ", "glitch", "color"),
    (67.28, 71.44, "電波が途切れる\nスパチャの通知もバグってループ", "glitch", "video2"),
    (71.44, 74.88, "「気のせいだよね…」\n足音ペタ、ペタ", "horror", "color"),
    (74.88, 78.08, "俺しかいないはずの\n長い廊下", "horror", "video2"),
    (78.08, 81.28, "カメラを下ろして\nそっと振り返る", "horror", "photo2"),
    (81.28, 86.24, "肉眼じゃ見えないのに\n画面（モニター）には映る『何か』", "glitch", "color"),

    # --- Bメロ2 ---
    (86.32, 91.92, "激流だったコメント欄が\n一斉にピタッと止まる", "horror", "video2"),
    (91.92, 95.84, "数秒後、画面いっぱいの\n『逃げて』『逃げて』『逃げて』", "warning", "color"),
    (95.84, 99.36, "やらせじゃない\nマジで無理！！", "shout", "video1"),
    (99.36, 101.60, "三脚なんて捨てて\nとにかく走り出したい", "fast", "video1"),
    (101.60, 106.40, "なのに足が床に\n張り付いたみたいに動かない", "horror", "photo2"),

    # --- サビ2 ---
    (106.40, 110.48, "ああ 帰りたい！\n帰りたい！", "shout", "color"),
    (110.64, 112.96, "心霊スポットで\nガチ泣き土下座配信", "climax", "photo1"),
    (112.96, 116.16, "息が切れる\n心臓が破裂しそう", "fast", "video1"),
    (116.16, 118.88, "（追いかけてくるよ\nガチでヤバいやつ！）", "glitch", "video2"),
    (118.88, 125.44, "登録者数より\n自分の命が大事！！", "shout", "color"),
    (125.44, 131.60, "でも待って、\n出口のドアが開かないんだけど！！", "warning", "photo2"),

    # --- Outro (余韻・インスト) ---
    (131.60, 146.00, "", "horror", "video2")
]

PHOTO1_PATH = "/Users/pupu/Downloads/vtuber_song/preview/photo1_perfect_censor.jpg"
PHOTO2_PATH = "/Users/pupu/Downloads/vtuber_song/preview/photo2_perfect_censor.jpg"
V1_DIR = "/Users/pupu/Downloads/vtuber_song/v1_frames"
V2_DIR = "/Users/pupu/Downloads/vtuber_song/v2_frames"

photo1_img = Image.open(PHOTO1_PATH).convert("RGB")
photo2_img = Image.open(PHOTO2_PATH).convert("RGB")

def get_video_frame(v_dir, t, max_frames=300):
    idx = int((t * 30) % max_frames) + 1
    f_path = os.path.join(v_dir, f"f_{idx:04d}.jpg")
    try:
        return Image.open(f_path).convert("RGB")
    except Exception:
        return Image.new("RGB", (1920, 1080), (10, 10, 15))

def render_frame(t, width, height, fps):
    # 現在のセグメント
    seg = TIMELINE[-1]
    for s in TIMELINE:
        if s[0] <= t < s[1]:
            seg = s
            break

    start_t, end_t, text, style, bg_type = seg
    progress = (t - start_t) / max(0.01, end_t - start_t)

    # カラーテーマ
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

    # 背景生成
    if bg_type == "photo1":
        im = photo1_img.copy()
        dark = Image.new("RGB", (width, height), (0, 0, 0))
        im = Image.blend(im, dark, 0.40)
    elif bg_type == "photo2":
        im = photo2_img.copy()
        dark = Image.new("RGB", (width, height), (0, 0, 0))
        im = Image.blend(im, dark, 0.40)
    elif bg_type == "video1":
        im = get_video_frame(V1_DIR, t)
        dark = Image.new("RGB", (width, height), (0, 0, 0))
        im = Image.blend(im, dark, 0.45)
    elif bg_type == "video2":
        im = get_video_frame(V2_DIR, t)
        dark = Image.new("RGB", (width, height), (0, 0, 0))
        im = Image.blend(im, dark, 0.45)
    else:
        im = Image.new("RGB", (width, height), bg_color)

    draw = ImageDraw.Draw(im)

    # シェイク（揺れ）
    shake_mag = 0
    if style in ["shout", "climax"]:
        shake_mag = int(12 * (1.0 - min(1.0, progress * 2.0)))
    elif style == "glitch":
        shake_mag = 6 if (int(t * fps) % 3 == 0) else 0
    elif style == "warning":
        shake_mag = 3

    sx = random.randint(-shake_mag, shake_mag) if shake_mag else 0
    sy = random.randint(-shake_mag, shake_mag) if shake_mag else 0

    # 警告ストライプ（歌詞以外の英語やUIは全撤廃し、グラフィック帯のみ適用）
    if style == "warning":
        stripe_h = 36
        for x in range(-stripe_h, width + stripe_h, stripe_h * 2):
            draw.polygon([(x, 0), (x + stripe_h, 0), (x, stripe_h), (x - stripe_h, stripe_h)], fill=(20, 20, 20))
            draw.polygon([(x, height - stripe_h), (x + stripe_h, height - stripe_h), (x, height), (x - stripe_h, height)], fill=(20, 20, 20))

    # 歌詞テキストの描画（歌詞がない区間は背景のみ）
    if not text.strip():
        return im

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    font_family = FONT_MINCHO if style in ["horror"] else FONT_HEAVY

    # セーフエリア: 左右余白160px、上下余白140px（見切れ完全防止）
    max_w = width - 320
    max_h = height - 280

    target_fs = int(width * 0.080)
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
            # 強い黒ストロークで視認性を確保
            stroke_r = max(4, int(target_fs * 0.09))
            for ox in range(-stroke_r, stroke_r + 1):
                for oy in range(-stroke_r, stroke_r + 1):
                    if ox * ox + oy * oy <= stroke_r * stroke_r:
                        draw.text((lx + ox, ly + oy), line, fill=(0, 0, 0), font=main_font)

        if style == "glitch":
            draw.text((lx - 7, ly), line, fill=(255, 0, 80), font=main_font)
            draw.text((lx + 7, ly), line, fill=(0, 255, 230), font=main_font)
        else:
            offset = 6 if style in ["shout", "climax"] else 4
            draw.text((lx + offset, ly + offset), line, fill=ac_color, font=main_font)

        draw.text((lx, ly), line, fill=fg_color, font=main_font)

    return im

def main():
    audio_path = "/Users/pupu/Downloads/限界探索チャンネル_廃村配信.mp3"
    temp_video = "/Users/pupu/Downloads/vtuber_song/temp_video_only.mp4"
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
    print(f"[INFO] Step 1: Rendering video stream to {temp_video}...")

    # Step 1: 映像パイプをレンダリング
    ffmpeg_video_cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",               # stdin pipe
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
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

    # Step 2: 音声を完全合成（AAC 320kbps + 確実なストリームマッピング）
    print(f"[INFO] Step 2: Merging audio {audio_path} into final video {output_mp4}...")
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
    print(f"\n[SUCCESS] Final MV with audio generated at: {output_mp4}")

if __name__ == "__main__":
    main()
