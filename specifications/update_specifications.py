import os
import sys
from utils.file_walker import find_in_files
from os.path import join
from elasticsearch import Elasticsearch
from langchain_community.document_loaders import TextLoader
from pathlib import Path
import json
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

agent_config = AgentConfig()
db = AgentDBBase(agent_config, agent_config.INDEX_SPECS, "system", "system")

def index_docs_elastic(directory_path, extension):
    file_list = find_in_files(directory_path, extension)

    for file_path in file_list:
        print(file_path)

        # Load the document
        loader = TextLoader(file_path, encoding="utf-8")
        prompt = loader.load()

        prompt_name = Path(file_path).stem

        db.index(
            id=prompt_name,
            doc={
                "filename": file_path,
                "specification": prompt[0].page_content
            },
        )
        print(f"{file_path} imported ")

if (len(sys.argv) > 1):
    local_path = sys.argv[1]
    print(f"Scanning tools: {local_path}")

    # a second argument means skip the indexing phase
    #if (len(sys.argv) < 3):
    # read the local .prompt files and index into elastic
    index_docs_elastic(local_path, '.specification')
    
    print("Done")
else:
    print("USEAGE: update_specifications <path> <skip>")