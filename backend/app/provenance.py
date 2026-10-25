"""Version evidence for evaluation freshness; never contains credentials or logs."""
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ('incidents.json', 'incidents_holdout.json', 'incidents_operational.json')


def digest_paths(paths, root=ROOT):
    result = hashlib.sha256()
    for path in sorted(paths):
        result.update(path.relative_to(root).as_posix().encode())
        result.update(path.read_bytes())
    return result.hexdigest()


def fingerprints(root=ROOT):
    return {'code': digest_paths([*(root/'backend/app').glob('*.py'), *(root/'evaluations').glob('*.py')], root),
            'corpus': digest_paths([root/'data/runbooks.json'], root),
            'dataset': digest_paths([root/'data'/name for name in DATASETS], root)}


def manifest(settings):
    versions = {}
    for name in ('langgraph','langgraph-checkpoint-sqlite','pydantic','chromadb','httpx','fastapi'):
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name] = 'not installed'
    model_digests = {}
    try:
        import httpx
        response = httpx.get(settings.ollama_url + '/api/tags', timeout=10, trust_env=False)
        response.raise_for_status()
        models = response.json()['models']
        for tag in (settings.model, settings.embed_model):
            model_digests[tag] = next((m.get('digest') for m in models if m['name'] == tag), None)
    except Exception:
        model_digests = {tag: None for tag in (settings.model, settings.embed_model)}
    return {'fingerprints': fingerprints(), 'model_digests': model_digests,
            'python': platform.python_version(), 'platform': platform.system(),
            'architecture': platform.machine(), 'dependencies': versions,
            'configuration': settings.public(), 'scope': 'frozen synthetic regression corpus; not independently adjudicated incident diagnoses'}


def freshness(report, current):
    previous = report.get('manifest', {}).get('fingerprints')
    if not previous:
        return {'status': 'unverified', 'reason': 'Historical run lacks a complete source/corpus/dataset manifest'}
    changed = [key for key in current if previous.get(key) != current[key]]
    return {'status': 'stale' if changed else 'current',
            'reason': 'Changed: ' + ', '.join(changed) if changed else 'Matches loaded application source and shipped corpus/dataset; model and custom document changes need separate verification'}
