
from pydantic import BaseModel, Field
from enum import Enum, IntEnum
from typing import List, Optional
import json
from typing import Set, Union

class DeserializableBaseModel(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class DocumentableIntEnum(IntEnum):
    @classmethod
    def __modify_schema__(cls, schema):
        schema["description"] += str([f"{choice.name} = {choice.value}" for choice in cls])
        # schema["enum"] = [f"{choice.name} = {choice.value}" for choice in cls]

        return schema
