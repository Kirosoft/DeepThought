# DeepThought

Functional agentic framework

# Features

* Context search by template specification. e.g. {% for doc in docs -%}

```
{% for doc in docs -%}
---
NAME: {{ doc.filename }}
PASSAGE:
{{ doc.page_content }}
---

{% endfor -%}
----
```

* Session history (aka Chat or Agent mode) by template specification e.g. {% for qa in history -%}

```
{% for qa in history -%}
{{qa.question}}
{{qa.answer}}
{% endfor -%}

{{ question }}

```

* Functional calling by template specification. Use [[tool1, tool2 ... tooln]] to specifiy available tools from the tool database

```
[[get_n_day_weather_forecast,get_current_weather]]
Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.

{% for qa in history -%}
{{qa.question}}
{{qa.answer}}
{% endfor -%}

{{ question }}
```

## Example request

First request (no session token):-

```
{
    "input": "{\"SystemProperties\":{},\"question\":\"plymouth in celcius\", \"role\":\"weather_forecast\", \"session_token\":\"\"}"
}
```

subsequent, request top continue the conversation - with the session token:

```
{
    "input": "{\"SystemProperties\":{},\"question\":\"follow up question\", \"role\":\"weather_forecast\", \"session_token\":\HqvYXY4B97jYMDJrrnqz"\"}"
}
```


## Update roles database

```
python roles/update_roles.py "<path-to-roles-directory>"
```

## Update tools database

```
python tools/update_tools.py "<path-to-tools-directory>"
```

