# ARTICULATION: 12 Talking-Point Drills

Each answer is in his voice, plain senior-engineer tone, 60 to 120 seconds spoken. Practice these out loud, not just on the page. Time yourself. The point is not memorization; it is having the structure ready so the words come out clean when adrenaline hits.

---

## 1. "Walk me through how you threat model"

(75 seconds)

> "I run seven phases. First I clarify scope: what we are protecting, who the actors are, what data classes flow. I write those on the board so we are solving the same problem. Second I draw a level-zero data flow diagram with external entities, processes, data stores, flows, and dashed lines for trust boundaries. Third I walk every trust boundary and apply STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. For ML systems I overlay MITRE ATLAS at the same time, especially prompt injection and excessive agency. Fourth I rank threats with a simple high-medium-low matrix because DREAD invents precision that is not really there. Fifth I propose mitigations, primary control plus compensating control plus tradeoff. Sixth I state residual risk explicitly with counts and rationale. Seventh I propose detection for every High and Medium so if a mitigation fails we know. The whole loop runs in 25 to 30 minutes. The discipline is to not skip residual risk, because that is where senior signal is."

---

## 2. "What is the difference between STRIDE and PASTA"

(60 seconds)

> "STRIDE is component-driven. You enumerate the system, then you ask the same six questions at every interface. It produces engineering-actionable output and you can run it in under an hour. PASTA is business-driven. It is seven stages that start from business objectives, decompose the application, then move to threat analysis and attack modeling, and end with risk and impact in dollars. STRIDE is the right tool for a sprint planning session. PASTA is the right tool when the threat model itself has to defend a business case to a CFO or a board. I reach for STRIDE first on every system. I run PASTA when the audience is non-technical executives or when the artifact must satisfy a regulatory framework like SOC 2 or HITRUST."

---

## 3. "How do you prioritize threats"

(60 seconds)

> "I use likelihood times impact, three by three matrix, high, medium, low. I avoid DREAD scoring with decimals because the precision is fake. The number 7.4 does not mean anything more than 'high'. Likelihood I anchor to attacker capability and existing controls. Impact I anchor to business consequence: data breach class, regulatory exposure, dollar impact, customer trust. Anything in the high-impact column with high or medium likelihood goes in the must-fix bucket. Lows get an acceptance rationale in writing. Two pieces of nuance: I never let a single threat sit at high without a named owner and a target date, and I revisit the matrix after I see real telemetry, because predicted likelihood is wrong about half the time."

---

## 4. "Tell me about a threat you found and how you mitigated it"

(90 seconds, this is his real story)

> "I run an autonomous agent on my own infrastructure. It has tool access to Notion, Gumroad, GitHub, and Gmail. When I threat-modeled it, I realized the LLM was a confused deputy. Anyone who could get text into its context, including via a poisoned email or a Telegram message, could potentially make it call a tool. The model itself was not authorizing anything. The threat I named was AML.T0048 external harms via prompt injection, residual rated high. The fix I shipped: I built a tool router that sits between the LLM and the actual tools. Every tool call goes through a per-skill allow-list, every irreversible action requires human approval through Telegram, and every action is rate-limited per workflow run. The LLM can plan whatever it wants. What it can execute is bounded by the router. The residual dropped from high to medium because the remaining surface is plan-level mischief, not action-level damage. I also added a critique loop that flags severity inconsistency between the alert content and the proposed action. That is what I would do for any agentic system: never trust the LLM to enforce authorization, put authorization in the tool router."

---

## 5. "What is residual risk and how do you communicate it"

(75 seconds)

> "Residual risk is what is left after controls are in place. It is the honest answer to 'are we shipping with a known gap, and if so why'. I communicate it in three dimensions: severity, ownership, acceptance. Severity is high, medium, or low. Ownership is a named person who can speak to it. Acceptance is a written rationale that holds up to scrutiny. So instead of saying 'we have residual risk in the auth layer', I say 'medium residual risk on session-fixation, accepted because we have short token TTL and anomaly detection on geo-velocity, owned by the platform team, reviewed quarterly'. To executives I translate severity into business terms: number of users at risk, dollar exposure, regulatory class. I never give a residual rating without an acceptance line attached. If I cannot defend the acceptance, the threat is not residual, it is unfixed."

---

## 6. "How does threat modeling change for AI systems"

(90 seconds)

> "Three things change. First, the trust boundaries shift. In a classical web app the boundary that matters most is internet-to-app. In an LLM system the boundaries that matter most are user-input-to-prompt, retrieved-document-to-context, and LLM-output-to-downstream-interpreter. The third one is where prompt injection becomes RCE. Second, you must overlay MITRE ATLAS on top of STRIDE because some threats do not exist in classical models: prompt injection, training data poisoning, model extraction, embedding inversion, excessive agency. ATLAS gives you techniques like AML.T0051 and AML.T0024 that map to specific defenses. Third, the concept of a confused deputy becomes the central pattern. The LLM has authority but does not have judgment. Every tool call must be authorized by something that is not the LLM. Every retrieved chunk is untrusted input. Every output is rendered in a sandbox before any downstream system consumes it. So the framework I run is STRIDE plus ATLAS at every boundary, with extra emphasis on output handling and tool authorization. The residual risk on prompt injection is currently medium for everyone. There is no perfect class of defense. Layers and humans-in-the-loop on irreversible actions are the realistic posture."

