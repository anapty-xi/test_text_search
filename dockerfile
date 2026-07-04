FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install -U poetry && pip install poetry-plugin-export
RUN poetry export ${POETRY_EXPORT_OPTIONS} --with dev --without-hashes -o requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /app

COPY --from=builder /app/wheels /wheels

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache /wheels/*

RUN useradd -m appuser

ENV PYTHONPATH="$PYTHONPATH:/app/src"

COPY --chown=appuser:appuser . .

USER appuser

CMD alembic upgrade head && uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload