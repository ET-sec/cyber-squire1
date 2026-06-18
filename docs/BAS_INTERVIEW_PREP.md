# BAS Interview Prep Guide
## Cybersecurity Engineer — Breach and Attack Simulation

---

## 1. The 30-Second Pitch

When someone asks "what is BAS?" or "what experience do you have with BAS?", this is what you say:

> "BAS is continuous, automated adversary simulation. Instead of running a pen test once a year and hoping your controls hold, you run attack scenarios on a schedule and measure whether your detection stack actually fires. You pick a threat actor, map their known TTPs from MITRE ATT&CK, execute each one against your environment, and check what your SIEM and EDR caught versus what it missed. The output is a gap list with remediation priorities, not a report that sits on a shelf."

That is the answer. Confident, practical, no textbook fluff.

If they push further:

> "The key difference is coverage validation. You are not just checking if a vulnerability exists. You are checking if your detection layer can see the exploit when it happens. I ran this at CoreDirective with Falco eBPF watching every container syscall. Ran OWASP ZAP against our application layer. Correlated everything in Datadog. Went from 200-plus noisy alerts down to 12 findings that actually represented real detection gaps."

---

## 2. BAS vs Everything Else

This question comes up in every interview. Know it cold.

| Method | Who runs it | Frequency | Goal | Output |
|---|---|---|---|---|
| Vulnerability Scanning | Automated tools | Continuous / daily | Find known CVEs in assets | CVE list with severity |
| Penetration Testing | Human operators | Annual / quarterly | Exploit weaknesses, prove business impact | Report with narrative |
| Red Teaming | Dedicated red team | Occasional | Simulate full APT campaign, test people + process | Full engagement report |
| BAS | Automated platform | Continuous / on-demand | Validate detection and response controls | Control coverage score + gap list |

The one-sentence separators:

- **Vuln scanning** answers "what is exposed?" It does not tell you if your SIEM will catch exploitation.
- **Pen testing** answers "can a human exploit this?" It is a snapshot in time, and a skilled tester, not a repeatable scenario.
- **Red teaming** answers "can we stop a full adversary campaign?" It tests people, process, and technology together. Expensive, slow, rare.
- **BAS** answers "does our detection stack work right now?" It runs continuously. It is not about finding new vulnerabilities. It is about validating existing controls.

In an interview: "Pen testing is a human doing creative exploitation. BAS is a platform doing repeatable, mapped, measurable adversary simulation so you know your controls are working between pen tests."

---

## 3. The BAS Lifecycle

Six phases. Know each one and have a real answer for what you did in it.

### Phase 1: Plan
Define scope, threat actor profile, and authorization. Which assets are in scope. Which ATT&CK techniques map to the threats you care about. Get written sign-off before anything runs. Change management ticket, not a verbal OK.

Your answer: "I scoped our container environment and selected APT29-aligned techniques because we run public-facing services and cloud workloads, which matches their targeting profile."

### Phase 2: Simulate
Execute the attack scenarios. In free/open-source setups this means running Atomic Red Team tests. In commercial platforms the agent does this automatically. Each test maps to a specific ATT&CK technique ID.

Your answer: "Ran Atomic Red Team tests covering initial access, execution, and persistence against containerized workloads. Also used OWASP ZAP for the application layer, covering OWASP Top 10."

### Phase 3: Detect
Check whether your detection controls fired. Query your SIEM. Pull Falco alerts. Look at EDR telemetry. The test result is binary for each technique: detected or not detected.

Your answer: "Falco eBPF was watching every syscall. I pulled the alerts in Datadog and correlated them against what I had run. For each test I documented whether a Falco rule fired, what rule fired, and at what severity."

### Phase 4: Analyze
For detected findings: is the alert actionable or noisy? For missed findings: why did nothing fire? Is there a rule gap? A tuning problem? A coverage gap in the sensor?

Your answer: "I went from 200-plus Falco alerts to 12 prioritized findings. Most of the noise was overly broad rules firing on normal container behavior. The 12 real findings were either techniques with no coverage at all or rules that fired but were miscategorized as low severity."

### Phase 5: Remediate
Write the specific fix for each gap. That might be a new Falco rule, an updated detection threshold in Datadog, a firewall rule, a WAF policy, a code fix in the application. Each gap needs an owner and a deadline.

