from json import dumps, loads, JSONDecodeError
from pathlib import Path
from time import time_ns
from logging import error, exception
from datetime import timedelta, datetime
from typing import Optional, Dict, Any
from subprocess import Popen, PIPE
from hashlib import sha256
from threading import Timer
from re import Pattern, Match, compile

from utils import parse_path

TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
RESULT_PATTERN: Pattern = compile(r"(?P<result>{.*})")


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
        timeout_reached: bool = False

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
            line_match: Match[str] | None = RESULT_PATTERN.match(line)
            if line_match:
                query_result: str = line_match.group("result")
                try:
                    result_bindings[ns_line] = loads(query_result)
                except JSONDecodeError as ex:
                    exception(ex)
                line = line.replace(query_result, "").strip()
            if line:
                unknown_output[ns_line] = line

        time_end: datetime = datetime.utcnow()
        timer.cancel()

        returncode = proc.poll()
        proc.terminate()

        if returncode and returncode != 1:
            error(f"Timeout reached after {timeout.total_seconds()} seconds")
            timeout_reached = True

        result_dumps = sorted(
            dumps(obj=r, sort_keys=True, ensure_ascii=False)
            for r in result_bindings.values()
        )

        result_hash = sha256(usedforsecurity=False)

        for result_dump in result_dumps:
            result_hash.update(result_dump.encode())

        return {
            "timeout": timeout_reached,
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
