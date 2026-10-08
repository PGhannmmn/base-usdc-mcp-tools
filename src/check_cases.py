"""Run offline expectations. No dependencies beyond Python stdlib."""
import argparse
import json
from pathlib import Path
from fixturekit import evaluate, load_cases, verify_document

ROOT = Path(__file__).resolve().parents[1]

def run(path: Path, case_id: str | None, json_output: bool) -> int:
    document = load_cases(path)
    errors = verify_document(document)
    cases = document['cases'] if not case_id else [c for c in document['cases'] if c['id']==case_id]
    if not cases:
        raise SystemExit(f'No such case id: {case_id}')
    rows=[]
    for case in cases:
        result=evaluate(case)
        passed=result['code']==case['expected']
        rows.append(dict(id=case['id'],expected=case['expected'],actual=result['code'],passed=passed,
                         claim_key=result['claim_key']))
    passed=sum(row['passed'] for row in rows)
    if json_output:
        print(json.dumps({'total':len(rows),'passed':passed,'failures':errors+[r['id'] for r in rows if not r['passed']], 'results':rows},indent=2))
    else:
        for row in rows:
            print(f'{"PASS" if row["passed"] else "FAIL"} {row["id"]:<29} expected={row["expected"]:<22} actual={row["actual"]}')
        print(f'RESULT {passed}/{len(rows)} passed; structural_errors={len(errors)}')
        for error in errors: print('ERROR',error)
    return 0 if passed == len(rows) and not errors else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Synthetic Base USDC fixture runner; offline only')
    parser.add_argument('--path',type=Path,default=ROOT/'fixtures'/'scenarios.json')
    parser.add_argument('--case',help='Only run one case id')
    parser.add_argument('--json',action='store_true',help='Machine-readable report')
    args=parser.parse_args()
    raise SystemExit(run(args.path,args.case,args.json))
