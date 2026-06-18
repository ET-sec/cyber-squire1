# Real Python and LangGraph Interview Questions, 2026

Reference document. Reported coding interview questions for Security and AI Security
Engineer roles, surfaced from public sources. Each entry lists the question or pattern,
the company (if known), the source, the difficulty if reported, and the time limit if
reported. `[UNVERIFIED]` marks questions paraphrased from secondary blogs without a
direct primary source.

Sources draw from Glassdoor, Hacker News, Blind, Reddit, public interview-prep repos
on GitHub, and engineering blogs. URLs cited inline.

---

## 1. String, Dict, and Collections Manipulation

### Q1.1 Apache log subnet aggregation
- **Pattern:** Parse an Apache access log, group requests by /24 subnet and month,
  return the top 10 subnets per month.
- **Company:** Amazon
- **Source:** Glassdoor interview report.
  https://www.glassdoor.com/Interview/Write-some-code-to-parse-an-apache-log-file-grouping-requests-by-24-subnet-and-month-and-then-give-me-the-top-10-subnets-QTN_870803.htm
- **Difficulty:** Medium. Tests `collections.Counter`, `defaultdict`, IP slicing, date
  parsing.
- **Evaluation:** Memory bound on a 5GB+ file. Streaming reads expected.

### Q1.2 Most popular URLs in a 5GB log
- **Pattern:** Given a 5GB access log, find the top 100 most-visited URLs.
- **Company:** Yelp
- **Source:** Glassdoor.
  https://www.glassdoor.com/Interview/We-have-a-fairly-large-log-file-about-5GB-Each-line-of-the-log-file-contains-an-url-which-a-user-has-visited-on-our-site-QTN_254050.htm
- **Difficulty:** Medium. Tests heap usage, streaming, memory ceiling reasoning.

### Q1.3 Character frequency interleave
- **Pattern:** Given a string, insert each character's frequency directly after that
  character in the output.
- **Company:** CrowdStrike
- **Source:** InterviewQuery CrowdStrike guide.
  https://www.interviewquery.com/interview-guides/crowdstrike-software-engineer
- **Difficulty:** Easy to Medium.

### Q1.4 is_subsequence
- **Pattern:** Return True if string1 appears in order (not necessarily contiguous)
  inside string2.
- **Company:** CrowdStrike
- **Source:** InterviewQuery.
  https://www.interviewquery.com/interview-guides/crowdstrike-software-engineer
- **Difficulty:** Easy. Two-pointer baseline expected.

### Q1.5 Sieve of Eratosthenes
- **Pattern:** Return all primes up to N efficiently.
- **Company:** CrowdStrike
- **Source:** Same as above.
- **Difficulty:** Easy. Tests willingness to choose Sieve over naive trial division.

### Q1.6 Recursive dice combinations
- **Pattern:** Generate all combinations of n dice with m faces, recursive.
- **Company:** CrowdStrike
- **Source:** Same as above.
- **Difficulty:** Medium. Tests recursion plus pruning.

### Q1.7 Reverse a linked list
- **Pattern:** Classic in-place reversal.
- **Company:** Cloudflare
- **Source:** InterviewQuery Cloudflare guide.
  https://www.interviewquery.com/interview-guides/cloudflare-software-engineer
- **Difficulty:** Easy. Iterative and recursive both expected.

### Q1.8 LRU cache from scratch
- **Pattern:** Design and implement an LRU cache. O(1) get and put.
- **Company:** Cloudflare
- **Source:** Same as above.
- **Difficulty:** Medium. Tests `OrderedDict` knowledge and the doubly linked list
  plus hash map pattern.

---

## 2. Log Parsing and Security Tooling

### Q2.1 Tail-and-extract security parser
- **Pattern:** Collect logs and write a parser that pulls out specific fields like
  domains, executable names, and timestamps.
- **Source:** gracenolan/Notes security engineering interview study guide.
  https://github.com/gracenolan/Notes/blob/master/interview-study-notes-for-security-engineering.md
- **Difficulty:** Medium. Tests regex discipline, datetime, and how the candidate
  handles malformed lines (skip vs raise vs route to dead-letter).
