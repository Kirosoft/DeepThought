import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

agent_config = AgentConfig()

try:
    print("Azure Queue storage - Python quickstart sample")
    # Quickstart code goes here
    connect_str = os.getenv('QUEUE_STORAGE_CONNECTION_STRING')

    # With connection string
    # client = QueueClient(
    #     "DefaultEndpointsProtocol=https;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;QueueEndpoint=https://127.0.0.1:10001/devstoreaccount1;", "main"
    # )
    #client = QueueClient("https://127.0.0.1:10001/devstoreaccount1/main", DefaultAzureCredential())
    #client = QueueClient(devsettings=true)
    # With account name and key
    # client = QueueClient(
    #     "https://127.0.0.1:10001/devstoreaccount1/queue-name",
    #     StorageSharedKeyCredential("devstoreaccount1", "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==")
    # )

    connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"

    # Initialize the QueueServiceClient
    queue_service_client = QueueServiceClient.from_connection_string(connection_string)

except Exception as ex:
    print('Exception:')
    print(ex)