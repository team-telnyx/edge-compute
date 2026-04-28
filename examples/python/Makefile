.PHONY: demo build clean run

# Default example
EXAMPLE ?= webhook-receiver

# Start container without running demo
run:
	@echo "🚀 Starting $(EXAMPLE)..."
	@$(MAKE) build
	@docker run -d --name $(EXAMPLE)-test -p 8080:8080 python-edge-$(EXAMPLE)
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
	@cp app.py $(EXAMPLE)/app.py
	@cd $(EXAMPLE) && docker build -t python-edge-$(EXAMPLE) -f ../Dockerfile . && rm -f app.py
	@echo "✅ Build complete: python-edge-$(EXAMPLE)"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@docker stop $(EXAMPLE)-test 2>/dev/null || true
	@docker rm $(EXAMPLE)-test 2>/dev/null || true
	@docker rmi python-edge-$(EXAMPLE) 2>/dev/null || true

# List available examples
list:
	@echo "📋 Available Python examples:"
	@for dir in */; do \
		if [ -f "$$dir/function/func.py" ] && [ -f "$$dir/demo.sh" ]; then \
			echo "  - $${dir%/}"; \
		fi; \
	done