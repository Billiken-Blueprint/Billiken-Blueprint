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
# Verify data_dumps exists and show contents
RUN echo "Checking for data_dumps files..." && \
    ls -la data_dumps/ 2>/dev/null && \
    echo "Found data_dumps directory" || \
    (echo "ERROR: data_dumps directory not found!" && exit 1)
RUN uv run scripts/update_instructor_rmp_data.py
# Note: Individual RMP reviews are loaded from JSON files automatically, but we need to update instructor RMP fields

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY --exclude=billiken_blueprint . .
# Verify data_dumps is available for runtime RMP review loading
RUN ls -la data_dumps/ 2>/dev/null && echo "data_dumps available in dev stage" || echo "WARNING: data_dumps not found in dev stage"
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