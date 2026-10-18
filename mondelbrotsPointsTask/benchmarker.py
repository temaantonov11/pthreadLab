import subprocess
import csv

NPOINTS = 1000000
THREADS = [1, 2, 4, 8, 12, 16, 24]
RUNS = 15


def build():
    cmd = ["gcc", "mondelbrot.c", "../shared_libs/my_rand.c", "-o", "mond"]
    subprocess.run(cmd)

def run(nthreads, npoints):
    cmd = ["./mond", str(nthreads), str(npoints)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout


def main():

    build()

    table = [
        ["RUN NUMBER", "NPOINTS", "THREADS COUNT", "AVG", "MIN"]
    ]

    thread_to_times = {}
    for thread in THREADS:
        run_times = []
        for _run in range(RUNS):
            time = run(thread, NPOINTS)
            print(f"[{thread} thread] run {_run + 1}/{RUNS}: {time}")
            run_times.append(time)
        thread_to_times[thread] = run_times

    for thread, times in thread_to_times.items():
        print(times)
        times = [float(x.strip('\n')) for x in times]

        avg_time = sum(times) / len(times)
        min_time = min(times)
        table.append([RUNS, NPOINTS, thread, round(avg_time, 4), round(min_time, 4)])

    with open("bench.csv", "w", newline="", encoding="utf-8-sig") as fd:
        writer = csv.writer(fd, delimiter=";")
        writer.writerows(table)
        

if __name__ == "__main__":
    main()