- **Evaluation:** Senior candidates ask about line ordering guarantees, log rotation,
  and how to handle structured (JSON) versus unstructured lines.

### Q2.2 Time-window log filter
- **Pattern:** Read an HTTP request log, return entries between two timestamps where
  status == 200.
- **Source:** Climb the Ladder log parsing question bank.
  https://climbtheladder.com/log-parsing-interview-questions/
- **Difficulty:** Easy.

### Q2.3 Cloudflare practical take-home
- **Pattern:** Build a log parser, a CLI tool, or a basic HTTP server end-to-end.
  Cloudflare runs realistic take-homes rather than pure whiteboarding.
- **Company:** Cloudflare
- **Source:** Cloudflare engineering interview blog.
  https://blog.cloudflare.com/cloudflare-interview-questions/ and InterviewQuery
  Cloudflare guide.
- **Difficulty:** Medium. Tests project hygiene, README quality, error handling, test
  coverage. Submitting a "main happy-path only" project is a common fail.

### Q2.4 Amazon security engineer scripting round
- **Pattern:** Write Python that converts log entries to a dictionary keyed for
  downstream investigation. Discuss tradeoffs.
- **Company:** Amazon
- **Source:** Yuva Surya Konatham, "What I learned from getting rejected by Amazon: a
  security engineer's interview experience."
  https://medium.com/@yuvasurya1998/what-i-learned-from-getting-rejected-by-amazon-a-security-engineers-interview-experience-293e65a2f942
- **Difficulty:** Medium. Tests not just the code but how the candidate explains
  scope and tradeoffs while typing.

---

## 3. Async and Concurrency

### Q3.1 What does `await` actually do
- **Pattern:** Walk through what happens when you `await` a coroutine. Describe how
  the event loop selects the next ready task and how `await` releases control.
- **Source:** dev.to asyncio interview questions and Real Python's asyncio quiz.
  https://dev.to/imsushant12/asyncio-interview-questions-and-practice-problems-3ode
  https://realpython.com/quizzes/async-io-python/
- **Difficulty:** Medium for senior. Tests if the candidate actually knows the runtime
  versus reciting "async makes things faster".

### Q3.2 GIL versus asyncio
- **Pattern:** Explain why asyncio bypasses the GIL for I/O-bound work but not
  CPU-bound work. When would you reach for `multiprocessing` or `concurrent.futures`?
- **Source:** SuperFastPython asyncio interview question set.
  https://superfastpython.com/python-asyncio-interview-questions/
- **Difficulty:** Medium. Tests whether the candidate understands that async is not a
  speed feature, it is a concurrency model for I/O.

### Q3.3 TaskGroup and structured concurrency
- **Pattern:** Refactor code that uses `asyncio.gather` with manual exception handling
  into Python 3.11 `asyncio.TaskGroup`. Explain why TaskGroup is safer.
- **Source:** dev.to asyncio interview questions.
- **Difficulty:** Medium. Tests modern Python knowledge and structured concurrency
  reasoning.

### Q3.4 Async rate-limited HTTP scanner
- **Pattern:** Build a scanner that fans out N async HTTP requests against a target
  list with a concurrency cap and a per-host rate limit. `[UNVERIFIED]` reported on
  multiple security take-home write-ups but no single canonical source.
- **Difficulty:** Medium. Tests `asyncio.Semaphore`, backoff, error budget reasoning.

---

## 4. Pydantic and Typing

### Q4.1 Validate untrusted JSON for an API endpoint
- **Pattern:** Given an API endpoint that accepts JSON from external clients, define
  a Pydantic model that validates the payload, rejects unknown fields, and enforces
  field-level constraints (length, regex, range). Discuss why Pydantic is preferred
  over hand-written `if/else` validation.
- **Source:** Pydantic LLM intro and FastAPI interview question banks.
  https://pydantic.dev/articles/llm-intro
  https://parikshapatr.com/interviews/backend-web-development-interview/fastapi-interview/fastapi-pydantic-models-interview-questions-and-answers
- **Difficulty:** Medium. Tests `model_config`, `extra="forbid"`, custom validators,
  and the security argument for whitelist-only validation.

