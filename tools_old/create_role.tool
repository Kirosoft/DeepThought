{
    "type": "function",
    "function": {
        "name": "create_role",
        "description": "Create a new agent role",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "short description of the agent role"
                },
                "role": {
                    "type": "string",
                    "description": "short description of the agent role"
                },
                "input": {
                    "type": "string",
                    "description": "what input are you expecting for this role"
                },
                "output": {
                    "type": "string",
                    "description": "what will the output look like"
                },
                "input": {
                    "type": "string",
                    "description": "The temperature unit to use. Infer this from the users location."
                },
                "tools": {
                    "type": "string",
                    "description": "Describe the tools that this agent will need to use"
                },
                "options": {
                    "type": "object",
                    "description": "option settings and overrides",
                    "properties": {
                        "model_override": {
                            "type":"string",
                            "description":"specifiy the llm and model if the default should be overriden e.g. ollama and llama3"
                        },
                        "rag_mode": {
                            "type":"string",
                            "description":"specifiy if the prompt should include data from database"
                        }
                    }
                }
            },
            "required": [
                "location",
                "format"
            ]
        }
    }
}