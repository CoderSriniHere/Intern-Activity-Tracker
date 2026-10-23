from pydantic import BaseModel

"""The schema of the project where the pydantic will validate the 
input and store it."""
class InternCreate(BaseModel):
    name: str
    role: str


class ActivityEntry(BaseModel):
    hours: int
    task: str


class StatusUpdate(BaseModel):
    status: str
