# Base USDC Payment QA Fixture Kit v0.1.0 — free synthetic preview

A small, free **offline-only** dataset and test runner for Base USDC payment edge cases. Includes 35 deterministic synthetic fixtures, Python 3.10+ evaluator and CLI, JSON Schema, automated tests and a standalone HTML case browser. No dependencies are required to run the core tests.

- Download the ZIP asset attached to **this** prerelease; extract and run `python src/check_cases.py` then `python -m unittest discover -s tests -v`.
- [Browse case matrix](https://github.com/PGhannmmn/base-usdc-mcp-tools/blob/preview/base-usdc-payment-qa-v0.1/docs/case-matrix.md)
- [Report missing cases](https://github.com/PGhannmmn/base-usdc-mcp-tools/issues/1)

**Safety / product scope:** All receipts, transactions, RPC views and finality states are invented. The code is **not** a real payment verifier, gateway or on-chain oracle and must never be used to approve real-world payments or trigger paid deliveries. No wallets, blockchain calls or live RPC access are performed. This is a free developer preview, not part of the paid MCP services.

Published from the isolated `preview/base-usdc-payment-qa-v0.1` branch. GitHub Pages `main`, Cloudflare Workers and existing paid services are unchanged. Download counts for this release **asset** may be used as a limited demand signal; they do not establish actual active users or willingness to pay.
