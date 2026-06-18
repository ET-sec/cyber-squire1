# n8n Context

## Workflows
| Workflow | ID | Webhook |
|----------|----|---------|
| MASTER_ORCHESTRATOR_V1 | `UIf3v1ZNN98OtUge` | `/webhook/master-cmd` |
| Telegram Supervisor Agent | `iO6PfPdk0SSPBTWb` | `/webhook/telegram-bot` |
| Content Research Pipeline | `nhtwRpJATQoaZpxL` | `/webhook/content-research` |
| YouTube Content Factory | `CPBPZ1obRFnuPOE3` | INACTIVE |
| Error Handler | `el07Swns2MrSSpOK` | n/a |
| Gmail Reader Main | `2A0O7MzPvUCCYoLV` | `/webhook/gmail-read-main` |
| Gmail Reader Brand | `wTUraUYjsHXCGWgr` | `/webhook/gmail-read` |
| Gmail Reader Personal | `NxoxcIcYRo0XPkOz` | `/webhook/gmail-read-personal` |
| Gmail Reader Business | `yLA81NXy9LBvps8m` | `/webhook/gmail-read-business` |
| API Health Check | `HrjxPHJ7yVznvRDg` | cron |
| Gumroad Solvency | `D6ZdnaRLlVmkjm3W` | cron |
| ADHD Commander | `bjv2gtSnBvXJ4Kxp` | n/a |
| Finance Manager | `6m44uhpOKDQ6nmSd` | n/a |
| Security Scan | `9ZFZFOqGCVWVlAmt` | n/a |
| System Status | `3trAv8CMqPop9W3f` | n/a |
| Gmail Label & Filter Creator | `EWQEr6TnXGS48Gmg` | n/a |

## Master Orchestrator
**Webhook:** `https://n8n.tigouetheory.com/webhook/master-cmd` | POST, application/json
```json
{"action": "postgres", "query": "SELECT NOW()"}
{"action": "telegram", "chat_id": "6691629392", "text": "..."}
{"action": "github", "owner": "ET-sec", "repo": "cyber-squire1"}
{"action": "notion", "query": "..."}
{"action": "tavily", "query": "...", "depth": "basic|advanced"}
{"action": "gmail", "to": "...", "subject": "...", "text": "..."}
{"action": "drive"} | {"action": "tasks"} | {"action": "sheets"}
{"action": "docs"} | {"action": "slides"} | {"action": "gumroad"} | {"action": "cloudflare"}
```
Note: `ollama` action removed. `workspace_admin` and `excel` need OAuth re-auth.

## Credential IDs (DO, recreated 2026-03-11)
**API Keys (working):**
- PostgreSQL `UuP653dTnvia3ocC` (verified)
- Telegram `kVdzT3vKPCZJvOrF` (verified)
- GitHub `bIzrMp7kfckCTz4N` (needs PAT update)
- Cloudflare `ke1ic3tGLvuwznA9` (needs token update)
- Notion `sa2qlo4cdM1Y0q5h`
- Gumroad `fFlar9lAmbXY44VW`

**OAuth (need browser Connect):**
- Google Tasks `gd9n98j3RZS1MRhv`, Slides `01j3kLcFRi9bzlgq`
- Sheets `u5l6jjkiGnqUgTEq`, Drive `6VxGmhQ6rEbpYss9`
- Docs `Df0EJcTbIqXm4uN8`, Workspace Admin `JwBMlO4ijw0GfGjF`
- Gmail Main `VcdKGOAn6V3KqLUx`, Brand `oxglU8muPD6zR1v4`
- Gmail Personal `ho6J73lw0Bqnr6ff`, Business `SPGZKD8LKZaPJW1a`
- Excel `9CPcktfwbjrXCDSn`

## REST API
Login: email=etigoue@tigouetheory.com, field=`emailOrLdapLoginId`
