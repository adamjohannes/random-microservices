# Notifications Service

Haskell microservice that consumes domain events from RabbitMQ and sends email notifications via SMTP. Built with servant (HTTP health endpoint), the `amqp` library (RabbitMQ consumer), and `smtp-mail` (email delivery), following hexagonal architecture.

## Architecture

```
src/Notification/
  Domain/Event.hs       EventPayload ADT — FromJSON/ToJSON discriminated on "event_type"
  Domain/Email.hs       EmailMessage — pure value type
  Domain/Dispatch.hs    dispatch :: EventPayload -> Maybe EmailMessage — pure mapping function
  Ports/EmailSender.hs  EmailSender typeclass (port)
  Adapters/SmtpEmail.hs SmtpEmailM — ReaderT SmtpConfig IO; implements EmailSender
  Adapters/AmqpConsumer.hs startConsuming — declares exchange + queues, installs consumers
  Config.hs             AppConfig loaded from environment; fails fast on missing required vars
  Health.hs             GET /health → {"status":"ok"}
app/Main.hs             Wires config, AMQP consumer (background thread), and Warp HTTP server
```

The domain layer (`Domain/`) is pure — no IO, no library dependencies beyond `aeson` and `base`. `Dispatch.hs` maps each event variant to an `EmailMessage` using plain pattern matching; adding a new event type without a dispatch branch causes a compile-time exhaustiveness warning.

## Events consumed

| Routing key                       | Queue                                         | Email sent to     |
|-----------------------------------|-----------------------------------------------|-------------------|
| `account.user_registered`         | `notifications.account.user_registered`       | New user          |
| `course.user_enrolled`            | `notifications.course.user_enrolled`          | Enrolled user     |
| `connections.request_received`    | `notifications.connections.request_received`  | Request addressee |
| `connections.request_accepted`    | `notifications.connections.request_accepted`  | Original requester |

All queues bind to the `domain_events` topic exchange (durable). Messages are ACKed only after a successful email send.

## Configuration

| Variable             | Required | Default                    | Description                          |
|----------------------|----------|----------------------------|--------------------------------------|
| `SMTP_HOST`          | yes      | —                          | SMTP server hostname                 |
| `SMTP_USER`          | yes      | —                          | SMTP username                        |
| `SMTP_PASS`          | yes      | —                          | SMTP password                        |
| `SMTP_FROM_ADDRESS`  | yes      | —                          | From address for outgoing emails     |
| `SMTP_PORT`          | no       | `587`                      | SMTP port                            |
| `SMTP_FROM_NAME`     | no       | `Platform Notifications`   | From display name                    |
| `AMQP_HOST`          | no       | `localhost`                | RabbitMQ hostname                    |
| `AMQP_USER`          | no       | `guest`                    | RabbitMQ username                    |
| `AMQP_PASS`          | no       | `guest`                    | RabbitMQ password                    |
| `PORT`               | no       | `8083`                     | HTTP listen port (health endpoint)   |

## Running

### Locally

```sh
export SMTP_HOST=smtp.example.com
export SMTP_USER=user@example.com
export SMTP_PASS=your-smtp-password
export SMTP_FROM_ADDRESS=notifications@example.com

cabal run notifications
```

Requires a running RabbitMQ instance. The health endpoint is available at `http://localhost:8083/health`.

### Docker Compose

```sh
docker compose up --build
```

Starts RabbitMQ, MailHog (local SMTP capture), and the service. Emails sent in development are captured by MailHog and visible at `http://localhost:8025`. No `SMTP_*` credentials are required when using MailHog.

## Testing

```sh
cabal test
```

Tests are pure — no RabbitMQ or SMTP connection required:

- `Domain/DispatchSpec` — verifies each event type maps to the correct recipient, subject, and body
- `Domain/EventSpec` — JSON round-trip tests for all four event payload types
- `Adapters/SmtpEmailSpec` — mock `EmailSender` using `WriterT` to verify captured email values
