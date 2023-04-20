from math import ceil
from typing import Generic, TypeVar

from fastapi import HTTPException
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base
from models import BaseModel

Model = TypeVar("Model", bound=BaseModel)
Table = TypeVar("Table", bound=Base)


class Page(BaseModel, Generic[Model]):
    total: int
    items: list[Model] = []


async def paginate(
    session: AsyncSession,
    table: type[Table],
    expression: ColumnElement[bool],
    limit: int,
    offset: int,
    model: type[Model],
) -> Page[Model]:
    total = (
        ceil(
            (
                await session.scalars(
                    select(func.count()).select_from(table).where(expression)
                )
            ).one()
            / limit
        )
        - 1
    )

    if total < 0:
        total = 0

    if offset > total:
        raise HTTPException(400, f"Offset can't be more than {total}")

    return Page(
        total=total,
        items=[
            model.from_orm(item)
            for item in await session.scalars(
                select(table).where(expression).limit(limit).offset(offset * limit)
            )
        ],
    )
