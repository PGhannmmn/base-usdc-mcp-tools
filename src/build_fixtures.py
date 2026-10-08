"""Deterministic generator. All proof hashes, wallets and RPC reports are synthetic."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from fixturekit import (NATIVE_USDC, BRIDGED_USDBC, TRANSFER_TOPIC, NETWORK, consumption_key)

ROOT = Path(__file__).resolve().parents[1]
PAYER = '0x' + '11' * 20
RECIPIENT = '0x' + '22' * 20
OTHER = '0x' + '33' * 20

def txhash(tag: str) -> str:
    # Non-broadcast SHA-256 fake identifier. NO corresponding transactions.
    return '0x' + hashlib.sha256(('synthetic-qa-fixture:' + tag).encode()).hexdigest()

def topic_addr(address: str) -> str:
    return '0x' + ('0' * 24) + address[2:].lower()

def make_log(tx: str, index: int, *, amount=1_000_000, token=NATIVE_USDC,
             sender=PAYER, receiver=RECIPIENT, topic=TRANSFER_TOPIC):
    return dict(address=token, topics=[topic,topic_addr(sender),topic_addr(receiver)],
                data='0x' + format(amount, '064x'), log_index=hex(index),
                transaction_hash=tx, removed=False)

def make_case(cid, description, *, tx_tag=None):
    tx = txhash(tx_tag or cid)
    rec = {'transaction_hash':tx, 'status':'0x1', 'block_number':1000,
           'logs':[make_log(tx, 0)]}
    return dict(id=cid, description=description,
                assumptions='All RPC views and order-binding attestations are invented input; no network checks.',
                expected='ACCEPT',
                order={'order_id':f'order-{cid}', 'network':NETWORK, 'asset':NATIVE_USDC,
                       'recipient':RECIPIENT, 'payer':PAYER, 'amount_atomic':'1000000',
                       'decimals':6, 'binding_verified':True},
                proof={'network':NETWORK,'transaction_hash':tx,'log_index':0},
                prior_claim_keys=[],
                rpc_views=[{'provider':'synthetic-rpc-a','chain_id':8453,'available':True,
                            'finalized_block':1001,'receipt':deepcopy(rec)},
                           {'provider':'synthetic-rpc-b','chain_id':8453,'available':True,
                            'finalized_block':1000,'receipt':deepcopy(rec)}])

def sync(c):
    c['rpc_views'][1]['receipt'] = deepcopy(c['rpc_views'][0]['receipt'])
    return c

def generate():
    cases = []
    def add(cid, descr, expected, mutate=None, *, tx_tag=None):
        c = make_case(cid, descr, tx_tag=tx_tag)
        if mutate: mutate(c)
        c['expected'] = expected
        cases.append(c)
        return c
    add('happy-path', 'Exact 1 USDC native transfer, two agreeing finalized snapshots.', 'ACCEPT')
    add('case-insensitive-address', 'Mixed-case input address still matches ERC-20 fields.', 'ACCEPT', lambda c: c['order'].update(recipient=RECIPIENT.upper().replace('0X', '0x')))
    add('wrong-order-network', 'Order asks for an unsupported EVM network.', 'WRONG_NETWORK', lambda c: c['order'].update(network='eip155:1'))
    add('wrong-proof-network', 'Proof network claims Ethereum L1.', 'WRONG_NETWORK', lambda c: c['proof'].update(network='eip155:1'))
    add('rpc-on-other-chain', 'RPC views report a different chain ID.', 'WRONG_NETWORK', lambda c: [v.update(chain_id=1) for v in c['rpc_views']])
    add('bridged-usdbc', 'USDbC log cannot fulfill a native USDC order.', 'WRONG_ASSET', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(address=BRIDGED_USDBC),sync(c)])
    add('wrong-order-token', 'Order requests bridged token instead of native USDC.', 'WRONG_ASSET', lambda c: c['order'].update(asset=BRIDGED_USDBC))
    add('wrong-payer', 'Transfer sender does not match bound order payer.', 'WRONG_PAYER', lambda c: [c['rpc_views'][0]['receipt']['logs'][0]['topics'].__setitem__(1,topic_addr(OTHER)),sync(c)])
    add('wrong-recipient', 'Transfer paid to a different wallet.', 'WRONG_RECIPIENT', lambda c: [c['rpc_views'][0]['receipt']['logs'][0]['topics'].__setitem__(2,topic_addr(OTHER)),sync(c)])
    add('underpayment', '999999 atomic units is less than the required 1000000.', 'UNDERPAYMENT', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(data='0x'+format(999999,'064x')),sync(c)])
    add('overpayment', 'Exact-match policy rejects 1000001 atomic units.', 'OVERPAYMENT', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(data='0x'+format(1000001,'064x')),sync(c)])
    add('wrong-decimals', 'Order metadata mistakenly declares 18 decimals instead of 6.', 'WRONG_DECIMALS', lambda c: c['order'].update(decimals=18))
    add('failed-receipt', 'Receipt status indicates reverted transaction.', 'TX_FAILED', lambda c: [c['rpc_views'][0]['receipt'].update(status='0x0'),sync(c)])
    add('pending-both', 'Both providers have no receipt yet.', 'PENDING', lambda c: [v.update(receipt=None) for v in c['rpc_views']])
    add('receipt-missing-on-one', 'One provider sees receipt while the other does not.', 'RPC_DISAGREEMENT', lambda c: c['rpc_views'][1].update(receipt=None))
    add('not-finalized', 'One provider finalized head remains below tx block.', 'NOT_FINALIZED', lambda c: c['rpc_views'][1].update(finalized_block=999))
    add('rpc-disagrees-receipt', 'Two RPC providers return different amounts.', 'RPC_DISAGREEMENT', lambda c: c['rpc_views'][1]['receipt']['logs'][0].update(data='0x'+format(1,'064x')))
    add('rpc-unavailable', 'One independent RPC is unavailable.', 'RPC_UNAVAILABLE', lambda c: c['rpc_views'][1].update(available=False))
    add('no-matching-log', 'Proof points at a log index not found in the receipt.', 'LOG_NOT_FOUND', lambda c: c['proof'].update(log_index=5))
    add('not-transfer-event', 'Indexed event has wrong topic0, not ERC-20 Transfer.', 'NOT_TRANSFER_EVENT', lambda c: [c['rpc_views'][0]['receipt']['logs'][0]['topics'].__setitem__(0, '0x'+'00'*32),sync(c)])
    add('malformed-topic-count', 'Only two topics for an indexed ERC-20 Transfer.', 'MALFORMED_LOG', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(topics=[TRANSFER_TOPIC,topic_addr(PAYER)]),sync(c)])
    add('malformed-amount-data', 'Transfer data is not 32 bytes.', 'MALFORMED_LOG', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(data='0x10'),sync(c)])
    add('bad-address-padding', 'Indexed address topic has nonzero high padding.', 'MALFORMED_LOG', lambda c: [c['rpc_views'][0]['receipt']['logs'][0]['topics'].__setitem__(1, '0x'+'ff'*12+PAYER[2:]),sync(c)])
    add('log-removed', 'Reorg-removed log is not valid evidence.', 'REMOVED_LOG', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(removed=True),sync(c)])
    add('log-tx-hash-mismatch', 'Log claims a different transaction hash.', 'MALFORMED_LOG', lambda c: [c['rpc_views'][0]['receipt']['logs'][0].update(transaction_hash=txhash('OTHER')),sync(c)])
    add('receipt-tx-hash-mismatch', 'Receipt tx hash does not equal supplied proof hash.', 'TX_HASH_MISMATCH', lambda c: [c['rpc_views'][0]['receipt'].update(transaction_hash=txhash('OTHER')),sync(c)])
    add('two-logs-select-first', 'Two valid transfers in one tx; log index 0 is uniquely selected.', 'ACCEPT', lambda c: [c['rpc_views'][0]['receipt']['logs'].append(make_log(c['proof']['transaction_hash'],1)),sync(c)],tx_tag='multi-valid')
    add('two-logs-select-second', 'Second independent log in same tx may have unique claim key.', 'ACCEPT', lambda c: [c['proof'].update(log_index=1),c['rpc_views'][0]['receipt']['logs'].append(make_log(c['proof']['transaction_hash'],1)),sync(c)],tx_tag='multi-valid')
    add('replay-claimed-proof', 'Same (network, transaction, log index) proof was previously consumed.', 'REPLAY', lambda c: c['prior_claim_keys'].append(consumption_key(NETWORK,c['proof']['transaction_hash'],0)))
    add('other-log-already-claimed', 'Claim of log 1 is not blocked solely because log 0 was consumed.', 'ACCEPT', lambda c: [c['proof'].update(log_index=1),c['rpc_views'][0]['receipt']['logs'].append(make_log(c['proof']['transaction_hash'],1)), c['prior_claim_keys'].append(consumption_key(NETWORK,c['proof']['transaction_hash'],0)),sync(c)])
    add('duplicate-log-index', 'Malformed receipt repeats logIndex 0 for multiple logs.', 'DUPLICATE_LOG_INDEX', lambda c: [c['rpc_views'][0]['receipt']['logs'].append(make_log(c['proof']['transaction_hash'],0)),sync(c)])
    add('unverified-order-binding', 'No trusted per-order binding attestation.', 'BINDING_UNVERIFIED', lambda c: c['order'].update(binding_verified=False))
    add('missing-proof-hash', 'Missing transaction hash is rejected.', 'INVALID_PROOF', lambda c: c['proof'].update(transaction_hash='0x1234'))
    add('zero-amount-order', 'Zero amount has no payable order semantics.', 'INVALID_AMOUNT', lambda c: c['order'].update(amount_atomic='0'))
    add('invalid-status', 'Receipt has invalid status rather than 0x0 or 0x1.', 'MALFORMED_RECEIPT', lambda c: [c['rpc_views'][0]['receipt'].update(status='0x2'),sync(c)])
    return {'version':'0.1.0','dataset':'Base USDC Synthetic Payment QA Fixtures',
            'not_for_production':True,
            'description':'Synthetic, no real signatures, no real private keys, no broadcast RPC.',
            'cases':cases}

if __name__ == '__main__':
    data = generate()
    dst=ROOT/'fixtures'/'scenarios.json'
    dst.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'generated {len(data["cases"])} fixture cases: {dst}')
