# CoreDirective Job Pipeline Tracker - System Spec

**Sheet ID:** `10xUZ-hPxgEhMpY8Y37Z37yNcWeg9HuFlrJ2rs1jFEHE`
**Owner:** Emmanuel Tigoue / CoreDirective
**Style:** Black void background, electric green text, JetBrains Mono font
**Tax basis:** Georgia (Atlanta), single filer, 2026 brackets
**Maintenance:** Edited by both Emmanuel directly and Claude Code via CLI (/tailor-resume skill, /pipeline-update skill, /job-research skill)

---

## 1. System overview

The tracker is a multi-tab spreadsheet that does three jobs in one product:

1. **Pipeline of record.** Every active job opportunity has both a row in a master sheet AND a dedicated tab. The master row is the at-a-glance view; the tab is the deep record.
2. **Compensation calculator.** Anything entered as gross hourly or annual salary is automatically converted to hourly net, weekly gross/net, monthly gross/net, and annualized totals using Georgia 2026 tax assumptions baked into named formulas.
3. **Cross-sheet integrity layer.** Adding or deleting an entry in the master sheet cascades to every place that entry appears (per-job tab, recruiter log, action list, comp analysis row).

The system is designed so a single command from Claude Code CLI ("add Milestone Tech to the pipeline") triggers all of: row insert, per-job tab spawn from template, recruiter log append, action list seed, and comp analysis row insertion with formulas filled. Likewise a single delete cascades the removal.

---

## 2. Tab inventory

Tabs visible on the bottom bar (left to right):

| Tab | Type | Purpose |
|---|---|---|
| Amex_AppSec | Per-job | Deep record for the Amex/Experis AppSec contract |
| NICE_AIDataSpec | Per-job | Deep record for the NICE Ltd AI Data Specialist req |
| JDs_Full | Reference | Full job description text for every active req, indexed by company key |
| Action_List | Operational | Next-actions queue across all reqs, dated with owner and due |
| Recruiter_Log | Operational | Chronological log of every recruiter touch (email, call, LinkedIn DM) |
| Comp_Analysis | Calculator | Master compensation comparison, one row per active opportunity |
| Brilliant_Cloudflare | Per-job | Deep record for the Brilliant Cloudflare Application Engineer C2H |

Implied additional tabs (likely hidden or scrolled off):
- **Pipeline_Master** - the master row table, source of truth for what is in play
- **Settings_Tax** - Georgia 2026 tax brackets, FICA rates, deductions
- **Settings_Conventions** - status enums, role categories, source platforms

---

## 3. Per-tab spec

### 3.1 Pipeline_Master (the source of truth)

This is the spine of the system. Every other tab cross-references this.

**Columns (16):**
| # | Field | Type | Notes |
|---|---|---|---|
| A | row_id | auto | UUID or sequence, never reused |
| B | company_key | text | UPPER_SNAKE_CASE used as tab name and Action_List key (e.g., MILESTONE_TECH) |
| C | company_display | text | Pretty name for UI ("Milestone Technologies") |
| D | end_client | text | If staffing firm, who is the actual client |
| E | role | text | Job title from JD |
| F | req_id | text | Recruiter or ATS req number |
| G | type | enum | FT, Contract, C2H |
| H | duration | text | "6+ months" if contract, blank if FT |
| I | location | text | Remote / Hybrid / Onsite + city |
| J | pay_offered | currency | Recruiter's first number |
| K | pay_counter | currency | Counter target |
| L | pay_floor | currency | Walk-away |
| M | recruiter_name | text |  |
| N | recruiter_contact | text | Email + phone |
| O | source | text | Indeed, LinkedIn, direct, referral |
| P | resume_used | text | Foundation + tailored variant filename |
| Q | prep_folder | path | `~/cyber-squire-ops/CoreDirective/career/<key>/` |
| R | status | enum | Applied, Screen Scheduled, Screened, Tech Screen, Offer, Rejected, Ghosted |
| S | next_action | text | What to do next |
| T | next_action_date | date |  |
| U | created | timestamp |  |
| V | updated | timestamp | auto on any cell edit |

