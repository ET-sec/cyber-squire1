# Adversarial AI Detection Read

**Question on the table:** A suspicious professor (Dr. Conklin, MGS 3400) asks me, "Is this AI?" What do I tell him?

**One-line verdict:** Yes, I would flag this for review. The artifact has been edited well enough to defeat a casual sniff test, but the underlying scaffolding still reads as machine-built. Expect a 6 to 7 out of 10 on a hostile read.

---

## Scores

| Surface | Score (1-10, 10 = obviously AI) | Read |
|---|---|---|
| Paper (paper.docx) | **6/10** | Heavily edited but the argument architecture is too clean. |
| Slide bodies (slides.pptx) | **5/10** | Bullet phrasing is consistent in a way student decks rarely are. |
| Speaker notes | **7/10** | Most damning surface. Notes have a clear "tell the presenter what to do" voice that AI defaults to when asked to write notes. |

A naive professor scores this lower. A professor who has read 200 of these papers and knows what real undergrad teamwork sounds like scores it higher.

---

## What the math says

I ran sentence statistics on the paper and the notes. Two readings.

**Paper:** 116 sentences, mean 11.3 words, median 8 words, stdev 10.7, range 1 to 54. That looks human at first glance. The variance is real and the median is short. But the variance comes mostly from chunking: short labels and section headers ("Chick-fil-A.", "How we define success.", "1. Organizational Culture") pulling the median down, with one or two long compound sentences pulling the max up. The middle of the distribution, the actual argumentative prose, is uniformly tight. 25 percent of sentences land in the 12 to 25 word band, which is the AI comfort zone, and most of the rest are deliberately clipped one or two beat fragments that read as a stylistic choice rather than student variance.

**Notes:** 83 sentences, mean 12.0, median 11, stdev 6.7. That is much tighter. Notes are the place a real student team gets sloppy: half-formed thoughts, "remember to mention," off-topic asides. These notes have none of that. They are clean prose with a low standard deviation. AI fingerprint.

**Em dashes:** Zero in both files. That tells me Round 1 cleanup was applied and the obvious AI tell was scrubbed. It does not tell me a human wrote it. It tells me someone who knew about the em-dash tell removed them.

**AI-favorite vocabulary:** None of the usual suspects ("leverage," "robust," "seamless," "navigate," "foster," "underscore," "tapestry," "myriad," "holistic"). Either a human wrote this, or the writer (or a Round 1 pass) deliberately suppressed those words. Given the rest of the surface, I read this as suppression.

---

## The signals that would tip a hostile professor

### 1. The argument is too tidy

> "Culture sets the environment workers operate in, leadership reinforces or undermines it shift by shift, and satisfaction is the downstream outcome that drives the discretionary effort customers see."

This is a textbook three-beat causal chain. Real undergrad writing in a four-person team does not produce this clean of a thesis sentence in paragraph one. When students collaborate, the joints show: somebody's pet phrase, a clunky transition, a repeated word the editor missed. This sentence is engineered.

The closing of the paper hits the same beat:

> "Two chains hiring from the same labor pool produce different employees because the upstream structures produce different working environments. Employee performance is engineered before it is trained."

That last sentence is a copywriter's drop-the-mic move. It is the kind of sentence ChatGPT produces when you tell it "end with a punchy line." A real student team writes a longer, less satisfying conclusion.

### 2. Triplet construction shows up in load-bearing sentences

I found five clean three-item lists, all in structural positions:

- "performance, retention, and observed engagement"
- "culture, leadership, and job satisfaction"
- "hiring, training, and operations"
- "conditions, supervision, and job security"
- "recognition, growth, and the work itself"

Every one of these is doing argumentative work, not just listing items. The triplet rhythm at structural pivots is an AI cadence signature. Humans use triplets too, but they fumble them: four items, or two items pretending to be three, or a triplet where the third item is awkwardly long.

### 3. Antithesis pattern in the notes (memory rule violation flag)

