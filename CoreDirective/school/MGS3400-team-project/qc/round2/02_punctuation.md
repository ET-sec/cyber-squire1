# Round 2 QC: Punctuation Sweep

**Scope:** `paper.docx` and `slides.pptx` in `qc/draft/`
**Method:** python-docx + python-pptx walk over every paragraph, table cell, header/footer, slide shape, table cell, and notes paragraph.

---

## Quote Style Audit

| File | Smart double quotes | Straight double quotes | Smart single/apos | Straight single/apos |
|------|---------------------|------------------------|-------------------|----------------------|
| paper.docx  | 0 | 4 | 0 | 12 |
| slides.pptx | 0 | 2 | 0 | 15 |

**Quote consistency:** clean (no mixing within either file).

---

## Findings

### citation parenthetical formatting  (4)

- **Location:** `slides.pptx slide3 shape4(TEXT_BOX (17)) ¶1`
  - **Original:** `(predecessor Dwarf Grill opened 1946 in Hapeville, Georgia)`
  - **Fix:** use APA: (Author, Year) with comma
- **Location:** `slides.pptx slide5 shape6(TEXT_BOX (17)) ¶1`
  - **Original:** `(ACSI 2023, limited service)`
  - **Fix:** use APA: (Author, Year) with comma
- **Location:** `slides.pptx slide9 shape4(TEXT_BOX (17)) ¶1`
  - **Original:** `(Burns 1978  /  Bass 1985)`
  - **Fix:** use APA: (Author, Year) with comma
- **Location:** `slides.pptx slide12 shape8(TEXT_BOX (17)) ¶1`
  - **Original:** `(over $150 million in scholarships since 1973)`
  - **Fix:** use APA: (Author, Year) with comma

### double space  (15)

- **Location:** `slides.pptx slide1 shape5(TEXT_BOX (17)) ¶1`
  - **Original:** `MGS 3400[  ]|[  ]Organizational Behavior[  ]`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape3(TEXT_BOX (17)) ¶1`
  - **Original:** `1.[  ]The two companies`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape5(TEXT_BOX (17)) ¶1`
  - **Original:** `2.[  ]How we define success`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape7(TEXT_BOX (17)) ¶1`
  - **Original:** `3.[  ]Component one: Organizationa`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape9(TEXT_BOX (17)) ¶1`
  - **Original:** `4.[  ]Component two: Leadership (B`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape11(TEXT_BOX (17)) ¶1`
  - **Original:** `5.[  ]Component three: Job Satisfa`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape13(TEXT_BOX (17)) ¶1`
  - **Original:** `6.[  ]How the three components con`
  - **Fix:** single space
- **Location:** `slides.pptx slide2 shape15(TEXT_BOX (17)) ¶1`
  - **Original:** `7.[  ]Takeaways and questions`
  - **Fix:** single space
- **Location:** `slides.pptx slide6 shape8(TEXT_BOX (17)) ¶1`
  - **Original:** `Burns (1978)[  ]/[  ]Bass (1985)
Transformatio`
  - **Fix:** single space
- **Location:** `slides.pptx slide7 shape4(TEXT_BOX (17)) ¶1`
  - **Original:** `1.[  ]Artifacts`
  - **Fix:** single space
- **Location:** `slides.pptx slide7 shape7(TEXT_BOX (17)) ¶1`
  - **Original:** `2.[  ]Espoused Values`
  - **Fix:** single space
- **Location:** `slides.pptx slide7 shape10(TEXT_BOX (17)) ¶1`
  - **Original:** `3.[  ]Basic Underlying Assumptions`
  - **Fix:** single space
- **Location:** `slides.pptx slide9 shape4(TEXT_BOX (17)) ¶1`
  - **Original:** `Transformational[  ](Burns 1978[  ]/[  ]Bass 1985)`
  - **Fix:** single space
- **Location:** `slides.pptx slide13 shape16(TEXT_BOX (17)) ¶1`
  - **Original:** `Single-Operator structure[  ]→[  ]transformational leadersh`
  - **Fix:** single space
- **Location:** `slides.pptx slide13 shape19(TEXT_BOX (17)) ¶1`
  - **Original:** `-unit franchise structure[  ]→[  ]transactional leadership `
  - **Fix:** single space

### non-ASCII char U+2192 (RIGHTWARDS ARROW)  (8)

- **Location:** `slides.pptx slide13 shape16(TEXT_BOX (17)) ¶1`
  - **Original:** `'tor structure  →  transformati'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape16(TEXT_BOX (17)) ¶1`
  - **Original:** `'al leadership  →  strong cultu'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape16(TEXT_BOX (17)) ¶1`
  - **Original:** `'trong culture  →  both Herzber'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape16(TEXT_BOX (17)) ¶1`
  - **Original:** `'g factors met  →  high engagem'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape19(TEXT_BOX (17)) ¶1`
  - **Original:** `'ise structure  →  transactiona'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape19(TEXT_BOX (17)) ¶1`
  - **Original:** `'al leadership  →  weak culture'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape19(TEXT_BOX (17)) ¶1`
  - **Original:** `' weak culture  →  both Herzber'`
  - **Fix:** consider ASCII equivalent for projector compatibility
