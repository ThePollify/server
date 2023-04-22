import hashlib
import os
import secrets
from typing import Annotated

import jwt
from aiofiles import open
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select

import database
from endpoints import dependencies
from models import account as models
from settings import settings

router = APIRouter(prefix="/account", tags=["Account"])


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


@router.get("/get/image")
async def get_image(user_id: int) -> FileResponse:
    path = f"./files/{user_id}-avatar.png"
    if not os.path.exists(path):
        return FileResponse("./static/no-avatar.png", filename="avatar.png")
    return FileResponse(path, filename="avatar.png")


@router.put("/update/username")
async def update_username(
    user: dependencies.User,
    update: models.UpdateUsername,
) -> models.User:
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
    async with database.sessions.begin() as session:
        session.add(user)

        user.salt = secrets.token_hex(8)
        user.password = hash_password(update.password.strip(), user.salt)
        return token_model(user)


@router.put("/update/image")
async def update_image(
    user: dependencies.User,
    file: Annotated[UploadFile, File()],
) -> None:
    if file.size is None or file.size > 524288:
        raise HTTPException(400, "The file is to large. Max size 512KiB")
    if file.filename is None or not file.filename.endswith(".png"):
        raise HTTPException(400, "Unsupported file type. Only png files are allowed.")

    async with open(f"./files/{user.id}-avatar.png", "wb") as sys_file:
        await sys_file.write(await file.read())


@router.delete("/delete")
async def delete(user: dependencies.User) -> models.User:
    async with database.sessions.begin() as session:
        await session.delete(user)
        return models.User.from_orm(user)
