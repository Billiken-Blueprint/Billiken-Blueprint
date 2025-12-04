FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base
WORKDIR /app

FROM base AS deps
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY . .
RUN mkdir -p data && alembic upgrade head

FROM migrations AS seeding
RUN uv run scripts/import_data.py
RUN uv run scripts/update_instructor_rmp_data.py
# Note: Individual RMP reviews are loaded from JSON files automatically, but we need to update instructor RMP fields

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY --exclude=billiken_blueprint . .
EXPOSE 8000
VOLUME [ "/app/billiken_blueprint" ]
VOLUME [ "/app/data" ]
CMD [ "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]

FROM deps AS prod
COPY --from=seeding /app/data /app/data
COPY . .
EXPOSE 8000
USER 1000
CMD [ "fastapi", "run", "server.py", "--host", "0.0.0.0" ]