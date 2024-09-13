from urllib.parse import unquote
import logging

from core.agent.agent_config import AgentConfig
from core.agent.agent_memory import AgentMemory
from core.agent.agent_memory_role import AgentMemoryRole
from core.llm.llm_base import LLMBase
from core.middleware.role import Role
from core.middleware.function_definition import FunctionDefinition
from core.middleware.context import Context
from core.middleware.schema_definition import SchemaDefinition
from  core.utils.schema import create_dynamic_model
import json

class AgentRole:

    def __init__(self, user_id, tenant, user_settings_keys):
        self.agent_config = AgentConfig(user_settings_keys=user_settings_keys)
        self.user_id = user_id
        self.tenant = tenant
        self.role = Role(self.agent_config, user_id, tenant)
        self.function_manager = FunctionDefinition(self.agent_config, user_id, tenant)
        self.spec = SchemaDefinition(self.agent_config, user_id, tenant)
        self.context = Context(self.agent_config, user_id, tenant)
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

        input = self.agent_config.input
    
        # get the role or find an auto assigned one
        role = self.role.get_role(role_name, input)

        tools = self.function_manager.load_all_tools() if "options" in role and "prefetch_tools" in role["options"] and "prefetch_tools" in role["options"] and role["options"]["prefetch_tools"] else None
        #roles = self.role.load_all_roles() if "options" in role and "prefetch_roles" in role["options"] and "prefetch_roles" in role["options"] and role["options"]["prefetch_roles"] else None

        messages = []
        options = {}

        if self.agent_memory is None:
            context = self.role.get_context(role, self.agent_config)
            self.agent_memory = AgentMemory(self.agent_config, self.user_id, self.tenant, context)

        if self.icl_memory is None:
            icl_context = self.role.get_icl_context(role, self.agent_config)
            self.icl_memory = AgentMemory(self.agent_config, self.user_id, self.tenant, icl_context)

        # user can override the examples 
        # TODO: probably deprecated with openai structure response mode
        output_format_json = "" #self.spec.get_specs(role['output_format']) if 'output_format' in role else []

        # construct the system prompt
        # TODO: detect if the output is a spec and prompt the whole spec as JSON {spec}
        system_prompt = f"""
            {role["description"] if "description" in role else ""}
            {role["role"] if "role" in role else ""}
            {f"Expected input: {role['expected_input']}" if role['expected_input'] != "" else ""}
            {f"Example output: {role['examples']}" if "examples" in role and role['examples'] != "" and self.icl_memory is not None else ""}
            {f"output format: JSON SCHEMA [{','.join(output_format_json)}] do not invent any new fields or change the output scehma in any way. Any UNESCAPED characters should be escaped. Ensuer there are no NEWLINE characters inserted. Ensure there are no back slashes or enescaped characters.The answer to the user should just be text and not JSON" if len(output_format_json) != 0 else ""}
        """           
        # ICL Mode - In Context Learning
        if self.role.is_icl(role) and isinstance(input, str):
            system_prompt += f"Example responses:\n"
            for doc in self.icl_memory.get_context(input):
                system_prompt += f"{doc['content']}"

        # RAG - context injection
        # build the function message
        # transform the search results into json payload
        if self.role.is_rag(role) and isinstance(input, str):
            for doc in self.agent_memory.get_context(input):
                system_prompt += f"NAME: {doc['path']}"
                system_prompt += f"CONTENT: {doc['content']}"

        messages.append({"role":"system", "content":system_prompt})

        # ASSISTANT - Session history
        if (not self.agent_config.new_session):
            session_results = self.agent_memory.get_session_history(self.agent_config.session_token, role["name"])
            for session in session_results:
                messages.append({"role":"user", "content":session["input"]}) if isinstance(session["input"], str) else messages.append(session["input"]["input"])
                messages.append({"role":"system", "content":session["answer"]}) if isinstance(session["answer"], str) else messages.append(session["answer"])

        # consuct the latest input as the last message
        user_prompt = {
            "role":"user",
            "content": input
        }
        messages.append(user_prompt) if isinstance(input, str) else messages.append(input['input'])

        # TODO: tools are being renamed to be functions as this matches the OPenAI definition for structured outputs more closely
        tools  = self.function_manager.get_function_schemas(role["tools"]) if "tools" in role and len(role["tools"]) > 0 else []

        # allow LLM model overrides on a per role basis
        if "options" in role and "model_override" in role["options"]:
            options["model_override"] = role["options"]["model_override"]

        schema = None
        if "schema" in role and role["schema"] is not None and role["schema"] != "":
            try:
                schema_obj = json.loads(role["schema"])
                schema_model = create_dynamic_model(schema_obj).schema()
                #schema_model["name"]=role["name"]
                schema = {"type":"json_schema", "json_schema":{"schema":schema_model, "name":role["name"], "strict":True}}
            except:
                logging.error('run_agent - schema validation failed: %s',role['schema'])

        return {"messages":messages, "tools":tools, "options":options, "output_format_json":output_format_json, "role":role["name"], "schema":schema}
