from pydantic import BaseModel, Field, create_model, EmailStr
from typing import Any, Dict, List, Union, Literal
from enum import Enum, auto

def create_enum_from_list(name, data_list):

    return Enum(name, {item.upper() if isinstance(item, str) else f'const{idx}': item for idx, item in enumerate(data_list)})

def infer_pydantic_type(value: Any) -> Any:
    if isinstance(value, bool):
        return bool
    elif isinstance(value, int):
        return int
    elif isinstance(value, float):
        return float
    elif isinstance(value, str):
        # Example: Email validation based on a field name heuristic
        if "@" in value:
            return EmailStr
        return str
    elif isinstance(value, list):
        if value:
            if (isinstance(value[0], str) and value[0].startswith("@")):
                enum_name = value[0][1:]
                return create_enum_from_list(enum_name, value[1:])
            else:
                # TODO: we only support str or int type lists
                return List[str] if isinstance(value[0], str) else List[int]

        return List[Any]
    elif isinstance(value, dict):
        inner_model =  create_dynamic_model('sub_object', value)
        return inner_model
    else:
        return Any

def create_dynamic_model(name, json_data: Dict[str, Any]) -> BaseModel:
    fields = {key: (infer_pydantic_type(value),...) for key, value in json_data.items()}
    return create_model(name, **fields)
