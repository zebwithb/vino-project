# ── STAGE 1: build your app and venv ────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

ARG uv=/root/.local/bin/uv

RUN apt-get update && apt-get install -y unzip curl wget && rm -rf /var/lib/apt/lists/*

# Install `uv` for faster package bootstrapping
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install system dependencies

# Copy local context to `/app` inside container

ADD . /app
WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

RUN uv sync --locked

# Deploy templates and prepare app
WORKDIR /app/reflex_ui
RUN $uv run reflex init

# Export static copy of frontend
RUN reflex export --frontend-only --no-zip

EXPOSE 3000 8000

# Always apply migrations before starting the backend
ENV PATH="/root/.cargo/bin:$PATH"
CMD ["uv", "run", "reflex", "run", "--env", "prod"]


