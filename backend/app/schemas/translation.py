from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl
from .base import DocumentableIntEnum

# { "success": true, "timeOut": true, "errorDesc": "test_b86a30ced21c", "errorCode": "sentsitive", "tokenCount": 123, "calcCount": 3, "costTime":20, "dataList": { "douyin": "抖音文案","weibo": "微博文案","wechat": "微信文案","xiaohongshu": "小红书文案" } }


class EnumTranslateDriection(DocumentableIntEnum):
    cn2en: 1
    en2cn: 2

class TranslateMultiResult(BaseModel):
    douyin: str
    weibo: str
    wechat: str
    xiaohongshu: str
    
class TranslationInRequest(BaseModel):
    sourceText: str
    apiKey: Optional[str]
    taskType: EnumTranslateDriection
    modelType: str  
    
class TranslationForResponse(BaseModel):
    success: bool
    timeOut: bool
    errorDesc: Optional[str]
    errorCode: Optional[str]
    tokenCount: int
    calcCount: int
    costTime: float
    dataList: TranslateMultiResult
