from typing import Optional
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import json
from config import settings


class ServiceBusQueuePublisher:
    def __init__(
        self,
        queue_name: Optional[str] = None,
        fully_qualified_namespace: Optional[str] = None,
    ):
        self._namespace = fully_qualified_namespace or settings.servicebus_namespace
        self._queue_name = queue_name or settings.servicebus_queue
        self._credential = DefaultAzureCredential()

    async def publish(self, payload: dict, subject: Optional[str] = None):
        async with self._credential:
            client = ServiceBusClient(
                fully_qualified_namespace=self._namespace, credential=self._credential
            )

            async with client:
                sender = client.get_queue_sender(queue_name=self._queue_name)

                async with sender:
                    message = ServiceBusMessage(
                        body=json.dumps(payload),
                        content_type="application/json",
                        subject=subject,
                    )

                    await sender.send_messages(message)
