"""Create a local API credential without printing it or sending it anywhere."""
import os
from pathlib import Path
import secrets
from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]


def configure():
    path = ROOT / ".env"
    if not path.exists():
        path.write_text((ROOT / ".env.example").read_text(), encoding="utf-8")
    values = dotenv_values(path)
    if not values.get("API_TOKEN") and not os.getenv("API_TOKEN"):
        set_key(str(path), "API_TOKEN", secrets.token_urlsafe(32))
    set_key(str(path), "REQUIRE_AUTH", "true")
    print("API authentication configured. Read API_TOKEN from the local .env file and enter it in the browser connection screen. Keep this file private.")


if __name__ == "__main__":
    configure()
