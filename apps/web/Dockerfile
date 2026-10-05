FROM node:22.20.0-alpine AS deps
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile --filter @atlas/web...

FROM deps AS builder
COPY apps/web apps/web
RUN pnpm --filter @atlas/web build

FROM node:22.20.0-alpine AS runtime
ENV NODE_ENV=production
RUN addgroup -S atlas && adduser -S atlas -G atlas
WORKDIR /app
COPY --from=builder --chown=atlas:atlas /app/apps/web/.next/standalone ./
COPY --from=builder --chown=atlas:atlas /app/apps/web/.next/static ./apps/web/.next/static
USER atlas
EXPOSE 3000
CMD ["node", "apps/web/server.js"]

