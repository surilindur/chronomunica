from json import dumps, loads
from pathlib import Path
from time import time_ns
from logging import exception, info
from datetime import timedelta, datetime
from typing import Optional, Dict, List, Any
from subprocess import Popen, PIPE
from hashlib import sha256
from threading import Timer

from utils import parse_path

TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class QueryEngine:
    bin: Path
    context: Optional[str]

    def __init__(self, config: Dict[str, str | Dict[str, str]]) -> None:
        self.bin = parse_path(config["bin"]).resolve()
        self.context = dumps(config["context"]) if "context" in config else None

    def query(
        self, query_string: str, timeout: timedelta, config_path: Path
    ) -> Dict[str, Any]:
        try:
            args = ["node", self.bin.as_posix(), "--query", query_string]

            if self.context:
                args.append("--context")
                args.append(self.context)

            proc: Popen = Popen(
                args,
                env={"COMUNICA_CONFIG": config_path.as_posix()},
                cwd=self.bin.parent.parent,
                encoding="utf-8",
                stdout=PIPE,
                stderr=PIPE,
            )

            result_intervals: List[int] = []
            result_bindings: List[Any] = []

            time_start: datetime = datetime.utcnow()
            time_end: datetime = time_start
            time_prev: int = time_ns()
            time_now: int = time_prev

            def on_timeout() -> None:
                proc.terminate()
                raise TimeoutError(
                    f"Query timed out after {timeout.total_seconds()} seconds"
                )

            timer: Timer = Timer(interval=timeout.total_seconds(), function=on_timeout)
            timer.start()

            while True:
                line: str = proc.stdout.readline()
                time_now = time_ns()
                line = line.strip().removesuffix(",").removeprefix("[").strip()
                if not line:
                    continue
                elif line.endswith("]"):
                    break
                elif line.startswith("{") and line.endswith("}"):
                    query_result = loads(line)
                    result_bindings.append(query_result)
                    result_intervals.append(time_now - time_prev)
                    time_prev = time_now
                else:
                    info(f"Unexpected output: {line}")

            time_end = datetime.utcnow()
            timer.cancel()
            proc.terminate()
            result_hash = sha256(usedforsecurity=False)

            for result in sorted(dumps(r) for r in result_bindings):
                result_hash.update(result.encode())

            return {
                "time_start": time_start.strftime(TIME_FORMAT),
                "time_end": time_end.strftime(TIME_FORMAT),
                "result_count": len(result_bindings),
                "result_hash": result_hash.hexdigest(),
                "result_list": result_bindings,
                "result_intervals": result_intervals,
                "error": proc.stderr.read(),
            }

        except Exception as ex:
            exception(ex)
            return {"error": str(ex)}
