#!/bin/bash

# Start FastAPI backend
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 &

# Start Reflex frontend  
uv run reflex run --app reflex_ui.app --frontend-host 0.0.0.0 --frontend-port 3000 &

# Wait for both processes
wait
