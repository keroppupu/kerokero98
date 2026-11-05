import os
import sys
import time
from pathlib import Path
import soundfile as sf
import numpy as np
import torch

STYLE_BERT_ROOT = Path("/Users/pupu/style-bert-vits2")
sys.path.insert(0, str(STYLE_BERT_ROOT))

from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from style_bert_vits2.tts_model import TTSModel

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {device}")

print("BERTモデルをロード中...")
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

models_dir = STYLE_BERT_ROOT / "model_assets"

def get_safetensor(folder_name):
    files = list((models_dir / folder_name).glob("*.safetensors"))
    if not files:
        raise FileNotFoundError(f"No safetensors found in {folder_name}")
    return files[0]

# ポッドキャスト向けペア:
# 女性: jvnv-F2-jp (標準女性モデル2)
# 男性: Sakura_Tokujiro (さくら徳次郎 - 爽やかで明るい若い男性パーソナリティ)
print("女性モデル (jvnv-F2-jp) ロード中...")
model_f = TTSModel(
    model_path=get_safetensor("jvnv-F2-jp"),
    config_path=models_dir / "jvnv-F2-jp" / "config.json",
    style_vec_path=models_dir / "jvnv-F2-jp" / "style_vectors.npy",
    device=device,
)

print("男性モデル (Sakura_Tokujiro) ロード中...")
model_m = TTSModel(
    model_path=get_safetensor("Sakura_Tokujiro"),
    config_path=models_dir / "Sakura_Tokujiro" / "config.json",
    style_vec_path=models_dir / "Sakura_Tokujiro" / "style_vectors.npy",
    device=device,
)

# 軽快・楽しげなポッドキャスト設定:
# スピード: 1.20〜1.26倍速 (会話がトントン拍子に進むリズム感)
# ピッチ: 1.02〜1.06 (声の響きを明るく前向きに)
# 抑揚: 1.25〜1.35 (生き生きとした感情表現)
# ノイズ: 0.25 (余計な息漏れ音・ざらつきを極小化)

