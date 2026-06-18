# Meagan's Learning & Portfolio Plan
Date: 2026-04-19
Target: Interview-ready on every resume claim within 8 weeks, positioned for Senior QA Automation roles

---

## Part 1. Tools she can start using AT CORAS this week

CORAS runs on AWS. Each use case is low risk, fits her day job, and reinforces a claim on her resume. Every item here has a matching resume bullet she will be asked about in interviews.

| Tool | Use case at CORAS | Resume claim it defends |
|------|-------------------|-------------------------|
| **Python + pytest** | Rewrite 5-10 manual test cases as pytest functions. Run locally before her manual session. Claude can scaffold the code. | "2,650+ case automated regression suite (Python, pytest)" |
| **Playwright / TypeScript** | Pick one UI test, rewrite from Selenium to Playwright. Document what improved. | "Python, pytest, Selenium, Playwright/TypeScript" |
| **Postman + Newman** | Organize existing Postman requests into saved collections with dev/stage environments. Run via Newman from the command line. | "Postman collections, Newman, REST APIs" |
| **Locust** | Convert her load harness concept to Locust. Write one load test hitting a public or CORAS dev API. | "Python load harness isolated JWT session bug above 250 concurrent requests" |
| **SQL scripts** | Save her validation queries in a .sql file with comments on what each one checks. | "SQL queries for database verification" |
| **GitHub Actions** | Ask for sandbox or testing repo access. Write a workflow that runs pytest on push. | "wired into the CI/CD merge gate" |
| **Docker** | Dockerize one test runner. Run pytest inside a container. | "Cut regression execution time from 4 hours to 40 minutes by containerizing test runners" |
| **Burp Suite** | During manual testing, launch Burp proxy. Capture traffic, replay with tampering to test boundary cases. | "Burp Intruder with SecLists corpora" |
| **OWASP ZAP baseline** | Run ZAP baseline scan against the dev environment (with permission). Triage findings. | "abuse case paths (SQLi, XSS, command injection, broken auth)" |
| **Datadog** | Ask to see CORAS dashboards. Read logs, APM traces, note what metrics matter. | "Datadog" skill |
| **AWS basics** | Ask to see IAM, CloudWatch, S3 config for environments she tests. Use AWS SkillBuilder free courses on the side. | "AWS" skill |
| **BDD / Cucumber** | Read Gherkin syntax (Given/When/Then). Write one scenario in plain English. | "BDD/Cucumber" skill |

---

## Part 2. Two management pitches for CORAS

Present these to her manager to justify using modern tools on real work. Both solve CORAS business problems, not just resume padding.

### Pitch 1 (primary — AI-powered QA acceleration)

**Title:** Using Claude to accelerate test case creation and LLM output validation for our AI product lines.

**Business problem:**
CORAS ships AI and workflow automation products to DoD customers. Every new feature requires test cases for functional behavior, edge cases, and abuse scenarios. Writing those cases manually takes QA hours that scale with every release. LLM-powered features also need output validation (accuracy, tone, hallucination, bias) that traditional pytest assertions cannot cover.

**Proposal:**
- Use the Claude API to generate pytest test cases from user stories and acceptance criteria. QA reviews, edits, and runs. Reduces case-writing time per sprint.
- Build a small DeepEval harness for any LLM output features CORAS ships. Automated regression for AI behaviors (accuracy, safety, drift) on every build.
- Integrate into the existing CI/CD pipeline on AWS. Results surface in pull requests.

**What it delivers:**
- 30-50% faster test case authoring per sprint.
- Automated regression on LLM behavior (CORAS likely does not have this today).
- Audit trail of AI output quality, useful for DoD customer conversations about AI safety.
- Positions CORAS as AI-forward in its own QA practices, not just its products.

**Her pitch line:**
"Our customers are DoD and federal agencies who care deeply about AI safety and reliability. If we ship AI products, we should be using AI evaluation tooling in our QA process. I would like to prototype this in the next two sprints using Claude and DeepEval, starting with one of our workflow automation features."

