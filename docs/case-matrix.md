# Scenario matrix

All input snapshots and transaction IDs are synthetic.

| ID | Expected outcome | Description |
|---|---|---|
| `happy-path` | `ACCEPT` | Exact 1 USDC native transfer, two agreeing finalized snapshots. |
| `case-insensitive-address` | `ACCEPT` | Mixed-case input address still matches ERC-20 fields. |
| `wrong-order-network` | `WRONG_NETWORK` | Order asks for an unsupported EVM network. |
| `wrong-proof-network` | `WRONG_NETWORK` | Proof network claims Ethereum L1. |
| `rpc-on-other-chain` | `WRONG_NETWORK` | RPC views report a different chain ID. |
| `bridged-usdbc` | `WRONG_ASSET` | USDbC log cannot fulfill a native USDC order. |
| `wrong-order-token` | `WRONG_ASSET` | Order requests bridged token instead of native USDC. |
| `wrong-payer` | `WRONG_PAYER` | Transfer sender does not match bound order payer. |
| `wrong-recipient` | `WRONG_RECIPIENT` | Transfer paid to a different wallet. |
| `underpayment` | `UNDERPAYMENT` | 999999 atomic units is less than the required 1000000. |
| `overpayment` | `OVERPAYMENT` | Exact-match policy rejects 1000001 atomic units. |
| `wrong-decimals` | `WRONG_DECIMALS` | Order metadata mistakenly declares 18 decimals instead of 6. |
| `failed-receipt` | `TX_FAILED` | Receipt status indicates reverted transaction. |
| `pending-both` | `PENDING` | Both providers have no receipt yet. |
| `receipt-missing-on-one` | `RPC_DISAGREEMENT` | One provider sees receipt while the other does not. |
| `not-finalized` | `NOT_FINALIZED` | One provider finalized head remains below tx block. |
| `rpc-disagrees-receipt` | `RPC_DISAGREEMENT` | Two RPC providers return different amounts. |
| `rpc-unavailable` | `RPC_UNAVAILABLE` | One independent RPC is unavailable. |
| `no-matching-log` | `LOG_NOT_FOUND` | Proof points at a log index not found in the receipt. |
| `not-transfer-event` | `NOT_TRANSFER_EVENT` | Indexed event has wrong topic0, not ERC-20 Transfer. |
| `malformed-topic-count` | `MALFORMED_LOG` | Only two topics for an indexed ERC-20 Transfer. |
| `malformed-amount-data` | `MALFORMED_LOG` | Transfer data is not 32 bytes. |
| `bad-address-padding` | `MALFORMED_LOG` | Indexed address topic has nonzero high padding. |
| `log-removed` | `REMOVED_LOG` | Reorg-removed log is not valid evidence. |
| `log-tx-hash-mismatch` | `MALFORMED_LOG` | Log claims a different transaction hash. |
| `receipt-tx-hash-mismatch` | `TX_HASH_MISMATCH` | Receipt tx hash does not equal supplied proof hash. |
| `two-logs-select-first` | `ACCEPT` | Two valid transfers in one tx; log index 0 is uniquely selected. |
| `two-logs-select-second` | `ACCEPT` | Second independent log in same tx may have unique claim key. |
| `replay-claimed-proof` | `REPLAY` | Same (network, transaction, log index) proof was previously consumed. |
| `other-log-already-claimed` | `ACCEPT` | Claim of log 1 is not blocked solely because log 0 was consumed. |
| `duplicate-log-index` | `DUPLICATE_LOG_INDEX` | Malformed receipt repeats logIndex 0 for multiple logs. |
| `unverified-order-binding` | `BINDING_UNVERIFIED` | No trusted per-order binding attestation. |
| `missing-proof-hash` | `INVALID_PROOF` | Missing transaction hash is rejected. |
| `zero-amount-order` | `INVALID_AMOUNT` | Zero amount has no payable order semantics. |
| `invalid-status` | `MALFORMED_RECEIPT` | Receipt has invalid status rather than 0x0 or 0x1. |