---

## 7. "What would you do differently if you had to threat model with no documentation"

(75 seconds)

> "Documentation is a nice-to-have, not a requirement. Threat modeling is a conversation, not a literature review. With no docs I start with the people. I ask the lead engineer to whiteboard the system from memory, level zero in eight minutes. The gaps in their drawing are the first signal of where threats hide. Then I trace one happy-path request from user to data store and back, narrating out loud, asking 'where does the trust change' at every hop. That gives me the boundaries. Then I run STRIDE at each boundary while the engineer is still in the room, because they know which controls actually exist versus what is on the wiki. I capture assumptions explicitly because in a no-doc environment most threats live in unstated assumptions. Output is a one-page DFD with boundaries, ten to fifteen ranked threats, mitigations for the top five, and a list of questions I could not answer in the room. That last list is often more useful than the threat list itself."

---

## 8. "What is your favorite threat modeling framework"

(45 seconds)

> "STRIDE for the daily work, plus ATLAS overlay on AI surfaces. STRIDE because it is fast, repeatable, and produces output engineering teams will actually act on. ATLAS because it forces you to think about ML-specific threats classical models miss. PASTA when I need to defend a business case. OCTAVE Allegro when I am supporting a SOC 2 or HITRUST audit. The framework matters less than the discipline. Same person, different system, different framework, mostly the same threats fall out. The framework is how I make sure I do not miss a category."

---

## 9. "How do you know when a threat model is done"

(60 seconds)

> "Two answers. First, never. A threat model is a snapshot of a moving system. I revisit on every architectural change, every new dependency, every new data class, and at minimum quarterly. Second, for any single session, I call it done when three things hold: every trust boundary has been walked, every high-impact threat has a named control or a written acceptance, and the residual risk has been signed off by someone with the authority to accept it. If any of those three is missing the model is not done, it is just unfinished. The deliverable is not the diagram, it is the decisions captured. That is what I treat as the artifact."

---

## 10. "Describe a time you disagreed with engineering on a threat"

(75 seconds)

> "On my own stack I had a debate with myself, which is the same conversation I have had with engineers. I had a feature flag service that could disable payments. The engineer argument was 'this is internal, behind SSO, the blast radius does not justify a two-person rule'. The threat-modeling argument was 'one click can take production payments offline, that is a HIGH impact action no matter how low the likelihood'. I held the line. The compromise was that toggle changes on payment-related flags require a second approver, while everything else stays single-click. The engineer was unhappy at first. Two months later we had a sleep-deprived deploy where someone almost flipped the wrong flag, the second-approver dialog caught it, and the engineer agreed it was the right call. Senior threat modeling is about defending controls that feel like friction in the moment but pay back later. I lead with impact, not with categorical rules."

---

## 11. "What is the most common threat modeling mistake"

(60 seconds)

> "Listing controls instead of threats. People say 'we have WAF, we have MFA, we have logging' and call that a threat model. That is a control inventory. A threat model says 'an attacker could do X at boundary Y, the consequence is Z, the control we have is W, the residual is R'. The second most common mistake is skipping residual risk. Teams enumerate threats, propose mitigations, and stop. They never write down what is left and why. That means the next quarter someone re-discovers the same risks and assumes they are new. Third common mistake is not redrawing the diagram when the architecture changes. The threat model is a living artifact. Stale diagrams are worse than no diagrams because they create false confidence."

---

## 12. "How would you teach threat modeling to a junior engineer"

(75 seconds)

> "I would not start with frameworks. I would start with a real system on a whiteboard and one prompt: where would an attacker put their effort if they wanted to break this. We would draw the system together, level zero, eight minutes. Then I would walk one boundary with them, asking the six STRIDE questions, and let them answer. The next boundary they walk alone. By the third boundary they have the rhythm. The framework comes later as a memory aid. I would also teach them to write the residual risk in plain language for an executive audience, because forcing yourself to translate technical findings into business impact is how you stop being junior. Last piece: I would make them threat model their own personal stack, the way I threat-modeled mine. Once you have done it for something you actually own, you understand why the discipline exists."

---

## Drill protocol

For each of the 12, do this:
1. Read it aloud at speaking pace. Time yourself.
2. Cover the page and try to repeat from memory. Aim for the first sentence verbatim and the structure intact.
3. Record yourself on phone. Listen back for AI-writing patterns, throat clearing, hedge words.
4. Re-do until you can hit it cold under three takes.

The opening sentence of each is the most important. Memorize those nine sentences cold, even if the body varies.
