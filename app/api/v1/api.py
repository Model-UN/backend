from fastapi import APIRouter

from app.api.v1.endpoints import (
    users,
    health,
    conferences,
    forms
)

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=['Users'])
router.include_router(health.router, prefix="/health", tags=['Health'])
router.include_router(conferences.router, prefix="/conferences", tags=['Conferences'])
router.include_router(forms.router, prefix="/forms", tags=['Forms'])
