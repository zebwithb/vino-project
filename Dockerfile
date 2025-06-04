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

# Create a startup script to run both services
RUN echo '#!/bin/bash\n\
# Start FastAPI backend\n\
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start Reflex frontend\n\
reflex run --app reflex_ui.app --frontend-host 0.0.0.0 --frontend-port 3000 &\n\
\n\
# Wait for both processes\n\
wait' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]