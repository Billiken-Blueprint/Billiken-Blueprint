FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

FROM base AS deps
WORKDIR /app
COPY ./backend/pyproject.toml ./backend/uv.lock ./
RUN uv sync --locked
ENV PATH="/app/.venv/bin:${PATH}"

FROM deps AS migrations
COPY ./backend/ .
RUN uv pip freeze
RUN mkdir -p data && rm -f data/data.db data/data.db-journal && uv run alembic upgrade heads

FROM migrations AS seeding
RUN uv run python get_courses.py || echo "Course seeding skipped (error or missing data)"
# Copy and run RMP import script (prioritize file with reviews)
COPY RateMyProfessor.com-Web-Scraper/cs_professors_with_reviews.json /app/cs_professors_with_reviews.json
COPY RateMyProfessor.com-Web-Scraper/cs_professors.json /app/cs_professors.json
COPY RateMyProfessor.com-Web-Scraper/math_professors_with_reviews.json /app/math_professors_with_reviews.json
COPY RateMyProfessor.com-Web-Scraper/math_professors.json /app/math_professors.json
RUN uv run python import_rmp_ratings.py || echo "RMP import skipped (file not found or error)"
# Update RMP review course_ids by matching course codes (optional, won't fail build if it errors)
RUN uv run python update_rmp_review_course_ids.py || echo "RMP course_id update skipped (error or no reviews to update)"

FROM deps AS dev
COPY --from=seeding /app/data /app/data
# Copy JSON files to dev stage so they're available if import needs to be re-run
COPY --from=seeding /app/cs_professors_with_reviews.json /app/cs_professors_with_reviews.json
COPY --from=seeding /app/cs_professors.json /app/cs_professors.json
COPY --from=seeding /app/math_professors_with_reviews.json /app/math_professors_with_reviews.json
COPY --from=seeding /app/math_professors.json /app/math_professors.json
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