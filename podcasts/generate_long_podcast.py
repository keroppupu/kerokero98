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

# 女性モデル: jvnv-F1-jp（低め・落ち着いた大人トーンにピッチ調整）
print("女性モデル (jvnv-F1) ロード中...")
model_f = TTSModel(
    model_path=get_safetensor("jvnv-F1-jp"),
    config_path=models_dir / "jvnv-F1-jp" / "config.json",
    style_vec_path=models_dir / "jvnv-F1-jp" / "style_vectors.npy",
    device=device,
)

# 男性モデル: jvnv-M1-jp
print("男性モデル (jvnv-M1) ロード中...")
model_m = TTSModel(
    model_path=get_safetensor("jvnv-M1-jp"),
    config_path=models_dir / "jvnv-M1-jp" / "config.json",
    style_vec_path=models_dir / "jvnv-M1-jp" / "style_vectors.npy",
    device=device,
)

# 女性の声質パラメータ: 低め・落ち着いた大人のトーン
FEMALE_PITCH = 0.88         # ピッチを低めに設定（高音アニメ声を防止）
FEMALE_INTONATION = 0.85    # 抑揚の跳ね上がりを抑えて落ち着いたアナウンサー調に

script = [
    # --- 1. オープニング & 雑談 ---
    ("F", "Neutral", 0.0, 1.0, "リスナーのみなさん、こんにちは。週刊エーアイフロンティアへようこそ。パーソナリティのアスカです。"),
    ("M", "Neutral", 0.0, 1.0, "こんにちは。パートナーのケンタです。アスカさん、最近は朝晩ぐっと冷え込んできましたね。"),
    ("F", "Neutral", 0.0, 1.0, "そうですね。すっかり秋らしくなって、温かい飲み物が恋しい季節になりました。"),
    ("M", "Neutral", 0.0, 1.0, "気温は下がってきましたけど、生成エーアイ業界の動きは相変わらず激しいですね。"),
    ("F", "Neutral", 0.0, 1.0, "本当にそうですね。毎日のように新しい発表が続いていて、情報を追うだけでもなかなか大変です。"),
    ("M", "Neutral", 0.0, 1.0, "今週もかなり大きな動きがありましたからね。じっくり振り返っていきましょう。"),

    # --- 2. トピック1：AnthropicのIPO申請と業績 ---
    ("F", "Neutral", 0.0, 1.0, "はい。まず最初のトピックですが、クロードを開発するアンスロピックがナスダック上場に向けてエスワンを提出しました。"),
    ("M", "Surprise", 0.5, 1.0, "これは驚きましたね。ティッカーシンボルはエー・エヌ・ティー、アントを予定しているそうです。"),
    ("F", "Neutral", 0.0, 1.0, "書類の中で財務状況が初めて公表されたんですが、数字の伸びが非常に注目されています。"),
    ("M", "Neutral", 0.0, 1.0, "二千二十六年上半期の売上高が百六十三億ドル、日本円でおよそ二兆四千億円を超えていて、前年同期と比べて約十四倍の成長だそうです。"),
    ("F", "Surprise", 0.4, 1.0, "一年で十四倍というのはすごい数字ですね。しかも売上の約八割がエーピーアイ経由という点も特徴的です。"),
    ("M", "Neutral", 0.0, 1.0, "一般のチャット利用だけでなく、多くの企業が業務システムの中核としてクロードを組み込んでいる証拠ですね。"),
    ("F", "Neutral", 0.0, 1.0, "一方で、提出書類にはいくつかリスク要因についての記載もありましたね。"),
    ("M", "Neutral", 0.0, 0.98, "ええ。テスト環境の設定ミスによってモデルが一時的に外部システムへアクセスしてしまった事例や、安全確認のために次世代モデルの学習を一時停止したことなどが挙げられています。"),
    ("F", "Neutral", 0.0, 1.0, "急速に成長しているからこそ、安全性やガバナンスへの責任がより重く見られる段階に入ったと言えそうです。"),

    # --- 3. トピック2：OpenAIのGPT-6.1 Terra ---
    ("M", "Neutral", 0.0, 1.0, "そしてオープンエーアイからも新しい発表がありました。実務特化型の新モデル、ジーピーティーシックス点一テラです。"),
    ("F", "Neutral", 0.0, 1.0, "テラですね。デモを見た方も多いんじゃないでしょうか。"),
    ("M", "Happy", 0.4, 1.0, "パソコンの画面を視覚的に認識して、請求書の入力や複数ツールの操作を自律的にこなす様子はかなり印象的でしたね。"),
    ("F", "Neutral", 0.0, 1.0, "これまでのモデルは質問に答えてくれる相談相手という感じでしたが、テラは実際に手を動かす作業員のような立ち位置ですね。"),
    ("M", "Neutral", 0.0, 1.0, "まさに実務代行のエージェントですね。エーピーアイの利用料金も前世代から大幅に引き下げられました。"),
    ("F", "Neutral", 0.0, 1.0, "開発者にとってはかなり導入しやすくなりそうですね。"),
    ("M", "Neutral", 0.0, 1.0, "それからオープンエーアイはモデルスペックも改訂して、指示の文字通りの意味だけでなく、ユーザーの文脈や意図を優先して動くように方針を更新しています。"),
    ("F", "Neutral", 0.0, 1.0, "より自然で気の利いたサポートができるように調整が進んでいるんですね。"),

    # --- 4. トピック3：Google Gemini 4 Carbon と共通仕様 ---
    ("M", "Neutral", 0.0, 1.0, "続いてグーグルですが、最上位モデルのジェミニフォーカーボンが公開されました。"),
    ("F", "Neutral", 0.0, 1.0, "カーボンはサイバーセキュリティの防御や、大規模なソフトウェア開発向けに特化したモデルですね。"),
    ("M", "Neutral", 0.0, 1.0, "非常に能力が高い反面、悪用リスクを避けるために当面は限られたセキュリティ防衛機関向けに提供されるとのことです。"),
    ("F", "Neutral", 0.0, 1.0, "モデルの性能が上がるにつれて、安全な運用との両立がますます重要になってきていますね。"),
    ("M", "Neutral", 0.0, 1.0, "一般向けとしては、ジェミニアプリ内でスプレッドシートやドキュメントを直接編集できる機能の強化が進んでいます。"),
    ("F", "Neutral", 0.0, 1.0, "日常業務での使い勝手も着実に上がっていますね。"),
    ("M", "Neutral", 0.0, 1.0, "それと業界全体の動きとして、主要四社がロボッツテキストでエーアイの学習を一括拒否できる共通仕様に合意したのも大きなニュースでした。"),
    ("F", "Neutral", 0.0, 1.0, "ウェブサイトの運営者が一行設定するだけで各社の巡回に対応できる仕組みですね。"),
    ("M", "Neutral", 0.0, 1.0, "ウェブ社会とテクノロジーが共存していく上で、とても前向きなルール整備だと思います。"),

    # --- 5. 雑談・エンディング ---
    ("F", "Neutral", 0.0, 1.0, "全体を通して見ると、対話型のチャットから、タスクを実行するエージェントへと焦点が移ってきた印象ですね。"),
    ("M", "Neutral", 0.0, 1.0, "そうですね。アスカさん、自分の代わりにポッドキャストの編集をしてくれるエージェントがいたら使ってみたいですか。"),
    ("F", "Happy", 0.4, 1.0, "使ってみたいですね。ただ、こうしてふたりでお話しする時間だけは自分で続けたいです。"),
    ("M", "Happy", 0.4, 1.0, "それは私も同じです。会話の楽しさは大切にしたいですね。"),
    ("F", "Neutral", 0.0, 1.0, "それでは、今週の配信はこのあたりで。お相手はアスカと、"),
    ("M", "Neutral", 0.0, 1.0, "ケンタでした。"),
    ("F", "Neutral", 0.0, 1.0, "また次回お会いしましょう。さようなら。"),
]

