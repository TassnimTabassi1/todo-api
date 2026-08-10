import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel

app = FastAPI(title="Task API", description="A small CRUD API for managing a to-do list.")

DB_FILE = "tasks.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  
    return conn


@app.on_event("startup")
def startup():
    conn = get_db()
    cursor = conn.cursor()

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy milk", False),
                ("Walk the dog", False),
                ("Learn FastAPI", True),
            ]
        )

    conn.commit()
    conn.close()


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
    """Returns every task currently stored in the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return dict(row)
@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    """Creates a new task. Title is required and cannot be empty."""
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, False)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}