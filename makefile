start-containers:
	docker compose up --build -d

backend-test:
	cd backend && pytest test
#  Did not include this in makefile because my WSL is not able to run torch quickly

frontend-test:
	cd frontend && npm test

stop-containers:
	docker compose down

clean-containers:
	docker compose down -v

