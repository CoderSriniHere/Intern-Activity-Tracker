from fastapi import APIRouter

from services import statistics_service

router = APIRouter(tags=["Statistics"])

"""Contains just the end point to the overall statistics 
and the actual function is in the services folder."""

@router.get("/statistics")
async def overall_statistics():
    return await statistics_service.overall_statistics()