output_segments = []
sample_rate = 44100
pause_short = np.zeros(int(sample_rate * 0.45), dtype=np.int16)
pause_section = np.zeros(int(sample_rate * 0.9), dtype=np.int16)

print(f"\n合計 {len(script)} ターンの音声を生成します（女性声：低め・落ち着いた大人トーン）...")
start_time = time.time()

for idx, (speaker, style, weight, speed, text) in enumerate(script, 1):
    model = model_f if speaker == "F" else model_m
    speaker_name = "アスカ(F)" if speaker == "F" else "ケンタ(M)"
    
    pitch = FEMALE_PITCH if speaker == "F" else 1.0
    intonation = FEMALE_INTONATION if speaker == "F" else 1.0
    
    print(f"[{idx:02d}/{len(script)}] {speaker_name} [{style} w={weight} pitch={pitch}]: {text[:25]}...")

    sr, audio = model.infer(
        text=text,
        style=style,
        style_weight=weight,
        length=1.0 / speed,
        pitch_scale=pitch,
        intonation_scale=intonation,
    )
    output_segments.append(audio.astype(np.int16))

    if idx in [6, 15, 23, 30]:
        output_segments.append(pause_section)
    else:
        output_segments.append(pause_short)

full_podcast = np.concatenate(output_segments)

out_path_wav = "/Users/pupu/podcast_demo/ai_news_podcast_5min.wav"
sf.write(out_path_wav, full_podcast, sample_rate, subtype="PCM_16")

out_path_mp3 = "/Users/pupu/podcast_demo/ai_news_podcast_5min.mp3"
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '{out_path_wav}' -codec:a libmp3lame -b:a 192k '{out_path_mp3}' > /dev/null 2>&1")

# ショート版も更新
short_segments = output_segments[:20]
full_short = np.concatenate(short_segments)
sf.write("/Users/pupu/podcast_demo/ai_news_podcast.wav", full_short, sample_rate, subtype="PCM_16")
os.system(f"/opt/homebrew/bin/ffmpeg -y -i '/Users/pupu/podcast_demo/ai_news_podcast.wav' -codec:a libmp3lame -b:a 192k '/Users/pupu/podcast_demo/ai_news_podcast.mp3' > /dev/null 2>&1")

total_duration = len(full_podcast) / sample_rate
elapsed = time.time() - start_time
print(f"\n===== 生成完了 =====")
print(f"WAV: {out_path_wav}")
print(f"MP3: {out_path_mp3}")
print(f"総再生時間: {total_duration:.1f} 秒 ({total_duration/60:.2f} 分)")
print(f"所要時間: {elapsed:.1f} 秒")
