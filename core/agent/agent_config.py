import json
import os
import random, string
import logging

# Helper class to gather all properties and settings expected when procesing
# a payload from the EventHub
class AgentConfig:
    def __init__(self, input_body:str = None, user_settings_keys = None):
        self.SESSION_ID_CHARS = 16

        # sanitise the input
        if input_body is None:
            self.body = '{}'
        else:
            self.update_from_body(input_body)

        if user_settings_keys is not None:
            self.update_from_user_settings(user_settings_keys)

        self.__init_env_vars()

    def update_from_body(self, input_body):
        try:
            self.body = json.loads(input_body)
            self.__setup_vars_from_payload()
        except Exception as err:
            # invalid json supplied
            logging.error(f'invalid json payload {input_body} {err}')
            self.body = {}
            
    def update_from_user_settings(self, user_settings_keys):

        self.OPENAI_API_KEY = user_settings_keys["OPENAI_API_KEY"]
        # AI config
        self.OPENAI_MODEL = user_settings_keys["OPENAI_MODEL"]
        self.OPENAI_EMBEDDING_MODEL = user_settings_keys["OPENAI_EMBEDDING_MODEL"]

        self.LLM_TYPE = user_settings_keys["LLM_TYPE"]
        self.EMEBDDING_TYPE = user_settings_keys["EMBEDDING_TYPE"]

        # github creds
        self.GITHUB_USER = user_settings_keys["GITHUB_USER"]
        self.GITHUB_KEY = user_settings_keys["GITHUB_KEY"]
        
        # LLAMA3
        self.OLLAMA_ENDPOINT = user_settings_keys["OLLAMA_ENDPOINT"]
        self.OLLAMA_MODEL = user_settings_keys["OLLAMA_MODEL"]
        self.OLLAMA_EMBEDDING_MODEL = user_settings_keys["OLLAMA_EMBEDDING_MODEL"]

        # GROK
        self.GROK_ENDPOINT = user_settings_keys["GROK_ENDPOINT"]
        self.GROK_MODEL = user_settings_keys["GROK_MODEL"]
        self.GROK_API_KEY = user_settings_keys["GROK_API_KEY"]

        # SERPER
        self.SERPER_API_KEY = user_settings_keys["SERPER_API_KEY"]

        # anthropic
        # self.ANTHROPIC_API_KEY = user_settings_keys["ANTHROPIC_API_KEY"]
        # self.ANTHROPIC_MODEL = user_settings_keys["ANTHROPIC_MODEL"]
        

    def __init_env_vars(self):

        self.MAX_SESSION_TOKENS = int(os.getenv("MAX_SESSION_TOKENS", "4096"))

        # database tables
        self.INDEX_ROLES = os.getenv("INDEX_ROLES", "ai_roles")
        self.INDEX_HISTORY = os.getenv("INDEX_HISTORY", "ai_history")
        self.INDEX_TOOLS = os.getenv("INDEX_TOOLS", "ai_tools")
        self.INDEX_VECTOR = os.getenv("INDEX_VECTOR", "ai_vector")
        self.INDEX_TEXT = os.getenv("INDEX_TEXT", "ai_text")
        self.INDEX_SPECS = os.getenv("INDEX_SPECS", "ai_specs")
        self.INDEX_USER = os.getenv("INDEX_USER", "ai_user")
        self.INDEX_FLOWS = os.getenv("INDEX_FLOWS", "ai_flows")
        self.INDEX_CONTEXT = os.getenv("INDEX_CONTEXT", "ai_context")
        self.INDEX_CONTEXT_DEFINITION = os.getenv("INDEX_CONTEXT_DEFINITION", "ai_context")

        self.DB_ROLES = os.getenv("DB_ROLES", "ai_roles")
        self.DB_HISTORY = os.getenv("DB_HISTORY", "ai_history")
        self.DB_TOOLS = os.getenv("DB_TOOLS", "ai_tools")
        self.DB_CONTEXT = os.getenv("DB_CONTEXT", "ai_context")
        self.DB_SPECS = os.getenv("DB_SPECS", "ai_specs")
        self.DB_USER = os.getenv("DB_USER", "ai_user")

        self.DEFAULT_TENANT = os.getenv("DEFAULT_TENANT", "default")
        self.SYSTEM_TENANT = os.getenv("SYSTEM_TENANT", "system")

        self.DATABASE_NAME = os.getenv("DATABASE_NAME","")
        self.TOP_K_DOCS = int(os.getenv("TOP_K_DOCS", "10"))
        self.DB_TYPE = os.getenv("DB_TYPE")

        # elastic specific settings
        self.ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID","")
        self.ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY","")

        # cosmos specific settings
        self.COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT","https://localhost:8081")
        self.COSMOS_KEY = os.getenv("COSMOS_KEY","C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")

        # queue storage
        self.QUEUE_STORAGE_CONNECTION_STRING = os.getenv("QUEUE_STORAGE_CONNECTION_STRING"),

        self.AzureDBSetupFunctions = os.getenv("AzureDBSetupFunctions", "false")

        self.TOKEN_EXPIRY_MINUTES = os.getenv("TOKEN_EXPIRY_MINUTES",30)

    # Setup the needed properties
    # If they were not supplied then provide suitable defaults
    def __setup_vars_from_payload(self):
    
        # persona to use when evaluating the message or use the default
        self.role=self.body.get("role", "default_role")                      
        
        # use the supplied session token or generate a new one
        self.session_token=self.body.get("session_token","")  
        if (len(self.session_token) < self.SESSION_ID_CHARS):
            self.new_session = True
            self.session_token = ''.join(random.choices(string.ascii_letters + string.digits, k=self.SESSION_ID_CHARS))
        else:
            self.new_session = False
            
        self.parent_role=self.body.get("parent_role","")  

    def __get_input(self):
        # TODO: security check the input text
        self.input = self.body.get('input', '')

        # when used in a flow, the payload can have named inputs/value pairs from input connections
        self.inputs = self.body.get('inputs',{})
        
        return self.input

    def is_valid(self):
        input = self.__get_input() 
        return True if input is not None and input != '' else False
    