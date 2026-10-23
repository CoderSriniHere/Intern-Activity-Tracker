from fastapi import FastAPI

from routers import interns, statistics

app = FastAPI(title="Intern Management API")

app.include_router(interns.router)
app.include_router(statistics.router)

"""The main file of the project also hold the home page of the web server
with a message "Intern Management API is running" """

@app.get("/")
async def root():
    return {"message": "Intern Management API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
