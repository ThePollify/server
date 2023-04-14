import pydantic.generics
import json


class BaseModel(pydantic.generics.GenericModel):
    class Config:
        orm_mode = True

    def serializable(self) -> dict:
        return json.loads(self.json())


from .settings import settings

from . import account
from . import poll
from . import statistics
