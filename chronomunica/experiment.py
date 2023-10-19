from pathlib import Path
from json import loads, dumps
from logging import error, info
from typing import Dict, List, Any
from datetime import timedelta, datetime

from utils import parse_path
from queryengine import QueryEngine
from proxyserver import ProxyServer


class Experiment:
    proxy_server: ProxyServer
    query_engine: QueryEngine

    replication: int
    result_path: Path
    timeout: timedelta

    configs: List[Path]
    queries: Dict[str, str]

    def __init__(self, manifest: Path) -> None:
        with open(manifest, "r") as manifest_file:
            data = loads(manifest_file.read())

        self.proxy_server = ProxyServer(data["proxy_server"])
        self.query_engine = QueryEngine(data["query_engine"])

        self.result_path = parse_path(data["execution"]["results"])
        self.replication = int(data["execution"]["replication"])
        self.timeout = timedelta(seconds=float(data["execution"]["timeout"]))
        self.configs = list(Path(c) for c in data["configs"])
        self.queries = self.load_queries(data["queries"])

    def load_queries(self, queries: List[str]) -> Dict[str, str]:
        output: Dict[str, str] = {}
        for string_path in queries:
            path = parse_path(string_path).resolve()
            info(f'Loading queries from "{path}"')
            with open(path, "r") as infile:
                all_queries = infile.read().split("\n\nPREFIX")
            for i in range(0, len(all_queries)):
                query_string = f"{'PREFIX'  if i > 0 else ''}{all_queries[i]}".strip()
                query_id = f"{path.as_uri()}#{i}"
                output[query_id] = query_string
        info(f"Loaded {len(output)} queries")
        return output

    def execute(self) -> None:
        results: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.proxy_server.start()
        executions_total: int = len(self.queries) * len(self.configs) * self.replication
        executions_done: int = 1
        skip_remaining: bool = False
        for config_path in self.configs:
            if skip_remaining:
                break
            info(f'Execute with config: "{config_path}"')
            config_results: Dict[str, List[Dict[str, Any]]] = {}
            for query_id, query_string in self.queries.items():
                if skip_remaining:
                    break
                query_results: List[Dict[str, Any]] = []
                for i in range(0, self.replication):
                    info(f"Query {executions_done} / {executions_total} <{query_id}>")
                    try:
                        query_results.append(
                            self.execute_query(query_string, config_path)
                        )
                        executions_done += 1
                    except KeyboardInterrupt:
                        info("Interrupted by user, will skip remaining queries")
                        skip_remaining = True
                        break
                config_results[query_id] = query_results
            results[config_path.as_posix()] = config_results
        self.serialize_results(results)
        self.proxy_server.stop()

    def execute_query(self, query_string: str, config_path: Path) -> Dict[str, Any]:
        try:
            result = self.query_engine.query(query_string, self.timeout, config_path)
        except Exception as ex:
            error(ex)
            result = {"error": str(ex)}
        requested_urls = self.proxy_server.reset()
        result["request_urls"] = requested_urls
        result["request_count"] = len(requested_urls)
        result["request_count_unique"] = len(set(requested_urls))
        return result

    def serialize_results(self, results: Dict[str, Any]) -> None:
        time_string: str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        result_path: Path = self.result_path.joinpath(f"{time_string}.json")
        info(f'Serializing results to "{result_path}"')
        with open(result_path, "w") as result_file:
            result_file.write(
                dumps(results, indent=2, ensure_ascii=False, sort_keys=True)
            )
