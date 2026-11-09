# RTX 3060 Ti image generation benchmark / 画像生成ベンチマーク

[日本語レポート](REPORT.ja.md) · [English report](REPORT.en.md)

Ten difficulty levels, direct text-to-image (Counterfeit V2.5 / FLUX.2 Klein) versus structured low-resolution object generation, compositing and image-to-image refinement.

10段階の課題で、直接生成と、物体別低解像度生成→座標合成→高解像度化を比較。

[Direct baseline](images/baseline_contact_sheet.jpg) · [FLUX.2](images/flux2_contact_sheet.jpg) · [Side-by-side](images/comparison_contact_sheet.jpg)

**Image generated ≠ prompt followed / 生成成功 ≠ 指示遵守。**


[Animagine XL contact sheet](images/animagine_contact_sheet.jpg) · [U2NetP object extraction](images/lv02_rembg_composite.png) · [Reference-based harbor fix](images/lv10_reference_composite.png)

See the bilingual reports for visual inspection notes, memory failures, retries, and method verdicts.


## Advanced image benchmark

[Advanced Lv.11–18 / 上級課題](advanced-11-18/README.md) — [日本語](advanced-11-18/REPORT.ja.md) | [English](advanced-11-18/REPORT.en.md)
