.PHONY: up down reset seed ingest test contract fmt logs

# Load .env so MYSQL_* vars are available in make targets
-include .env
export

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v && docker compose up -d

seed:
	@echo "Applying seeds to running DB..."
	@for f in db/seeds/02_match_10_ger_cur.sql \
	           db/seeds/03_team_aggregates.sql \
	           db/seeds/04_all_matches.sql \
	           db/seeds/05_final_third_entries.sql; do \
		echo "  → $$f"; \
		cat $$f | docker compose exec -T db mysql -u$(MYSQL_USER) -p$(MYSQL_PASSWORD) $(MYSQL_DATABASE); \
	done
	@echo "Done."

ingest:
	docker compose --profile ingest run --rm ingestion python -m ingestion.watch_pdfs

test:
	cd frontend && npm run check && npm run lint
	cd backend && python -m pytest --tb=short
	docker compose --profile test up --abort-on-container-exit --exit-code-from test

contract:
	cd backend && python app/export_openapi.py > ../frontend/src/lib/types/openapi-raw.json
	cd frontend && npx openapi-typescript src/lib/types/openapi-raw.json -o src/lib/types/openapi.ts

fmt:
	cd backend && python -m ruff check --fix . && python -m black .
	cd ingestion && python -m ruff check --fix . && python -m black .
	cd frontend && npm run format

logs:
	docker compose logs -f
