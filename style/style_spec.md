# Share the Shares: style spec

The look is defined by C1 (`renders/c1/c1_sheet.jpg`). Values live in `config/look.json`, `config/engravings.json` and `config/seeds.json`; this file explains them. There are no inspiration videos. The references are public-domain certificate and banknote art, listed in `assets/engravings/sources.tsv` (used) and `reference/certificates/sources.tsv` (layout and palette only).

## The look in one line

A real two-colour engraved certificate of about 1870, printed on cream paper and lying on a desk under a document camera. Its figures are Durand's own engravings, cut loose as paper puppets.

## Format and frame rate

- **24 fps, animated on twos** (`fps`, `animation_on`): each pose holds two frames, as the brief's "paper puppets on twos" asks. Camera moves run on ones, so pushes stay smooth while the figures step.
- 16:9 main video; the 9:16 cut and the final resolution come from the shot list and `config/render_profiles.json`. The live shots should be filmed at 24 fps (23.976 is fine: the offsets are fixed).

## The sheet

- **Size:** US letter, landscape (11 × 8.5 in), 4400 × 3400 px at 400 dpi. The printed prop and the render share one layout (`layout.json`), so the corner denominations are in the same place on both, and the track and the composite line up.
- **Layout** (brief, "The world"):
  - top: Progress's vignette, flanked by the cherub choir;
  - the company name, AMALGAMATED BENEFIT, LLC, on a green underprint panel;
  - the body text and the "This Certifies that" line;
  - corners: four "5" counters;
  - right: the number-of-shares box, and Prudence below it;
  - left: the certificate number, Mercury in the fine print, and the laborer in the lower corner;
  - bottom: President, Secretary and a blank Recipient line;
  - the numbered stub on the left, behind a perforation;
  - seven coupons along the bottom, with the pledge number along the edge.
- **Two sheets per version:** `sheet.png` (the prop: figures printed at rest) and `static/` (no figures, for renders, where each figure is its own layer).

## Palette (`palette`)

| Role | Hex | Use |
| --- | --- | --- |
| Paper | `#EEE5CC` | Cream stock. The paper grain (seed `paper_grain` 41) varies it by about 2% |
| Green ink | `#2F5E4C` | The green plate: border bands, guilloche, counters, coupon panels, the underprint |
| Sepia ink | `#3E2C1E` | The sepia plate: vignettes, figures, type, rules, perforations |
| Gold ink | `#A8843A` | Reserved for S36: the key change re-inks the sheet, gold creeping into the green |
| Desk | `#2B211A` → `#5A4535` | Dark wood under the sheet |

Inks multiply into the paper, as on the press (`certificate.py`, `print_sheet`). In renders a figure layer composites over the paper, so its ink colour is pre-multiplied by the paper colour and the two methods agree. The live composite uses the same multiply (brief, "Tracking and compositing").

## Type (`fonts`, all OFL, `assets/fonts/`)

| Role | Font | Where |
| --- | --- | --- |
| Display | Abril Fatface | Company name, counters, certificate number, coupon values: the fat-face Didone of mid-century bank notes |
| Small caps | IM Fell English SC | Labels (NUMBER OF SHARES, PRESIDENT…), letter-spaced as engravers set them |
| Body | IM Fell English, roman and italic | The boilerplate, "is the owner of" |
| Script | Pinyon Script | "This Certifies that" |

The brief's title card, SHARE THE SHARES in engraved capitals, and the fact card ("in the same engraved type") use the display face and the small caps.

## Ornament: generated, not copied

The border bands, coupon panels, underprint and counter rosettes are drawn in code from sums of sine waves along a path (`guilloche_band`, `rosette`), as a geometric lathe cut them. Cyrus Durand's lathe work (Met 393954–393991) is the reference for density and line weight; no lathe piece is copied. This is also how S11's gag gets built: the guilloche resolves into LLC LLC LLC. It has a real precedent, Met 393986, a lathe rosette made from the repeated words "Five thousand".

## Engravings: the cast

Every figure comes from one engraver's banknote vignettes, Asher Brown Durand (ca. 1824–37, Met Open Access, public domain). So the hatching, stipple and line weight match across the cast.

| Figure | Source | Piece |
| --- | --- | --- |
| Progress (the Founder) | 393940, Allegory of America | `progress` |
| Prudence (the Board) | 393946, Liberty and Justice: the seated Justice, with sword and scales | `prudence` |
| Mercury (the Lawyer) | 393925: the flying putto with winged helmet and caduceus | `mercury` |
| The cherub choir | 393931: three putti | `cherubs` (mirrored for the right side) |
| The engraved laborer | 393945, a blacksmith and forge | `laborer` |

`scripts/ink_extract.py` turns each scan into a clean ink map. It divides out the paper level, which removes the foxing, stains and paper tone, then remaps the levels and applies the vignette's feathered oval. So every piece prints in the certificate's own ink on its own paper.

**Known gaps, for the puppet build after C1:**
- Progress holds a spear, not the brief's torch. The torch is a separate prop piece that replaces the spear when the puppet is cut.
- Progress's shield carries stars and stripes; it's an allegory of America, not a logo, but it reads as American. It can be masked if that's unwanted.
- The laborer's hammer rests against the anvil block. S07 ("hammer raised") and S29's match cut ("the engraved laborer's raised hammer") need either another laborer source or new wording. He never moves, so the shot must take him as engraved.

## Paper and light

- **Paper:** matte (roughness 0.82). The ink stands slightly proud of the paper (intaglio), shown as a fine bump from the plates. The sheet curls slightly at its edges, the long edges more (`curl`).
- **Light:** a document camera's soft overhead box (`light.key_w` 6.5) plus a low warm fill from the room (`fill_w` 1.3). It's calibrated so the paper renders at about its printed colour in the **Standard** view transform, not AgX: the inks should read as the printed colours.

## Camera

A document camera (brief, "Motion"): slow pushes, pans and flips, never handheld. The wide frame is 40 mm from about 45 cm, looking down at a slight angle (S02's push). Close-ups are 60 mm at about 12 cm, at f/16, so the engraving stays sharp across the vignette (S07). Detail holds in close-ups because each figure layer keeps its source resolution: the laborer is 2177 px across, against about 500 px on the print.

## Motion (for C4 onward; not in C1)

- Hinged paper-puppet limbs and jaws on twos. Each figure is cut at its joints with round overlaps, as in Victorian-engraving cutout animation, and any hidden area is filled by the agent (inpainting from the surrounding hatching), never redrawn by hand.
- The hatching "boils" slightly: a small per-hold displacement of the ink map, reseeded every two frames.
- Flips (S24) turn the sheet over to the transfer form on its back.

## C1 outcome

Pending review. In C1: the sheet, its sources, the look config and two test frames. Not in C1: the puppet cuts, the torch, the transfer form on the back, the seal (it stamps down in S34), the animation, and the live-shot composite.
