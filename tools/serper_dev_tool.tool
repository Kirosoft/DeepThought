{
    "type": "function",
    "function": {
        "name": "serper_dev_tool",
        "description": "A tool that can be used to search the internet",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Mandatory search query you want to use to search the internet"
                }
            "required": [
                "search_query"
            ]
        }
    }
}