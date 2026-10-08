"""Offline deterministic evaluator for synthetic Base USDC ERC-20 receipt fixtures.

This is a teaching/testing oracle, NOT an RPC client or production payment verifier.
Inputs, including the trusted binding flag and RPC snapshots, are simulated.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

NETWORK = 'eip155:8453'
NATIVE_USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'.lower()
BRIDGED_USDBC = '0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'.lower()
TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ADDRESS_RE = re.compile(r'^0x[0-9a-fA-F]{40}$')
HASH_RE = re.compile(r'^0x[0-9a-fA-F]{64}$')
HEX_RE = re.compile(r'^0x[0-9a-fA-F]+$')
DEC_RE = re.compile(r'^(0|[1-9][0-9]*)$')


def consumption_key(network: str, tx_hash: str, log_index: int) -> str:
    """Canonical synthetic single-use key, per Transfer log (not entire tx)."""
    return f'{network.lower()}:{tx_hash.lower()}:{log_index}'


def _int_hex(s: str) -> int:
    if not isinstance(s, str) or not HEX_RE.fullmatch(s):
        raise ValueError('not hex')
    return int(s, 16)


def _addr(s: str) -> str:
    if not isinstance(s, str) or not ADDRESS_RE.fullmatch(s):
        raise ValueError('invalid address')
    return s.lower()


def _topic_address(topic: str) -> str:
    if not isinstance(topic, str) or not HASH_RE.fullmatch(topic):
        raise ValueError('invalid topic')
    if topic[2:26].lower() != '0' * 24:
        raise ValueError('nonzero address padding')
    return _addr('0x' + topic[-40:])


def _out(code: str, key: str | None = None) -> dict:
    return {'code': code, 'claim_key': key if code == 'ACCEPT' else None}


def evaluate(case: dict) -> dict:
    """Fail-closed deterministic classification of *mocked* reports. No live verification."""
    try:
        order, proof = case['order'], case['proof']
        if order['binding_verified'] is not True:
            return _out('BINDING_UNVERIFIED')
        if order['network'] != NETWORK or proof['network'] != NETWORK:
            return _out('WRONG_NETWORK')
        if _addr(order['asset']) != NATIVE_USDC:
            return _out('WRONG_ASSET')
        if type(order['decimals']) is not int or order['decimals'] != 6:
            return _out('WRONG_DECIMALS')
        recipient = _addr(order['recipient'])
        payer = _addr(order['payer'])
        amt = order['amount_atomic']
        if not isinstance(amt, str) or DEC_RE.fullmatch(amt) is None or int(amt) <= 0:
            return _out('INVALID_AMOUNT')
        tx = proof['transaction_hash']
        if not isinstance(tx, str) or HASH_RE.fullmatch(tx) is None:
            return _out('INVALID_PROOF')
        if isinstance(proof['log_index'], bool) or not isinstance(proof['log_index'], int) or proof['log_index'] < 0:
            return _out('INVALID_PROOF')
        key = consumption_key(NETWORK, tx, proof['log_index'])
        prior = case['prior_claim_keys']
        if not isinstance(prior, list) or not all(isinstance(k, str) for k in prior):
            return _out('INVALID_FIXTURE')
        if key in prior:
            return _out('REPLAY')
        views = case['rpc_views']
        if not isinstance(views, list) or len(views) != 2 or views[0]['provider'] == views[1]['provider']:
            return _out('INVALID_FIXTURE')
        if any(v['available'] is not True for v in views):
            return _out('RPC_UNAVAILABLE')
        if any(v['chain_id'] != 8453 for v in views):
            return _out('WRONG_NETWORK')
        receipts = [v['receipt'] for v in views]
        if all(r is None for r in receipts):
            return _out('PENDING')
        if any(r is None for r in receipts) or receipts[0] != receipts[1]:
            return _out('RPC_DISAGREEMENT')
        receipt = receipts[0]
        if receipt['transaction_hash'].lower() != tx.lower():
            return _out('TX_HASH_MISMATCH')
        if receipt['status'] == '0x0':
            return _out('TX_FAILED')
        if receipt['status'] != '0x1':
            return _out('MALFORMED_RECEIPT')
        block = receipt['block_number']
        if type(block) is not int or block < 0:
            return _out('MALFORMED_RECEIPT')
        if any(type(v['finalized_block']) is not int or v['finalized_block'] < block for v in views):
            return _out('NOT_FINALIZED')
        logs = receipt['logs']
        if not isinstance(logs, list):
            return _out('MALFORMED_RECEIPT')
        indices = []
        for log in logs:
            ix = _int_hex(log['log_index'])
            if log['transaction_hash'].lower() != tx.lower() or not isinstance(log.get('removed'), bool):
                return _out('MALFORMED_LOG')
            indices.append(ix)
        if len(indices) != len(set(indices)):
            return _out('DUPLICATE_LOG_INDEX')
        found = [l for l, ix in zip(logs, indices) if ix == proof['log_index']]
        if not found:
            return _out('LOG_NOT_FOUND')
        log = found[0]
        if log['removed']:
            return _out('REMOVED_LOG')
        if _addr(log['address']) != NATIVE_USDC:
            return _out('WRONG_ASSET')
        topics = log['topics']
        if not isinstance(topics, list) or len(topics) != 3:
            return _out('MALFORMED_LOG')
        if topics[0].lower() != TRANSFER_TOPIC:
            return _out('NOT_TRANSFER_EVENT')
        try:
            from_addr, to_addr = _topic_address(topics[1]), _topic_address(topics[2])
        except (ValueError, TypeError):
            return _out('MALFORMED_LOG')
        if from_addr != payer:
            return _out('WRONG_PAYER')
        if to_addr != recipient:
            return _out('WRONG_RECIPIENT')
        data = log['data']
        if not isinstance(data, str) or not HASH_RE.fullmatch(data):
            return _out('MALFORMED_LOG')
        actual = int(data, 16)
        required = int(amt)
        if actual < required:
            return _out('UNDERPAYMENT')
        if actual > required:
            return _out('OVERPAYMENT')
        return _out('ACCEPT', key)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return _out('MALFORMED_FIXTURE')


def load_cases(path: str | Path) -> dict:
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def verify_document(document: dict) -> list[str]:
    """Lightweight built-in document validation; optional JSON Schema validation via jsonschema."""
    errors = []
    if not isinstance(document, dict) or document.get('version') != '0.1.0' or not isinstance(document.get('cases'), list):
        return ['invalid document root/version/cases']
    ids = set()
    if not document['cases']:
        errors.append('empty cases')
    for idx, case in enumerate(document['cases']):
        if not isinstance(case, dict):
            errors.append(f'case #{idx} not object')
            continue
        cid = case.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'[a-z0-9-]+', cid):
            errors.append(f'case #{idx} invalid id')
        if cid in ids:
            errors.append(f'duplicate id {cid}')
        ids.add(cid)
        if not isinstance(case.get('expected'), str):
            errors.append(f'case {cid}: expected missing')
        if not isinstance(case.get('description'), str) or not case['description']:
            errors.append(f'case {cid}: description missing')
        got = evaluate(case)['code']
        if got == 'MALFORMED_FIXTURE' or got == 'INVALID_FIXTURE':
            errors.append(f'case {cid}: malformed input')
    return errors
