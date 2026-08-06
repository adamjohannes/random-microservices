# Connections Service

Java microservice for managing social connections between users. Built with Spring Boot 3 and Neo4j, following hexagonal architecture. Supports sending, accepting, and rejecting connection requests, and graph-based queries over the social network.

## Architecture

```
src/main/java/com/example/connections/
  domain/model/             Connection, User, Course nodes; ConnectionStatus enum
  domain/exception/         DomainException hierarchy
  application/port/in/      Inbound use case interfaces
  application/port/out/     Outbound repository interfaces
  application/usecase/      ConnectionService, UserSyncService, CourseSyncService
  adapter/in/http/          Spring MVC controllers, JWT filter, exception handler, DTOs
  adapter/out/neo4j/        Spring Data Neo4j repositories, Cypher queries
  adapter/out/messaging/    RabbitMQ event publisher
```

The domain models (`User`, `Course`) are thin projections synced from the Account and Course services respectively. The source of truth for user and course data lives in those services.

## API

### User-facing (Bearer JWT required)

| Method  | Path                              | Description                                       |
|---------|-----------------------------------|---------------------------------------------------|
| `POST`  | `/connections`                    | Send a connection request to another user         |
| `PATCH` | `/connections/{id}/accept`        | Accept a pending connection request               |
| `PATCH` | `/connections/{id}/reject`        | Reject a pending connection request               |
| `GET`   | `/connections`                    | List all accepted connections for the caller      |
| `GET`   | `/connections/courses`            | List courses enrolled in by the caller's connections |

### Service-to-service (M2M JWT required — `ROLE_SERVICE`)

| Method   | Path                               | Description                            |
|----------|------------------------------------|----------------------------------------|
| `POST`   | `/users`                           | Sync a user from the Account service   |
| `POST`   | `/courses`                         | Sync a course from the Course service  |
| `POST`   | `/courses/{id}/enrollment`         | Record a course enrollment             |
| `DELETE` | `/courses/{id}/enrollment/{userId}`| Remove a course enrollment             |

Authentication uses HS256 JWTs. User tokens carry `sub` = account UUID. M2M tokens carry a `service` claim instead of `sub` and are verified with a separate secret.

Connection IDs are derived deterministically: the two participant UUIDs are sorted lexicographically and joined with `_`, making concurrent duplicate requests idempotent.

## Events published

| Routing key                       | Trigger                                      |
|-----------------------------------|----------------------------------------------|
| `connections.request_received`    | After a connection request is successfully saved |
| `connections.request_accepted`    | After a request is accepted                  |

Published to the `domain_events` topic exchange on RabbitMQ.

## Configuration

| Variable       | Required | Default     | Description                                  |
|----------------|----------|-------------|----------------------------------------------|
| `JWT_SECRET`   | yes      | —           | HS256 secret shared with Account and Course  |
| `M2M_SECRET`   | yes      | —           | HS256 secret for service-to-service tokens   |
| `NEO4J_URI`    | yes      | —           | Neo4j Bolt URI                               |
| `NEO4J_USERNAME` | no     | `neo4j`     | Neo4j username                               |
| `NEO4J_PASSWORD` | no     | `password`  | Neo4j password                               |
| `AMQP_HOST`    | no       | `localhost` | RabbitMQ hostname                            |
| `AMQP_USER`    | no       | `guest`     | RabbitMQ username                            |
| `AMQP_PASS`    | no       | `guest`     | RabbitMQ password                            |
| `PORT`         | no       | `8082`      | HTTP listen port                             |

## Running

### Locally

```sh
export JWT_SECRET=your-secret
export M2M_SECRET=your-m2m-secret
./gradlew bootRun
```

Requires a running Neo4j instance. The service starts on port `8082`.

### Docker Compose

```sh
export JWT_SECRET=your-secret
export M2M_SECRET=your-m2m-secret
docker compose up --build
```

Starts Neo4j, RabbitMQ, and the service. Neo4j browser available at `http://localhost:7474`.

## Testing

```sh
./gradlew test
```

Tests use Mockito mocks — no Neo4j or RabbitMQ instance required.
