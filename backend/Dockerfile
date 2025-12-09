ARG base_image=python:3.13-slim
FROM ${base_image} AS base

FROM base AS uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

FROM uv AS deps
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --compile-bytecode

FROM deps AS seeding
COPY . .
RUN mkdir -p data && uv run alembic upgrade head
RUN uv run scripts/import_data.py
RUN uv run scripts/update_instructor_rmp_data.py

FROM base AS development
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY --from=seeding /app/data /app/data
COPY . .
ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000
VOLUME [ "/billiken_blueprint" ]
CMD [ "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]

FROM base AS production
WORKDIR /app
COPY --chown=1000:1000 --from=deps /app/.venv /app/.venv
COPY --chown=1000:1000 --from=seeding /app/data /app/data
COPY --chown=1000:1000 . .
ENV PATH="/app/.venv/bin:${PATH}"
ENV GEMINI_API_KEY=""
EXPOSE 8000
USER 1000
CMD ["fastapi", "run", "server.py", "--host", "0.0.0.0", "--port", "8000"]