- **Location:** `slides.pptx slide13 shape19(TEXT_BOX (17)) ¶1`
  - **Original:** `'factors unmet  →  low engageme'`
  - **Fix:** consider ASCII equivalent for projector compatibility

---

## Bullet Terminal-Punctuation Consistency (slides)

- **Slide 3:** 4 bullet(s) end with period, 2 do not.
  - terminal `'A'`: Chick-fil-A
  - terminal `'e'`: Privately held, Atlanta-rooted, employee-first by structure
  - terminal `'.'`: • Founded in 1967 by S. Truett Cathy at Atlanta's Greenbriar...
  - terminal `'.'`: • Headquartered in College Park, Georgia. More than 3,000 US...
  - terminal `'.'`: • Operator model: under 1 percent of applicants accepted, $1...
  - terminal `'.'`: • Corporate purpose centers on stewardship and hospitality, ...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 4:** 4 bullet(s) end with period, 2 do not.
  - terminal `'n'`: Popeyes Louisiana Kitchen
  - terminal `'e'`: Public, multi-unit franchised, brand-led from corporate
  - terminal `'.'`: • Founded by Al Copeland in 1972 in the New Orleans suburb o...
  - terminal `'.'`: • Owned by Restaurant Brands International, parent of Burger...
  - terminal `'.'`: • Multi-unit franchise model: a single franchisee may own do...
  - terminal `'.'`: • Cheryl Bachelder served as CEO from 2007 to 2017, led the ...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 6:** 1 bullet(s) end with period, 7 do not.
  - terminal `'s'`: Three Components of Individual Effectiveness
  - terminal `'e'`: Organizational Culture
  - terminal `'e'`: Schein (1985)
Three Levels of Culture
  - terminal `'p'`: Leadership
  - terminal `'l'`: Burns (1978)  /  Bass (1985)
Transformational vs. Transactio...
  - terminal `'n'`: Job Satisfaction
  - terminal `'y'`: Herzberg (1959)
