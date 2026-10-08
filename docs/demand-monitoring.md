# Product-specific interest measurement — v0.1

## Source of evidence

- Public feedback: https://github.com/PGhannmmn/base-usdc-mcp-tools/issues/1
- Run the stdlib-only script from this branch: `python scripts/public_interest.py PGhannmmn/base-usdc-mcp-tools`
- The script reports unique independent commenters (excluding owner and GitHub bots), total potential external comments, and last comment date.
- Every response is **potential** feedback; independent qualitative review is required to exclude spam, irrelevant comments and duplicates across accounts.
- We do **not** claim real-world user adoption, product downloads, installations, real purchases, or willingness to pay based on comments.

## What is not measured

- GitHub archive/branch ZIP download counts: no trustworthy public per-branch counter is exposed.
- Repository-level stars, forks, traffic, views or clones: they mix the existing Base USDC services with this experimental kit.
- GitHub issue comment totals alone: may include the repository owner or spam.
- GitHub release asset download counts: no product release asset is published.
- Search Console: the preview is not deployed to the live indexed GitHub Pages site.

## Decision rule

Before investing in a paid storefront, seek at least 3 independent developer feedback reports with a specific workflow or missing-case need. **Even this is weak evidence, not proof of willingness to pay.** If there is no activity after 30 days, mark as "no measurable feedback", not "no demand". Do not fabricate visits, downloads or conversions.

## Security and scope

Read-only public GitHub REST API only. No tracking pixels, user identification database, credentials, transactions, wallets or marketing automation.
This file and script live only on the preview branch. GitHub Actions on the default branch are not modified and no schedule is enabled by these files.
