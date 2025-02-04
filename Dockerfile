FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./
COPY hn_core/ ./hn_core/
COPY data/ ./data/

RUN poetry config virtualenvs.create false --local
RUN poetry install --only main --no-root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "hn_core.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
