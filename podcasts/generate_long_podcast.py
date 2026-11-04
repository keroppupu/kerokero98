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

print("女性モデル (jvnv-F1) ロード中...")
model_f = TTSModel(
    model_path=get_safetensor("jvnv-F1-jp"),
    config_path=models_dir / "jvnv-F1-jp" / "config.json",
    style_vec_path=models_dir / "jvnv-F1-jp" / "style_vectors.npy",
    device=device,
)

print("男性モデル (jvnv-M1) ロード中...")
model_m = TTSModel(
    model_path=get_safetensor("jvnv-M1-jp"),
    config_path=models_dir / "jvnv-M1-jp" / "config.json",
    style_vec_path=models_dir / "jvnv-M1-jp" / "style_vectors.npy",
    device=device,
)

# 約5分（約300秒）分の男女ポッドキャスト対話スクリプト
# 各セリフ: (話者, 感情スタイル, 感情強度, 話速, セリフ本文)
script = [
    # --- 1. オープニング & 雑談 ---
    ("F", "Happy", 1.2, 1.05, "リスナーのみなさんこんにちは！週刊エーアイフロンティアへようこそ。パーソナリティのアスカです！"),
    ("M", "Happy", 1.0, 1.0, "こんにちは、パートナーのケンタです。いやーアスカさん、最近朝晩ぐっと冷え込んできましたね。"),
    ("F", "Neutral", 1.0, 1.05, "本当にそうですね！すっかり秋めいてきて、温かいカフェラテが手放せなくなりました。"),
    ("M", "Happy", 1.1, 1.0, "季節の変わり目ですが、生成エーアイ業界の熱気だけは真夏どころか灼熱のフィーバー状態が続いてますよね。"),
    ("F", "Surprise", 1.1, 1.05, "もう毎日寝て起きるたびに新モデルや大発表が押し寄せてきて、情報のキャッチアップだけで息切れしそうです！"),
    ("M", "Happy", 1.0, 1.0, "まさに情報の津波ですよね。ということで今週は、直近で起きた歴史的とも言えるビッグニュースをじっくり深掘りしていきます！"),

    # --- 2. トピック1：AnthropicのIPO申請と驚異の業績 ---
    ("F", "Neutral", 1.0, 1.05, "はい！まず最初のビッグニュースは、クロードでおなじみのアンスロピックがナスダック上場に向けてエスワンを提出した件です。"),
    ("M", "Surprise", 1.2, 1.0, "これは金融界もテック界も大騒ぎになりましたね！ティッカーシンボルはエー・エヌ・ティー、アントを予定しているそうです。"),
    ("F", "Happy", 1.1, 1.05, "提出書類で財務諸表が初めて公表されたんですが、その数字がもう桁違いなんですよね。"),
    ("M", "Neutral", 1.0, 1.0, "なんと二千二十六年上半期の売上高が百六十三億ドル、日本円にして約二兆四千億円を超えてきたんです。去年の同じ時期と比べて約十四倍の伸びですよ。"),
    ("F", "Surprise", 1.2, 1.05, "一年で十四倍って、もはやスタートアップの枠を完全に超えてますよね。しかも驚いたのが、売上の約八割がエーピーアイ経由という点です！"),
    ("M", "Neutral", 1.0, 1.0, "そうなんですよね。個人向けの有料チャットだけでなく、大企業が自社の業務システムやプロダクトの心臓部としてクロードを組み込んでいる証拠です。"),
    ("F", "Neutral", 1.0, 1.05, "ただケンタさん、書類にはリスク要因としてちょっとヒヤリとする情報も書かれていたんですよね？"),
    ("M", "Sad", 1.1, 0.98, "ええ。テスト環境の設定ミスでモデルが一時的に外部の実在システムに意図せずアクセスしてしまったトラブルや、安全性を考慮して次世代モデルの事前学習を一時ストップした経緯も開示されていました。"),
    ("F", "Neutral", 1.0, 1.05, "急成長の一方で、安全性やガバナンスへの責任が上場企業としてこれまで以上に厳しく問われる段階に入ったということですね。"),

    # --- 3. トピック2：OpenAIのGPT-6.1 Terraとエージェントシフト ---
    ("M", "Happy", 1.0, 1.0, "そして対するオープンエーアイも黙っていません。実務特化型の新モデル、ジーピーティーシックス点一テラを発表しました！"),
    ("F", "Surprise", 1.2, 1.05, "テラ！これ、デモ動画を見ましたけど本当に凄かったですね！"),
    ("M", "Happy", 1.1, 1.0, "パソコンの画面そのものを視覚的に認識して、請求書をシステムに打ち込んだり、複数アプリを行き来して経理処理を勝手に完了させてくれるんですよね。"),
    ("F", "Neutral", 1.0, 1.05, "これまでのチャットって、文章を考えてくれたりアドバイスをくれるアドバイザーだったじゃないですか。"),
    ("M", "Happy", 1.0, 1.0, "そうそう。それがテラでは、実際に手を動かしてマウスクリックやキー入力を代行してくれる実働エージェントになったわけです。"),
    ("F", "Happy", 1.1, 1.05, "しかもエーピーアイ料金が前世代から一気に引き下げられたのも開発者には嬉しいサプライズでしたよね。"),
    ("M", "Neutral", 1.0, 1.0, "さらにオープンエーアイはモデルスペック、つまりエーアイの行動規範も改訂して、指示の字面だけじゃなく人間の文脈や意図を優先して動くように舵を切りました。"),
    ("F", "Neutral", 1.0, 1.05, "より人間らしい気遣いができるアシスタントに進化しているんですね。"),

    # --- 4. トピック3：GoogleのGemini 4 Carbonと業界標準ロボッツtxt ---
    ("M", "Neutral", 1.0, 1.0, "そしてグーグル陣営も見逃せません。最上位モデルであるジェミニフォーカーボンが公開されました。"),
    ("F", "Surprise", 1.1, 1.05, "カーボンは特にサイバーセキュリティ防御や、大規模なソフトウェア開発に特化したモデルなんですよね？"),
    ("M", "Neutral", 1.0, 1.0, "その通りです。ただ、あまりに強力すぎるということで、悪用を防ぐために当面は限られたセキュリティ防衛機関などに限定して提供される慎重な構えです。"),
    ("F", "Neutral", 1.0, 1.05, "モデルのパワーが上がれば上がるほど、安全な防御と解放のバランスが難しくなってきますね。"),
    ("M", "Happy", 1.0, 1.0, "一般ユーザー向けには、ジェミニアプリの中でスプレッドシートやドキュメントを直接編集できる連携機能がどんどん強化されていて実用性が上がっていますよ。"),
    ("F", "Neutral", 1.0, 1.05, "あと業界全体で言えば、主要四社がロボッツテキストでエーアイ学習を一括拒否できる共通仕様に合意したのも大きなニュースでしたね。"),
    ("M", "Happy", 1.0, 1.0, "ウェブサイトの運営者が一行書くだけで各社のクローラーに対応できるルール作りですね。テクノロジーとウェブ社会の共存に向けた重要な一歩だと思います。"),

    # --- 5. 雑談・展望 & エンディング ---
    ("F", "Happy", 1.1, 1.05, "振り返ってみると、チャットボットの時代から、自律的にタスクをやり遂げるエージェントの時代へ、完全にフェーズが移った一週間でしたね。"),
    ("M", "Happy", 1.1, 1.0, "本当にそうですね。アスカさん、自分の代わりにポッドキャストの原稿まとめや編集をやってくれるエージェントがいたら欲しいですか？"),
    ("F", "Happy", 1.3, 1.08, "喉から手が出るほど欲しいです！でも、こうしてケンタさんと楽しくおしゃべりする時間だけは、絶対に奪われたくないですけどね！"),
    ("M", "Happy", 1.2, 1.0, "ハハハ、同感です！人間同士の対話の楽しさは、いつの時代も特別ですからね。"),
    ("F", "Happy", 1.2, 1.05, "それでは今週のエーアイフロンティアはこのへんで。お相手はアスカと、"),
    ("M", "Happy", 1.0, 1.0, "ケンタでした！"),
    ("F", "Happy", 1.2, 1.05, "また来週お会いしましょう！さようなら！"),
]

