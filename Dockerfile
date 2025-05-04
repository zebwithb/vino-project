FROM python:3.11-slim

WORKDIR /app

# Install Rust and Cargo
RUN apt-get update && apt-get install -y curl build-essential && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    export PATH="/root/.cargo/bin:${PATH}"

# Add Cargo to PATH for subsequent RUN commands
ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .
# Install Python dependencies (now with Rust available)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]