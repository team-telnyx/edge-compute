FROM node:18-alpine

RUN apk --no-cache add curl

WORKDIR /app

# Install runtime dependencies (skip devDependencies)
COPY package.json ./
RUN npm install --omit=dev 2>/dev/null || npm install --production 2>/dev/null || true

# Copy function and the shared runtime wrapper (copied in by Makefile build step)
COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD ["node", "app.js"]
