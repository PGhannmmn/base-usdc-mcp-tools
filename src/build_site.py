"""Build a standalone, fully offline static case browser; no external assets."""
from __future__ import annotations
from collections import Counter
import html
from pathlib import Path
from fixturekit import load_cases

ROOT=Path(__file__).resolve().parents[1]
doc=load_cases(ROOT/'fixtures'/'scenarios.json')
cs=doc['cases']
counts=Counter(c['expected'] for c in cs)
html_safe=html.escape
rows='\n'.join(f'''<article class="case" tabindex="0" data-code="{html_safe(c['expected'])}" data-search="{html_safe((c['id']+' '+c['description']+' '+c['expected']).lower(),quote=True)}">
<div class="casehead"><span class="caseid">{html_safe(c['id'])}</span><span class="status {'good' if c['expected']=='ACCEPT' else 'bad'}">{html_safe(c['expected'])}</span></div>
<p>{html_safe(c['description'])}</p></article>''' for c in cs)
html_page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Offline synthetic Base USDC payment QA fixture browser. 35 deterministic test cases, zero networking.">
<title>Base USDC · Payment QA Fixtures</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#111e31;--line:#283851;--text:#eef5ff;--muted:#9fb0c6;--mint:#5ddfbd;--coral:#ffa68c}
*{box-sizing:border-box}body{margin:0;font:15px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;background:radial-gradient(650px 400px at 100% 0,#163952 0,transparent 74%),var(--bg);color:var(--text)}
a{color:var(--mint)}.wrap{max-width:1120px;margin:auto;padding:32px 24px 80px}header{border-bottom:1px solid var(--line);padding-bottom:28px}
.eyebrow{font-size:12px;font-weight:750;color:var(--mint);letter-spacing:.13em;text-transform:uppercase}h1{font-size:clamp(30px,6vw,55px);line-height:1.1;letter-spacing:-.05em;margin:16px 0}h2{font-size:21px;margin:0 0 10px}p{margin:10px 0 0;color:var(--muted)}
.hero{max-width:850px;font-size:17px}.warn{border:1px solid #735c31;background:#2c261d;border-radius:12px;padding:16px 20px;margin-top:25px;color:#ffdfad}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:25px 0 32px}.stat{border:1px solid var(--line);background:var(--panel);padding:22px;border-radius:14px}.stat strong{display:block;font-size:32px;line-height:1.2}.stat small{color:var(--muted)}
.controls{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.controls input,.controls select{background:#142338;border:1px solid #526580;color:var(--text);padding:11px 12px;border-radius:9px;min-height:45px;flex:1}.controls select{flex:0 0 190px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.case{border:1px solid var(--line);background:var(--panel);padding:17px 18px;border-radius:11px;min-height:120px}.casehead{display:flex;gap:8px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}.caseid{font-size:14px;font-weight:730;overflow-wrap:anywhere}.status{font-size:10px;font-weight:800;border-radius:6px;padding:4px 6px;letter-spacing:.05em}.good{color:#5ddfbd;background:#12392e}.bad{color:#ffbb9e;background:#422a2a}.case p{font-size:13px;margin-top:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#09101b;border:1px solid var(--line);padding:22px;border-radius:12px;color:#d3e4ff}footer{color:var(--muted);border-top:1px solid var(--line);margin-top:45px;padding-top:22px}.noresult{display:none;padding:20px;color:var(--muted)}:focus-visible{outline:2px solid var(--mint);outline-offset:2px}
@media(max-width:700px){.wrap{padding:25px 16px 50px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr}.controls select{flex:1 1 100%}}
</style></head><body><div class="wrap">
<header><span class="eyebrow">Free Developer Preview · v0.1.0 · 100% Offline</span><h1>Base USDC<br>Payment QA Fixtures</h1><p class="hero">Test payment verification edge cases with deterministic, synthetic ERC-20 event logs. No live RPC, wallet, private keys, gas or API costs.</p>
<div class="warn"><strong>Not a payment verifier.</strong> All data is invented. This package cannot validate real transactions, x402 authorizations or safely grant paid access.</div></header>
<section class="stats" aria-label="Dataset details"><div class="stat"><strong>__CASE_COUNT__</strong><small>Synthetic fixtures</small></div><div class="stat"><strong>__CODE_COUNT__</strong><small>Expected outcomes</small></div><div class="stat"><strong>$0</strong><small>External dependencies</small></div></section>
<section aria-labelledby="cases-head"><h2 id="cases-head">Explore scenarios <span id="visible" style="color:var(--muted);font-size:14px;font-weight:normal">__CASE_COUNT__ showing</span></h2>
<div class="controls"><label style="flex:1"><span class="eyebrow">Search</span><input id="search" type="search" placeholder="Try: replay, recipient, USDbC…" aria-label="Filter scenario descriptions"></label><label><span class="eyebrow">Result</span><select id="filter" aria-label="Filter by expected classification"><option value="">All outcomes</option>__OUTCOMES__</select></label></div>
<div id="cards" class="grid">__ROWS__</div><p class="noresult" id="none">No matching fixtures.</p></section>
<section style="margin-top:42px"><h2>Run the checks</h2><p>Python 3.10+ and the standard library are sufficient. Use commands from the extracted kit root:</p>
<pre>python src/check_cases.py
python src/check_cases.py --case bridged-usdbc
python -m unittest discover -s tests -v</pre></section>
<footer>Offline demonstration · Synthetic Base network metadata · Public ERC-20 token addresses are used only as test constants · No live verification</footer>
</div><script>
const items=[...document.querySelectorAll('.case')]; const search=document.getElementById('search');const filter=document.getElementById('filter');
function update(){const q=search.value.toLowerCase().trim(),f=filter.value;let n=0;for(const el of items){const show=(!q||el.dataset.search.includes(q))&&(!f||el.dataset.code===f);el.hidden=!show;if(show)n++;}document.getElementById('visible').textContent=n+' showing';document.getElementById('none').style.display=n?'none':'block';}
search.addEventListener('input',update);filter.addEventListener('change',update);
</script></body></html>
'''
outcomes=''.join(f'<option value="{html_safe(k)}">{html_safe(k)} ({v})</option>' for k,v in sorted(counts.items()))
html_page=html_page.replace('__CASE_COUNT__',str(len(cs))).replace('__CODE_COUNT__',str(len(counts))).replace('__ROWS__',rows).replace('__OUTCOMES__',outcomes)
(ROOT/'site'/'index.html').write_text(html_page,encoding='utf-8')
(ROOT/'docs'/'case-matrix.md').write_text('# Scenario matrix\n\nAll input snapshots and transaction IDs are synthetic.\n\n| ID | Expected outcome | Description |\n|---|---|---|\n'+''.join(f'| `{c["id"]}` | `{c["expected"]}` | {c["description"].replace("|", "\\|")} |\n' for c in cs),encoding='utf-8')
print(f'built standalone HTML preview and case matrix: {len(cs)} cases, {len(counts)} outcomes')
