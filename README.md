# DeepThought

Functional agentic framework

<img src="./images/_d376e6fa-4fea-409b-a841-00e47f35bdad.jpeg"  height="500">
<br>
"Deep Thought announced that the new machine would be so large, it would resemble a planet, and be of such complexity that organic life itself would become part of its operating matrix." - Douglas Adams, Hitch Hikers Guide To The Galaxy

# Features

* Code free AI agent framework to orchestrate business flows
* Fully deployed locally or at scale in the cloud
* Recursive agent implementation with Domain Speciifc Language (DSL) built into the template
* Support for context based search (RAG)
* Dynamic workflow between agents

# Agent Features

* RAG Support using VectorDB
* Multi-Agent session learning
* Function calling support
* JSON Output formatting
* Reflective queries
* Includes multi-shot learning
* Change LLM model on a per agent basis

# VectorDB Integrations

ElasticCloud<br>
CosmosDB (custom vector DB implementation)<br>

# LLM Integrations

OpenAI<Br>
Ollama (local)<br>
GroqCloud<br>

# Demo

Job posting agent


> [!IMPORTANT]  
<bold>
This project is currently in a very early development/experimental stage. <br/>
There are a lot of unimplemented/broken features at the moment. <br/>
</bold>

# Terminology

Functions/Tools - 3rd party functions to perform specific tasks e.g. scrape a web page etc
Specification - Used to define the JSON output format from an AI conversation (not used like 'functions')

# Examples




## Example request



## Update roles database

```
python roles/update_roles.py "<path-to-roles-directory>"
```

## Update tools database

```
python tools/update_tools.py "<path-to-tools-directory>"
```

# TODO:

UI:

Develop TTS and STT interface
OR
Develop flow based interface

Docs:

* Fully local run installation instructions<br/>


System

Support multiple users

Problems:


Features:

* Self learning role/tool/specifications 
* allow all role fields to be overriden from input<br>
* run a role purely from the payload input<br>
* Build a message routing framework<br>
* develop a multie role agent demo<br>

<strike>* fix the ollama sdk to support function calling<br></strike>
<Strike>* Local cosmodb init is slow ... <br></strike>
<strike>* develop a job posting agent demo<br></strike>
<Strike>* Support JSON schema specification outputs<br></strike>
<strike>* LLM Model overrides from templates e.g. change the llm model based on the role<br></strike>
<Strike>* rework function calling - now known as tools<br></strike>
<Strike>* Add support for Grok<br/></strike>
<strike>* Add support for local AI model - LLama3 - DONE<br></strike>
<strike>* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE<br></strike>

# Installation

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

