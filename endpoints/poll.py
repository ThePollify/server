from json import loads

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_, select

import database
from endpoints import dependencies
from models import poll as models
from utils import page

router = APIRouter(prefix="/poll", tags=["Poll"])


@router.post("/add")
async def add(
    user: dependencies.User,
    poll_schema: models.PollSchema,
) -> models.Poll:
    async with database.sessions.begin() as session:
        poll = database.Poll(
            owner_id=user.id,
            name=poll_schema.name,
            poll=poll_schema.serializable_dict(),
        )

        session.add(poll)
        await session.flush()
        await session.refresh(poll)

        return models.Poll.from_orm(poll)


@router.get("/get/id")
async def get_by_id(user: dependencies.User, id: int) -> models.Poll | None:
    async with database.sessions.begin() as session:
        poll = await session.scalar(
            select(database.Poll).where(
                and_(
                    database.Poll.owner_id == user.id,
                    database.Poll.id == id,
                )
            )
        )

        if poll is None:
            return None

        return models.Poll.from_orm(poll)


@router.get("/get/name")
async def get_by_name(
    user: dependencies.User,
    name: str | None = None,
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
) -> page.Page[models.Poll]:
    async with database.sessions.begin() as session:
        return await page.paginate(
            session,
            database.Poll,
            and_(
                database.Poll.owner_id == user.id,
                database.Poll.name.contains(name, autoescape=True),
            )
            if name is not None
            else database.Poll.owner_id == user.id,
            limit,
            offset,
            models.Poll,
        )


@router.put("/update")
async def update(
    user: dependencies.User,
    id: int,
    poll_schema: models.PollSchema,
) -> models.Poll:
    async with database.sessions.begin() as session:
        poll = await session.scalar(select(database.Poll).where(database.Poll.id == id))

        if poll is None:
            raise HTTPException(404, f"Poll with id {id} does not exist")
        if poll.owner_id != user.id:
            raise HTTPException(405, "You are not the owner of this poll")

        poll.name = poll_schema.name
        poll.poll = poll_schema.serializable_dict()
        await session.flush()

        return models.Poll.from_orm(poll)


@router.delete("/delete")
async def delete(user: dependencies.User, id: int) -> models.Poll:
    async with database.sessions.begin() as session:
        poll = await session.scalar(select(database.Poll).where(database.Poll.id == id))

        if poll is None:
            raise HTTPException(404, f"Poll with id {id} does not exist")
        if poll.owner_id != user.id:
            raise HTTPException(405, "You are not the owner of this poll")

        await session.delete(poll)
        return models.Poll.from_orm(poll)
