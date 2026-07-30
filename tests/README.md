# Test Suites

To maintain a clean monolithic architecture, our test suites are deeply integrated directly into their respective microservice boundaries rather than clustered at the root.

However, you can execute all test suites from the root directory.

## Backend Tests (FastAPI / Pytest)
The backend unit and integration tests are located in `../backend/tests/`.
To run them with coverage via Docker:
```bash
docker compose exec backend pytest tests/ -v --cov=app
```

## Frontend Tests (React / Vitest)
The frontend component and utility tests are located in `../frontend/src/**/*.test.ts(x)`.
To run them via Docker:
```bash
docker compose exec frontend npm run test
```
