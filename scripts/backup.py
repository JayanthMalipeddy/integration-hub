"""Offline, consistent backup and conservative restore. Stop the backend first."""
import argparse
import hashlib
import json
import sqlite3
import zipfile
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory


def backup(source: Path, target: Path):
    if target.exists(): raise ValueError('Backup destination already exists')
    with TemporaryDirectory() as temp:
        entries={}
        for name in ('hub.sqlite3','checkpoints.sqlite3'):
            if not (source/name).exists(): continue
            copy=Path(temp)/name
            with closing(sqlite3.connect(source/name)) as db, closing(sqlite3.connect(copy)) as dest: db.backup(dest)
            entries[name]=copy.read_bytes()
        if 'hub.sqlite3' not in entries: raise ValueError('No canonical database found')
        manifest={name:hashlib.sha256(data).hexdigest() for name,data in entries.items()}
        with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as archive:
            for name,data in entries.items(): archive.writestr(name,data)
            archive.writestr('manifest.json',json.dumps(manifest))


def restore(source: Path, target: Path):
    if target.exists() and any(target.iterdir()): raise ValueError('Restore requires an empty destination; existing data will not be overwritten')
    with zipfile.ZipFile(source) as archive:
        names=archive.namelist()
        allowed={'manifest.json','hub.sqlite3','checkpoints.sqlite3'}
        if set(names)-allowed or len(names)!=len(set(names)): raise ValueError('Unexpected or duplicate backup entries')
        if sum(i.file_size for i in archive.infolist())>100_000_000: raise ValueError('Backup exceeds 100 MB limit')
        manifest=json.loads(archive.read('manifest.json'))
        if set(manifest)!=set(names)-{'manifest.json'}: raise ValueError('Manifest does not match archive')
        data={name:archive.read(name) for name in manifest}
        for name,content in data.items():
            if hashlib.sha256(content).hexdigest()!=manifest[name]: raise ValueError('Backup checksum mismatch')
        target.mkdir(parents=True,exist_ok=True)
        for name,content in data.items(): (target/name).write_bytes(content)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['backup','restore']);parser.add_argument('source',type=Path);parser.add_argument('target',type=Path)
    args=parser.parse_args()
    globals()[args.operation](args.source,args.target)
    print('Completed. Rebuild vector indexes after restore; they are deliberately not copied.')
