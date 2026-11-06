"""Smoke test: deterministic MintLens brief pipeline, end-to-end.

Runs mintlens.build_brief on one known contract and asserts the brief's
structure and verdict against ground truth established during the build:

    Moth Club (MOTH) 0x48c3ae8e8129efa9d20800ac8932d8b51f85c0f0
    — Sourcify-verified, ungated free mint (the fresh-address probe
    passes), verdict "Worth it" (FINDINGS, 2026-11-06 live tests).

Needs no API key and no model — only public BSC RPCs, Sourcify, and
DexScreener. Uses the 6-hour local cache when a fresh entry is present;
pass --fresh to force live reads. Exits 0 on pass, 1 on any failure.

    python smoke_test.py [--fresh]
"""

import sys

import mintlens

ADDRESS = "0x48c3ae8e8129efa9d20800ac8932d8b51f85c0f0"
EXPECTED_VERDICT = "Worth it"

_checks = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global _checks
    _checks += 1
    print(f"  [{'ok' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        raise AssertionError(label)


def main() -> int:
    use_cache = "--fresh" not in sys.argv
    print(f"MintLens smoke test — brief for {ADDRESS} (cache: {use_cache})")
    brief = mintlens.build_brief(ADDRESS, use_cache=use_cache)

    check("brief is a dict", isinstance(brief, dict))
    check("address echoes the request", brief.get("address", "").lower() == ADDRESS.lower())
    check("observed_at stamp present", bool(brief.get("observed_at")), str(brief.get("observed_at")))
    check("from_cache flag present", "from_cache" in brief, f"from_cache={brief.get('from_cache')}")

    contract = brief.get("contract") or {}
    check("contract has code on BSC", contract.get("has_code") is True)
    check("contract identity read", bool(contract.get("name")), f"name={contract.get('name')!r}")
    check("contract symbol read", bool(contract.get("symbol")), f"symbol={contract.get('symbol')!r}")

    verification = brief.get("verification") or {}
    check("verification section present", "verified" in verification)
    check("Sourcify verified (ground truth)", verification.get("verified") is True,
          f"match={verification.get('match')}")

    check("market section present", "has_market" in (brief.get("market") or {}))

    free_paths = brief.get("free_paths") or {}
    check("free-path probe section present", "probes" in free_paths)
    check("free-path signal (ground truth)", free_paths.get("has_free_path_signal") is True,
          f"methods_ok={free_paths.get('methods_ok')}")

    reasons = brief.get("reasons")
    check("reasons is a non-empty list", isinstance(reasons, list) and len(reasons) > 0,
          f"{len(reasons) if isinstance(reasons, list) else 0} reasons")
    check("verdict field present", "verdict" in brief)
    check(f"verdict == {EXPECTED_VERDICT!r} (ground truth)",
          brief.get("verdict") == EXPECTED_VERDICT, f"got {brief.get('verdict')!r}")

    print(f"SMOKE TEST PASSED — {_checks} checks, verdict {brief['verdict']!r} "
          f"({'cached' if brief.get('from_cache') else 'live'} brief)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"SMOKE TEST FAILED at check: {exc}")
        raise SystemExit(1)
