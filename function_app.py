import azure.functions as func
import logging
from langchain_community.vectorstores import ElasticsearchStore
from llm_integrations import get_llm
from elasticsearch_client import elasticsearch_client
from langchain.embeddings import OpenAIEmbeddings
import os
import jinja2
import json
from urllib.parse import unquote


app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtcore",
                               connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
@app.event_hub_output(arg_name="answer",event_hub_name="eventhub_output",
                      connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB")
def CoreLLMAgent(azeventhub: func.EventHubEvent, answer: func.Out[str]) -> func.HttpResponse:
    body = json.loads(azeventhub.get_body().decode('utf-8'))
    question=body["question"]
    role=body["role"]
    logging.info('PythonCoreLLMAgent processed an event: %s',question)

    # TODO: should there be an index per role or per agent or both?
    INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    ES_NUM_DOCS = int(os.getenv("ES_NUM_DOCS", "10"))
    ES_INDEX_ROLES = os.getenv("ES_INDEX_ROLES", "ai_roles")

    # connect to elastic and intialise a connection to the vector store
    store = ElasticsearchStore(
        es_connection=elasticsearch_client,
        index_name=INDEX,
        embedding=OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY, model = EMBEDDING_MODEL)
    )

    result = store.client.get(index=ES_INDEX_ROLES, id = role)
    rag_prompt = unquote(result.body["_source"]["prompt"])
    # result = store.client.search(index=ES_INDEX_ROLES, query={"match": {"_id": "ukho_policy"}})

    # use the input question to do a lookup similarity search in elastic
    store.client.indices.refresh(index=INDEX)
    results = store.similarity_search(question, k = ES_NUM_DOCS)

    # transform the search results into json payload
    doc_results = []
    for doc in results:
        doc_source = {**doc.metadata, 'page_content': doc.page_content}
        doc_results.append(doc_source)
 
    # create the prompt template
    template = jinja2.Template(rag_prompt)
    qa_prompt = template.render(question=question, docs=doc_results)

    # send to the AI bot
    answer_str = ''
    for chunk in get_llm().stream(qa_prompt):
        answer_str += chunk.content


    logging.info('Answer: %s',answer_str)
    answer.set(f'{answer_str}')

    return func.HttpResponse(answer_str)

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtoutput",
                               connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
def eventhub_output(azeventhub: func.EventHubEvent):

    logging.info('[output]: %s',azeventhub.get_body().decode('utf-8'))
