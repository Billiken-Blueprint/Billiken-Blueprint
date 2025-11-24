FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./backend/pyproject.toml ./backend/uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY ./backend/ .
RUN uv pip freeze
RUN mkdir -p data && uv run alembic upgrade head

FROM migrations AS seeding
RUN uv run python get_courses.py || echo "Course seeding skipped (error or missing data)"
# Copy and run RMP import script (prioritize file with reviews)
COPY RateMyProfessor.com-Web-Scraper/cs_professors_with_reviews.json /app/cs_professors_with_reviews.json
COPY RateMyProfessor.com-Web-Scraper/cs_professors.json /app/cs_professors.json
COPY RateMyProfessor.com-Web-Scraper/math_professors_with_reviews.json /app/math_professors_with_reviews.json
COPY RateMyProfessor.com-Web-Scraper/math_professors.json /app/math_professors.json
RUN uv run python import_rmp_ratings.py || echo "RMP import skipped (file not found or error)"

FROM deps AS dev
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
EXPOSE 8000
VOLUME [ "/app/billiken_blueprint" ]
CMD [ "uv", "run", "fastapi", "dev", "server.py", "--host", "0.0.0.0" ]

FROM deps AS prod
COPY --from=seeding /app/data /app/data
COPY ./backend/ .
EXPOSE 8000
USER 1000
CMD [ "uv", "run", "fastapi", "run", "server.py", "--host", "0.0.0.0" ]