FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY . .
RUN uv pip freeze
RUN mkdir data && alembic upgrade head

FROM migrations AS seeding
RUN python get_courses.py

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY --exclude=./billiken_blueprint . .
EXPOSE 8000
VOLUME [ "/app/billiken_blueprint" ]
CMD [ "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]