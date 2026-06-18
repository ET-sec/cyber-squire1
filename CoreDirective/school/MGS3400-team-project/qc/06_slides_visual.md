# QC Report 06 — Visual Layout, Formatting, and Design Audit

**File audited:** `src/slides.pptx`
**Tool:** python-pptx (programmatic inspection)
**Auditor scope:** dimensions, layout, fonts, colors, hierarchy, density, narrative flow

## Deck-level findings

- Dimensions: 13.33 in x 7.50 in. Aspect ratio 1.7778. Confirmed 16:9 widescreen. Correct.
- Total slide count: 15. For a 15 minute talk that yields about 60 seconds per slide, which is workable but tight. Two of those slides (title + references) carry no narrative content, so the team has 13 slides to fill 15 minutes. Realistic.
- Speaker notes: ZERO across all 15 slides. This is a deck-wide gap. Every slide should carry presenter notes for rehearsal, handoff between teammates, and graders who read the file outside the live talk.
- Font family: only `Calibri` is explicitly set on the title slide. Every other slide leaves the font name empty, which means it inherits from the master (default Office theme font). Consistent by default, but no intentional typography choice. Acceptable but bland.
- Color palette: red `E51636` (CFA brand), orange `F15A22` (Popeyes brand), darker red `8B1A1A`, green `2E7D32`, red `C62828`, white `FFFFFF`, gray `555555`. The two-brand color logic is consistent and used correctly throughout. Good.
- Title sizes: range from 24pt to 32pt. Below the 36-44pt rule of thumb on most slides. Titles will read as subdued in a classroom projector setting.
- Body sizes: range from 12pt (references) to 18pt. Most body copy sits at 14-16pt, below the 18-28pt rule of thumb. References at 12pt is too small for a projected slide.

## Per-slide findings

**Slide 1 — Chick-fil-A vs. Popeyes / Why Employees Make the Difference**
- **Issue:** Title sized at 32pt with subtitle line at 24pt inside the same Title placeholder. Subtitle placeholder text "MGS 3400 | Organizational Behavior | Team Project" is only 16pt. Title is left-aligned and starts at left=1.26 in, so visual weight pulls hard to the upper-left. Lots of dead space on the right half.
- **Fix:** Bump main title to 44pt, secondary line to 28pt. Either center-align the title or add a brand visual (CFA + Popeyes logos) to balance the right side. Add presenter intro to speaker notes.

**Slide 2 — Agenda**
- **Issue:** Title 28pt is undersized. Five bullet items at 18pt with no numbering, no icons, no visual grouping. Agenda wording does not match actual section titles (see deck-level mismatch below). No notes.
- **Fix:** Number the agenda items 1-5 and align them to the actual deck sections. Bump title to 36pt. Add speaker notes with the time allocation per section (for example: Intros 2 min, Success 1 min, Three Elements 7 min, Takeaways 3 min, Q&A 2 min).

**Slide 3 — Chick-fil-A Overview**
- **Issue:** 74 words of body copy, the densest non-reference slide in the deck. Six bullets at 16pt. Last bullet is the full mission statement quoted in plain text, no quote styling. Title color `E51636` (red) only applied here (and not on Popeyes slide), so brand-color treatment is inconsistent between the two intros.
- **Fix:** Cut to 4 bullets max. Move the mission quote to a styled callout box (italic, indented, smaller). Apply title color `F15A22` to slide 4 to mirror the brand-color treatment, OR remove from slide 3 for parity.

**Slide 4 — Popeyes Overview**
- **Issue:** Title placeholder is 1.43 in tall (slide 3 title is 0.77 in tall), so the title box is roughly double the height of slide 3. Visual inconsistency between the two parallel intro slides. Body density is also high (47 words, 6 bullets). Last bullet text is truncated in inspection at "...inco..." which suggests it runs long.
- **Fix:** Match the title box height to slide 3 (0.77 in, top 1.06 in). Trim the 2014 turnaround bullet to one line. Apply red/orange title color treatment to match slide 3 styling.

