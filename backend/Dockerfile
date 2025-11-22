FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./backend/pyproject.toml ./backend/uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY ./backend/ .
RUN uv pip freeze
RUN mkdir data && alembic upgrade head

FROM migrations AS seeding
RUN python get_courses.py
# Copy and run RMP import script
COPY RateMyProfessor.com-Web-Scraper/cs_professors.json /app/cs_professors.json
RUN python import_rmp_ratings.py || echo "RMP import skipped (file not found or error)"

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
EXPOSE 8000
VOLUME [ "/app/billiken_blueprint" ]
CMD [ "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]

FROM deps AS prod
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
EXPOSE 8000
USER 1000
CMD [ "fastapi", "run", "server.py", "--host", "0.0.0.0" ]