from fastapi import APIRouter

from . import dependencies

from . import account
from . import poll
from . import statistics

router = APIRouter()
router.include_router(account.router)
router.include_router(poll.router)
router.include_router(statistics.router)
