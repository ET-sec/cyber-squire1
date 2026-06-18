# Verified Learning Resources — AI Security Engineer Track

Best-of-class resources for each topic, verified by reputation and direct check May 2026. Each entry: URL, free or paid, time estimate, level, and an honest verified-as-good note. Marked [UNVERIFIED] where reputation is solid but URL/pricing not directly confirmed in this session.

Time estimates are for absorbing the resource sufficiently to defend it in an interview. Mastery requires applying it, not just consuming it.

---

## Python (interview-ready, not language-mastery)

### Real Python
- URL: https://realpython.com/
- Cost: Free tier extensive; Premium ~$20/mo
- Time: 10–20 hours for the topics that matter (async, type hints, dataclasses, pytest)
- Level: Beginner to intermediate
- Verified: Tier-1 reputation in the Python community since 2014. Tutorials are technically accurate, well-edited, and senior-engineer reviewed.

### Fluent Python (2nd ed.) — Luciano Ramalho
- URL: https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/
- Cost: $50 print, free with O'Reilly subscription
- Time: 30+ hours to read; reference for life
- Level: Intermediate to advanced
- Verified: The reference Python book for senior engineers. Author is a Python Software Foundation fellow. Skip the parts you don't need (descriptors, metaclasses); read the async, dataclass, typing, and iterator chapters.

### Python Crash Course (3rd ed.) — Eric Matthes
- URL: https://nostarch.com/python-crash-course-3rd-edition
- Cost: $45 print
- Time: 15–20 hours
- Level: Beginner
- Verified: Most-recommended starter book for absolute Python beginners. Project-driven approach matches ADHD learning style well. Skip if Python basics are already in hand.

---

## LangChain / LangGraph

### Official LangGraph docs
- URL: https://langchain-ai.github.io/langgraph/
- Cost: Free
- Time: 5–10 hours for the core concepts (state, nodes, edges, checkpointers, persistence)
- Level: Intermediate (assumes Python + async)
- Verified: Primary source. LangGraph 1.0 GA in October 2025 means the docs are stable and recent. Read these before any third-party tutorial.

### DeepLearning.ai short courses (with LangChain/LangGraph)
- URL: https://www.deeplearning.ai/short-courses/
- Cost: Free
- Time: 1–2 hours per course
- Level: Beginner to intermediate
- Verified: Andrew Ng's outfit, partnered directly with LangChain founders. The "AI Agents in LangGraph" and "Functions Tools and Agents" courses are the highest-leverage starting points.

### James Briggs YouTube
- URL: https://www.youtube.com/@jamesbriggs
- Cost: Free
- Time: pick episodes as needed
- Level: Beginner to intermediate
- Verified: One of the cleaner LangChain/LangGraph educators on YouTube. Updates content as APIs change. Useful for visualizing what the docs explain in text.

---

## AWS Security

### AWS Skill Builder
- URL: https://skillbuilder.aws/
- Cost: Free tier extensive; Subscription tier ~$29/mo for hands-on labs
- Time: 10+ hours for the security learning paths
- Level: Beginner to advanced
- Verified: AWS's own training. The Security Engineer learning path and Security Specialty exam prep are credible. Skip the marketing courses, focus on the technical labs.

### Stratus Red Team (DataDog)
- URL: https://stratus-red-team.cloud/
- Cost: Free
- Time: 5–10 hours to run all scenarios
- Level: Intermediate
- Verified: Open-source AWS/Azure/GCP attack emulation. Each technique maps to ATT&CK. Used by detection engineers to validate alerting. Run it against your own lab account before discussing in interviews.

### flAWS challenges
- URL: https://flaws.cloud/ and https://flaws2.cloud/
- Cost: Free
- Time: 4–8 hours for flaws.cloud, 6–10 hours for flaws2.cloud (attacker + defender tracks)
- Level: Beginner to intermediate
- Verified: Created by Scott Piper, the gold-standard AWS-pentest-by-puzzle CTF. Universally cited in cloud security learning paths.

### CloudGoat (Rhino Security Labs)
- URL: https://github.com/RhinoSecurityLabs/cloudgoat
- Cost: Free (your AWS account costs apply, ~$5–20/scenario if cleaned up promptly)
- Time: 1–2 hours per scenario, 20+ scenarios
- Level: Intermediate
- Verified: Terraform-deployed vulnerable AWS scenarios. Same authors as Pacu. Pair with Pacu for a complete attack workflow.

---

## AI Security

### Hugging Face — Safety / Red Teaming courses
- URL: https://huggingface.co/learn
- Cost: Free
- Time: 4–8 hours per course
- Level: Beginner to intermediate
- Verified: Hugging Face's official courses are well-written and current. The Audio, NLP, and Diffusion courses include security considerations; check the dedicated red-teaming material as it's added.

### Anthropic published guides and research
- URLs: https://www.anthropic.com/research, https://alignment.anthropic.com/, https://docs.claude.com/
- Cost: Free
- Time: pick papers as needed
- Level: Intermediate to advanced
- Verified: Primary sources. Read Sleeper Agents (arXiv 2401.05566), Constitutional AI (arXiv 2212.08073), and the Constitutional Classifiers writeup. Cite by name in interviews.