Your answer: "For each of the 12 findings I wrote a remediation ticket with the specific Falco rule change or new rule needed, the ATT&CK technique it covers, and the expected behavior after the fix."

### Phase 6: Retest
Run the same scenario again after the fix is deployed. Confirm the gap is closed. This is not optional. A fix that is not verified is not a fix.

Your answer: "Retested each finding after the rule was deployed. Confirmed detection fired for all 12. Documented the before/after in Datadog dashboards."

---

## 4. BAS Tools

### Atomic Red Team (Know This One Best)
Red Canary's open-source library of atomics. Each test maps to one ATT&CK technique. Written in YAML. Executed via Invoke-AtomicRedTeam (PowerShell) or the Python runner.

How it works technically:
- Each atomic test has a test definition file: technique ID, name, description, executor type (bash, powershell, command_prompt, manual), and the actual command
- You run: `Invoke-AtomicTest T1059.001` and it executes the mapped attack
- You check your detection stack immediately after
- Cleanup commands undo the test artifacts when done

What you need to say: "Atomic Red Team is the baseline. Every technique has a test you can run in minutes. It is not an agent-based platform, it is a command library. You run it, you check your SIEM, you document what fired. That is the core BAS workflow."

### Caldera (MITRE's C2 Framework)
MITRE's own adversary simulation platform. Open source. Agent-based.

How it works:
- Deploy a Caldera server (Python, runs local or cloud)
- Deploy agents (Sandcat) on test endpoints
- Build adversary profiles by selecting ATT&CK techniques
- Run operations and watch the attack chain execute
- Built-in reporting shows which techniques ran, which produced artifacts, which were detected

Key point: Caldera is more sophisticated than Atomic Red Team. It chains techniques together into full operations. Atomic Red Team tests one technique at a time. Caldera simulates a campaign.

### SafeBreach, AttackIQ, Cymulate (Commercial Platforms)
These are enterprise BAS-as-a-service. Same concept, polished UI, vendor-maintained content libraries, pre-built threat actor profiles, integration with major SIEMs.

How they work technically:
- SaaS console for configuration and reporting
- Lightweight agents deployed on endpoints or in cloud environments
- Attack content library updated continuously by vendor research teams
- Direct integration with Splunk, QRadar, Sentinel, CrowdStrike, SentinelOne
- Automated scoring: what percentage of your controls detected the simulated attack

What to say in an interview: "I am familiar with the commercial platforms and the architecture they use. Agents on endpoints, centralized orchestration, SIEM integration for closed-loop validation. My hands-on experience is with Atomic Red Team and Caldera for cost reasons, and I have mapped that to what enterprise platforms do at scale."

---

## 5. MITRE ATT&CK Deep Dive

### What it is
A knowledge base of adversary behavior based on real-world observations. Not theoretical. Built from actual incident investigations. Maintained by MITRE. Free and public.

The key distinction: ATT&CK describes the "what" and "how" of attacker behavior, not just the vulnerability. T1059 is not a CVE. It is the technique of using scripting interpreters for execution. Every attacker uses it differently but the underlying behavior is the same.

### The 14 Tactics (in kill-chain order)
These are the "why" column. What is the attacker trying to accomplish?

1. Reconnaissance
2. Resource Development
3. Initial Access
4. Execution
5. Persistence
6. Privilege Escalation
7. Defense Evasion
8. Credential Access
9. Discovery
10. Lateral Movement
11. Collection
12. Command and Control
13. Exfiltration
14. Impact

In BAS, you typically start with Initial Access and run through to Exfiltration or Impact, skipping Reconnaissance and Resource Development (those happen before hitting your environment).

### Techniques vs Sub-techniques
- Technique: T1059 — Command and Scripting Interpreter. This is the parent.
- Sub-technique: T1059.001 — PowerShell. T1059.003 — Windows Command Shell. T1059.004 — Unix Shell.

When you write Falco rules or detection logic, you are usually targeting sub-techniques because the behavior is specific enough to write a real detection.

### Threat Actor Profiles
Go to attack.mitre.org/groups and pick any group. Each one has a list of techniques they are known to use with citations from real incidents. This is how you build a BAS scenario that reflects an actual threat.

