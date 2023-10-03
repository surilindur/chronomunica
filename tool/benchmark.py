from pathlib import Path
from datetime import timedelta
from json import loads, dumps
from subprocess import check_output, PIPE, TimeoutExpired
from logging import error, info
from typing import Dict, List
from os import environ

from definitions import QueryExecution, QueryExecutionResult, BenchmarkConfiguration

RUNNER: Path = Path(__file__, "..", "..", "runner", "runner.js").resolve()


def execute_query(execution: QueryExecution) -> QueryExecutionResult | str:
    try:
        benchmark_env = environ.copy()
        for key, value in execution.environment.items():
            benchmark_env[key] = value
        output = check_output(
            [
                "node",
                RUNNER,
                "--query",
                execution.query,
                "--config",
                execution.config.as_posix(),
            ],
            timeout=int(execution.timeout.total_seconds()),
            env=benchmark_env,
            cwd=execution.workdir,
            encoding="utf-8",
            stderr=PIPE,
        )
        output = "{" + output.split("{", maxsplit=1)[1]
        return QueryExecutionResult(**loads(output))
    except TimeoutExpired as ex:
        return f"Timeout after {ex.timeout} seconds"
    except Exception as ex:
        error(ex)
        return str(ex)


def load_queries(path: Path) -> Dict[str, str]:
    with open(path, "r") as infile:
        queries = infile.read().split("\n\nPREFIX")
    query_file_id = path.name.split(".")[0]
    output = {}
    for i in range(0, len(queries)):
        query_string = f"{'PREFIX'  if i > 0 else ''}{queries[i]}"
        query_id = f"{query_file_id}-{i}"
        output[query_id] = query_string
    return output


def load_benchmark_config(path: Path) -> BenchmarkConfiguration:
    with open(path, "r") as infile:
        config_data = loads(infile.read())
    config = BenchmarkConfiguration(
        config=Path(config_data["config"]).resolve(),
        workdir=Path(config_data["workdir"]).resolve(),
        output=Path(config_data["output"]).resolve(),
        timeout=int(config_data["timeout"]),
        repeat=int(config_data["repeat"]),
        context={k: v for k, v in config_data["context"].items()}
        if "context" in config_data
        else None,
        queries=list(Path(p).resolve() for p in config_data["queries"]),
        environment={k: v for k, v in config_data["environment"].items()},
    )
    return config


def run_benchmark(path: Path) -> None:
    info(f"Loading benchmark config from {path}")
    config = load_benchmark_config(path)
    queries: Dict[str, str] = {}
    for query_file in config.queries:
        queries = queries | load_queries(query_file)
    execution_results: Dict[str, List[QueryExecutionResult]] = {
        k: [] for k in queries.keys()
    }
    total_queries = len(queries) * config.repeat
    executed_queries = 1
    for query_id, query_string in queries.items():
        for i in range(0, config.repeat):
            execution = QueryExecution(
                query=query_string,
                context=dumps(config.context),
                config=config.config,
                workdir=config.workdir,
                timeout=timedelta(seconds=config.timeout),
                environment=config.environment,
            )
            info(f"Execute {executed_queries} / {total_queries} as {query_id} {i}")
            result = execute_query(execution)
            if isinstance(result, QueryExecutionResult):
                execution_results[query_id].append(result._asdict())
            else:
                execution_results[query_id].append({"error": result})
            executed_queries += 1
    with open(config.output, "w") as outfile:
        outfile.write(
            dumps(execution_results, indent=2, sort_keys=True, ensure_ascii=False)
        )
