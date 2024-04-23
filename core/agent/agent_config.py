import json
import os
import random, string
import logging

# Helper class to gather all properties and settings expected when procesing
# a payload from the EventHub
class AgentConfig:
    def __init__(self, input_body:str = None):
        self.SESSION_ID_CHARS = 16

        # sanitise the input
        if input_body is None:
            self.body = '{}'
        else:
            try:
                self.body = json.loads(input_body)
                self.__setup_vars()
            except Exception as err:
                # invalid json supplied
                logging.error(f'invalid json payload {input_body} {err}')
                self.body = {}

        self.__init_env_vars()

    def __init_env_vars(self):
        # AI config
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
        self.OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

        self.LLM_TYPE = os.getenv("LLM_TYPE")
        self.EMEBDDING_TYPE = os.getenv("EMBEDDING_TYPE")

        self.MAX_SESSION_TOKENS = int(os.getenv("MAX_SESSION_TOKENS", "4096"))

        # database tables
        self.INDEX_ROLES = os.getenv("INDEX_ROLES", "ai_roles")
        self.INDEX_HISTORY = os.getenv("INDEX_HISTORY", "ai_history")
        self.INDEX_TOOLS = os.getenv("INDEX_TOOLS", "ai_tools")
        self.INDEX_CONTEXT = os.getenv("INDEX_CONTEXT", "ai_context")
        self.INDEX_SPECS = os.getenv("INDEX_SPECS", "ai_specs")

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

        # github creds
        self.GITHUB_USER = os.getenv("GITHUB_USER")
        self.GITHUB_KEY = os.getenv("GITHUB_KEY")
        
        # LLAMA3
        self.OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
        self.OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL")

        # GROK
        self.GROK_ENDPOINT = os.getenv("GROK_ENDPOINT")
        self.GROK_MODEL = os.getenv("GROK_MODEL")
        self.GROK_API_KEY = os.getenv("GROK_API_KEY")

        # SERPER
        self.SERPER_API_KEY = os.getenv("SERPER_API_KEY")


    # Setup the needed properties
    # If they were not supplied then provide suitable defaults
    def __setup_vars(self):
    
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
        self.input = self.body.get('input', '')
        return self.input

    def is_valid(self):
        input = self.__get_input() 
        return True if input is not None and input != '' else False
    