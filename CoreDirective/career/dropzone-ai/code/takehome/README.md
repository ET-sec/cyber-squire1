# AWS Q&A Chatbot

A chatbot that answers plain English questions about an AWS account. Built
with LangChain tools wrapping boto3, and a Moto sandbox that simulates AWS so
runs stay local and reproducible.

## What it does

You ask in plain English, the agent calls the right AWS API, and answers.

```
Q: How many S3 buckets are exposed to the public?
A: You have 1 public S3 bucket out of 3 total. The public one is cd-prod-logs.

Q: What data does the S3 bucket tigoue-customers hold?
A: The bucket holds 2 objects: addresses.csv (33 bytes) and users.csv (47 bytes).

Q: What is the size of the EC2 instance with IP 10.0.1.42?
A: The instance is type t3.micro (name brand-web).

Q: What permissions does the user et-analyst have?
A: et-analyst has one managed policy (CDReadOnlyAccess) and one inline policy
   (RunbooksRead).
```

Examples above show the gist. Real runs produce longer markdown answers
because the model formats with bullets and bold. Moto generates a new
EC2 private IP each run, so Q3's IP will differ from the example. Full
transcript in `sample_output.txt`.

## How to run

Requires Python 3.11+ and a valid `ANTHROPIC_API_KEY`. Expect roughly
$0.02 to $0.05 per demo run (Sonnet 4.6 default, Opus 4.7 on escalation).

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY

# Scripted demo (runs all 4 sample questions):
./.venv/bin/python demo.py

# Interactive chat:
./.venv/bin/python main.py
```

## Architecture

```
main.py (chat REPL)  |  demo.py (scripted)
        |                    |
        +----------+---------+
                   |
           @mock_aws context
                   |
            moto_setup.populate_all()
                   |
            agent.build_router()
            (builds both agents below at startup via
             langchain.agents.create_agent, each
             bound to tools.ALL_TOOLS + system prompt)
                   |
        +----------+----------+
        |                     |
   Sonnet 4.6             Opus 4.7
   (default tier)         (escalation tier)
        |                     |
        +---------+-----------+
                  |
          agent.ask(router, question)
          picks tier by complexity; falls back
          to Opus on error or low confidence
                  |
            tools.ALL_TOOLS
                  |
          +-- count_public_s3_buckets()
          +-- list_s3_bucket_contents(bucket_name)
          +-- get_ec2_instance_by_ip(ip_address)
          +-- get_iam_user_permissions(username)
                  |
                boto3
                  |
             Moto mock
```

`ask()` picks the tier and invokes the chosen agent. The agent reads
the question, picks a tool, calls it, reads the result, and either
calls another tool or produces a final answer.

## Files

| File               | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `main.py`          | Interactive chat REPL                               |
| `demo.py`          | Scripted run of the four sample questions           |
| `agent.py`         | LangChain agent setup (LLM + prompt + tools)        |
| `tools.py`         | Four custom `@tool` functions wrapping boto3        |
| `moto_setup.py`    | Seeds the Moto sandbox with S3, EC2, IAM test data  |
| `requirements.txt` | Pinned dependencies                                 |
| `.env.example`     | Template for `ANTHROPIC_API_KEY`                    |
| `sample_output.txt`| Captured run of `demo.py`                           |

## Design decisions

**Moto over real AWS.** The brief allows it. Reviewer can run this with no
AWS account, no credentials, no cleanup. Every boto3 call works identically
against real AWS if the `@mock_aws` wrapper is removed.

**Router with a default and an escalation tier: Sonnet 4.6 by default,
Opus 4.7 on escalation, errors, or low confidence.** The router has three
triggers:

1. Complexity routing at entry: questions over 20 words or containing
   signals like "explain," "compare," "walk me through," "analyze,"
   or "deeply" go straight to Opus.
2. Error fallback: if Sonnet errors (API issue, token overrun), the
   question retries on Opus before returning to the user.
3. Confidence fallback: if Sonnet's answer contains uncertainty markers
   ("I am not sure," "I cannot determine," "unclear if"), the question
   runs again on Opus for a stronger answer.

All three sit in `agent.py:ask`. In production I'd replace the string-
matching confidence check with a structured confidence signal from the
model (response metadata or a scoring second pass), but the pattern is
the same.

**`create_agent` over a fixed chain.** A chain locks you into a fixed
tool order. The agent picks per question so it handles the natural
variation in how people phrase things. Cost: wrong tool picks on
ambiguous input, mitigated with `max_iterations` and tight tool
docstrings.

**Four narrow tools.** Narrow tools map 1:1 to the sample questions and
are easier for the LLM to select. One tool that handles everything pushes the work into
prompt engineering, which is harder to audit.

**`temperature=0`.** Reproducibility. Same question, same answer, every
run. Security work wants determinism, not creativity.

**Clients created inside each tool, not at module load.** If I created a
boto3 client at import time, it would bind to real AWS before `@mock_aws`
could intercept. Calling `boto3.client(...)` inside each tool keeps
everything inside the mock context.

**Input validation at the tool boundary.** Bucket names, IPs, and
usernames get a regex/`ipaddress` check before any boto3 call. Prevents
malformed input from reaching AWS APIs and gives the user a clear error.

See the Security posture section below for the full layered defense
story (question length cap, prompt injection guard, tools that only read).

## Security posture

**Threat model.** The agent reads AWS metadata. Primary threats: prompt
injection steering tool calls, hallucinated answers, cost amplification
from runaway tokens or tool calls, and secrets leakage through error paths.

**Defense layers:**

- Tools only read. No Create, Delete, or Put actions exist. A successful
  prompt injection has no destructive path to escalate into.
- Input validated at the tool boundary (regex for bucket names and IAM
  usernames, `ipaddress` for IPv4). Malformed input never reaches AWS.
- System prompt treats user input as untrusted and blocks instructions
  that try to change the agent's role.
- Question cap of 500 characters and routing by complexity stop cheap DoS
  and runaway token consumption.
- `ANTHROPIC_API_KEY` loads from `.env` (gitignored). Tool errors return
  only the AWS error code, never the full exception.
- `temperature=0` removes answer drift. Security work wants determinism
  as part of the trust model.

**Known gaps.** Moto's bucket policy evaluation is a subset of real IAM;
production should call `GetBucketPolicyStatus` or Access Analyzer. The
confidence check uses string matching; production should use a structured
confidence signal from the model.

## Tradeoffs I accepted

- Tools return strings, not Pydantic models. Works at four tools. I'd
  switch to typed returns past ten.
- No memory across turns. Each question is stateless. Real Dropzone work
  would keep conversation history.
- The IAM tool lists policy names but doesn't expand inline policy
  documents into the effective action set.

## Limitations

- Moto simulates a subset of AWS. Bucket policy evaluation is simplified
  here (wildcard Principal with Allow). Production would call
  `GetBucketPolicyStatus` or use Access Analyzer.
- No retry on transient boto3 errors (throttling, connection reset).
  Moto is reliable; real AWS needs exponential backoff. The LLM layer
  does fall back Sonnet to Opus on error or low confidence (see above).
