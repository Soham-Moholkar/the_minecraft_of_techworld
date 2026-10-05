FROM node:22.20.0-alpine AS build
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/api-node/package.json apps/api-node/package.json
RUN pnpm install --frozen-lockfile --filter @atlas/api-node...
COPY apps/api-node apps/api-node
RUN pnpm --filter @atlas/api-node build

FROM node:22.20.0-alpine AS runtime
ENV NODE_ENV=production
RUN addgroup -S atlas && adduser -S atlas -G atlas
WORKDIR /app
COPY --from=build --chown=atlas:atlas /app/node_modules ./node_modules
COPY --from=build --chown=atlas:atlas /app/apps/api-node ./apps/api-node
USER atlas
EXPOSE 8100 8101
CMD ["node", "apps/api-node/dist/server.js"]
