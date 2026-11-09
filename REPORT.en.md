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


## Qualitative FLUX.2 visual assessment

The following near-complete / partial / fail labels are subjective inspections of one sample per prompt, not controlled scores.

| Level | Qualitative status | Observations |
|---|---|---|
| 1 | partial | Exactly one apple, but two leaves rather than one. |
| 2 | near-complete | Blue teapot between two pears; orientation is close to instructions. |
| 3 | near-complete | Lightbulb, wood base, miniature greenhouse and bench are legible. |
| 4 | partial | Bicycle, wet cobbles, reflection are convincing; exact front-wheel immersion unclear. |
| 5 | partial | Tree, spiral railway and train recognizable, but exact three loops/five cars not clear. |
| 6 | partial | Glass/mechanical whale with gears; prescribed fin orientations are unclear. |
| 7 | fail | Mirror stays blank; more than exactly three chess pieces. |
| 8 | partial | Farm, market, power level exist, but residential level replaced by market-like room. |
| 9 | partial | Similar silver-haired orange-jacket explorer appears in only three views. |
| 10 | partial | Day/night towns in hourglass, but house placements differ and glass geometry is imperfect. |

## Animagine XL 3.1 extra tests

[Three-image contact sheet](images/animagine_contact_sheet.jpg) / [Measurements](data/animagine.json) / [Original script](scripts/animagine.py) / [Low-resolution retry](scripts/animagine_retry.py)

- Level 7 at 768×512 (25 steps) generated in 7.76 s, but mirror/chess constraints were not satisfied.
- Levels 9 and 10 initially hit CUDA out-of-memory at 768×512 (failed to allocate a further 192 MiB). Measured max PyTorch reserved GPU memory for the successful Lv7: 7.47 GiB.
- Retrying Lv9/Lv10 at 640×384 with expandable CUDA allocator segments succeeded in 4.02 and 3.56 s respectively.
- Lv9 had four related-looking characters but no true running pose. Lv10 was an abstract circular image, not a coherent hourglass.
- **Lower resolution was a practical solution for 8GB-VRAM OOM** in this case, not evidence of better semantic compliance or visual quality.

## Component workflow verdicts

| Method | Case | What worked | What failed |
|---|---|---|---|
| Low-resolution Counterfeit one-shot | 1–10 | Fast and memory-efficient | Complex constraints often ignored |
| One-shot FLUX.2 Klein 4B | 1–10 | Natural multi-object integration, best near-compliance on Lv2/Lv3 | First-load overhead, ≈7.5GB live GPU occupancy; failures in mirrors, floor functions, panels, aligned structures |
| Independent objects + naive whiteness mask + composition | 2 | Positions are deterministic | Rectangular cutouts, unrelated backgrounds and unwanted objects |
| U2NetP (rembg) matte + composition | 2 | Reduced rectangular matte; CPU inference step 1.58 s including initial download | Background/extra-fruit artifacts remained; considerably worse than direct FLUX |
| Generate four floors + draw one elevator | 8 | Exact floor order and number | Harsh seams, different perspective and lighting |
| Generate four separate viewpoints + assemble | 9 | Exactly four panels | No guaranteed identity or viewpoint accuracy |
| Same harbor pixels, transformed day-to-night and placed in hourglass | 10 | Source building locations shared | Glass silhouette/masks look unnatural |
| Reproject FLUX upper harbor to lower bulb | 10 | Preserves FLUX exterior glass scene better | Night scene overly dark and perspective not fully aligned |
| 1.25x resize + low-strength img2img | 2/8 | Layout remained mostly stable | strength=0.20 did not remove the major cutout seams |

[U2NetP matte output](images/lv02_rembg_composite.png) / [Harbor reference re-composition](images/lv10_reference_composite.png) / [Postprocessing measurements](data/postprocess.json) / [Postprocessing source](scripts/postprocess.py)

### Practical conclusions

**The most promising workflow from these specific trials is to build a global layout directly with FLUX.2, then correct only regions that demand exact placement/counting with explicit masks and localized conditioning.** Low resolution helped save VRAM and allow iteration, but did not by itself solve compositional constraints.

Naive independent generation of every subject followed by simple compositing was unsuccessful in these tests: unrelated lighting, scale and unwanted scene content damaged coherence. The next meaningful experiments should use localized FLUX editing, ControlNet/segmentation masks, and shared image-reference conditioning for character viewpoints.