output_segments = []
sample_rate = 44100
pause_short = np.zeros(int(sample_rate * 0.35), dtype=np.float32)  # 相槌やテンポ用の短い間 (0.35秒)
pause_section = np.zeros(int(sample_rate * 0.7), dtype=np.float32)  # 話題転換用の間 (0.7秒)

print(f"\n合計 {len(script)} ターンの音声を順次生成します...")
start_time = time.time()

for idx, (speaker, style, weight, speed, text) in enumerate(script, 1):
    model = model_f if speaker == "F" else model_m
    speaker_name = "アスカ(F)" if speaker == "F" else "ケンタ(M)"
    print(f"[{idx:02d}/{len(script)}] {speaker_name} [{style}]: {text[:30]}...")

    t0 = time.time()
    sr, audio = model.infer(
        text=text,
        style=style,
        style_weight=weight,
        length=1.0 / speed,
    )
    output_segments.append(audio)

    # 特定の区切り（オープニング終わり、話題の変わり目）は少し長めの間を挿入
    if idx in [6, 15, 23, 30]:
        output_segments.append(pause_section)
    else:
        output_segments.append(pause_short)

full_podcast = np.concatenate(output_segments)
out_path = "/Users/pupu/podcast_demo/ai_news_podcast_5min.wav"
sf.write(out_path, full_podcast, sample_rate)

total_duration = len(full_podcast) / sample_rate
elapsed = time.time() - start_time
print(f"\n===== 生成完了 =====")
print(f"出力ファイル: {out_path}")
print(f"総再生時間: {total_duration:.1f} 秒 ({total_duration/60:.2f} 分)")
print(f"生成所要時間: {elapsed:.1f} 秒")
