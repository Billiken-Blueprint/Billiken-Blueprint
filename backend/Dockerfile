FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./backend/pyproject.toml ./
# uv.lock is optional - if it doesn't exist, uv sync will generate it
COPY ./backend/uv.lock* ./
RUN uv sync --locked || uv sync
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY ./backend/ .
RUN uv pip freeze
RUN mkdir -p data && alembic upgrade head

FROM migrations AS seeding
RUN python get_courses.py
# Copy and run RMP import script (files are optional - may not exist in CI)
# Copy the entire RateMyProfessor directory if it exists
# The import script handles missing files gracefully by checking multiple paths
COPY RateMyProfessor.com-Web-Scraper /tmp/rmp_source/
RUN if [ -d /tmp/rmp_source ]; then \
      [ -f /tmp/rmp_source/cs_professors_with_reviews.json ] && cp /tmp/rmp_source/cs_professors_with_reviews.json /app/ || true; \
      [ -f /tmp/rmp_source/cs_professors.json ] && cp /tmp/rmp_source/cs_professors.json /app/ || true; \
      [ -f /tmp/rmp_source/math_professors_with_reviews.json ] && cp /tmp/rmp_source/math_professors_with_reviews.json /app/ || true; \
      [ -f /tmp/rmp_source/math_professors.json ] && cp /tmp/rmp_source/math_professors.json /app/ || true; \
    fi || true
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
