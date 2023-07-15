from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl
    
class TranslationInRequest(BaseModel):
    src: str
    
class TranslationForResponse(BaseModel):
    result: str
