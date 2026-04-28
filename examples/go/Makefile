.PHONY: demo build clean run

# Default example
EXAMPLE ?= middleware-patterns

# Start container without running demo
run:
	@echo "🚀 Starting $(EXAMPLE)..."
	@$(MAKE) build
	@docker run -d --name $(EXAMPLE)-test -p 8080:8080 go-edge-$(EXAMPLE)
	@echo "⏳ Waiting for service to be ready..."
	@sleep 3
	@echo "✅ Container started: http://localhost:8080"

# Demo a specific example
demo:
	@echo "🧪 Demonstrating $(EXAMPLE)..."
	@$(MAKE) run
	@echo "🧪 Running demo suite..."
	@cd $(EXAMPLE) && ./demo.sh
	@echo "🧹 Cleaning up..."
	@$(MAKE) clean

# Build for container testing
build:
	@echo "🏗️ Building $(EXAMPLE)..."
	@mkdir -p $(EXAMPLE)/app
	@cp app.go $(EXAMPLE)/app/main.go
	@cd $(EXAMPLE) && docker build --build-arg TARGETPLATFORM=linux/arm64 --build-arg TARGETOS=linux --build-arg TARGETARCH=arm64 -t go-edge-$(EXAMPLE) -f ../Dockerfile . && rm -rf app
	@echo "✅ Build complete: go-edge-$(EXAMPLE)"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@docker stop $(EXAMPLE)-test 2>/dev/null || true
	@docker rm $(EXAMPLE)-test 2>/dev/null || true
	@docker rmi go-edge-$(EXAMPLE) 2>/dev/null || true

# List available examples
list:
	@echo "📋 Available Go examples:"
	@for dir in */; do \
		if [ -f "$$dir/handler.go" ] && [ -f "$$dir/go.mod" ]; then \
			echo "  - $${dir%/}"; \
		fi; \
	done