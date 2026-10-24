# Deployment and validation

## Native development — executed

Python 3.12 environment, installed dependency versions pinned in requirements.txt. React 19, TypeScript 6 and Vite 8 frontend. Use the project-local .venv as described in README. The application no longer relies on the Week 2 Python environment. Ollama Qwen 2.5 and nomic-embed-text were present; no model download or paid API was necessary.

- Backend: `python -m scripts.serve` → 127.0.0.1:8010.
- Frontend: `npm run dev` in frontend → 127.0.0.1:5180; `/api` proxies to 8010.
- Data/logs: project-local runtime directory, ignored by Git.
- API health and frontend HTTP responses checked. Frontend production build passed.

Native startup loads this project's .env; existing process environment values override it. Set API_TOKEN for authenticated use and enter it in the Settings screen; it is retained only for the browser session. No keys are stored by the frontend.

## Docker Compose — prepared, runtime not verified

`docker compose config --quiet` passed. Docker Desktop's engine was not running, so no image build/container startup is claimed.

```sh
docker compose up -d --build
docker compose exec ollama ollama pull qwen2.5:latest
docker compose exec ollama ollama pull nomic-embed-text:latest
```

The first setup requires internet for images, Python/npm packages and model downloads. Subsequent core operation is offline. Ollama and backend have private container ports. The only published port is `127.0.0.1:5180`. Persistent named volumes hold models and canonical data. Model absence is shown in provider status rather than replaced by simulated inference.

Compose forwards core profile/LLM settings. To use optional sponsored add-ons in containers, explicitly add only the needed credential/ceiling variables from `.env.example` to the backend environment; none are embedded in images. Do not put secrets in a Dockerfile or frontend build variable.

## CI and separate repository

The included `.github/workflows/ci.yml` runs fixture/API tests and frontend build without cloud credentials or Ollama. Real model evaluations are a separate explicit command. The project lives at C:\Projects\integration-hub, outside the Week 2 repository. Publish it as a separate repository to enable the included workflow. No repository has been created or pushed automatically.

## Replit / portfolio

The API/frontend architecture can be hosted behind a reverse proxy. Replit deployment was not tested and cannot be described as permanently free. A Replit environment without an installed local model needs an explicitly authorized compatible inference backend. The project remains useful as a static portfolio through README, architecture, saved evaluation JSON, screenshot and scenario documentation even when inference is stopped.

Public deployment is a later decision: authentication, organization-approved data handling, provider budgets and infrastructure configuration must be reviewed first.

The current native configuration connects to the project-owned Chroma HTTP server on 127.0.0.1:8082, started with scripts/start-chroma.ps1. For Docker Desktop access to that host service use CHROMA_MODE=http and CHROMA_HOST=host.docker.internal in Compose. A loopback-only host service may require host networking configuration; container connectivity has not been verified. Use CHROMA_MODE=embedded for the self-contained container setup.