**Formulas:**
- `Q` (prep_folder): `="~/cyber-squire-ops/CoreDirective/career/" & LOWER(B2) & "/"`
- `V` (updated): driven by an `onEdit` Apps Script trigger that writes `NOW()` to V whenever any cell in the row changes

**Behavior on row insert (add):**
1. Apps Script `onInsert(row)` fires
2. Spawns a new tab from the Per_Job_Template using `B` as the tab name
3. Appends a row to Comp_Analysis with B as Pipeline display, G as Type, and J/K/L feeding the comp formulas
4. Appends a row to Recruiter_Log if N is non-empty
5. Appends a row to Action_List from S+T
6. Creates the prep folder on disk via the `gws-cli` or `gcloud` integration (out-of-spreadsheet)
7. Appends an entry to JDs_Full keyed by B, with the JD text from a paired field

**Behavior on row delete:**
1. Apps Script `onDelete(row)` fires
2. Captures B (company_key) before the delete completes
3. Removes the matching tab named B
4. Removes the matching row from Comp_Analysis (lookup by Pipeline = B-derived display)
5. Removes any rows from Recruiter_Log where company_key column = B
6. Removes any rows from Action_List where company_key column = B
7. Removes the JDs_Full entry keyed by B
8. Optionally archives all of the above to a hidden Archived_<date> tab so it can be undone within 7 days

This is the cascade the user described. It does not depend on Claude Code; it is pure Apps Script bound to the Sheet.

---

### 3.2 Comp_Analysis (the compensation calculator)

**Columns (visible in screenshot, with full set):**

| Col | Field | Source | Formula |
|---|---|---|---|
| A | Pipeline | Pipeline_Master.C with bracket of pay band | manual or `=VLOOKUP(...)` |
| B | Type | Pipeline_Master.G | `=VLOOKUP(...)` |
| C | Hourly Gross | from K Pipeline_Master if hourly, else Annual/2080 | `=IF(G="FT", AnnualGross/2080, HourlyRate)` |
| D | Hourly Net | C minus tax | `=C * (1 - TaxRate(G, AnnualGrossEstimate))` |
| E | Weekly Gross | C * 40 | `=C*40` |
| F | Weekly Net | D * 40 | `=D*40` |
| G | Monthly Gross | E * 52 / 12 | `=E*52/12` (avg 4.33 weeks/mo) |
| H | Monthly Net | F * 52 / 12 | `=F*52/12` |
| I | Annual Gross | C * 2080 | `=C*2080` |
| J | Annual Net | D * 2080 | `=D*2080` |
| K | Effective Tax % | (Gross - Net) / Gross | `=(I-J)/I` |
| L | Delta vs Baseline | this row - CURRENT BASELINE | `=H - $B$9` (where row 9 holds baseline) |

**Tax formula (named function `TaxRate(type, annual_gross)`):**

For Georgia, single filer, 2026:
- Federal income tax (progressive 2026 brackets):
  - 10% on first $11,925
  - 12% on $11,925 - $48,475
  - 22% on $48,475 - $103,350
  - 24% on $103,350 - $197,300
  - 32% on $197,300 - $250,525
  - 35% on $250,525 - $626,350
  - 37% above $626,350
- Standard deduction (single 2026): $15,000
- Georgia state income tax: **flat 5.39%** for 2026 (decreasing 0.10% per year toward 4.99% by 2029)
- Georgia standard deduction (single 2026): $12,000
- FICA: 6.2% Social Security on first $176,100 + 1.45% Medicare (uncapped) + 0.9% additional Medicare above $200K = 7.65% baseline
- For Contract / C2H W2: same as FT W2
- For 1099 / SE: add 7.65% self-employment tax (employer FICA portion); subtract 1/2 SE tax above the line

Implementation as a named LAMBDA in Sheets:

