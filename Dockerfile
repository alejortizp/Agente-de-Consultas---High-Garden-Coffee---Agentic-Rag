# syntax=docker/dockerfile:1

# --- Builder stage ---
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first for better caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source and install project
COPY src/ src/
COPY data_transformation.py .
RUN uv sync --frozen --no-dev

# --- Runtime stage ---
FROM python:3.14-slim AS runtime

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/data_transformation.py .

# Copy data files
COPY coffee_db.parquet coffee_final.csv ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Create plots directory
RUN mkdir -p plots

CMD ["python", "-m", "agente_consultas.main"]
