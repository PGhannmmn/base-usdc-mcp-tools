# Boundaries & limitations

**A passing test is a passing synthetic expectation only. It does not demonstrate real-chain verification.**

This kit illustrates deterministic decision logic applied to invented `rpc_views`. It does **not**:

1. Fetch a live transaction, token metadata, finality signals or contract state from any network.
2. Verify RPC provenance, consensus, chain state proofs, reorg risk, or independence of upstream RPC providers.
3. Check EIP-712 signatures, EIP-3009 authorization, x402 facilitator status, payer identity or token transfer ownership.
4. Cryptographically bind a transaction proof to a particular order: `binding_verified` is a synthetic upstream boolean and must **never** be trusted when sent by an end user.
5. Atomically claim a transfer proof in a durable multi-process database. `prior_claim_keys` is just an injected hypothetical history.
6. Deliver paid downloads or implement refund, dispute, expiry and recovery policies.
7. Establish merchant eligibility, consumer law compliance, tax treatment or any saleability of a data product.

The evaluator has fail-closed behavior for common invalid mock fields, but should never be considered a security audit. A real implementation also needs strong input-size bounds, RPC error handling, token code/metadata validation, explicit proof-to-request binding (such as a per-order unique recipient/instrument), a protocol-defined finality policy, durable atomic idempotency, and independent adversarial security testing.

**Specific pitfalls illustrated**

- Native Base USDC is not interchangeable with bridged USDbC.
- A transaction can emit more than one ERC-20 Transfer; proof identity includes the log index, and an incorrectly constructed claim key can enable double delivery or block valid independent payments.
- A valid-looking transfer log alone is not enough. Check the native token address, network, payer, recipient, amount, transaction receipt status, and provider consensus.
- Wrong amounts do not become payable simply because the token has six decimals. Raw data amounts are integer atomic units.
- Finalized head numbers inside synthetic JSON are assertions, not verified proofs; local agreement can be faked.
- Duplicate submission and duplicate delivery are distinct. The x402 exact scheme describes atomic claim requirements for client-submitted proofs.

**No network:** All supplied command examples are offline. No real USDC, gas, wallet connection, block explorer call, third-party API, or paid AI service is needed.
