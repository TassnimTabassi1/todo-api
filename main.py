from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel

app = FastAPI(title="Task API", description="A small CRUD API for managing a to-do list.")

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Learn FastAPI", "done": True},
]
next_id = 4

class TaskCreate(BaseModel):
    title: str = ""

class TaskUpdate(BaseModel):
    title: str = ""
    done: bool = False

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

@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    """Creates a new task. Title is required and cannot be empty."""
    global next_id
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate):
    """Replaces a task's title and done status. 404 if not found, 400 if title is empty."""
    if not update.title or not update.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = update.title
            task["done"] = update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Removes a task by id. 404 if it doesn't exist."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")