**Slide 5 — How We Define Success**
- **Issue:** 54 words. Three bold bullets each carry full statistics inline. The "Observable Engagement" bullet appears truncated in inspection ("eye contact, teamwork, and..."). Lead-in line is plain text using "NOT" in caps, which is a soft AI-style emphasis pattern.
- **Fix:** Convert the three metrics into a 3-column comparison strip (CFA vs Popeyes side-by-side numbers) instead of bullets. Drop the "NOT" caps emphasis, rephrase as "Success here means employee outcomes, not revenue." Verify the Observable Engagement bullet does not overflow.

**Slide 6 — The Three Elements We Analyzed**
- **Issue:** Three rounded rectangles laid out at left=1.39 / 5.21 / 9.03 with width 3.06 each. Last box's right edge sits at 12.09 in, leaving only 1.24 in of right margin (vs 1.39 in left margin). Slight asymmetry. Three picture icons are positioned at left=2.53 / 6.35 / 10.17 with width 0.78. They sit on top of the rectangles rather than inside a clean composition. Rectangle 3 ("Job Satisfaction") font size is unset while boxes 1 and 2 also have unset sizes; only the bold + white color is set, which means box copy size is theme-default. Caption strip at bottom is only 14pt.
- **Fix:** Reposition boxes to left=1.50 / 5.17 / 8.83 for true symmetric centering. Center icons inside each rectangle vertically (currently sitting at top=2.78, near top of box). Set explicit font size on box titles (24pt bold). Bump caption strip to 18pt.

**Slide 7 — Organizational Culture: Schein's Three Levels (1985)**
- **Issue:** Title at 24pt, drops below the 28pt used on most other slides. The three-level structure uses three different colors (`E51636`, `8B1A1A`, `F15A22`) for the three numbered headers, but the third color is Popeyes orange, which signals "Popeyes" semantically when this slide is purely framework. Confusing color signal.
- **Fix:** Use a single neutral accent color (or a single CFA red) for all three Schein level headers. Reserve the brand red/orange pairing for comparison slides only. Bump title to 28pt.

**Slide 8 — Culture Comparison**
- **Issue:** Two-column compare slide. CFA column body at 14pt, all bullets bold. Popeyes column same. Bold-on-everything kills the bold's emphasis function. 61 total words across both columns, near density limit.
- **Fix:** Make the column headers bold red/orange at 20pt, then make bullet labels (Artifacts, Values, Assumptions) bold at 14pt and the descriptions plain at 14pt. Currently everything is bold.

**Slide 9 — Leadership: Transformational vs. Transactional**
- **Issue:** Single content block holds both leadership styles stacked vertically. Transformational has 4 sub-bullets, Transactional has 2. All bullets are bold. The two style headers use red and orange brand colors, but this slide is the framework explanation, not the comparison. Same color-semantic problem as slide 7.
- **Fix:** Split into two visual columns OR use neutral colors for the framework. Save red/orange contrast for the comparison slide that follows. Reduce bold usage so emphasis means something.

**Slide 10 — Leadership Comparison**
- **Issue:** Clean two-column layout. 63 words total, just over the 30-word density target per slide (though split across two columns it reads as 30ish per side). Body bullets at 14pt are small for projection.
- **Fix:** Bump body to 16pt. Add a one-line summary at the top of each column (for example: CFA "Operators on the floor, not in the office.") to give the audience a takeaway before they read bullets.

**Slide 11 — Job Satisfaction: Herzberg's Two-Factor Theory (1959)**
- **Issue:** Hygiene Factors header uses Popeyes orange `F15A22`, Motivators header uses CFA red `E51636`. Same color-semantic problem: this is the framework slide, not a brand comparison, but the colors imply hygiene = Popeyes and motivators = CFA. The "Key Insight" bullet is truncated in inspection ("You need BOTH...").
- **Fix:** Use neutral colors for Hygiene and Motivators headers (gray + black, or two shades of blue). Verify the Key Insight bullet fits without truncation. Consider rendering the slide as a visual: a horizontal bar with "Dissatisfied" on the left, neutral middle, "Satisfied" on the right, with the two factor groups labeled below.

**Slide 12 — Job Satisfaction Comparison**
- **Issue:** Includes ✓ and ✗ unicode marks with `2E7D32` (green) and `C62828` (red) color treatment. These are the only checkmark/X marks in the deck and may render as boxed glyphs depending on installed fonts on the projection machine. Slight risk.
- **Fix:** Either use shapes (a green circle with check, red circle with X) drawn in PowerPoint instead of unicode glyphs, or test on the actual classroom projector before relying on the symbols.

