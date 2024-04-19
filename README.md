# DeepThought

Functional agentic framework

<img src="_d376e6fa-4fea-409b-a841-00e47f35bdad.jpeg"  height="500">
<br>
"Deep Thought announced that the new machine would be so large, it would resemble a planet, and be of such complexity that organic life itself would become part of its operating matrix." - Douglas Adams, Hitch HIkers Guide To The Galaxy

# Features

* Cloud first functional agent framework
* Stateless agent implementation with templated roles
* Flexible tool/skills model
* Build interactive session roles (either agent to agent of agent to human)
* Support for context based search (RAG)
* Dynamic workflow between agents


> [!IMPORTANT]  
> This project is currently in a very early development/experimental stage. There are a lot of unimplemented/broken features at the moment. 


# Template Features

* Context search by template specification. e.g. {% for doc in docs -%}

```
{% for doc in docs -%}
---
NAME: {{ doc.filename }}
PASSAGE:
{{ doc.page_content }}
---

{% endfor -%}
----
```

* Session history (aka Chat or Agent mode) by template specification e.g. {% for qa in history -%}

```
{% for qa in history -%}
{{qa.question}}
{{qa.answer}}
{% endfor -%}

{{ question }}

```

* Functional calling by template specification. Use [[tool1, tool2 ... tooln]] to specifiy available tools from the tool database

```
[[get_n_day_weather_forecast,get_current_weather]]
Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

{% for qa in history -%}
{{qa.question}}
{{qa.answer}}
{% endfor -%}

{{ question }}
```

* Routing hints - you can indicate which agents might be able to help with a response e.g. [[tool1,tool2,@rolename1,@rolename2]]

Where @rolename1 is a registered agent in the system


## Example request

First request (no session token):-

```
{
    "input": "{\"SystemProperties\":{},\"question\":\"plymouth in celcius\", \"role\":\"weather_forecast\", \"session_token\":\"\"}"
}
```

subsequent, request top continue the conversation - with the session token:

```
{
    "input": "{\"SystemProperties\":{},\"question\":\"follow up question\", \"role\":\"weather_forecast\", \"session_token\":\HqvYXY4B97jYMDJrrnqz"\"}"
}
```


## Update roles database

```
python roles/update_roles.py "<path-to-roles-directory>"
```

## Update tools database

```
python tools/update_tools.py "<path-to-tools-directory>"
```

# TODO:

* Build a message routing framework<br>
* Model overrides from templates<br>
* Add support for local AI model - LLama3 - Inprogress<br>
<strike>* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE</strike>

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

