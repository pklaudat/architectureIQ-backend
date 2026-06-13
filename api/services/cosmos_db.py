from typing import Any, Dict, List, Optional

from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.aio import CosmosClient
from azure.identity import DefaultAzureCredential
from config import settings


class CosmosDbService:
    def __init__(
        self,
        container_name: str,
    ):
        self.client = CosmosClient(
            settings.cosmos_db_url, credential=DefaultAzureCredential()
        )

        self.database = self.client.get_database_client(settings.cosmos_db_account_name)
        self.container = self.database.get_container_client(container_name)

    async def get_item(
        self,
        item_id: str,
        partition_key: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            return await self.container.read_item(
                item=item_id,
                partition_key=partition_key,
            )
        except CosmosResourceNotFoundError:
            return None

    async def create_item(
        self,
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.container.create_item(body=document)

    async def upsert_item(
        self,
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.container.upsert_item(body=document)

    async def replace_item(
        self,
        item_id: str,
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.container.replace_item(
            item=item_id,
            body=document,
        )

    async def delete_item(
        self,
        item_id: str,
        partition_key: str,
    ) -> None:
        await self.container.delete_item(
            item=item_id,
            partition_key=partition_key,
        )

    async def query_items(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        results = [
            item
            async for item in self.container.query_items(
                query=query, parameters=parameters or []
            )
        ]

        return results

    async def patch_item(
        self,
        item_id: str,
        partition_key: str,
        operations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return await self.container.patch_item(
            item=item_id,
            partition_key=partition_key,
            patch_operations=operations,
        )
