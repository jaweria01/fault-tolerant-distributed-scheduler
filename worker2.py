from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
import sys

app = FastAPI()

# -----------------------------
# Configuration
# -----------------------------

# Get port from command line argument

PORT = "8002"

WORKER_ID = f"worker_{PORT}"
WORKER_URL = f"http://127.0.0.1:{PORT}"
SCHEDULER_URL = "http://127.0.0.1:8000"


# -----------------------------
# Task Model
# -----------------------------

class Task(BaseModel):
    task_id: int
    duration: int


# -----------------------------
# Register Worker on Startup
# -----------------------------

@app.on_event("startup")
def register():
    try:
        requests.post(
            f"{SCHEDULER_URL}/register_worker",
            json={
                "worker_id": WORKER_ID,
                "worker_url": WORKER_URL
            }
        )
        print(f"{WORKER_ID} registered successfully.")
    except:
        print("Failed to register worker.")


# -----------------------------
# Execute Task Endpoint
# -----------------------------

@app.post("/execute_task")
def execute_task(task: Task):
    print(f"{WORKER_ID} executing task {task.task_id}")

    for i in range(task.duration):
        print(f"{WORKER_ID} working... {i+1}/{task.duration}")
        time.sleep(1)

    requests.post(
        f"{SCHEDULER_URL}/task_complete",
        params={"task_id": task.task_id}
    )

    return {"message": f"Task {task.task_id} completed by {WORKER_ID}"}