### Q4.2 Constrain LLM output with a Pydantic schema
- **Pattern:** You are getting structured output back from an LLM and the model
  occasionally returns extra fields or wrong types. Define a Pydantic model and a
  retry policy that re-prompts the model when validation fails.
- **Source:** Pydantic for LLMs: Schema, Validation & Prompts.
  https://pydantic.dev/articles/llm-intro
- **Difficulty:** Senior. Tests the candidate's grasp of probabilistic outputs, the
  reason structured output matters for tool calls, and how to bound retries.

### Q4.3 Type a function whose return depends on input
- **Pattern:** Write `Generic`, `TypeVar`, and `Protocol` types so that a function
  that loads a model file returns the right concrete subclass based on the file
  extension. `[UNVERIFIED]` paraphrased from senior Python interview question banks.
- **Difficulty:** Senior. Tests knowledge of `mypy` strict mode, generics, and
  structural typing.

---

## 5. Classes and OOP

### Q5.1 Bank transaction system, four levels
- **Pattern:** Build a bank transaction system from scratch. Each level adds
  requirements (multi-account transfers, scheduled transactions, merge logic, audit).
  Code must absorb new requirements without collapsing.
- **Company:** Anthropic
- **Source:** interviewing.io Anthropic guide and LinkJob 2026 Anthropic question
  bank.
  https://interviewing.io/anthropic-interview-questions
  https://www.linkjob.ai/interview-questions/anthropic-coding-interview/
- **Time limit:** 90 minutes for the take-home, four progressively harder levels.
- **Evaluation:** Clean, modular code. Strong typing. Tests pass at every level.
  Anthropic explicitly looks for first-principles reasoning under added requirements,
  not memorized patterns.

### Q5.2 Web crawler (BFS)
- **Pattern:** Build a web crawler that starts from a seed URL, discovers and
  crawls all links on the same domain. Same-domain rule, dedupe, retry with backoff.
- **Company:** Anthropic
- **Source:** LinkJob 2026 Anthropic guide and IGotAnOffer.
  https://www.linkjob.ai/interview-questions/anthropic-coding-interview/
  https://igotanoffer.com/en/advice/anthropic-interview-questions
- **Difficulty:** Medium. Tests BFS, URL normalization, robots.txt awareness, async
  patterns.

### Q5.3 Design a Claude chat service
- **Pattern:** Design the class structure for a chat service. Conversation state,
  tool use, retries. Live system design with code-level discussion.
- **Company:** Anthropic
- **Source:** interviewing.io Anthropic guide.
- **Difficulty:** Senior.

---

## 6. LangGraph State Design

### Q6.1 Researcher plus Writer multi-agent graph
- **Pattern:** A Researcher agent gathers data, a Writer agent drafts a report.
  Choose the right graph structure: sequential, parallel, supervisor, swarm. Justify.
- **Source:** LangGraph interview question bank surfaced via LinkedIn community
  and GeeksforGeeks LangGraph guides.
  https://www.linkedin.com/posts/naved-khan-093167137_top-20-interview-questions-on-langgraph-activity-7404723324435619840-0QJ4
  https://www.geeksforgeeks.org/artificial-intelligence/building-ai-agents-using-langchain-and-langgraph/
- **Difficulty:** Senior. Tests StateGraph design, when to use a supervisor pattern,
  message passing semantics.

### Q6.2 Parallel branches modify the same state field
- **Pattern:** In a multi-agent LangGraph system two parallel branches both write to
  the same state field that has no reducer defined. What happens? How do you fix it?
- **Source:** Same LangGraph question bank.
- **Difficulty:** Senior. Tests knowledge of `Annotated` reducers, `add_messages`,
  custom merge functions, and why missing reducers cause silent overwrites.

### Q6.3 Define a TypedDict state schema for an investigation agent
- **Pattern:** Design the state schema for a SOC investigation agent. Fields for
  raw_alert, enriched_context, hypotheses, verdict, evidence_links. Decide which
  fields use reducers vs replacement semantics.
- **Source:** Pattern reported across LangGraph tutorials and Dropzone-style
  agent investigation references. `[UNVERIFIED]` precise question text varies by
  source.
