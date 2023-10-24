from typing import Dict, List, Any
from pathlib import Path
from logging import info
from json import loads, dumps
from os import getcwd


class Experiment:
    def __init__(self, path: Path, create: bool = False) -> None:
        if create and not path.exists():
            self.create(path=path)
        elif not create and path.exists() and path.is_file():
            self.load(path=path)
        else:
            raise Exception(f'Invalid experiment path "{path}"')

    def as_dict(self) -> Dict[str, Any]:
        return {
            "queries": [p.as_posix() for p in self.queries],
            "configs": [p.as_posix() for p in self.configs],
            "replication": self.replication,
            "results": self.results.as_posix(),
            "query_engine_cwd": self.query_engine_cwd.as_posix(),
            "query_engine_bin": self.query_engine_bin.as_posix(),
            "query_engine_timeout": self.query_engine_timeout,
            "query_engine_context": self.query_engine_context,
            "query_engine_environment": self.query_engine_environment,
            "proxy_server_host": self.proxy_server_host,
            "proxy_server_port": self.proxy_server_port,
            "proxy_server_upstream_host": self.proxy_server_upstream_host,
            "proxy_server_upstream_port": self.proxy_server_upstream_port,
        }

    def create(self, path: Path) -> None:
        info(f'Creating experiment at "{path}"')
        cwd: Path = Path(getcwd()).resolve()
        # Common options
        self.queries: List[Path] = []
        self.configs: List[Path] = []
        self.replication: int = 3
        self.results: Path = cwd
        # Proxy server
        self.proxy_server_host: str = "localhost"
        self.proxy_server_port: int = 3000
        self.proxy_server_upstream_host: str = "localhost"
        self.proxy_server_upstream_port: int = 3001
        # Query engine
        self.query_engine_timeout: int = 60
        self.query_engine_cwd: Path = cwd
        self.query_engine_bin: Path = cwd.joinpath("bin", "query.js")
        self.query_engine_context: Dict[str, Any] = {"sources": [], "lenient": True}
        self.query_engine_environment: Dict[str, str] = {
            "NODE_OPTIONS": "--max-old-space-size=8192",
            "NODE_ENV": "production",
        }
        # Serialize into file
        with open(path, "w") as manifest_file:
            manifest_file.write(
                dumps(self.as_dict(), sort_keys=True, ensure_ascii=False, indent=2)
            )

    def load(self, path: Path) -> None:
        info(f'Loading experiment from "{path}"')
        with open(path, "r") as manifest_file:
            data = loads(manifest_file.read())
        # Common options
        self.queries: List[Path] = list(Path(p).resolve() for p in data["queries"])
        self.configs: List[Path] = list(Path(p) for p in data["configs"])
        self.results: Path = Path(data["results"]).resolve()
        self.replication: int = data["replication"]
        # Proxy server section
        self.proxy_server_host: str = data["proxy_server_host"]
        self.proxy_server_port: int = data["proxy_server_port"]
        self.proxy_server_upstream_host: str = data["proxy_server_upstream_host"]
        self.proxy_server_upstream_port: int = data["proxy_server_upstream_port"]
        # Query engine section
        self.query_engine_timeout: int = data["query_engine_timeout"]
        self.query_engine_cwd: Path = Path(data["query_engine_cwd"]).resolve()
        self.query_engine_bin: Path = Path(data["query_engine_bin"]).resolve()
        self.query_engine_context: Dict[str, Any] = data["query_engine_context"]
        self.query_engine_environment: Dict[str, str] = data["query_engine_environment"]
        # Load individual query strings for queries from the files
        self.query_strings: Dict[str, str] = {}
        for query_path in self.queries:
            info(f'Loading queries from "{query_path}"')
            with open(query_path, "r") as query_file:
                all_queries = query_file.read().split("\n\nPREFIX")
            for i in range(0, len(all_queries)):
                query_string = f"{'PREFIX'  if i > 0 else ''}{all_queries[i]}".strip()
                query_id = f"{query_path.as_uri()}#{i}"
                self.query_strings[query_id] = query_string
        info(f"Loaded {len(self.query_strings)} queries")