Examples:
- APT29 (Cozy Bear, Russia): Focuses on cloud services, OAuth abuse, spearphishing. Heavy use of T1078 (Valid Accounts), T1071 (App Layer Protocol for C2).
- FIN7 (criminal, financially motivated): CARBANAK malware, spearphishing, POS system targeting. Heavy T1059, T1053, T1055.
- Lazarus (North Korea): Supply chain attacks, crypto theft. T1195, T1190, T1486 (ransomware).

### Key Technique IDs to Know Cold

**T1059 — Command and Scripting Interpreter**
Attackers use native scripting (bash, PowerShell, Python) to execute malicious commands. Common in every campaign. Detection: log every script execution, flag unusual interpreters spawned from unexpected parent processes.

Falco relevance: A container spawning a shell unexpectedly is T1059. Your "Terminal shell in container" rule covers this.

**T1071 — Application Layer Protocol**
C2 communication disguised as normal web traffic (HTTP, HTTPS, DNS). Attackers blend into normal traffic. Detection: anomaly detection on outbound connections, DNS query frequency analysis, C2 framework IOC feeds.

Falco relevance: "Unexpected outbound connection" rule covers unexpected egress. Pair with network policy enforcement.

**T1190 — Exploit Public-Facing Application**
Exploiting vulnerabilities in internet-facing applications. Web shells, SSRF, RCE. This is where OWASP ZAP lives. Detection: WAF rules, application-layer anomaly detection, unexpected process spawns from web server processes.

Your OWASP ZAP experience is direct coverage of this technique.

**T1110 — Brute Force**
Password guessing, credential stuffing, password spraying. Detection: authentication failure rate monitoring, account lockout policies, geographic anomalies in login attempts.

Datadog relevance: Authentication failure dashboards directly monitor this.

**T1078 — Valid Accounts**
Using legitimate stolen credentials. No exploit needed. Detection is hard: the behavior looks normal. Focus on contextual anomalies: login from new location, unusual time, service account used interactively.

This is why account behavioral analytics matters. Falco can catch a container using a valid credential to contact an API it has never contacted before.

**T1053 — Scheduled Task/Job**
Persistence via cron jobs, scheduled tasks. Attacker plants a job that re-establishes access or exfiltrates data on schedule. Detection: monitor cron directories, audit scheduled task creation events.

Falco relevance: Write below `/etc/cron*` paths should alert.

**T1055 — Process Injection**
Injecting malicious code into a legitimate process (ptrace, /proc/pid/mem writes). Evades detection by hiding inside trusted processes. Detection: ptrace calls, /proc writes, unexpected memory regions in processes.

Falco relevance: Falco can detect ptrace-based injection with syscall rules. This is one of the harder ones to tune because legitimate debuggers also use ptrace.

**T1098 — Account Manipulation**
Modifying accounts to maintain access: adding SSH keys, modifying sudoers, adding cloud IAM bindings. Detection: monitor /etc/passwd, /etc/sudoers, ~/.ssh/authorized_keys for changes.

Falco relevance: Write to sensitive files rules cover this. "Write below binary dir" and sudoers modification rules map here.

---

## 6. Designing a BAS Scenario From Scratch

Step by step. This is what you say when they ask "walk me through how you would build a BAS scenario."

### Step 1: Select Threat Actor
Pick one that is relevant to the target industry. For a financial services company: FIN7 or Carbanak. For a government contractor: APT29 or APT41. For a healthcare target: Lazarus or TA505.

Why this matters: It makes the scenario defensible. You are not just running random tests. You are simulating a realistic threat that the organization actually faces.

### Step 2: Map Their TTPs
Go to attack.mitre.org/groups/[group-id]. Pull their technique list. Select the techniques that apply to your environment.

Example for APT29 targeting a cloud-heavy organization:
- T1078 — Valid Accounts (initial access via stolen credentials)
- T1566.002 — Spearphishing Link
- T1071.001 — Web Protocols for C2
- T1560 — Archive Collected Data
- T1041 — Exfiltration Over C2 Channel

### Step 3: Design the Attack Chain
Map techniques to kill-chain phases:

