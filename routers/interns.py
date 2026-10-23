from fastapi import APIRouter

from schemas import InternCreate, ActivityEntry, StatusUpdate
from services import interns_service

router = APIRouter(prefix="/interns", tags=["Interns"])

"""Contains the endpoints, and awaits for the functions from the 
services folder. Where the actual functions are defined."""

@router.post("/AddIntern")
async def add_intern(payload: InternCreate):
    return await interns_service.add_intern(payload)


@router.post("/{intern_id}/activity")
async def add_daily_activity(intern_id: str, payload: ActivityEntry):
    return await interns_service.add_daily_activity(intern_id, payload)


@router.patch("/{intern_id}/status")
async def update_intern_status(intern_id: str, payload: StatusUpdate):
    return await interns_service.update_intern_status(intern_id, payload)


@router.get("/{intern_id}")
async def view_intern_summary(intern_id: str):
    return await interns_service.view_intern_summary(intern_id)
