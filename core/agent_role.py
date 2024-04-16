import jinja2
from urllib.parse import unquote
import logging

from core.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
class AgentRole:

    def __init__(self, agent_config : AgentConfig):
        self.__agent_config = agent_config
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.db = AgentDBBase(self.__agent_config)

    def __get_role_prompt(self, role: str) -> str:
        
        if not hasattr(self, 'role_prompt'):
            # determine role
            result = self.db.get(index=self.__agent_config.ES_INDEX_ROLES, id = role)

            if not result["_source"]:
                result = self.db.get(index=self.__agent_config.ES_INDEX_ROLES, id = "default_role")

            self.role_prompt = unquote(result["_source"]["prompt"])

        return self.role_prompt

    # Automatically detect if a context search by the role prompt template
    # showing it is expecting some data
    def use_context_search(self, role):
        role_prompt = self.__get_role_prompt(role)

        return role_prompt.find("{% for doc in docs -%}") != -1

    # Automatically detect if session history is used via role prompt template
    # showing it is expecting some data
    def use_session_history(self, role):
        role_prompt = self.__get_role_prompt(role)

        return role_prompt.find("{% for qa in history -%}") != -1

    # the first part of the temmplate can specify tools to be used
    # the tool names are comma seperated between [[ ]]
    # e.g. [[ tool1, tool2, tool3]]
    def __parse_tools(self, role_prompt):
        self.tools = []
        self.routing = []
        role_parts = role_prompt.split("]]")

        if (len(role_parts) == 1):
            return role_prompt
        else:
            if (len(role_parts) != 2):
                logging.warning(f"Unexpected format found trying to parse tools {role_parts}")
            
            try:
                routes_or_tools = role_parts[0][2:].split(",")

                tool_list = [tool.strip() for tool in routes_or_tools if tool[0].strip() != '@']
                self.routing = [route.strip()[1:] for route in routes_or_tools if route[0].strip() == '@']

                # find and parse the tools
                if len(tool_list) > 0:
                    self.tools = self.db.multi_get(index=self.__agent_config.ES_INDEX_TOOLS, docs=[{"_id":tool} for tool in tool_list])

            except:
                logging.error(f"Error found parsing tools list. Check syntax is correct. {role_parts[0][2:]}")

            return role_parts[1]

    # loads the role prompt from the database
    # populates the template with context data based on the the supplied user input 'question'
    # the context data search is driven by the template format expecting context data
    # for example the template includes the '{% for doc in docs -%}' expecting data
    # should be inserted
    def get_completed_prompt(self, context, session_history, role) -> str:
        role_prompt = self.__get_role_prompt(role)

        role_prompt = self.__parse_tools(role_prompt)

        # transform the search results into json payload
        context_results = []
        for doc in context:
            doc_source = {**doc.metadata, 'page_content': doc.page_content}
            context_results.append(doc_source)

        # session history
        session_results = []
        for doc in session_history:
            doc_source = {**doc['_source']}
            session_results.append(doc_source)

        # create the prompt template
        # TODO: We need to be careful to need exceed the token length. We may need a summarizing step here
        template = jinja2.Template(role_prompt)
        completed_prompt_template = template.render(question=self.__agent_config.input, docs=context_results, history=session_results)

        return completed_prompt_template, self.tools, self.routing

