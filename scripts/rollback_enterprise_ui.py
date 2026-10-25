"""Restore only frontend files changed by this redesign, preserving other project work."""
from pathlib import Path
import argparse, hashlib, json, zipfile, datetime
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'runtime'/'ui-rollback'
def digest(data):return hashlib.sha256(data).hexdigest()
def target(name):
 p=(ROOT/name).resolve()
 if not p.is_relative_to((ROOT/'frontend').resolve()):raise ValueError('Rollback target escapes frontend: '+name)
 return p

def run(restore=False):
 snapshot=Path((BASE/'latest.txt').read_text(encoding='utf-8').strip()).resolve()
 if not snapshot.is_relative_to(BASE.resolve()):raise ValueError('Invalid rollback archive location')
 before=json.loads((snapshot/'manifest.json').read_text(encoding='utf-8'))
 after=json.loads((snapshot/'after-manifest.json').read_text(encoding='utf-8'))
 changed=[name for name in set(before)|set(after) if before.get(name)!=after.get(name)]
 with zipfile.ZipFile(snapshot/'frontend-before.zip') as archive:
  for name,expected in before.items():
   target(name)
   if digest(archive.read(name))!=expected:raise ValueError('Archive integrity failure: '+name)
  for name in changed:
   p=target(name);actual=digest(p.read_bytes()) if p.exists() else None
   if actual!=after.get(name):raise RuntimeError('A file changed after the redesign; review it before rollback: '+name)
  # Rehearse exact restoration in memory before allowing any filesystem change.
  restored=dict(after)
  for name in changed:
   if name in before:restored[name]=digest(archive.read(name))
   else:restored.pop(name,None)
  if restored!=before:raise AssertionError('Restoration rehearsal failed')
  print(f'Archive verified; {len(changed)} frontend files can be restored. Existing backend/security work is preserved.')
  if not restore:return
  rescue=snapshot/('before-restore-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
  with zipfile.ZipFile(rescue,'w',zipfile.ZIP_DEFLATED) as saved:
   for name in changed:
    p=target(name)
    if p.exists():saved.write(p,name)
  for name in changed:
   p=target(name)
   if name in before:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(name))
   elif p.exists():p.unlink()
  print('Previous frontend restored. Rebuild frontend/dist if serving the production build.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--restore',action='store_true',help='Restore the UI; default only verifies archive and current file hashes.');args=parser.parse_args();run(args.restore)
