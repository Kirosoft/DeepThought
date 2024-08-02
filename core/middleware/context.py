from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.llm.embedding_base import EmbeddingBase
from urllib.parse import unquote
from core.middleware.loader import Loader
import json
import logging
import urllib3
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import base64
import numpy as np
from os import path

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

    
class Context:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.db_contexts_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_CONTEXT_DEFINITION, user_id, tenant)
        self.db_contexts_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_CONTEXT_DEFINITION, "system", "system")
        self.embedding = EmbeddingBase(agent_config)
        self.user_id = user_id
        self.tenant = tenant

    def load_all_contexts(self):
        system_contexts = list(self.db_contexts_system.get_all())
        user_contexts = list(self.db_contexts_user.get_all())

        # TODO: tenant contexts?
        return { "system_contexts": system_contexts, "user_contexts": user_contexts}

    def save_context(self, context, level = "user"):
        # TODO: split out context data to be context seachable?
        if level == "user":
            context["level"] = "user"
            return self.db_contexts_user.index(context["name"], context)
        elif level == "system" or self.tenant=="system":
            context["level"] = "system"
            return self.db_contexts_system.index(context["name"], context)


    def get_context(self, context_name: str) -> str:
        
        # determine context, default user_id, default tenant
        result = self.db_contexts_user.get(context_name)

        if result is None:
            result = self.db_contexts_system.get(context_name)
            
            if result is None:
                logging.error(f"Request context not found {context_name}")
                return None

        return result

        
    def delete_context(self, context_name, level = "user"):
        
        if (level == "user"):
            return self.db_contexts_user.delete(context_name)
        else:
            return self.db_contexts_system.delete(context_name)


    def embedding_to_lsh(self, embedding, num_planes=10, seed=123):

        # Generate a set of random planes (vectors) for the projection
        planes = np.random.normal(size=(num_planes, len(embedding)))

        # Project the embedding onto each plane and binarize the results
        projections = np.dot(planes, embedding)
        binary_projections = (projections >= 0).astype(int)

        # Convert the binary projections to a string hash
        hash_str = ''.join(str(bit) for bit in binary_projections)

        # Return the hash as a string
        return hash_str

    def schedule_for_deletion(self, context_name, version, ttl_seconds=60*5):
        full_context_name = f'{self.agent_config.INDEX_VECTOR}_{context_name}_v{version}'
        db_vector_chunks = AgentDBBase(self.agent_config, full_context_name, self.user_id, self.tenant)
        db_vector_chunks.set_ttl_for_data_type(full_context_name, ttl_seconds)
    
    def process_text_content(self, docs, context_name, version, options):
        text_db = AgentDBBase(self.agent_config, f'{self.agent_config.INDEX_TEXT}_{context_name}_v{version}', self.user_id, self.tenant)
        for doc in docs:
            text_doc = {}
            text_doc["url"] = doc.metadata["source"] if "source" in doc.metadata else ""
            text_doc["path"] = doc.metadata["path"] if "path" in doc.metadata else ""
            text_doc["content"] = doc.page_content
            head, tail= path.split(text_doc["path"])
            text_db.index(id=tail, doc=text_doc)

    def process_vector_content(self, docs, context_name, version, rag_options):

        db_vector_chunks = AgentDBBase(self.agent_config, f'{self.agent_config.INDEX_VECTOR}_{context_name}_v{version}', self.user_id, self.tenant)
        chunk_size = rag_options['chunk_size'] if 'chunk_size' in rag_options else 5000
        chunk_overlap = rag_options['chunk_overlap'] if 'chunk_overlap' in rag_options else 100
        separator = rag_options['separator'] if 'separator' in rag_options else "\n\n"
        is_regex = rag_options['is_regex'] if 'is_regex' in rag_options else False
        strategy = rag_options['strategy'] if 'strategy' in rag_options else 'CharacterTextSplitter'

        for doc in docs:

            match strategy:
                case 'CharacterTextSplitter':
                    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator=separator,is_separator_regex=is_regex)
                    chunks = text_splitter.split_text(doc.page_content)

            # Adding metadata to documents
            for i, chunk in enumerate(chunks):
                vector_doc={}
                result=self.embedding.get_embedding(chunk)
                vector = result.data[0].embedding
                # TODO support output mapper for meta data properties
                vector_doc["url"] = doc.metadata["source"] if "source" in doc.metadata else ""
                vector_doc["path"] = doc.metadata["path"] if "path" in doc.metadata else ""
                vector_doc["embedding"] = vector
                vector_doc["content"] = chunk

                hash = self.embedding_to_lsh(vector,256)
                row_key = int(hash, 2).to_bytes(-(-len(hash) // 8), byteorder='big')
                # encode the int array into a base64 string
                encoded = base64.b64encode(row_key).decode('utf-8').replace('/','-').replace('=','_')
                vector_doc["encoded"] = encoded

                db_vector_chunks.index(id=encoded, doc=vector_doc)

    def process_content(self, docs, context_name, version):
        context = self.get_context(context_name)
        rag_options = context['rag_options'] if 'rag_options' in context else None

        if rag_options is not None:
            self.process_vector_content(docs, context_name, version, rag_options)
        else:
            self.process_text_content(docs, context_name, version, context["options"])







