import json
import os
import random, string
import logging

# Helper class to gather all properties and settings expected when procesing
# a payload from the EventHub
class AgentConfig:
    def __init__(self, input_body:bytes):
        # sanitise the input
        if input_body is None:
            self.body = '{}'
        else:
            body_str = input_body.decode('utf-8')
            try:
                self.body = json.loads(body_str)
            except:
                # invalid json supplied
                logging.error(f'invalid json payload {body_str}')

                self.body = {}

        self.SESSION_ID_CHARS = 16
        self.__init_env_vars()
        self.__setup_vars()

    def __init_env_vars(self):
        # AI config
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
        self.MAX_SESSION_TOKENS = int(os.getenv("MAX_SESSION_TOKENS", "4096"))

        # Elastic search config
        self.ES_NUM_DOCS = int(os.getenv("ES_NUM_DOCS", "10"))
        self.INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
        self.ES_INDEX_ROLES = os.getenv("ES_INDEX_ROLES", "ai_roles")
        self.ES_INDEX_HISTORY = os.getenv("ES_INDEX_HISTORY", "ai_history")
        self.ES_INDEX_TOOLS = os.getenv("ES_INDEX_TOOLS", "ai_tools")

        self.ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
        self.ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

    # Setup the needed properties
    # If they were not supplied then provide suitable defaults
    def __setup_vars(self):
    
        # persona to use when evaluating the message or use the default
        self.role=self.body.get("role", "default_role")                      
        
        # use the supplied session token or generate a new one
        self.session_token=self.body.get("session_token","")  
        if (len(self.session_token) < self.SESSION_ID_CHARS):
            self.session_token = ''.join(random.choices(string.ascii_letters + string.digits, k=self.SESSION_ID_CHARS))

    def __get_question(self):
        self.question = self.body.get('question', '')
        return self.question

    def is_valid(self):
        question = self.__get_question() 
        return True if question is not None and question != '' else False
    