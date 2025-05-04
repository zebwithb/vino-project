FROM python:3.11-slim

WORKDIR /app

# Install Rust and Cargo (needed if any dependencies require compilation)
# If no dependencies need Rust, you might remove this section
RUN apt-get update && apt-get install -y curl build-essential && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add Cargo to PATH for subsequent RUN commands
ENV PATH="/root/.cargo/bin:${PATH}"

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:${PATH}"

COPY requirements.txt .

# Install Python dependencies using uv
# uv caches by default, so --no-cache-dir is not needed and might interfere
RUN uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000

# Update the CMD to point to src.main:app based on previous changes
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]