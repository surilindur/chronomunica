from typing import List, Dict, Any, NamedTuple
from pathlib import Path
from datetime import timedelta


class QueryExecutionResult(NamedTuple):
    duration: int
    resultCount: int
    resultHash: int
    resultIntervals: List[int]
    requestCount: int
    requestUrls: List[str]


class QueryExecution(NamedTuple):
    query: str
    context: str
    config: Path
    workdir: Path
    timeout: timedelta
    environment: Dict[str, str]


class BenchmarkConfiguration(NamedTuple):
    config: Path
    workdir: Path
    output: Path
    timeout: int
    repeat: int
    context: Dict[str, str] | None
    queries: List[Path]
    environment: Dict[str, str]