script = [
    # --- 1. オープニング & 雑談 ---
    ("F", 1.24, 1.05, 1.30, "リスナーのみなさんこんにちは！週刊エーアイフロンティアへようこそ！パーソナリティのアオイです！"),
    ("M", 1.24, 1.04, 1.30, "こんにちは！パートナーのトクジローです！いやーアオイさん、最近朝晩ぐっと冷え込んできましたね！"),
    ("F", 1.23, 1.04, 1.28, "本当にそうですね！すっかり秋らしくなって、温かいカフェラテが手放せなくなりました！"),
    ("M", 1.25, 1.05, 1.32, "気温は下がってきましたけど、生成エーアイ業界の熱気だけは真夏以上の大フィーバーですよね！"),
    ("F", 1.26, 1.06, 1.35, "もう毎日寝て起きるたびに超弩級のニュースが飛び込んできて、ワクワクが止まりません！"),
    ("M", 1.25, 1.05, 1.30, "まさに進化の特異点ですよね！ということで今週も、大注目の最新トピックをテンポよく深掘りしていきましょう！"),

    # --- 2. トピック1：AnthropicのIPO申請と驚異の業績 ---
    ("F", 1.24, 1.05, 1.30, "はい！まず最初のビッグニュースは、クロードでおなじみのアンスロピックがナスダック上場に向けてエスワンを提出しました！"),
    ("M", 1.26, 1.06, 1.35, "これは驚きましたね！ティッカーシンボルはエー・エヌ・ティー、アントを予定しているそうです！"),
    ("F", 1.24, 1.05, 1.30, "提出書類で財務状況が初めて明かされたんですが、その成長スピードがまさに桁違いなんですよね！"),
    ("M", 1.25, 1.05, 1.30, "二千二十六年上半期の売上高が百六十三億ドル、日本円でおよそ二兆四千億円超え！前年同期比でなんと約十四倍の伸びですよ！"),
    ("F", 1.26, 1.06, 1.35, "一年で十四倍って凄すぎますよね！しかも売上の約八割がエーピーアイ経由というのも注目のポイントです！"),
    ("M", 1.24, 1.04, 1.28, "一般のチャットにとどまらず、世界中の大企業が基幹システムにクロードを組み込んでいる証拠ですね！"),
    ("F", 1.23, 1.03, 1.25, "一方で、書類にはリスク要因として興味深い情報も書かれていましたよね？"),
    ("M", 1.22, 1.02, 1.20, "ええ。テスト環境の設定ミスで外部システムへ一時アクセスしてしまった事例や、安全確認のために次世代モデルの学習を一時ストップした経緯も開示されていました。"),
    ("F", 1.24, 1.04, 1.28, "急成長の一方で、上場企業としての安全性やガバナンスへの高い責任が求められるフェーズに入ったということですね！"),

    # --- 3. トピック2：OpenAIのGPT-6.1 Terraとエージェント革命 ---
    ("M", 1.25, 1.05, 1.32, "そしてオープンエーアイも凄まじい一手を出してきました！実務特化型の新モデル、ジーピーティーシックス点一テラです！"),
    ("F", 1.26, 1.06, 1.35, "テラ！公開されたデモ動画、世界中でめちゃくちゃ話題になってますよね！"),
    ("M", 1.25, 1.05, 1.30, "パソコンの画面そのものを視覚で認識して、請求書を打ち込んだり複数アプリを行き来して実務を片付けてくれるんです！"),
    ("F", 1.24, 1.04, 1.30, "これまでのチャットはアドバイスをくれる相談役でしたけど、テラは実際に手を動かしてくれる本物の相棒ですよね！"),
    ("M", 1.25, 1.05, 1.30, "しかもエーピーアイ料金が前世代から大幅に値下げされたのも大きなサプライズでした！"),
    ("F", 1.24, 1.04, 1.28, "これなら個人開発者やスタートアップも一気にエージェントを組み込めますね！"),
    ("M", 1.24, 1.04, 1.28, "さらにオープンエーアイはモデルスペックも刷新して、指示の字面だけでなく人間の本当の意図を汲み取って動く方針に舵を切りました。"),
    ("F", 1.25, 1.05, 1.30, "より気が利いて、人間らしく寄り添ってくれるアシスタントへ進化しているわけですね！"),

    # --- 4. トピック3：Google Gemini 4 Carbon と業界標準ルール ---
    ("M", 1.24, 1.04, 1.28, "そしてグーグル陣営からも強力な最上位モデル、ジェミニフォーカーボンが公開されました！"),
    ("F", 1.26, 1.06, 1.35, "カーボンはサイバーセキュリティの防御や、超大規模な開発タスクに特化したモンスターモデルですね！"),
    ("M", 1.23, 1.03, 1.25, "あまりに強力すぎるため、悪用防止として当面は限定された防衛機関等に提供される厳重体制をとっています。"),
    ("F", 1.24, 1.04, 1.28, "能力が高くなればなるほど、安心・安全な運用との両立が最重要テーマになってきますね！"),
    ("M", 1.24, 1.04, 1.28, "一般向けにも、ジェミニアプリ内でスプレッドシートやドキュメントを直接編集できる機能がどんどん進化していますよ！"),
    ("F", 1.24, 1.04, 1.28, "普段のデスクワークがますます快適になりますね！"),
    ("M", 1.24, 1.04, 1.28, "それから業界全体として、主要四社がロボッツテキストでエーアイ学習を一括拒否できる共通仕様に合意したのも大きな前進でした！"),
    ("F", 1.24, 1.04, 1.28, "サイト運営者が一行設定するだけで対応できるルール作りですね！"),
    ("M", 1.25, 1.05, 1.30, "テクノロジーとウェブ社会が健全に共存していくための、素晴らしい一歩だと思います！"),

    # --- 5. 雑談・エンディング ---
    ("F", 1.25, 1.05, 1.30, "こうして振り返ると、単なるおしゃべりボットから、自律して仕事を実行するエージェントへと完全に主役が交代した一週間でしたね！"),
    ("M", 1.25, 1.05, 1.30, "本当にそうですね！アオイさん、自分の代わりにポッドキャストの編集を全部やってくれるエージェントがいたらどうしますか？"),
    ("F", 1.27, 1.06, 1.35, "今すぐ欲しいです！でも、こうしてトクジローさんと楽しくおしゃべりする時間だけは、絶対に自分たちの手で続けたいですね！"),
    ("M", 1.27, 1.06, 1.35, "ハハハ、大賛成です！人と人との生きたコミュニケーションこそ最高の価値ですからね！"),
    ("F", 1.25, 1.05, 1.30, "それでは今週のエーアイフロンティアはこのへんで！お相手はアオイと、"),
    ("M", 1.25, 1.05, 1.30, "トクジローでした！"),
    ("F", 1.26, 1.06, 1.35, "また次回お会いしましょう！さようなら！"),
]

