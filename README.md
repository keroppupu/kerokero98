# kerokero98 - AI Music & MV Collection

AI生成によるオリジナル楽曲と、Whisperミリ秒同期・キネティックタイポグラフィによる縦型（9:16）YouTube Shorts MVの制作コレクションです。

---

## 🏕️ Track 2: 荷物が帰りは入らんだに！ (YouTube Shorts MV)

キャンプのパッキングあるあるをテーマにした、BPM200超高速電波系ラップ楽曲＆イラスト連動縦型ショートMVです。

### 📁 収録ファイル
- `hairan_dani_shorts_mv.mp4`: 1080x1920 (9:16) YouTube Shorts / TikTok用 MV動画（45秒フルバージョン）
- `hairan_dani_full_lyrics.mp3`: 楽曲オリジナル音源（ACE-Step 1.5 生成、200 bpm、全歌詞完全歌唱版）
- `render_illustrated_shorts_mv.py`: シーン切り替え・クロスフェード連動型MV生成Pythonスクリプト
- `assets/chara_happy.jpg`: キャンプ出発時の笑顔パッキングイラスト
- `assets/chara_panic.jpg`: 撤収時のパンパン頭抱え困り顔イラスト

### 🎵 楽曲情報
- **曲名**: 荷物が帰りは入らんだに！
- **テンポ**: BPM 200
- **歌唱**: 電波系ハイスピード女性ボーカル（ラップ＆シャウト）
- **楽曲生成**: ACE-Step 1.5 (acestep-v15-turbo DiT + MLX Metal 加速)
- **MV演出**: 筑紫B丸ゴシック、Whisperタイムコード同期、シーン切り替え、クロスフェード、ビート連動バウンス＆シェイク

### 📝 歌詞
```text
[Verse 1]
行きは入った荷物が　帰りは入らんだに！
行きは入った荷物が　帰りは入らんだに！

[Verse 2]
入った！入らん！入った！入らん！
同じカバン！同じギア！増えとらんに！増えとらんに！

[Chorus]
なんでだや！？パンパンだに！チャックがパンパンだら！
行きはスッポリ！帰りはパンパンだに！
入らん！入らん！ばか入らん！
行きは入った荷物が　帰りは入らんだに！！

[Outro]
パンパンだに！
入らんだに！！
```

---

## 🧦 Track 1: 消えた片方の靴下 (YouTube Shorts JIZURA MV)

AI生成による女性アイドルバラード楽曲と、Whisper実測同期による縦型（9:16）キネティック・タイポグラフィ（JIZURA）MVプロジェクトです。

### 📁 収録ファイル
- `lost_sock_jizura_shorts.mp4`: 1080x1920 (9:16) YouTube Shorts / TikTok用 MV動画（120秒フルバージョン）
- `lost_sock_ballad_v4.mp3`: 楽曲オリジナル音源（ACE-Step 1.5 生成、88 bpm）

### 🎵 楽曲情報
- **曲名**: 片方だけの足音
- **歌唱**: 女性アイドル（バラード）
- **演奏**: ピアノ、ストリングス、アコースティックギター
- **楽曲生成**: ACE-Step 1.5 (acestep-5Hz-lm-0.6B + acestep-v15-turbo)
- **MV制作**: JIZURA キネティック・タイポグラフィ レンダラー + Whisper ミリ秒同期

### 📝 歌詞
```text
[Verse]
ほすのを わすれたあさ
へやは しずかすぎて
せんたくものの なかで
ひとつだけ かけてた

[Chorus]
みつからない かたほうを
さがして あるくの
つめたい ゆかのうえに
あしを おいたまま
きえた そのさきで
まってるのは だれ？
きみのぬくもりを
ずっと おもいだす

[Outro]
きょうも ひとりきり
あしおとが ひびく
ららら ららら
```

## 限界探索チャンネル - 地図から消えた廃村配信 (VTuber JIZURA MV)
- **楽曲**: `haison_haishin.mp3` (ACE-Step 1.5 生成、女性ボーカル J-Rock)
- **動画**: `haison_haishin_jizura_mv.mp4` (1080p Full HD JIZURA キネティック・タイポグラフィ MV)
- **生成スクリプト**:
  - `generate_song.py`: 分割生成・音声リファレンスによる声質維持・クロスフェード結合
  - `render_haison_mv.py`: 歌声同期、目線加工写真・探索動画カットイン、JIZURAタイポグラフィ