```
TaxRate = LAMBDA(type, gross,
  LET(
    federal_taxable, MAX(0, gross - 15000),
    federal_tax,
      IF(federal_taxable <= 11925, federal_taxable * 0.10,
      IF(federal_taxable <= 48475, 1192.50 + (federal_taxable - 11925) * 0.12,
      IF(federal_taxable <= 103350, 5578.50 + (federal_taxable - 48475) * 0.22,
      IF(federal_taxable <= 197300, 17651 + (federal_taxable - 103350) * 0.24,
      IF(federal_taxable <= 250525, 40199 + (federal_taxable - 197300) * 0.32,
      IF(federal_taxable <= 626350, 57231 + (federal_taxable - 250525) * 0.35,
                                    188769.75 + (federal_taxable - 626350) * 0.37)))))),
    ga_taxable, MAX(0, gross - 12000),
    ga_tax, ga_taxable * 0.0539,
    fica_ss, MIN(gross, 176100) * 0.062,
    fica_medicare, gross * 0.0145 + MAX(0, gross - 200000) * 0.009,
    se_addon, IF(type = "1099", gross * 0.0765, 0),
    total_tax, federal_tax + ga_tax + fica_ss + fica_medicare + se_addon,
    total_tax / gross
  )
)
```

This single function returns the effective tax rate. The whole tab uses it. Update the function once when 2027 brackets change and every row recalculates.

**Spot check against every visible row:**

| Pipeline | Gross | Sheet Net | Spec Net | Spec Eff. Tax | Verdict |
|---|---|---|---|---|---|
| Dropzone AI High ($217K FTE) | $104/hr | $72/hr | $71.50/hr | 31.3% | OK |
| Dropzone AI Mid ($196K FTE) | $94/hr | $65/hr | $65.20/hr | 30.6% | OK |
| OneDigital AI Sec ($125K FTE) | $60/hr | $43/hr | $44.10/hr | 26.5% | OK (slightly low) |
| ETS / Repay ($110K Contract+Convert) | $53/hr | $39/hr | $39.30/hr | 25.8% | OK |
| **Brilliant Cloudflare ($85/hr Contract C2H)** | **$85/hr** | **$74/hr** | **$59/hr** | **30.6%** | **BROKEN** |

**Five rows correct, one row broken.** The Cloudflare row has an effective tax rate of 12.9% which is mathematically impossible at $176,800 gross W2 in Georgia. FICA alone is 7.65%, and federal income tax pushes the floor above 25%. The most likely cause: the formula in C7:H7 was overwritten with a stale rate or a different tax model (possibly 1099 net with deductions, or just FICA-only). **Do not use the $74 net in any negotiation; the real number is $59.**

**Corrected row 7 (Brilliant Cloudflare):**

| Field | Value |
|---|---|
| Hourly Gross (C7) | $85 |
| Hourly Net (D7) | $59 |
| Weekly Gross (E7) | $3,400 |
| Weekly Net (F7) | $2,361 |
| Monthly Gross (G7) | $14,733 |
| Monthly Net (H7) | $10,233 |
| Annual Gross (I7) | $176,800 |
| Annual Net (J7) | $122,756 |
| Effective Tax % (K7) | 30.6% |

**The fix in the live sheet:**

Replace the static numbers in row 7 with the same TaxRate LAMBDA formula every other row uses, so the row recalculates instead of holding stale values. In C7 through K7, the formulas should be:

```
C7: =85
D7: =C7 * (1 - TaxRate(B7, I7))
E7: =C7 * 40
F7: =D7 * 40
G7: =E7 * 52 / 12
H7: =F7 * 52 / 12
I7: =C7 * 2080
J7: =D7 * 2080
K7: =(I7 - J7) / I7
```

Once the LAMBDA is in place at the workbook level, every row including row 7 recalculates from one source of truth. Then a single edit in Settings_Tax (when 2027 brackets drop) updates every row in the system.

**Sanity check after fix:**

The corrected $59/hr net at 40 hrs/wk gives Emmanuel **$10,233/mo net** vs the **$72/hr Dropzone FTE giving $12,480/mo net**. The Dropzone FTE is roughly $2,247/mo better than the Cloudflare contract at the listed rates, which is the kind of comparison the tracker exists to surface accurately. The broken $74 net was hiding a $1,300/mo gap.

