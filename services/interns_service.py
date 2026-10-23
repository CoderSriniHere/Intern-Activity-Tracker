from fastapi import HTTPException

from schemas import InternCreate, ActivityEntry, StatusUpdate
from database import read_data, write_data
from utilities import find_intern, generate_intern_id

"""Actual function defination is in this file,
 where the end points are in the router folder"""

async def add_intern(payload: InternCreate):
    name = payload.name.strip()
    role = payload.role.strip()
    if not name or not role:
        raise HTTPException(status_code=400, detail="Name and role cannot be empty")

    data = await read_data()
    new_id = generate_intern_id(data)
    new_intern = {
        "intern_id": new_id,
        "name": name,
        "role": role,
        "status": "Active",
        "hours": [],
        "tasks": [],
    }
    data.append(new_intern)
    await write_data(data)

    return {"message": "Intern added successfully", "intern_id": new_id}


async def add_daily_activity(intern_id: str, payload: ActivityEntry):
    data = await read_data()
    intern = find_intern(data, intern_id)

    if intern is None:
        raise HTTPException(status_code=404, detail="Intern not found")

    if intern["status"] != "Active":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot add activity - intern status is '{intern['status']}'"
        )

    if payload.hours < 0 or payload.hours > 24:
        raise HTTPException(status_code=400, detail="Hours must be between 0 and 24")

    task = payload.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    intern["hours"].append(payload.hours)
    intern["tasks"].append(task)
    await write_data(data)

    return {"message": "Activity recorded", "intern_id": intern_id}


async def update_intern_status(intern_id: str, payload: StatusUpdate):
    valid_statuses = ["Active", "Inactive", "Completed"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    data = await read_data()
    intern = find_intern(data, intern_id)

    if intern is None:
        raise HTTPException(status_code=404, detail="Intern not found")

    intern["status"] = payload.status
    await write_data(data)

    return {"message": "Status updated", "intern_id": intern_id, "status": payload.status}


async def view_intern_summary(intern_id: str):
    data = await read_data()
    intern = find_intern(data, intern_id)

    if intern is None:
        raise HTTPException(status_code=404, detail="Intern not found")

    hours = intern["hours"]
    tasks = intern["tasks"]
    total_hours = sum(hours)
    average_hours = (total_hours / len(hours)) if hours else 0
    most_recent_task = tasks[-1] if tasks else None

    return {
        "intern_id": intern["intern_id"],
        "name": intern["name"],
        "role": intern["role"],
        "status": intern["status"],
        "total_hours": total_hours,
        "average_hours": round(average_hours, 2),
        "task_history": tasks,
        "most_recent_activity": most_recent_task,
    }