> "Transactional leadership is not bad. It is necessary in any organization. But it does not by itself produce engagement."

> "Herzberg's key insight: hygiene and motivators are not on the same scale. They are two different scales."

Both are textbook "Not X. Y." juxtaposition. There is also a subtler "Solving hygiene problems takes a worker from miserable to neutral. Adding motivators takes a worker from neutral to engaged" parallel construction in the same paragraph. AI loves this structure. Humans use it occasionally; AI uses it three times in 83 sentences.

### 4. The "round numbers and headline statistics" tell

The paper hits hard with:
- "85 out of 100"
- "71 against an industry average of 78"
- "60 percent... 130 to 150 percent"
- "$10,000 fee"
- "more than 3,000 US restaurants"
- "more than 4,200 restaurants worldwide"
- "$150 million in scholarships since 1973"
- "40,000 applicants per year"
- "under one percent"

Every figure is a clean headline number. None of them are weird. A real student visit produces a weird specific: "the drive-through line was 11 cars deep at 12:43," "one of the cashiers had a name tag that said 'Trainee'," "they were out of mac and cheese." None of that texture is here. The "observed engagement" claims are abstract: "eye contact, coordinated rush" vs. "long waits, visible stress." That is the level of specificity AI produces when it is asked to fabricate field observations.

### 5. The speaker notes voice is too even

Real student notes look like: "TODO: figure out transition," "Sara handles this slide," "skip if running long." These notes read like a professional facilitator wrote them. Examples:

> "Land the three takeaways slowly."
> "Walk the audience down the iceberg."
> "Read across each row to make the contrast hit."
> "Time check: 30 to 45 seconds for this slide including intros."

The "Time check" lines are particularly suspect. Four-person student teams almost never pre-budget time at the slide level on a first draft. They do it during rehearsal, by feel. Slide-level time budgets in the notes look like a deliverable spec, not a working document.

### 6. Voice consistency is too perfect across 15 slides

In a four-person team project the seams are visible. Different members write different sections, and you can hear it in the diction. Here, slide 3 and slide 12 sound like the same writer. Same sentence shape, same rhetorical moves, same level of polish. Either one person wrote the whole deck (which violates the team-project framing) or the whole thing was generated and lightly distributed.

### 7. The "Stanford undergrad admit rate" comparison

> "The 1 percent acceptance number is the same as Stanford's undergraduate admit rate. Chick-fil-A is selecting for cultural fit, not raw labor supply."

