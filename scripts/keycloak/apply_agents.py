#!/usr/bin/env python3
"""Apply agent IAM additions to existing Keycloak 'coredirective' realm via REST API.

Idempotent: checks for existence before creating. Safe to re-run.
Adds: 6 realm roles, 8 client scopes, 6 service-account clients.
Does NOT modify existing teleport client, cd-admin/operator/auditor roles, or etigoue user.
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

KC_BASE = "http://localhost:8080"
REALM = "coredirective"
ADMIN_USER = os.environ["KC_ADMIN_USER"]
ADMIN_PASS = os.environ["KC_ADMIN_PASS"]

# Capability scopes
CLIENT_SCOPES = [
    ("drift:read", "Read drift detection facts and reports"),
    ("drift:write", "Write drift events to change log"),
    ("grc:read", "Read GRC corpus, policies, and control mappings"),
    ("telegram:send", "Send notifications via Telegram bot"),
    ("vault:read", "Read scoped secrets from Vault Transit engine"),
    ("audit:read", "Read append-only audit log entries"),
    ("notion:read", "Read from scoped Notion pages"),
    ("notion:write", "Write to scoped Notion pages (Stack Facts mirror)"),
]

# Agent realm roles
AGENT_ROLES = [
    ("agent:soc-tier1", "SOC tier 1 agent role - read-only triage capability"),
    ("agent:soc-defensive", "SOC defensive response agent - can act on tier 1 recommendations"),
    ("agent:soc-offensive", "SOC offensive red team agent - read-only access to test targets"),
    ("agent:grc-corpus", "GRC corpus search agent"),
    ("agent:audit", "Audit and governance agent - append-only audit log access"),
    ("agent:drift-detector", "Stack drift detection agent"),
]

# Service-account clients: (client_id, name, description, secret_env_var, optional_scopes)
AGENT_CLIENTS = [
    ("squire", "Squire - Tier 1 SOC triage agent",
     "Read-only Datadog alert triage. LangGraph 7-node state machine with NeMo Guardrails. Tier 1, no write actions.",
     "KC_CLIENT_SQUIRE_SECRET",
     ["drift:read", "grc:read", "notion:read"]),
    ("blue-squire", "Blue Squire - Defensive response agent",
     "Defensive response to Squire-recommended actions. Can send Telegram alerts and read Vault secrets.",
     "KC_CLIENT_BLUE_SQUIRE_SECRET",
     ["drift:read", "telegram:send", "vault:read"]),
    ("red-squire", "Red Squire - Offensive red team agent",
     "Adversarial testing against Squire and OpenClaw skill catalog. Read-only access to test target metadata.",
     "KC_CLIENT_RED_SQUIRE_SECRET",
     ["drift:read"]),
    ("grc-librarian", "GRC Librarian - corpus search agent",
     "Searches GRC corpus (54 docs) via MCP server. Returns control mappings and citations. Read-only.",
     "KC_CLIENT_GRC_LIBRARIAN_SECRET",
     ["grc:read"]),
    ("keeper-squire", "Keeper Squire - audit and governance agent",
     "Reads append-only audit log entries. Verifies cross-agent compliance with assigned scopes.",
     "KC_CLIENT_KEEPER_SQUIRE_SECRET",
     ["audit:read", "grc:read"]),
    ("drift-detector", "Drift Detector - stack drift agent",
     "Runs verify-facts.py, diffs stack-facts.yaml against reality, writes to Notion ChangeLog, alerts via Telegram.",
     "KC_CLIENT_DRIFT_DETECTOR_SECRET",
     ["drift:write", "telegram:send", "notion:write"]),
]


def http(method, path, token=None, body=None, form=None):
    url = f"{KC_BASE}{path}"
    headers = {"Accept": "application/json"}
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            if not raw:
                return r.status, None
            try:
                return r.status, json.loads(raw)
            except Exception:
                return r.status, raw.decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def get_admin_token():
    code, data = http("POST", "/realms/master/protocol/openid-connect/token",
                      form={"grant_type": "password", "client_id": "admin-cli",
                            "username": ADMIN_USER, "password": ADMIN_PASS})
    if code != 200:
        sys.exit(f"admin token failed: {code} {data}")
    return data["access_token"]


def add_realm_roles(token):
    print("\n=== REALM ROLES ===")
    code, existing = http("GET", f"/admin/realms/{REALM}/roles", token=token)
    existing_names = {r["name"] for r in existing} if isinstance(existing, list) else set()
    for name, desc in AGENT_ROLES:
        if name in existing_names:
            print(f"  SKIP {name} (exists)")
            continue
        code, _ = http("POST", f"/admin/realms/{REALM}/roles", token=token,
                       body={"name": name, "description": desc, "composite": False, "clientRole": False})
        print(f"  {'ADD ' if code in (201, 204) else 'FAIL'} {name} (HTTP {code})")


def add_client_scopes(token):
    print("\n=== CLIENT SCOPES ===")
    code, existing = http("GET", f"/admin/realms/{REALM}/client-scopes", token=token)
    existing_names = {s["name"]: s["id"] for s in existing} if isinstance(existing, list) else {}
    scope_ids = {}
    for name, desc in CLIENT_SCOPES:
        if name in existing_names:
            print(f"  SKIP {name} (exists)")
            scope_ids[name] = existing_names[name]
            continue
        body = {
            "name": name,
            "description": desc,
            "protocol": "openid-connect",
            "attributes": {
                "include.in.token.scope": "true",
                "display.on.consent.screen": "false",
            },
        }
        code, _ = http("POST", f"/admin/realms/{REALM}/client-scopes", token=token, body=body)
        print(f"  {'ADD ' if code in (201, 204) else 'FAIL'} {name} (HTTP {code})")
    # refresh and capture ids of any newly created
    code, refreshed = http("GET", f"/admin/realms/{REALM}/client-scopes", token=token)
    if isinstance(refreshed, list):
        scope_ids = {s["name"]: s["id"] for s in refreshed if s["name"] in [n for n, _ in CLIENT_SCOPES]}
    return scope_ids


def add_clients(token, scope_ids):
    print("\n=== SERVICE ACCOUNT CLIENTS ===")
    code, existing = http("GET", f"/admin/realms/{REALM}/clients", token=token)
    existing_ids = {c["clientId"]: c["id"] for c in existing} if isinstance(existing, list) else {}
    for client_id, name, desc, secret_env, opt_scopes in AGENT_CLIENTS:
        if client_id in existing_ids:
            print(f"  SKIP {client_id} (exists)")
            continue
        secret = os.environ.get(secret_env)
        if not secret:
            print(f"  FAIL {client_id}: missing env {secret_env}")
            continue
        body = {
            "clientId": client_id,
            "name": name,
            "description": desc,
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "standardFlowEnabled": False,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": False,
            "serviceAccountsEnabled": True,
            "secret": secret,
            "attributes": {
                "access.token.lifespan": "900",
                "client.session.idle.timeout": "900",
                "use.refresh.tokens": "false",
            },
        }
        code, _ = http("POST", f"/admin/realms/{REALM}/clients", token=token, body=body)
        if code not in (201, 204):
            print(f"  FAIL {client_id} create (HTTP {code})")
            continue
        # Attach optional client scopes
        code2, c_lookup = http("GET", f"/admin/realms/{REALM}/clients?clientId={client_id}", token=token)
        if not isinstance(c_lookup, list) or not c_lookup:
            print(f"  FAIL {client_id} re-lookup (HTTP {code2})")
            continue
        c_uuid = c_lookup[0]["id"]
        attached = 0
        for sname in opt_scopes:
            sid = scope_ids.get(sname)
            if not sid:
                print(f"    WARN {client_id}: scope {sname} not found in registry")
                continue
            code3, _ = http("PUT", f"/admin/realms/{REALM}/clients/{c_uuid}/optional-client-scopes/{sid}", token=token)
            if code3 in (204, 200):
                attached += 1
        print(f"  ADD  {client_id} (HTTP 201, scopes attached: {attached}/{len(opt_scopes)})")


def test_token(client_id, secret_env, scopes):
    secret = os.environ.get(secret_env)
    if not secret:
        return None
    code, data = http("POST", f"/realms/{REALM}/protocol/openid-connect/token",
                      form={"grant_type": "client_credentials",
                            "client_id": client_id,
                            "client_secret": secret,
                            "scope": " ".join(scopes)})
    return code, data


def main():
    print("Connecting to Keycloak admin...")
    token = get_admin_token()
    print(f"  got admin token ({len(token)} chars)")
    add_realm_roles(token)
    scope_ids = add_client_scopes(token)
    add_clients(token, scope_ids)
    print("\n=== TOKEN ISSUANCE TEST: squire ===")
    code, data = test_token("squire", "KC_CLIENT_SQUIRE_SECRET", ["drift:read", "grc:read", "notion:read"])
    if code == 200 and isinstance(data, dict) and "access_token" in data:
        tok = data["access_token"]
        # JWT decode payload section
        import base64
        parts = tok.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            print(f"  HTTP 200, expires_in={data.get('expires_in')}s, scope='{data.get('scope')}'")
            print(f"  Token claims: sub={payload.get('sub')[:8]}..., azp={payload.get('azp')}, aud={payload.get('aud')}, scope='{payload.get('scope')}'")
            print(f"  Lifetime: exp - iat = {payload.get('exp') - payload.get('iat')}s")
        else:
            print(f"  HTTP 200 but token malformed")
    else:
        print(f"  FAIL: HTTP {code} {data}")


if __name__ == "__main__":
    main()
