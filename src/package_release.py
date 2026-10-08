"""Reproducible ZIP package builder; stdlib only."""
from __future__ import annotations
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
RELEASE='base-usdc-payment-qa-kit-v0.1.0'
DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True)
TARGET=DIST/(RELEASE+'.zip')
FILES=[x for x in ROOT.rglob('*') if x.is_file() and not any(p in ('dist','__pycache__','.git') for p in x.relative_to(ROOT).parts)]
FILES.sort(key=lambda x:x.relative_to(ROOT).as_posix())
assert all(not ('.env' in x.name or 'secret' in x.name.lower() or x.name=='id_rsa') for x in FILES)
manifest=''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.relative_to(ROOT).as_posix()+'\n' for x in FILES)
(ROOT/'SHA256SUMS.txt').write_text(manifest,encoding='utf-8')
FILES.append(ROOT/'SHA256SUMS.txt')
FILES.sort(key=lambda x:x.relative_to(ROOT).as_posix())
with ZipFile(TARGET,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for p in FILES:
        relative=(Path(RELEASE)/p.relative_to(ROOT)).as_posix()
        zi=ZipInfo(relative,date_time=(2026,10,8,0,0,0))
        zi.compress_type=ZIP_DEFLATED
        zi.external_attr=(0o100644 << 16)
        z.writestr(zi,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print(TARGET)
print('package_files',len(FILES),'zip_bytes',TARGET.stat().st_size)
print('package_sha256',hashlib.sha256(TARGET.read_bytes()).hexdigest())
