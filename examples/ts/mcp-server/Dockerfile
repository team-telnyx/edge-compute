# Multi-stage build for standalone TypeScript Edge Functions
# Stage 1: Compile TypeScript and install all dependencies
FROM node:20-bookworm-slim AS builder

WORKDIR /build

COPY package.json package-lock.json tsconfig.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Runtime image with production dependencies
FROM node:20-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/dist ./dist
COPY --from=builder /build/package.json /build/package-lock.json ./
RUN npm ci --omit=dev

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["npm", "start"]
