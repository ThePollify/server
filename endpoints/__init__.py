from fastapi import APIRouter

from . import dependencies

from . import account
from . import poll
from . import answers

router = APIRouter()
router.include_router(account.router)
router.include_router(poll.router)
router.include_router(answers.router)
