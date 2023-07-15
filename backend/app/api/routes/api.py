from fastapi import APIRouter

from . import translation
# import writing

router = APIRouter()
router.include_router(translation.router, tags=["translation"], prefix="/translator")
# router.include_router(writing.router, tags=["writing"], prefix="/writer")

