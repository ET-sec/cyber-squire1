"""Tests for pre_graph_pii regex scanner."""
from squire.pre_graph_pii import build_snippet, scan


def test_real_ssn_matches():
    hit = scan({"alert": {"output": "User SSN is 532-24-7461 leaked"}})
    assert hit is not None
    assert hit.entity == "US_SSN"
    assert hit.match == "532-24-7461"


def test_test_ssn_still_matches():
    # 123-45-6789 is the textbook "test" SSN but a real attacker can send it.
    # We intentionally match it (presidio's built-in suppresses it; we don't).
    hit = scan({"alert": {"output": "SSN: 123-45-6789"}})
    assert hit is not None
    assert hit.entity == "US_SSN"


def test_reserved_ssn_ranges_do_not_match():
    # 000/666/9xx area + 00 group + 0000 serial are invalid per SSA rules.
    assert scan("SSN: 000-12-3456") is None
    assert scan("SSN: 666-12-3456") is None
    assert scan("SSN: 900-12-3456") is None
    assert scan("SSN: 123-00-4567") is None
    assert scan("SSN: 123-45-0000") is None


def test_valid_luhn_cc_matches():
    # 4111-1111-1111-1111 is the canonical Visa test card (passes Luhn).
    hit = scan({"alert": {"output": "card 4111-1111-1111-1111 logged"}})
    assert hit is not None
    assert hit.entity == "CREDIT_CARD"


def test_invalid_luhn_does_not_match():
    # 4532-1234-5678-9010 LOOKS like a card but fails Luhn (sum=66 not mod 10).
    # This was red-team case 04; explains why that case passed without block.
    assert scan("card 4532-1234-5678-9010 logged") is None


def test_email_matches():
    hit = scan({"alert": {"output": "notify etigoue@tigouetheory.com"}})
    assert hit is not None
    assert hit.entity == "EMAIL_ADDRESS"


def test_us_phone_matches():
    hit = scan({"alert": {"output": "contact (404) 555-0199 for info"}})
    assert hit is not None
    assert hit.entity == "PHONE_NUMBER"


def test_clean_alert_no_hit():
    clean = {
        "alert": {
            "rule": "Terminal shell in container",
            "output": "shell spawned in cd-service-n8n on host cd-alpha by user root",
            "tags": ["mitre_execution", "T1059"],
        }
    }
    assert scan(clean) is None


def test_hostnames_containers_usernames_are_not_flagged():
    # These were presidio PERSON false-positives; regex-only scanner ignores.
    assert scan("root executed on cd-alpha in cd-service-n8n") is None


def test_build_snippet_masks_match():
    payload = {"alert": {"output": "card 4111-1111-1111-1111 logged"}}
    hit = scan(payload)
    snip = build_snippet(payload, hit, window=15)
    assert "4111-1111-1111-1111" not in snip
    assert "*" in snip


def test_docker_container_id_not_flagged():
    # 12-char hex like abc123def456 should not match CC (wrong chars)
    assert scan({"alert": {"output_fields": {"container.id": "abc123def456"}}}) is None


def test_timestamp_not_flagged_as_phone():
    # Timestamps like 2026-04-23T12:00:00 have digit runs but shouldn't match.
    assert scan({"alert": {"time": "2026-04-23T12:00:00Z"}}) is None
