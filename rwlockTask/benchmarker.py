import csv
import os
import re
import statistics
import subprocess
from dataclasses import dataclass
from enum import Enum


class Rwlock(Enum):
    STDLIB = "stdrwl"
    LAB = "labrwl"



BUILD_CMDS = {
    Rwlock.STDLIB: ["gcc", "-O2", "pth_II_rwl.c", "../shared_libs/my_rand.c",
                    "-o", Rwlock.STDLIB.value, "-pthread"],
    Rwlock.LAB: ["gcc", "-O2", "pth_II_myrwl.c", "../shared_libs/my_rand.c",
                 "my_rwlock.c", "-o", Rwlock.LAB.value, "-pthread"],
}


@dataclass(frozen=True)
class Workload:
    name: str
    search_pct: float
    insert_pct: float 


WORKLOADS = [
    Workload("read99.9", 0.999, 0.0005),
    Workload("mixed80", 0.8, 0.1),
    Workload("write50", 0.5, 0.25),
]

THREADS = [1, 2, 4, 8, 16, 24]
LIST_SIZE = 1000
TOTAL_OPS = 80000
REPEATS = 7


def build(impl: Rwlock) -> str:
    subprocess.run(BUILD_CMDS[impl], check=True)
    return impl.value


def run(exe: str, threads: int, list_size: int, total_ops: int,
        search_pct: float, insert_pct: float) -> str:
    stdin_data = f"{list_size}\n{total_ops}\n{search_pct}\n{insert_pct}\n"
    result = subprocess.run(
        [f"./{exe}", str(threads)],
        input=stdin_data,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def get_time(output: str) -> float:
    m = re.search(r"Elapsed time = ([\d.eE+-]+) seconds", output)
    return float(m.group(1))


def main():
    exes = {}
    try:
        for impl in Rwlock:
            exes[impl] = build(impl)

        rows = []

        for wl in WORKLOADS:
            for threads in THREADS:
                for impl, exe in exes.items():
                    print(f"{wl}: {threads}: {impl}")
                    times = [
                        get_time(run(exe, threads, LIST_SIZE, TOTAL_OPS,
                                        wl.search_pct, wl.insert_pct))
                        for _ in range(REPEATS)
                    ]
                    avg = sum(times) / len(times)
                    min_time = min(times)
                    rows.append({
                        "impl": impl.name, "workload": wl.name,
                        "size": LIST_SIZE, "threads": threads,
                        "min": min_time, "average": avg,
                    })
                    print(f"{impl.name:6} size={LIST_SIZE:<6} {wl.name:9} "
                            f"t={threads:<2} median={avg:.4f}s min={min_time:.4f}")

        with open("benchs.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        

    finally:
        for exe in exes.values():
            if os.path.exists(exe):
                os.remove(exe)


if __name__ == "__main__":
    main()