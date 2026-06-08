from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from config import settings


class BlobStorageService:

    def __init__(self, container_name: str):

        account_url = f"https://{settings.storage_account_name}.blob.core.windows.net"

        credential = DefaultAzureCredential()

        self.client = BlobServiceClient(account_url=account_url, credential=credential)

        self.container = self.client.get_container_client(container_name)

    async def upload_file(
        self,
        blob_name: str,
        content: bytes,
        content_type: str,
    ):

        self.container.upload_blob(
            name=blob_name, data=content, overwrite=True, content_type=content_type
        )

        return (
            f"https://{settings.storage_account_name}"
            f".blob.core.windows.net/"
            f"{self.container.container_name}/{blob_name}"
        )

    async def read_text(self, blob_name: str, encoding: str = "utf-8") -> str:

        download_stream = self.client.get_blob_client(
            container=self.container.container_name, blob=blob_name
        ).download_blob()

        content = download_stream.readall()

        return content.decode(encoding)
