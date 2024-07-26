# Installation (needs updating)

Download and install Azure Core Tools runtime (Python)

https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python

For VSCode install the Azure Functions extension: ms-azuretools.vscode-azurefunctions
For local running you will also need to install Azurite Blob Serive (running on port 10000)

## Download and install CosmoDB emulator

https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-develop-emulator?tabs=windows%2Ccsharp&pivots=api-nosql
https://aka.ms/cosmosdb-emulator (takes a few minutes to start)

### data explorer:

https://localhost:8081/_explorer/index.html


## Queue storage

Account name: devstoreaccount1
Account key: Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==


## LLM 

OLLAMA installation:<br>

https://ollama.com/download

Install a model e.g.  llama3:<br>

https://ollama.com/library/llama3


## Configuration of services and keys

Setup the secret tokens in the local.settings.json file:

{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",

    "ELASTIC_CLOUD_ID":"<CloudId>",
    "ELASTIC_API_KEY":"<ApiKey>",
    "ES_INDEX":"embedding_test_index",
    "ES_INDEX_ROLES": "deepthought_roles",
    "ES_INDEX_HISTORY": "deepthought_history",
    "ES_INDEX_TOOLS": "deepthought_tools",
    "ES_NUM_DOCS": "5",

    "LLM_TYPE":"openai",
    "OPENAI_API_KEY":"<your api key for open-ai>",
    "OPENAI_MODEL":"gpt-4-turbo-preview",
    "EMBEDDING_MODEL":"text-embedding-3-small",
    "MAX_SESSION_TOKENS": "4096"
  }
}

## running (see .vscode/settings.json)

.venv\Scripts\activate ; func host start 

## other tools

Installation of mqttx app (https://mqttx.app/) for local testing 


