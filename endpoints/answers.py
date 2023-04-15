from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import and_, delete, or_, select

import database
from endpoints import dependencies
from models import answers as models

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.post("/add/value")
async def add_value(
    user: dependencies.OptionalUser,
    poll_id: int,
    value: models.Value,
) -> models.Answer:
    async with database.sessions.begin() as session:
        if (
            user is not None
            and (
                answer := await session.scalar(
                    select(database.Answer).where(
                        and_(
                            database.Answer.poll_id == poll_id,
                            database.Answer.answerer_id == user.id,
                        )
                    )
                )
            )
            is not None
        ):
            answer_schema = models.AnswerSchema.parse_obj(answer.answer)
        else:
            answer_schema = models.AnswerSchema(values=[])
            answer = database.Answer(
                poll_id=poll_id,
                answerer_id=user.id if user is not None else None,
                answer=answer_schema.serializable(),
            )
            session.add(answer)

        answer_schema.values.append(value)

        try:
            models.AnswerSchema.validate(answer_schema)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)

        answer.answer = answer_schema.serializable()
        await session.flush()
        await session.refresh(answer)

        try:
            return models.Answer.from_orm(answer)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)


@router.post("/add/answer")
async def add_answer(
    user: dependencies.OptionalUser,
    poll_id: int,
    answer_schema: models.AnswerSchema,
) -> models.Answer:
    async with database.sessions.begin() as session:
        answer = database.Answer(
            poll_id=poll_id,
            answerer_id=user.id if user is not None else None,
            answer=answer_schema.serializable(),
        )

        session.add(answer)
        await session.flush()
        await session.refresh(answer)

        return models.Answer.from_orm(answer)


@router.get("/get/id")
async def get_by_id(user: dependencies.OptionalUser, id: int) -> models.Answer | None:
    async with database.sessions.begin() as session:
        answer = await session.scalar(
            select(database.Answer).where(
                and_(
                    database.Answer.id == id,
                    (
                        or_(
                            database.Answer.answerer_id == user.id,
                            database.Answer.answerer_id.is_(None),
                        )
                        if user is not None
                        else database.Answer.answerer_id.is_(None)
                    ),
                )
            )
        )

        if answer is None:
            return None

        return models.Answer.from_orm(answer)


@router.get("/get/my")
async def get_by_poll_id(user: dependencies.User, poll_id: int) -> models.Answer | None:
    async with database.sessions.begin() as session:
        answer = await session.scalar(
            select(database.Answer).where(
                and_(
                    database.Answer.poll_id == poll_id,
                    or_(
                        database.Answer.answerer_id == user.id,
                        database.Answer.answerer_id.is_(None),
                    ),
                )
            )
        )

        if answer is None:
            return None

        return models.Answer.from_orm(answer)


@router.get("/get/values")
async def get_values(
    user: dependencies.User,
    poll_id: int,
) -> list[models.Value]:
    async with database.sessions.begin() as session:
        values = []
        for answer in map(
            models.Answer.from_orm,
            await session.scalars(
                select(database.Answer)
                .where(
                    and_(
                        database.Poll.owner_id == user.id,
                        database.Answer.poll_id == poll_id,
                    )
                )
                .join(database.Answer.poll)
            ),
        ):
            values.extend(answer.answer.values)
        return values


@router.delete("/delete")
async def delete_answers(user: dependencies.User, poll_id: int) -> None:
    async with database.sessions.begin() as session:
        await session.execute(
            delete(database.Answer).where(
                and_(
                    database.Answer.poll_id == poll_id,
                    database.Answer.poll.has(database.Poll.owner_id == user.id),
                )
            )
        )


# @router.websocket("/listen/question")
# async def listen_question() -> None:
#     pass


# @router.websocket("/listen/values")
# async def listen_values() -> None:
#     pass