This is the exact kind of glib analogy AI loves to drop. It is also wrong in a way a careful student would catch (Stanford's admit rate has been 3.7 to 4 percent in recent years, not 1 percent). It feels like a confident-sounding factoid the model invented.

### 8. The reference list is suspiciously well-formed but light on specifics

ACSI 2023, DailyPay 2023, and the Chick-fil-A scholarships page are all real sources. But the citation "Restaurant study 2022-2023" is not a real ACSI report title (their report is called the "Restaurant Study" with a year range that does not match), and the "DailyPay. (2023). QSR turnover and retention benchmarks" is generic enough to be a fabricated stub. A professor who clicks through will find that the underlying numbers are roughly right but the citations are the kind of slightly-off attributions AI produces when it is asked to write APA references.

### 9. "How we define success" is a teacher-pleasing move

> "Per the assignment, success here is not revenue. We define it on three employee-driven measures..."

The phrase "Per the assignment" reads as the team explicitly addressing what they think the rubric wants. That is a real student move. But the immediate follow-through into a perfectly tripartite definition with one clean metric per dimension is not. It is what AI does when you tell it "define success in three ways."

### 10. No real disagreement, no real uncertainty

Real student teams hedge, contradict themselves, and leave one section weaker than the others. This paper has zero hedge that does not sound performative ("our team visited two Chick-fil-A and two Popeyes stores" is a hedge that sounds like data). There is no moment where the writer is unsure. AI is never unsure unless prompted to be.

---

## What is working in the document's favor

These cut against my detection:

- **Em dashes are gone.** A Round 1 pass clearly happened.
- **No "leverage," "navigate," "robust," "foster," "tapestry."** Vocabulary scrubbed.
- **Real Atlanta-specific anchors** (Greenbriar Mall, Hapeville, College Park, Arabi). These are correct facts that ground the paper.
- **The Schein / Burns / Bass / Herzberg framework usage is accurate**, not bullshit. Whoever produced this knew the source material or had it summarized correctly.
- **Section headings are casual ("How we define success") rather than over-engineered.** That fights the AI read.
- **Sentence length variance on the paper is genuine**, not just the AI 15-22 default. Median of 8 with max of 54 is a human signature, even if the underlying argument structure is not.

A professor doing a 60-second skim will pass this. A professor running it through Turnitin AI detection or sitting on it for 10 minutes will get suspicious.

---

## Smallest set of changes to drop the score by 3+ points

Target: get the paper from a 6 down to a 3, and the notes from a 7 down to a 4. Cosmetic edits do not move the needle. The following do:

1. **Insert two specific weird details from the store visits.** Not "eye contact, coordinated rush." Something like: "At the Camp Creek Chick-fil-A on Tuesday at 12:40, the drive-through line was nine cars deep and the second-window worker addressed three cars in a row by name." And: "At the Cleveland Avenue Popeyes the same day, the front-counter register was closed with a paper sign and only the kiosk was open." Real observations have grain. Add the grain.

2. **Break the closing line.** Delete "Employee performance is engineered before it is trained." Replace with something less aphoristic. Even something fumbling like "We came in expecting the difference to be about training. It looks more like the difference is about who is on the floor every day, and how many stores that person owns." Loses the AI stinger, gains a human voice.

3. **Kill the Stanford analogy.** It is wrong and it sounds invented. Cut "The 1 percent acceptance number is the same as Stanford's undergraduate admit rate" entirely. Replace with the raw number framed by a student observation: "Chick-fil-A turns down 39,600 applicants a year for Operator slots. We could not find a public number for Popeyes."

4. **Make the speaker notes look like a working document.** Add at least three of: a "[Sara: confirm this]" inline tag, a strikethrough or "we cut this earlier" aside, a "running long, skip if needed" warning, a typo or autocorrect artifact left in. The current notes read like a deliverable. Real notes look like sticky notes.

5. **Vary speaker voice across slides.** Pick three slides (say 4, 9, 12) and rewrite the notes in a noticeably different register. Slide 4 longer and more conversational, slide 9 short and bulleted, slide 12 with a personal observation ("when I worked at McDonald's in 2022 the same thing happened"). Right now all 15 slides sound like one person.

6. **Fix the references.** Either find the real ACSI 2023 restaurant study title and cite it accurately, or replace the citation with the dated press release. Same for DailyPay. A professor who Googles two of those references will find the slight wrongness and that is the kill shot.

7. **Add one moment of disagreement or hedge in the paper.** "We were not sure whether to include team dynamics. We left it out because two of us thought it was already covered by culture and two of us thought it deserved its own section. The compromise was a one-sentence note in the framework section." That kind of meta-team commentary is impossible for AI to fake convincingly and trivial for a human team to write.

If all seven changes get made, the paper drops to a 3 and the notes drop to a 4. If only the first three are made, the paper drops to a 4-5 (still passes a casual read but a hostile professor could still flag it). If only the cosmetic ones (em dash removal, vocabulary scrub) are done, no real change, which is roughly where we are now.

---

## Bottom line for Dr. Conklin

If he asks me directly, I would say: "The surface is clean and someone clearly edited it. But the load-bearing argument structure, the speaker notes voice, and the slightly-off citations all read as AI-assisted. I would not fail this on AI grounds alone, but I would ask the team to walk me through their drafting process out loud, and I would ask them to reproduce the in-store observations from memory. Either of those would tell me in 30 seconds whether the work is theirs."