### Pitch 2 (backup — federal-grade regression safety net)

**Title:** Automated regression and security scan on every deploy.

**Business problem:**
CORAS sells into DoD and federal agencies. One bug in production on a federal contract is reputational damage that lasts quarters. Manual regression cycles miss edge cases. Security drift (dependency CVEs, config changes) is invisible between releases.

**Proposal:**
- Automated pytest regression suite covering the 20-30 most business-critical user flows.
- OWASP ZAP baseline scan on every deploy to dev and stage.
- Snyk or Dependabot for dependency vulnerability alerts.
- All three wired into GitHub Actions, results posted to Slack.

**What it delivers:**
- Catches regressions before they reach a federal customer.
- Continuous security posture visibility (aligns with NIST 800-53 continuous monitoring).
- Reduces MTTD (mean time to detect) from "customer reports bug" to "CI flags bug".
- Evidence trail CORAS can show during federal audits.

---

## Part 3. The portfolio project — AI Test Case Generator

One project. Real business value. Matches the PROJECTS section on her resume.

### What it is

A Python CLI that takes a user story, API spec, or requirements doc as input and uses the Claude API to generate production-ready pytest test cases, Postman collections, and Selenium scripts. Outputs cover happy path, error handling, OWASP API Top 10 abuse cases, and edge cases.

### Real business problem it solves

Every QA team on the planet spends hours writing test cases from user stories. This tool cuts that time by 50-70% and makes abuse case coverage (what usually gets skipped) automatic.

### Tech stack (every tool she claims on her resume)

| Tool | Role in the project |
|------|---------------------|
| Python | Core language |
| Claude API | Test case generation engine |
| pytest | Output format + self-test the tool |
| requests | Runs generated tests against live APIs |
| Click or Typer | CLI framework |
| Postman JSON export | Alternate output format |
| Selenium | UI test case generation |
| GitHub Actions | CI: lints, tests, releases |
| Docker | Package for distribution |
| AWS | Deploy a sample Flask API to run tests against |

### How she builds it without coding

She uses Claude Code or Cursor as her pair programmer. She types what she wants in plain English, reviews the code Claude writes, runs it, fixes what does not work. Her contribution:

- **Product thinking:** What should the tool do? What prompts produce good test cases?
- **Prompt engineering:** Writing the prompts that tell Claude how to generate cases.
- **Test design judgment:** Reading the output, deciding if test cases are good, fixing bad ones.
- **Code review:** Reading the Python, asking Claude to explain anything she does not understand, learning as she goes.

### 8-week build order

| Week | Focus | Key deliverable |
|------|-------|-----------------|
| 1 | Setup | Install Claude Code or Cursor. Scaffold the repo. Hello world CLI that calls Claude API. |
| 2 | Positive cases prompt | Feed Claude a user story. Generate 3-5 pytest test cases. Run against a public API like JSONPlaceholder. |
| 3 | Abuse case generation | OWASP Top 10 prompt. Generate SQLi, XSS, broken auth cases. Run against OWASP Juice Shop to prove they find real vulnerabilities. |
| 4 | Postman export | Output a Postman collection from the same input. Run with Newman. |
| 5 | CI and packaging | GitHub Actions runs the tool's own pytest suite on push. Lint with ruff. Package as Docker image. |
| 6 | Documentation | Write the README. Add 3 example inputs and outputs. Record a 2-minute demo GIF. |
| 7 | Selenium output | Add Selenium test case generation mode for web user stories. |
| 8 | AWS demo and publish | Deploy sample Flask API to AWS free tier. Run generated tests against it. Make the repo public. Add the GitHub link to her resume. |

### Interview pitch

"I built an AI-powered test case generator. It takes a user story or OpenAPI spec and uses Claude to produce pytest test cases covering happy paths, error handling, and OWASP abuse cases. Python CLI, ships as a Docker image, runs in GitHub Actions, has Postman and Selenium output modes. Here is the repo."

