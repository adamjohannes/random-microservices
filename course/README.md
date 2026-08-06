# Course Service

Python microservice for managing courses, chapters, and user enrollment. Built with FastAPI and SQLAlchemy (async), following hexagonal architecture.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- PostgreSQL 17

## Running locally

```bash
# Install dependencies
uv sync

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/course_db
export JWT_SECRET=your-secret-here

# Run migrations
uv run alembic upgrade head

# Start the server
uv run python main.py
```

## Running with Docker

```bash
docker compose up
```

The service starts on port **8081**. Interactive API docs: http://localhost:8081/docs

## Environment variables

| Variable       | Required | Default       | Description                                      |
|----------------|----------|---------------|--------------------------------------------------|
| `DATABASE_URL` | yes      | —             | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `JWT_SECRET`   | yes      | —             | HS256 secret shared with the Account service     |
| `PORT`         | no       | `8080`        | Port the server listens on                       |
| `ENVIRONMENT`  | no       | `development` | Set to `production` to disable auto-reload       |

## Running tests

Unit and use case tests (no database required):

```bash
uv run pytest tests/domain tests/application
```

Integration tests (requires a running PostgreSQL instance at `localhost:5432`):

```bash
uv run pytest tests/adapters
```

## API

| Method   | Path                                              | Description                        |
|----------|---------------------------------------------------|------------------------------------|
| `POST`   | `/users`                                          | Sync a user from the Account service |
| `GET`    | `/courses`                                        | List all courses (paginated)       |
| `POST`   | `/courses`                                        | Create a course                    |
| `GET`    | `/courses/authored`                               | List courses authored by the caller |
| `GET`    | `/courses/enrolled`                               | List courses the caller is enrolled in |
| `GET`    | `/courses/{id}`                                   | Get a course by ID                 |
| `PATCH`  | `/courses/{id}/archive`                           | Archive a course                   |
| `PATCH`  | `/courses/{id}/unarchive`                         | Unarchive a course                 |
| `POST`   | `/courses/{id}/enroll/{user_id}`                  | Enroll a user in a course          |
| `DELETE` | `/courses/{id}/enroll/{user_id}`                  | Unenroll a user from a course      |
| `POST`   | `/courses/{id}/chapters`                          | Add a chapter                      |
| `PUT`    | `/courses/{id}/chapters/{chapter_id}`             | Update a chapter                   |
| `PATCH`  | `/courses/{id}/chapters/{chapter_id}/archive`     | Archive a chapter                  |
| `PATCH`  | `/courses/{id}/chapters/{chapter_id}/unarchive`   | Unarchive a chapter                |

All endpoints require a `Authorization: Bearer <jwt>` header issued by the Account service `/login` endpoint.
