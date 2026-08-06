# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

Monorepo with four services and a shared Bruno API collection:

```
account/      Go 1.x    — Gin + GORM + PostgreSQL   — port 8080
course/       Python 3.13 — FastAPI + SQLAlchemy async + PostgreSQL — port 8081
connections/  Java 21   — Spring Boot 3 + Neo4j     — port 8082
bruno/        Bruno API collections (account/, course/, connections/)
```

A planned `notifications/` Haskell service is next.

## Git conventions

Conventional Commits with a mandatory service scope:

```
feat(course): add use cases to list all courses
fix(account): adjust timezone for consistency
chore: add Bruno collections for all three services
```

Scope matches the service directory name (`account`, `course`, `connections`, `notifications`). Use `chore` (no scope) for cross-cutting changes. Type `doc` is used (not `docs`) based on existing history.

Before the first commit of a session, confirm whether to land on the current branch or a new one.

## Commands

### account (Go)

```sh
cd account
go run ./cmd/api          # run (needs DATABASE_URL, JWT_SECRET env vars)
go test ./...             # all tests (testcontainers spins up Postgres automatically)
go test ./internal/...    # single package: go test ./internal/usecase/...
```

Migrations run automatically at startup via GORM `AutoMigrate`. No Makefile.

### course (Python/uv)

```sh
cd course
uv sync                                      # install deps
uv run alembic upgrade head                  # run migrations
uv run python main.py                        # run (needs DATABASE_URL, JWT_SECRET)
uv run pytest tests/domain tests/application # unit tests — no DB needed
uv run pytest tests/adapters                 # integration tests — needs Postgres at localhost:5432
uv run pytest tests/domain/test_course.py    # single file
```

`asyncio_mode = "auto"` is set in `pyproject.toml` — no `@pytest.mark.asyncio` needed.

### connections (Java/Gradle)

```sh
cd connections
./gradlew bootRun         # run (needs NEO4J_URI, JWT_SECRET, M2M_SECRET env vars)
./gradlew test            # all tests (Mockito mocks only — no container needed)
./gradlew bootJar         # build fat JAR to build/libs/
```

### Docker Compose (per service)

Each service has its own `docker-compose.yaml`. Run from the service directory:

```sh
docker compose up --build
```

The `course` compose runs a `migrate` service (alembic) before starting the app. The `connections` compose waits for Neo4j healthcheck before starting the app. The `account` compose does **not** include `JWT_SECRET` — add it manually before running in production.

### Bruno collections

```sh
# via CLI (from repo root)
bru run bruno/account --env local
bru run bruno/course --env local
bru run bruno/connections --env local
```

Or open each `bruno/<service>/` folder in the Bruno desktop app with the `local` environment.

## Architecture

All three services implement **hexagonal (ports-and-adapters)** architecture. The domain layer has zero knowledge of HTTP, databases, or frameworks. The direction of naming differs slightly by language but the concepts are consistent:

| Concept | account (Go) | course (Python) | connections (Java) |
|---|---|---|---|
| Domain entities | `internal/domain/` | `src/course/domain/` | `domain/model/` |
| Port interfaces | `internal/domain/` (same package) | `application/ports/` | `application/port/in/` + `application/port/out/` |
| Use cases | `internal/usecase/` | `application/use_cases/` | `application/usecase/` |
| HTTP adapter | `internal/delivery/http/` | `adapters/driving/http/` | `adapter/in/http/` |
| DB adapter | `internal/adapter/storage/postgres/` | `adapters/driven/storage/postgres/` | `adapter/out/neo4j/` |

**Port interfaces are owned by the domain/application layer, not by adapters.** In Go, `AccountRepository` and `TokenService` live in `domain/`. In Python, `CourseRepository` and `UserRepository` are `Protocol` classes in `application/ports/`. In Java, outbound ports live in `application/port/out/`.

### Course as aggregate root

`Course` is the aggregate root in the course service. Chapters are only accessed through `Course` methods (`add_chapter`, `update_chapter`, `archive_chapter`, `unarchive_chapter`). There is no `ChapterRepository` — `PostgresCourseRepository.save` upserts the full course and all its chapters in one operation.

### User mirroring across services

Users are owned by the Account service. Course and Connections each maintain their own read-only projection:

- **Account → Course:** Caller posts `{ account_id, name, email }` to `POST /users` on the Course service (user JWT required). `UserUseCase.sync_user` upserts — skips the DB write if nothing changed. The Account `UUID` is reused as the primary key.
- **Account/Course → Connections:** Same upsert pattern via `POST /users` and `POST /courses` on Connections, but these endpoints require an M2M JWT (`ROLE_SERVICE`), not a user JWT.

### JWT authentication

All services share the same HS256 secret (`JWT_SECRET` env var). Tokens contain only `sub` (account UUID string), `iat`, and `exp` — no custom claims.

The Connections service adds a second secret (`M2M_SECRET`) for service-to-service calls. M2M tokens carry `{ "service": "<name>" }` instead of `sub`. `JwtAuthenticationFilter` tries the user key first; on failure tries the M2M key. Result: `ROLE_USER` or `ROLE_SERVICE` principal. Routes requiring M2M: `POST /users`, `POST /courses`, `POST /courses/*/enrollment`, `DELETE /courses/*/enrollment/*`.

### Domain exceptions → HTTP status codes

The mapping is identical across all three services:

| Semantic | Status |
|---|---|
| Entity not found | 404 |
| Caller not owner / forbidden | 403 |
| Invalid credentials | 401 |
| Duplicate / state conflict (already archived, author cannot be assignee, etc.) | 409 |
| Validation (bad input, invalid value object) | 400 |

In account: `handleError` switch in `account_handler.go` using `errors.Is`. In course: `add_exception_handler` in `app.py` keyed on exception base classes. In connections: `@RestControllerAdvice` in `GlobalExceptionHandler`.

### Deterministic Connection ID

`Connection.create(requesterId, addresseeId)` sorts the two UUIDs lexicographically and joins them with `_`. This makes the ID order-independent — a request A→B and B→A produce the same ID, so concurrent duplicate requests collapse to one via a constraint violation catch in `ConnectionService.sendRequest`.

### Ownership rules

- **Account:** Every protected route compares the URL `id` param to the JWT `sub`. Mismatch → 403. No admin role.
- **Course:** `Course._ensure_author(actor_id)` guards all mutations. Any authenticated user can enroll/unenroll (no author check on those).
- **Connections:** `respondToRequest` checks `connection.getAddressee().getId().equals(actorId)` — only the addressee can accept or reject.
