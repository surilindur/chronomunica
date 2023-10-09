from pathlib import Path
from time import sleep
from json import loads, dumps
from logging import error, info
from typing import Dict, List, Any

from queryengine import QueryEngine
from proxyserver import ProxyServer


class Benchmark:
    proxy_server: ProxyServer
    query_engine: QueryEngine

    replication: int
    queries: Dict[str, str]
    results: Path

    def __init__(self, manifest: Path) -> None:
        with open(manifest, "r") as manifest_file:
            data = loads(manifest_file.read())

        self.query_engine = QueryEngine(data["engine"])
        self.proxy_server = ProxyServer(data["server"])

        self.results = Path(data["results"]).resolve()
        self.replication = int(data["replication"])
        self.queries = {}

        for string_path in data["queries"]:
            path = Path(string_path).resolve()
            info(f"Load queries from {path}")
            with open(path, "r") as infile:
                all_queries = infile.read().split("\n\nPREFIX")
            for i in range(0, len(all_queries)):
                query_string = f"{'PREFIX'  if i > 0 else ''}{all_queries[i]}".strip()
                query_id = f"file://{path.as_posix()}#{i}"
                self.queries[query_id] = query_string

        info(f"Loaded {len(self.queries)} queries")

    def execute(self) -> None:
        results: Dict[str, List[Dict[str, Any]]] = {}
        self.proxy_server.start()
        sleep(5)
        executions_total: int = len(self.queries) * self.replication
        executions_done: int = 1
        for query_id, query_string in self.queries.items():
            results[query_id] = []
            for i in range(0, self.replication):
                info(f"Query ({executions_done} / {executions_total}) {query_id}")
                results[query_id].append(self.execute_query(query_string))
                executions_done += 1
        input("Any key to quit")
        self.serialize_results(results)
        self.proxy_server.stop()

    def execute_query(self, query_string) -> Dict[str, Any]:
        try:
            result = self.query_engine.query(query_string)
            result["requested_urls"] = self.proxy_server.reset()
            return result
        except Exception as ex:
            error(ex)
            return {"error": str(ex)}

    def serialize_results(self, results: Dict[str, Any]) -> None:
        info(f"Serializing results to {self.results}")
        with open(self.results, "w") as result_file:
            result_file.write(
                dumps(results, indent=2, ensure_ascii=False, sort_keys=True)
            )
