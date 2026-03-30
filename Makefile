.PHONY: help setup seed run stop clean rebuild logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup: build + seed
	docker compose build
	docker compose run --rm backend python -m data.scripts.seed_database
	@echo "✅ Setup complete. Run 'make run' to start."

seed: ## Seed database with demo data
	docker compose run --rm backend python -m data.scripts.seed_database

pipeline: ## Run the full data pipeline
	docker compose run --rm backend python -m data.scripts.run_pipeline

run: ## Start all services
	docker compose up -d
	@echo "✅ Dashboard: http://localhost"
	@echo "✅ API: http://localhost/api"
	@echo "✅ Health: http://localhost/api/health"

dev: ## Start in development mode with logs
	docker compose up --build

stop: ## Stop all services
	docker compose down

clean: ## Stop and remove volumes
	docker compose down -v
	rm -f app/backend/data/parkshare.db

rebuild: ## Full rebuild
	docker compose down -v
	docker compose build --no-cache
	docker compose run --rm backend python -m data.scripts.seed_database
	docker compose up -d

logs: ## Tail all logs
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker compose logs -f frontend
