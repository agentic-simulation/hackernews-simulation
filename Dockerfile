FROM python:3.10-slim

WORKDIR /app

# Install curl and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false --local && \
    poetry install --only main --no-root && \
    rm -rf /root/.cache/pip /root/.cache/poetry

# Copy application code
COPY hn_core/ ./hn_core/
COPY data/ ./data/

EXPOSE 8000

# Use poetry run to ensure all dependencies are in the PATH
CMD ["uvicorn", "hn_core.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
