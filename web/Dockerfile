FROM node:24-alpine AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"
RUN corepack enable

FROM base AS deps
RUN npm install -g @angular/cli
WORKDIR /app
COPY  ./package.json ./package-lock.json ./pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

FROM deps AS dev
WORKDIR /app
COPY --exclude=./src . .
COPY --from=deps /app/node_modules /app/node_modules
RUN mkdir src
VOLUME [ "/app/src" ]
EXPOSE 4200
CMD [ "pnpm", "run", "start" ]