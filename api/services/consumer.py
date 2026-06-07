from azure.identity import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
import json
from config import settings


class ServiceBusQueueConsumer:
    def __init__(
        self,
        queue_name: str,
        fully_qualified_namespace: str,
    ):
        self._namespace = fully_qualified_namespace or settings.servicebus_namespace
        self._queue_name = queue_name
        self._credential = DefaultAzureCredential()

    async def start(self):

        client = ServiceBusClient(
            fully_qualified_namespace=self._namespace, credential=self._credential
        )

        async with client:
            receiver = client.get_queue_receiver(
                queue_name=self._queue_name, max_wait_time=30
            )

            async with receiver:
                async for message in receiver:

                    payload = json.loads(str(message))

                    try:
                        await self.process_message(payload)

                        await receiver.complete_message(message)

                    except Exception:
                        await receiver.abandon_message(message)
                        raise

    async def process_message(self, payload: dict):
        pass
