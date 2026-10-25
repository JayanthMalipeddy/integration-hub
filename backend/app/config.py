"""One profile selection; credentials are never returned to the browser."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


def flag(name: str) -> bool:
    return os.getenv(name, "false").lower() == "true"


@dataclass
class Settings:
    profile: str = "local_free"
    data_dir: Path = Path("runtime")
    ollama_url: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:latest"
    embed_model: str = "nomic-embed-text:latest"
    vector_store: str = "auto"
    chroma_mode: str = "embedded"
    chroma_host: str = "127.0.0.1"
    chroma_port: int = 8082
    cloud_key: str = ""
    cloud_model: str = ""
    allow_cloud: bool = False
    allow_paid: bool = False
    data_consent: bool = False
    local_fallback: bool = False
    max_cost: float = 0
    input_price: float = 0
    output_price: float = 0
    api_token: str = ""
    require_auth: bool = True
    timeout: float = 180
    max_output: int = 700
    max_steps: int = 18
    max_corrections: int = 2
    max_tokens: int = 10000

    @classmethod
    def from_env(cls, env_file=None):
        # Only load this project's configuration, never a parent directory's file.
        load_dotenv(env_file if env_file is not None else Path(__file__).resolve().parents[2] / ".env", override=False)
        s = cls(profile=os.getenv("AI_PROFILE", "local_free"),
            data_dir=Path(os.getenv("DATA_DIR", "runtime")),
            ollama_url=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:latest"),
            embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text:latest"),
            vector_store=os.getenv("VECTOR_STORE", "auto"),
            chroma_mode=os.getenv("CHROMA_MODE", "http"),
            chroma_host=os.getenv("CHROMA_HOST", "127.0.0.1"),
            chroma_port=int(os.getenv("CHROMA_PORT", "8082")),
            cloud_key=os.getenv("CLOUD_API_KEY", ""), cloud_model=os.getenv("CLOUD_MODEL", ""),
            allow_cloud=flag("ALLOW_CLOUD"), allow_paid=flag("ALLOW_PAID"),
            data_consent=flag("CLOUD_DATA_CONSENT"), local_fallback=flag("ALLOW_LOCAL_FALLBACK"),
            max_cost=float(os.getenv("MAX_COST_USD", "0")),
            input_price=float(os.getenv("CLOUD_INPUT_USD_PER_MILLION", "0")),
            output_price=float(os.getenv("CLOUD_OUTPUT_USD_PER_MILLION", "0")),
            api_token=os.getenv("API_TOKEN", ""),
            require_auth=os.getenv("REQUIRE_AUTH", "true").lower() == "true")
        if s.profile not in {"local_free", "hybrid", "sponsored"}:
            raise ValueError("AI_PROFILE must be local_free, hybrid or sponsored")
        if s.vector_store not in {"auto", "chroma", "pinecone"}:
            raise ValueError("VECTOR_STORE must be auto, chroma or pinecone")
        if s.vector_store == "pinecone" and s.profile != "sponsored":
            raise ValueError("Pinecone requires AI_PROFILE=sponsored")
        if s.chroma_mode not in {"embedded", "http"}:
            raise ValueError("CHROMA_MODE must be embedded or http")
        if s.chroma_host not in {"localhost", "127.0.0.1", "chroma", "host.docker.internal"}:
            raise ValueError("CHROMA_HOST must be a local endpoint")
        if not 1 <= s.chroma_port <= 65535:
            raise ValueError("CHROMA_PORT must be between 1 and 65535")
        # No remote Ollama proxies or cloud-suffixed models through the local route.
        from urllib.parse import urlparse
        if urlparse(s.ollama_url).hostname not in {"localhost", "127.0.0.1", "ollama", "host.docker.internal"}:
            raise ValueError("OLLAMA_URL must be a local endpoint")
        if "cloud" in s.model.lower():
            raise ValueError("A cloud Ollama model is not allowed in the local adapter")
        return s

    @property
    def effective_vector_store(self):
        return self.vector_store if self.vector_store != "auto" else ("pinecone" if self.profile == "sponsored" else "chroma")

    def public(self):
        return {"profile": self.profile, "model": self.model if self.profile == "local_free" else self.cloud_model,
                "embedding_model": self.embed_model, "cloud_enabled": self.allow_cloud,
                "cloud_data_consent": self.data_consent, "paid_enabled": self.allow_paid,
                "max_cost_usd": self.max_cost, "max_steps": self.max_steps,
                "max_tokens": self.max_tokens, "authentication": bool(self.api_token),
                "authentication_required": self.require_auth,
                "max_corrections": self.max_corrections,
                "local_fallback": self.local_fallback,
                "vector_store": self.effective_vector_store,
                "chroma_mode": self.chroma_mode,
                "chroma_endpoint": f"http://{self.chroma_host}:{self.chroma_port}" if self.chroma_mode == "http" else str(self.data_dir / "chroma")}