### OWASP AI Verification Standard / AI Exchange
- URLs: https://owasp.org/www-project-ai-security-and-privacy-guide/ and https://owaspai.org/
- Cost: Free
- Time: 5–10 hours to absorb the threat catalog
- Level: Intermediate
- Verified: Primary source for AI threats and controls. Feeds ISO/IEC 27090 and EU AI Act conformance work.

### Promptfoo + Garak hands-on
- URLs: https://www.promptfoo.dev/docs and https://github.com/NVIDIA/garak
- Cost: Free
- Time: 10–20 hours to run a full red-team against a toy LLM agent
- Level: Intermediate
- Verified: The two open-source tools that AI Security Engineers actually run on the job. Build a vulnerable LangGraph agent, scan it with Garak, eval it with Promptfoo, document the findings. That artifact is interview gold.

---

## Threat Modeling

### Adam Shostack — "Threat Modeling: Designing for Security"
- URL: https://shostack.org/books/threat-modeling-book
- Cost: ~$50 print, free with O'Reilly subscription
- Time: 20+ hours
- Level: Beginner to advanced
- Verified: The reference threat modeling book. Shostack ran threat modeling at Microsoft and authored the STRIDE methodology documentation. Cite in any threat-model interview.

### Threat Modeling Manifesto
- URL: https://www.threatmodelingmanifesto.org/
- Cost: Free
- Time: 30 minutes
- Level: All
- Verified: Co-authored by Shostack and other senior practitioners. Single page. Read before any threat modeling interview to align vocabulary.

### OWASP Threat Modeling Project + threagile + pytm
- URLs: https://owasp.org/www-community/Threat_Modeling, https://github.com/Threagile/threagile, https://github.com/izar/pytm
- Cost: Free
- Time: 5–10 hours
- Level: Intermediate
- Verified: pytm is the practitioner's tool for code-as-threat-model. threagile is the YAML-driven equivalent. Both produce actual reports, useful as portfolio artifacts.

---

## Pentesting and Web Security

### PortSwigger Web Security Academy
- URL: https://portswigger.net/web-security
- Cost: Free
- Time: 100+ hours for full track; pick topics for 20–30 hours
- Level: Beginner to advanced
- Verified: Industry consensus best free web security training. Authored by the team behind Burp Suite. Lab-driven, every topic ends in a live exploit. Universally recommended by AppSec hiring managers.

### HackTheBox AI/ML modules
- URL: https://academy.hackthebox.com/
- Cost: Tiered subscriptions; free trial available
- Time: 5–15 hours per module
- Level: Intermediate
- Verified: HTB Academy added AI/ML security modules in 2024–2026 covering prompt injection, model extraction, supply chain. Quality varies by module; the prompt-injection and adversarial-ML modules are the strongest.

### TryHackMe AI tracks
- URL: https://tryhackme.com/
- Cost: Free tier extensive; Premium ~$15/mo
- Time: 5–15 hours per path
- Level: Beginner
- Verified: More beginner-friendly than HTB. Good for fast onboarding to AI security concepts. Less depth than HTB or PortSwigger.

---

## Detection, Triage, SOC

### SOC Prime Threat Detection Marketplace
- URL: https://socprime.com/
- Cost: Free tier (limited rules), paid tiers
- Time: pick rules as needed
- Level: Intermediate
- Verified: Largest commercial Sigma rule marketplace. Free tier gives you access to community-contributed rules. Useful for studying real detection logic.

### BlueTeamLabs.online
- URL: https://blueteamlabs.online/
- Cost: Free tier; Premium ~$20/mo
- Time: 1–4 hours per challenge
- Level: Beginner to intermediate
- Verified: Hands-on blue team challenges. Network forensics, malware analysis, IR scenarios. Good for building investigative reps.

### LetsDefend
- URL: https://letsdefend.io/
- Cost: Free tier; Premium ~$25/mo
- Time: 2–6 hours per case
- Level: Beginner to intermediate
- Verified: SOC analyst simulator with real-feeling alerts and investigation workflows. Stronger on Tier-1/Tier-2 SOC practice than on engineering.

---

## Quick "start here" path

For a candidate compressed on time, this is the order that maximizes interview-defensible signal in 4–8 weeks:

1. PortSwigger Web Security Academy — XSS, SQLi, BOLA, BFLA, SSRF chapters (10 hours)
2. flaws.cloud + flaws2.cloud — both tracks (12 hours)
3. CloudGoat one or two scenarios with Pacu (8 hours)
4. Build a LangGraph agent + Garak it + Promptfoo eval it (15 hours)
5. Read OWASP LLM Top 10, MCP Top 10, ATLAS top 10 techniques (4 hours)
6. Read Shostack's threat modeling book chapters 1–6 (8 hours)
7. Skim NIST AI 600-1 GenAI Profile (3 hours)
8. Anki everything as you go (10 min/day, ongoing)

That is roughly 60 hours of high-leverage work plus daily Anki. At 2 sprint cycles per day (90 minutes each, 5 days/week), it fits in 7–8 weeks. The artifact in step 4 becomes the resume centerpiece.
