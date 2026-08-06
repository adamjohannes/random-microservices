import json
import logging

import aio_pika
import aio_pika.abc

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "domain_events"


class RabbitMQEventPublisher:
    def __init__(self, host: str, user: str, password: str) -> None:
        self._url = f"amqp://{user}:{password}@{host}/"
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        assert self._connection is not None
        channel = await self._connection.channel()
        self._exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def publish(self, routing_key: str, payload: dict) -> None:
        if self._exchange is None:
            logger.warning("event publisher not connected, skipping event %s", routing_key)
            return
        try:
            await self._exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )
        except Exception:
            logger.exception("failed to publish event %s", routing_key)


class NoopEventPublisher:
    async def publish(self, routing_key: str, payload: dict) -> None:
        pass
