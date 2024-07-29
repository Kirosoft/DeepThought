from urllib.parse import unquote
import logging

from core.agent.agent_config import AgentConfig
from core.agent.agent_memory import AgentMemory
from core.agent.agent_memory_role import AgentMemoryRole
from core.llm.llm_base import LLMBase
from core.middleware.role import Role
from core.middleware.tool import Tool
from core.middleware.spec import Spec

class AgentRole:

    def __init__(self, user_id, tenant, user_settings_keys):
        self.agent_config = AgentConfig(user_settings_keys=user_settings_keys)
        self.user_id = user_id
        self.tenant = tenant
        self.role = Role(self.agent_config, user_id, tenant)
        self.tool = Tool(self.agent_config, user_id, tenant)
        self.spec = Spec(self.agent_config, user_id, tenant)
        self.agent_memory = None
        self.icl_memory = None

    def run_agent(self, body):
        self.agent_config.update_from_body(body)

        if self.agent_config.is_valid():
            logging.info('run_agent processed an event: %s',self.agent_config.input)
        

            llm = LLMBase(self.agent_config)

            # use the configured role to find the prompt and populate with the context and session history as required
            completed_prompt = self.get_completed_prompt(self.agent_config.role)

            llm_result = llm.inference(completed_prompt)

            self.agent_memory.save_session_history(llm_result)

            return llm_result
        else:
            return None

    # loads the role prompt from the database
    # populates the template with context data based on the the supplied user input 'question'
    # the context data search is driven by the template format expecting context data
    # for example the template includes the '{% for doc in docs -%}' expecting data
    # should be inserted
    def get_completed_prompt(self, role_name:str) -> object:
        
        role = self.role.get_role(role_name, self.agent_config.input)

        messages = []
        options = {}

        if self.agent_memory is None:
            context = self.role.get_context(role, self.agent_config)
            self.agent_memory = AgentMemory(self.agent_config, self.user_id, self.tenant, context)

        if self.icl_memory is None:
            icl_context = self.role.get_icl_context(role, self.agent_config)
            self.icl_memory = AgentMemory(self.agent_config, self.user_id, self.tenant, icl_context)

        # user can override the examples 
        output_format_json = self.spec.get_specs(role['output_format']) if 'output_format' in role else []

        # construct the system prompt
        # TODO: detect if the output is a spec and prompt the whole spec as JSON {spec}
        system_prompt = f"""
            {role["description"] if "description" in role else ""}
            {role["role"] if "role" in role else ""}
            {f"Expected input: {role['expected_input']}" if role['expected_input'] != "" else ""}
            {f"Think about your response. If all the INPUT was provided and the OUTPUT seems complete, OUTPUT [[**FINISHED**]] OR [[**NOT_FINISHED**]] if not finished. You *MUST* output one or the other based on the circumstances."}
            {f"Example output: {role['examples']}" if role['examples'] != "" and self.icl_memory is not None else ""}
            {f"output format: JSON SCHEMA [{','.join(output_format_json)}] do not invent any new fields or change the output scehma in any way. Any UNESCAPED characters should be escaped. Ensuer there are no NEWLINE characters inserted. Ensure there are no back slashes or enescaped characters.The answer to the user should just be text and not JSON" if len(output_format_json) != 0 else ""}
        """           
        # ICL Mode - In Context Learning
        if self.role.is_icl(role):
            system_prompt += f"Example responses:\n"
            for doc in self.icl_memory.get_context(self.agent_config.input):
                system_prompt += f"{doc['content']}"

        # TODO: AutoRoute - use the input to fine the agent role automatically

        # RAG - context injection
        # build the function message
        # transform the search results into json payload
        if self.role.is_rag(role):
            for doc in self.agent_memory.get_context(self.agent_config.input):
                system_prompt += f"NAME: {doc['path']}"
                system_prompt += f"CONTENT: {doc['content']}"

        messages.append({"role":"system", "content":system_prompt})

        # ASSISTANT - Session history
        # TODO: does the session history need to be sequenced to replay in the right order?
        if (not self.agent_config.new_session):
            session_results = self.agent_memory.get_session_history(self.agent_config.session_token)
            for session in session_results:
                messages.append({"role":"user", "content":session["input"]})
                messages.append({"role":"system", "content":session["answer"]})

        # consuct the latest input as the last message
        user_prompt = {
            "role":"user",
            "content": self.agent_config.input
        }
        messages.append(user_prompt)

        tools  = self.tool.get_tools(role["tools"]) if "tools" in role and len(role["tools"]) > 0 else []

        if "options" in role and "model_override" in role["options"]:
            options["model_override"] = role["options"]["model_override"]

        return {"messages":messages, "tools":tools, "options":options, "output_format_json":output_format_json}
