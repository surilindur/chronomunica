from json import JSONDecodeError, loads, dumps
from datetime import datetime
from logging import debug
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING
from hashlib import md5

if TYPE_CHECKING:
    from hashlib import _Hash

TIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT_FILENAME: str = "%Y%m%dT%H%M%SZ"


class Result:
    def __init__(self, config: str, query: str) -> None:
        self.config: str = config
        self.query: str = query
        self.results: Dict[int, Any] = {}
        self.other: Dict[int, str] = {}
        self.urls: List[str] = []
        self.stderr: str | None = None
        self.timeout: bool = False

    def begin(self) -> None:
        self.time_begin: datetime = datetime.utcnow()

    def end(self) -> None:
        self.time_end: datetime = datetime.utcnow()

    def add_result(self, timestamp: int, result: str) -> None:
        try:
            self.results[timestamp] = loads(result)
        except JSONDecodeError as ex:
            debug(ex)
            self.other[timestamp] = (
                result
                if timestamp not in self.other
                else self.other[timestamp] + result
            )

    def get_time_taken_seconds(self) -> float:
        return (self.time_end - self.time_begin).total_seconds()

    def get_result_values_as_strings(self) -> List[str]:
        result_values: List[str] = list(
            dumps(r, sort_keys=True, ensure_ascii=False) for r in self.results.values()
        )
        result_values.sort()
        return result_values

    def get_result_hash(self) -> str:
        return self.__result_hash__().hexdigest()

    def get_result_count_unique(self) -> int:
        return len(set(self.get_result_values_as_strings()))

    def get_url_count_unique(self) -> int:
        return len(set(self.urls))

    def __result_hash__(self) -> "_Hash":
        hash_object = md5(usedforsecurity=False)
        for result in sorted(self.get_result_values_as_strings()):
            hash_object.update(result.encode())
        return hash_object

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and hash(self) == hash(__value)

    def __hash__(self) -> int:
        return self.__result_hash__().digest()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "time_begin": self.time_begin.strftime(TIME_FORMAT),
            "time_end": self.time_end.strftime(TIME_FORMAT),
            "time_taken_seconds": self.get_time_taken_seconds(),
            "engine_timeout_reached": self.timeout,
            "engine_config": self.config,
            "engine_query": self.query,
            "engine_stderr": self.stderr,
            "result_hash": self.get_result_hash(),
            "result_count": len(self.results),
            "result_count_unique": self.get_result_count_unique(),
            "result_data": self.results,
            "result_data_other": self.other,
            "requested_urls": self.urls,
            "requested_urls_count": len(self.urls),
            "requested_urls_count_unique": self.get_url_count_unique(),
        }


def load_result(path: Path) -> Result:
    with open(path, "r") as result_file:
        data = loads(result_file.read())
    result: Result = Result(config=data["engine_config"], query=data["engine_query"])
    result.timeout = data["engine_timeout_reached"]
    result.time_begin = datetime.strptime(data["time_begin"], TIME_FORMAT)
    result.time_end = datetime.strptime(data["time_end"], TIME_FORMAT)
    result.urls = data["requested_urls"]
    result.results = data["result_data"]
    result.other = data["result_data_other"]
    result.stderr = data["engine_stderr"]
    return result


def save_result(path: Path, result: Result) -> Result:
    result_path: Path = path.joinpath(
        f"{result.time_begin.strftime(TIME_FORMAT_FILENAME)}.json"
    )
    with open(result_path, "w") as result_file:
        result_file.write(
            dumps(result.as_dict(), sort_keys=True, ensure_ascii=False, indent=2)
        )
