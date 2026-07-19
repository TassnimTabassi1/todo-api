from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request

app = FastAPI(title="Task API", description="A small CRUD API for managing a to-do list.")

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Learn FastAPI", "done": True},
]

# This makes EVERY HTTPException in the app return {"error": "..."}
# instead of FastAPI's default {"detail": "..."}
@app.exception_handler(HTTPException)
def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.get("/", summary="API info")
def read_root():
    """Describes this API and lists its main resource."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health check")
def health_check():
    """Confirms the server is running."""
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    """Returns every task currently stored in memory."""
    return tasks

@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")