from asyncio import Queue
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import and_, delete, or_, select
from websockets.exceptions import ConnectionClosed

import database
import models as m
from endpoints import dependencies
from models import answers as models

router = APIRouter(prefix="/answers", tags=["Answers"])
values_pull: dict[int, set[Queue[models.Value]]] = {}
questions_pull: dict[int, set[Queue[m.poll.Question]]] = {}


def put_values(poll_id: int, values: list[models.Value]) -> None:
    if poll_id not in values_pull:
        return
    for queue in (q for q in values_pull[poll_id]):
        for value in values:
            queue.put_nowait(value)


def put_questions(poll_id: int, question: m.poll.Question) -> None:
    if poll_id not in questions_pull:
        return
    for queue in (q for q in questions_pull[poll_id]):
        queue.put_nowait(question)


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
            answer_model = models.Answer.from_orm(answer)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)

        put_values(poll_id, answer_model.answer.values)
        return answer_model


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

        try:
            answer_model = models.Answer.from_orm(answer)
        except ValidationError as e:
            raise RequestValidationError(e.raw_errors)

        put_values(poll_id, answer_model.answer.values)
        return answer_model


@router.post("/send/question")
async def send_questions(
    user: dependencies.User,
    poll_id: int,
    question_id: UUID,
) -> None:
    async with database.sessions.begin() as session:
        poll = await session.scalar(
            select(database.Poll).where(
                and_(
                    database.Poll.id == poll_id,
                    database.Poll.owner_id == user.id,
                )
            )
        )

        if poll is None:
            raise HTTPException(400, "Poll not found")

        uuids = m.poll.Poll.from_orm(poll).poll.uuids
        if question_id not in uuids:
            raise HTTPException(400, "Question not found")

        put_questions(poll_id, uuids[question_id])


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


@router.websocket("/listen/values")
async def listen_values(websocket: WebSocket, poll_id: int) -> None:
    await websocket.accept()
    if poll_id not in values_pull:
        values_pull[poll_id] = set()

    queue: Queue[models.Value] = Queue()
    values_pull[poll_id].add(queue)

    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message.json())
    except ConnectionClosed:
        values_pull[poll_id].remove(queue)
        if len(values_pull[poll_id]) == 0:
            values_pull.pop(poll_id)
        await websocket.close()


@router.websocket("/listen/questions")
async def listen_questions(websocket: WebSocket, poll_id: int) -> None:
    await websocket.accept()
    if poll_id not in questions_pull:
        questions_pull[poll_id] = set()

    queue: Queue[m.poll.Question] = Queue()
    questions_pull[poll_id].add(queue)

    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message.json())
    except ConnectionClosed:
        questions_pull[poll_id].remove(queue)
        if len(questions_pull[poll_id]) == 0:
            questions_pull.pop(poll_id)
        await websocket.close()
