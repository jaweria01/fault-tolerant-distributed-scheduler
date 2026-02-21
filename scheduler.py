from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
import threading
import logging
task_timestamps = {}
# "round_robin" or "least_loaded"
SCHEDULING_POLICY = "least_loaded"

worker_load = {}
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI()

# Store workers and tasks
workers = []
tasks = {}
current_worker_index = 0
worker_last_seen = {}

# -----------------------------
# Data Models
# -----------------------------

class Worker(BaseModel):
    worker_id: str
    worker_url: str


class Task(BaseModel):
    task_id: int
    duration: int


# -----------------------------
# Endpoint 1: Register Worker
# -----------------------------

@app.post("/register_worker")
def register_worker(worker: Worker):
    if worker.worker_id not in [w.worker_id for w in workers]:
        workers.append(worker)

        # initialize load tracking
        worker_load[worker.worker_id] = 0

        logging.info(f"Worker registered: {worker.worker_id}")
    else:
        logging.info(f"Worker already registered: {worker.worker_id}")

    return {"message": "Worker registered successfully"}


#
def send_task_async(worker_url, task_data):
    try:
        requests.post(f"{worker_url}/execute_task", json=task_data)
    except Exception as e:
        logging.error(f"Failed to send task: {e}")


# -----------------------------
# Endpoint 2: Submit Task
# -----------------------------

def select_worker():
    global current_worker_index

    if SCHEDULING_POLICY == "round_robin":
        selected = workers[current_worker_index]
        current_worker_index = (current_worker_index + 1) % len(workers)
        return selected

    elif SCHEDULING_POLICY == "least_loaded":
        return min(workers, key=lambda w: worker_load.get(w.worker_id, 0))

    else:
        return workers[0]
    
# submit task endpoint
@app.post("/submit_task")
def submit_task(task: Task):
    global current_worker_index

    if not workers:
        return {"error": "No workers available"}
    # Select least-loaded worker
    selected_worker = select_worker()
    # Update worker load
    worker_load[selected_worker.worker_id] = worker_load.get(selected_worker.worker_id, 0) + 1

    # Store task status
    tasks[task.task_id] = {
    "status": "ASSIGNED",
    "worker_id": selected_worker.worker_id,
    "data": task.model_dump()
}
    # Record timestamps for experiment
    task_timestamps[task.task_id] = {
    "start": time.time(),
    "end": None
}

    # Send task to worker
    try:
        threading.Thread(
    target=send_task_async,
    args=(selected_worker.worker_url, task.model_dump()),
    daemon=True
).start()
    except:
        return {"error": "Failed to send task"}

    return {"message": f"Task {task.task_id} assigned to {selected_worker.worker_id}"}


# -----------------------------
# Endpoint 3: Task Complete
# -----------------------------

@app.post("/task_complete")
def task_complete(task_id: int):
    if task_id in tasks:
        tasks[task_id]["status"] = "COMPLETED"

        # record completion time
        if task_id in task_timestamps:
            task_timestamps[task_id]["end"] = time.time()

        worker_id = tasks[task_id]["worker_id"]
        worker_load[worker_id] = max(worker_load.get(worker_id, 1) - 1, 0)
        logging.info(f"Task {task_id} completed by {worker_id}")

    return {"message": f"Task {task_id} marked as completed"}
#
@app.on_event("startup")
def start_monitoring():
    threading.Thread(target=monitor_workers, daemon=True).start()

# heartbeat endpoint to track worker health
@app.post("/heartbeat")
def heartbeat(worker_id: str):
    worker_last_seen[worker_id] = time.time()
    logging.info(f"Heartbeat received from {worker_id}")
    return {"message": f"Heartbeat received from {worker_id}"}

# Background thread to check worker health
def monitor_workers():
    while True:
        current_time = time.time()

        for worker_id, last_seen in list(worker_last_seen.items()):
            if current_time - last_seen > 8:
                logging.warning(f"Worker {worker_id} is DEAD")
                logging.info(f"Current tasks: {tasks}")  # 

                # find tasks owned by this worker
                for task_id, info in tasks.items():
                    if info["worker_id"] == worker_id and info["status"] != "COMPLETED":
                        logging.info(f"Reassigning task {task_id} from {worker_id}")

                        # find another worker
                        for w in workers:
                            if w.worker_id != worker_id:
                                try:
                                    requests.post(
                                        f"{w.worker_url}/execute_task",
                                        json=info["data"]
                                    )
                                    
                                    # reset timing since task restarted
                                    if task_id in task_timestamps:
                                        task_timestamps[task_id]["start"] = time.time()
                                        task_timestamps[task_id]["end"] = None

                                    info["worker_id"] = w.worker_id
                                    logging.info(f"Task {task_id} reassigned to {w.worker_id}")
                                    break
                                except:
                                    pass

        time.sleep(5)

# Status endpoint for debugging
@app.get("/status")
def status():
    return {
        "policy": SCHEDULING_POLICY,
        "workers": [w.worker_id for w in workers],
        "last_seen": worker_last_seen,
        "tasks": tasks,
        "load": worker_load
    }

# Experiment results endpoint

@app.get("/experiment_results")
def experiment_results():
    results = []

    for task_id, times in task_timestamps.items():
        if times["end"] is not None:
            duration = times["end"] - times["start"]
            worker = tasks[task_id]["worker_id"]

            results.append({
                "task_id": task_id,
                "worker": worker,
                "duration": duration
            })

    return {
        "policy": SCHEDULING_POLICY,
        "results": results
    }
