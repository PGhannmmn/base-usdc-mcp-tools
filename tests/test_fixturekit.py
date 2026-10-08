"""Unit and regression tests; network-free, standard-library only."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from fixturekit import (BRIDGED_USDBC, NATIVE_USDC, NETWORK, consumption_key,
                        evaluate, load_cases, verify_document)
from build_fixtures import generate

DATA = ROOT / 'fixtures/scenarios.json'

class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=load_cases(DATA)
        cls.cases={c['id']:c for c in cls.doc['cases']}

    def test_all_expected_results(self):
        for cid,case in self.cases.items():
            with self.subTest(cid=cid):
                self.assertEqual(evaluate(case)['code'],case['expected'])

    def test_at_least_30_scenarios(self):
        self.assertGreaterEqual(len(self.cases),30)

    def test_all_ids_unique(self):
        self.assertEqual(len(self.cases),len(self.doc['cases']))

    def test_valid_envelope(self):
        self.assertEqual(verify_document(self.doc),[])

    def test_generated_exactly_matches_shipped_fixtures(self):
        self.assertEqual(generate(),self.doc)

    def test_gen_is_deterministic(self):
        self.assertEqual(generate(),generate())

    def test_chain_asset_constants(self):
        self.assertEqual(NETWORK,'eip155:8453')
        self.assertEqual(NATIVE_USDC,'0x833589fcd6edb6e08f4c7c32d4f71b54bda02913')
        self.assertNotEqual(NATIVE_USDC,BRIDGED_USDBC)

    def test_all_proof_hashes_are_synthetic(self):
        # All values were generated from stable synthetic prefix; check exact regeneration.
        self.assertEqual(self.doc, generate())

    def test_claim_key_canonical(self):
        one=self.cases['happy-path']
        p=one['proof']
        self.assertEqual(consumption_key(NETWORK,p['transaction_hash'].upper().replace('0X','0x'),0),
                         consumption_key(NETWORK,p['transaction_hash'],0))

    def test_claim_0_does_not_block_claim_1(self):
        one=self.cases['other-log-already-claimed']
        self.assertEqual(evaluate(one)['code'],'ACCEPT')
        self.assertNotEqual(evaluate(one)['claim_key'],one['prior_claim_keys'][0])

    def test_replay_mutation_fails_closed(self):
        case=copy.deepcopy(self.cases['happy-path'])
        k=evaluate(case)['claim_key']
        case['prior_claim_keys'].append(k)
        self.assertEqual(evaluate(case)['code'],'REPLAY')

    def test_mutating_recipient_is_rejected(self):
        case=copy.deepcopy(self.cases['happy-path'])
        case['order']['recipient']='0x'+'ee'*20
        self.assertEqual(evaluate(case)['code'],'WRONG_RECIPIENT')

    def test_mutating_token_is_rejected(self):
        case=copy.deepcopy(self.cases['happy-path'])
        for v in case['rpc_views']:v['receipt']['logs'][0]['address']=BRIDGED_USDBC
        self.assertEqual(evaluate(case)['code'],'WRONG_ASSET')

    def test_rpc_disagreement_fails_closed(self):
        case=copy.deepcopy(self.cases['happy-path'])
        case['rpc_views'][1]['receipt']['logs'][0]['data']='0x'+'00'*32
        self.assertEqual(evaluate(case)['code'],'RPC_DISAGREEMENT')

    def test_unfinalized_fails_closed(self):
        case=copy.deepcopy(self.cases['happy-path'])
        case['rpc_views'][0]['finalized_block']=999
        self.assertEqual(evaluate(case)['code'],'NOT_FINALIZED')

    def test_malformed_input_fails_closed(self):
        case=copy.deepcopy(self.cases['happy-path'])
        del case['order']['payer']
        self.assertEqual(evaluate(case)['code'],'MALFORMED_FIXTURE')

    def test_zero_price_rejected(self):
        case=copy.deepcopy(self.cases['happy-path'])
        case['order']['amount_atomic']='0'
        self.assertEqual(evaluate(case)['code'],'INVALID_AMOUNT')

    def test_no_network_deps_in_package(self):
        for f in (ROOT/'src').glob('*.py'):
            txt=f.read_text()
            self.assertNotIn('requests.get(',txt)
            self.assertNotIn('urllib.request',txt)

    def test_schema_is_json(self):
        schema=json.loads((ROOT/'schema'/'scenarios.schema.json').read_text())
        self.assertEqual(schema['$schema'],'https://json-schema.org/draft/2020-12/schema')

    def test_cli_success(self):
        p=subprocess.run([sys.executable, str(ROOT/'src'/'check_cases.py'), '--json'],
                         capture_output=True,text=True,check=False)
        self.assertEqual(p.returncode,0,p.stderr+p.stdout[:800])
        self.assertEqual(json.loads(p.stdout)['passed'],len(self.doc['cases']))

if __name__=='__main__':unittest.main()
