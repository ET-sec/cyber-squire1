# Round 2 QC: Slides Visual Audit

**File:** `/Users/et/cyber-squire-ops/CoreDirective/school/MGS3400-team-project/qc/draft/slides.pptx`
**Method:** python-pptx programmatic inspection + LibreOffice PDF render to PNG, visual review of all 15 slides.
**Date:** 2026-04-19

---

## Round 1 Issue Verification (Global)

| R1 Issue | Status | Notes |
|---|---|---|
| 9 em dashes | FIXED | 0 em dashes, 0 en dashes across all body text and notes. |
| Title sizes too small | FIXED (mostly) | Range 30-54pt. Slide 11 is 30pt (one below 32pt floor). |
| Body too small | FIXED | Body 15-18pt, comparison body 15pt. Acceptable. |
| Zero speaker notes | FIXED | All 15 slides have substantive notes (290-584 chars), real content not placeholder. |
| Color semantic conflict on framework slides | FIXED | Slides 7, 9, 11 now use neutral grays/navy (gray, slate, navy). No red/orange on framework slides. |
| Density walls | FIXED | Slides 3, 4 have 4 bullets at 18pt with breathing room. Comparison slides cleaner. |
| Title height inconsistency S3 vs S4 | FIXED | All content slides now at H=0.9" uniformly (S2-S15). |
| Agenda mismatch | FIXED | Agenda 7 items map cleanly to deck section structure. |
| References at 12pt | FIXED | Now 14pt. |
| Bold inflation on S8, 10, 12 | FIXED | Only section labels (Artifacts/Hygiene/Motivators) and header bars are bold. Body text not bolded. |
| S13 satisfaction box header smaller | FIXED | All three boxes use 22pt bold white headers (Culture/Leadership/Satisfaction). |
| S14 buried punchline | FIXED | Bottom-line "people-management gap, not a product gap" is now a 24pt italic white hero band on navy. |

---

## Per-Slide Findings

### Slide 1 — Title
- FIXED: 54pt title, 28pt subtitle, large quiet hierarchy.
- ISSUE: "Team members: [Add names here]" placeholder still in deck. Must be filled in before delivery.
- MINOR: Top red+orange band repeats brand colors of both companies, which is a nice frame but worth noting it doubles down on the same colors used for semantic comparison later. Not a defect.

### Slide 2 — Agenda
- FIXED: 40pt title, 20pt items, time budgets right-aligned.
- FIXED: Section labels match the deck flow (companies, success, three components, connect, takeaways).
- CLEAN. No issues.

### Slide 3 — Chick-fil-A overview
- FIXED: 40pt red title, 18pt body, 4 bullets fit comfortably.
- FIXED: Title height matches Slide 4 (both H=0.9).
- ISSUE: Bullet glyph is ASCII bullet (•) not pptx native bullet. Renders fine but lines do not have hanging indent — wrapped lines start at the left margin instead of indenting under the first character of text. Minor, readable.

### Slide 4 — Popeyes overview
- FIXED: 40pt orange title, 18pt body, 4 bullets, parallel structure with Slide 3.
- Same minor bullet hanging-indent issue as Slide 3.

### Slide 5 — How We Define Success
- FIXED: 40pt title, three columns with header bars (Customer Satisfaction, Hourly Turnover, Observed Engagement).
- FIXED: Source captions present at 12pt under each header. Worth bumping these to 14pt for consistency with references slide standard, but they are intentionally subordinate so 12pt is defensible.
- ISSUE: Observed Engagement column has only 2 rows (Chick-fil-A and Popeyes) while the other two columns have 3 rows (CFA, industry avg, Popeyes). The middle "industry avg" row is missing on column 3, leaving a visible vertical gap between the red and orange entries. Either add a neutral middle row ("Industry: mixed") or shift both entries up to close the gap.

### Slide 6 — Three Components framework
- FIXED: 36pt title, three navy boxes with white labels.
- ISSUE: Subtitle text inside boxes uses awkward two-line layout — "Schein (1985)" on line 1 then "Three Levels of Culture" on line 2, with the second line center-aligned independently. Looks slightly off-center because of the soft-break behavior. Same on all three boxes.
- MINOR: Box headers (Organizational Culture, Leadership, Job Satisfaction) sit ~25% from box top, leaving large empty space above. Could vertically center for tighter feel.

### Slide 7 — Schein's Three Levels (framework)
- FIXED: Title 32pt (at the floor of acceptable range, but still readable).
- FIXED: Color semantic conflict resolved — uses three neutral gray/slate/navy bars (no red/orange).
- CLEAN. Nice gradient from light gray to dark navy reinforces the iceberg concept (surface to depth).

### Slide 8 — Culture Comparison
- FIXED: 36pt title, two columns, label colors red/orange match brand assignment.
- FIXED: Bold inflation gone — only section labels (Artifacts/Espoused Values/Basic Assumptions) and column header bars are bold. Body 15pt regular.
- CLEAN.

### Slide 9 — Leadership framework
- FIXED: Title 32pt.
- FIXED: Two neutral header bars (navy + gray). No red/orange on framework slide.
- CLEAN.

### Slide 10 — Leadership Comparison
- FIXED: 36pt title, red/orange brand colors on header bars (correct semantic use here on comparison slide).
- FIXED: Bold gone from body bullets. Body 15pt regular.
- CLEAN.

