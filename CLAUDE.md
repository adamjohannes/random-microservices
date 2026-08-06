# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

Monorepo with five services, a Vue frontend, a message broker, and a shared Bruno API collection:

```
account/       Go 1.x      — Gin + GORM + PostgreSQL          — port 8080
course/        Python 3.13 — FastAPI + SQLAlchemy async + PG   — port 8081
connections/   Java 21     — Spring Boot 3 + Neo4j             — port 8082
notifications/ Haskell     — servant + amqp + smtp-mail        — port 8083
web/           Vue 3       — Vite + Pinia + Tailwind CSS       — port 5173 (dev)
bruno/         Bruno API collections (account/, course/, connections/, notifications/)
```

All four services publish/consume domain events via **RabbitMQ** (topic exchange `domain_events`). Each service's `docker-compose.yaml` includes a `rabbitmq` service.

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

### web (Vue 3/Vite)

```sh
cd web
npm install
npm run dev      # Vite dev server on http://localhost:5173 (proxies API calls to backend services)
npm run build    # production build to web/dist/ (runs vue-tsc then vite build)
npm run preview  # preview production build locally
```

The dev proxy rewrites:
- `/api/account/*` → `http://localhost:8080/api/v1/accounts/*`
- `/api/course/*`  → `http://localhost:8081/*`
- `/api/connections/*` → `http://localhost:8082/*`

All four backend services must be running for the full feature set. Auth store persists the JWT to `localStorage` under key `access_token` and rehydrates on page load.

### notifications (Haskell/cabal)

```sh
cd notifications
cabal build                    # compile
cabal test                     # unit tests (pure — no broker or SMTP needed)
cabal run notifications        # run (needs SMTP_HOST, SMTP_USER, SMTP_PASS, SMTP_FROM_ADDRESS)
docker compose up              # starts rabbitmq + mailhog (port 8025) + notifications
```

Environment variables:

| Var | Required | Default |
|---|---|---|
| `AMQP_HOST` | no | `localhost` |
| `AMQP_USER` | no | `guest` |
| `AMQP_PASS` | no | `guest` |
| `SMTP_HOST` | **yes** | — |
| `SMTP_PORT` | no | `587` |
| `SMTP_USER` | **yes** | — |
| `SMTP_PASS` | **yes** | — |
| `SMTP_FROM_ADDRESS` | **yes** | — |
| `PORT` | no | `8083` |

MailHog is included in `docker-compose.yaml` for local email capture (`localhost:8025`). For production replace `SMTP_*` vars with real values.

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
bru run bruno/notifications --env local
```

Or open each `bruno/<service>/` folder in the Bruno desktop app with the `local` environment.

## Architecture

All three services implement **hexagonal (ports-and-adapters)** architecture. The domain layer has zero knowledge of HTTP, databases, or frameworks. The direction of naming differs slightly by language but the concepts are consistent:

| Concept | account (Go) | course (Python) | connections (Java) | notifications (Haskell) |
|---|---|---|---|---|
| Domain entities | `internal/domain/` | `src/course/domain/` | `domain/model/` | `src/Notification/Domain/` |
| Port interfaces | `internal/domain/` (same package) | `application/ports/` | `application/port/in/` + `application/port/out/` | `src/Notification/Ports/` |
| Use cases | `internal/usecase/` | `application/use_cases/` | `application/usecase/` | `Domain/Dispatch.hs` (pure fn) |
| HTTP adapter | `internal/delivery/http/` | `adapters/driving/http/` | `adapter/in/http/` | `Health.hs` (health only) |
| Broker/email adapter | `adapter/messaging/rabbitmq/` | `adapters/driven/messaging/` | `adapter/out/messaging/` | `Adapters/AmqpConsumer.hs` + `Adapters/SmtpEmail.hs` |

**Port interfaces are owned by the domain/application layer, not by adapters.** In Go, `AccountRepository` and `TokenService` live in `domain/`. In Python, `CourseRepository` and `UserRepository` are `Protocol` classes in `application/ports/`. In Java, outbound ports live in `application/port/out/`.

### Event publishing (RabbitMQ)

Topic exchange `domain_events`. Each service publishes fire-and-forget (failures are logged, not propagated). The notifications service subscribes and sends emails.

| Routing key | Publisher | Trigger |
|---|---|---|
| `account.user_registered` | account | After `repo.Create` succeeds in `RegisterAccount` |
| `course.user_enrolled` | course | After `course_repo.save` in `enroll_user_in_course` |
| `connections.request_received` | connections | After `connectionRepository.save` in `sendRequest` |
| `connections.request_accepted` | connections | After `connectionRepository.save` in `respondToRequest` (accept=true) |

AMQP env vars (`AMQP_HOST`, `AMQP_USER`, `AMQP_PASS`) have safe defaults (`localhost`, `guest`, `guest`) so all services start without a broker — publishing silently degrades to a noop.

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
