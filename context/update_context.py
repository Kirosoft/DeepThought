import os
import sys
import json
import requests
import base64
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
from core.llm.embedding_base import EmbeddingBase

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from os.path import join
import numpy as np
import pathlib

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

agent_config = AgentConfig()
db = AgentDBBase(agent_config, agent_config.INDEX_CONTEXT)
embedding = EmbeddingBase(agent_config, agent_config.EMBEDDING_MODEL)


def embedding_to_lsh(embedding, num_planes=10, seed=123):
    
    # Generate a set of random planes (vectors) for the projection
    planes = np.random.normal(size=(num_planes, len(embedding)))
    
    # Project the embedding onto each plane and binarize the results
    projections = np.dot(planes, embedding)
    binary_projections = (projections >= 0).astype(int)
    
    # Convert the binary projections to a string hash
    hash_str = ''.join(str(bit) for bit in binary_projections)
    
    # Return the hash as a string
    return hash_str

def get_content(url, path):
    result = requests.get(url, auth=("kirosoft","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"))

    if result.status_code == 200:
        data = json.loads(result.content)
        if "content" in data:
            decoded_content = base64.b64decode(data["content"])
            print(decoded_content)
            process_content(url, str(decoded_content), path)
    else:
        print(f"failed to fetch {url} Error: {result.status_code}")    


def process_content(url, content, path):
    text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=100)
    chunks = text_splitter.split_text(content)

    # Adding metadata to documents
    for i, chunk in enumerate(chunks):
        doc={}
        result=embedding.get_embedding(chunk)
        vector = result.data[0].embedding
        doc["url"] = url
        doc["path"] = path
        doc["embedding"] = vector
        doc["content"] = chunk
        hash = embedding_to_lsh(vector,256)
        row_key = int(hash, 2).to_bytes(-(-len(hash) // 8), byteorder='big')
        # encode the int array into a base64 string
        encoded = base64.b64encode(row_key).decode('utf-8').replace('/','-').replace('=','_')

        db.index(id=encoded, doc=doc)


def test_query():

    txt = "what is the policy on code pairing"
    result=embedding.get_embedding(txt)
    vector = result.data[0].embedding

    results = db.similarity_search(vector)

    # Print the top 5 results
    for i, item in enumerate(results):
        print(f'Result {i+1}: similarity={item["similarity"]} path={item["path"]}')

def do_import():
    url = "https://api.github.com/repos/ukho/docs/git/trees/main?recursive=1"  # The basic URL to use the GitHub API
    r = requests.get(url, auth=(agent_config.GITHUB_USER, agent_config.GITHUB_KEY))
    res = r.json()

    for file in res["tree"]:
        file_type = pathlib.Path(file["path"]).suffix
        print(f'{file["path"]} suffix {file_type} url {file["url"]}')
        if file_type.lower() == ".md":
            txt = get_content(file["url"], file["path"])


test_query()