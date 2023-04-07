import hashlib
import secrets

import jwt
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

import database
from endpoints import dependencies
from models import account as models
from models import settings

router = APIRouter(prefix="/account", tags=["accounts", "users"])


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha512((password + salt).encode("UTF-8")).hexdigest()


def token_model(user: database.User) -> models.Token:
    return models.Token(
        id=user.id,
        username=user.username,
        token=jwt.encode(
            {"sub": user.id},
            settings.secret + user.password,
            "HS256",
        ),
    )


@router.post("/register")
async def register(auth: models.Auth) -> models.Token:
    if len(auth.username.strip()) == 0:
        raise HTTPException(400, "Username must not be empty")
    if len(auth.password.strip()) == 0:
        raise HTTPException(400, "Password must not be empty")

    salt = secrets.token_hex(8)
    async with database.sessions.begin() as session:
        if (
            await session.scalar(
                select(database.User).where(database.User.username == auth.username)
            )
            is not None
        ):
            raise HTTPException(400, "User with this username already exists")

        user = database.User(
            username=auth.username,
            password=hash_password(auth.password, salt),
            salt=salt,
        )
        session.add(user)
        await session.flush()

        return token_model(user)


@router.post("/login")
async def login(auth: models.Auth) -> models.Token:
    async with database.sessions.begin() as session:
        user = await session.scalar(
            select(database.User).where(database.User.username == auth.username)
        )

        if user is None or user.password != hash_password(auth.password, user.salt):
            raise HTTPException(403, "Username or password is invalid")

        return token_model(user)


@router.get("/me")
async def me(user: dependencies.User) -> models.User:
    return models.User.from_orm(user)


@router.get("/get/id")
async def get_by_id(id: int) -> models.User | None:
    async with database.sessions.begin() as session:
        user = await session.scalar(select(database.User).where(database.User.id == id))

        if user is None:
            return None

        return models.User.from_orm(user)


@router.get("/get/username")
async def get_by_username(username: str) -> models.User | None:
    async with database.sessions.begin() as session:
        user = await session.scalar(
            select(database.User).where(database.User.username == username)
        )

        if user is None:
            return None

        return models.User.from_orm(user)


@router.put("/update/username")
async def update_username(
    user: dependencies.User,
    update: models.UpdateUsername,
) -> models.User:
    if len(update.username.strip()) == 0:
        raise HTTPException(400, "Username must not be empty")
    async with database.sessions.begin() as session:
        session.add(user)

        if (
            await session.scalar(
                select(database.User).where(
                    database.User.username == update.username.strip()
                )
            )
            is not None
        ):
            raise HTTPException(400, "User with this username already exists")

        user.username = update.username.strip()
        return models.User.from_orm(user)


@router.put("/update/password")
async def update_password(
    user: dependencies.User,
    update: models.UpdatePassword,
) -> models.Token:
    if len(update.password.strip()) == 0:
        raise HTTPException(400, "Password must not be empty")
    async with database.sessions.begin() as session:
        session.add(user)

        user.salt = secrets.token_hex(8)
        user.password = hash_password(update.password.strip(), user.salt)
        return token_model(user)


@router.delete("/delete")
async def delete(user: dependencies.User) -> models.User:
    async with database.sessions.begin() as session:
        await session.delete(user)
        return models.User.from_orm(user)
