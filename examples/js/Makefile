.PHONY: demo build clean run list

# Default example
EXAMPLE ?= webhook-receiver

# Start container without running demo
# Standalone examples (with their own Dockerfile) need env vars forwarded.
run:
	@echo "🚀 Starting $(EXAMPLE)..."
	@$(MAKE) build
	@if [ -f "$(EXAMPLE)/Dockerfile" ]; then \
		docker run -d --name $(EXAMPLE)-test -p 8080:8080 \
			-e TELNYX_API_KEY -e SHARED_SECRET \
			js-edge-$(EXAMPLE) ; \
	else \
		docker run -d --name $(EXAMPLE)-test -p 8080:8080 js-edge-$(EXAMPLE) ; \
	fi
	@echo "⏳ Waiting for service to be ready..."
	@sleep 2
	@echo "✅ Container started: http://localhost:8080"

# Demo a specific example
demo:
	@echo "🧪 Demonstrating $(EXAMPLE)..."
	@$(MAKE) run
	@echo "🧪 Running demo suite..."
	@cd $(EXAMPLE) && ./demo.sh
	@echo "🧹 Cleaning up..."
	@$(MAKE) clean

# Build Docker image
# Standalone examples (with their own Dockerfile) are built directly.
# Function-module examples use the shared app.js wrapper + Dockerfile.
build:
	@echo "🏗️ Building $(EXAMPLE)..."
	@if [ -f "$(EXAMPLE)/Dockerfile" ]; then \
		cd $(EXAMPLE) && docker build -t js-edge-$(EXAMPLE) . ; \
	else \
		cp app.js $(EXAMPLE)/app.js && \
		cd $(EXAMPLE) && docker build -t js-edge-$(EXAMPLE) -f ../Dockerfile . && rm -f app.js ; \
	fi
	@echo "✅ Build complete: js-edge-$(EXAMPLE)"

# Remove containers and images
clean:
	@echo "🧹 Cleaning up..."
	@docker stop $(EXAMPLE)-test 2>/dev/null || true
	@docker rm $(EXAMPLE)-test 2>/dev/null || true
	@docker rmi js-edge-$(EXAMPLE) 2>/dev/null || true

# List available examples
list:
	@echo "📋 Available JavaScript examples:"
	@for dir in */; do \
		if [ -f "$$dir/index.js" ] && [ -f "$$dir/demo.sh" ]; then \
			echo "  - $${dir%/}"; \
		fi; \
	done
