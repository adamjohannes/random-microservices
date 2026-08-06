from fastapi import APIRouter, Depends, status

from src.course.adapters.driving.http.auth import get_current_user_id
from src.course.adapters.driving.http.dependencies import get_user_usecase
from src.course.adapters.driving.http.schemas import SyncUserRequest, UserResponse
from src.course.application.use_cases.user_usecase import UserUseCase

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def sync_user(
    body: SyncUserRequest,
    _actor_id: str = Depends(get_current_user_id),
    usecase: UserUseCase = Depends(get_user_usecase),
) -> UserResponse:
    user = await usecase.sync_user(
        account_id=body.account_id,
        name=body.name,
        email=body.email,
    )
    return UserResponse(
        id=user.id,
        name=str(user.name),
        email=str(user.email),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
