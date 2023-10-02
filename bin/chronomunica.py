from subprocess import Popen, PIPE
from datetime import datetime


def test_output() -> None:
    proc = Popen(["ls", "-la"], stdout=PIPE)
    last_time = datetime.now()
    output_intervals = []
    while True:
        line = proc.stdout.readline()
        current_time = datetime.now()
        output_intervals.append((current_time - last_time).microseconds)
        last_time = current_time
        if not line:
            break
    print(output_intervals)


if __name__ == "__main__":
    test_output()
