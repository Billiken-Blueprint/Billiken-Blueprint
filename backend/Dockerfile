FROM ghcr.io/astral-sh/uv:python3.13-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked

FROM base AS migrations
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"
COPY . .
RUN mkdir data && alembic upgrade head

FROM base AS dev
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app/backend"
COPY --from=migrations /app/data /app/data
COPY . .
EXPOSE 8000
VOLUME [ "/app/backend" ]
CMD [ "fastapi", "dev", "backend/server.py", "--host", "0.0.0.0" ]