**CURRENT BASELINE row (row 9 in screenshot):** holds Emmanuel's current monthly net so every other row's L column shows delta. Currently $0/mo because between roles.

---

### 3.3 Per-job tabs (Amex_AppSec, NICE_AIDataSpec, Brilliant_Cloudflare, etc.)

One tab per active opportunity, spawned from `Per_Job_Template` when a row is inserted in Pipeline_Master.

**Sections (top to bottom):**

1. **Header block** (rows 1-5)
   - Company display name (linked formula `=Pipeline_Master!C{row}`)
   - End client
   - Role + req ID
   - Type / duration / location
   - Status (linked, color-coded conditional formatting)

2. **Recruiter block** (rows 7-12)
   - Recruiter name, email, phone, LinkedIn
   - Date of first contact
   - Source (Indeed / LinkedIn / direct / referral)
   - Last touch date (linked to Recruiter_Log MAX date for this key)
   - Next touch date

3. **Pay block** (rows 14-22)
   - Pay offered, counter, floor (mirrored from Pipeline_Master J/K/L)
   - Hourly gross, hourly net, weekly gross, weekly net, monthly gross, monthly net, annual gross, annual net (all mirrored from Comp_Analysis row for this key via `INDEX/MATCH` on company_key)
   - Delta vs baseline

4. **Resume block** (rows 24-28)
   - Foundation used (e.g., AISecurity_Engineer)
   - Tailored variant filename
   - Path to docx + pdf in Documents/Resumes/resume variations/
   - Path to clean Downloads filename
   - Date last updated
   - Verify_resume QC pass status (PASS/FAIL)

5. **JD block** (rows 30-50)
   - Top 5 must-haves (extracted from JD)
   - Required keywords with present/missing flag (cross-referenced against the resume DOCX text via Apps Script reading the file)
   - Stack list
   - Salary range from JD if posted
   - Link to full JD text in JDs_Full tab

6. **Process block** (rows 52-65)
   - Recruiter screen date + result + notes
   - Tech screen date + result + notes
   - Behavioral round date + result + notes
   - Final / fit round
   - Offer date + amount + signed?
   - Rejection date + reason

7. **Prep block** (rows 67-90)
   - Tier 1 study items checklist (4 hrs)
   - Tier 2 study items checklist (6 hrs)
   - Tier 3 study items checklist (2 hrs)
   - Lab/POC checklist
   - Mock screen done?
   - Cheat card link (path to 02_CHEAT_CARD.md in prep folder)

8. **Notes block** (rows 92+)
   - Free text running journal
   - Auto-stamped by Apps Script `onEdit` to prepend `[YYYY-MM-DD HH:MM] ` to each new entry

---

### 3.4 JDs_Full

**Columns:**
| Col | Field |
|---|---|
| A | company_key (the join key to everything else) |
| B | role |
| C | date_posted |
| D | source_url |
| E | jd_text (full text, monospace, wrapped) |
| F | extracted_must_haves (JSON-ish or comma-separated) |
| G | extracted_keywords |
| H | extracted_stack |
| I | extracted_salary_range |
| J | last_synced |

Rows are seeded by Claude Code's /job-research skill, which scrapes the JD URL and writes columns A-J in one transaction.

Cascade: when company_key is removed from Pipeline_Master, the matching row here is deleted (or moved to Archived_JDs).

---

### 3.5 Action_List

**Columns:**
| Col | Field |
|---|---|
| A | company_key |
| B | action_text |
| C | due_date |
| D | priority (P0 P1 P2) |
| E | status (open, doing, done, blocked) |
| F | created |
| G | done_at |
| H | owner (Emmanuel, Claude, Recruiter) |

Auto-population:
- New row in Pipeline_Master inserts a default "Send tailored resume to <recruiter_name>" P0 action with due = today.
- Status change to "Screen Scheduled" inserts "Tier 1 study (4 hrs) before <screen_date>" P0 action.
- Status change to "Tech Screen" inserts "Run Bedrock Guardrails lab + Databricks Community Edition walkthrough" P0 action.
- Cascade delete on company_key from Pipeline_Master removes all matching rows here.

