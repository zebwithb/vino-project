# ── STAGE 1: build your app and venv ────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

ARG uv=/root/.local/bin/uv

RUN apt-get update && apt-get install -y unzip curl wget && rm -rf /var/lib/apt/lists/*

# Install `uv` for faster package bootstrapping
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install system dependencies

# Copy local context to `/app` inside container
WORKDIR /app
COPY . .

# Create virtualenv which will be copied into final container
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN $uv venv

# Install dependencies using uv with lock file
RUN $uv sync --locked

# Switch to src folder and sync backend dependencies
WORKDIR /app/src
RUN $uv sync --locked

# Deploy templates and prepare app
WORKDIR /app/reflex_ui
RUN $uv run reflex init

# Export static copy of frontend
RUN $uv run reflex export --frontend-only --no-zip

# ── STAGE 2: runtime ───────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app /app

# Install runtime dependencies if needed
RUN apt-get update && apt-get install -y curl unzip  && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Needed until Reflex properly passes SIGTERM on backend
STOPSIGNAL SIGKILL

WORKDIR /app/reflex_ui

EXPOSE 3000 8000

# Always apply migrations before starting the backend
CMD [ -d alembic ] && $uv run reflex db migrate; \
    exec $uv run reflex --env prod --loglevel debug


