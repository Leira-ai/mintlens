"""MintLens — read-only research-brief tools for BSC free-mint opportunities.

Every function in this module is READ-ONLY: JSON-RPC eth_call/eth_getCode,
the Sourcify public API, and the DexScreener public API. Nothing here signs,
sends, approves, or moves value. The same functions back both the standalone
CLI (deterministic brief, no model needed) and the OpenMinion agent tools
in agent.py.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests
from Crypto.Hash import keccak

CHAIN_ID = 56  # BNB Smart Chain
RPCS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed2.binance.org",
    "https://bsc-dataseed1.defibit.io",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (MintLens research agent; read-only)"}
# Simulations run "from" this public address; eth_call never moves funds.
SIM_FROM = "0xD4F22Ab69166ddd6822C8626e43A47830D5BdbF7"
ZERO_ADDR = "0x" + "00" * 20

CACHE_PATH = Path(__file__).parent / ".mintlens_cache.json"
CACHE_TTL_SECONDS = 6 * 3600


# --------------------------------------------------------------------------
# Low-level helpers
# --------------------------------------------------------------------------

def selector(signature: str) -> str:
    h = keccak.new(digest_bits=256)
    h.update(signature.encode())
    return "0x" + h.hexdigest()[:8]


def _rpc(method: str, params: list):
    """Try each public RPC in order; return the JSON-RPC result or raise."""
    last_err = None
    for url in RPCS:
        try:
            r = requests.post(
                url,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                headers=HEADERS,
                timeout=15,
            )
            data = r.json()
            if "result" in data:
                return data["result"]
            last_err = data.get("error")
        except Exception as exc:  # noqa: BLE001 - report via last_err
            last_err = exc
    raise RuntimeError(f"all RPCs failed for {method}: {last_err}")


def eth_call(to: str, data: str, from_addr: str | None = None) -> str:
    tx = {"to": to, "data": data, "value": "0x0"}
    if from_addr:
        tx["from"] = from_addr
    return _rpc("eth_call", [tx, "latest"])


def _decode_string(raw: str) -> str | None:
    if not raw or raw == "0x":
        return None
    b = bytes.fromhex(raw[2:])
    try:
        if len(b) >= 64:  # dynamic string: offset, length, data
            length = int.from_bytes(b[32:64], "big")
            return b[64 : 64 + length].decode("utf-8", "replace")
        if len(b) == 32:  # bytes32 symbol/name
            return b.rstrip(b"\x00").decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None
    return None


def _decode_uint(raw: str) -> int | None:
    if not raw or raw == "0x":
        return None
    try:
        return int(raw, 16)
    except ValueError:
        return None


def _try_read(fn):
    try:
        return fn()
    except Exception:  # noqa: BLE001 - a revert just means "not readable"
        return None


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

def check_contract(address: str) -> dict:
    """Bytecode presence + ERC-20/721 identity reads (name/symbol/supply/owner)."""
    code = _rpc("eth_getCode", [address, "latest"])
    has_code = bool(code) and code != "0x"
    out: dict = {"has_code": has_code, "code_bytes": (len(code) - 2) // 2 if has_code else 0}
    if not has_code:
        return out
    out["name"] = _try_read(lambda: _decode_string(eth_call(address, selector("name()"))))
    out["symbol"] = _try_read(lambda: _decode_string(eth_call(address, selector("symbol()"))))
    out["decimals"] = _try_read(lambda: _decode_uint(eth_call(address, selector("decimals()"))))
    out["total_supply_raw"] = _try_read(
        lambda: _decode_uint(eth_call(address, selector("totalSupply()")))
    )
    owner_raw = _try_read(lambda: eth_call(address, selector("owner()")))
    out["owner"] = ("0x" + owner_raw[-40:]) if owner_raw and len(owner_raw) >= 42 else None
    return out


def check_verification(address: str) -> dict:
    """Sourcify v2 lookup: is the source verified, and under what name?

    Note: in the v2 API the contract name lives in
    metadata.settings.compilationTarget — there is no top-level "name" field
    selector (asking for one returns HTTP 400).
    """
    try:
        r = requests.get(
            f"https://sourcify.dev/server/v2/contract/{CHAIN_ID}/{address}",
            params={"fields": "metadata"},
            headers=HEADERS,
            timeout=15,
        )
        if r.status_code != 200:
            return {"verified": False, "match": None, "error": f"HTTP {r.status_code}"}
        d = r.json()
        match = d.get("match")
        name = None
        target = ((d.get("metadata") or {}).get("settings") or {}).get("compilationTarget") or {}
        if target:
            name = next(iter(target.values()), None)
        return {
            "verified": bool(match),
            "match": match,
            "name": name,
            "verified_at": d.get("verifiedAt"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"verified": False, "match": None, "error": str(exc)}


def check_market(address: str) -> dict:
    """DexScreener: best BSC pair by liquidity, if any."""
    try:
        r = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{address}",
            headers=HEADERS,
            timeout=15,
        )
        pairs = [p for p in (r.json().get("pairs") or []) if p.get("chainId") == "bsc"]
        if not pairs:
            return {"has_market": False}
        best = max(pairs, key=lambda p: (p.get("liquidity") or {}).get("usd") or 0)
        return {
            "has_market": True,
            "pair": best.get("pairAddress"),
            "dex": best.get("dexId"),
            "price_usd": best.get("priceUsd"),
            "liquidity_usd": (best.get("liquidity") or {}).get("usd"),
            "volume_24h_usd": (best.get("volume") or {}).get("h24"),
            "url": best.get("url"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"has_market": False, "error": str(exc)}


# Mint/claim entry points probed with value-0 eth_call simulations.
# A passing simulation is a SIGNAL, not proof — a full gate still applies.
_FREE_PROBES: list[tuple[str, str]] = [
    ("freeMint()", "freeMint()"),
    ("freeMint(uint256)=1", "freeMint(uint256)"),
    ("mint(uint256)=1", "mint(uint256)"),
    ("claimFree()", "claimFree()"),
    ("claimFree(uint256)=1", "claimFree(uint256)"),
    ("claim()", "claim()"),
    ("openFree()", "openFree()"),
    ("mintFree(uint256,address)=(1,zero)", "mintFree(uint256,address)"),
]


def _probe_calldata(signature: str) -> str:
    data = selector(signature)
    if signature in ("freeMint(uint256)", "mint(uint256)", "claimFree(uint256)"):
        data += "%064x" % 1
    elif signature == "mintFree(uint256,address)":
        data += "%064x" % 1 + "%064x" % 0
    return data


def _simulate(address: str, signature: str, from_addr: str) -> str:
    try:
        eth_call(address, _probe_calldata(signature), from_addr=from_addr)
        return "ok"
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        return "revert" if "revert" in msg else "error"


# A neutral address that has never minted anywhere: probes from here answer
# "does a free path exist at all", while probes from SIM_FROM answer
# "can this specific wallet still use it" (quota may already be spent).
FRESH_FROM = "0x0000000000000000000000000000000000001234"


def probe_free_paths(address: str) -> dict:
    """Simulate common free mint/claim entry points with value 0 (read-only),
    from both a fresh address and the operator wallet."""
    results = []
    for label, sig in _FREE_PROBES:
        results.append(
            {
                "method": label,
                "fresh_wallet": _simulate(address, sig, FRESH_FROM),
                "operator_wallet": _simulate(address, sig, SIM_FROM),
            }
        )
    ok = [r["method"] for r in results if r["fresh_wallet"] == "ok"]
    wallet_ok = [r["method"] for r in results if r["operator_wallet"] == "ok"]
    return {
        "has_free_path_signal": bool(ok),
        "methods_ok": ok,
        "operator_wallet_methods_ok": wallet_ok,
        "probes": results,
    }


# --------------------------------------------------------------------------
# Brief composition (deterministic; the model narrates, it does not invent)
# --------------------------------------------------------------------------

def _load_cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text())
    except Exception:  # noqa: BLE001
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2))
    except Exception:  # noqa: BLE001
        pass


def build_brief(address: str, use_cache: bool = True) -> dict:
    """Compose the full research brief for one contract address."""
    address = address.strip()
    cache = _load_cache()
    key = address.lower()
    if use_cache and key in cache and time.time() - cache[key]["ts"] < CACHE_TTL_SECONDS:
        cached = dict(cache[key]["brief"])
        cached["from_cache"] = True
        return cached

    contract = check_contract(address)
    brief: dict = {
        "address": address,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contract": contract,
        "from_cache": False,
    }
    if not contract.get("has_code"):
        brief["verdict"] = "Hindari"
        brief["reasons"] = ["Address has no contract bytecode on BSC (EOA or wrong address)."]
        cache[key] = {"ts": time.time(), "brief": brief}
        _save_cache(cache)
        return brief

    brief["verification"] = check_verification(address)
    brief["market"] = check_market(address)
    brief["free_paths"] = probe_free_paths(address)

    verified = bool(brief["verification"].get("verified"))
    free_signal = bool(brief["free_paths"].get("has_free_path_signal"))
    has_market = bool(brief["market"].get("has_market"))
    reasons: list[str] = []
    if free_signal:
        reasons.append(
            "Value-0 simulation from a fresh address passed for: "
            + ", ".join(brief["free_paths"]["methods_ok"])
            + " (free-path signal — not proof; the full gate still applies)."
        )
        if brief["free_paths"].get("operator_wallet_methods_ok"):
            reasons.append("The operator wallet can still use that path (simulation passed).")
        else:
            reasons.append(
                "The operator wallet did NOT pass simulation — its free quota is likely spent or blocked by another condition."
            )
    else:
        reasons.append(
            "No free mint/claim path passed value-0 simulation from the test address — "
            "that can mean there is no free path, the global quota is exhausted, or the path is "
            "identity-gated (e.g. requires an Agent ID) so simulations from a plain address always revert."
        )
    reasons.append(
        "Contract is verified on Sourcify." if verified else "Contract is NOT verified on Sourcify."
    )
    if has_market:
        reasons.append(
            f"There is a DEX market (liquidity ${brief['market'].get('liquidity_usd')}, price ${brief['market'].get('price_usd')})."
        )
    else:
        reasons.append("No DEX pair on BSC yet (DexScreener).")

    if free_signal and verified:
        verdict = "Layak"
    elif free_signal or has_market or verified:
        # A verified contract (or a traded token) is never "Hindari" just because
        # the generic probe found no free path — the path may be identity-gated.
        verdict = "Pantau"
    else:
        verdict = "Hindari"
    brief["verdict"] = verdict
    brief["reasons"] = reasons

    cache[key] = {"ts": time.time(), "brief": brief}
    _save_cache(cache)
    return brief


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3 and sys.argv[1] == "brief":
        print(json.dumps(build_brief(sys.argv[2], use_cache="--fresh" not in sys.argv), indent=2))
    else:
        print("usage: python mintlens.py brief <contract-address> [--fresh]")