### Slide 11 — Herzberg framework
- ISSUE: Title is 30pt — 2pt below the 32-44pt target floor. Title text is long ("Job Satisfaction: Herzberg's Two-Factor Theory (1959)") so 32pt would still fit. Bump to 32pt to comply with the rule.
- FIXED: Two neutral header bars (gray Hygiene + navy Motivators). No red/orange on framework slide.
- CLEAN otherwise.

### Slide 12 — Job Satisfaction Comparison
- FIXED: 36pt title, red/orange brand on column headers.
- FIXED: Section labels (Hygiene/Motivators) bold in brand colors. Body 15pt regular.
- CLEAN.

### Slide 13 — How the Three Components Connect
- FIXED: All three top-row box headers (Culture/Leadership/Satisfaction) at 22pt bold white. Equal sizing.
- FIXED: Bottom synthesis bands have brand-color labels (Chick-fil-A red, Popeyes orange) at 16pt bold with arrow-flow body at 15pt white.
- ISSUE: Subtitle text inside the three top boxes uses the same awkward two-line center-align as Slide 6 — "Schein" on line 1, "Sets the environment" indented/right-shifted on line 2. Looks like a manual line break inside an otherwise center-aligned paragraph.
- MINOR: The right arrows between boxes are small (0.5x0.4) and could use more visual weight.

### Slide 14 — Takeaways
- FIXED: Bottom-line punchline now hero element — 24pt italic white "The performance gap between these chains is a people-management gap, not a product gap" inside a 1.6"-tall navy band at the bottom. Strong.
- FIXED: 40pt title, three numbered red ovals, takeaway text at 18pt regular.
- ISSUE: The "Bottom line" label inside the navy band is 16pt orange. It is centered above the punchline but feels like a tiny caption above a much larger hero quote — visually disconnected. Consider 14pt uppercase tracking, or remove the label entirely and let the quote speak.
- MINOR: Numbered oval list has tight vertical rhythm (rows at 2.0, 2.95, 3.9). Consider increasing row gap by 0.05" for a calmer feel.

### Slide 15 — References
- FIXED: References at 14pt (was 12pt). Readable from second-row classroom.
- FIXED: 36pt title.
- CLEAN. APA formatting consistent. URLs intact.

---

## New Issues Found in Round 2

1. **Slide 11 title at 30pt** — below the 32pt target floor. Single-point fix.
2. **Slide 1 placeholder text** — `[Add names here]` must be filled in before delivery.
3. **Slide 5 Column 3 row imbalance** — Observed Engagement has 2 rows while Customer Satisfaction and Hourly Turnover have 3. Visible vertical gap.
4. **Slide 6 and 13 subtitle two-line break** — manual line break inside center-aligned paragraph creates awkward indent. Either remove the break (let it wrap naturally) or use a single-paragraph layout.
5. **Slides 3, 4, 9, 10, 11 ASCII bullets** — bullet glyph (•) is part of the text run instead of native pptx bullet, so wrapped lines do not hang-indent. Readable but typographically loose.
6. **Slide 14 "Bottom line" label** — feels orphaned above the hero quote. Consider tighter caption treatment or removal.

---

## Color Contrast Check
- All white text on navy/red/orange/gray backgrounds passes WCAG AA at the sizes used.
- Body text 222222 on white background: high contrast, fine.
- Subtitle gray 555555 on white: passes for 18pt+ regular text.
- 12pt source captions on Slide 5 in 555555 gray: borderline — survives because they are paired with stronger anchor headers.

## Speaker Notes Quality
- All 15 slides have notes (290-584 chars).
- Notes are real content — key points, transitions, hand-offs to teammates, source attribution, time budgets.
- Notes contain useful "land this point" cues (e.g., S11 "you cannot skip the first to get to the second", S13 "the three components compound on each other").
- No placeholder notes anywhere.

## Overflow Check
- No text extends past shape boundaries on any of the 15 rendered PNGs.
- Comparison columns use enough horizontal width to wrap cleanly.
- No clipped headers or truncated bullets.

## Alignment Check
- Title underline accent (red bar at 0.75 left) consistent across all content slides.
- Comparison columns use mirrored 0.5/6.75 left positions, equal 6.0 widths.
- Slide 5 column header bars sit at three matched positions (0.45, 4.6, 8.75) with equal 4.0 widths.

---

## Overall Verdict

**PASS with 6 minor cleanups.**

All 12 Round 1 issues are addressed. The deck is now presentation-ready in structure, hierarchy, color discipline, and speaker notes. Six remaining issues are cosmetic polish (one font-size bump, one placeholder fill, one column row imbalance, two text-wrap breaks, one bullet typography note, one caption treatment). None are blockers.

Recommended fix order:
1. Slide 1 — fill in team names (BLOCKER for delivery).
2. Slide 11 — bump title from 30pt to 32pt.
3. Slide 5 — balance Observed Engagement column to 3 rows.
4. Slide 6 / Slide 13 — fix the manual line break in box subtitles.
5. Slides 3, 4, 9, 10, 11 — convert ASCII bullets to native pptx bullets if time permits.
6. Slide 14 — tighten or remove the "Bottom line" caption.