Two-Factor Theory
  - terminal `'.'`: Culture sets the environment. Leadership reinforces it shift...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 7:** 3 bullet(s) end with period, 4 do not.
  - terminal `')'`: Organizational Culture: Schein's Three Levels (1985)
  - terminal `'s'`: 1.  Artifacts
  - terminal `'.'`: Visible structures, processes, behaviors. What you see, hear...
  - terminal `'s'`: 2.  Espoused Values
  - terminal `'.'`: Stated strategies, goals, philosophies. What the company say...
  - terminal `'s'`: 3.  Basic Underlying Assumptions
  - terminal `'.'`: Unconscious, taken-for-granted beliefs that actually drive b...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 8:** 6 bullet(s) end with period, 9 do not.
  - terminal `'n'`: Culture Comparison
  - terminal `'A'`: Chick-fil-A
  - terminal `'s'`: Artifacts
  - terminal `'.'`: Clean stores, matching uniforms, scripted "My Pleasure," Sun...
  - terminal `'s'`: Espoused Values
  - terminal `'.'`: Corporate purpose: stewardship and positive influence on eve...
  - terminal `'s'`: Basic Assumptions
  - terminal `'.'`: Each interaction matters. Effort is noticed because the Oper...
  - terminal `'s'`: Popeyes
  - terminal `'s'`: Artifacts
  - terminal `'.'`: Maintenance varies store to store, no signature script, loos...
  - terminal `'s'`: Espoused Values
  - terminal `'.'`: Servant-leadership framework stated at corporate, not carrie...
  - terminal `'s'`: Basic Assumptions
  - terminal `'.'`: The job is transactional. High turnover signals that workers...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 9:** 1 bullet(s) end with period, 9 do not.
  - terminal `'l'`: Leadership: Transformational vs. Transactional
  - terminal `')'`: Transformational  (Burns 1978  /  Bass 1985)
  - terminal `'e'`: • Idealized influence: lead by example
  - terminal `'n'`: • Inspirational motivation: shared vision
  - terminal `'w'`: • Intellectual stimulation: challenge people to grow
  - terminal `'n'`: • Individualized consideration: develop each person
  - terminal `'l'`: Transactional
  - terminal `'e'`: • Contingent reward: pay tied to performance
  - terminal `'e'`: • Management by exception: intervene only when problems aris...
  - terminal `'.'`: Transformational leadership predicts higher commitment, lowe...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 10:** 1 bullet(s) end with period, 10 do not.
  - terminal `'n'`: Leadership Comparison
  - terminal `'l'`: Chick-fil-A: transformational
  - terminal `'r'`: • One Operator per store, hand-selected from roughly 40,000 ...
  - terminal `'h'`: • Operator is on the floor daily and works the line during t...
  - terminal `'.'`: • Promotes from within. Many corporate leaders began as hour...
  - terminal `'h'`: • Personal training, same-shift recognition, visible promoti...
  - terminal `'l'`: Popeyes: transactional
  - terminal `'s'`: • Multi-unit franchisees may own dozens of stores
  - terminal `'s'`: • Daily management delegated to hired general managers witho...
  - terminal `'k'`: • Contingent reward: complete the shift, receive a paycheck
  - terminal `'s'`: • Management by exception: attention shows up only when some...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 11:** 1 bullet(s) end with period, 15 do not.
  - terminal `')'`: Job Satisfaction: Herzberg's Two-Factor Theory (1959)
  - terminal `'s'`: Hygiene Factors
  - terminal `'n'`: Prevent dissatisfaction
  - terminal `'y'`: • Pay
  - terminal `'s'`: • Working conditions
  - terminal `'y'`: • Job security
  - terminal `'y'`: • Supervision quality
  - terminal `'s'`: • Company policies
  - terminal `'s'`: Motivators
  - terminal `'n'`: Drive satisfaction
  - terminal `'t'`: • Achievement
  - terminal `'n'`: • Recognition
  - terminal `'f'`: • The work itself
  - terminal `'y'`: • Responsibility
  - terminal `'t'`: • Growth and advancement
  - terminal `'.'`: Hygiene factors are the floor. Motivators are what produce e...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 12:** 4 bullet(s) end with period, 7 do not.
  - terminal `'n'`: Job Satisfaction Comparison
  - terminal `'t'`: Chick-fil-A: both factors met
  - terminal `'e'`: Hygiene
  - terminal `'.'`: Competitive QSR pay, well-equipped kitchens, predictable sch...
  - terminal `'s'`: Motivators
  - terminal `'.'`: Remarkable Futures program (over $150 million in scholarship...
  - terminal `'t'`: Popeyes: both factors unmet
  - terminal `'e'`: Hygiene
  - terminal `'.'`: Wages near the industry minimum, chronic understaffing, inco...
  - terminal `'s'`: Motivators
  - terminal `'.'`: Limited growth at most franchise stores, minimal recognition...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 13:** 2 bullet(s) end with period, 9 do not.
  - terminal `'t'`: How the Three Components Connect
  - terminal `'e'`: Culture
  - terminal `'t'`: Schein
Sets the environment
  - terminal `'p'`: Leadership
  - terminal `'t'`: Burns and Bass
Reinforces the environment
  - terminal `'n'`: Satisfaction
  - terminal `'e'`: Herzberg
Measures the outcome
  - terminal `'A'`: Chick-fil-A
  - terminal `'.'`: Single-Operator structure  →  transformational leadership  →...
  - terminal `'s'`: Popeyes
  - terminal `'.'`: Multi-unit franchise structure  →  transactional leadership ...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 14:** 4 bullet(s) end with period, 2 do not.
  - terminal `'s'`: Takeaways
  - terminal `'.'`: Employee performance is engineered upstream through structur...
  - terminal `'.'`: A mission document by itself does not create culture. Daily ...
  - terminal `'.'`: Hygiene factors are the floor. Real engagement comes from re...
  - terminal `'e'`: Bottom line
  - terminal `'.'`: The performance gap between these chains is a people-managem...
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.
- **Slide 15:** 6 bullet(s) end with period, 4 do not.
  - terminal `'s'`: References
  - terminal `'g'`: ACSI. (2023). Restaurant study 2022-2023. American Customer ...
  - terminal `'.'`: Bachelder, C. (2015). Dare to serve: How to drive superior r...
  - terminal `'.'`: Bass, B. M. (1985). Leadership and performance beyond expect...
  - terminal `'.'`: Burns, J. M. (1978). Leadership. Harper & Row.
  - terminal `'.'`: Cathy, S. T. (2002). Eat Mor Chikin: Inspire more people. Lo...
  - terminal `'s'`: Chick-fil-A. (2023). Remarkable Futures scholarships. https:...
  - terminal `'m'`: DailyPay. (2023). QSR turnover and retention benchmarks. htt...
  - terminal `'.'`: Herzberg, F., Mausner, B., & Snyderman, B. (1959). The motiv...
  - terminal `'.'`: Schein, E. H. (1985). Organizational culture and leadership....
  - **Fix:** pick one style per slide (all periods or none) and apply uniformly.

---

## Totals

- Em dashes (U+2014): **0**  (target: 0)
- En dashes in prose (U+2013): **0**
- En dashes inside numeric ranges (advisory): **0**
- Ellipsis chars (U+2026): **0**
- Three-period ellipses (`...`): **0**
- Double spaces: **15**
- Trailing whitespace paragraphs: **0**
- Semicolons: **0**
- Spaced-hyphen as dash ( - ): **0**
- Excessive hyphens (3+): **0**
- Citation parenthetical issues: **4**
- Weird/non-ASCII unicode flags: **8**
- Bullet terminal-punctuation inconsistencies: **12**

- **Hard violations:** 39
- **Advisory items:** 0

## Verdict

**NOT CLEAN** — 31 hard violation(s) require fixing before submission.