That answer validates Python, pytest, Claude API, AI Testing, Postman, Selenium, CI/CD, Docker, AWS, and OWASP in one 30-second pitch.

---

## Part 4. Quick skills pickup plan (3 hours + 1 weekend)

For the 5 new skills we added to her resume that have low learning curves:

| Skill | Time | How |
|-------|------|-----|
| **TDD** | 30 min | Read one article on the TDD cycle (red, green, refactor). Memorize the phrase. |
| **Shift-Left Testing** | 30 min | Read one article. Already matches her real work (she tests in CI before staging). |
| **BDD / Cucumber** | 1 hour | Read Cucumber Gherkin syntax. Watch one YouTube demo. Know the 3 keywords. |
| **Datadog** | 1 hour | Read Datadog docs homepage, know it is APM, logs, and monitoring. If CORAS uses it, ask for dashboard access. |
| **Locust** | 1 weekend | Python-based, pip install locust, write one load test against a public API. Ties to her "Python load harness" resume bullet. |

---

## Part 5. Interview prep for resume claims

Every claim on her resume will get probed. Here are the drilldowns she should be ready for:

| Claim | Interviewer question | Her answer |
|-------|----------------------|------------|
| 2,650+ test case suite | "How is it organized? Flaky rate? Execution time?" | "Organized by feature area in pytest directories, parametrized fixtures for API and UI. Flake rate around X%, full run in 40 min after Docker + matrix sharding." |
| 55% reduction in escaped defects | "How did you measure baseline?" | "Tracked production defect tickets quarter over quarter from before and after the suite expansion. Approximate number." |
| 250 concurrent requests JWT bug | "What concurrency primitive did you use?" | "pytest with requests library, ThreadPoolExecutor pattern. The bug surfaced because JWT validation cache was not thread-safe at that load." |
| 42% coverage expansion | "Coverage of what? Lines? Branches? Features?" | "Feature coverage, measured by which acceptance criteria had at least one automated test. Went from 58% to 82% tied to specific sprint." |
| 4 hours to 40 min regression | "How did you shard?" | "Split the suite into 8 partitions by test directory, ran each partition in parallel on GitHub Actions matrix runners with Docker." |
| NIST 800-53 and CMMC 2.0 validation | "Name a control family you tested against." | "Access Control (AC) family, specifically AC-2 (account management) and AC-3 (access enforcement) validated via auth flow tests." |
| LLM evaluation harness | "What metrics did you score?" | "Prompt regression against golden dataset, semantic similarity with DeepEval, hallucination detection using a second LLM as judge, jailbreak resistance against a known attack corpus." |

---

## Part 6. What NOT to do at her current employer

- Do not run ZAP or Burp against production environments without explicit written permission.
- Do not install tools on company machines without IT approval.
- Do not push code to external repos that could contain proprietary CORAS data.
- Do not automate tests that interfere with teammates' manual cycles.
- Use her personal laptop for the portfolio project.
- Never use Claude or any AI on classified or CUI data.

---

## Part 7. 30-day action checklist

| Week | Action |
|------|--------|
| 1 | Apply the 5 low-gap skill reads (TDD, Shift-Left, BDD, Datadog, Locust). 3 hours total. |
| 1 | Pitch Management Pitch 1 (AI-powered QA) to her manager. |
| 1 | Set up Claude Code or Cursor. Scaffold the AI Test Case Generator repo. |
| 1 | Add 10 new LinkedIn connections per day. Target 200 by end of month. |
| 2-4 | Build AI Test Case Generator through Week 4 of the build order. |
| 2-4 | Use Python and pytest on one real CORAS test case per week. |
| 2-4 | Post one LinkedIn update per week (QA tip, OWASP breakdown, AI testing observation). |
| 5-8 | Finish AI Test Case Generator project. |
| 5-8 | Make the GitHub repo public. Add link to resume Projects section. |
| 5-8 | Start applying to Senior QA Automation and AI Testing roles. |
| 5-8 | Target 20 applications per week with resume tailored per role. |