- **Difficulty:** Senior. Tests typing rigor and reducer semantics.

### Q6.4 Conditional edges based on tool output
- **Pattern:** Implement a conditional edge that routes the graph to `human_review`
  if a tool returns low confidence and to `auto_remediate` if high. Show the edge
  function signature.
- **Source:** LangGraph official docs and GeeksforGeeks LangGraph build guide.
  https://www.geeksforgeeks.org/machine-learning/what-is-langgraph/
- **Difficulty:** Medium. Tests `add_conditional_edges`, return-string routing.

### Q6.5 Checkpointer and replay
- **Pattern:** A long-running agent crashes mid-run. How do you resume from the last
  successful step? Walk through `MemorySaver`, `PostgresSaver`, and `time travel`.
- **Source:** LangGraph documentation and rohanmistry231/Langchain-Interview-Preparation.
  https://github.com/rohanmistry231/Langchain-Interview-Preparation
- **Difficulty:** Senior. Tests durable execution reasoning, idempotent tool calls,
  and how checkpointers serialize state.

### Q6.6 Tool node with retries and circuit breaking
- **Pattern:** Wrap an external API call as a LangGraph tool node. Add retries with
  exponential backoff and a circuit breaker that stops calling on repeated failures.
- **Source:** LangChain tool calling docs and community Q&A.
- **Difficulty:** Medium to Senior.

### Q6.7 Human-in-the-loop interrupt
- **Pattern:** Use `interrupt` to pause the agent before a destructive action and
  return control to a human reviewer. Resume on approval.
- **Source:** LangGraph human-in-the-loop docs and rohanmistry231 prep repo.
- **Difficulty:** Medium. Tests safety by design, how interrupts persist via the
  checkpointer, and idempotency on resume.

### Q6.8 Memory and long-term context
- **Pattern:** Compare short-term checkpointer state vs long-term memory store. When
  do you store a summary in long-term memory and what triggers retrieval?
- **Source:** LangGraph memory docs.
- **Difficulty:** Senior.

---

## 7. Error Handling in Agents

### Q7.1 Tool returns an unexpected schema
- **Pattern:** A tool returns a dict that does not match what the agent expected.
  Should the agent retry, ask the user, or fail? Show the code path.
- **Source:** LangChain community discussions, paraphrased. `[UNVERIFIED]` exact
  wording varies.
- **Difficulty:** Senior. Tests defensive programming and the principle that LLM
  outputs and tool outputs both need validation.

### Q7.2 Recursion limit hit
- **Pattern:** Your LangGraph agent loops between two nodes and trips
  `GraphRecursionError`. Diagnose and fix.
- **Source:** LangGraph docs and community Q&A.
- **Difficulty:** Medium. Tests understanding of `recursion_limit`, when loops are
  legitimate (ReAct style) versus a bug, and how to add a termination condition.

### Q7.3 Async tool call timeout
- **Pattern:** A tool node hangs. Add a per-call timeout that cancels cleanly without
  leaking the underlying connection.
- **Source:** AsyncIO interview banks plus LangChain tool docs.
- **Difficulty:** Senior.

---

## 8. Prompt Injection Sanitization at the Code Level

### Q8.1 Sanitize a RAG retrieval before injecting into the prompt
- **Pattern:** Implement a function that takes retrieved document chunks and strips
  or escapes anything that looks like a prompt instruction. Discuss why escaping is
  not enough.
- **Source:** OpenAI prompt injection essay and Practical DevSecOps AI security
  question bank.
  https://openai.com/index/prompt-injections/
  https://www.practical-devsecops.com/ai-security-interview-questions/
- **Difficulty:** Senior. Strong answers say "escaping helps but the real fix is to
  treat retrieved content as untrusted data and design the prompt template so the
  model cannot follow instructions inside data." Weak answers reach for regex.

### Q8.2 Build an output validator
- **Pattern:** The LLM is asked for JSON. Build a validator that parses, repairs, and
  retries. Cap the retry count.
- **Source:** OWASP LLM Top 10 LLM05 (Improper Output Handling) guidance.
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- **Difficulty:** Medium.

