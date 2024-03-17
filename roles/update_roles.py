import os
import sys
from utils.file_walker import find_in_files
from os.path import join
from elasticsearch import Elasticsearch
from langchain_community.document_loaders import TextLoader
from pathlib import Path
import json

settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)


# secrets
ELASTIC_CLOUD_ID = settings["Values"]["ELASTIC_CLOUD_ID"]
ELASTIC_API_KEY = settings["Values"]["ELASTIC_API_KEY"]

# settings
ES_INDEX_ROLES = settings["Values"]["ES_INDEX_ROLES"]

print(f"Elastic cloud id {ELASTIC_CLOUD_ID}")
db = Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY)

def index_docs_elastic(directory_path, extension):
    file_list = find_in_files(directory_path, extension)

    for file_path in file_list:
        print(file_path)

        # Load the document
        loader = TextLoader(file_path, encoding="utf-8")
        prompt = loader.load()

        prompt_name = Path(file_path).stem

        db.index(
            index=ES_INDEX_ROLES,
            id=prompt_name,
            document={
                "filename": file_path,
                "prompt": prompt[0].page_content
            },
        )
        print(f"{file_path} imported ")



if (len(sys.argv) > 1):
    local_path = sys.argv[1]
    print(f"Scanning: {local_path}")

    # a second argument means skip the indexing phase
    #if (len(sys.argv) < 3):
    # read the local .prompt files and index into elastic
    index_docs_elastic(local_path, '.prompt')
    
    print("Done")
else:
    print("USEAGE: import_local_docs <path> <skip>")