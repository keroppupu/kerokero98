#!/usr/bin/env python3
"""
generate_song.py - Generate 2 parts of the song maintaining female vocal consistency, then concatenate with crossfade.
"""
import os
import sys
import time
import subprocess
import torch

os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

ACE_STEP_ROOT = "/Users/pupu/.gemini/antigravity/scratch/ACE-Step-1.5"
sys.path.insert(0, ACE_STEP_ROOT)

from loguru import logger
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

CHECKPOINT_DIR = os.path.join(ACE_STEP_ROOT, "checkpoints")
OUTPUT_DIR = "/Users/pupu/Downloads/vtuber_song"

# Detailed prompt locking the vocal identity and music style
PROMPT = (
    "japanese modern vocaloid style j-pop rock, fast tempo, driving electric guitar, punchy bass, synth, live drums, "
    "clear melodic cute and expressive young Japanese female vocal, consistent solo female singer, emotional and dynamic"
)

# Part 1 Lyrics (~60-70s)
LYRICS_PART1 = """[Spoken Intro]
「はいどーも！げんかいたんさくチャンネルです！
きょうはね、ネットでうわさの『ちずからきえたはいそん』…きてます！
みんな、こうひょうかとチャンネルとうろくよろしくね！」

[Verse 1]
がかくなじみ　ジンバルかたてに
たちいりきんしの　サビついたフェンスごえ
「ここヤバくない？」　カメラにウィンク
どうせつじわじわ　のびるアドレナリン
ゆかのぬけそうな　もくぞうのはいりょかん
ホコリのにおいと　カビたくろでんわ

[Pre-Chorus]
コメントらんは「うしろ！うしろ！」のおやくそく
はいはい、いつものノリでしょ？わかってるって
やらせはしないしゅぎだけど
ちょっとくらいもるのが　クリエイターだましい
「おっと、いまなにかおとがしたような…？」

[Chorus]
ああ　バズりたい　バズりたい
しんやのはいきょで　かみかいをプリーズ
かいちゅうでんとうの　あかりがふしぜんにチカチカ
（あれ、えんしゅつじゃないよ、ガチでヤバいやつ？）
さいせいかいすう　みぎかたあがり
でもまって、はいってきた いりぐち…どこだっけ？"""

# Part 2 Lyrics (~75-80s)
LYRICS_PART2 = """[Verse 2]
けんがいギリギリ　でんぱがとぎれる
スパチャのつうちも　バグってループ
「きのせいだよね…」　あしおとペタ、ペタ
おれしかいない　はずのながいろうか
カメラをおろして　そっとふりかえる
にくがんじゃみえないのに　モニターにはうつる『なにか』

[Pre-Chorus]
げきりゅうだったコメントらんが　いっせいにピタッととまる
すうびょうご、がめんいっぱいの『にげて』『にげて』『にげて』
やらせじゃない　マジでむり
さんきゃくなんてすてて　とにかくはしりだしたい
なのにあしが、ゆかに はりついたみたいに うごかない

[Chorus]
ああ　かえりたい　かえりたい
しんれいスポットで　ガチなき どげざはいしん
いきがきれる　しんぞうがはれつしそう
（おいかけてくるよ、ガチでヤバいやつ！）
とうろくしゃすうより　じぶんのいのちがだいじ
でもまって、でぐちのドアが…あかないんだけど！！

[Bridge]
たのみのつなのスマホバッテリー　なぜかきゅうに のこりいちパーセント
さいごのひかりが　ふっとおちるしゅんかん
くらやみのなか、まうしろから みみもとでささやく
つめたくて、ノイズまじりのおんなのこえ
「……ねぇ……チャンネル、とうろく、して、ね……？」

[Outro / Spoken]
「えっ、ちょ、まっ、やめ……！！」
（ガシャァァン！きかいがたおれるおと）
（プツンッ！はいしんがとぎれるおと）
……
…………
………………
（はいしんは しゅうりょう しました）"""

