FROM python:3.11.10-slim-bullseye AS builder

WORKDIR /app
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry
COPY todo-list-app/pyproject.toml todo-list-app/poetry.lock /app/
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi 

FROM python:3.11.10-slim-bullseye
WORKDIR /app
COPY --from=builder /app/.venv/ /app/.venv/
COPY ../.env /app
COPY todo-list-app/ /app
RUN chmod +x ./entrypoint.sh
EXPOSE 8000
RUN useradd -m -U app && chown -R app:app /app 
USER app

ENTRYPOINT ["./entrypoint.sh"]
