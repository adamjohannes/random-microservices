# Account Service

A microservice for account management: registration, authentication, and account lifecycle. Built with Go and Gin, backed by PostgreSQL, using JWT (HS256) for auth.

## Architecture

Layered / hexagonal layout:

```
cmd/api/                  entrypoint
internal/
  domain/                 entities and value objects (email, name, password, account id)
  usecase/                application logic
  delivery/http/          Gin handlers, router, middleware, DTOs
  adapter/storage/        PostgreSQL repository (GORM)
  auth/                   JWT issuing and validation
  config/                 environment configuration
api/openapi.yaml          OpenAPI 3.0 specification
```

## API

Base path: `/api/v1/accounts`

| Method | Path                | Auth | Description              |
|--------|---------------------|------|--------------------------|
| POST   | `/`                 | No   | Register a new account   |
| POST   | `/login`            | No   | Authenticate, get token  |
| GET    | `/:id`              | Yes  | Get account by ID        |
| PUT    | `/:id`              | Yes  | Update account           |
| PATCH  | `/:id/password`     | Yes  | Change password          |
| DELETE | `/:id`              | Yes  | Delete account (soft)    |

Authentication is bearer JWT (`Authorization: Bearer <token>`). Authorization is
ownership-based: the `:id` in the path must match the token's subject, so a caller
may only act on their own account.

See [`api/openapi.yaml`](api/openapi.yaml) for the full contract, request/response
schemas, and error shapes.

## Configuration

Set via environment variables:

| Variable       | Required | Default       | Description                          |
|----------------|----------|---------------|--------------------------------------|
| `DATABASE_URL` | Yes      | —             | PostgreSQL connection string         |
| `JWT_SECRET`   | Yes      | —             | Secret for signing JWTs (HS256)      |
| `PORT`         | No       | `8080`        | HTTP listen port                     |
| `ENVIRONMENT`  | No       | `development` | Runtime environment                  |
| `JWT_EXPIRY`   | No       | `24h`         | Token lifetime                       |
| `LOG_LEVEL`    | No       | —             | Log level                            |
| `LOG_CALLER`   | No       | —             | Include caller in log output         |

## Running

### Locally

```sh
export DATABASE_URL="postgres://user:password@localhost:5432/account_db?sslmode=disable"
export JWT_SECRET="your-secret"
go run ./cmd/api
```

### Docker Compose

```sh
docker compose up --build
```

This starts PostgreSQL and the service on port `8080`. Note that the service
requires `JWT_SECRET`; add it to the `account` service environment in
`docker-compose.yaml` before running.

## Testing

```sh
go test ./...
```
