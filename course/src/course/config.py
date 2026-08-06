import os


class Config:
    def __init__(self) -> None:
        self.database_url: str = self._require("DATABASE_URL")
        self.jwt_secret: str = self._require("JWT_SECRET")
        self.port: int = int(os.getenv("PORT", "8080"))
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.amqp_host: str = os.getenv("AMQP_HOST", "localhost")
        self.amqp_user: str = os.getenv("AMQP_USER", "guest")
        self.amqp_pass: str = os.getenv("AMQP_PASS", "guest")

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"required environment variable not set: {key}")
        return value
