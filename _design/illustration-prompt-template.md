# Aventario Illustration — Locked Prompt Template

Use this exact template for every Higgsfield call so the visual system stays coherent. Replace `{SCENE}` with the scene description and pick `{ACCENT_HEX}` from the locked accent palette.

---

## Template (paste verbatim into higgsfield prompt)

> Editorial hand-drawn flat illustration in the style of Tom Froese / Inwook Choi / Olimpia Zagnoli. {SCENE}. Single abstracted human figure(s) with no facial detail beyond a minimal nose mark and dot eyes; expressive theatrical body language; thick wobbly black outline with variable line weight (heavier on shadow side, thinner on inner detail). One soft flat color block sitting BEHIND the figure as a halo / burst / canopy shape, in `{ACCENT_HEX}`. No gradients, no shading inside the color block, no perspective tricks. Small ornamental flourishes around the figure — squiggles, dotted motion lines, leaf shapes — but never overlapping the figure. Warm cream background `#F5EFE0`. Square 1:1 framing. Editorial cartoon, NOT vector-perfect SaaS-icon style, NOT 3D, NOT photoreal. Composition centred, balanced, with breathing room on all sides.

## Accent palette (pick ONE per illustration)

| Token | Hex | Use when scene is… |
|---|---|---|
| Dusty blue | `#A8B9C8` | Conversational / contemplative / "weather the storm" |
| Butter yellow | `#F0D58B` | Bright moment / discovery / celebration |
| Peach | `#F4B89B` | Warmth / handover / human touch |
| Mint | `#A6CFB4` | Growth / team / partnership |
| Dusty pink | `#E8A8B8` | Care / listening / heart |
| Warm clay | `#B89E84` | Confidence / standing tall / steady |

## CLI invocation (Higgsfield)

```bash
higgsfield product-photoshoot create \
  --mode product_shot \
  --aspect_ratio 1:1 \
  --count 1 \
  --prompt "{full template above with {SCENE} + {ACCENT_HEX} filled in}"
```

`product_shot` mode is used (not generic image gen) so the backend prompt enhancer applies its editorial photography vocabulary, but the prompt itself forces it into illustration mode via "editorial hand-drawn flat illustration" lead.

## Post-process (always)

1. Download PNG.
2. Run through PIL: convert to RGBA, optionally remove the cream background if you need a transparent illustration on a different surface (`rembg` or Higgsfield's transparent-bg toggle if available).
3. Optimise to web JPG at q88 for cream-bg use OR PNG with transparency.
4. Save to `images/illustrations/v2/<scene-slug>.png`.

## Workflow rule

**Never write a freehand prompt** for a new illustration. Always paste this template and only fill in `{SCENE}` and `{ACCENT_HEX}`. That's what keeps the set looking like a set.
