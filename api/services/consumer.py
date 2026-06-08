from typing import Optional
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient
import json
import time
from config import settings


class ServiceBusQueueConsumer:
    def __init__(
        self,
        queue_name: Optional[str] = None,
        fully_qualified_namespace: Optional[str] = None,
    ):
        self._namespace = fully_qualified_namespace or settings.servicebus_namespace
        self._queue_name = queue_name or settings.servicebus_queue
        self._credential = DefaultAzureCredential()

    async def start(self):
        
        print("starting new process")
        while True:
            try:
                async with self._credential:
                    client = ServiceBusClient(
                        fully_qualified_namespace=self._namespace, credential=self._credential
                    )

                    print("setup client for service bus consumer")

                    async with client:
                        receiver = client.get_queue_receiver(
                            queue_name=self._queue_name, max_wait_time=30
                        )

                        async with receiver:

                            async for message in receiver:

                                print("iterating over receiver")

                                payload = json.loads(str(message))

                                print(f"Received message {payload}")

                                try:
                                    await self.process_message(payload)

                                    await receiver.complete_message(message)

                                except Exception:
                                    await receiver.abandon_message(message)
                                    raise
            except Exception:
                time.sleep(3)

    async def process_message(self, payload: dict):
        pass
