# Multi-stage build for Go Edge Functions
# Stage 1: Build the Go application
FROM golang:1.24-alpine AS builder

WORKDIR /build

# Copy the entire example directory
COPY . .

# Download dependencies
RUN go mod download

# Build statically for the target platform from the correct directory
ARG TARGETPLATFORM=linux/arm64
ARG TARGETOS=linux
ARG TARGETARCH=arm64

RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -a -installsuffix cgo -o ./app/main ./app

# Stage 2: Runtime image
FROM alpine:latest

RUN apk --no-cache add ca-certificates curl

WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /build/app/main .

# Make the binary executable
RUN chmod +x ./main

# Copy configuration
COPY func.toml .

# Expose HTTP port
EXPOSE 8080

# Healthcheck for local testing and orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the Go application
CMD ["./main"]