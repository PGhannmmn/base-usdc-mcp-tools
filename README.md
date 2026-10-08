# Base USDC Payment QA Fixture Kit — Free v0.1.0

**Public experimental preview · 35 synthetic cases · Python 3.10+ · offline and free.**

**[Download GitHub source ZIP](https://github.com/PGhannmmn/base-usdc-mcp-tools/archive/refs/heads/preview/base-usdc-payment-qa-v0.1.zip)** · [Browse cases](docs/case-matrix.md) · [Download offline HTML viewer](site/index.html)

**Publication scope:** An isolated, public GitHub branch only. The production website on `main` and all Cloudflare Workers are unchanged. To view the HTML browser interactively, download `site/index.html` and open it locally; GitHub's source viewer does not execute HTML.

**Demand monitoring:** NOT enabled. No trustworthy count of product downloads or paying customers has been collected. No storefront or checkout is enabled.

---

# Base USDC Payment QA Fixture Kit

**35 synthetic cases · Offline / no keys / no transactions**

A small, deterministic **fixture dataset and test oracle** for developers building Base USDC payment flows. Exercise the decision points around ERC-20 Transfer logs, payer/recipient/amount matching, proof replay, mock chain finality and divergent RPC results **without any actual transfer or RPC request**.

> **TEST-ONLY: NOT A PAYMENT VERIFIER.** All transaction hashes are constructed from a `synthetic-qa-fixture:` prefix and do **not** attest to real transactions. The two `rpc_views` are invented. `order.binding_verified` is a **mock trusted-upstream flag**, NOT authentication: never trust a client-submitted flag in production. Do not use this package to grant real paid access.

## Contents

| Path | Purpose |
| --- | --- |
| `fixtures/scenarios.json` | Full 35-case synthetic dataset and expected classifications |
| `schema/scenarios.schema.json` | JSON Schema Draft 2020-12 fixture-envelope contract (intentionally permits malformed receipt/event fields in negative tests) |
| `src/fixturekit.py` | Offline reference evaluator (Python standard library only) |
| `src/build_fixtures.py` | Deterministic fixture generator |
| `src/check_cases.py` | CLI expectation runner |
| `src/build_site.py` | Generates standalone offline HTML case browser |
| `tests/test_fixturekit.py` | Unit and regression tests |
| `site/index.html` | Standalone offline case browser |
| `docs/case-matrix.md` | Every case, summary, expected result |
| `docs/limitations.md` | Security and correctness boundaries |
| `LICENSE` | MIT license for original source code and synthetic data |

## Quick start

Requirements: **Python 3.10+**. Zero packages required for core CLI/tests. No accounts, API keys, wallet, network or blockchain node required.

```bash
python src/check_cases.py
python src/check_cases.py --case bridged-usdbc
python src/check_cases.py --json
python -m unittest discover -s tests -v
```

To rebuild all synthetic scenarios deterministically:

```bash
python src/build_fixtures.py
python src/build_site.py
```

Open `site/index.html` locally in a browser to explore all the test cases; it makes no network requests.

For optional independent JSON Schema validation, if `jsonschema` already exists:

```python
import json, jsonschema
schema = json.load(open('schema/scenarios.schema.json'))
data = json.load(open('fixtures/scenarios.json'))
jsonschema.validate(data, schema)
```

## Integration example — mock test data only

```python
import sys
sys.path.insert(0, 'src')
from fixturekit import load_cases, evaluate

cases = load_cases('fixtures/scenarios.json')['cases']
for case in cases:
    assert evaluate(case)['code'] == case['expected'], case['id']
```

These labels model a **strict exact amount** demonstration policy (an overpayment is rejected). `claim_key = eip155:8453:transaction_hash:log_index` is an example identifier for independent ERC-20 log claims. The in-memory `prior_claim_keys` list merely simulates durable replay protection; real systems require atomic storage and per-order binding.

## Test data conventions

- Network: Base Mainnet `eip155:8453` / EVM chain ID 8453, but **all receipts are fake**.
- Native Circle USDC contract: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (public reference only).
- Bridged USDbC contract: `0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA` (negative tests).
- USDC units: six decimals; `1000000` is one USDC nominal unit in fixture math **not a payment instruction**.
- Payer and payee addresses are visibly fictitious (`0x11…` / `0x22…`).
- Canonical ERC-20 indexed `Transfer(address,address,uint256)` event is modeled with topic0, two 32-byte padded address topics, and 32-byte amount data.
- `finalized_block` in each mock RPC view is **made-up metadata**; equal/sufficient values do not prove chain finality. No automatic confirmation count is promised.
- The pure evaluator requires two mock providers to agree on the receipt and checks each invented finalized head.
- `binding_verified` means **simulated external attestation only**, not a proof that a chain payment is bound to an order.

## Safety

Do not use any part of this kit as a real-world checkout, signature verifier, transaction indexer, x402 facilitator, settlement endpoint, USDC transfer authorizer, or release gate for paid downloads. It does not validate EIP-3009 signatures, query trusted nodes, verify RPC authenticity or perform atomic production claim storage. See `docs/limitations.md`.

### Reference specifications (verified 2026-10-08)

- [Circle — native USDC on Base vs USDbC](https://www.circle.com/blog/usdc-now-available-natively-on-base)
- [EIP-20 token standard](https://eips.ethereum.org/EIPS/eip-20)
- [x402 exact scheme — payment proof and duplicate-delivery handling](https://github.com/x402-foundation/x402/blob/main/specs/schemes/exact/scheme_exact.md)
- [x402 v2 specification](https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md)

### License & provenance

The original fixture generator, synthetic dataset, schema, CLI, tests and static preview were created for this kit, with no external illustrations or paid assets. See `LICENSE`. The real-world token contract addresses listed here are public facts; no wallet private keys or secrets are included.
