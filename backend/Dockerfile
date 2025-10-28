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
COPY --from=migrations /app/data /app/data
COPY --exclude=./src . .
EXPOSE 8000
VOLUME [ "/app/src" ]
CMD [ "fastapi", "dev", "src/main.py", "--host", "0.0.0.0" ]