"""Tests for sanitize_output.sanitize().

Covers each pattern, multi-pattern combo, no-match passthrough, and the
critical false-positive guards: POA&M IDs (P17-15) and NIST control IDs
(AC-2, SI-7, IR-4, RA-5) MUST pass through unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc.sanitize_output import sanitize  # noqa: E402


# --- per-pattern coverage --------------------------------------------------

def test_pattern_1_production_droplet_ip():
    assert sanitize("Hit 161.35.0.184 today") == "Hit [REDACTED-IP] today"


def test_pattern_2_rfc1918_10():
    assert sanitize("internal 10.20.30.40 host") == "internal [INTERNAL-IP] host"


def test_pattern_2_rfc1918_192_168():
    assert sanitize("router 192.168.1.1") == "router [INTERNAL-IP]"


def test_pattern_2_rfc1918_172_16():
    assert sanitize("docker bridge 172.17.0.1 net") == "docker bridge [INTERNAL-IP] net"


def test_pattern_3_cd_service_container_name():
    assert sanitize("cd-service-n8n is down") == "[INTERNAL-SVC] is down"


def test_pattern_4_internal_domain():
    assert sanitize("ssh.tigouetheory.com") == "ssh.[INTERNAL-DOMAIN]"


def test_pattern_5_root_path():
    assert (
        sanitize("/root/COREDIRECTIVE_ENGINE/.env was modified")
        == "[INTERNAL-PATH] was modified"
    )


def test_pattern_6_doppler_token():
    assert sanitize("dp.st.prd.AbCdEfGhIjK_lmnoPQR") == "[REDACTED-DOPPLER-TOKEN]"
    assert sanitize("dp.pt.dev.x_y-z123") == "[REDACTED-DOPPLER-TOKEN]"


def test_pattern_7_anthropic_key():
    assert (
        sanitize("key=sk-ant-api03-AAA_BBB-ccc")
        == "key=[REDACTED-ANTHROPIC-KEY]"
    )


def test_pattern_8_github_pat():
    # 20+ chars after the prefix
    assert (
        sanitize("token ghp_abcdefghij1234567890XYZ rotated")
        == "token [REDACTED-GH-TOKEN] rotated"
    )
    assert (
        sanitize("token ghs_abcdefghij1234567890XYZ rotated")
        == "token [REDACTED-GH-TOKEN] rotated"
    )


def test_pattern_9_aws_access_key_id():
    assert sanitize("AKIAIOSFODNN7EXAMPLE here") == "[REDACTED-AWS-KEY] here"


def test_pattern_10_bearer_token():
    assert (
        sanitize("Authorization: Bearer abcdefgh1234567890_xyz.ext-tail")
        == "Authorization: Bearer [REDACTED]"
    )


# --- multi-pattern combo --------------------------------------------------

def test_multi_pattern_combo():
    src = "Hit 161.35.0.184 from cd-service-n8n at /root/CD/.env (P17-15, AC-2)"
    expected = "Hit [REDACTED-IP] from [INTERNAL-SVC] at [INTERNAL-PATH] (P17-15, AC-2)"
    assert sanitize(src) == expected


# --- no-match passthrough --------------------------------------------------

def test_no_match_passthrough():
    assert sanitize("Plain text with no secrets.") == "Plain text with no secrets."


def test_empty_string_passthrough():
    assert sanitize("") == ""


# --- CRITICAL FALSE-POSITIVE GUARDS ---------------------------------------

def test_poam_ids_pass_through_unchanged():
    """POA&M IDs (P17-15, P19-99) MUST NOT be redacted."""
    s = "POAM-P17-15 closed, POAM-P19-99 open. P17-01 also open."
    assert sanitize(s) == s


def test_nist_control_ids_pass_through_unchanged():
    """NIST 800-53 control IDs MUST NOT be redacted."""
    s = "Controls AC-2, SI-7, IR-4, RA-5, SC-12 mapped."
    assert sanitize(s) == s


def test_idempotent():
    src = "/root/x was 161.35.0.184 from cd-service-db"
    once = sanitize(src)
    twice = sanitize(once)
    assert once == twice
