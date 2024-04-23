import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import base64

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

agent_config = AgentConfig()

try:
    print("Azure Queue storage - Python quickstart sample")
    # Quickstart code goes here
    connection_string = os.getenv('QUEUE_STORAGE_CONNECTION_STRING')

    # Initialize the QueueServiceClient
    queue_service_client = QueueServiceClient.from_connection_string(connection_string)
    queue_client = queue_service_client.get_queue_client("main");
    document = {"input": "please create a new role to find information about a ukho policy","role":"create_role"}

    # Convert the document to a JSON string
    message = base64.b64encode(json.dumps(document).encode('utf-8')).decode('utf-8')

    # Send the message
    queue_client.send_message(message)
    print("Message added to the queue:", message)

except Exception as ex:
    print('Exception:')
    print(ex)