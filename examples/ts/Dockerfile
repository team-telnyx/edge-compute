# Multi-stage build for TypeScript Edge Functions
# Stage 1: Compile TypeScript
FROM node:18-alpine AS builder

WORKDIR /build

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Runtime image
FROM node:18-alpine

RUN apk --no-cache add curl

WORKDIR /app

# Copy compiled output, runtime wrapper, and package manifest
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/app.js ./
COPY --from=builder /build/package.json ./

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["node", "app.js"]
