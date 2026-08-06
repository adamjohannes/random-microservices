# Microservices

A polyglot microservices monorepo built as a proof of concept: the choice of language or framework is not a blocker for spinning up a set of well-structured, interoperating services. Each service is independently deployable, uses the same architectural pattern (hexagonal/ports-and-adapters), and communicates over standard HTTP and AMQP interfaces.

## Services

| Service | Language | Stack | Port |
|---|---|---|---|
| [account](./account) | Go | Gin, GORM, PostgreSQL | 8080 |
| [course](./course) | Python | FastAPI, SQLAlchemy async, PostgreSQL | 8081 |
| [connections](./connections) | Java | Spring Boot 3, Neo4j | 8082 |
| [notifications](./notifications) | Haskell | servant, amqp, smtp-mail | 8083 |
| [web](./web) | TypeScript | Vue 3, Vite, Tailwind CSS | 5173 |

All services share the same HS256 JWT for user authentication, publish domain events to a RabbitMQ topic exchange, and follow the same exception-to-HTTP-status mapping regardless of language.

## Running

```sh
export JWT_SECRET=your-secret
export M2M_SECRET=your-m2m-secret
./setup.sh
```

`setup.sh` validates dependencies and required environment variables, then starts each service via `docker compose`.

For the frontend:

```sh
cd web && npm install && npm run dev
```