Default view: filter `status != "done"` AND `due_date <= TODAY() + 7`, sorted by priority then due_date.

---

### 3.6 Recruiter_Log

**Columns:**
| Col | Field |
|---|---|
| A | timestamp |
| B | company_key |
| C | recruiter_name |
| D | direction (in / out) |
| E | channel (email, call, sms, LinkedIn, Indeed) |
| F | summary (1-2 lines) |
| G | full_message (collapsed) |
| H | next_step |
| I | next_step_date |

Each new touch is one row. The per-job tab's Last Touch field is `=MAXIFS(Recruiter_Log.A, Recruiter_Log.B, ThisCompanyKey)`.

Cascade: rows where B = deleted company_key are removed (or archived).

---

### 3.7 Settings_Tax

Holds the constants used by the TaxRate LAMBDA. Editing here updates every comp calculation in the system.

| Setting | Value |
|---|---|
| federal_brackets_2026 | array |
| federal_standard_deduction_single_2026 | 15000 |
| ga_flat_rate_2026 | 0.0539 |
| ga_standard_deduction_single_2026 | 12000 |
| fica_ss_rate | 0.062 |
| fica_ss_wage_base_2026 | 176100 |
| fica_medicare_rate | 0.0145 |
| fica_additional_medicare_rate | 0.009 |
| fica_additional_medicare_threshold | 200000 |
| se_tax_rate | 0.0765 |
| hours_per_year_ft | 2080 |
| hours_per_week_default | 40 |
| weeks_per_year | 52 |

When a year changes, update this tab once. Every dependent calculation re-runs.

---

### 3.8 Settings_Conventions

| Setting | Allowed values |
|---|---|
| status_enum | Applied, Screen Scheduled, Screened, Tech Screen, Behavioral, Final, Offer, Accepted, Rejected, Ghosted, Withdrawn |
| type_enum | FT Remote, FT Hybrid, FT Onsite, Contract Remote, Contract Hybrid, Contract Onsite, Contract C2H |
| source_enum | Indeed, LinkedIn, Direct, Referral, Recruiter Outbound, HiringCafe, Greenhouse, Workday, ATS Other |
| priority_enum | P0, P1, P2 |
| color_status | mapping table for conditional formatting (e.g., Offer = bright green, Rejected = dim red, Ghosted = grey) |

---

## 4. Data flow

### When Claude Code adds a new opportunity (CLI command)

1. Claude Code parses the JD (URL, paste, or screenshot).
2. Claude Code POSTs to n8n master-cmd webhook with action `sheets`, payload includes:
   - sheet_id
   - target_tab `Pipeline_Master`
   - row payload (all 22 columns)
   - JD text for `JDs_Full`
   - Recruiter touch for `Recruiter_Log`
3. n8n writes the row to Pipeline_Master.
4. Apps Script onInsert fires the cascade (spawns per-job tab, inserts Comp_Analysis row, JDs_Full row, default Action_List rows, Recruiter_Log row).
5. Apps Script returns success or error to n8n which logs to Datadog.
6. Claude Code receives the response and creates the local prep folder on disk.

### When Emmanuel manually edits a cell

1. Apps Script onEdit fires.
2. If the edited cell is in Pipeline_Master, propagates the change to the per-job tab and Comp_Analysis row via INDEX/MATCH dependents.
3. Updates `updated` timestamp on the affected row.

### When a row is deleted (cascade)

Already specced in section 3.1. Apps Script captures the company_key before delete completes, then sweeps all dependent tabs and removes matching rows.

### When a comp number changes

1. Pay column edited in Pipeline_Master.
2. Comp_Analysis row recalculates via formula chain.
3. Per-job tab's Pay block re-mirrors via INDEX/MATCH.
4. Delta vs baseline updates.

---

## 5. Apps Script triggers needed

