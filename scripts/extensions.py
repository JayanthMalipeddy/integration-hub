"""Explicit operator entry point for optional external writes. Never run by agents."""
import argparse
from pathlib import Path
from backend.app.config import Settings
from backend.app.store import Store
from backend.app.providers import ProviderFactory

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['rebuild-cloud-index','sync-memory','export-trace','search','speak'])
    parser.add_argument('--value',default='')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--approve-external',action='store_true',help='Explicitly authorize this external request; configured consent/budget gates still apply')
    args=parser.parse_args()
    if not args.approve_external:parser.error('External operation requires --approve-external')
    s=Settings.from_env()
    if s.profile!='sponsored':parser.error('These optional cloud operations require AI_PROFILE=sponsored')
    p=ProviderFactory(s,Store(s.data_dir))
    if args.action=='rebuild-cloud-index':print(p.knowledge.rebuild('local'))
    elif args.action=='sync-memory':print(p.memory.sync('local'))
    elif args.action=='export-trace':print(p.observability.export('local',args.value))
    elif args.action=='search':print(p.search.search(args.value))
    elif args.action=='speak':
        if not args.output or args.output.exists():parser.error('Supply a new output path')
        args.output.write_bytes(p.voice.synthesize(args.value))
