from json import dumps
from pathlib import Path
from time import time_ns
from logging import error
from datetime import timedelta
from typing import Dict, Any, List
from subprocess import Popen, PIPE
from threading import Timer
from re import Pattern, Match, compile

from experiment.result import Result

RESULT_PATTERN: Pattern = compile(r"(?P<result>{.*})")


class QueryEngine:
    def __init__(
        self,
        cwd: Path,
        bin: Path,
        node: Path,
        env: Dict[str, str],
        context: Dict[str, Any] | None,
    ) -> None:
        self.cwd: Path = cwd
        self.bin: Path = bin
        self.node: Path = node
        self.env: Dict[str, str] = env
        self.context: str | None = dumps(context) if context else None

    def query_bindings(
        self, query_id: str, query_string: str, timeout: timedelta, config_path: Path
    ) -> Result:
        result: Result = Result(config=config_path.as_posix(), query=query_id)

        args: List[str] = [
            self.node.as_posix(),
            self.bin.as_posix(),
            "--query",
            query_string,
        ]

        if self.context:
            args.append("--context")
            args.append(self.context)

        result.begin()

        proc: Popen = Popen(
            args=args,
            env={**self.env, "COMUNICA_CONFIG": config_path.as_posix()},
            cwd=self.cwd,
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
                result.add_result(ns_line, query_result)
                line = line.replace(query_result, "").strip()
            if line:
                result.add_result(ns_line, line)

        result.end()
        timer.cancel()

        returncode: int | None = proc.poll()

        proc.terminate()

        if returncode and returncode != 1:
            error(f"Timeout reached after {timeout.total_seconds()} seconds")
            result.timeout = True

        result.stderr = proc.stderr.read()

        return result