output_segments = []
sample_rate = 44100
# テンポの良い掛け合いのために間を短縮（0.20秒 / 話題転換時は0.40秒）
pause_short = np.zeros(int(sample_rate * 0.20), dtype=np.int16)
pause_section = np.zeros(int(sample_rate * 0.40), dtype=np.int16)

print(f"\n合計 {len(script)} ターンの音声を生成します（軽快・明るいポッドキャストモデル）...")
start_time = time.time()

for idx, (speaker, speed, pitch, intonation, text) in enumerate(script, 1):
    model = model_f if speaker == "F" else model_m
    speaker_name = "アオイ(女:jvnv-F2)" if speaker == "F" else "トクジロー(男:Sakura)"
    
    print(f"[{idx:02d}/{len(script)}] {speaker_name} [spd={speed} pit={pitch} int={intonation}]: {text[:25]}...")

    sr, audio = model.infer(
        text=text,
        length=1.0 / speed,
        pitch_scale=pitch,
        intonation_scale=intonation,
        noise=0.25,      # 息漏れノイズを極小化
        noise_w=0.45,    # 発音ざらつき防止
        sdp_ratio=0.25,  # 発音の明瞭化
    )
    output_segments.append(audio.astype(np.int16))

    if idx in [6, 15, 23, 30]:
        output_segments.append(pause_section)
    else:
        output_segments.append(pause_short)

full_podcast = np.concatenate(output_segments)

out_path_raw_wav = "/Users/pupu/podcast_demo/ai_news_podcast_raw.wav"
sf.write(out_path_raw_wav, full_podcast, sample_rate, subtype="PCM_16")

out_path_wav = "/Users/pupu/podcast_demo/ai_news_podcast_5min.wav"
out_path_mp3 = "/Users/pupu/podcast_demo/ai_news_podcast_5min.mp3"

filter_cmd = "highpass=f=60,afftdn=nr=12:nf=-25"
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '{out_path_raw_wav}' -af '{filter_cmd}' '{out_path_wav}' > /dev/null 2>&1")
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '{out_path_wav}' -codec:a libmp3lame -b:a 192k '{out_path_mp3}' > /dev/null 2>&1")

# ショート版も同様にクリーン生成
short_segments = output_segments[:20]
full_short = np.concatenate(short_segments)
sf.write("/tmp/short_raw.wav", full_short, sample_rate, subtype="PCM_16")
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '/tmp/short_raw.wav' -af '{filter_cmd}' '/Users/pupu/podcast_demo/ai_news_podcast.wav' > /dev/null 2>&1")
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '/Users/pupu/podcast_demo/ai_news_podcast.wav' -codec:a libmp3lame -b:a 192k '/Users/pupu/podcast_demo/ai_news_podcast.mp3' > /dev/null 2>&1")

total_duration = len(full_podcast) / sample_rate
elapsed = time.time() - start_time
print(f"\n===== 生成完了 =====")
print(f"WAV: {out_path_wav}")
print(f"MP3: {out_path_mp3}")
print(f"総再生時間: {total_duration:.1f} 秒 ({total_duration/60:.2f} 分)")
print(f"所要時間: {elapsed:.1f} 秒")
