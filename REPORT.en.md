# Ten-level image generation benchmark — RTX 3060 Ti

日本語: [REPORT.ja.md](REPORT.ja.md)

## Hardware and setup

- Date: 2026-11-09
- GPU: NVIDIA RTX 3060 Ti, 8192 MiB
 - Counterfeit V2.5 (SD1.5 family): fp16, 23 steps, CFG 7; 10/10 PNGs generated. Inference time excluding model startup: 30.28 s total; max PyTorch reserved GPU memory ≈3.72 GiB.
 - FLUX.2 Klein 4B FP8 with Qwen3 4B FP4 encoder: 4 steps, CFG 1; 10/10 outputs generated with low-VRAM model offload and CPU VAE.
 - These are exploratory runs, not controlled quality/speed rankings: different resolutions, steps and model families.
 - **Successfully saving an image is not the same as satisfying the instructions.**

## Images

| Level | Counterfeit | Seconds | FLUX.2 | Seconds | Object-level composite | img2img refinement |
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

[Counterfeit contact sheet](images/baseline_contact_sheet.jpg) / [FLUX.2 contact sheet](images/flux2_contact_sheet.jpg) / [Side-by-side comparison](images/comparison_contact_sheet.jpg)

## Baseline visual findings

- Lv.1: Multiple apples instead of exactly one.
- Lv.2: Blue teapots were duplicated; the specified two pears were absent.
- Lv.3: Greenhouse interior; no enclosing lightbulb or plinth.
- Lv.4: Wet street and bicycle, but wheel immersion and exact reflection not established.
- Lv.5: Tree and train, but neither exactly three spiral loops nor five cars.
- Lv.6: Mechanical aquatic form, but no legible glass enclosure or fin angles.
- Lv.7: People at a mirror; chessboard and specified pieces absent.
- Lv.8: Multilevel building, but four intended functions and elevator missing.
- Lv.9: Multiple related-looking adventurers; scar and exact viewpoints inconsistent.
- Lv.10: Cathedral interior instead of hourglass with aligned harbors.

## Structured workflow experiments

1. Generate low-resolution scenes first (512–768 px). This reduces VRAM, but does not guarantee logical constraints.
2. Level 2: independently generate a background, blue teapot, a horizontal pear and an upright pear; perform threshold-based background removal and place subjects at fixed coordinates.
3. Level 8: generate four cutaway floor bands independently (farm, market, homes, power) and add one geometrically continuous elevator shaft.
4. Level 9: generate four views with shared identity prompt tokens and assemble a 4-panel contact sheet; prompt reuse alone does not guarantee identity.
5. Level 10: create morning and night versions from the *same source harbor pixels* and composite them into the hourglass. Architecture alignment is exact, but lighting is not physically simulated.
6. Levels 2 and 8: upscale the compositions 1.25× and perform low-denoise image-to-image refinement (strength=0.20). Refiner may overwrite compositional constraints.

## Limitations

- Counting, reflection, anatomy, geometry, occlusion and identity are distinct failure modes.
- Layering gives deterministic positions but often introduces inconsistent shadows, light, scale, and visible seams.
- Results are single-seed and must not be generalized to probabilities or a model leaderboard.
- Next step: regional conditioning, ControlNet or segmentation masks plus multiple seeds.
- See [scripts](scripts/) for executed code, [data](data/) for prompts, seeds, time and output statuses; model weights are not redistributed.