```
Initial Access   → T1566.002 (phishing) or T1190 (exploit app)
Execution        → T1059.004 (bash/shell) or T1059.001 (PowerShell)
Persistence      → T1053.003 (cron) or T1098 (SSH key add)
Privilege Esc.   → T1055 (process injection) or T1078 (valid accounts)
Defense Evasion  → T1070 (log clearing) or T1562 (impair defenses)
Lateral Movement → T1021.004 (SSH) or T1078 (reuse valid accounts)
Exfiltration     → T1041 (over C2) or T1048 (via alternative protocol)
```

### Step 4: Execute Each Technique
Using Atomic Red Team: `Invoke-AtomicTest T1053.003 -GetPrereqs` then `Invoke-AtomicTest T1053.003`.

After each test, immediately check:
- Did Falco fire?
- Did Datadog alert?
- Did the SIEM log the event?
- What was the severity?

Document each result in a spreadsheet: Technique ID | Ran | Detected | Rule Name | Severity | Gap?

### Step 5: Check What Did Not Fire
These are your findings. For each miss, ask:
- Does a rule exist that should have caught this?
- Did the rule not fire because of a tuning problem (threshold too high)?
- Does no rule exist at all (coverage gap)?
- Is the sensor not deployed where this attack ran (telemetry gap)?

Three types of gaps: coverage gap, tuning gap, telemetry gap. The fix is different for each.

### Step 6: Document and Remediate
For each gap, write:
- ATT&CK technique ID and name
- What the test did (one sentence)
- Why it was not detected (root cause)
- Recommended fix (specific: new Falco rule, threshold change, sensor deployment)
- Priority: Critical / High / Medium based on technique prevalence and business impact

### Step 7: Retest After Fix
Deploy the fix. Run the same atomic test again. Confirm detection fires. Close the finding.

---

## 7. How Your Real Work Maps to BAS

This is the connective tissue. When you talk about your experience, frame everything in BAS terms.

**Falco eBPF = the detection layer being validated**

"Falco is my primary detection control for container workloads. In a BAS context, it is the tool I am validating. I run an atomic test that simulates process injection or an unexpected shell spawn, and I check whether Falco's rules fire with the right severity. If they do not, that is a gap in my detection coverage."

**Tuning 200+ alerts to 12 = BAS result analysis in practice**

"That tuning work is exactly what BAS analysis looks like. You start with a noisy detection environment, you identify which alerts represent real adversary behavior versus normal operational noise, and you fix the rules until every alert is actionable. Going from 200 to 12 means I removed 188 false positives and re-prioritized 12 findings that represent actual control gaps."

**Datadog dashboards = reporting and visualization layer**

"Datadog is where I aggregate and present BAS results. I built dashboards that show detection coverage by MITRE ATT&CK tactic, alert volume over time, and mean time to detect. When a BAS run completes, the results surface in these dashboards. That is the reporting layer that communicates control posture to stakeholders."

**OWASP ZAP = application-layer attack simulation**

"ZAP covers OWASP Top 10 against web applications, which maps directly to T1190 (Exploit Public-Facing Application) in MITRE ATT&CK. I run active scans against our app endpoints, analyze findings, and validate that our WAF rules or application-level controls catch the attack patterns ZAP exercises. It is BAS for the application layer."

**Red teaming AI = BAS for AI-specific attack vectors**

"AI systems need their own threat models. I built and tested prompt injection scenarios and jailbreak attempts against our LLM stack. That is BAS applied to a non-traditional attack surface. The same lifecycle applies: define the threat, simulate it, check if your guardrails fire, document what they missed, fix it. The ATT&CK framework has an AI-specific matrix now (ATLAS) that maps exactly to this work."

---

## 8. Interview Questions and Sample Answers

### "Design a BAS program for our enterprise. Where do you start?"

"First thing is threat profiling. I want to know what the organization's actual threat landscape looks like. Who targets your industry? What TTPs do they use? That informs which ATT&CK techniques I am going to prioritize.

Second is inventory: what assets exist, what detection controls are deployed, and where are the telemetry gaps. You can not run BAS against assets your sensors are not watching.

Third is authorization and change management. Every test gets a ticket before it runs. No exceptions. Production environments need coordination with operations teams.

Then I run a baseline BAS sweep using Atomic Red Team, starting with the highest-priority techniques from our threat profile. I collect results, categorize gaps as coverage, tuning, or telemetry, and produce a prioritized remediation list.

