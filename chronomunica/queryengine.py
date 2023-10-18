from json import dumps, loads
from pathlib import Path
from time import time_ns
from datetime import timedelta, datetime
from typing import Optional, Dict, Any
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
        args = ["node", self.bin.as_posix(), "--query", query_string]

        if self.context:
            args.append("--context")
            args.append(self.context)

        unknown_output: Dict[int, str] = {}
        result_bindings: Dict[int, Any] = {}

        time_start: datetime = datetime.utcnow()

        proc: Popen = Popen(
            args=args,
            env={"COMUNICA_CONFIG": config_path.as_posix()},
            cwd=self.bin.parent.parent,
            encoding="utf-8",
            stdout=PIPE,
            stderr=PIPE,
        )

        timer: Timer = Timer(interval=timeout.total_seconds(), function=proc.terminate)
        timer.start()

        ns_start: int = time_ns()

        for line in proc.stdout:
            ns_line: int = time_ns() - ns_start
            line: str = line.strip().removesuffix(",").removeprefix("[").strip()
            if not line:
                # skip empty lines
                continue
            elif line.endswith("]"):
                # when the result bindings are done, the reading loop can be terminated
                break
            elif line.startswith("{") and line.endswith("}"):
                query_result = loads(line)
                result_bindings[ns_line] = query_result
            else:
                unknown_output[ns_line] = line

        time_end: datetime = datetime.utcnow()
        timer.cancel()

        proc_returncode = proc.poll()
        proc.terminate()

        if proc_returncode:
            raise TimeoutError(
                f"Timed out after {timeout.total_seconds()} seconds (code {proc_returncode})"
            )

        result_hash = sha256(usedforsecurity=False)
        result_dumps = sorted(dumps(r) for r in result_bindings.values())

        for result_dump in result_dumps:
            result_hash.update(result_dump.encode())

        return {
            "time_start": time_start.strftime(TIME_FORMAT),
            "time_end": time_end.strftime(TIME_FORMAT),
            "time_taken": (time_end - time_start).total_seconds(),
            "result_count": len(result_bindings),
            "result_count_unique": len(set(result_dumps)),
            "result_hash": result_hash.hexdigest(),
            "result_bindings": result_bindings,
            "other_output": unknown_output,
            "error": proc.stderr.read(),
        }
