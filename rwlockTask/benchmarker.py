import csv
import os
import re
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
    search_pct: float
    insert_pct: float

    @property
    def delete_pct(self) -> float:
        return round(1.0 - self.search_pct - self.insert_pct, 6)


WORKLOADS = [
    Workload(0.999, 0.0005),
    Workload(0.8, 0.1),
    Workload(0.5, 0.25),
]

THREADS = [1, 2, 4, 8, 16, 24]
LIST_SIZE = 1000
TOTAL_OPS = 80000
REPEATS = 10


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
                    print(f"{impl.name}: threads={threads}, search={wl.search_pct}, "
                          f"insert={wl.insert_pct}, delete={wl.delete_pct}")
                    times = [
                        get_time(run(exe, threads, LIST_SIZE, TOTAL_OPS,
                                     wl.search_pct, wl.insert_pct))
                        for _ in range(REPEATS)
                    ]
                    avg = sum(times) / len(times)
                    min_time = min(times)
                    rows.append({
                        "impl": impl.name,
                        "list_size": LIST_SIZE,
                        "total_ops": TOTAL_OPS,
                        "search_pct": wl.search_pct,
                        "insert_pct": wl.insert_pct,
                        "delete_pct": wl.delete_pct,
                        "threads": threads,
                        "min": min_time,
                        "average": avg,
                    })
                    print(f"  avg={avg:.4f}s min={min_time:.4f}s")

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