# Illustration iteration log

## L4 — Handshake across a table (CTA on landing)

Generated 3 variants, validated v2 as the baseline.

| Variant | Model | Verdict |
|---|---|---|
| v1 | flux_2 | Figures too detailed — full mouths, ears, hair, eyebrows. Color block was jagged starburst. Off-brand. |
| **v2** | **flux_2** | **VALIDATED.** Bald oval heads, just dot eyes + nose mark, simple shirts. Smooth organic dusty-blue blob halo. Leaf flourishes. Cream bg. Hand-drawn wobbly line. Matches the reference set's archetype (compare to high-five / heart-hugger / money-bag-hugger pieces). |
| v3 | flux_2 | Same prompt direction as v2, slightly more rendered/3D feeling on the figures. v2 is flatter and more on-brand. |

### Validated prompt (use this exact template for every future illustration)

> Hand-drawn editorial cartoon spot illustration, New Yorker magazine style, by Tom Froese or Inwook Choi. {SCENE}. The figure(s) have bald oval heads, two tiny black dot eyes, a minimal single nose line, NO mouth, NO ears, NO eyebrows, NO hair. Wobbly hand-drawn imperfect BLACK ink outline with variable line weight — heavier on the outer silhouette and shadow side, thinner on the inner details. Behind the figure(s) floats ONE soft solid flat color shape forming a smooth organic blob halo in {ACCENT_HEX} — wavy soft edges, no spikes. Warm cream background color #F5EFE0. Small ornamental flourishes — two tiny black squiggle marks and one small leaf shape — placed around the figure(s) with empty space, never overlapping them. NO gradients, NO shading inside shapes, NO 3D, NO photorealism, NO digital perfection. Square 1:1 frame, centered composition, generous breathing room. The artwork must look like it was hand-drawn with ink and brush on textured paper, printed in a magazine.

### Locked CLI invocation

```bash
higgsfield generate create flux_2 \
  --prompt "{full template above with {SCENE} + {ACCENT_HEX} filled in}" \
  --aspect_ratio 1:1 \
  --wait
```

## Process learnings

- **NEVER mention** "bare", "topless", "no clothes", or even "no mouth/ears" without explicit clothing details — GPT Image 2 flags this as NSFW.
- **Always include explicit clothing** ("plain off-white shirts") so the figures look clothed even when stylised.
- **Flux 2 > GPT Image 2** for this hand-drawn editorial style. GPT Image 2 leans too photorealistic and NSFW-flags artistic abstraction.
- The "behind" word for the halo is important — without it, Flux puts the color block in front of the figure.
- "Smooth organic blob, wavy soft edges, no spikes" — without this, Flux defaults to jagged starburst shapes.

## Starter set of 4 — Aventario-tinted palette

User approved the handshake style + asked for "a little bit of Aventario colors" — moved the palette from generic pastels to brand-derived pastels (each tinted from one of the 4 brand colours).

| ID | Scene | File | Accent | Brand tie |
|---|---|---|---|---|
| L4 | Handshake across a table | `handshake-VALIDATED.png` | `#A8B9C8` dusty blue | navy `#334b60` desaturated |
| A1 | Roped pair, hand offered back | `A1-roped-pair-v1.png` | `#B5D8CF` soft seafoam | seafoam `#88C9BE` desaturated |
| R1 | Letter into mailbox | `R1-mailbox-v1.png` | `#F4C99B` soft orange | orange `#f19a51` desaturated |
| I1 | Shrugging figure with empty folder | `I1-shrugger-v1.png` | `#E8AAC8` soft magenta | magenta `#d15298` desaturated |

All four use the validated Flux 2 prompt template (above), only `{SCENE}` and `{ACCENT_HEX}` swapped. Set reads as a coherent series with brand variety.

## Next up (pending user approval of the starter set)

Once the user signs off:
1. Wire each starter into its target page (CTA / About hero / Resources newsletter / empty state)
2. Scale to the full 12-illustration map per `_design/illustration-spec.md`:
   - 6 Our Values mini-illustrations
   - 4 People values mini-illustrations
   - Remaining placements (As-a-Service handover, References stacked-team, founder backdrop accent, Contact listening, Resources writer's desk)
