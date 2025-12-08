ARG base_image=node:24-alpine
ARG nginx_base_image=nginxinc/nginx-unprivileged:alpine3.22-perl

FROM ${base_image} AS base

FROM base AS builder
ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"
RUN corepack enable
RUN npm install -g @angular/cli
WORKDIR /app
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    --mount=type=bind,source=pnpm-lock.yaml,target=pnpm-lock.yaml \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    pnpm install --frozen-lockfile

FROM builder AS development
WORKDIR /app
COPY . .
VOLUME ["/app"]
EXPOSE 4200
CMD ["pnpm", "run", "start"]

FROM builder AS dist-builder
WORKDIR /app
COPY . .
ENV API_URL="http://localhost:8000"
RUN pnpm run build



FROM ${nginx_base_image} AS production
USER nginx
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY --chown=nginx:nginx --from=dist-builder /app/dist/*/browser /usr/share/nginx/html
COPY --chown=nginx:nginx ./nginx-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8080
ENV API_URL=""
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "nginx", "-g", "daemon off;" ]