# Aventario — Illustration Style Spec & Use-Case Plan

Reference: the 6-piece editorial set the user shared (umbrella in rain / lifting up / high-five / hugging money bag / heart-hugger / confident stance).

---

## 1. Reverse-engineered style spec

Use this exact spec for every new illustration so the set stays coherent.

### Visual DNA

| Property | Value |
|---|---|
| **Line** | Hand-drawn black outline, variable line weight (thicker on shadows + ground contact, thinner on inner detail). NOT vector-perfect; slight wobble is the point. |
| **Background** | Warm cream `#F5EFE0` (close to brand `#FAFAF7` but slightly more yellow). |
| **Color blocks** | Exactly ONE soft-color accent per illustration, sitting BEHIND the figure as a flat shape (a halo / burst / umbrella / heart / etc.). No gradients, no shading. |
| **Accent palette** | Pick one per piece from: dusty blue `#A8B9C8`, butter yellow `#F0D58B`, peach `#F4B89B`, mint `#A6CFB4`, dusty pink `#E8A8B8`, warm clay `#B89E84`. Tied loosely to brand accent colors (seafoam, orange, magenta) but with the chalk/pastel softness of the reference. |
| **Figures** | Abstracted, no facial features beyond minimal nose/eye marks. Simple body silhouettes. Hands and feet are slightly exaggerated. |
| **Pose** | Expressive, almost theatrical. Body language carries 80% of the meaning. |
| **Ornaments** | Small flourishes — squiggles, dotted lines, leaf shapes, motion lines — added around the figure, not over it. |
| **Aspect** | Square (1:1) for cards/icons; tall (3:4) for section spotlights. |

### Reference artists (style cousins)

- Tom Froese (editorial cartoonist, organic line + flat color)
- Inwook Choi (Korean editorial, simplified figures + soft palette)
- Olimpia Zagnoli (graphic minimalism + warm tones)
- Some Pentagram editorial work
- *Not* the Notion / Stripe vector school — too clean, too geometric

### Reusable prompt template

Saved separately at `_design/illustration-prompt-template.md` (below). Substitute the `{SCENE}` token for each new illustration; everything else stays fixed.

---

## 2. Use-case map — where they land

12 concrete placements across the site, each tied to a specific scene that earns the illustration. I picked scenes that pay off the *exact* meaning of the section they sit next to.

### Landing page (`index.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **L1** | Our Services intro | Person standing on a small ladder placing 6 puzzle pieces into a wall (one piece in mid-air). Mint accent. | "Six core services. One platform." — assembled-together feel. |
| **L2** | As a Service explainer | Two figures handing off a glowing torch on a path; the second one steps forward holding it. Peach accent. | "We support your initiatives from initial spark through to turnkey." Spark + handover. |
| **L3** | References intro | Three figures stacked on each other's shoulders to reach a top shelf with a row of small trophy/folder icons. Butter yellow accent. | "Real results from real engagements" — getting things off the high shelf. |
| **L4** | CTA — Book a meeting | Two people across a table mid-handshake, with a small calendar/clock icon between them. Dusty blue accent. | "30 minutes. Real answers." Conversational. |

### About page (`about.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **A1** | Hero (small accent above headline) | A roped pair walking up a slope; the front figure looks back and offers a hand. Mint accent. | "Partners for mutual success." |
| **A2** | Founder quote backdrop accent | A figure sitting cross-legged with a lit lantern in their lap, illuminating a small map. Butter yellow accent. | "Having the right expertise" — quiet expertise. |
| **A3a–A3f** | Our Values — 6 cards | Each value gets its own bespoke mini-illustration (replaces the current Phosphor icons). See full list below. | Values become memorable, not generic. |
| **A4a–A4d** | People values — 4 cards (Speed / Hands-on / Structure / Measurable Impact) | Each gets a bespoke mini-illustration. | Same logic. |
| **A5** | Why this way — over photo | Skip — keep the photo clean. | Don't compete with the mountain. |

### Impact page (`impact.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **I1** | Empty state (when filters return nothing) | A figure shrugging with an open empty file folder; a small "?" floats nearby. Dusty blue accent. | Soft no-results feedback. |

### Resources page (`resources.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **R1** | Newsletter signup section | A figure sliding a folded letter into a mailbox; small leaves around. Mint accent. | Tactile mail-not-spam feel. |
| **R2** | "Want a topic written up?" CTA | A figure at a small desk with a typewriter and a coffee cup, looking up with a small lightbulb above. Butter yellow accent. | Editorial / writer-at-work tone. |

### Contact page (`contact.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **C1** | Form sidebar / above form | A figure waving with the other hand cupped to their ear (listening). Dusty pink accent. | "We're listening — tell us where to land." |

### Blog page (`blog.html`)

| # | Section | Scene | Why |
|---|---|---|---|
| **B1** | Empty state (when filters return nothing) | Same shrugging figure as I1 (consistency). | Reuse — efficient + on-brand. |

### Per-card mini-illustrations (the deeper set)

These are the bigger investment but pay back the hardest — they replace generic icons with on-brand visual storytelling.

**Our Values (about §3) — 6 illustrations:**

| Value | Scene |
|---|---|
| Authentic relationships built on trust | Two figures shaking hands; soft halo behind. |
| Pragmatism — listen, simplify, deliver | A figure cutting a tangled rope with scissors; a clean coiled rope below. |
| Service excellence, tailored to you | A figure measuring fabric with a measuring tape against a mannequin form. |
| Accountability — we keep our word | A figure holding up a folded contract with a wax seal. |
| Empowering collaboration | Two figures with hands stacked in the middle (huddle/team-in). |
| Curiosity. Growth. Innovation. | A figure tending a small plant on a windowsill; tiny new leaf sprouting. |

**People values (about §4) — 4 illustrations:**

| Value | Scene |
|---|---|
| Speed | Figure running mid-stride with a paper airplane trailing motion lines. |
| Hands-on | Two hands rolling up a sleeve — gesture only, no full body. |
| Structure | Figure stacking three building blocks into a small tower. |
| Measurable impact | Figure pointing at a wall chart with a single upward-trending line and one big circled dot. |

---

## 3. What I'd recommend generating FIRST

To prove the style and the workflow before committing to 20+ illustrations, generate the small **starter set of 4** that have the highest visual leverage and are reusable:

1. **L4 — Handshake across a table** (CTA on landing — high-visibility, sets tone)
2. **A1 — Roped pair, hand offered back** (About hero accent — brand metaphor anchor)
3. **R1 — Letter into mailbox** (Newsletter — clean test of the style on a small object scene)
4. **I1 — Shrugging figure with empty folder** (Empty state — reusable across blog + impact)

Once the user approves these 4, generate the bigger sets (Our Values × 6, People values × 4) in a batch with the locked-in spec.

---

## 4. Locked prompt template

See `_design/illustration-prompt-template.md`.
