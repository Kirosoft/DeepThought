{
    "type": "function",
    "function": {
        "name": "website_search",
        "description": "A tool that can be used to search the internet",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Mandatory search query you want to use to search a specific website"
                },
                "website": {
                    "type": "string",
                    "description": "Mandatory valid website URL you want to search on"
                },
            "required": [
                "search_query",
                "website"
            ]
        }
    }
}