```javascript
function onEdit(e) {
  const sheet = e.range.getSheet().getName();
  if (sheet === "Pipeline_Master") {
    propagateMasterEdit(e);
    stampUpdated(e);
  } else if (sheet.startsWith("Per_") || isPerJobTab(sheet)) {
    stampJournalIfNotesEdit(e);
  }
}

function onChange(e) {
  // captures structural changes including row inserts and deletes
  if (e.changeType === "INSERT_ROW") {
    spawnDependents(e);
  } else if (e.changeType === "REMOVE_ROW") {
    cascadeDelete(e);
  }
}
```

Triggers are bound to the spreadsheet, not specific user actions. They fire whether Claude Code wrote the row or Emmanuel typed it.

---

## 6. Design system (enforced across every tab, every cell)

CoreDirective brand: black void + electric green, tactical, restraint reads as intelligence. Every tab in this workbook honors the system. Plain default Sheets styling (white background, black text, Arial) is a bug, not a tab "Claude for Sheets has not gotten to yet."

### 6.1 Color palette (locked hex values)

| Token | Hex | Use |
|---|---|---|
| `bg.void` | `#0d1117` | Default cell background, every tab |
| `bg.elevated` | `#161b22` | Header rows, banner rows, subtotal rows |
| `bg.recessed` | `#010409` | Pinned title row, footer rows |
| `accent.signal` | `#3fb950` | Primary text, key data, hyperlinks |
| `accent.signal.bright` | `#56d364` | Title text in banner rows |
| `accent.signal.dim` | `#238636` | Borders, gridlines, secondary text |
| `text.body` | `#c9d1d9` | Long-form text (notes, JD body, descriptions) |
| `text.muted` | `#8b949e` | Timestamps, metadata, helper text |
| `state.warn` | `#d29922` | Pending, blocked, watch states |
| `state.danger` | `#f85149` | Rejected, error, missed deadline |
| `state.success` | `#3fb950` | Offer, accepted, done |
| `state.neutral` | `#6e7681` | Ghosted, withdrawn, archived |

No other colors. Anything outside this palette is a violation and gets rewritten on the next audit.

### 6.2 Typography rules

| Element | Font | Size | Weight | Color |
|---|---|---|---|---|
| Tab title banner row | JetBrains Mono | 14pt | Bold | `accent.signal.bright` on `bg.recessed` |
| Section headers within a tab | JetBrains Mono | 12pt | Bold | `accent.signal` on `bg.elevated` |
| Column headers | JetBrains Mono | 10pt | Bold | `accent.signal` on `bg.elevated` |
| Data cells (numeric, currency, date, enum) | JetBrains Mono | 10pt | Regular | `accent.signal` on `bg.void` |
| Data cells (long-form text, notes, JD) | Inter | 10pt | Regular | `text.body` on `bg.void` |
| Helper / metadata text (timestamps, system notes) | Inter | 9pt | Regular | `text.muted` on `bg.void` |
| Hyperlinks | JetBrains Mono | 10pt | Regular | `accent.signal` underlined |
| Empty / blank cell | n/a | n/a | n/a | `bg.void` (never default white) |

JetBrains Mono is the workhorse. Inter is the long-form body font. No other fonts. No Arial, no Calibri, no default sans-serif. If a cell is "regular no color text," it has skipped the system and must be repainted.

### 6.3 Layout and spacing

- **Row height:** 28px default for data rows, 36px for section headers, 48px for tab title banner.
- **Column padding:** Use cell padding via wrap text + a 4px left/right indent style. No values should sit flush against the left border.
- **Borders:** No gridlines visible by default. Section headers carry a 1px bottom border in `accent.signal.dim`. Data tables carry no borders, separation comes from row banding.
- **Row banding:** Data tables alternate `bg.void` and `#0f141b` (one shade lighter) for readability. Banding starts under the column header, not from row 1.
- **Frozen rows:** Tab title banner (row 1) and column header row (row 2) frozen on every tab.
- **Frozen columns:** Pipeline_Master freezes columns A-C (id, key, display name). Per-job tabs freeze A-B.
- **Merged cells:** Only for tab title banners and section dividers. Data cells never merge.

### 6.4 Status enum styling (conditional formatting, applied workbook-wide)

