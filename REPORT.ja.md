# 10段階の画像生成実験 — RTX 3060 Ti

English: [REPORT.en.md](REPORT.en.md)

## 実行環境と方法

- 実行日: 2026-11-09
- GPU: NVIDIA RTX 3060 Ti, 8192 MiB
- Counterfeit V2.5: SD1.5系、float16、23 steps、CFG=7.0、10/10枚生成成功。推論のみの合計 30.28秒、観測されたPyTorch最大メモリ予約量約3.72GiB。
- FLUX.2 Klein 4B: FP8 diffusion model、Qwen3 4B FP4 text encoder、4 steps、CFG=1、10/10枚生成成功。低VRAM・CPU VAE。初回起動には重み読み込みを含む。
- 比較は探索的なもの。モデルごとに解像度・stepが異なり、速度・品質の厳密な公平比較ではない。
- **画像ファイルの生成成功とプロンプトの指示遵守は別の評価項目**。

## 生成結果

| 難度 | Counterfeit | 時間(s) | FLUX.2 | 時間(s) | 個別生成・合成 | img2img高解像度補正 |
|---|---|---:|---|---:|---|---|
| 1 | [image](images/lv01_baseline.png) | 2.8 | [image](images/lv01_flux2.png) | 93.27 | — | — |
| 2 | [image](images/lv02_baseline.png) | 2.7 | [image](images/lv02_flux2.png) | 24.02 | [image](images/lv02_composite.png) | [image](images/lv02_refined.png) |
| 3 | [image](images/lv03_baseline.png) | 2.7 | [image](images/lv03_flux2.png) | 24.01 | — | — |
| 4 | [image](images/lv04_baseline.png) | 2.7 | [image](images/lv04_flux2.png) | 24.01 | — | — |
| 5 | [image](images/lv05_baseline.png) | 2.7 | [image](images/lv05_flux2.png) | 24.01 | — | — |
| 6 | [image](images/lv06_baseline.png) | 2.7 | [image](images/lv06_flux2.png) | 21.01 | — | — |
| 7 | [image](images/lv07_baseline.png) | 2.7 | [image](images/lv07_flux2.png) | 21.15 | — | — |
| 8 | [image](images/lv08_baseline.png) | 4.0 | [image](images/lv08_flux2.png) | 24.01 | [image](images/lv08_composite.png) | [image](images/lv08_refined.png) |
| 9 | [image](images/lv09_baseline.png) | 3.2 | [image](images/lv09_flux2.png) | 24.01 | [image](images/lv09_composite.png) | — |
| 10 | [image](images/lv10_baseline.png) | 4.1 | [image](images/lv10_flux2.png) | 21.01 | [image](images/lv10_composite.png) | — |

[Counterfeit一覧](images/baseline_contact_sheet.jpg) / [FLUX.2一覧](images/flux2_contact_sheet.jpg) / [比較一覧](images/comparison_contact_sheet.jpg)

## Counterfeit一次生成の目視評価

- Lv.1: リンゴが複数個になり1個の指定に失敗。
- Lv.2: 青い急須は生成されたが重複し、洋梨2個が見当たらない。
- Lv.3: 温室風の室内で、外側の電球と台座は見当たらない。
- Lv.4: 濡れた道路と自転車は描かれたが、前輪の水没と厳密な鏡像は未達。
- Lv.5: 列車と木はあるが、螺旋線路3周・5両の構造は未達。
- Lv.6: 機械的な海洋生物はあるが、透明な外装や胸びれは判然としない。
- Lv.7: 鏡の前の人物になり、チェス盤と指定駒が欠落。
- Lv.8: 多層建築にはなったが、指定の4用途・昇降機は再現されていない。
- Lv.9: 似た服装の人物が複数あるが、傷・視点の完全な一貫性はない。
- Lv.10: 大聖堂の室内となり、砂時計・同一の港町を再現していない。

## 採用した実験フロー

1. まず単純な低解像度（512〜768px）で構図と対象の存在を試す。高解像度化は論理的制約の遵守を保証しない。
2. Lv2は背景・急須・横向き洋梨・直立洋梨を別々に生成し、白背景から簡易抽出して決めた座標に貼り合わせる。
3. Lv8は農園・市場・住宅・発電所を4枚の別画像で作り、上下に並べて昇降路を幾何学的に接続する。
4. Lv9は正面・側面・背面・走行を別々に生成し4コマ化するが、人物同一性は独立したプロンプトだけでは保証されない。
5. Lv10は港町の1枚の画像から昼・夜の2状態を作り、画素位置を同一にした上で砂時計内へ重ねる。建物の一致は保証されるが、照明の物理的自然さは保証されない。
6. Lv2・8の構成後画像を1.25倍補間し、拡散img2img（strength=0.20）で融合・細部修正する試験を行う。補正で部品が消える恐れもある。

## 限界と評価上の注意

- 個数・鏡像・反射・部品の相互作用・人体の同一性を構図と独立に評価する必要がある。
- 層合成は個数や相対位置を強制できるが、遮蔽・影・材質・遠近感・輪郭線の連続性が崩れる。
- 単一seedのサンプルは成功率を示さない。将来は複数seedと領域条件付けモデル、ControlNet等を試したい。
- 自動的な画像の美観スコアは条件遵守スコアの代用にできない。失敗例は画像と併せて公開。

## 再現

ソース: [scripts](scripts/) ・設定と測定: [data](data/) ・出力画像: [images](images/)。モデル重みは収録していません。モデル提供元の利用条件に従ってください。
