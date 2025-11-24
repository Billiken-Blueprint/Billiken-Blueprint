FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./backend/pyproject.toml ./backend/uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY ./backend/ .
RUN uv pip freeze
RUN mkdir -p data && (uv run alembic upgrade heads 2>/dev/null || (uv run alembic merge heads -m "merge_heads" 2>/dev/null && uv run alembic upgrade head) || echo "Migration skipped or already up to date")

FROM migrations AS seeding
# Copy parent directory context to access RateMyProfessor files
COPY . /build-context/
RUN uv run python get_courses.py || echo "Course seeding skipped (error or missing data)"
# Copy RMP JSON files if they exist (using shell to handle missing files)
RUN mkdir -p /app && \
    (cp /build-context/RateMyProfessor.com-Web-Scraper/cs_professors_with_reviews.json /app/ 2>/dev/null || true) && \
    (cp /build-context/RateMyProfessor.com-Web-Scraper/cs_professors.json /app/ 2>/dev/null || true) && \
    (cp /build-context/RateMyProfessor.com-Web-Scraper/math_professors_with_reviews.json /app/ 2>/dev/null || true) && \
    (cp /build-context/RateMyProfessor.com-Web-Scraper/math_professors.json /app/ 2>/dev/null || true) || true
RUN uv run python import_rmp_ratings.py || echo "RMP import skipped (file not found or error)"

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
# Note: RMP JSON files will be imported on startup if missing (see server.py)
# They can be on host filesystem in RateMyProfessor.com-Web-Scraper/ directory
EXPOSE 8000
VOLUME [ "/app/billiken_blueprint" ]
CMD [ "uv", "run", "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]

FROM deps AS prod
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
EXPOSE 8000
USER 1000
CMD [ "uv", "run", "fastapi", "run", "server.py", "--host", "0.0.0.0" ]