| Status | Background | Text | Notes |
|---|---|---|---|
| Applied | `bg.elevated` | `text.muted` | Quiet, in-flight |
| Screen Scheduled | `#1f6feb` 20% alpha | `accent.signal` | Cool blue tint |
| Screened | `accent.signal.dim` 20% alpha | `accent.signal` | Made it past stage 1 |
| Tech Screen | `#a371f7` 20% alpha | `accent.signal.bright` | Purple tint, in the depth zone |
| Behavioral | `#a371f7` 20% alpha | `accent.signal.bright` | Same as Tech Screen |
| Final | `state.warn` 20% alpha | `state.warn` | Watch state |
| Offer | `state.success` 30% alpha | `accent.signal.bright` Bold | Bright |
| Accepted | `state.success` 60% alpha | `bg.void` Bold | Inverted, peak signal |
| Rejected | `state.danger` 15% alpha | `state.danger` | Dim red, no shouting |
| Ghosted | `state.neutral` 15% alpha | `state.neutral` strikethrough | Dead |
| Withdrawn | `state.neutral` 15% alpha | `text.muted` | Pulled by Emmanuel |

Apply the rules workbook-wide via Conditional Formatting > Custom formula on the status column of every tab.

### 6.5 Number / date / currency format

| Type | Format | Example |
|---|---|---|
| Currency USD | `[Green]$#,##0;[Red]-$#,##0` | `$1,234` / `-$56` |
| Hourly rate | `[Green]$#,##0/"hr"` | `$85/hr` |
| Percent | `[Green]0.0%` | `30.6%` |
| Date | `yyyy-mm-dd` | `2026-04-29` |
| Timestamp | `yyyy-mm-dd hh:mm` | `2026-04-29 12:00` |
| Integer count | `[Green]#,##0` | `1,234` |

Every numeric cell uses one of these formats. Default General is a violation.

### 6.6 Brand audit checklist (run on every audit pass)

For each tab, verify:

1. **Background:** Cell A1:Z1000 default fill is `bg.void` (`#0d1117`), not white.
2. **Font:** Default cell font is JetBrains Mono 10pt for data, Inter 10pt for long text. No Arial, no Calibri.
3. **Title banner:** Row 1 is merged, height 48px, fill `bg.recessed`, text `accent.signal.bright` 14pt Bold all caps.
4. **Column headers:** Row 2 fill `bg.elevated`, text `accent.signal` 10pt Bold.
5. **Frozen rows:** Rows 1-2 frozen.
6. **Number formats:** Currency, percent, date, hourly all match section 6.5.
7. **Status conditional formatting:** Applied to the status column with the rules in section 6.4.
8. **Row banding:** Alternating `bg.void` and `#0f141b` from row 3 down.
9. **No defaults:** No cell uses the default Sheets styling (white bg, black text, Arial 10).
10. **Empty cells:** Empty cells still carry the brand fill `bg.void`, not the default white.

If any check fails, repaint the tab. Do not skip on the assumption that "the formula matters more than the look." The look IS part of the system, because Emmanuel reads this sheet 5 times a day during a job hunt and the brand identity is what makes glanceability fast.

### 6.7 Anti-patterns to fix on sight

- Plain white background in any cell. Repaint to `bg.void`.
- Black text on white background. Repaint to `accent.signal` on `bg.void`.
- Default Arial. Switch to JetBrains Mono (data) or Inter (long text).
- Mixed font sizes within one column. Standardize to 10pt.
- Cells with `=NA()` or `#REF!` showing in red default. Wrap in `IFERROR` to show empty `bg.void` instead.
- Currency without the green color override. Re-apply the format from section 6.5.
- Status text without conditional formatting. Apply the rules from section 6.4.
- Hyperlinks in default blue. Override to `accent.signal` underlined.
- Title banners that are not merged or are missing the bg/text contrast.
- "Notes" cells that wrap into a giant unreadable block. Set max row height 6 lines, then click-to-expand.

### 6.8 Other conventions (carryover)

