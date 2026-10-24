from backend.app.config import Settings
from backend.app.store import Store
from backend.app.providers import ProviderFactory

if __name__=='__main__':
    s=Settings.from_env();store=Store(s.data_dir)
    print({'indexed_chunks':ProviderFactory(s,store).knowledge.rebuild('local'),'embedding_model':s.embed_model})
