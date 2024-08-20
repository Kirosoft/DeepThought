from pydantic import BaseModel, create_model, EmailStr
from typing import Any, Dict, List, Union
from enum import Enum, auto

def create_enum_from_list(name, strings):
    return Enum(name, {string.upper(): string for string in strings})

def infer_pydantic_type(value: Any) -> Any:
    if isinstance(value, int):
        return int
    elif isinstance(value, float):
        return float
    elif isinstance(value, str):
        # Example: Email validation based on a field name heuristic
        if "@" in value:
            return EmailStr
        return str
    elif isinstance(value, bool):
        return bool
    elif isinstance(value, list):
        if value:
            if (isinstance(value[0], str) and value[0].startswith("@")):
                enum_name = value[0][1:]
                return create_enum_from_list(enum_name, value[1:])
            else:
                return List[infer_pydantic_type(value[0])]

        return List[Any]
    elif isinstance(value, dict):
        return create_dynamic_model(value)
    else:
        return Any

def create_dynamic_model(json_data: Dict[str, Any]) -> BaseModel:
    fields = {key: (infer_pydantic_type(value), ...) for key, value in json_data.items()}
    return create_model('DynamicModel', **fields)
