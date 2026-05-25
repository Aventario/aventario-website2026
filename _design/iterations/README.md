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

## Next up (pending user approval of handshake-VALIDATED.png)

Generate the rest of the starter set of 4 (per `_design/illustration-spec.md` §3):

1. ✅ L4 — Handshake across a table — VALIDATED
2. ⏳ A1 — Roped pair, hand offered back (mint accent #A6CFB4)
3. ⏳ R1 — Letter into mailbox (mint accent #A6CFB4)
4. ⏳ I1 — Shrugging figure with empty folder (dusty blue accent #A8B9C8)
