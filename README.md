# Performance Evaluation of a Fault-Tolerant Distributed Task Scheduling System
This repo contains a fault-tolerant distributed task scheduling system with heartbeat-based failure detection, dynamic task reassignment, Round-Robin and Least-Loaded scheduling policies, and experimental performance evaluation.
## 📌 Overview

A fault-tolerant distributed task scheduling system implemented in Python using FastAPI.  
The project simulates a distributed computing environment in which a central scheduler assigns tasks to multiple worker nodes via HTTP communication.

The system demonstrates core distributed-systems principles including:

- Service decoupling  
- Network-based coordination  
- Failure detection  
- Automatic recovery  
- Scheduling strategy evaluation  

The project is designed for educational, research, and experimentation purposes in distributed systems and cloud computing.

## 🏗 System Architecture

The system follows a **Scheduler–Worker distributed model**.

### 🔹 Scheduler

Responsible for:

- Registering workers dynamically  
- Assigning tasks using scheduling policies  
- Monitoring worker health via heartbeats  
- Detecting worker failure  
- Reassigning unfinished tasks automatically  
- Tracking task performance metrics  

### 🔹 Workers

Responsible for:

- Receiving tasks from the scheduler  
- Executing tasks independently  
- Sending periodic heartbeat signals  
- Reporting task completion  

### 🔹 Communication Model

All components communicate using **REST APIs over HTTP**, meaning:

- No shared memory  
- No shared variables  
- All coordination happens through network calls

## ⚙️ Core Features

The system implements several core mechanisms commonly found in real distributed platforms:

### ✅ Distributed Task Execution
Tasks are executed across multiple worker services running as independent processes.

### ✅ Dynamic Worker Registration
Workers automatically register with the scheduler at startup, allowing flexible scaling of the system.

### ✅ Heartbeat-Based Failure Detection
Workers periodically send heartbeat signals to indicate liveness.  
If heartbeats stop, the scheduler marks the worker as failed.

### ✅ Automatic Task Reassignment
If a worker fails while executing a task, the scheduler automatically reassigns unfinished work to another available worker.

### ✅ Scheduling Policies
Two task allocation strategies are implemented:

- **Round-Robin Scheduling** — tasks are assigned sequentially to workers
- **Least-Loaded Scheduling** — tasks are assigned to the worker with the lowest current load

These strategies allow experimentation with different scheduling behaviors.

### ✅ System Monitoring Interface
A status API exposes real-time information about workers, task states, and system load, enabling inspection and debugging.


This interaction pattern mirrors real-world microservice-based distributed systems.

## 🧪 Experimental Evaluation

To study the behavior of the scheduling system, a series of controlled experiments were conducted comparing the Round-Robin and Least-Loaded policies.

Experiments were designed to evaluate how scheduling decisions influence system performance under different workload characteristics. Two types of task distributions were tested:

- **Uniform workload experiments**, where task durations were similar
- **Heterogeneous workload experiments**, where task durations varied significantly

For each experiment, the system recorded task completion times, worker utilization, and overall execution performance. These measurements were used to generate visualizations and analyze how effectively each scheduling policy distributed work across available workers.

The evaluation focuses on three primary metrics:

- **Task completion time**, indicating how long individual tasks require to finish
- **Worker utilization**, showing how tasks are distributed across nodes
- **Makespan**, representing the total time required for all tasks to complete

The following subsections present the experimental results along with visualizations and interpretations.


