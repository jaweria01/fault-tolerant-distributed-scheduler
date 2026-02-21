import json
import os
import matplotlib.pyplot as plt
from collections import Counter

# ----------------------------
# Ensure plots folder exists
# ----------------------------
os.makedirs("plots", exist_ok=True)

# ----------------------------
# Load experiment files
# ----------------------------

with open("experiments/results_round_robin.json") as f:
    rr1 = json.load(f)["results"]

with open("experiments/results_least_loaded.json") as f:
    ll1 = json.load(f)["results"]

with open("experiments/results_round_robin_experiment2.json") as f:
    rr2 = json.load(f)["results"]

with open("experiments/exp2_result_least_loaded_.json") as f:
    ll2 = json.load(f)["results"]


# ----------------------------
# Plot comparison function
# ----------------------------

def plot_comparison(rr, ll, title, filename):
    rr_times = [r["duration"] for r in rr]
    ll_times = [r["duration"] for r in ll]

    plt.figure()
    plt.plot(rr_times, marker="o", label="Round Robin")
    plt.plot(ll_times, marker="o", label="Least Loaded")
    plt.xlabel("Task Index")
    plt.ylabel("Completion Time (seconds)")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.savefig(f"plots/{filename}", dpi=300, bbox_inches="tight")
    plt.close()


# ----------------------------
# Worker utilization chart
# ----------------------------

def plot_utilization(rr, ll, title, filename):
    rr_workers = [r["worker"] for r in rr]
    ll_workers = [r["worker"] for r in ll]

    rr_counts = Counter(rr_workers)
    ll_counts = Counter(ll_workers)

    labels = sorted(set(rr_counts.keys()).union(ll_counts.keys()))
    rr_vals = [rr_counts.get(l,0) for l in labels]
    ll_vals = [ll_counts.get(l,0) for l in labels]

    x = range(len(labels))

    plt.figure()
    plt.bar(x, rr_vals, width=0.4, label="Round Robin")
    plt.bar([i+0.4 for i in x], ll_vals, width=0.4, label="Least Loaded")
    plt.xticks([i+0.2 for i in x], labels)
    plt.title(title)
    plt.xlabel("Worker")
    plt.ylabel("Number of Tasks Executed")
    plt.legend()

    plt.savefig(f"plots/{filename}", dpi=300, bbox_inches="tight")
    plt.close()


# ----------------------------
# Average completion chart
# ----------------------------

def plot_average(rr, ll, title, filename):
    rr_avg = sum(r["duration"] for r in rr) / len(rr)
    ll_avg = sum(r["duration"] for r in ll) / len(ll)

    plt.figure()
    plt.bar(["Round Robin","Least Loaded"], [rr_avg,ll_avg])
    plt.title(title)
    plt.ylabel("Seconds")

    plt.savefig(f"plots/{filename}", dpi=300, bbox_inches="tight")
    plt.close()


# ----------------------------
# Duration histogram
# ----------------------------

def plot_histogram(rr, ll, title, filename):
    rr_times = [r["duration"] for r in rr]
    ll_times = [r["duration"] for r in ll]

    plt.figure()
    plt.hist(rr_times, alpha=0.5, label="Round Robin")
    plt.hist(ll_times, alpha=0.5, label="Least Loaded")
    plt.title(title)
    plt.xlabel("Completion Time")
    plt.ylabel("Frequency")
    plt.legend()

    plt.savefig(f"plots/{filename}", dpi=300, bbox_inches="tight")
    plt.close()


# ----------------------------
# Generate graphs for Experiment 1
# ----------------------------

plot_comparison(rr1, ll1,
                "Experiment 1: Uniform Tasks",
                "exp1_comparison.png")

plot_utilization(rr1, ll1,
                 "Experiment 1: Worker Utilization",
                 "exp1_utilization.png")

plot_average(rr1, ll1,
             "Experiment 1: Average Completion Time",
             "exp1_average.png")

plot_histogram(rr1, ll1,
               "Experiment 1: Duration Distribution",
               "exp1_distribution.png")


# ----------------------------
# Generate graphs for Experiment 2
# ----------------------------

plot_comparison(rr2, ll2,
                "Experiment 2: Mixed Tasks",
                "exp2_comparison.png")

plot_utilization(rr2, ll2,
                 "Experiment 2: Worker Utilization",
                 "exp2_utilization.png")

plot_average(rr2, ll2,
             "Experiment 2: Average Completion Time",
             "exp2_average.png")

plot_histogram(rr2, ll2,
               "Experiment 2: Duration Distribution",
               "exp2_distribution.png")

print("Graphs saved successfully in /plots folder")
#
# ----------------------------
# Makespan calculation
# ----------------------------

def compute_makespan(results):
    worker_times = {}

    for r in results:
        worker = r["worker"]
        duration = r["duration"]
        worker_times[worker] = worker_times.get(worker, 0) + duration

    return max(worker_times.values())


# Calculate makespans
ms_rr1 = compute_makespan(rr1)
ms_ll1 = compute_makespan(ll1)
ms_rr2 = compute_makespan(rr2)
ms_ll2 = compute_makespan(ll2)


# ----------------------------
# Plot makespan comparison
# ----------------------------

import matplotlib.pyplot as plt

labels = ["Exp1 Round Robin", "Exp1 Least Loaded",
          "Exp2 Round Robin", "Exp2 Least Loaded"]

values = [ms_rr1, ms_ll1, ms_rr2, ms_ll2]

plt.figure()
plt.bar(labels, values)
plt.title("Makespan Comparison Across Scheduling Policies")
plt.ylabel("Total Completion Time (seconds)")
plt.xticks(rotation=20)

plt.savefig("plots/makespan_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

print("Makespan graph saved in plots/makespan_comparison.png")
