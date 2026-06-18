# QC Agent 2: Punctuation Audit

**Scope:** `src/paper.docx` and `src/slides.pptx`
**Method:** Walked every paragraph in the docx (body and tables) and every shape, table cell, and speaker-notes paragraph in the pptx using python-docx and python-pptx. Scanned for em dashes (U+2014), en dashes (U+2013), excessive hyphens, smart vs straight quote drift, double spaces after periods, trailing whitespace, ellipses, semicolons that glue thoughts, parenthetical citation drift, and unbalanced quotes.

---

## 1. Em Dashes (U+2014) — MUST BE ELIMINATED

All nine em dashes live in the slide deck. The paper is clean. Every one of these is doing the job of a colon and should be replaced with a colon, or split into two lines.

### Slide 9 — Bass leadership categories

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [1]
- **Original:** `Idealized Influence — Role modeling`
- **Fix:** `Idealized Influence: role modeling`
- **Em-dash offset:** 20

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [2]
- **Original:** `Inspirational Motivation — Shared vision`
- **Fix:** `Inspirational Motivation: shared vision`
- **Em-dash offset:** 25

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [3]
- **Original:** `Intellectual Stimulation — Challenging employees to grow`
- **Fix:** `Intellectual Stimulation: challenging employees to grow`
- **Em-dash offset:** 25

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [4]
- **Original:** `Individualized Consideration — Personal development`
- **Fix:** `Individualized Consideration: personal development`
- **Em-dash offset:** 29

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [6]
- **Original:** `Contingent Reward — Pay for performance`
- **Fix:** `Contingent Reward: pay for performance`
- **Em-dash offset:** 18

- **Location:** slide [9], shape [1] 'Content Placeholder 2', para [7]
- **Original:** `Management by Exception — Intervene only when problems arise`
- **Fix:** `Management by Exception: intervene only when problems arise`
- **Em-dash offset:** 24

### Slide 10 — Comparison row

- **Location:** slide [10], shape [1] 'Content Placeholder 2', para [0]
- **Original:** `CFA — Transformational`
- **Fix:** `CFA: transformational`
- **Em-dash offset:** 4

- **Location:** slide [10], shape [2] 'Content Placeholder 3', para [0]
- **Original:** `Popeyes — Transactional`
- **Fix:** `Popeyes: transactional`
- **Em-dash offset:** 8

### Slide 14 — Closing line

- **Location:** slide [14], shape [1] 'Content Placeholder 2', para [0]
- **Original:** `Employee success is not about the product — it is about how organizations invest in their people`
- **Fix:** `Employee success is not about the product. It is about how organizations invest in their people.`
- **Em-dash offset:** 42

---

## 2. En Dashes (U+2013)

None found in either file. No action.

---

## 3. Excessive Hyphens

The scanner flagged 34 multi-hyphen tokens. After review, every single one is a legitimate proper noun or standard compound:

- `Chick-fil-A` (29 instances across paper and deck) — brand name, correct as is
- `Day-to-day` (paper para 9 offset 326, slide 4 shape 1 para 4) — standard compound, correct
- `employee-to-customer` (paper para 13 offset 296) — standard compound, correct
- `taken-for-granted` (slide 7 shape 1 para 5) — standard compound, correct
- `chick-fil-a` in URL (paper para 42) — correct domain casing

No fixes required.

---

## 4. Smart vs Straight Quote Consistency

No mixing detected within any single paragraph. The paper uses smart quotes (U+201C / U+201D and U+2018 / U+2019) consistently. The deck uses straight quotes (`"` and `'`) consistently within each shape.

**Cross-document drift to flag for Agent 3 or content owner:** the paper uses curly typographic quotes while the deck uses straight ASCII quotes. Pick one and apply across both deliverables. Recommend straight quotes in the deck and curly in the paper as is, since that is the conventional split for body prose vs slide projection.

No unbalanced quote pairs found.

---

## 5. Double Spaces After Periods

None found.

---

## 6. Trailing Whitespace

None found on any non-empty paragraph.

---

## 7. Ellipses

No ellipsis character (U+2026) and no `...` runs of three or more dots. No action.

---

## 8. Semicolons Gluing Two Thoughts

Zero semicolons in either document. No AI tell here. Clean.

---

## 9. Parenthetical Citation Formatting

Spot-checked all in-text citations. They follow APA `(Author, Year)` format consistently.

One scanner hit, paper para [12] offset 474: `(ACSI, 2023)`. This is correctly formatted and was only logged because the regex captures every match. No drift, no missing periods inside the parens, comma placement consistent across the paper.

No fixes required.

---

## 10. Unbalanced Quote Marks

None.

---

## Totals

| Issue category | Count |
|---|---|
| Em dashes (must fix) | **9** |
| En dashes | 0 |
| Excessive hyphens (real issues) | 0 |
| Excessive hyphens (false positives, proper nouns) | 34 |
| Smart vs straight quote mixing within paragraph | 0 |
| Double spaces after periods | 0 |
| Trailing whitespace | 0 |
| Ellipsis characters | 0 |
| `...` ellipsis runs | 0 |
| Semicolons | 0 |
| Citation format drift | 0 |
| Unbalanced quote marks | 0 |
| **Total actionable issues** | **9** |

All nine issues sit in `slides.pptx` on slides 9, 10, and 14. The paper is punctuation-clean.