def init_models():
    print("[1/5] Initializing ACE-Step DiT...")
    dit_handler = AceStepHandler()
    status_msg, success = dit_handler.initialize_service(
        project_root=ACE_STEP_ROOT,
        config_path="acestep-v15-turbo",
        device="auto",
        offload_to_cpu=True,
    )
    if not success:
        raise RuntimeError(f"DiT init failed: {status_msg}")

    print("[2/5] Initializing ACE-Step LM (acestep-5Hz-lm-0.6B MLX)...")
    llm_handler = LLMHandler()
    status_msg, success = llm_handler.initialize(
        checkpoint_dir=CHECKPOINT_DIR,
        lm_model_path="acestep-5Hz-lm-0.6B",
        backend="mlx",
        device="auto",
        offload_to_cpu=False,
    )
    if not success:
        raise RuntimeError(f"LLM init failed: {status_msg}")

    return dit_handler, llm_handler

def generate_part(dit_handler, llm_handler, lyrics, duration, output_path, reference_audio=None, seed=42):
    print(f"\n--- Generating {os.path.basename(output_path)} (duration: {duration}s, ref: {reference_audio}) ---")
    params = GenerationParams(
        task_type="text2music",
        thinking=True,
        use_cot_caption=False, # preserve exact female vocal prompt
        use_cot_language=False,
        cot_vocal_language="ja",
        caption=PROMPT,
        lyrics=lyrics,
        bpm=160,
        keyscale="Am",
        timesignature="4/4",
        vocal_language="ja",
        duration=duration,
        inference_steps=8,
        guidance_scale=7.0,
        lm_cfg_scale=2.0,
        lm_temperature=0.7,
        seed=seed,
        reference_audio=reference_audio,
    )

    config = GenerationConfig(
        batch_size=1,
        audio_format="wav",
    )

    result = generate_music(
        dit_handler,
        llm_handler,
        params=params,
        config=config,
        save_dir=OUTPUT_DIR,
    )

    if not result.success or not result.audios:
        raise RuntimeError(f"Generation failed: {result.status_message} {result.error}")

    raw_path = result.audios[0]["path"]
    print(f"Generated raw file: {raw_path}")
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(raw_path, output_path)
    print(f"Saved to: {output_path}")
    return output_path

def concat_audio(part1_path, part2_path, final_output_path):
    print(f"\n--- Concatenating {part1_path} and {part2_path} into {final_output_path} ---")
    # Crossfade 2 seconds between part 1 and part 2
    cmd = [
        "/opt/homebrew/bin/ffmpeg", "-y",
        "-i", part1_path,
        "-i", part2_path,
        "-filter_complex", "acrossfade=d=2.0:c1=tri:c2=tri",
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        final_output_path
    ]
    subprocess.check_call(cmd)
    print(f"Successfully generated final song: {final_output_path}")

def main():
    dit_handler, llm_handler = init_models()

    part1_wav = os.path.join(OUTPUT_DIR, "part1.wav")
    part2_wav = os.path.join(OUTPUT_DIR, "part2.wav")
    final_mp3 = "/Users/pupu/Downloads/限界探索チャンネル_廃村配信.mp3"

    # Part 1 (Intro, A1, B1, Sabi1)
    generate_part(
        dit_handler, llm_handler,
        lyrics=LYRICS_PART1,
        duration=68,
        output_path=part1_wav,
        reference_audio=None,
        seed=4242
    )

    # Part 2 (A2, B2, Sabi2, C, Outro) using Part 1 as reference audio to keep the voice & timbre consistent!
    generate_part(
        dit_handler, llm_handler,
        lyrics=LYRICS_PART2,
        duration=80,
        output_path=part2_wav,
        reference_audio=part1_wav,
        seed=4242
    )

    # Concatenate & Crossfade
    concat_audio(part1_wav, part2_wav, final_mp3)

if __name__ == "__main__":
    main()
