import uvicorn
from backend.app.config import Settings
from backend.app.store import Store
from scripts.seed import seed

if __name__ == "__main__":
    seed(Store(Settings.from_env().data_dir))
    uvicorn.run("backend.app.main:create_app", factory=True, host="127.0.0.1", port=8010)
