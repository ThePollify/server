from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select

import database
from settings import settings


async def user(token: Annotated[str, Header(alias="x-token")]) -> database.User:
    try:
        data = jwt.decode(token, options={"verify_signature": False})
    except jwt.exceptions.DecodeError:
        raise HTTPException(401, "Token is invalid")

    if "sub" not in data and not isinstance(data["sub"], int):
        raise HTTPException(401, "Token is invalid")

    async with database.sessions.begin() as session:
        user = await session.scalar(
            select(database.User).where(database.User.id == data["sub"])
        )

        if user is None:
            raise HTTPException(401, "Token is invalid")

        try:
            jwt.decode(token, settings.secret + user.password, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPException(401, "Token is invalid")

        session.expunge(user)
        return user


async def optional_user(
    token: str | None = Header(None, alias="x-token"),
) -> database.User | None:
    return await user(token) if token is not None else token


User = Annotated[database.User, Depends(user, use_cache=False)]
OptionalUser = Annotated[database.User | None, Depends(optional_user, use_cache=False)]