The program runs continuously. Not as a one-time exercise. Monthly sweeps against core techniques, with immediate retesting after any remediation. Coverage scores tracked over time in the SIEM dashboard."

### "You ran a simulation and Falco didn't detect it. What do you do?"

"First I confirm the test ran correctly. Verify the atomic executed cleanly, check the logs to confirm the action actually happened on the system. If the test failed, that is a test problem not a detection gap.

If the test ran clean and Falco did not fire, I look at three things. One: does a rule exist that should cover this technique? Pull the Falco rule set and search for rules that should match the syscalls or file paths involved. Two: if a rule exists, why did it not fire? Check thresholds, check if the container is in scope for the rule, check if the rule has exceptions that accidentally excluded this behavior. Three: if no rule exists, that is a coverage gap and I write one.

For the rule I write, I start with the specific syscall or file event Falco should see, define the condition using Falco's condition syntax, set priority based on technique severity, and test the new rule in a non-production environment before deploying. Then I retest the atomic and confirm it fires."

### "How do you prioritize which ATT&CK techniques to test first?"

"Three factors: threat actor relevance, technique prevalence, and control risk.

Threat actor relevance: techniques used by groups that actually target your industry get priority. I look at MITRE ATT&CK Groups and cross-reference with threat intel feeds. APT29 techniques are higher priority for government contractors than for retail.

Technique prevalence: ATT&CK publishes data on which techniques show up most often in real incidents. T1059, T1078, T1110 are everywhere. These go to the top of the list regardless of threat actor.

Control risk: if I know a technique hits a part of my stack where I have low confidence in detection coverage, that goes first. No point spending time validating controls I know are solid when there are known gaps to close.

In practice I weight these and build a ranked backlog. Top 20 techniques get tested in the first sprint. Everything else follows on a rolling schedule."

### "What's the difference between a BAS finding and a pen test finding?"

"A pen test finding is a proven exploitable vulnerability with a business impact narrative. A human exploited it, walked through the attack chain, and documented what they could access. It is a snapshot.

A BAS finding is a control gap. It is not necessarily exploitable in the way a pen test finding is. It means: this technique ran, and nothing in our detection stack saw it. That is a coverage problem. The vulnerability might not even exist, but if the detection is not there, we are flying blind when an attacker does exploit it.

The remediation is also different. A pen test finding usually gets remediated by fixing the vulnerability. A BAS finding usually gets remediated by improving detection or adding a control. They are complementary. Pen testing tells you what is exploitable. BAS tells you what is invisible."

---

## 9. What Can Go Wrong

Know these. Being able to articulate the risks shows operational maturity.

**Simulation crashes production**

Atomic tests that involve resource exhaustion, file deletion, or network disruption can impact live systems. The fix is never running production BAS without change management, and starting with test environments first. Know which atomics are destructive before you run them. The atomic test YAML files mark destructive tests explicitly.

**Agent causes false positive cascade**

A BAS agent doing legitimate simulation can trigger every detection rule simultaneously. Your SOC gets flooded with alerts, they escalate, and now you have an incident response drill you did not plan for. The fix is telling your SOC team ahead of time: "BAS runs on these hosts from this IP on this schedule." Pre-authorized exception in the SIEM for test traffic.

**Testing without proper authorization**

Running BAS tests without a written scope and authorization document is unauthorized access, even in your own environment. If something goes wrong and it is not documented, you own it. Always get written sign-off. Always have a change management ticket. Always define the scope before running anything.

**Confusing simulation artifacts with real incidents**

BAS agents leave artifacts: modified files, new scheduled tasks, unusual network connections. If operations or security teams do not know BAS is running, they may respond to these as real incidents. Mitigation: run cleanup commands after every test, maintain a BAS activity log that SOC can reference, use dedicated test hosts when possible.

---

## 10. Falco Rules You Need to Know

### Terminal Shell in Container

```yaml
- rule: Terminal shell in container
  desc: A shell was spawned in a container with an attached terminal
  condition: >
    spawned_process and container
    and shell_procs and proc.tty != 0
  output: >
    A shell was spawned in a container with an attached terminal
    (user=%user.name container=%container.name shell=%proc.name
    parent=%proc.pname cmdline=%proc.cmdline)
  priority: WARNING
```

