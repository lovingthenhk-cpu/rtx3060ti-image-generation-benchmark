# RTX3060Ti Advanced image generation: Lv.11–18

[日本語](REPORT.ja.md) | [Selected](images/selected_contact.jpg) | [Counterfeit](images/counterfeit_contact.jpg) | [FLUX.2](images/flux2_contact.jpg)

## Outcome

All eight difficult tasks received direct generation attempts, structured alternatives, and selected retests. All eight have saved output candidates. However, complete compliance with every condition was neither achieved nor verified for all cases.

Auditable numerical/topological invariants include Lv11 (3 continuous ribbons, 6 ends), Lv12 (3 movers, 6 contacts, 4 table legs), Lv14 (12 arms, 11 lit bulbs), and Lv16 (5 islands and 5 bridges). Dynamics (Lv13), physically simulated caustics (Lv15), functional assembly (Lv17), and fully convincing impossible stairs (Lv18) remain unverified. An engineering schematic is not a photorealistic success.

## Hardware and timing

- Date: 2026-11-10 JST. NVIDIA RTX3060Ti 8GB.
- Counterfeit V2.5 (SD1.5 fp16, 27 steps, CFG7, ~768px): 8/8 output saved, sum inference ~37.0 s, peak CUDA reservation 4.68 GiB.
- FLUX.2 Klein 4B FP8 with Qwen3 4B FP4 (ComfyUI, 4 steps, CFG1, ~640px, CPU VAE/low-VRAM): 8/8 saved, total submitted-task wall ~210 s, including first run ~99 s.
- Three prompt rewrites for Lv11,12,18. Seven SD1.5 image-to-image images and two FLUX image-to-image files were produced.
- The FLUX image-to-image outputs collapsed into noise despite API success and are not viable refinements. SD1.5 mostly preserved layout but added little photographic quality.
- Different resolutions/steps prevent a controlled model ranking; single-seed tests do not estimate success probabilities.

## Selected candidates

| Task | Candidate | Structural status | Compare |
|---|---|---|---|
| 11 Three ribbons | [candidate](images/lv11_constructed.png) | structure_pass | [comparison](images/lv11_comparison.jpg) |
| 12 Three movers | [candidate](images/lv12_constructed.png) | structure_pass | [comparison](images/lv12_comparison.jpg) |
| 13 Mechanical chain | [candidate](images/lv13_constructed.png) | structure_partial | [comparison](images/lv13_comparison.jpg) |
| 14 Twelve lamps | [candidate](images/lv14_constructed.png) | structure_pass | [comparison](images/lv14_comparison.jpg) |
| 15 Glass refraction | [candidate](images/lv15_constructed.png) | partial | [comparison](images/lv15_comparison.jpg) |
| 16 Five islands | [candidate](images/lv16_constructed.png) | structure_pass | [comparison](images/lv16_comparison.jpg) |
| 17 Exploded watch | [candidate](images/lv17_constructed.png) | partial | [comparison](images/lv17_comparison.jpg) |
| 18 Penrose stairs | [candidate](images/lv18_flux2_variant.png) | partial | [comparison](images/lv18_comparison.jpg) |

A structure_pass label indicates that specific geometric/counting constraints were checked; it does not imply total prompt compliance.

## Per-task observations

### Lv.11 Three ribbons

Counterfeit turned strands into hanging banners; FLUX generated three separate knots and the retry branched endpoints. Deterministic continuous color paths and six ends are auditable, but realistic material physics is unverified.

### Lv.12 Three movers

Counterfeit showed seated people; FLUX produced four movers then two after retry. Constructed composition guarantees three silhouettes, six hand contacts, four legs and elevation order. Its style is not photorealistic.

### Lv.13 Mechanical chain

FLUX depicted partial components without the full causal chain. A diagram fixes the funnel, sloping ramp, steel ball, left-down seesaw and bell. Motion and collision dynamics were not simulated.

### Lv.14 Twelve lamps

Twelve arms at exact 30-degree intervals are calculated with trigonometry. Exactly eleven lamps glow and one at two oclock is dark. Material rendering is stylized. Naive FLUX image-to-image collapsed into colorful noise.

### Lv.15 Glass refraction

Three glass spheres and red-blue striped background. Two surface refractions per camera ray use Snell law. Ground caustics are only illustrative. FLUX appeared photoreal but did not guarantee correct optics or depth.

### Lv.16 Five islands

Counterfeit lost bridge topology; FLUX drew a bridge ring without a guaranteed vertex count. The deterministic graph contains five vertices, five edges, degree two at every node, and no crossings.

### Lv.17 Exploded watch

FLUX generated a pleasing watch explosion but not all mechanical details. The structured version aligns nine stages on one axis. Physical assembly and actual meshing/function of gears have not been validated.

### Lv.18 Penrose stairs

First models generated normal staircases. A rewritten FLUX prompt produced a connected four-flight stone loop. Strictly ascending clockwise perception remains ambiguous, so full success is not claimed.

## Techniques and limitations

1. Direct FLUX.2 was generally more semantically coherent than Counterfeit, but text-only prompting did not ensure exact people, endpoints or bridge graph counts.
2. Deterministic geometry enforced ribbon continuity, equal angular lamp spacing, and bridge topology but limited photorealism.
3. Naive FLUX VAEEncode + SplitSigmasDenoise + SamplerCustomAdvanced reference editing produced dense noise, not a validated edit.
4. Low-strength SD1.5 img2img retained layout with modest material improvements and degraded lettering.
5. Further research: exact person/hand-contact constraints, ray-traced optics and caustics, CAD mechanical assembly, a rigorously projected impossible staircase, and multiple-seed statistical evaluations.

## Artifacts and reproducibility

[images](images/) includes baseline images, variants, selected constructions, and unsuccessful noise output; [data](data/) includes prompts, seeds, timings, structural metadata, evaluations and SHA256 hashes; [scripts](scripts/) contains executed Python code. Model weights are excluded, and external dependencies must be installed. [tests](tests/) can verify file existence and metadata invariants, not aesthetics or perceptual illusion validity.
