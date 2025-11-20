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
COPY --exclude=./src . .
RUN mkdir src
VOLUME [ "/app/src" ]
EXPOSE 4200
CMD [ "pnpm", "run", "start" ]

FROM deps AS build
RUN pwd
COPY . .
RUN pnpm run build

FROM nginxinc/nginx-unprivileged:alpine3.22-perl AS prod
USER nginx
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY --chown=nginx:nginx --from=build /app/dist/*/browser /usr/share/nginx/html
COPY --chown=nginx:nginx ./nginx-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8080
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "nginx", "-g", "daemon off;" ]