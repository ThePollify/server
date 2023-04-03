import pydantic


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True


from .settings import settings

from . import account
from . import poll
from . import statistics
