import jinja2
from elasticsearch import Elasticsearch
from urllib.parse import unquote

from core.agent_config import AgentConfig

class AgentRole:

    def __init__(self, agent_config : AgentConfig):
        self.__agent_config = agent_config
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.db = Elasticsearch(cloud_id=self.__agent_config.ELASTIC_CLOUD_ID, api_key=self.__agent_config.ELASTIC_API_KEY)

    def __get_role_prompt(self, role: str) -> str:
        # determine role
        result = self.db.get(index=self.__agent_config.ES_INDEX_ROLES, id = role)

        if not result["_source"]:
            result = self.db.get(index=self.__agent_config.ES_INDEX_ROLES, id = "default_role")

        self.role_prompt = unquote(result["_source"]["prompt"])

        return self.role_prompt

    def get_prompt(self, context, session_history, role) -> str:
        role_prompt = self.__get_role_prompt(role)

        # transform the search results into json payload
        context_results = []
        for doc in context:
            doc_source = {**doc.metadata, 'page_content': doc.text}
            context_results.append(doc_source)

        # session history
        session_results = []
        for doc in session_history:
            doc_source = {**doc['_source']}
            session_results.append(doc_source)

        # create the prompt template
        template = jinja2.Template(role_prompt)
        completed_prompt_template = template.render(question=self.__agent_config.question, docs=context_results, history=session_results)

        return completed_prompt_template

