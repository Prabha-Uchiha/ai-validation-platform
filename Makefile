up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy .

test:
	pytest