What it catches: Interactive shell sessions in containers. Attacker gaining shell access is one of the most common early indicators after initial access. Maps to T1059.

### Write Below Binary Dir

```yaml
- rule: Write below binary dir
  desc: An attempt to write to any file below a binary directory
  condition: >
    bin_dir and evt.dir = < and open_write
    and not package_mgmt_procs
    and not exe_running_docker_save
  output: >
    File below a known binary directory opened for writing
    (user=%user.name command=%proc.cmdline file=%fd.name)
  priority: ERROR
```

What it catches: Binaries being dropped into /bin, /usr/bin, /sbin etc. Persistence and defense evasion. Maps to T1036 (Masquerading) and T1543 (Create/Modify System Process).

### Contact K8S API Server From Container

```yaml
- rule: Contact K8s API Server From Container
  desc: Detect container communicating with K8s API server
  condition: >
    outbound and k8s_api_server
    and container
    and not k8s_containers
  output: >
    Unexpected connection to K8s API server
    (command=%proc.cmdline container=%container.name
    connection=%fd.name)
  priority: WARNING
```

What it catches: Containers accessing the Kubernetes API without authorization. Container escape attempts, privilege escalation to cluster-admin. Maps to T1078 and T1548.

### Unexpected Outbound Connection

```yaml
- rule: Unexpected outbound connection
  desc: Container made an unexpected outbound connection
  condition: >
    outbound and container
    and not (proc.name in (expected_processes))
    and not (fd.sip in (allowed_ips))
  output: >
    Unexpected outbound connection from container
    (command=%proc.cmdline container=%container.name
    destination=%fd.sip:%fd.sport)
  priority: WARNING
```

What it catches: C2 communication, data exfiltration, beaconing. Maps to T1071 (Application Layer Protocol) and T1041 (Exfiltration Over C2 Channel).

### How to Write a Custom Falco Rule

The structure every rule follows:

```yaml
- rule: [Rule Name]
  desc: [What this detects in plain English]
  condition: [Falco condition expression using fields and macros]
  output: [What gets logged when the rule fires, with field interpolation]
  priority: [EMERGENCY | ALERT | CRITICAL | ERROR | WARNING | NOTICE | INFO | DEBUG]
  tags: [mitre_technique_id, container, filesystem, etc.]
```

The condition uses Falco's field class system:
- `evt.*` — event fields (evt.type, evt.dir)
- `proc.*` — process fields (proc.name, proc.pid, proc.cmdline)
- `fd.*` — file descriptor fields (fd.name, fd.sip, fd.sport)
- `container.*` — container fields (container.name, container.id)
- `user.*` — user fields (user.name, user.uid)

Falco macros let you compose conditions from reusable pieces. `spawned_process`, `container`, `outbound`, `open_write` are all macros defined in Falco's default rules file. You can reuse them or override them.

Writing process for a new rule:

1. Identify the specific syscall or event you want to catch. Start with `falco -l` to list all supported fields.
2. Write the condition narrowly first. Run it and see what fires. Expect false positives.
3. Add exceptions for legitimate processes using `and not proc.name in (...)`.
4. Test against your BAS atomic. Confirm it fires for the attack, not for normal traffic.
5. Set priority based on technique severity. T1055 process injection is CRITICAL. Unusual file read is WARNING.
6. Add ATT&CK tags so your SIEM can correlate across technique IDs.

Common mistake: writing conditions that are too broad and catching everything. The result is noise that gets ignored. Start narrow, expand coverage incrementally as you validate each addition.

---

## Day-Before Checklist

- Say the 30-second BAS pitch out loud. Not in your head. Out loud.
- Run through the lifecycle phases: Plan, Simulate, Detect, Analyze, Remediate, Retest.
- Know the 8 technique IDs by heart. Say T1059 and say "Command and Scripting Interpreter." No looking.
- Prepare the APT29 scenario walkthrough. Be ready to design a full campaign in 3 minutes.
- Know the three gap types: coverage, tuning, telemetry.
- Have the "200 to 12" story ready. That is your best BAS credential.
- Prepare one question to ask them: "How are you currently measuring detection coverage between pen test cycles?"

That question tells them you understand the problem BAS solves. It also turns the interview into a conversation.
