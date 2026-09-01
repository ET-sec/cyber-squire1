"""Break-glass access alert: CloudTrail event in, Telegram message out.

Fires from EventBridge on any GetSecretValue against the break-glass
secret. A break-glass credential nobody watches is a backdoor; this makes
every access loud within minutes of the API call.
"""

import json
import os
import urllib.parse
import urllib.request

import boto3

_ssm = boto3.client("ssm")


def _telegram_creds() -> tuple[str, str]:
    path = os.environ["TELEGRAM_PARAM_PATH"]
    raw = _ssm.get_parameter(Name=path, WithDecryption=True)["Parameter"]["Value"]
    creds = json.loads(raw)
    return creds["bot_token"], creds["chat_id"]


def handler(event, _context):
    detail = event.get("detail", {})
    who = detail.get("userIdentity", {}).get("arn", "unknown principal")
    src_ip = detail.get("sourceIPAddress", "unknown ip")
    when = detail.get("eventTime", "unknown time")

    text = (
        "BREAK-GLASS ACCESS\n"
        f"principal: {who}\n"
        f"source: {src_ip}\n"
        f"time: {when}\n"
        "If this was not you, rotate the OCI emergency credential now."
    )

    token, chat_id = _telegram_creds()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        resp.read()

    return {"ok": True}
