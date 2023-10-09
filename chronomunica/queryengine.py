from json import dumps, loads
from pathlib import Path
from time import time_ns
from logging import exception
from datetime import timedelta, datetime
from typing import Optional, Dict, List, Any
from subprocess import Popen, PIPE
from collections.abc import Sequence
from threading import Timer

TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class QueryEngine:
    js: Path
    cwd: Path
    timeout: timedelta
    context: Optional[str]
    environment: Optional[Dict[str, str]]

    def __init__(self, config: Dict[str, str | Dict[str, str]]) -> None:
        self.cwd = Path(config["cwd"]).resolve()
        self.js = Path(config["js"])
        self.timeout = timedelta(seconds=float(config["timeout"]))
        self.environment = {"COMUNICA_CONFIG": Path(config["config"]).as_posix()}
        if "environment" in config:
            for k, v in config["environment"].items():
                self.environment[k] = v
        if "context" in config:
            self.context = dumps(config["context"])

    def query(self, query_string: str) -> Dict[str, Any]:
        try:
            args = ["node", self.js.as_posix(), "--query", query_string]
            if self.context:
                args.append("--context")
                args.append(self.context)
            proc: Popen = Popen(
                args,
                env=self.environment,
                cwd=self.cwd,
                encoding="utf-8",
                stdout=PIPE,
                stderr=PIPE,
            )
            timer: Timer = Timer(
                interval=self.timeout.total_seconds(), function=proc.kill
            )
            intervals: List[int] = []
            results: List[Any] = []
            time_start: datetime = datetime.utcnow()
            time_end: datetime = time_start
            time_prev: int = time_ns()
            time_now: int = time_prev
            timer.start()
            while True:
                line: Optional[str] = proc.stdout.readline()
                time_now = time_ns()
                if not line:
                    break
                line = line.strip().removesuffix(",")
                if line == "[]" or line.startswith("]"):
                    break
                if line.startswith("{") and line.endswith("}"):
                    query_result = loads(line)
                    results.append(query_result)
                    intervals.append(time_now - time_prev)
                    time_prev = time_now
            time_end = datetime.utcnow()
            timer.cancel()
            proc.kill()
            output = {
                "time_start": time_start.strftime(TIME_FORMAT),
                "time_end": time_end.strftime(TIME_FORMAT),
                "result_count": len(results),
                "result_hash": hash("".join(sorted(dumps(r) for r in results))),
                "result_list": results,
                "result_intervals": intervals,
            }
            stderr: Optional[str] = proc.stderr.read()
            if stderr:
                output["error"] = stderr.strip()
            return output
        except Exception as ex:
            exception(ex)
            return {"error": str(ex)}
