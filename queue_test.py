import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy

try:
    print("Azure Queue storage - Python quickstart sample")
    # Quickstart code goes here
except Exception as ex:
    print('Exception:')
    print(ex)