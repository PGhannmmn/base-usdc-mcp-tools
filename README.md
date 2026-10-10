# Base USDC Tools

Public static landing page for three independent Base mainnet MCP services.

Website: https://PGhannmmn.github.io/base-usdc-mcp-tools/

## Static files

- index.html: responsive landing page with inline CSS; no JavaScript or trackers.
- llms.txt: service descriptions, endpoints and pricing.
- robots.txt: crawler allowance.

## Pricing

| Service | Package | Protected operation |
| --- | --- | --- |
| 003 Receivables Auditor | 0.12 USDC / 100 credits | 10 credits / report |
| 002 Payment Assurance | 0.11 USDC / 100 credits | 1 credit / call |
| 001E Hash Encoding | 0.10 USDC / 100 credits | 1 credit / call |

Buyer pays Base gas. Direct prepaid credits; not x402. Check each service's live payment information before purchasing.

This repository contains only public static website files. It contains no service implementation, credentials, payment ledger or deployment configuration. The site does not collect wallet credentials or accept payments itself.

GitHub Pages: deploy from main, root directory. No custom domain or secrets are required.

## Free developer QA fixtures

[Base USDC Payment QA Fixture Kit](https://pghannmmn.github.io/base-usdc-mcp-tools/qa-fixture-kit/) is a separate, **free and offline synthetic testing resource** for developers: 35 deterministic ERC-20 payment scenarios, JSON fixtures, Python reference checks and an HTML case browser. [View the dedicated preview branch](https://github.com/PGhannmmn/base-usdc-mcp-tools/tree/preview/base-usdc-payment-qa-v0.1) or [the downloadable prerelease](https://github.com/PGhannmmn/base-usdc-mcp-tools/releases/tag/qa-fixture-kit-v0.1.0).

**Never treat synthetic QA results as real payment verification or authorization.** The kit does not call RPCs, validate real chain state, sign transactions or grant paid access. It is independent of all three paid MCP services.

## Experiment 003 pilot interest (opt-in)

Are you working with Base USDC receivables and interested in a small, read-only product pilot or feedback conversation? [Open the 003 pilot interest form](https://github.com/PGhannmmn/base-usdc-mcp-tools/issues/new?template=003-pilot.yml).

This is a **public GitHub Issue** (GitHub login required). Do not post credentials, seed phrases, bearer tokens, confidential wallet/transaction data or customer information. Submitting does not guarantee a free trial, access, or feature delivery. The current service still uses its posted direct-USDC credit pricing. No unsolicited outreach is conducted.