**Slide 13 — How It All Connects**
- **Issue:** 16 shapes on this slide, the most complex layout in the deck. Boxes positioned left=1.32 / 5.21 / 9.10 with width 2.71. Right edge of last box sits at 11.81 in, vs left margin of 1.32 in, so 0.20 in of asymmetry. Right Arrow shapes at top=2.50 with height 0.28 are flagged by the overflow heuristic; not real overflow, just shapes near their content size. The Satisfaction Box header is 14pt (smaller than the matching Culture and Leadership headers at 16pt) because the "Job Satisfaction (Herzberg)" label is longer and was downsized to fit.
- **Fix:** Shorten the third box label to "Satisfaction (Herzberg)" so it can stay at 16pt to match the other two. Recenter the three top boxes (use left=1.43 / 5.32 / 9.21 to balance the 0.20 in margin). Add 2-3 sentences of speaker notes that walk through the cause-effect chain so the presenter does not just read the boxes.

**Slide 14 — Key Takeaways**
- **Issue:** 72 words, the second densest slide in the deck. Five bullets where the last one is bold and 18pt acting as a closing line ("not about chicken. It is about people."). The closing line is buried at the bottom of a wall of bullets. Buried punchline.
- **Fix:** Cut the four lead-in bullets to 3 max. Promote the closing line to a large centered statement at 32pt, ideally on its own slide or as a hero block on this slide with the bullets shrunk above it.

**Slide 15 — References**
- **Issue:** 12pt body copy, 9 entries. 12pt is too small to read on a projector. References slide is rarely read aloud anyway, but if it is up on screen it should at least be legible.
- **Fix:** Bump to 14pt and accept that one or two entries may move below the fold (acceptable for a closing slide). OR split into two columns at 12pt to use the horizontal space.

## Deck-wide issues

- **Agenda mismatch:** The agenda on slide 2 lists "Company Introductions" (single item) but the deck has two introduction slides (3 and 4). The agenda also says "Theoretical Framework & Comparison" as one item but the deck dedicates 6 slides (7-12) to framework + comparison. Re-word the agenda to: (1) Companies, (2) Defining Success, (3) Culture, (4) Leadership, (5) Job Satisfaction, (6) Synthesis, (7) Takeaways. Or keep 5 items but match them to the deck's actual structure.
- **Color-semantic conflict:** Red and orange are used as both brand colors (CFA = red, Popeyes = orange) AND as accent colors on framework slides (Schein, Herzberg). On framework slides the audience will read the orange section as "this is the Popeyes part" when it isn't. Reserve red/orange strictly for comparison slides; use neutral palette (grays, navy, accent yellow) for framework slides.
- **Bold inflation:** Slides 8, 10, 12 set every bullet to bold. When everything is bold, nothing is. Reserve bold for headers and the single most important phrase per slide.
- **Title-size inconsistency:** Section titles range from 24pt to 32pt. Standardize to 32pt for opening slides, 28pt for content slides.
- **Speaker notes are empty on every slide.** Add at minimum 2-3 sentences per slide so presenters have a script and graders reading the file can follow the narrative without the live talk.

## Summary

- **Total slides:** 15
- **Slides with issues flagged:** 15 of 15 (every slide has at least a notes-missing flag; 9 slides have substantive layout/density issues)
- **Highest priority fixes:**
  1. Add speaker notes to all 15 slides
  2. Fix agenda-to-section mismatch on slide 2
  3. Reduce density on slides 3, 5, 8, 10, 12, 14
  4. Resolve color-semantic conflict on slides 7, 9, 11
  5. Fix title-box height inconsistency between slides 3 and 4
  6. Bump references font from 12pt to 14pt
- **Pacing recommendation for 15 minutes:** Current 15-slide structure is fine. Suggested timing: title 30s, agenda 30s, two intros at 1 min each, success metrics 1 min, three-elements overview 1 min, three framework + comparison pairs at 2 min each (6 min total), synthesis slide 1.5 min, takeaways 1.5 min, references 30s for Q&A pivot. Total: 14.5 min, leaves 30s buffer. Workable. If team wants more breathing room, merge slides 7+8, 9+10, 11+12 into single combined slides (framework on left, comparison on right) to drop to 12 slides and gain 1.5 min of pacing slack.
