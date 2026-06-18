# Recruiter Screen Prep: Conexess Group, Sarah Cross

**Role:** Web Application Security and Zero Trust Security Engineer (Remote)
**Recruiter:** Sarah Cross, Account Manager / Technical Recruiter, Conexess Group
**Rate:** $55/hr (accepted, do not negotiate on call)
**Length:** 6+ month contract, possible extension
**Call:** Today after 2pm ET

---

## About Conexess Group

- Staffing firm founded 2009. Around 200 employees, 15 states.
- HQ Nashville, TN. Sarah is in Hartford, CT.
- Clients range from Fortune 500/1000 down to mid-small.
- Offers contract, contract-to-hire, direct placement, project-based work.
- Sarah is the **recruiter**. She is not the hiring manager. Her job today is to confirm you sound coherent, match the JD, and submit you to the client.
- The end client is **not disclosed** in the JD. Ask her who it is on the call.

**What this means for the call:** Recruiter screens are fit and logistics, not technical depth. Sarah is checking:
1. Can you talk about the JD bullets without fumbling?
2. Do you sound professional?
3. Are you actually available?
4. Do you understand the rate and contract structure?

She will then submit you to the client. The client does the deep technical screen later.

---

## 60-Second Pitch (Memorize)

Open with this when she asks "tell me about yourself" or "walk me through your background."

> I am a security engineer based in Atlanta with around four years of hands-on experience. I run security engineering at CoreDirective where I own the full stack. WAF tuning on Cloudflare, Zero Trust access through Teleport and Keycloak with OAuth, OIDC, and SAML federation, Terraform with OPA policy gates across AWS, DigitalOcean, and Cloudflare, and Python automation. Before that I ran IT security and operations at Texaco for three retail sites where I deployed Splunk SIEM, rebuilt the network into four VLANs, and ran PCI DSS audits. Certs are SecurityX, SSCP, CCNA, Security+. CISSP in progress. The role you sent lines up almost exactly with my day to day, so I am very interested.

Time it. Should land in 55 to 65 seconds.

---

## Likely Questions and Scripted Answers

### "Why are you interested in this role?"
> The JD lines up with what I already do. WAF tuning, Zero Trust policies, OAuth and SAML, multi-cloud, Terraform and Python automation. Remote contract works for my situation, and the stack is current.

Do NOT say: "I am looking for a new opportunity," "I want to grow," or anything generic.

### "Walk me through your most recent role"
Pick CoreDirective. Hit three bullets only:
1. WAF and Zero Trust on Cloudflare and Teleport plus Keycloak, cut Datadog alerts from 200 plus to 12 daily.
2. Terraform across AWS, DigitalOcean, Cloudflare with OPA gates for IAM, KMS, tagging.
3. SAST, SCA, DAST in the SDLC. Semgrep, Trivy, OWASP ZAP, blocked unsigned container images.

Stop. Do not list everything. Three bullets, then ask "want me to go deeper on any of those?"

### "Walk me through the Texaco role"
> Three retail locations, around 45 endpoints. I deployed Splunk as the SIEM, built correlation rules that cut detection time from 48 hours to under four. Rebuilt a flat network into four VLANs for POS, back office, guest WiFi, and management. Ran PCI DSS audits and quarterly Nessus scans.

### "What is your WAF experience?"
> Cloudflare WAF in production. I tune rules, manage rate limiting, and integrate with the CDN edge. I also enforce mTLS access on internal tunnels and tie it back to Falco eBPF runtime detection for layered defense.

If she asks about Akamai or F5: "I have not worked Akamai directly, but WAF concepts are portable. Rule tuning, false positive reduction, log analysis, integration with CDN. Cloudflare is the WAF and CDN I run today."

### "What is your Zero Trust experience?"
> I run Zero Trust access at CoreDirective. Teleport for JIT privileged access with session recording. Keycloak for SSO and RBAC, federating OAuth, OIDC, and SAML. mTLS for service to service. Eliminated standing admin entirely, every admin path requires MFA.

### "How do you handle incident response?"
> At Texaco I investigated POS skimmer attempts using Wireshark, ran tabletop exercises, and tracked credential compromises. At CoreDirective I built detection rules in Datadog and tuned alert volume from 200 plus to 12 daily so the real signal is not buried.

### "What is your Python and Terraform experience?"
> Python for automation. I built workflow automation across 14 n8n workflows touching 16 services and 20 plus secrets. Patch deployment, user provisioning, compliance reporting all scripted. Terraform across 16 files and 30 plus resources with 8 OPA policy gates enforcing KMS, IAM, tagging, and zero public ingress.

### "What is your salary expectation?"
She already told you 55. Do NOT renegotiate.
> 55 per hour works for me. I understand it is a 6 plus month contract with possible extension.

### "Are you available to start immediately?"
> Yes. I can start within standard timing for a contract.

### "Are you authorized to work in the US?"
> Yes, US citizen, no sponsorship needed. Eligible for security clearance.

### "Are you currently working?"
> Yes, I run my own security engineering practice at CoreDirective. I can take on this contract alongside it without conflict. It is remote and the work scope is different.

(Do not say you are "unemployed" or "between roles." You are running CoreDirective.)

---

## Questions to Ask Her

Ask 2 or 3 of these. Shows engagement.

1. **Who is the end client?** (Most important. You need this for research before the next round.)
2. What industry is the client in? Finance, healthcare, tech?
3. Is this a pure contract or contract-to-hire?
4. Who would I be reporting to on the client side, and what does their security team look like?
5. What WAF stack is the client running today? Akamai, F5, Cloudflare, AWS WAF?
6. What is the timeline? When does the client want someone in seat?
7. How many candidates are you submitting?
8. What did the previous engineer in this seat work on?

---

## Common Reasons Screens Bomb

You said you have been doing awful. Likely causes and fixes:

| Problem | Fix |
|---------|-----|
| Rambling, no structure | Use the 60-second pitch verbatim. Stop talking. |
| Listing every skill | Three bullets max per role. Pause. Ask if they want more. |
| Sounding desperate | Already accepted rate. No pleading. Confident answers. |
| No questions back | Ask 2 to 3 from the list above. |
| Trash-talking past employer | Never. Texaco was a growth role. CoreDirective is your own practice. |
| Filler words (um, like, you know) | Slow down. Pauses are fine. Silence is better than filler. |
| Apologizing | Never apologize for your background or gaps. Skip it. |

---

## Red Flags to Avoid Saying

- "I am pivoting into AI Security." (You are AI Security. Already.)
- "I do not have much experience with X." (Use: "I have not worked X directly, but Y is the same concept.")
- "I am W2 ready." (Memory: do not mention employment type, that is the client's compliance call.)
- "I really need this job." (Never. Confidence.)
- Any complaint about Texaco, prior employers, or job search.

---

## Pre-Call Checklist (Run at 1:50pm)

- Resume open in tab: `Downloads/Emmanuel_Tigoue_AISecurity_Engineer_v2.pdf`
- JD open in tab: `Downloads/Zero Trust Security Engineer - Remote.docx`
- This prep doc open
- Water nearby
- Quiet space, good headphones, clear background
- Phone fully charged or on a charger
- Notebook for taking notes during the call (client name, next steps, timeline)

---

## After the Call

Email her within 30 minutes:
> Hi Sarah, thanks for the call. Confirming I am interested and available to move forward. Let me know when you have an update on next steps with the client.

Then save the client name and next steps to memory.
