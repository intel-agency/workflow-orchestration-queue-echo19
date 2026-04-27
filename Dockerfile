FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first for caching
COPY pyproject.toml ./

# Copy source before install (required for editable installs)
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Copy the rest
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.notifier_service:app", "--host", "0.0.0.0", "--port", "8000"]