- **Currency:** USD, no decimals, `$1,234` not `$1,234.00`.
- **Dates:** `yyyy-mm-dd` everywhere, 24-hour times.
- **Tab names:** UPPER_SNAKE_CASE for company keys, PascalCase for system tabs.
- **No PII outside the system tabs.** Recruiter contact info is fine. SSN, full address, DOB never enter the sheet.

---

## 7. Integrations

| System | Direction | Method | Auth |
|---|---|---|---|
| Claude Code CLI | write | n8n master-cmd webhook, action: sheets | n8n API key |
| Local markdown tracker | mirror write | gws CLI or rclone | Google OAuth (etigoue@tigouetheory.com) |
| Telegram (@CDirective_bot) | read alerts | Apps Script daily digest at 7 AM ET | Telegram Bot Token |
| Datadog | observability | Apps Script error log POST | Datadog API key |
| Resume DOCX files | read for ATS gap | Apps Script Drive read | Google Drive scope |

---

## 8. Open questions for Emmanuel to confirm

1. **Tax baseline:** The spec assumes Georgia 2026 single-filer with standard deduction. Are you actually filing single, married, or HoH? Adjust standard deduction and brackets if married/HoH.
2. **Pre-tax deductions:** Comp_Analysis currently shows $74/hr net on $85/hr Contract C2H, which implies your formula assumes ~12-13% effective tax. The math without pre-tax deductions gives ~30%. Is the formula subtracting an assumed health insurance + 401k contribution before computing tax? Confirm, or recalibrate.
3. **CURRENT BASELINE:** Currently $0/mo because between roles. Should this default to last role's monthly net so deltas are meaningful, or stay at $0?
4. **Cascade timing:** Hard delete vs archive-on-delete? Recommend archive-on-delete with 7-day undo window.
5. **Per-job tab template:** Does one already exist or do I need to draft a Per_Job_Template tab spec? If so, the section 3.3 layout above is what to build.
6. **Hidden tabs:** Are Pipeline_Master, Settings_Tax, Settings_Conventions actually present, or do I need to spec them as new tabs?

---

## 9. What Claude for Sheets should do with this spec

1. **Read this spec** and treat it as the system contract.
2. **Audit the live sheet** against section 3 - flag any tab that does not match its spec.
3. **Run the brand audit checklist (section 6.6) on every tab.** Any tab with default white background, black text, Arial font, or any of the section 6.7 anti-patterns gets repainted in the same pass. Brand consistency is non-negotiable.
4. **Verify formulas** in Comp_Analysis against the TaxRate LAMBDA in section 3.2 and recalibrate if the live values do not match the spec output. Specifically replace the broken Brilliant_Cloudflare row 7 hardcoded values with the formula chain.
5. **Build the missing pieces:** Pipeline_Master, Settings_Tax, Settings_Conventions, Per_Job_Template, and the cascade Apps Script triggers.
6. **Run a dry-run cascade test:** insert a fake row in Pipeline_Master named TEST_DELETE_ME, verify the dependent tabs and rows spawn, then delete and verify cascade removal.
7. **Backfill:** every existing per-job tab (Amex_AppSec, NICE_AIDataSpec, Brilliant_Cloudflare) needs a matching row in Pipeline_Master if not already present.
8. **Wire the integrations** in section 7 so Claude Code CLI can write to the sheet via n8n. Every Claude Code write must apply the brand on insert, not leave plain default styling for a later audit.

When Claude for Sheets finishes the audit and build, output a single status report:

```
SPEC COMPLIANCE: <pct>%
TABS PRESENT: <count> / <count>
TABS BRAND-COMPLIANT: <count> / <count>
FORMULAS VALIDATED: <count> / <count>
CASCADE TESTED: PASS / FAIL
INTEGRATIONS WIRED: <list>
ANTI-PATTERNS REMOVED: <list with cell refs>
GAPS: <list of missing pieces>
NEXT ACTIONS: <list>
```

**Standing rule for all future writes:** any new row, tab, or cell added by Claude Code, Claude for Sheets, or Emmanuel must arrive brand-compliant on creation. The brand is a system contract, not a polish step. If the writer cannot apply the brand inline, it does not write.
