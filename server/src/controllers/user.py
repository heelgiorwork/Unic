from datetime import datetime
from typing import List

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from src.core.entities.user import UserEntity
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


class CreateUserRequest(BaseModel):
    username: str
    password: str
    full_name: str


class UpdateUserRequest(BaseModel):
    full_name: str | None = None
    username: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(e: UserEntity) -> "UserResponse":
        return UserResponse(
            id=e.id,
            username=e.user_name,
            full_name=e.full_name,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )


@router.post("/", response_model=UserResponse)
@inject
async def create_user(
    request: CreateUserRequest,
    service: FromDishka[UserService],
) -> UserResponse:
    try:
        entity = await service.create_user(
            username=request.username,
            password_hash=request.password,
            full_name=request.full_name,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    return UserResponse.from_entity(entity)


@router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user_by_id(
    user_id: int,
    service: FromDishka[UserService],
) -> UserResponse:
    entity = await service.get_user_by_id(user_id)
    if not entity:
        raise HTTPException(404, "User not found")
    return UserResponse.from_entity(entity)


@router.get("/", response_model=List[UserResponse])
@inject
async def get_all_users(
    service: FromDishka[UserService],
    limit: int = 100,
    offset: int = 0,
) -> List[UserResponse]:
    users = await service.get_all_users(limit=limit, offset=offset)
    return [UserResponse.from_entity(u) for u in users]


@router.get("/search/", response_model=List[UserResponse])
@inject
async def search_users(
    name: str,
    service: FromDishka[UserService],
) -> List[UserResponse]:
    try:
        users = await service.search_users_by_name(name)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return [UserResponse.from_entity(u) for u in users]


@router.put("/{user_id}", response_model=UserResponse)
@inject
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    service: FromDishka[UserService],
) -> UserResponse:
    try:
        entity = await service.update_user(
            user_id=user_id,
            full_name=request.full_name,
            username=request.username,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return UserResponse.from_entity(entity)


@router.delete("/{user_id}")
@inject
async def delete_user(
    user_id: int,
    service: FromDishka[UserService],
) -> dict:
    try:
        await service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

    return {"status": "deleted"}


@router.post("/batch", response_model=List[UserResponse])
@inject
async def create_multiple(
    users: List[CreateUserRequest],
    service: FromDishka[UserService],
) -> List[UserResponse]:
    try:
        entities = await service.create_multiple_users(
            [
                {
                    "username": u.username,
                    "password_hash": u.password,
                    "full_name": u.full_name,
                }
                for u in users
            ]
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return [UserResponse.from_entity(e) for e in entities]


@router.delete("/batch")
@inject
async def delete_multiple(
    service: FromDishka[UserService],
    ids: List[int] = Body(...),
) -> dict:
    count = await service.delete_multiple_users(ids)
    return {"deleted": count}
