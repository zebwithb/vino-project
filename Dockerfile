FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies using uv and lockfile for reproducibility
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Expose ports for Reflex frontend and FastAPI backend
EXPOSE 3000 8000

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run both services - FastAPI backend and Reflex frontend
CMD ["sh", "-c", "cd src && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & cd /app/reflex_ui && uv run reflex run --frontend-host 0.0.0.0 --frontend-port 3000 & wait"]