### Q8.3 Detect indirect prompt injection in retrieved context
- **Pattern:** Write a classifier or rule set that flags retrieved chunks containing
  imperative-tone instructions, role-switching language, or tool-call attempts.
- **Source:** OWASP Gen AI Security project.
- **Difficulty:** Senior. Tests defense in depth: classifier plus prompt template
  design plus output filtering, not just one layer.

### Q8.4 Tool allowlist enforcement
- **Pattern:** An agent can call any tool the model picks. Add a runtime guard that
  enforces an allowlist per session and per user role. Show the wrapper.
- **Source:** Reversec design patterns and OWASP Excessive Agency (LLM08) guidance.
  https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
- **Difficulty:** Senior. Excessive Agency is one of the most common production
  failures, candidates who reach for this pattern unprompted signal seniority.

---

## 9. Reported Format Notes by Company

| Company | Format | Time | Source |
|---------|--------|------|--------|
| Anthropic | CodeSignal four-level OA, then live coding, system design, values | 90m OA + 60m rounds | interviewing.io |
| Cloudflare | Take-home (parser, CLI, or HTTP server) plus systems plus core CS | Varies, take-home typically 1 week | blog.cloudflare.com |
| CrowdStrike | One or two LeetCode-style problems plus systems plus distributed | 60m live coding | InterviewQuery |
| Snyk | Recruiter screen, hiring manager, technical, then 60m systems for senior | Multi-stage | Snyk engineering blog |
| Amazon Sec Eng | Phone screen, full loop with scripting, threat modeling, behavioral | 5 to 6 rounds | Yuva Surya Medium |
| Lakera | Screening plus two 45m technical interviews | 45m each | Glassdoor Lakera |
| Dropzone AI | Senior SWE codebase is Python, focus on production-grade code and agentic systems | Multi-stage | dropzone-ai/jobs Rippling |

---

## 10. Patterns to Drill Before a Top-Tier Round

The single most-asked Python interview pattern across this dataset is **streaming log
parsing with a top-N aggregation**. Variants appear at Amazon, Yelp, Cloudflare, and
across the security engineer study guides. Drill: open a multi-GB file as an iterator,
extract a tuple per line, fold into a `Counter`, return `most_common(N)`. Be ready
to discuss memory ceilings, malformed lines, and rotation.

The single most-asked LangGraph pattern is **state schema design with reducers and
conditional edges**. Drill: define a `TypedDict` state, mark which fields use
`add_messages` or a custom reducer, build a conditional edge function, attach a
checkpointer, and explain how a crash-and-resume works.

---

## Sources

- Glassdoor interview question reports (Amazon, Yelp, Cloudflare, CrowdStrike,
  Anthropic, Lakera, Snyk).
- interviewing.io Anthropic interview guide. https://interviewing.io/anthropic-interview-questions
- LinkJob 2026 Anthropic question banks.
  https://www.linkjob.ai/interview-questions/anthropic-coding-interview/
- IGotAnOffer Anthropic guide. https://igotanoffer.com/en/advice/anthropic-interview-questions
- Cloudflare engineering interview blog. https://blog.cloudflare.com/cloudflare-interview-questions/
- InterviewQuery Cloudflare and CrowdStrike guides.
- gracenolan/Notes security engineering interview study guide.
  https://github.com/gracenolan/Notes/blob/master/interview-study-notes-for-security-engineering.md
- Climb the Ladder log parsing question bank.
  https://climbtheladder.com/log-parsing-interview-questions/
- SuperFastPython and dev.to asyncio question banks.
- Pydantic LLM intro. https://pydantic.dev/articles/llm-intro
- LangGraph documentation and rohanmistry231/Langchain-Interview-Preparation.
  https://github.com/rohanmistry231/Langchain-Interview-Preparation
- Practical DevSecOps AI Security Interview Questions and Answers for 2026.
  https://www.practical-devsecops.com/ai-security-interview-questions/
- OWASP Gen AI Security Project. https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- Reversec design patterns to secure LLM agents.
  https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
- Yuva Surya Konatham Amazon security engineer interview write-up. Medium.
